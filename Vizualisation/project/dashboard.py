import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
from PIL import Image
import missingno as msno
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests
import json
import geopandas as gpd
import geopy.distance

# --- Configuration de la Page Streamlit ---
st.set_page_config(
    page_title="Dashboard Data Viz",
    page_icon=":rocket:", 
    layout="wide",
)

# --- Fonctions utilitaires ---
def count_rows(rows):
    return len(rows)

def load_lottiefile(filepath: str):
    """Charge une animation Lottie depuis un fichier local."""
    with open(filepath, "r") as f:
        return json.load(f)
    
def show_data_preview(df, title):
    st.write(f"**Aperçu des données ({title}) :**")
    st.dataframe(df.head())  # Affiche les 5 premières lignes

# Charger les animations Lottie 
lottie_taxi = load_lottiefile("taxi.json")
lottie_data = load_lottiefile("data.json") 


# --- Chargement et Prétraitement des Données ---

df_uber = pd.read_csv('uber.csv', delimiter=",")
df_uber['Date/Time'] = pd.to_datetime(df_uber['Date/Time'], format='%m/%d/%Y %H:%M:%S')
df_uber["day"] = df_uber["Date/Time"].map(lambda dt: dt.day)
df_uber["weekday"] = df_uber["Date/Time"].map(lambda dt: dt.weekday())
df_uber["hour"] = df_uber["Date/Time"].map(lambda dt: dt.hour)
df_uber["month"] = df_uber["Date/Time"].map(lambda dt: dt.month)  # Ajout du mois

df_tips = pd.read_csv("tips.csv")
df_tips["day"] = df_tips["day"].astype("category")
df_tips["time"] = df_tips["time"].astype("category")


# Charger le fichier GeoJSON
@st.cache_data
def load_geojson(filepath):
    with open(filepath, "r") as f:
        return json.load(f)

nyc_geojson = load_geojson("nyc.geojson")

# Charger le shapefile ou GeoJSON précis de New York (remplacez par le chemin correct)
nyc_boroughs = gpd.read_file("nyc.geojson") # ou nyc_boroughs.geojson

# --- Images ---
uber_logo = Image.open('Uber.png')  
my_pic = Image.open('CV.jpg')
efrei_logo = Image.open('efrei.png') 

# --- Sidebar ---
with st.sidebar:
    # Logo et Titre
    st.image(efrei_logo, width=200)
    st.title("Data Explorer") 

    # Section À propos (utilisez st.expander pour la réduire par défaut)
    with st.expander("À propos de Samuel BIENVENU 👋"): 
        st.image(my_pic, use_column_width=True) # Assurez-vous que l'image s'adapte à la sidebar
        st.markdown("Passionné par la Data Science et la création de dashboards \
                    interactifs pour révéler des informations exploitables.")
        st.write("**Compétences:** Python, Data Analysis, Machine Learning, \
                 Data Visualization (Streamlit, Plotly, etc.)")

        st.markdown("---")  # Séparateur
        
        st.header("Contactez-moi 📞") #Section contact
        st.write("Email: samuel.bienvenu@protonmail.com")
        st.write("Téléphone: +33 (0) 6 XX XX XX XX") # Remplacez par votre numéro
        st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/votre-profil-linkedin/)") #Remplacer le lien vers linkedin 

    # --- Formulaire de Contact --- 
    with st.expander("Formulaire de Contact 📧"):
        st.write("Envie de collaborer ? Envoyez-moi un message !")
        nom = st.text_input("Votre Nom")
        email = st.text_input("Votre Email")
        objet = st.text_input("Objet du Message")
        message = st.text_area("Votre Message")

        if st.button("Envoyer"):
            # Gérer l'envoi du message (voir explications ci-dessous)
            st.success("Message envoyé avec succès !") 

    # Copyright en bas de la sidebar
    st.sidebar.markdown(
        """
        <div style="text-align: center; font-size: 12px; margin-top: 20px;">
            Copyright © 2024 Samuel BIENVENU. Tous droits réservés.
        </div>
        """,
        unsafe_allow_html=True
    )


