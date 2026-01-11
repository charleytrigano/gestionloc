import os
import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
from streamlit_calendar import calendar
import plotly.express as px

# ========================
# CHARGEMENT DES INDICATIFS
# ========================
@st.cache_data
def load_indicatifs():
    path = "data/indicatifs_pays.csv"
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=["Indicatif", "Pays", "Drapeau", "Code ISO"])

indicatifs_df = load_indicatifs()

# ========================
# GESTION FICHIERS CSV
# ========================
def reservations_path(slug: str) -> str:
    return f"data/reservations_{slug}.csv"

def load_reservations(slug: str) -> pd.DataFrame:
    path = reservations_path(slug)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=[
        "nom_client", "plateforme", "telephone",
        "date_arrivee", "date_depart", "nuitees",
        "prix_brut", "prix_net", "paye", "pays",
        "commissions"
    ])

def save_reservations(slug: str, df: pd.DataFrame):
    df.to_csv(reservations_path(slug), index=False)

# ========================
# DÉTECTION PAYS
# ========================
def detect_pays(telephone: str) -> str:
    for _, row in indicatifs_df.iterrows():
        indicatif = str(row["Indicatif"]).replace("-", "").replace("/", "")
        if telephone.startswith(indicatif):
            return f"{row['Drapeau']} {row['Pays']}"
    return "❓ Inconnu"

# ========================
# AFFICHER LES RÉSERVATIONS
# ========================
def afficher_reservations(slug: str):
    st.subheader("📋 Réservations")
    df = load_reservations(slug)
    if df.empty:
        st.info("Aucune réservation.")
    else:
        st.dataframe(df, use_container_width=True)

# ========================
# AJOUTER UNE RÉSERVATION
# ========================
def ajouter_reservation_ui(slug: str):
    st.subheader("➕ Ajouter une réservation")
    with st.form("form_ajout"):
        nom = st.text_input("Nom du client")
        plateforme = st.selectbox("Plateforme", ["Booking", "Airbnb", "Direct", "Autre"])
        telephone = st.text_input("Téléphone")
        col1, col2 = st.columns(2)
        with col1:
            date_arrivee = st.date_input("Date d’arrivée")
        with col2:
            date_depart = st.date_input("Date de départ")

        nuitees = max((date_depart - date_arrivee).days, 0)
        st.info(f"🌙 Nuitées : {nuitees}")

        prix_brut = st.number_input("Prix brut (€)", min_value=0.0)
        prix_net = st.number_input("Prix net (€)", min_value=0.0)
        commissions = st.number_input("Commissions (€)", min_value=0.0)
        paye = st.checkbox("Payé")

        submit = st.form_submit_button("Ajouter")
        if submit:
            pays = detect_pays(telephone)
            df = load_reservations(slug)
            new_row = {
                "nom_client": nom,
                "plateforme": plateforme,
                "telephone": telephone,
                "date_arrivee": date_arrivee.strftime("%d/%m/%Y"),
                "date_depart": date_depart.strftime("%d/%m/%Y"),
                "nuitees": nuitees,
                "prix_brut": prix_brut,
                "prix_net": prix_net,
                "commissions": commissions,
                "paye": paye,
                "pays": pays
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_reservations(slug, df)
            st.success("✅ Réservation ajoutée.")

# ========================
# MODIFIER UNE RÉSERVATION
# ========================
def modifier_reservation_ui(slug: str):
    st.subheader("✏️ Modifier une réservation")
    df = load_reservations(slug)
    if df.empty:
        st.info("Aucune réservation.")
        return

    idx = st.selectbox("Sélectionner une réservation", df.index,
        format_func=lambda i: f"{df.loc[i,'nom_client']} – {df.loc[i,'date_arrivee']}")
    row = df.loc[idx]

    with st.form("form_modifier"):
        nom = st.text_input("Nom", row["nom_client"])
        plateforme = st.selectbox("Plateforme", ["Booking", "Airbnb", "Direct", "Autre"],
                                  index=["Booking", "Airbnb", "Direct", "Autre"].index(row["plateforme"]))
        telephone = st.text_input("Téléphone", row["telephone"])
        date_arrivee = st.date_input("Date d’arrivée", datetime.strptime(row["date_arrivee"], "%d/%m/%Y"))
        date_depart = st.date_input("Date de départ", datetime.strptime(row["date_depart"], "%d/%m/%Y"))
        nuitees = max((date_depart - date_arrivee).days, 0)
        prix_brut = st.number_input("Prix brut (€)", value=float(row["prix_brut"]))
        prix_net = st.number_input("Prix net (€)", value=float(row["prix_net"]))
        commissions = st.number_input("Commissions (€)", value=float(row.get("commissions", 0)))
        paye = st.checkbox("Payé", value=bool(row["paye"]))

        col1, col2 = st.columns(2)
        with col1:
            save_btn = st.form_submit_button("💾 Enregistrer")
        with col2:
            delete_btn = st.form_submit_button("🗑️ Supprimer")

    if save_btn:
        pays = detect_pays(telephone)
        df.loc[idx] = [
            nom, plateforme, telephone,
            date_arrivee.strftime("%d/%m/%Y"),
            date_depart.strftime("%d/%m/%Y"),
            nuitees, prix_brut, prix_net, paye, pays, commissions
        ]
        save_reservations(slug, df)
        st.success("✅ Réservation modifiée.")

    if delete_btn:
        df = df.drop(index=idx).reset_index(drop=True)
        save_reservations(slug, df)
        st.success("🗑️ Réservation supprimée.")

# ========================
# CALENDRIER
# ========================
def afficher_calendrier_google(slug: str):
    st.subheader("📅 Calendrier")
    df = load_reservations(slug)
    if df.empty:
        st.info("Aucune réservation.")
        return

    df["date_arrivee"] = pd.to_datetime(df["date_arrivee"], dayfirst=True)
    df["date_depart"] = pd.to_datetime(df["date_depart"], dayfirst=True)

    couleurs = {
        "booking": "#003580",
        "airbnb": "#FF5A5F",
        "direct": "#2ecc71",
        "autre": "#7f8c8d"
    }

    events = []
    for _, r in df.iterrows():
        events.append({
            "title": r["nom_client"],
            "start": r["date_arrivee"].strftime("%Y-%m-%d"),
            "end": r["date_depart"].strftime("%Y-%m-%d"),
            "color": couleurs.get(str(r["plateforme"]).lower(), "#999999")
        })

    calendar(
        events=events,
        options={
            "initialView": "dayGridMonth",
            "locale": "fr",
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,listWeek"
            }
        }
    )

