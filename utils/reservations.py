import os
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from io import BytesIO

# ========================
# FICHIERS
# ========================

def reservations_path(slug: str) -> str:
    return f"data/reservations_{slug}.csv"


def load_reservations(slug: str) -> pd.DataFrame:
    path = reservations_path(slug)
    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path)

    # Sécurisation colonnes
    for col in ["nom_client", "plateforme", "date_arrivee", "date_depart"]:
        if col not in df.columns:
            df[col] = ""

    for col in ["nuitees", "prix_brut", "prix_net", "commissions"]:
        if col not in df.columns:
            df[col] = 0.0

    if "paye" not in df.columns:
        df["paye"] = False

    return df


def save_reservations(slug: str, df: pd.DataFrame):
    os.makedirs("data", exist_ok=True)
    df.to_csv(reservations_path(slug), index=False)


# ========================
# AFFICHAGE
# ========================

def afficher_reservations(slug: str):
    st.subheader("📋 Réservations")
    df = load_reservations(slug)

    if df.empty:
        st.info("Aucune réservation.")
        return

    st.dataframe(df, use_container_width=True)


# ========================
# AJOUT
# ========================

def ajouter_reservation_ui(slug: str):
    st.subheader("➕ Ajouter une réservation")

    with st.form("ajout_reservation"):
        nom = st.text_input("Nom client")
        plateforme = st.selectbox("Plateforme", ["Booking", "Airbnb", "Direct", "Autre"])
        date_arrivee = st.date_input("Date d'arrivée")
        date_depart = st.date_input("Date de départ")
        prix_brut = st.number_input("Prix brut", min_value=0.0)
        prix_net = st.number_input("Prix net", min_value=0.0)
        paye = st.checkbox("Payé")

        submit = st.form_submit_button("Ajouter")

    if submit:
        nuitees = max((date_depart - date_arrivee).days, 0)

        df = load_reservations(slug)
        df = pd.concat(
            [
                df,
                pd.DataFrame([{
                    "nom_client": nom,
                    "plateforme": plateforme,
                    "date_arrivee": date_arrivee.strftime("%d/%m/%Y"),
                    "date_depart": date_depart.strftime("%d/%m/%Y"),
                    "nuitees": nuitees,
                    "prix_brut": prix_brut,
                    "prix_net": prix_net,
                    "commissions": prix_brut - prix_net,
                    "paye": paye
                }])
            ],
            ignore_index=True
        )

        save_reservations(slug, df)
        st.success("Réservation ajoutée ✅")
        st.rerun()


# ========================
# MODIFIER / SUPPRIMER
# ========================

def modifier_reservation_ui(slug: str):
    st.subheader("✏️ Modifier / Supprimer")
    df = load_reservations(slug)

    if df.empty:
        st.info("Aucune réservation.")
        return

    options = df.index.tolist()

    idx = st.selectbox(
        "Sélectionner une réservation",
        options,
        format_func=lambda i: f"{df.at[i, 'nom_client']} – {df.at[i, 'date_arrivee']}"
    )

    row = df.loc[idx]

    with st.form("modifier"):
        nom = st.text_input("Nom", row["nom_client"])
        plateforme = st.selectbox(
            "Plateforme",
            ["Booking", "Airbnb", "Direct", "Autre"],
            index=["Booking", "Airbnb", "Direct", "Autre"].index(row["plateforme"])
        )
        prix_brut = st.number_input("Prix brut", value=float(row["prix_brut"]))
        prix_net = st.number_input("Prix net", value=float(row["prix_net"]))
        paye = st.checkbox("Payé", value=bool(row["paye"]))

        save_btn = st.form_submit_button("💾 Enregistrer")
        delete_btn = st.form_submit_button("🗑️ Supprimer")

    if save_btn:
        df.loc[idx, ["nom_client", "plateforme", "prix_brut", "prix_net", "paye"]] = [
            nom, plateforme, prix_brut, prix_net, paye
        ]
        save_reservations(slug, df)
        st.success("Réservation modifiée")
        st.rerun()

    if delete_btn:
        df = df.drop(idx).reset_index(drop=True)
        save_reservations(slug, df)
        st.success("Réservation supprimée")
        st.rerun()


# ========================
# CALENDRIER (simple)
# ========================

def afficher_calendrier_google(slug: str):
    st.subheader("📅 Calendrier")
    df = load_reservations(slug)

    if df.empty:
        st.info("Aucune réservation.")
        return

    df["date_arrivee"] = pd.to_datetime(df["date_arrivee"], dayfirst=True, errors="coerce")
    df["date_depart"] = pd.to_datetime(df["date_depart"], dayfirst=True, errors="coerce")

    st.dataframe(df[["nom_client", "date_arrivee", "date_depart", "plateforme"]])


# ========================
# STATISTIQUES
# ========================

def afficher_statistiques(slug: str):
    st.subheader("📈 Statistiques")
    df = load_reservations(slug)

    if df.empty:
        st.info("Aucune donnée.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Réservations", len(df))
    col2.metric("Nuitées", int(df["nuitees"].sum()))
    col3.metric("CA brut", f"{df['prix_brut'].sum():.0f} €")

    fig = px.pie(df, names="plateforme", values="prix_brut")
    st.plotly_chart(fig, use_container_width=True)


# ========================
# ANALYSE FINANCIÈRE
# ========================

def afficher_analyse_financiere(slug: str):
    st.subheader("💼 Analyse financière")

    df = load_reservations(slug)
    if df.empty:
        st.info("Aucune donnée.")
        return

    df["date_arrivee"] = pd.to_datetime(df["date_arrivee"], dayfirst=True, errors="coerce")
    df["annee"] = df["date_arrivee"].dt.year

    kpi = df.groupby("annee").agg(
        nuitees=("nuitees", "sum"),
        ca_brut=("prix_brut", "sum"),
        ca_net=("prix_net", "sum"),
    ).reset_index()

    st.dataframe(kpi)

    fig = px.bar(
        kpi,
        x="annee",
        y=["ca_brut", "ca_net"],
        barmode="group",
        title="CA par année"
    )
    st.plotly_chart(fig, use_container_width=True)

    buffer = BytesIO()
    kpi.to_excel(buffer, index=False)

    st.download_button(
        "Télécharger analyse Excel",
        buffer.getvalue(),
        "analyse_financiere.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )