import datetime
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Mon Carnet de Recettes Intelligent",
    page_icon="🍳",
    layout="wide",
)

# Initialisation de la base de données simulée en session
if "recettes" not in st.session_state:
    st.session_state.recettes = [
        {
            "id": 1,
            "titre": "Gratin de courges d'automne",
            "categorie": "Plats",
            "saison": "Automne / Hiver",
            "temps": "45 min",
            "ingredients": [
                "Courge butternut (1)",
                "Crème fraîche (200ml)",
                "Comté râpé (100g)",
                "Noix de muscade",
            ],
            "etapes": "1. Couper la courge. 2. Cuire à la vapeur. 3. Mélanger avec la crème et le muscade. 4. Parsemer de Comté et enfourner 20 min à 200°C.",
        },
        {
            "id": 2,
            "titre": "Salade fraîcheur tomates-mozzarella",
            "categorie": "Entrées",
            "saison": "Été",
            "temps": "10 min",
            "ingredients": [
                "Tomates du jardin (3)",
                "Mozzarella di Bufala (2)",
                "Huile d'olive",
                "Basilic frais",
            ],
            "etapes": (
                "1. Trancher les tomates et la mozza. 2. Disposer en alternance."
                " 3. Assaisonner avec l'huile et le basilic."
            ),
        },
    ]

if "menu_semaine" not in st.session_state:
    st.session_state.menu_semaine = []

# Barre latérale de navigation
st.sidebar.title("🍳 Mes Recettes")
menu = st.sidebar.radio(
    "Navigation",
    [
        "📖 Mes Recettes & Recherche",
        "📸 Ajouter une Recette (Photo)",
        "🗓️ Suggestions & Menus",
        "🛒 Liste de Courses",
    ],
)

