import streamlit as st
from utils.style import apply_style
from utils.auth import load_apartments, gestion_appartements_ui
from utils.reservations import (
    load_reservations,
    afficher_reservations,
    ajouter_reservation_ui,
    modifier_reservation_ui,
    afficher_calendrier_google,
    afficher_statistiques
)
from analyse import afficher_analyse_financiere

# Configuration de la page
st.set_page_config(page_title="GestionLoc", layout="wide")
apply_style()

st.markdown("# 🏠 GestionLoc")
st.markdown("### Liste des appartements disponibles :")

# Chargement des appartements
df_apts = load_apartments()

if df_apts.empty:
    st.warning("Aucun appartement trouvé. Veuillez en ajouter dans l'onglet 🏢 Appartements.")
    slug = None
else:
    slugs = df_apts["slug"].tolist()
    apt_dict = df_apts.set_index("slug")["nom"].to_dict()

    slug = st.selectbox("Choisissez un appartement", slugs)
    apt_nom = apt_dict.get(slug, slug)

    st.markdown(f"**Appartement sélectionné :** `{apt_nom}`")

# Navigation par onglet
onglet = st.sidebar.radio("Navigation", [
    "📋 Réservations",
    "➕ Ajouter",
    "✏️ Modifier / Supprimer",
    "📅 Calendrier",
    "📈 Statistiques",
    "💼 Analyse Financière",
    "🏢 Appartements"
])

# Affichage des écrans selon l’onglet sélectionné
if onglet == "📋 Réservations":
    if slug:
        afficher_reservations(slug)

elif onglet == "➕ Ajouter":
    if slug:
        ajouter_reservation_ui(slug)

elif onglet == "✏️ Modifier / Supprimer":
    if slug:
        modifier_reservation_ui(slug)

elif onglet == "📅 Calendrier":
    if slug:
        afficher_calendrier_google(slug)

elif onglet == "📈 Statistiques":
    if slug:
        afficher_statistiques(slug)

elif onglet == "💼 Analyse Financière":
    if slug:
        afficher_analyse_financiere(slug)

elif onglet == "🏢 Appartements":
    gestion_appartements_ui()
