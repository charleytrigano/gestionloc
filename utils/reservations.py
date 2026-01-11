import os
import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
import plotly.express as px
from streamlit_calendar import calendar

# =====================================================
# FICHIERS
# =====================================================

def reservations_path(slug: str) -> str:
    return f"data/reservations_{slug}.csv"


def load_reservations(slug: str) -> pd.DataFrame:
    path = reservations_path(slug)

    if not os.path.exists(path):
        return pd.DataFrame(columns=[
            "nom_client", "plateforme", "telephone",
            "date_arrivee", "date_depart",
            "nuitees", "prix_brut", "prix_net",
            "commissions", "paye", "pays"
        ])

    df = pd.read_csv(path)

    # Nettoyage minimal et sécurisé
    df.columns = df.columns.str.strip()

    for col in ["date_arrivee", "date_depart"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")

    if "paye" in df.columns:
        df["paye"] = df["paye"].fillna(False).astype(bool)

    return df


def save_reservations(slug: str, df: pd.DataFrame):
    df_copy = df.copy()

    for col in ["date_arrivee", "date_depart"]:
        if col in df_copy.columns:
            df_copy[col] = df_copy[col].dt.strftime("%d/%m/%Y")

    df_copy.to_csv(reservations_path(slug), index=False)


# =====================================================
# LISTE DES RÉSERVATIONS
# =====================================================

def afficher_reservations(slug: str):
    st.subheader("📋 Réservations")
    df = load_reservations(slug)

    if df.empty:
        st.info("Aucune réservation.")
        return

    st.dataframe(df, use_container_width=True)


# =====================================================
# AJOUT
# =====================================================

def ajouter_reservation_ui(slug: str):
    st.subheader("➕ Ajouter une réservation")

    with st.form("add_resa"):
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
        commissions = prix_brut - prix_net
        paye = st.checkbox("Payé")

        if st.form_submit_button("Ajouter"):
            df = load_reservations(slug)

            df = pd.concat([df, pd.DataFrame([{
                "nom_client": nom,
                "plateforme": plateforme,
                "telephone": telephone,
                "date_arrivee": date_arrivee,
                "date_depart": date_depart,
                "nuitees": nuitees,
                "prix_brut": prix_brut,
                "prix_net": prix_net,
                "commissions": commissions,
                "paye": paye,
                "pays": ""
            }])], ignore_index=True)

            save_reservations(slug, df)
            st.success("✅ Réservation ajoutée")


# =====================================================
# MODIFIER / SUPPRIMER (BUG -™ CORRIGÉ)
# =====================================================

def modifier_reservation_ui(slug: str):
    st.subheader("✏️ Modifier / Supprimer")
    df = load_reservations(slug)

    if df.empty:
        st.info("Aucune réservation.")
        return

    # 👉 LABEL ROBUSTE (plus jamais -™)
    def label_reservation(i):
        try:
            nom = str(df.at[i, "nom_client"]) if pd.notna(df.at[i, "nom_client"]) else "Client"
            d = df.at[i, "date_arrivee"]
            if pd.isna(d):
                date_str = "Date inconnue"
            else:
                date_str = d.strftime("%d/%m/%Y")
            return f"{nom} — {date_str}"
        except Exception:
            return f"Réservation #{i}"

    idx = st.selectbox(
        "Sélectionner une réservation",
        df.index.tolist(),
        format_func=label_reservation
    )

    row = df.loc[idx]

    with st.form("edit_resa"):
        nom = st.text_input("Nom", row.get("nom_client", ""))
        plateforme = st.selectbox(
            "Plateforme",
            ["Booking", "Airbnb", "Direct", "Autre"],
            index=["Booking", "Airbnb", "Direct", "Autre"].index(
                row.get("plateforme", "Direct")
            )
        )

        prix_brut = st.number_input("Prix brut", value=float(row.get("prix_brut", 0)))
        prix_net = st.number_input("Prix net", value=float(row.get("prix_net", 0)))
        paye = st.checkbox("Payé", value=bool(row.get("paye", False)))

        col1, col2 = st.columns(2)
        with col1:
            save_btn = st.form_submit_button("💾 Enregistrer")
        with col2:
            delete_btn = st.form_submit_button("🗑️ Supprimer")

    if save_btn:
        df.at[idx, "nom_client"] = nom
        df.at[idx, "plateforme"] = plateforme
        df.at[idx, "prix_brut"] = prix_brut
        df.at[idx, "prix_net"] = prix_net
        df.at[idx, "commissions"] = prix_brut - prix_net
        df.at[idx, "paye"] = paye

        save_reservations(slug, df)
        st.success("✅ Réservation modifiée")

    if delete_btn:
        df = df.drop(idx).reset_index(drop=True)
        save_reservations(slug, df)
        st.success("🗑️ Réservation supprimée")


# =====================================================
# CALENDRIER
# =====================================================

def afficher_calendrier_google(slug: str):
    st.subheader("📅 Calendrier")
    df = load_reservations(slug)

    if df.empty:
        st.info("Aucune réservation.")
        return

    couleurs = {
        "booking": "#003580",
        "airbnb": "#FF5A5F",
        "direct": "#2ecc71",
        "autre": "#7f8c8d"
    }

    events = []
    for _, r in df.iterrows():
        if pd.isna(r["date_arrivee"]) or pd.isna(r["date_depart"]):
            continue

        events.append({
            "title": r.get("nom_client", "Client"),
            "start": r["date_arrivee"].strftime("%Y-%m-%d"),
            "end": r["date_depart"].strftime("%Y-%m-%d"),
            "color": couleurs.get(str(r.get("plateforme", "")).lower(), "#999999")
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


# =====================================================
# STATISTIQUES
# =====================================================

def afficher_statistiques(slug: str):
    st.subheader("📈 Statistiques")
    df = load_reservations(slug)

    if df.empty:
        st.info("Aucune donnée.")
        return

    df["annee"] = df["date_arrivee"].dt.year

    annee = st.selectbox("Année", sorted(df["annee"].dropna().unique(), reverse=True))
    df_f = df[df["annee"] == annee]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Réservations", len(df_f))
    col2.metric("Nuitées", int(df_f["nuitees"].sum()))
    col3.metric("CA brut", f"{df_f['prix_brut'].sum():,.2f} €")
    col4.metric("CA net", f"{df_f['prix_net'].sum():,.2f} €")

    st.plotly_chart(
        px.pie(
            df_f,
            names="plateforme",
            values="prix_net",
            title="Répartition du CA net"
        ),
        use_container_width=True
    )

    st.markdown("### 📋 Détail des réservations")
    st.dataframe(df_f, use_container_width=True)