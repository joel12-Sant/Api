import pandas as pd
from fastapi import FastAPI, HTTPException,Path
from fastapi.responses import HTMLResponse,Response,StreamingResponse
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from io import BytesIO
import os

app = FastAPI()

#Variables de entorno
MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')  
MYSQL_USER = os.getenv('MYSQL_USER', 'user')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password') 
MYSQL_DB = os.getenv('MYSQL_DB', 'video_games')

#Conexion a la base de datos
engine = create_engine(f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}')

#Definicion de Variables
FIELD_QUERIES = {
"platform_name": "SELECT DISTINCT platform_name FROM platform",
"release_year": "SELECT DISTINCT release_year FROM game_platform ORDER BY release_year",
"publisher_name": "SELECT DISTINCT publisher_name FROM publisher",
"genre_name": "SELECT DISTINCT genre_name FROM genre",
"region_name": "SELECT DISTINCT region_name FROM region"
}
tablas = ['genre', 'game','game_platform','game_publisher','platform','publisher','region','region_sales']
carpeta_destino = '/app/data'

#Exportacion de archivos
def extraer_tablas():
    os.makedirs(carpeta_destino, exist_ok=True)
    for tabla in tablas:
        df = pd.read_sql(f"SELECT * FROM {tabla}", con=engine)
        archivo_salida = os.path.join(carpeta_destino, f"{tabla}.csv")
        df.to_csv(archivo_salida, index=False)
        print(f"Tabla {tabla} exportada a {archivo_salida}")
extraer_tablas()

#Verificar la existencia de loa archivos exportados y asignacion
df = {}
for archivo in tablas:
    ruta_archivo = os.path.join(carpeta_destino, f"{archivo}.csv")
    
    if os.path.exists(ruta_archivo):
        print(f"El archivo {archivo} se ha descargado correctamente.")
        d = pd.read_csv(ruta_archivo)        
        df[archivo] = d 
    else:
        print(f"El archivo {archivo} no se encuentra en la ruta {ruta_archivo}.")

df_game = df["game"]
df_genre = df["genre"]
df_game_pub = df["game_publisher"]
df_game_platform = df["game_platform"]
df_platform = df["platform"]
df_region = df["region"]
df_region_sales = df["region_sales"]
df_publisher = df["publisher"]

#Consultas Grafica
@app.get("/games/genre/grafic")
def get_genre_games_chart(genre: str = "", limit: int = 20):
    #consulta echa con pandas
    try:
        merged = df_game.merge(
            df_genre, 
            left_on="genre_id", 
            right_on="id", 
            suffixes=("", "_genre")
        )
        merged = merged.merge(
            df_game_pub, 
            left_on="id", 
            right_on="game_id"
        )
        merged = merged.merge(
            df_game_platform, 
            left_on="id_y", 
            right_on="game_publisher_id"
        )
        merged = merged.merge(
            df_platform, 
            left_on="platform_id", 
            right_on="id", 
            suffixes=("", "_platform")
        )
        filtro = merged["genre_name"].str.contains(genre, case=False, na=False)
        resultado = merged.loc[filtro, ["game_name", "platform_name", "release_year"]]
        resultado = resultado.head(limit)
        conteo = resultado["platform_name"].value_counts()
        fig, ax = plt.subplots(figsize=(8, 4))
        conteo.plot(kind="bar", color="green", ax=ax)
        ax.set_title(f"Juegos del género '{genre}' por plataforma")
        ax.set_xlabel("Plataforma")
        ax.set_ylabel("Cantidad de juegos")
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)  
        plt.close()
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar gráfico: {e}")
    
@app.get("/games/top_sales/grafic")
def get_top_sales_chart(region: str = "", limit: int = 10):
    #consulta echa con mysql
    query = """
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
    LIMIT %s;
    """
    try:
        region_param=f"{region}%"
        with engine.connect() as connection:
            df = pd.read_sql(query, con=engine, params=(region_param, limit))
        if df.empty:
            raise HTTPException(status_code=404, detail="No se encontraron resultados para esa región.")

        fig, ax = plt.subplots(figsize=(10, 5))
        df.set_index("game_name")["total_sales"].plot(kind="barh", ax=ax, color="skyblue")
        ax.set_title(f"Top {limit} juegos más vendidos en región '{region}'")
        ax.set_xlabel("Ventas totales (millones)")
        ax.set_ylabel("Juego")
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar gráfico: {e}")

