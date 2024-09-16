import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk
import geopandas as gpd

# 1. Préparation des données

# Charger le dataset
df = pd.read_csv("consommation-annuelle-d-electricite-et-gaz-par-region.csv", sep=";")

# Remplacer les valeurs manquantes par 0
df.fillna(0, inplace=True)

# Convertir 'part_thermosensible' en pourcentage
df['part_thermosensible'] = df['part_thermosensible'] * 100

# Calculer la consommation totale d'énergie (électricité + gaz) 
df["conso_totale"] = df["conso_totale_mwh"] + df["conso_totale_a_usages_thermosensibles_mwh"] + df["conso_totale_a_usages_non_thermosensibles_mwh"]

# Calculer la consommation par habitant pour l'ensemble du dataset
df["conso_par_habitant"] = df["conso_totale"] / df["nombre_d_habitants"]

# Charger le GeoJSON des régions françaises et extraire les coordonnées
regions_geojson = gpd.read_file("https://france-geojson.gregoiredavid.fr/repo/regions.geojson")
regions_geojson["code"] = regions_geojson["code"].astype(int)  
regions_geojson["longitude"] = regions_geojson["geometry"].centroid.x
regions_geojson["latitude"] = regions_geojson["geometry"].centroid.y

# Fusionner les coordonnées avec le DataFrame principal
df = df.merge(regions_geojson[["code", "longitude", "latitude"]], left_on="code_region", right_on="code")

# 2. Interface utilisateur de Streamlit

# Style personnalisé pour la sidebar
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf,#2e7bcf);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Votre photo
st.sidebar.image("CV.jpg", use_column_width=True)

# Vos informations personnelles
st.sidebar.markdown("**Prénom NOM**")
st.sidebar.markdown("**Email :** votre_email@example.com")
st.sidebar.markdown("**LinkedIn :**  linkedin.com/in/votre_profil")
st.sidebar.markdown("---")

# Créer les pages du dashboard
pages = ["Présentation", "Dashboard"]
page_selected = st.sidebar.radio("Navigation", pages)

# 3.1 Page de présentation
# 3. Contenu des pages

# 3.1 Page de présentation
if page_selected == "Présentation":
    
    st.header("Bienvenue sur mon dashboard!")

    # Colonnes pour organiser la page de présentation
    col1, col2 = st.columns([3, 1])

    # Description du dashboard dans la première colonne
    with col1:
        st.markdown("""
            # Analyse de la consommation d'énergie en France (2011-2022)

            Ce dashboard interactif vous permet d'explorer les tendances de consommation d'énergie 
            en France, à travers une variété de perspectives et de filtres dynamiques. 
            Découvrez comment la consommation d'électricité et de gaz a évolué au fil des années, 
            en fonction des régions, des secteurs d'activité et des opérateurs.

            **Plongez au cœur des données et découvrez des insights fascinants sur la consommation d'énergie en France!**
        """)

        st.subheader("Fonctionnalités:")
        st.markdown("""
            * **Visualisations interactives:**  Explorez les données à travers des cartes choroplèthes, 
            des graphiques en barres, en courbes et à nuage de points, tous interactifs.
            * **Filtres dynamiques:**  Affinez votre analyse en sélectionnant des années spécifiques, 
            des régions, des filières énergétiques (électricité ou gaz), des secteurs d'activité 
            et des opérateurs.
            * **Thermosensibilité:**  Analysez l'impact des variations de température sur la 
            consommation d'énergie et découvrez les régions les plus thermosensibles.
            * **Caractéristiques du logement:**  Explorez comment la consommation d'énergie par 
            habitant est influencée par des facteurs tels que le taux de logements collectifs, le 
            taux de chauffage électrique et le taux de résidences principales.
            * **Carte 3D immersive:** Visualisez la consommation d'énergie par région de manière 
            interactive et géographique grâce à une carte 3D immersive.
        """)

        st.subheader("Sources de données:")
        st.markdown("""
            * [Données publiques sur la consommation d'énergie]
              (lien vers la source du dataset - remplacez par le lien réel)
        """)

    # Image dans la deuxième colonne
    with col2:
        st.image("CV.jpg", use_column_width=True) 

