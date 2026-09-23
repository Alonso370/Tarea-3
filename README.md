# Atlas musical

Aplicación Streamlit con cuatro secciones. La primera contiene coordenadas paralelas D3 con datos reales; las demás conservan espacios reservados.

## Ejecutar

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Para una instalación nueva: `python -m pip install -r requirements.txt`, después `python -m streamlit run app.py`.

## Gráfica 01

- Edita `charts/grafica_01.js` para cambiar la agregación, escalas, colores e interacciones. Es JavaScript sin etiquetas script.
- `app.py` lee `data/data_by_year.csv` y pasa los registros al componente como JSON. No se requiere servidor adicional para los CSV.
- `charts/chart.html` carga D3 7.9.0 por CDN y contiene la plantilla y estilos generales. Requiere internet.
- Guarda y recarga la página para aplicar los cambios de JavaScript.

Cada línea representa la media aritmética de los valores anuales disponibles de una década. No es una media ponderada por número de canciones. Los datos comienzan en 1921: 1920s incluye nueve años; 1930s–2010s incluyen diez y 2020 incluye solo ese año. Los valores ausentes se omiten por variable y n indica el número de años válidos.

Ejes: Períodos, Acousticness, Energy, Loudness (dB), Danceability, Valence, Tempo (BPM) y Popularity. Cada eje tiene una escala independiente. Períodos es categórico. Las siete variables se promedian; el período se asigna a partir de year.

Interacciones: arrastrar los títulos para reordenar ejes (también con Tab y flechas); hover para década y valores; clic en una línea o botón para seleccionarla y atenuar el resto; segundo clic o Mostrar todas para quitar la selección; Restablecer ejes para volver al orden inicial. En pantallas estrechas se puede desplazar horizontalmente el gráfico.

Los cinco CSV del ZIP están guardados en `data/` para las siguientes gráficas.

Referencias: [D3 drag](https://d3js.org/d3-drag), [Streamlit components](https://docs.streamlit.io/develop/concepts/custom-components/components-v1/intro).
