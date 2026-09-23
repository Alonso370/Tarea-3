"""Página de presentación musical. Los contenedores están listos para gráficas."""

from pathlib import Path
from html import escape
import ast
import csv
import json
import random

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Atlas musical", page_icon="🎵", layout="wide")
st.html(f"<style>{Path(__file__).with_name('styles.css').read_text(encoding='utf-8')}</style>")

st.html('''
<header class="masthead">
  <span class="brand">◉ &nbsp; ATLAS MUSICAL</span>
  <span class="masthead-note">Una exploración del sonido</span>
</header>
<div class="intro">
  <p class="eyebrow">MÚSICA · PERFILES · POPULARIDAD</p>
  <h1>La música, desde<br><span>otra perspectiva.</span></h1>
  <p class="intro-copy">Cuatro preguntas para explorar las canciones, sus artistas y lo que los conecta.</p>
</div>
''')

SECTIONS = [
    ("01", "A TRAVÉS DEL TIEMPO", "¿Cómo ha evolucionado el perfil musical y la popularidad de las canciones a través de las décadas?", "Evolución por décadas"),
    ("02", "EL UNIVERSO DE LAS CANCIONES", "¿Cómo se distribuyen las canciones según su perfil musical y nivel de popularidad?", "Distribución de canciones"),
    ("03", "LA IDENTIDAD DE LOS ARTISTAS", "¿Cómo se diferencian los perfiles musicales de los artistas pertenecientes a distintos géneros y qué características explican esas diferencias?", "Comparación de artistas y géneros"),
    ("04", "CONEXIONES MUSICALES", "¿Qué patrones globales de similitud y diferencia existen entre las canciones a partir de sus características musicales?", "Similitudes y diferencias entre canciones"),
]


def chart_placeholder(label: str) -> None:
    """Sustituye esta llamada por tu gráfica cuando esté lista."""
    st.html(f'''
    <div class="chart-placeholder" role="region" aria-label="{escape(label)}: espacio reservado">
      <span class="placeholder-symbol" aria-hidden="true">＋</span>
      <span class="placeholder-title">{escape(label)}</span>
      <span class="placeholder-note">Espacio reservado para la visualización</span>
    </div>
    ''')


def read_rows(filename: str) -> list[dict]:
    with (Path(__file__).parent / "data" / filename).open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


SONG_FEATURES = ["energy", "danceability", "valence", "acousticness", "instrumentalness", "speechiness", "tempo"]
SAMPLE_SIZE = 15000


@st.cache_data
def song_sample() -> dict:
    """Muestra aleatoria (semilla fija) de data.csv en formato columnas + filas, más n, sumas y
    productos cruzados de las variables sobre TODAS las canciones (para sus correlaciones)."""
    k = len(SONG_FEATURES)
    n, sums, cross, songs = 0, [0.0] * k, [[0.0] * k for _ in range(k)], []
    for row in read_rows("data.csv"):
        try:
            v = [float(row[key]) for key in SONG_FEATURES]
            popularity = int(float(row["popularity"]))
        except (KeyError, ValueError):
            continue
        n += 1
        for i in range(k):
            sums[i] += v[i]
            vi, ci = v[i], cross[i]
            for j in range(i, k):
                ci[j] += vi * v[j]
        artists = row.get("artists", "").strip("[]").replace("'", "").replace('"', "")
        songs.append([*(round(x, 4) for x in v), popularity, row.get("name", ""), artists])
    for i in range(k):
        for j in range(i):
            cross[i][j] = cross[j][i]
    sample = random.Random(42).sample(songs, min(SAMPLE_SIZE, len(songs)))
    return {"columns": [*SONG_FEATURES, "popularity", "name", "artists"], "rows": sample,
            "moments": {"n": n, "features": SONG_FEATURES, "sums": sums, "cross": cross}}


STAR_FEATURES = ["energy", "danceability", "valence", "acousticness", "instrumentalness", "speechiness", "tempo"]


@st.cache_data
def star_artists() -> dict:
    """Artistas de data_w_genres.csv con al menos un género (lista original) y sus 7 características
    promedio, en formato compacto columnas + filas. La familia musical de cada artista se asigna en
    charts/grafica_03.js (genreFamily / artistFamily)."""
    rows = []
    for row in read_rows("data_w_genres.csv"):
        try:
            genres = ast.literal_eval(row["genres"])
            values = [round(float(row[key]), 4) for key in STAR_FEATURES]
        except (KeyError, ValueError, SyntaxError):
            continue
        if genres:
            rows.append([row["artists"], list(genres), *values])
    return {"columns": ["artists", "genres", *STAR_FEATURES], "rows": rows}


PCA_FEATURES = ["energy", "danceability", "valence", "acousticness", "instrumentalness", "speechiness", "tempo", "loudness"]


@st.cache_data
def song_pca_data() -> dict:
    """Para el PCA de la gráfica 04: sumas y productos cruzados de las 8 variables sobre TODAS las
    canciones de data.csv (media, desviación y correlaciones exactas) + una muestra aleatoria para dibujar."""
    k = len(PCA_FEATURES)
    n, sums, cross, songs = 0, [0.0] * k, [[0.0] * k for _ in range(k)], []
    for row in read_rows("data.csv"):
        try:
            v = [float(row[key]) for key in PCA_FEATURES]
            popularity = int(float(row["popularity"]))
        except (KeyError, ValueError):
            continue
        n += 1
        for i in range(k):
            sums[i] += v[i]
            vi, ci = v[i], cross[i]
            for j in range(i, k):
                ci[j] += vi * v[j]
        artists = row.get("artists", "").strip("[]").replace("'", "").replace('"', "")
        songs.append([*(round(x, 4) for x in v), popularity, row.get("name", ""), artists])
    for i in range(k):
        for j in range(i):
            cross[i][j] = cross[j][i]
    sample = random.Random(42).sample(songs, min(SAMPLE_SIZE, len(songs)))
    return {"n": n, "features": PCA_FEATURES, "sums": sums, "cross": cross,
            "columns": [*PCA_FEATURES, "popularity", "name", "artists"], "rows": sample}


def d3_chart(filename: str, rows: list[dict] | dict, height: int = 790) -> None:
    """Inserta el JavaScript local en una plantilla que carga D3."""
    folder = Path(__file__).parent / "charts"
    template = (folder / "chart.html").read_text(encoding="utf-8")
    javascript = (folder / filename).read_text(encoding="utf-8")
    payload = json.dumps(rows, ensure_ascii=True).replace("<", "\\u003c")
    html = template.replace("/* CHART_SCRIPT */", javascript).replace("<!-- CHART_DATA -->", f'<script id="chart-data" type="application/json">{payload}</script>')
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:
        components.html(html, height=height, scrolling=True)


for number, category, question, label in SECTIONS:
    with st.container(key=f"section-{number}"):
        st.html(f'''
        <div class="section-heading">
          <span class="section-number">{number}</span>
          <div>
            <p class="eyebrow">{category}</p>
            <h2>{escape(question)}</h2>
          </div>
        </div>
        ''')
        if number == "01":
            d3_chart("grafica_01.js", read_rows("data_by_year.csv"))
        elif number == "02":
            d3_chart("grafica_02.js", song_sample(), height=800)
        elif number == "03":
            d3_chart("grafica_03.js", star_artists(), height=780)
        elif number == "04":
            d3_chart("grafica_04.js", song_pca_data(), height=760)
        else:
            chart_placeholder(label)

st.html('<footer><span>◉ &nbsp; ATLAS MUSICAL</span><span>Cuatro preguntas. Muchas formas de escuchar.</span></footer>')
