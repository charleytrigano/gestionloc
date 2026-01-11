def modifier_reservation_ui(slug: str):
    st.subheader("✏️ Modifier / Supprimer une réservation")

    df = load_reservations(slug)

    if df.empty:
        st.info("Aucune réservation.")
        return

    # Sécurisation des colonnes
    nom_col = "nom_client" if "nom_client" in df.columns else df.columns[0]
    date_col = "date_arrivee" if "date_arrivee" in df.columns else None

    # Création des libellés lisibles
    labels = []
    for i, row in df.iterrows():
        nom = str(row.get(nom_col, "Client"))
        date = str(row.get(date_col, "")) if date_col else ""
        labels.append(f"{nom} – {date}")

    idx = st.selectbox(
        "Sélectionner une réservation",
        options=df.index.tolist(),
        format_func=lambda i: labels[df.index.tolist().index(i)]
    )

    row = df.loc[idx]

    with st.form("form_modifier"):
        st.markdown("### 🧾 Informations client")

        nom = st.text_input("Nom du client", value=str(row.get("nom_client", "")))
        plateforme = st.text_input("Plateforme", value=str(row.get("plateforme", "")))
        telephone = st.text_input("Téléphone", value=str(row.get("telephone", "")))

        st.markdown("### 📅 Séjour")

        date_arrivee = st.text_input(
            "Date d’arrivée",
            value=str(row.get("date_arrivee", ""))
        )
        date_depart = st.text_input(
            "Date de départ",
            value=str(row.get("date_depart", ""))
        )

        st.markdown("### 💰 Finances")

        prix_brut = st.number_input(
            "Prix brut",
            value=float(row.get("prix_brut", 0.0))
        )
        prix_net = st.number_input(
            "Prix net",
            value=float(row.get("prix_net", 0.0))
        )

        paye = st.checkbox(
            "Payé",
            value=bool(row.get("paye", False))
        )

        col1, col2 = st.columns(2)
        save_btn = col1.form_submit_button("💾 Enregistrer")
        delete_btn = col2.form_submit_button("🗑️ Supprimer")

    if save_btn:
        df.loc[idx, "nom_client"] = nom
        df.loc[idx, "plateforme"] = plateforme
        df.loc[idx, "telephone"] = telephone
        df.loc[idx, "date_arrivee"] = date_arrivee
        df.loc[idx, "date_depart"] = date_depart
        df.loc[idx, "prix_brut"] = prix_brut
        df.loc[idx, "prix_net"] = prix_net
        df.loc[idx, "paye"] = paye

        save_reservations(slug, df)
        st.success("✅ Réservation modifiée")
        st.rerun()

    if delete_btn:
        df = df.drop(index=idx).reset_index(drop=True)
        save_reservations(slug, df)
        st.success("🗑️ Réservation supprimée")
        st.rerun()