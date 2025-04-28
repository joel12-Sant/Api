import pymysql
import pandas as pd
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine    
from pymysql.cursors import DictCursor
import os

app = FastAPI()

MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')  
MYSQL_USER = os.getenv('MYSQL_USER', 'user')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password') 
MYSQL_DB = os.getenv('MYSQL_DB', 'video_games')  

def get_db_connection():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        cursorclass=DictCursor 
    )

def extraer_tablas():
    tablas = ['genre', 'game']
    carpeta_destino = '/app/data'

    os.makedirs(carpeta_destino, exist_ok=True)

    engine = create_engine(f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}')

    for tabla in tablas:
        df = pd.read_sql(f"SELECT * FROM {tabla}", con=engine)
        archivo_salida = os.path.join(carpeta_destino, f"{tabla}.csv")
        df.to_csv(archivo_salida, index=False)
        print(f"Tabla {tabla} exportada a {archivo_salida}")

    engine.close()  # Cerrar la conexión al final

extraer_tablas()


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
    WHERE genre.genre_name = %s
    LIMIT 50;
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query,(genre,))
            result = cursor.fetchall()  # Obtiene todos los resultados
        connection.close()
        return result
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a la base de datos: {e}")
