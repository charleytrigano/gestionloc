import pandas as pd
import os

def load_apartments(path="data/apartments.csv") -> pd.DataFrame:
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=["slug", "nom"])

import os
import pandas as pd
import streamlit as st

APARTMENTS_PATH = "data/apartments.csv"

def load_apartments() -> pd.DataFrame:
    if os.path.exists(APARTMENTS_PATH):
        return pd.read_csv(APARTMENTS_PATH)
    else:
        return pd.DataFrame(columns=["slug", "nom"])

def save_apartments(df: pd.DataFrame):
    df.to_csv(APARTMENTS_PATH, index=False)

def gestion_appartements_ui():
    st.header("🏢 Gestion des appartements")
    df = load_apartments()

    # Affichage du tableau actuel
    if df.empty:
        st.info("Aucun appartement pour le moment.")
    else:
        st.dataframe(df, use_container_width=True)

    # Formulaire d'ajout ou modification
    with st.form("ajout_appart"):
        st.subheader("➕ Ajouter / Modifier un appartement")
        slug = st.text_input("Identifiant (slug)")
        nom = st.text_input("Nom de l'appartement")

        submit = st.form_submit_button("Enregistrer")
        if submit:
            if slug == "" or nom == "":
                st.warning("Veuillez remplir tous les champs.")
            else:
                if slug in df["slug"].values:
                    df.loc[df["slug"] == slug, "nom"] = nom
                    st.success("✏️ Appartement modifié.")
                else:
                    df = pd.concat([df, pd.DataFrame([{"slug": slug, "nom": nom}])], ignore_index=True)
                    st.success("✅ Appartement ajouté.")
                save_apartments(df)

    # Suppression
    st.subheader("🗑️ Supprimer un appartement")
    if not df.empty:
        slugs = df["slug"].tolist()
        slug_to_delete = st.selectbox("Choisir un appartement à supprimer", slugs)
        if st.button("Supprimer"):
            df = df[df["slug"] != slug_to_delete]
            save_apartments(df)
            st.success(f"Appartement `{slug_to_delete}` supprimé.")