@app.get("/publishers/top/{limit}/grafic")
def get_top_publishers_chart(limit: int = 10):
    #consulta echa con pandas
    try:
        merged = df_game_pub.merge(
            df_publisher, 
            left_on="publisher_id", 
            right_on="id"
        )
        
        conteo = merged.groupby("publisher_name")["game_id"].nunique().sort_values(ascending=False).head(limit)

        fig, ax = plt.subplots(figsize=(10, 5))
        conteo.plot(kind="bar", color="orange", ax=ax)
        ax.set_title(f"Top {limit} editoras por cantidad de juegos publicados")
        ax.set_ylabel("Cantidad de juegos")
        ax.set_xlabel("Editora")
        plt.xticks(rotation=60, ha='right')
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()
        return StreamingResponse(buf, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar gráfico: {e}")

#Consultas de Tablas
@app.get("/games/genre/table",response_class=HTMLResponse)
def get_genre_html(genre: str = "",limit: int = 20):
    #consulta echa con pandas
    try:
        merged = df_game.merge(
        df_genre,
        left_on="genre_id",
        right_on="id",
        suffixes=("", "_genre")
        )
        merged = merged.merge(
            df_game_pub,
            left_on="id",           
            right_on="game_id", 
            suffixes=("", "_gp")
        )
        merged = merged.merge(
            df_game_platform,
            left_on="id_gp",       
            right_on="game_publisher_id",
            suffixes=("", "_gplat")
        )
        merged = merged.merge(
            df_platform,
            left_on="platform_id",
            right_on="id",
            suffixes=("", "_platform")
        )
        filtro = merged["genre_name"].str.contains(genre, case=False, na=False)
        resultado = merged.loc[filtro, ["game_name", "platform_name", "release_year"]]
        resultado = resultado.head(limit).to_html(index=False)
        return HTMLResponse(content=resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/games/year/table",response_class=HTMLResponse)
async def get_year(year: str = "2000",platform: str= "",limit: int=20):
    #Consulta echa con pandas
    try:
        merged = df_game.merge(
        df_game_pub,
        left_on="id",
        right_on="game_id",
        suffixes=("","_gp") 
        )
        merged = merged.merge(
            df_game_platform,
            left_on="id_gp",
            right_on="game_publisher_id",
            suffixes=("","_gplat") 
        )
        merged = merged.merge(
            df_platform,
            left_on="platform_id",
            right_on="id",
            suffixes=("","_platform") 
        )
        filtro = merged["release_year"].astype(str).str.contains(year,case=False,na=False) & \
                merged["platform_name"].str.contains(platform,case=False,na=False) 
        resultado = merged.loc[filtro,["game_name","platform_name","release_year"]] 
        resultado = resultado.head(limit).to_html(index=False)
        return HTMLResponse(content=resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@app.get("/games/top_sales/table",response_class=HTMLResponse)
def get_total_sale(region_name: str = "", limit: int = 10):
    #consulta echa con pandas
    try:
        merged = df_game.merge(
            df_game_pub, 
            left_on="id", 
            right_on="game_id", 
            suffixes=("", "_gp")
        )
        merged = merged.merge(
            df_game_platform, 
            left_on="id_gp",
            right_on="game_publisher_id",
            suffixes=("", "_gplat")
        )
        merged = merged.merge(
            df_region_sales, 
            left_on="id_gplat", 
            right_on="game_platform_id", 
            suffixes=("", "_rs")
        )
        merged = merged.merge(
            df_region, 
            left_on="region_id", 
            right_on="id", 
            suffixes=("", "_reg")
        )
        filtro = merged["region_name"].str.contains(region_name, case=False, na=False)
        filtered_data = merged.loc[filtro]
        total_sales = filtered_data.groupby("game_name")["num_sales"].sum().reset_index()
        total_sales = total_sales.sort_values(by="num_sales", ascending=False)
        total_sales = total_sales.head(limit).to_html(index=False)
        return HTMLResponse(content=total_sales)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener ventas: {e}")

#Consultas Basicas
@app.get("/games/genre")
async def get_shooter_games(genre: str = "",limit: int = 20):
    #consulta echa con sql
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
    LIMIT %s;
    """
    try:
        genre_param = f"%{genre}%"
        with engine.connect() as connection:
            result = pd.read_sql(query, con=engine, params=(genre_param,limit))
        return result.to_dict(orient='records') 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a la base de datos: {e}")

@app.get("/games/year")
async def get_shooter_games(year: int = 2000,platform: str= ""):
    #consulta echa con sql
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
        year_param = f"%{year}%"
        platform_param= f"%{platform}%"
        with engine.connect() as connection:
            result = pd.read_sql(query, con=engine, params=(year_param,platform_param,))
        return result.to_dict(orient='records') 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a la base de datos: {e}")

@app.get("/video_games/{field}")
async def get_field_values(field: str = Path(..., description="Campo a consultar")):
    #conulta echa con sql usando los field_queries declarados al inicio
    query = FIELD_QUERIES.get(field)
    if not query:
        raise HTTPException(status_code=400, detail=f"Campo '{field}' no es válido. Usa uno de: {', '.join(FIELD_QUERIES.keys())}")
    try:
        with engine.connect() as connection:
            result = pd.read_sql(query, con=engine)
        return result[field].dropna().unique().tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {e}")

@app.get("/games/top_sales")
async def get_top_sales_by_region(region: str = "", limit: int = 5):
    #consulta echa con sql
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
    LIMIT %s;
    """
    try:
        region_param=f"{region}%"
        with engine.connect() as connection: 
            result = pd.read_sql(query, con=engine, params=(region_param,limit,))
        return result.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/game")
async def get_top_sales_by_regions(
        game: str = "",
        platform: str="",
        year: str = "",
    ):
    #consulta echa con sql
    query = """
    SELECT game_name,platform_name,release_year,genre_name
    FROM game,genre,game_publisher,game_platform,platform
    WHERE platform.id=game_platform.platform_id
    and game_platform.release_year like %s
    and platform.platform_name like %s 
    and game_publisher.id=game_platform.game_publisher_id
    AND game.id=game_publisher.game_id
    and genre.id=game.genre_id
    and game.game_name like %s
    LIMIT 100;
    """
    try:
        year_param = f"%{year}%"
        platform_param = f"%{platform}%" 
        game_param = f"%{game}%"
        with engine.connect() as connection: 
            result = pd.read_sql(query, con=engine, params=(year_param,platform_param,game_param,))
        return result.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/publishers/top/{limit}")
async def get_top_publishers(limit: int = 10):
    #consulta echa con sql
    query = """
    SELECT 
        pub.publisher_name,
        COUNT(DISTINCT gp.game_id) AS total_games
    FROM publisher pub
    JOIN game_publisher gp ON pub.id = gp.publisher_id
    GROUP BY pub.publisher_name
    ORDER BY total_games DESC
    LIMIT %s;
    """
    try:
        with engine.connect() as connection:
            result = pd.read_sql(query, con=engine, params=(limit,))
        return result.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
