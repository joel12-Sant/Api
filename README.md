# 📊 Video Games API

API para consultar y visualizar información sobre videojuegos, editoras, plataformas, ventas por región, géneros y años de lanzamiento. Construida con FastAPI, Pandas y SQL para generar tablas y gráficos dinámicos.

## 🚀 Tecnologías Utilizadas

- **FastAPI**: Framework para construir APIs web.
- **SQLAlchemy**: Conexión con base de datos MySQL.
- **Pandas**: Procesamiento de datos.
- **Matplotlib**: Visualización de datos en gráficos.
- **MySQL**: Base de datos que almacena la información de videojuegos.

## 📦 Endpoints

### 1. `/games/genre/grafic`
- **Método**: GET
- **Descripción**: Muestra una gráfica de barras de los juegos de un género, agrupados por plataforma.
- **Parámetros**:
  - `genre` (str): Nombre parcial del género (ej. `"Shooter"`).
  - `limit` (int): Número máximo de juegos a incluir (default: 20).

---

### 2. `/games/top_sales/grafic`
- **Método**: GET
- **Descripción**: Genera una gráfica de los juegos más vendidos en una región.
- **Parámetros**:
  - `region` (str): Nombre de la región (ej. `"Europe"`).
  - `limit` (int): Número máximo de juegos a mostrar (default: 10).

---

### 3. `/publishers/top/{limit}/grafic`
- **Método**: GET
- **Descripción**: Muestra las editoras con más juegos publicados en una gráfica.
- **Parámetros**:
  - `limit` (int): Número de editoras a mostrar.

---

### 4. `/games/genre/table`
- **Método**: GET
- **Descripción**: Devuelve una tabla HTML con juegos filtrados por género.
- **Parámetros**:
  - `genre` (str): Género a filtrar.
  - `limit` (int): Número máximo de registros.

---

### 5. `/games/year/table`
- **Método**: GET
- **Descripción**: Devuelve una tabla HTML de juegos por año y plataforma.
- **Parámetros**:
  - `year` (str): Año a filtrar.
  - `platform` (str): Plataforma a filtrar.
  - `limit` (int): Cantidad máxima de resultados.

---

### 6. `/games/top_sales/table`
- **Método**: GET
- **Descripción**: Tabla HTML de los juegos más vendidos por región.
- **Parámetros**:
  - `region_name` (str): Nombre de la región.
  - `limit` (int): Número de juegos a mostrar.

---

### 7. `/games/genre`
- **Método**: GET
- **Descripción**: Lista juegos filtrados por género.
- **Parámetros**:
  - `genre` (str): Género a buscar.
  - `limit` (int): Número de resultados.

---

### 8. `/games/year`
- **Método**: GET
- **Descripción**: Lista juegos por año y plataforma.
- **Parámetros**:
  - `year` (int): Año de lanzamiento.
  - `platform` (str): Plataforma.

---

### 9. `/video_games/{field}`
- **Método**: GET
- **Descripción**: Lista los valores únicos de un campo (género, plataforma, año, etc.).
- **Parámetro**:
  - `field` (str): Campo a consultar (`platform_name`, `release_year`, etc.).

---

### 10. `/games/top_sales`
- **Método**: GET
- **Descripción**: Lista los juegos más vendidos por región.
- **Parámetros**:
  - `region` (str): Nombre de la región.
  - `limit` (int): Número de resultados.

---

### 11. `/game`
- **Método**: GET
- **Descripción**: Filtro múltiple por juego, plataforma y año.
- **Parámetros**:
  - `game` (str): Nombre parcial del juego.
  - `platform` (str): Nombre de la plataforma.
  - `year` (str): Año de lanzamiento.

---

### 12. `/publishers/top/{limit}`
- **Método**: GET
- **Descripción**: Lista las editoras con más juegos publicados.
- **Parámetro**:
  - `limit` (int): Número de editoras a mostrar.

## 📁 Archivos Exportados

Las tablas de la base de datos se exportan como archivos `.csv` en `/app/data` automáticamente al iniciar la aplicación.

## ⚙️ Variables de Entorno

Asegúrate de configurar las siguientes variables de entorno en tu archivo `.env`:

- `MYSQL_HOST` – Dirección del servidor MySQL.
- `MYSQL_USER` – Usuario de la base de datos.
- `MYSQL_PASSWORD` – Contraseña de la base de datos.
- `MYSQL_DB` – Nombre de la base de datos.

## 📈 Visualizaciones

Todas las gráficas son generadas usando `matplotlib` y se devuelven como imágenes PNG listas para integrar en frontend o dashboards.

## 🧪 Ejecución

Puedes probar los endpoints interactivos usando Swagger UI:  
`http://localhost:8000/docs`

## ©️ Derechos de autor

© 2025 joel12-Sant. Todos los derechos reservados.
