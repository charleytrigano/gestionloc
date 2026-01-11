import streamlit as st
from utils.reservations import (
    load_reservations,
    afficher_reservations,
    ajouter_reservation_ui,
    modifier_reservation_ui,
    afficher_calendrier_google,
    afficher_statistiques,
    afficher_analyse_financiere,
)

# ========================
# CONFIG
# ========================

st.set_page_config(
    page_title="GestionLoc",
    layout="wide"
)

st.title("🏠 GestionLoc")

# ========================
# CHOIX APPARTEMENT
# ========================

st.subheader("Liste des appartements disponibles")

# 👉 ici on liste les CSV présents dans /data
import os

DATA_DIR = "data"
slugs = []

if os.path.exists(DATA_DIR):
    for f in os.listdir(DATA_DIR):
        if f.startswith("reservations_") and f.endswith(".csv"):
            slugs.append(f.replace("reservations_", "").replace(".csv", ""))

if not slugs:
    st.warning("Aucun appartement trouvé (aucun fichier reservations_*.csv)")
    st.stop()

slug = st.selectbox("Choisissez un appartement", slugs)
st.markdown(f"**Appartement sélectionné :** `{slug}`")

# ========================
# NAVIGATION
# ========================

onglet = st.sidebar.radio(
    "Navigation",
    [
        "📋 Réservations",
        "➕ Ajouter",
        "✏️ Modifier / Supprimer",
        "📅 Calendrier",
        "📈 Statistiques",
        "💼 Analyse Financière",
    ]
)

# ========================
# AFFICHAGE
# ========================

if onglet == "📋 Réservations":
    afficher_reservations(slug)

elif onglet == "➕ Ajouter":
    ajouter_reservation_ui(slug)

elif onglet == "✏️ Modifier / Supprimer":
    modifier_reservation_ui(slug)

elif onglet == "📅 Calendrier":
    afficher_calendrier_google(slug)

elif onglet == "📈 Statistiques":
    afficher_statistiques(slug)

elif onglet == "💼 Analyse Financière":
    afficher_analyse_financiere(slug)