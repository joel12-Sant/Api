---------- Configuarcion
Solo debes de colocar el comando " docker compose up --build " en la terminal en la ruta donde extragiste el archivo

---------- EndPoint
1.- /games/gender?gender=               -> Esta primer consulta nos permite consultar todos los juegos existentes para un genero, nos regresa el nombre anio de lanzamiento y la plataforma 
2.- /games/year?year=  &platform=      -> Esta consulta nos permite consultar los juegos filtrandolos por anio y plataforma, nos regresas lo mismo que el anterior
3.- 

---------- Notas
los archivos.csv se guardan en la ruta /data que se crea de manera automatica al ejecutar el contenedor
