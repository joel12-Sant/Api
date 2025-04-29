import pandas as pd
from fastapi import FastAPI, HTTPException,Path
from sqlalchemy import create_engine
import os

app = FastAPI()

MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')  
MYSQL_USER = os.getenv('MYSQL_USER', 'user')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password') 
MYSQL_DB = os.getenv('MYSQL_DB', 'video_games')

engine = create_engine(f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}')
tablas = ['genre', 'game','game_platform','game_publisher','platform','publisher','region','region_sales']
carpeta_destino = '/app/data'

def extraer_tablas():
    tablas = ['genre', 'game','game_platform','game_publisher','platform','publisher','region','region_sales']
    carpeta_destino = '/app/data'

    os.makedirs(carpeta_destino, exist_ok=True)

    for tabla in tablas:
        df = pd.read_sql(f"SELECT * FROM {tabla}", con=engine)
        archivo_salida = os.path.join(carpeta_destino, f"{tabla}.csv")
        df.to_csv(archivo_salida, index=False)
        print(f"Tabla {tabla} exportada a {archivo_salida}")

extraer_tablas()

#Verificar la existencia de loa archivos exportados
for archivo in tablas:
    ruta_archivo = os.path.join(carpeta_destino, f"{archivo}.csv")
    
    if os.path.exists(ruta_archivo):
        print(f"El archivo {archivo} se ha descargado correctamente.")
        df = pd.read_csv(ruta_archivo)        
    else:
        print(f"El archivo {archivo} no se encuentra en la ruta {ruta_archivo}.")

@app.get("/games/genre")
async def get_shooter_games(genre: str):
    query = """
    SELECT game.game_name as nombre_juego, 
           platform.platform_name as plataforma,
           release_year as año_lanzamiento
    FROM game
    JOIN genre ON genre.id = game.genre_id
    JOIN game_publisher ON game_publisher.game_id = game.id
    JOIN game_platform ON game_platform.game_publisher_id = game_publisher.id
    JOIN platform ON platform.id = game_platform.platform_id
    WHERE genre.genre_name LIKE %s
    LIMIT 50;
    """
    try:
        genre_param = f"%{genre}%" 
        result = pd.read_sql(query, con=engine, params=(genre_param,))
        return result.to_dict(orient='records') 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a la base de datos: {e}")

@app.get("/games/year")
async def get_shooter_games(year: int = 2000,platform: str= ""):
    query = """
    SELECT 
    g.game_name, 
    p.platform_name, 
    gpl.release_year
    FROM game g
    INNER JOIN game_publisher gp ON g.id = gp.game_id
    INNER JOIN game_platform gpl ON gp.id = gpl.game_publisher_id
    INNER JOIN platform p ON gpl.platform_id = p.id
    WHERE gpl.release_year like %s
    AND p.platform_name like %s
    LIMIT 50;
    """
    try:
        result = pd.read_sql(query, con=engine, params=(f"%{year}%",f"%{platform}%"))
        return result.to_dict(orient='records') 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a la base de datos: {e}")
    
FIELD_QUERIES = {
"platform_name": "SELECT DISTINCT platform_name FROM platform",
"release_year": "SELECT DISTINCT release_year FROM game_platform ORDER BY release_year",
"publisher_name": "SELECT DISTINCT publisher_name FROM publisher",
"genre_name": "SELECT DISTINCT genre_name FROM genre",
"region_name": "SELECT DISTINCT region_name FROM region"
}

@app.get("/video_games/{field}")
async def get_field_values(field: str = Path(..., description="Campo a consultar")):
    query = FIELD_QUERIES.get(field)
    
    if not query:
        raise HTTPException(status_code=400, detail=f"Campo '{field}' no es válido. Usa uno de: {', '.join(FIELD_QUERIES.keys())}")
    
    try:
        result = pd.read_sql(query, con=engine)
        return result[field].dropna().unique().tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")

@app.get("/games/top_sales")
async def get_top_sales_by_region(region: str = "Japan", limit: int = 2):
    query = f"""
    SELECT 
        g.game_name, 
        SUM(rs.num_sales) AS total_sales
    FROM game g
    JOIN game_publisher gp ON g.id = gp.game_id
    JOIN game_platform gpl ON gp.id = gpl.game_publisher_id
    JOIN region_sales rs ON gpl.id = rs.game_platform_id
    JOIN region r ON rs.region_id = r.id
    WHERE r.region_name LIKE %s
    GROUP BY g.game_name
    ORDER BY total_sales DESC
    LIMIT {limit};
    """
    try:
        result = pd.read_sql(query, con=engine, params=(f"%{region}%",))
        return result.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/video_games/{field}")
async def get_field_values(field: str = Path(..., description="Campo a consultar")):
    query = FIELD_QUERIES.get(field)
    
    if not query:
        raise HTTPException(status_code=400, detail=f"Campo '{field}' no es válido. Usa uno de: {', '.join(FIELD_QUERIES.keys())}")
    
    try:
        result = pd.read_sql(query, con=engine)
        return result[field].dropna().unique().tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")

@app.get("/games/game")
async def get_top_sales_by_region(game: str = ""):
    query = f"""
    SELECT game_name,platform_name,release_year,genre_name
    FROM game,genre,game_publisher,game_platform,platform
    WHERE platform.id=game_platform.platform_id
    and game_publisher.id=game_platform.game_publisher_id
    AND game.id=game_publisher.game_id
    and genre.id=game.genre_id
    and game.game_name like %s;
    """
    try:
        result = pd.read_sql(query, con=engine, params=(f"%{game}%",))
        return result.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
