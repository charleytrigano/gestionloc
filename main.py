import streamlit as st

from utils.style import apply_style
from utils.auth import load_apartments
from utils.reservations import (
    afficher_reservations,
    ajouter_reservation_ui,
    modifier_reservation_ui,
    afficher_calendrier_google,
    afficher_statistiques
)

# ========================
# CONFIG
# ========================

st.set_page_config(
    page_title="GestionLoc",
    layout="wide"
)

apply_style()

# ========================
# TITRE
# ========================

st.markdown("# 🏠 GestionLoc")
st.markdown("### Liste des appartements disponibles")

# ========================
# APPARTEMENTS
# ========================

df_apts = load_apartments()

if df_apts.empty:
    st.warning("Aucun appartement trouvé. Ajoutez-en un dans le menu Appartements.")
    st.stop()

slugs = df_apts["slug"].tolist()
apt_dict = df_apts.set_index("slug")["nom"].to_dict()

slug = st.selectbox("Choisissez un appartement", slugs)
apt_nom = apt_dict.get(slug, slug)

st.markdown(f"**Appartement sélectionné :** `{apt_nom}`")

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
    ]
)

# ========================
# CONTENU
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