# --- Tabs ---
onglet_accueil, onglet_uber, onglet_pourboires, onglet_avance = st.tabs(
    ["Accueil 🏠", "Analyse Uber 🚕", "Analyse des Pourboires 🍽️", "Visualisations Avancées ✨"]
)

# --- Page d'accueil ---
with onglet_accueil:
    st.title("Dashboard d'Analyse de Données 📊")  # Titre plus descriptif

    # Logo Uber centré avec une meilleure présentation
    st.image(uber_logo, width=200)


    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h2 style="color:#00A0E9;font-family:Arial;font-size: 20px; font-weight: bold"> Exploration des données Uber et des pourboires de restaurants</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    Ce dashboard interactif vous permet d'explorer les données Uber et les pourboires de restaurants de manière approfondie.  
    Découvrez les visualisations et analyses ci-dessous :
    """)

    st.markdown("""
    **Fonctionnalités clés :**
    * **Analyse des courses Uber :**
        * Visualisation de la fréquence des courses par jour, heure, jour de la semaine et base Uber.
        * Carte interactive et animée montrant l'évolution des courses Uber à New York par arrondissement.
    * **Analyse des pourboires :**
        * Visualisations interactives des pourboires en fonction de la facture totale, du jour de la semaine, du sexe et de l'habitude de fumer.
        * Exploration des relations entre ces variables grâce à un tableau croisé dynamique.
    """)

# --- Page Analyse Uber ---
with onglet_uber:
    st.title("Analyse des Données Uber 🚕")
    show_data_preview(df_uber, "Uber") #Aperçu des données brutes

    # --- Filtres ---
    col1, col2 = st.columns(2)
    with col1:
        jour_filtre = st.slider("Jour du mois:", 1, 30, (1, 30))
    with col2:
        heure_filtre = st.slider("Heure de la journée:", 0, 23, (0, 23))

    # --- Appliquer les filtres ---
    df_uber_filtree = df_uber[
        (df_uber["day"] >= jour_filtre[0]) & (df_uber["day"] <= jour_filtre[1]) &
        (df_uber["hour"] >= heure_filtre[0]) & (df_uber["hour"] <= heure_filtre[1])
    ]

    # --- Visualisations ---
    st.header("Visualisations des Courses Uber")

    # --- Graphique 1: Histogramme des courses par heure ---
    fig_heure = px.histogram(
        df_uber_filtree, x="hour", title="Nombre de courses par heure"
    )
    st.plotly_chart(fig_heure)

    # --- Graphique 2: Carte 3D des points de dépose ---
    st.subheader("Carte 3D des points de dépose")
    midpoint = (np.average(df_uber_filtree["Lat"]), np.average(df_uber_filtree["Lon"]))
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=pdk.ViewState(
            latitude=midpoint[0],
            longitude=midpoint[1],
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                "HexagonLayer",
                df_uber_filtree[["Lon", "Lat"]].rename(columns={"Lon": "lon", "Lat": "lat"}),
                get_position=["lon", "lat"],
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ],
    ))

    # Nouveau Graphique 3:  Heatmap des courses Uber
    st.subheader("Heatmap des courses Uber")
    fig_heatmap = px.density_mapbox(
    df_uber_filtree, lat="Lat", lon="Lon", radius=10,  # Supprimer z="hour"
    center=dict(lat=40.7128, lon=-74.0060), zoom=10,
    mapbox_style="carto-positron", title="Densité des courses Uber"
    )
    st.plotly_chart(fig_heatmap)

    # 4. Diagramme circulaire des différentes bases Uber
    st.subheader("Proportion des trajets par base Uber")
    base_counts = df_uber_filtree["Base"].value_counts()
    fig_pie = px.pie(
        values=base_counts.values, 
        names=base_counts.index, 
        title="Proportion des trajets par base Uber"
    )
    st.plotly_chart(fig_pie)


    # 5. Tableau croisé dynamique du nombre de trajets par jour et heure
    st.subheader("Nombre de trajets par jour et heure")
    df_pivot = df_uber_filtree.groupby(["weekday", "hour"]).size().unstack()
    st.dataframe(df_pivot) # Affiche le tableau croisé dynamique

    # Nouveau graphique : Histogramme du nombre de trajets par jour de la semaine
    st.subheader("Nombre de trajets par jour de la semaine")
    fig_weekday = px.histogram(df_uber_filtree, x='weekday', title="Nombre de trajets par jour de la semaine", nbins=7)
    st.plotly_chart(fig_weekday)

# --- Page Analyse des Pourboires ---
with onglet_pourboires:
    st.title("Analyse des Données de Pourboires 🍽️")
    show_data_preview(df_tips, "Tips") #Aperçu des données brutes

    # --- Filtres ---
    col1, col2, col3 = st.columns(3)
    with col1:
        jour_filtre_tips = st.multiselect("Jour de la semaine:", df_tips["day"].unique(), default=df_tips["day"].unique())
    with col2:
        fumeur_filtre = st.radio("Fumeur :", ["All", "Yes", "No"], index=0)
    with col3:
        # Utiliser st.radio pour le filtre "Sexe" avec une option "All"
        sexe_filtre = st.radio("Sexe :", ["All", "Male", "Female"], index=0)

    # --- Appliquer les filtres ---
    df_tips_filtree = df_tips[df_tips["day"].isin(jour_filtre_tips)]
    if sexe_filtre != "All":
        df_tips_filtree = df_tips_filtree[df_tips_filtree["sex"] == sexe_filtre]
    if fumeur_filtre != "All":
        df_tips_filtree = df_tips_filtree[df_tips_filtree["smoker"] == fumeur_filtre]

    # --- Visualisations ---
    st.header("Visualisation des données de pourboires")

    # --- Graphique 1 :  Scatter plot pour la relation entre Facture et Pourboire ---
    fig_scatter = px.scatter(df_tips_filtree, x="total_bill", y="tip", 
                         color="day", size="size", 
                         title="Relation facture totale - pourboire")
    st.plotly_chart(fig_scatter)

    # --- Graphique 2 : Violin Plot  ---
    fig_violin = px.violin(df_tips_filtree, x="day", y="tip", color="sex", 
                       box=True, points="all", 
                       title="Distribution des pourboires par jour et sexe")
    st.plotly_chart(fig_violin)

    # Nouveau Graphique 3:  Boxplot des pourboires par jour de la semaine et sexe
    st.subheader("Distribution des pourboires par jour et sexe")
    fig_boxplot_tips, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x="day", y="tip", hue="sex", data=df_tips_filtree, ax=ax)
    ax.set_xlabel('Jour de la semaine')
    ax.set_ylabel('Pourboire')
    ax.set_title('Distribution des pourboires par jour et sexe')
    st.pyplot(fig_boxplot_tips)


    # Nouveau Graphique 4: Histogramme des pourboires
    st.subheader("Distribution des pourboires")
    fig_hist_tips = px.histogram(df_tips_filtree, x="tip", nbins=20, title="Distribution des pourboires")
    st.plotly_chart(fig_hist_tips)

    # Nouveau graphique : Nuage de points avec régression
    st.subheader("Relation entre pourboire et facture totale")
    fig_regplot, ax = plt.subplots(figsize=(10,6))
    sns.regplot(x="total_bill", y="tip", data=df_tips_filtree, ax=ax)
    ax.set_xlabel("Montant total de la facture")
    ax.set_ylabel("Pourboire")
    ax.set_title("Relation entre pourboire et facture totale")
    st.pyplot(fig_regplot)

    # Nouveau graphique : Boite à moustache des pourboires par taille du groupe
    st.subheader("Distribution des pourboires par taille du groupe")
    fig_boxplot_size, ax = plt.subplots(figsize=(10,6))
    sns.boxplot(x="size", y="tip", data=df_tips_filtree, ax=ax)
    ax.set_xlabel("Taille du groupe")
    ax.set_ylabel("Pourboire")
    ax.set_title("Distribution des pourboires par taille du groupe")
    st.pyplot(fig_boxplot_size)

    # Nouveau graphique: Tableau croisé dynamique
    st.subheader("Tableau croisé dynamique (moyenne des pourboires)")
    df_pivot_tips = pd.pivot_table(df_tips_filtree, values='tip', index=['day'], columns=['sex'], aggfunc=np.mean)
    st.dataframe(df_pivot_tips)

    # Nouveau graphique: Histogramme des pourboires en pourcentage
    st.subheader("Distribution des pourboires en pourcentage du total")
    df_tips_filtree['pourcentage_pourboire'] = (df_tips_filtree['tip'] / df_tips_filtree['total_bill']) * 100
    fig_hist_pourcentage, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df_tips_filtree['pourcentage_pourboire'], kde=True, ax=ax)
    ax.set_xlabel("Pourcentage de pourboire")
    ax.set_ylabel("Fréquence")
    ax.set_title("Distribution des pourboires en pourcentage")
    st.pyplot(fig_hist_pourcentage)

# --- Page Visualisations Avancées ---
with onglet_avance:
    st.title("Plongeons dans des Visualisations Époustouflantes! 🚀")

    # --- Exemple 1: Graphique 3D interactif avec Plotly ---
    st.header("1. Nuage de points 3D : Relation Facture-Pourboire-Jour")

    fig = px.scatter_3d(
        df_tips, 
        x="total_bill", 
        y="tip", 
        z="day", 
        color="sex", 
        size="size",
        title="Relation 3D entre Facture, Pourboire et Jour",
        labels={"total_bill": "Facture Totale", "tip": "Pourboire", "day": "Jour", "sex": "Sexe"},
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Exemple 2: Carte Choroplèthe Animée (New York) ---
    st.header("2. Carte Choroplèthe Animée : Évolution des Courses Uber à New York par Arrondissement")

    # Préparation des données pour la carte (CORRECTION)
    df_uber_geo = gpd.GeoDataFrame(
    df_uber,
    geometry=gpd.points_from_xy(df_uber.Lon, df_uber.Lat),
    crs="EPSG:4326"
    )

    # Jointure spatiale (spatial join)
    df_joined = gpd.sjoin(df_uber_geo, nyc_boroughs, how="left", predicate="intersects")

    # Grouper les données
    df_joined['Date'] = pd.to_datetime(df_joined['Date/Time']).dt.date
    df_grouped = df_joined.groupby(["Date", "name"]).size().reset_index(name="Nombre de Courses")

    # Création de la carte choroplèthe
    fig_choro_ny = px.choropleth(
        df_grouped,
        geojson=nyc_geojson,
        locations="name",  # utiliser 'name' car c'est le nom dans le GeoJSON
        featureidkey="properties.name",
        color="Nombre de Courses",
        animation_frame="Date",
        color_continuous_scale="Viridis",
        range_color=(0, df_grouped["Nombre de Courses"].max()),
        title="Évolution des Courses Uber à New York par Arrondissement",
        hover_data=["Nombre de Courses"],
        scope="north america",
    )

    # Amélioration de l'apparence et projection
    fig_choro_ny.update_geos(
        center=dict(lon=-74.0060, lat=40.7128),
        fitbounds="locations",
        projection=dict(type="albers usa", parallels=[30, 40]),
    )
    fig_choro_ny.update_layout(
        geo=dict(
            showland=True,
            landcolor="rgb(217, 217, 217)",
            countrycolor="white"
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    # Ajouter un slider pour sélectionner la date
    dates_uniques = df_grouped["Date"].unique()
    fig_choro_ny.update_layout(
        sliders=[{"steps": [{"args": [["Date", date]], "label": date.strftime("%Y-%m-%d"), "method": "animate",}
                             for date in dates_uniques],
                 }],
    )

    st.plotly_chart(fig_choro_ny, use_container_width=True)


    # --- Exemple 3: Graphique Sunburst Interactif ---
    st.header("3. Graphique Sunburst : Ventilation des Pourboires")
    
    fig_sunburst = px.sunburst(
        df_tips, 
        path=['day', 'sex', 'time'],
        values='tip',
        title='Ventilation des Pourboires par Jour, Sexe et Moment'
    )
    st.plotly_chart(fig_sunburst)
