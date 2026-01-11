




import streamlit as st
from utils.style import apply_style
from utils.auth import load_apartments
from utils.reservations import (
    load_reservations,
    afficher_reservations,
    ajouter_reservation_ui,
    modifier_reservation_ui,
    afficher_calendrier_google,
    afficher_statistiques
from utils.auth import gestion_appartements_ui

)
from analyse import afficher_analyse_financiere

st.set_page_config(page_title="GestionLoc", layout="wide")
apply_style()

st.markdown("# 🏠 GestionLoc")
st.markdown("### Liste des appartements disponibles :")

df_apts = load_apartments()
if df_apts.empty:
    st.error("Aucun appartement trouvé dans apartments.csv.")
    st.stop()

slugs = df_apts["slug"].tolist()
apt_dict = df_apts.set_index("slug")["nom"].to_dict()

slug = st.selectbox("Choisissez un appartement", slugs)
apt_nom = apt_dict.get(slug, slug)
st.markdown(f"**Appartement sélectionné :** `{apt_nom}`")

onglet = st.sidebar.radio("Navigation", [
    "📋 Réservations",
    "➕ Ajouter",
    "✏️ Modifier",
    "📅 Calendrier",
    "📈 Statistiques",
    "💹 Analyse financière"
])

if onglet == "📋 Réservations":
    afficher_reservations(slug)

elif onglet == "➕ Ajouter":
    ajouter_reservation_ui(slug)

elif onglet == "✏️ Modifier":
    modifier_reservation_ui(slug)

elif onglet == "📅 Calendrier":
    afficher_calendrier_google(slug)

elif onglet == "📈 Statistiques":
    afficher_statistiques(slug)

elif onglet == "💹 Analyse financière":
    afficher_analyse_financiere(slug)

elif onglet == "🏢 Appartements":
    gestion_appartements_ui()


from utils.auth import gestion_appartements_ui  # importer la nouvelle fonction

# Onglet Navigation
onglet = st.sidebar.radio("Navigation", [
    "📋 Réservations",
    "➕ Ajouter",
    "✏️ Modifier / Supprimer",
    "📅 Calendrier",
    "📈 Statistiques",
    "🏢 Appartements"  # <== nouveau
])

# Affichage des pages
if onglet == "📋 Réservations":
    afficher_reservations(slug)

elif onglet == "➕ Ajouter":
    ajouter_reservation_ui(slug)

elif onglet == "✏️ Modifier / Supprimer":
    modifier_reservation_ui(slug)

elif onglet == "📅 Calendrier":
    afficher_calendrier_google(slug)

elif onglet == "📈 Statistiques":
    afficher_analyse_financiere(slug)  # ou afficher_statistiques(slug)

elif onglet == "🏢 Appartements":
    gestion_appartements_ui()


