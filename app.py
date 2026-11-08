import datetime
from google import genai
from PIL import Image
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
    key="navigation_principale",
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
if menu == "📸 Ajouter une Recette (Photo)":
    st.header("📸 Ajouter une Recette par Photo")
    
    uploaded_file = st.file_uploader("Prends en photo ou importe une page de recette", type=["jpg", "jpeg", "png"], key="upload_photo_recette")

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Photo de la recette importée", width='stretch')
        
        if st.button("✨ Analyser automatiquement la photo", key="btn_lancer_analyse"):
            with st.spinner("Analyse de la photo en cours par l'IA..."):
                try:
                    # Initialisation du client officiel Google GenAI
                    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                    
                    prompt = (
                        "Analyse cette image de recette de cuisine et extrait précisément : "
                        "1. Le titre exact de la recette\n"
                        "2. La catégorie (Entrées, Plats, ou Desserts)\n"
                        "3. La saison idéale (Printemps, Été, Automne, Hiver ou Toutes saisons)\n"
                        "4. Le temps de préparation total en minutes (chiffre uniquement)\n"
                        "5. La liste complète des ingrédients (un par ligne)\n"
                        "6. Les étapes de préparation détaillées"
                    )
                    
                    # Conversion propre de l'image pour l'API moderne
                    img = Image.open(uploaded_file)
                    
                    # Utilisation du modèle flash standard universel
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[img, prompt]
                    )
                    
                    st.success("Recette analysée avec succès !")
                    st.write(response.text)
                    
                except Exception as e:
                    st.error(f"Erreur lors de l'analyse : {e}")

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

        tous_les_ingredients = []
        for r in st.session_state.menu_semaine:
            for ing in r["ingredients"]:
                tous_les_ingredients.append(ing)

        st.markdown("---")
        for i, ingredient in enumerate(tous_les_ingredients):
            st.checkbox(f"{ingredient}", key=f"course_{i}")

        if st.button("🗑️ Vider la liste / Réinitialiser le menu"):
            st.session_state.menu_semaine = []
            st.rerun()
