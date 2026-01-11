
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from utils.reservations import load_reservations
from datetime import datetime

def afficher_analyse_financiere(slug: str):
    st.header("📊 Analyse Financière Avancée")

    df = load_reservations(slug)
    if df.empty:
        st.info("Aucune réservation à analyser.")
        return

    df["date_arrivee"] = pd.to_datetime(df["date_arrivee"], dayfirst=True, errors="coerce")
    df["mois"] = df["date_arrivee"].dt.month
    df["annee"] = df["date_arrivee"].dt.year
    df["prix_brut_par_nuit"] = df["prix_brut"] / df["nuitees"]
    df["prix_net_par_nuit"] = df["prix_net"] / df["nuitees"]

    annees = sorted(df["annee"].dropna().unique(), reverse=True)
    plateformes = df["plateforme"].dropna().unique()

    col1, col2 = st.columns(2)
    with col1:
        selected_annees = st.multiselect("Années à comparer", annees, default=annees)
    with col2:
        selected_plateformes = st.multiselect("Plateformes", plateformes, default=plateformes)

    df_f = df[df["annee"].isin(selected_annees) & df["plateforme"].isin(selected_plateformes)]

    if df_f.empty:
        st.warning("Aucune donnée pour les filtres sélectionnés.")
        return

    st.subheader("🔢 Indicateurs clés multi-années")
    kpi = df_f.groupby("annee").agg({
        "nuitees": "sum",
        "prix_brut": "sum",
        "prix_net": "sum"
    }).reset_index()
    kpi["taux_occupation"] = (kpi["nuitees"] / 365) * 100
    kpi["prix_brut/nuit"] = kpi["prix_brut"] / kpi["nuitees"]
    kpi["prix_net/nuit"] = kpi["prix_net"] / kpi["nuitees"]

    st.dataframe(kpi)

    fig = px.bar(kpi, x="annee", y=["prix_brut", "prix_net"], barmode="group",
                 labels={"value": "Montant (€)", "annee": "Année", "variable": "Type"},
                 title="Comparaison du chiffre d'affaires par année")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📆 Visualisation mensuelle")
    df_mensuel = df_f.groupby(["annee", "mois"]).agg({
        "prix_brut": "sum",
        "prix_net": "sum"
    }).reset_index()
    df_mensuel["mois_str"] = df_mensuel["mois"].apply(lambda x: datetime(2000, x, 1).strftime("%b"))

    fig2 = px.line(df_mensuel, x="mois_str", y="prix_net", color="annee", markers=True,
                   title="Évolution mensuelle du CA net")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🏷 Répartition du chiffre d'affaires par plateforme")
    pie = px.pie(df_f, names="plateforme", values="prix_net", title="Répartition CA net")
    st.plotly_chart(pie, use_container_width=True)

    st.subheader("📥 Export Excel")
    buffer = BytesIO()
    kpi.to_excel(buffer, index=False)
    st.download_button(
        "⬇️ Télécharger les indicateurs financiers",
        buffer.getvalue(),
        "analyse_financiere.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
