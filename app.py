import datetime
import time
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
            ["Toutes", "Printemps", "Été", "Automne / Hiver", "Toutes saisons"],
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
        
        if st.button("⚡ Analyse ultra-rapide", key="btn_lancer_analyse"):
            with st.spinner("Analyse éclair en cours..."):
                try:
                    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
                    
                    # Compression agressive et instantanée pour réduire le poids de l'image à analyser
                    img = Image.open(uploaded_file)
                    img.thumbnail((800, 800))
                    
                    prompt = (
                        "Extrais rapidement de cette image : \n"
                        "TITRE: [Nom]\n"
                        "CATEGORIE: [Entrées, Plats, ou Desserts]\n"
                        "SAISON: [Printemps, Été, Automne / Hiver, ou Toutes saisons]\n"
                        "TEMPS: [ex: 30 min]\n"
                        "INGREDIENTS:\n"
                        "- Ingrédient 1\n"
                        "ETAPES:\n"
                        "[Étapes courtes]"
                    )
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[img, prompt]
                    )
                    
                    if response:
                        st.session_state.derniere_analyse = response.text
                        st.success("Analyse terminée !")
                    
                except Exception as e:
                    st.error(f"Erreur : {e}")

    # Si une analyse est en cache dans la session, on l'affiche avec un bouton d'enregistrement
    if "derniere_analyse" in st.session_state:
        st.markdown("### 📋 Résultat de l'analyse :")
        st.write(st.session_state.derniere_analyse)
        
        if st.button("💾 Enregistrer cette recette dans ma bibliothèque", key="btn_sauver_recette"):
            texte = st.session_state.derniere_analyse
            
            nouveau_titre = "Recette scannée"
            nouvelle_cat = "Plats"
            nouvelle_saison = "Toutes saisons"
            nouveau_temps = "30 min"
            ingredients_list = []
            etapes_texte = texte
            
            en_cours_ingredients = False
            en_cours_etapes = False
            lignes_etapes = []
            
            for ligne in texte.split("\n"):
                ligne_clean = ligne.strip()
                if ligne_clean.startswith("TITRE:"):
                    nouveau_titre = ligne_clean.replace("TITRE:", "").strip()
                elif ligne_clean.startswith("CATEGORIE:"):
                    nouvelle_cat = ligne_clean.replace("CATEGORIE:", "").strip()
                elif ligne_clean.startswith("SAISON:"):
                    nouvelle_saison = ligne_clean.replace("SAISON:", "").strip()
                elif ligne_clean.startswith("TEMPS:"):
                    nouveau_temps = ligne_clean.replace("TEMPS:", "").strip()
                elif ligne_clean.startswith("INGREDIENTS:"):
                    en_cours_ingredients = True
                    en_cours_etapes = False
                    continue
                elif ligne_clean.startswith("ETAPES:"):
                    en_cours_ingredients = False
                    en_cours_etapes = True
                    continue
                
                if en_cours_ingredients and ligne_clean.startswith("-"):
                    ingredients_list.append(ligne_clean.lstrip("- ").strip())
                elif en_cours_etapes and ligne_clean:
                    lignes_etapes.append(ligne_clean)
            
            if not ingredients_list:
                ingredients_list = ["Ingrédients extraits automatiquement"]
            if lignes_etapes:
                etapes_texte = "\n".join(lignes_etapes)
                
            nouvel_id = len(st.session_state.recettes) + 1
            nouvelle_recette = {
                "id": nouvel_id,
                "titre": nouveau_titre,
                "categorie": nouvelle_cat,
                "saison": nouvelle_saison,
                "temps": nouveau_temps,
                "ingredients": ingredients_list,
                "etapes": etapes_texte
            }
            
            st.session_state.recettes.append(nouvelle_recette)
            st.success(f"🎉 '{nouveau_titre}' a été enregistrée avec succès dans votre bibliothèque !")
            del st.session_state.derniere_analyse
            st.rerun()

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
        st.info("🍂 **Suggestion du moment**")
        st.write(
            "Puisque c'est la saison, profitez de vos recettes enregistrées !"
        )
        if st.button("Suggérer une recette au hasard"):
            import random
            if st.session_state.recettes:
                recette_sugg = random.choice(st.session_state.recettes)
                st.write(f"✨ Nous vous conseillons : **{recette_sugg['titre']}**")
                if st.button("Ajouter cette suggestion au menu"):
                    st.session_state.menu_semaine.append(recette_sugg)
                    st.success("Ajouté !")

    with col2:
        st.info("🥦 **Anti-gaspillage / Ingrédients dispos**")
        ingredients_frigo = st.multiselect(
            "Qu'avez-vous dans le frigo à épuiser ?",
            ["Tomates", "Crème fraîche", "Œufs", "Fromage", "Courge butternut"],
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
