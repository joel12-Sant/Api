---------- Configuarcion
Solo debes de colocar el comando " docker compose up --build " en la terminal en la ruta donde extragiste el archivo (debes de tener instalado docker)


---------- EndPoint (desactualizado)
1.- /games/genre?genre=               -> Esta primer consulta nos permite consultar todos los juegos existentes para un genero, nos regresa el nombre anio de lanzamiento y la plataforma 
2.- /games/year?year= &platform=      -> Esta consulta nos permite consultar los juegos filtrandolos por anio y plataforma, nos regresas lo mismo que el anterior
3.- /video_games/{field}              -> En esta consulta puedes colocar en el field cuanlquiera de estas opciones que quieras consultar
[release_year,platform_name,region_name,genre_name,publisher_name] y te devolvera los valores de cada una para que puedas realizar el resto de consultas
4.- /games/top_sales?region= &limit=  -> Esta consulta te permite consultar el top juegos vendidos de cada region, puedes colocar el nonmre de la region y el limite que desees, se recomienda consultarlo con el anterior
5.- /games/name_game?game=            -> Esta consulta nos permite buscar un juego por su nombre o parecidos   
6.- /publishers/top?limit=            -> Esta consulta nos permite buscar las empresas que publicaron mas juegos, pudiendo modificar el limite


---------- Notas
los archivos.csv se guardan en la ruta /data que se crea de manera automatica al ejecutar el contenedor



joel12-San