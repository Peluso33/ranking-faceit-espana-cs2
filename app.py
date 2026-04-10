import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="🇪🇸 Ranking Faceit CS2 España", layout="wide", page_icon="🇪🇸")
st.title("🇪🇸 Ranking Faceit CS2 - Jugadores Españoles")
st.caption(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Datos oficiales de Faceit")

# Cargar datos
@st.cache_data(ttl=3600)  # recarga cada hora
def load_data():
    try:
        with open("ranking_espana_cs2.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Convertir map_stats (que es string en JSON) a diccionario
        df["map_stats"] = df["map_stats"].apply(lambda x: json.loads(x) if isinstance(x, str) else x)
        return df
    except:
        st.error("No se encontró el archivo ranking_espana_cs2.json. Ejecuta el workflow primero.")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# Filtros
col1, col2, col3 = st.columns(3)
with col1:
    min_elo = st.slider("ELO mínimo", int(df["elo"].min()), int(df["elo"].max()), 1800)
with col2:
    min_level = st.slider("Nivel mínimo", 1, 10, 7)
with col3:
    search = st.text_input("🔎 Buscar jugador por nickname", "")

# Filtrar datos
filtered = df[(df["elo"] >= min_elo) & (df["level"] >= min_level)]
if search:
    filtered = filtered[filtered["nickname"].str.contains(search, case=False)]

st.dataframe(
    filtered[["position", "nickname", "level", "elo", "lifetime_matches"]].sort_values("elo", ascending=False),
    use_container_width=True,
    hide_index=True
)

st.divider()

# Gráfico winrate promedio por mapa (Top 50)
st.subheader("📊 Winrate promedio por mapa (Top 50 jugadores)")
top50 = filtered.nlargest(50, "elo")

map_winrates = {}
for maps in top50["map_stats"]:
    if isinstance(maps, dict):
        for m, stats in maps.items():
            if m not in map_winrates:
                map_winrates[m] = []
            try:
                wr = float(str(stats.get("winrate", 0)).replace("%", ""))
                map_winrates[m].append(wr)
            except:
                pass

if map_winrates:
    avg_map = {m: round(sum(v)/len(v), 1) for m, v in map_winrates.items() if v}
    map_df = pd.DataFrame(list(avg_map.items()), columns=["Mapa", "Winrate %"]).sort_values("Winrate %", ascending=False)
    st.bar_chart(map_df.set_index("Mapa"))
else:
    st.info("No hay datos de mapas todavía.")

# Detalle de un jugador
st.subheader("🔎 Estadísticas detalladas de un jugador")
if not filtered.empty:
    selected = st.selectbox("Elige un jugador", options=filtered["nickname"].tolist())
    player = filtered[filtered["nickname"] == selected].iloc[0]

    st.write(f"**Posición:** {player['position']} | **ELO:** {player['elo']} | **Nivel:** {player['level']} | **Partidas:** {player['lifetime_matches']}")

    if player["map_stats"] and isinstance(player["map_stats"], dict):
        map_player = []
        for m, stats in player["map_stats"].items():
            map_player.append({
                "Mapa": m,
                "Winrate %": stats.get("winrate", "N/A"),
                "K/D": stats.get("kd", "N/A"),
                "Rounds": stats.get("rounds", "N/A")
            })
        map_df_player = pd.DataFrame(map_player)
        st.dataframe(map_df_player.sort_values("Winrate %", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("Este jugador no tiene stats de mapas todavía.")