# ========================
# STATISTIQUES SIMPLIFIÉES
# ========================
def afficher_statistiques(slug: str):
    st.subheader("📈 Statistiques")
    df = load_reservations(slug)
    if df.empty:
        st.info("Aucune donnée")
        return

    df["date_arrivee"] = pd.to_datetime(df["date_arrivee"], dayfirst=True, errors="coerce")
    df["date_depart"] = pd.to_datetime(df["date_depart"], dayfirst=True, errors="coerce")
    df["duree"] = (df["date_depart"] - df["date_arrivee"]).dt.days

    st.markdown("### Vue d'ensemble")
    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Réservations", len(df))
    col2.metric("🛏️ Nuitées totales", int(df["nuitees"].sum()))
    col3.metric("💶 Revenu brut", f"{df['prix_brut'].sum():.2f} €")

    st.markdown("### Répartition par plateforme")
    if "plateforme" in df.columns:
        fig = px.pie(df, names="plateforme", title="Répartition des réservations", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Indicateurs financiers")
    col4, col5, col6 = st.columns(3)
    col4.metric("💰 Revenu net", f"{df['prix_net'].sum():.2f} €")
    col5.metric("💸 Commissions", f"{df['commissions'].sum():.2f} €")
    col6.metric("📊 Durée moyenne (jours)", f"{df['duree'].mean():.1f}")

    if "paye" in df.columns:
        total = len(df)
        payees = df["paye"].sum()
        taux = 100 * payees / total
        st.metric("✅ Taux de paiement", f"{taux:.1f}% ({payees}/{total})")

    st.markdown("### Détail par réservation")
    st.dataframe(df[[
        "nom_client", "plateforme", "date_arrivee", "date_depart",
        "nuitees", "prix_brut", "prix_net", "commissions", "paye"
    ]], use_container_width=True)

