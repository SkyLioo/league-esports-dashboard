import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

DATA_FILE = "Data.xlsx"
ICON_DIR = Path("Icon_Champs")     # icônes champions
ITEM_DIR = Path("Icon_Items")      # icônes items
SPELL_DIR = Path("Icon_Spells")    # icônes summoner spells

st.set_page_config(page_title="League Esports Dashboard", layout="wide")

# mapping pour correspondre Excel → fichier PNG
SUMMONER_MAPPING = {
    "Flash": "SummonerFlash",
    "Ignite": "SummonerDot",
    "Teleport": "SummonerTeleport",
    "Smite": "SummonerSmite",
    "Exhaust": "SummonerExhaust",
    "Barrier": "SummonerBarrier",
    "Ghost": "SummonerHaste",
    "Cleanse": "SummonerBoost",
    "Heal": "SummonerHeal",
    "Clarity": "SummonerMana",
}


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    try:
        df = pd.read_excel(DATA_FILE)
        return df
    except Exception as e:
        st.error(f"❌ Impossible de charger {DATA_FILE}\n\n{e}")
        st.stop()

df = load_data()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚔️ Esports Data Dashboard")

# Sélection du joueur
player_selected = st.sidebar.selectbox(
    "Sélectionne un joueur :",
    sorted(df["Player's Name"].unique())
)

df_player = df[df["Player's Name"] == player_selected]

# ✅ juste le nom du champion dans la sidebar
df_player["Label Match"] = df_player["Champion Played"]

match_selected = st.sidebar.selectbox(
    "Sélectionne un match :",
    df_player["Label Match"].tolist()
)

df_match = df_player[df_player["Champion Played"] == match_selected].iloc[0]


# ============================================================
# MAIN PAGE
# ============================================================

st.title("📊 League of Legends - Match Review")

champ = df_match["Champion Played"]
icon_path = ICON_DIR / f"{champ}.png"

col1, col2 = st.columns([1, 2])

# ----------------- COLONNE 1 (icone + stats principales) -----------------
with col1:
    st.subheader("Champion")
    if icon_path.exists():
        st.image(str(icon_path), width=250)
    else:
        st.warning(f"⚠️ Icône introuvable : {champ}")

    st.markdown(f"**👤 Joueur :** {player_selected}")
    st.markdown(f"**🧩 Champion :** `{champ}`")
    st.metric("💰 GoldDiff @ 10", df_match["goldDiff@10"])
    st.metric("🌾 CSDiff @ 10", df_match["csDiff@10"])
    st.metric("🔥 KDA", df_match["KDA"])


# ----------------- COLONNE 2 (tableau + build + spells) -----------------
with col2:
    st.subheader("📋 Détails du match")

    # menu déroulant
    selected_category = st.selectbox(
        "Choisis le type de stats à afficher :",
        ["Vision", "Damage", "Farm / Gold", "Utility / Objectives", "Runes / Spells"]
    )

    stats_map = {
        "Vision": [
            "Vision Score",
            "Wards Placed",
            "Control Wards Placed",
            "Wards Killed",
        ],
        "Damage": [
            "Total Damage Dealt to Champions",
            "Total Damage Taken",
            "Total Damage Shielded Teammates",
            "Total Heals on Teammates",
        ],
        "Farm / Gold": [
            "Total Gold Earned",
            "Total Minions Killed",
            "Total Neutral Minions Killed",
            "Total Ally Jungle Minions Killed",
            "Total Enemy Jungle Minions Killed",
        ],
        "Utility / Objectives": [
            "Objectives Stolen",
            "Objectives Stolen Assists",
            "Number of Wards Bought",
        ],
        "Runes / Spells": [
            "Summoner Spell 1",
            "Summoner Spell 2",
            "Primary Perk Style",
            "Keystone Perk",
            "Secondary Perk Style",
        ],
    }

    st.dataframe(df_match[stats_map[selected_category]].to_frame())

    # ICONES — ITEMS ---------------------------------------------------------
    st.write("### 🛒 Build complet")

    item_cols = ["Item 0", "Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6"]

    item_icons = []
    for item in df_match[item_cols]:
        icon = ITEM_DIR / f"{item}.png"
        if icon.exists():
            item_icons.append(str(icon))

    st.image(item_icons, width=60)

    # ICONES — SUMMONER SPELLS ----------------------------------------------
    st.write("### ✨ Summoner Spells Used")

    summoner_cols = ["Summoner Spell 1", "Summoner Spell 2"]
    summoner_icons = []

    for spell in df_match[summoner_cols].values.flatten():
        spell_key = SUMMONER_MAPPING.get(spell)
        if spell_key:
            icon = SPELL_DIR / f"{spell_key}.png"
            if icon.exists():
                summoner_icons.append(str(icon))

    st.image(summoner_icons, width=60)


# ============================================================
# GRAPH — goldDiff@10 & csDiff@10
# ============================================================

st.write("---")
st.subheader("📈 Performance du joueur sur ses matchs récents")

chart_data = df_player[["Match ID", "goldDiff@10", "csDiff@10"]]

chart = (
    alt.Chart(chart_data)
    .transform_fold(["goldDiff@10", "csDiff@10"], as_=["Metric", "Value"])
    .mark_line(point=True)
    .encode(
        x=alt.X("Match ID:N", title="Match"),
        y=alt.Y("Value:Q", title="Différence"),
        color="Metric:N"
    )
)

st.altair_chart(chart, use_container_width=True)