elif page_selected == "Dashboard":

    # Titre du dashboard
    st.title("Consommation d'énergie en France: Électricité et Gaz (2011-2022)")

    # Sidebar globale pour les filtres

    # Année (filtre commun à toutes les sections)
    annee_selected = st.sidebar.selectbox("Sélectionnez l'année", df["annee"].unique())

    # Filière (filtre commun à la vue d'ensemble, la thermosensibilité et la carte 3D)
    filiere_selected = st.sidebar.selectbox("Sélectionnez la filière énergétique", df["filiere"].unique())

    # Opérateur (filtre pour la vue d'ensemble)
    operateur_selected = st.sidebar.multiselect("Sélectionnez l'opérateur", df["operateur"].unique())

    # Région (filtre pour l'analyse temporelle et les caractéristiques du logement)
    region_selected = st.sidebar.selectbox("Sélectionnez la région", df["nom_region"].unique())

    # Secteur d'activité (filtre pour l'analyse temporelle et la carte 3D)
    secteur_selected = st.sidebar.selectbox("Sélectionnez le secteur d'activité", df["code_grand_secteur"].unique())

    # 3. Visualisations et analyses

    # 3.1 Vue d'ensemble (filtrage par année, filière et opérateur)

    st.header("Vue d'ensemble")

    # Filtrer le DataFrame en fonction des selections de la sidebar
    filtered_df = df[(df["annee"] == annee_selected) & (df["filiere"] == filiere_selected)]
    if operateur_selected:
        filtered_df = filtered_df[filtered_df["operateur"].isin(operateur_selected)]

    # Carte choroplèthe
    st.subheader("Consommation totale d'énergie par région")
    fig = px.choropleth(
        filtered_df,
        geojson="https://france-geojson.gregoiredavid.fr/repo/regions.geojson",
        locations="code_region",
        featureidkey="properties.code",
        color="conso_totale",
        color_continuous_scale="Viridis",
        hover_name="nom_region",
        hover_data={"conso_totale": True, "conso_moyenne_mwh": True},
        title="Consommation d'énergie par région",
        labels={"conso_totale": "Consommation totale (MWh)"}
    )
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig)

    # Graphique en barres empilées
    st.subheader("Répartition de la consommation par secteur d'activité")
    fig = px.bar(
        filtered_df,
        x="code_grand_secteur",
        y="conso_totale",
        color="code_grand_secteur",
        title="Consommation d'énergie par secteur d'activité",
        labels={"conso_totale": "Consommation totale (MWh)"}
    )
    st.plotly_chart(fig)

    # 3.2 Analyse temporelle (filtrage par région et secteur)

    st.header("Analyse temporelle")
    filtered_df = df[(df["nom_region"] == region_selected) & (df["code_grand_secteur"] == secteur_selected)]

    # Graphique en courbes
    st.subheader("Évolution de la consommation d'énergie au fil des années")
    fig = px.line(
        filtered_df,
        x="annee",
        y="conso_totale",
        color="filiere",
        title="Consommation d'énergie au fil des années",
        labels={"conso_totale": "Consommation totale (MWh)"}
    )
    st.plotly_chart(fig)

    # Graphique en barres groupées
    st.subheader("Comparaison de la consommation d'électricité et de gaz")
    fig = px.bar(
        filtered_df,
        x="annee",
        y="conso_totale",
        color="filiere",
        barmode="group",
        title="Consommation d'électricité et de gaz par année",
        labels={"conso_totale": "Consommation totale (MWh)"}
    )
    st.plotly_chart(fig)

    # 3.3 Thermosensibilité (filtrage par année et filière)

    st.header("Thermosensibilité")
    filtered_df = df[(df["annee"] == annee_selected) & (df["filiere"] == filiere_selected)]

    # Carte choroplèthe
    st.subheader("Part de la consommation thermosensible par région")
    fig = px.choropleth(
        filtered_df,
        geojson="https://france-geojson.gregoiredavid.fr/repo/regions.geojson",
        locations="code_region",
        featureidkey="properties.code",
        color="part_thermosensible",
        color_continuous_scale="RdBu_r",
        hover_name="nom_region",
        hover_data={
            "part_thermosensible": True,
            "conso_totale_a_usages_thermosensibles_mwh": True
        },
        title="Part de la consommation thermosensible par région",
        labels={"part_thermosensible": "Part thermosensible (%)"}
    )
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig)

    # Graphique à nuage de points
    st.subheader("Relation entre la thermosensibilité et les DJU")
    fig = px.scatter(
        filtered_df,
        x="dju_a_tr",
        y="thermosensibilite_totale_kwh_dju",
        hover_name="nom_region",
        hover_data={
            "dju_a_tr": True,
            "thermosensibilite_totale_kwh_dju": True
        },
        title="Relation entre la thermosensibilité et les DJU",
        labels={
            "dju_a_tr": "DJU (base température de référence)",
            "thermosensibilite_totale_kwh_dju": "Thermosensibilité totale (kWh/DJU)"
        }
    )
    st.plotly_chart(fig)

    # 3.4 Caractéristiques du logement (filtrage par année et région)

    st.header("Caractéristiques du logement")
    filtered_df = df[(df["annee"] == annee_selected) & (df["nom_region"] == region_selected)]

    # Calcul de la consommation par habitant pour chaque ligne
    filtered_df["conso_par_habitant"] = filtered_df["conso_totale"] / filtered_df["nombre_d_habitants"]

    # Graphiques en barres
    caractéristiques = ["taux_de_logements_collectifs", "taux_de_chauffage_electrique", "taux_de_residences_principales"]
    for caractéristique in caractéristiques:
        st.subheader(f"Consommation d'énergie par habitant en fonction de {caractéristique}")
        fig = px.bar(
            filtered_df,
            x=caractéristique,
            y="conso_par_habitant",
            color="filiere",
            labels={"conso_par_habitant": "Consommation par habitant (MWh)"},
            hover_data={caractéristique: True, "conso_par_habitant": True, "filiere": True}
        )
        st.plotly_chart(fig)

    # 3.5 Comparaison de la consommation moyenne par habitant entre les régions (avec sélection par année)

    st.subheader("Consommation moyenne par habitant et par région")
    # Calculer la consommation moyenne par habitant pour chaque région
    region_conso = df[df["annee"] == annee_selected].groupby("nom_region").apply(lambda x: x["conso_totale"].sum() / x["nombre_d_habitants"].sum()).sort_values(ascending=False)

    fig = px.bar(
        region_conso,
        x=region_conso.index,
        y=region_conso.values,
        title=f"Consommation moyenne d'énergie par habitant en {annee_selected}",
        labels={"y": "Consommation moyenne par habitant (MWh)", "nom_region": "Région"}
    )
    st.plotly_chart(fig)

    # 3.6 Top 5 des régions les plus consommatrices (avec sélection par année)

    st.header("Analyses complémentaires")
    st.subheader("Top 5 des régions les plus consommatrices")

    top_regions = df.groupby(["annee", "nom_region"])["conso_totale"].sum().reset_index()
    top_regions = top_regions[top_regions["annee"] == annee_selected].sort_values(by="conso_totale", ascending=False).head(5)
    fig = px.bar(
        top_regions,
        x="nom_region",
        y="conso_totale",
        title=f"Top 5 des régions les plus consommatrices en {annee_selected}",
        labels={"conso_totale": "Consommation totale (MWh)"}
    )
    st.plotly_chart(fig)

    # 3.7 Analyse de la thermosensibilité par DJU (Degrés Jour Unifiés)
    # (Utilise le dataframe complet pour observer les tendances générales)

    st.subheader("Analyse de la thermosensibilité par DJU")
    dju_type = st.sidebar.selectbox("Type de DJU", ["dju_a_tr", "dju_a_tn"]) # Selection dans la sidebar
    fig = px.scatter(
        df.dropna(),
        x=dju_type,
        y="thermosensibilite_totale_kwh_dju",
        color="nom_region",
        hover_name="nom_region",
        hover_data={
            dju_type: True,
            "thermosensibilite_totale_kwh_dju": True
        },
        title=f"Relation entre la thermosensibilité et les {dju_type}",
        labels={
            dju_type: f"{dju_type}",
            "thermosensibilite_totale_kwh_dju": "Thermosensibilité totale (kWh/DJU)"
        }
    )
    st.plotly_chart(fig)

    # 3.8 Carte 3D: Consommation d'énergie par région 
    # (filtrage par année, filière et secteur)

    st.header("Carte 3D de la consommation par région")

    # Filtrer le DataFrame en fonction des selections de la sidebar
    filtered_df = df[(df["annee"] == annee_selected) & (df["filiere"] == filiere_selected) & (df["code_grand_secteur"] == secteur_selected)]

    # Calculer la consommation par habitant pour chaque ligne
    filtered_df["conso_par_habitant"] = filtered_df["conso_totale"] / filtered_df["nombre_d_habitants"]

    # Grouper les données pour la carte 3D 
    geo_df = filtered_df.groupby(["code", "nom_region", "longitude", "latitude"])[["conso_totale", "conso_par_habitant"]].sum().reset_index()

    # Pydeck: configuration de la carte 3D
    view_state = pdk.ViewState(latitude=46.2276, longitude=2.2137, zoom=5, pitch=45)
    layer = pdk.Layer(
        "ColumnLayer",
        data=geo_df,
        get_position=["longitude", "latitude"],
        get_elevation="conso_totale",
        elevation_scale=0.01,
        radius=10000, # Rayon des colonnes ajusté
        get_fill_color=[255, 0, 0],
        pickable=True,
        auto_highlight=True
    )

    # Infobulles dynamiques (correction)
    for i in range(len(geo_df)):
        geo_df["conso_par_habitant"][i] = f'{geo_df["conso_par_habitant"][i]:.2f}' 

    tooltip = {
        "html": "<b>Région:</b> {nom_region} <br/>"
                "<b>Consommation totale:</b> {conso_totale} MWh <br/>"
                "<b>Consommation par habitant:</b> {conso_par_habitant} MWh",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    # Afficher la carte 3D
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))