# ---------------------------------------------------------
# 1. MES RECETTES & RECHERCHE
# ---------------------------------------------------------
if menu == "📖 Mes Recettes & Recherche":
    st.title("Mon Carnet de Recettes")

    col1, col2, col3 = st.columns(3)
    with col1:
        recherche = st.text_input(
            "🔍 Rechercher (titre ou ingrédient)", ""
        ).lower()
    with col2:
        filtre_cat = st.selectbox(
            "Filtrer par catégorie",
            [
                "Toutes",
                "Entrées",
                "Plats",
                "Desserts",
                "Apéritifs / Snacks",
            ],
        )
    with col3:
        filtre_saison = st.selectbox(
            "Filtrer par saison",
            ["Toutes", "Printemps", "Été", "Automne / Hiver"],
        )

    st.markdown("---")

    # Filtrage
    recettes_filtrees = st.session_state.recettes
    if recherche:
        recettes_filtrees = [
            r
            for r in recettes_filtrees
            if recherche in r["titre"].lower()
            or any(recherche in ing.lower() for ing in r["ingredients"])
        ]
    if filtre_cat != "Toutes":
        recettes_filtrees = [
            r for r in recettes_filtrees if r["categorie"] == filtre_cat
        ]
    if filtre_saison != "Toutes":
        recettes_filtrees = [
            r for r in recettes_filtrees if r["saison"] == filtre_saison
        ]

    if not recettes_filtrees:
        st.info("Aucune recette ne correspond à vos critères.")
    else:
        for r in recettes_filtrees:
            with st.expander(
                f"**{r['titre']}** — *{r['categorie']}* ({r['saison']} | ⏱️ {r['temps']})"
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Ingrédients :**")
                    for ing in r["ingredients"]:
                        st.write(f"- {ing}")
                with c2:
                    st.markdown("**Préparation :**")
                    st.write(r["etapes"])

                if st.button(
                    f"➕ Ajouter au menu de la semaine", key=f"menu_{r['id']}"
                ):
                    st.session_state.menu_semaine.append(r)
                    st.success(f"'{r['titre']}' a été ajouté à votre menu !")

# ---------------------------------------------------------
# 2. AJOUTER UNE RECETTE (PHOTO / SCAN)
# ---------------------------------------------------------
elif menu == "📸 Ajouter une Recette (Photo)":
    st.title("Ajouter une Recette via une Photo")

    uploaded_file = st.file_uploader(
        "Prenez en photo ou téléchargez une page de recette (image)",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Photo importée", use_container_width=True)
        st.info(
            "Analyse de l'image en cours par l'intelligence artificielle..."
        )

        # Simulation d'extraction OCR intelligente
        titre_ext = "Tarte rustique aux légumes du soleil"
        cat_ext = "Plats"
        saison_ext = "Été"
        temps_ext = "35 min"
        ing_ext = [
            "Pâte feuilletée (1)",
            "Courgettes (2)",
            "Tomates (3)",
            "Moutarde à l'ancienne (2 c. à s.)",
        ]
        etapes_ext = "1. Dérouler la pâte. 2. Badigeonner de moutarde. 3. Disposer les légumes coupés en rondelles. 4. Cuire 30 min à 180°C."

        st.success("Analyse réussie ! Voici les informations extraites :")

        with st.form("form_validation"):
            n_titre = st.text_input("Titre de la recette", value=titre_ext)
            n_cat = st.selectbox(
                "Catégorie",
                [
                    "Entrées",
                    "Plats",
                    "Desserts",
                    "Apéritifs / Snacks",
                ],
                index=1,
            )
            n_saison = st.selectbox(
                "Saison idéale",
                ["Printemps", "Été", "Automne / Hiver", "Toutes saisons"],
                index=1,
            )
            n_temps = st.text_input("Temps de préparation", value=temps_ext)

            st.markdown("**Ingrédients détectés (modifiables) :**")
            ing_text = st.text_area(
                "Un ingrédient par ligne", value="\n".join(ing_ext)
            )

            st.markdown("**Étapes :**")
            n_etapes = st.text_area("Préparation", value=etapes_ext)

            submitted = st.form_submit_button(
                "Valider et enregistrer dans mon carnet"
            )
            if submitted:
                nouvelle_recette = {
                    "id": len(st.session_state.recettes) + 1,
                    "titre": n_titre,
                    "categorie": n_cat,
                    "saison": n_saison,
                    "temps": n_temps,
                    "ingredients": [
                        i.strip() for i in ing_text.split("\n") if i.strip()
                    ],
                    "etapes": n_etapes,
                }
                st.session_state.recettes.append(nouvelle_recette)
                st.balloons()
                st.success(
                    f"La recette '{n_titre}' a bien été enregistrée et classée dans '{n_cat}' !"
                )

# ---------------------------------------------------------
# 3. SUGGESTIONS & MENUS
# ---------------------------------------------------------
elif menu == "🗓️ Suggestions & Menus":
    st.title("Suggestions & Idées de Menus")

    st.markdown(
        "### 💡 Suggestions basées sur la saison actuelle et vos placards"
    )
    col1, col2 = st.columns(2)

    with col1:
        st.info("🍂 **Suggestion du moment (Automne)**")
        st.write(
            "Puisque c'est la saison des courges et des plats réconfortants :"
        )
        if st.button("Suggérer un menu d'automne"):
            recette_sugg = [
                r
                for r in st.session_state.recettes
                if "Automne" in r["saison"]
            ]
            if recette_sugg:
                st.write(f"✨ Nous vous conseillons : **{recette_sugg[0]['titre']}**")
                if st.button("Ajouter cette suggestion au menu"):
                    st.session_state.menu_semaine.append(recette_sugg[0])
                    st.success("Ajouté !")

    with col2:
        st.info("🥦 **Anti-gaspillage / Ingrédients dispos**")
        ingredients_frigo = st.multiselect(
            "Qu'avez-vous dans le frigo à épuiser ?",
            ["Courge butternut", "Tomates", "Crème fraîche", "Œufs", "Fromage"],
        )
        if ingredients_frigo:
            st.write("💡 Recettes réalisables avec ces ingrédients :")
            for r in st.session_state.recettes:
                if any(
                    any(ing.lower().find(inf.lower()) != -1 for inf in ingredients_frigo)
                    for ing in r["ingredients"]
                ):
                    st.write(f"- ✅ **{r['titre']}**")

    st.markdown("---")
    st.subheader("📋 Votre Menu de la Semaine")
    if not st.session_state.menu_semaine:
        st.write(
            "Aucun plat planifié pour l'instant. Parcourez vos recettes pour en ajouter !"
        )
    else:
        for idx, item in enumerate(st.session_state.menu_semaine):
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.write(
                    f"**{idx + 1}.** {item['titre']} (*{item['categorie']}*)"
                )
            with col_b:
                if st.button("❌", key=f"del_menu_{idx}"):
                    st.session_state.menu_semaine.pop(idx)
                    st.rerun()

# ---------------------------------------------------------
# 4. LISTE DE COURSES
# ---------------------------------------------------------
elif menu == "🛒 Liste de Courses":
    st.title("Liste de Courses Automatisée")

    if not st.session_state.menu_semaine:
        st.warning(
            "Votre menu de la semaine est vide. Ajoutez des recettes pour générer votre liste de courses !"
        )
    else:
        st.write(
            "Voici la liste consolidée des ingrédients nécessaires pour vos menus de la semaine :"
        )

        # Extraction et fusion des ingrédients
        tous_les_ingredients = []
        for r in st.session_state.menu_semaine:
            for ing in r["ingredients"]:
                tous_les_ingredients.append(ing)

        # Affichage sous forme de liste à cocher
        st.markdown("---")
        for i, ingredient in enumerate(tous_les_ingredients):
            st.checkbox(f"{ingredient}", key=f"course_{i}")

        if st.button("🗑️ Vider la liste / Réinitialiser le menu"):
            st.session_state.menu_semaine = []
            st.rerun()
import datetime
import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Mon Carnet de Recettes Intelligent",
    page_icon="🍳",
    layout="wide",
)

# Initialisation de la base de données simulée en session
if "recettes" not in st.session_state:
    st.session_state.recettes = [
        {
            "id": 1,
            "titre": "Gratin de courges d'automne",
            "categorie": "Plats",
            "saison": "Automne / Hiver",
            "temps": "45 min",
            "ingredients": [
                "Courge butternut (1)",
                "Crème fraîche (200ml)",
                "Comté râpé (100g)",
                "Noix de muscade",
            ],
            "etapes": "1. Couper la courge. 2. Cuire à la vapeur. 3. Mélanger avec la crème et le muscade. 4. Parsemer de Comté et enfourner 20 min à 200°C.",
        },
        {
            "id": 2,
            "titre": "Salade fraîcheur tomates-mozzarella",
            "categorie": "Entrées",
            "saison": "Été",
            "temps": "10 min",
            "ingredients": [
                "Tomates du jardin (3)",
                "Mozzarella di Bufala (2)",
                "Huile d'olive",
                "Basilic frais",
            ],
            "etapes": (
                "1. Trancher les tomates et la mozza. 2. Disposer en alternance."
                " 3. Assaisonner avec l'huile et le basilic."
            ),
        },
    ]

if "menu_semaine" not in st.session_state:
    st.session_state.menu_semaine = []

# Barre latérale de navigation
st.sidebar.title("🍳 Mes Recettes")
menu = st.sidebar.radio(
    "Navigation",
    [
        "📖 Mes Recettes & Recherche",
        "📸 Ajouter une Recette (Photo)",
        "🗓️ Suggestions & Menus",
        "🛒 Liste de Courses",
    ],
)

# ---------------------------------------------------------
# 1. MES RECETTES & RECHERCHE
# ---------------------------------------------------------
if menu == "📖 Mes Recettes & Recherche":
    st.title("Mon Carnet de Recettes")

    col1, col2, col3 = st.columns(3)
    with col1:
        recherche = st.text_input(
            "🔍 Rechercher (titre ou ingrédient)", ""
        ).lower()
    with col2:
        filtre_cat = st.selectbox(
            "Filtrer par catégorie",
            [
                "Toutes",
                "Entrées",
                "Plats",
                "Desserts",
                "Apéritifs / Snacks",
            ],
        )
    with col3:
        filtre_saison = st.selectbox(
            "Filtrer par saison",
            ["Toutes", "Printemps", "Été", "Automne / Hiver"],
        )

    st.markdown("---")

    # Filtrage
    recettes_filtrees = st.session_state.recettes
    if recherche:
        recettes_filtrees = [
            r
            for r in recettes_filtrees
            if recherche in r["titre"].lower()
            or any(recherche in ing.lower() for ing in r["ingredients"])
        ]
    if filtre_cat != "Toutes":
        recettes_filtrees = [
            r for r in recettes_filtrees if r["categorie"] == filtre_cat
        ]
    if filtre_saison != "Toutes":
        recettes_filtrees = [
            r for r in recettes_filtrees if r["saison"] == filtre_saison
        ]

    if not recettes_filtrees:
        st.info("Aucune recette ne correspond à vos critères.")
    else:
        for r in recettes_filtrees:
            with st.expander(
                f"**{r['titre']}** — *{r['categorie']}* ({r['saison']} | ⏱️ {r['temps']})"
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Ingrédients :**")
                    for ing in r["ingredients"]:
                        st.write(f"- {ing}")
                with c2:
                    st.markdown("**Préparation :**")
                    st.write(r["etapes"])

                if st.button(
                    f"➕ Ajouter au menu de la semaine", key=f"menu_{r['id']}"
                ):
                    st.session_state.menu_semaine.append(r)
                    st.success(f"'{r['titre']}' a été ajouté à votre menu !")

# ---------------------------------------------------------
# 2. AJOUTER UNE RECETTE (PHOTO / SCAN)
# ---------------------------------------------------------
elif menu == "📸 Ajouter une Recette (Photo)":
    st.title("Ajouter une Recette via une Photo")

    uploaded_file = st.file_uploader(
        "Prenez en photo ou téléchargez une page de recette (image)",
        type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Photo importée", use_container_width=True)
        st.info(
            "Analyse de l'image en cours par l'intelligence artificielle..."
        )

        # Simulation d'extraction OCR intelligente
        titre_ext = "Tarte rustique aux légumes du soleil"
        cat_ext = "Plats"
        saison_ext = "Été"
        temps_ext = "35 min"
        ing_ext = [
            "Pâte feuilletée (1)",
            "Courgettes (2)",
            "Tomates (3)",
            "Moutarde à l'ancienne (2 c. à s.)",
        ]
        etapes_ext = "1. Dérouler la pâte. 2. Badigeonner de moutarde. 3. Disposer les légumes coupés en rondelles. 4. Cuire 30 min à 180°C."

        st.success("Analyse réussie ! Voici les informations extraites :")

        with st.form("form_validation"):
            n_titre = st.text_input("Titre de la recette", value=titre_ext)
            n_cat = st.selectbox(
                "Catégorie",
                [
                    "Entrées",
                    "Plats",
                    "Desserts",
                    "Apéritifs / Snacks",
                ],
                index=1,
            )
            n_saison = st.selectbox(
                "Saison idéale",
                ["Printemps", "Été", "Automne / Hiver", "Toutes saisons"],
                index=1,
            )
            n_temps = st.text_input("Temps de préparation", value=temps_ext)

            st.markdown("**Ingrédients détectés (modifiables) :**")
            ing_text = st.text_area(
                "Un ingrédient par ligne", value="\n".join(ing_ext)
            )

            st.markdown("**Étapes :**")
            n_etapes = st.text_area("Préparation", value=etapes_ext)

            submitted = st.form_submit_button(
                "Valider et enregistrer dans mon carnet"
            )
            if submitted:
                nouvelle_recette = {
                    "id": len(st.session_state.recettes) + 1,
                    "titre": n_titre,
                    "categorie": n_cat,
                    "saison": n_saison,
                    "temps": n_temps,
                    "ingredients": [
                        i.strip() for i in ing_text.split("\n") if i.strip()
                    ],
                    "etapes": n_etapes,
                }
                st.session_state.recettes.append(nouvelle_recette)
                st.balloons()
                st.success(
                    f"La recette '{n_titre}' a bien été enregistrée et classée dans '{n_cat}' !"
                )

# ---------------------------------------------------------
# 3. SUGGESTIONS & MENUS
# ---------------------------------------------------------
elif menu == "🗓️ Suggestions & Menus":
    st.title("Suggestions & Idées de Menus")

    st.markdown(
        "### 💡 Suggestions basées sur la saison actuelle et vos placards"
    )
    col1, col2 = st.columns(2)

    with col1:
        st.info("🍂 **Suggestion du moment (Automne)**")
        st.write(
            "Puisque c'est la saison des courges et des plats réconfortants :"
        )
        if st.button("Suggérer un menu d'automne"):
            recette_sugg = [
                r
                for r in st.session_state.recettes
                if "Automne" in r["saison"]
            ]
            if recette_sugg:
                st.write(f"✨ Nous vous conseillons : **{recette_sugg[0]['titre']}**")
                if st.button("Ajouter cette suggestion au menu"):
                    st.session_state.menu_semaine.append(recette_sugg[0])
                    st.success("Ajouté !")

    with col2:
        st.info("🥦 **Anti-gaspillage / Ingrédients dispos**")
        ingredients_frigo = st.multiselect(
            "Qu'avez-vous dans le frigo à épuiser ?",
            ["Courge butternut", "Tomates", "Crème fraîche", "Œufs", "Fromage"],
        )
        if ingredients_frigo:
            st.write("💡 Recettes réalisables avec ces ingrédients :")
            for r in st.session_state.recettes:
                if any(
                    any(ing.lower().find(inf.lower()) != -1 for inf in ingredients_frigo)
                    for ing in r["ingredients"]
                ):
                    st.write(f"- ✅ **{r['titre']}**")

    st.markdown("---")
    st.subheader("📋 Votre Menu de la Semaine")
    if not st.session_state.menu_semaine:
        st.write(
            "Aucun plat planifié pour l'instant. Parcourez vos recettes pour en ajouter !"
        )
    else:
        for idx, item in enumerate(st.session_state.menu_semaine):
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.write(
                    f"**{idx + 1}.** {item['titre']} (*{item['categorie']}*)"
                )
            with col_b:
                if st.button("❌", key=f"del_menu_{idx}"):
                    st.session_state.menu_semaine.pop(idx)
                    st.rerun()

# ---------------------------------------------------------
# 4. LISTE DE COURSES
# ---------------------------------------------------------
elif menu == "🛒 Liste de Courses":
    st.title("Liste de Courses Automatisée")

    if not st.session_state.menu_semaine:
        st.warning(
            "Votre menu de la semaine est vide. Ajoutez des recettes pour générer votre liste de courses !"
        )
    else:
        st.write(
            "Voici la liste consolidée des ingrédients nécessaires pour vos menus de la semaine :"
        )

        # Extraction et fusion des ingrédients
        tous_les_ingredients = []
        for r in st.session_state.menu_semaine:
            for ing in r["ingredients"]:
                tous_les_ingredients.append(ing)

        # Affichage sous forme de liste à cocher
        st.markdown("---")
        for i, ingredient in enumerate(tous_les_ingredients):
            st.checkbox(f"{ingredient}", key=f"course_{i}")

        if st.button("🗑️ Vider la liste / Réinitialiser le menu"):
            st.session_state.menu_semaine = []
            st.rerun()
