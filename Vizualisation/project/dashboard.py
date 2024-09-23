import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
from PIL import Image

# --- FONCTIONS ---

def count_rows(rows):
    return len(rows)

# --- CHARGEMENT ET TRANSFORMATION DES DONNÉES ---

df_uber = pd.read_csv('uber.csv', delimiter=",")
df_uber['Date/Time'] = pd.to_datetime(df_uber['Date/Time'], format='%m/%d/%Y %H:%M:%S')
df_uber["day"] = df_uber["Date/Time"].map(lambda dt: dt.day)
df_uber["weekday"] = df_uber["Date/Time"].map(lambda dt: dt.weekday())
df_uber["hour"] = df_uber["Date/Time"].map(lambda dt: dt.hour)

df_tips = pd.read_csv("tips.csv")
df_tips["day"] = df_tips["day"].astype("category")
df_tips["time"] = df_tips["time"].astype("category")

# --- IMAGES ---

uber_logo = Image.open('Uber.png')
my_pic = Image.open('CV.jpg')

# --- SIDEBAR ---

st.sidebar.image(uber_logo)
st.sidebar.title("BIENVENU Samuel")
st.sidebar.image(my_pic, caption="Engineering Student")
st.sidebar.markdown("![alt text](https://logosmarcas.net/wp-content/uploads/2020/04/Linkedin-Logo-650x366.png)")
st.sidebar.write("xxxxxx@protonmail.com")

# --- NAVIGATION ---

onglet_presentation, onglet_uber, onglet_pourboires = st.tabs(["Présentation", "Analyse Uber", "Analyse des Pourboires"])

# --- PAGE DE PRÉSENTATION ---

with onglet_presentation:
    st.title("Dashboard d'Analyse de Données")
    st.header("Bienvenue!")
    st.write("""
    Ce dashboard interactif explore deux jeux de données:
    - Données Uber: Analyse des courses Uber en avril 2014.
    - Données de Pourboires: Analyse des facteurs influençant les pourboires dans un restaurant.

    Naviguez entre les pages pour découvrir les visualisations et analyses!
    """)

# --- PAGE D'ANALYSE UBER ---

with onglet_uber:
    st.title("Analyse des Données Uber")

    # --- Filtres dans la sidebar ---
    with st.sidebar:
        st.header("Filtres Uber")
        jour_filtre = st.slider("Jour du mois:", min_value=1, max_value=30, value=(1, 30))
        heure_filtre = st.slider("Heure de la journée:", min_value=0, max_value=23, value=(0, 23))

    # --- Application des filtres ---
    df_uber_filtree = df_uber[
        (df_uber["day"] >= jour_filtre[0]) & (df_uber["day"] <= jour_filtre[1]) & 
        (df_uber["hour"] >= heure_filtre[0]) & (df_uber["hour"] <= heure_filtre[1])
    ]

    # --- Aperçu des données ---
    st.header("Aperçu des Données")
    st.dataframe(df_uber_filtree.head())

    # --- Visualisations ---
    st.header("Visualisations")

    # Fréquence par jour du mois
    st.subheader('Fréquence par Jour du Mois')
    fig, ax = plt.subplots(figsize=(10, 5))
    df_uber_filtree['day'].plot.hist(bins=30, rwidth=0.8, range=(0.5, 30.5), ax=ax)
    ax.set_xlabel('Jour du mois')
    ax.set_title('Fréquence par Jour du Mois - Uber - Avril 2014')
    st.pyplot(fig)

    # Fréquence par heure de la journée
    st.subheader('Fréquence par Heure de la Journée')
    fig, ax = plt.subplots(figsize=(10, 5))
    df_uber_filtree['hour'].plot.hist(bins=24, range=(-0.5, 23.5), ax=ax)
    ax.set_xlabel('Heure de la journée')
    ax.set_title('Fréquence par Heure - Uber - Avril 2014')
    st.pyplot(fig)

    # Fréquence par jour de la semaine
    st.subheader('Fréquence par Jour de la Semaine')
    fig, ax = plt.subplots(figsize=(10, 5))
    df_uber_filtree['weekday'].value_counts().sort_index().plot(kind='bar', ax=ax)
    ax.set_xlabel('Jour de la semaine (0=Lundi)')
    ax.set_ylabel('Fréquence')
    ax.set_title('Fréquence par Jour de la Semaine - Uber - Avril 2014')
    st.pyplot(fig)

    # Heatmap par heure et jour de la semaine
    st.subheader('Heatmap par Heure et Jour de la Semaine')
    df2 = df_uber_filtree.groupby(['weekday', 'hour']).apply(count_rows).unstack()
    fig, ax = plt.subplots(figsize=(12, 8))
    heatmap = sns.heatmap(df2, linewidths=.5, ax=ax)
    ax.set_title('Heatmap par Heure et Jours de la Semaine - Uber - Avril 2014', fontsize=15)
    heatmap.set_yticklabels(('Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'), rotation='horizontal')
    st.pyplot(fig)

    # --- Cartographie des points de dépose ---
    st.header("Cartographie des Points de Dépose")
    map_data = df_uber_filtree[["Lat", "Lon"]].rename(columns={"Lat": "lat", "Lon": "lon"})
    st.map(map_data)

    # --- Carte 3D avec PyDeck ---
    st.subheader("Carte 3D avec PyDeck")
    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=40.7128,  # Latitude de New York
            longitude=-74.0060,  # Longitude de New York
            zoom=10,  # Zoom adapté à New York
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'HexagonLayer',
                map_data,
                get_position='[lon, lat]',
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                map_data,
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=200,
            ),
        ],
    ))

# --- PAGE D'ANALYSE DES POURBOIRES ---

with onglet_pourboires:
    st.title("Analyse des Données de Pourboires")

    # --- Filtres dans la sidebar ---
    with st.sidebar:
        st.header("Filtres Pourboires")
        jour_filtre_tips = st.multiselect("Jour de la semaine:", df_tips["day"].unique(), default=df_tips["day"].unique())
        heure_filtre_tips = st.multiselect("Moment de la journée:", df_tips["time"].unique(), default=df_tips["time"].unique())
        fumeur_filtre = st.selectbox("Fumeur:", ["Tous", "Oui", "Non"], index=0)

    # --- Application des filtres ---
    df_tips_filtree = df_tips[
        (df_tips["day"].isin(jour_filtre_tips)) &
        (df_tips["time"].isin(heure_filtre_tips))
    ]
    if fumeur_filtre != "Tous":
        df_tips_filtree = df_tips_filtree[df_tips_filtree["smoker"] == (fumeur_filtre == "Oui")]

    # --- Aperçu des données ---
    st.header("Aperçu des Données")
    st.dataframe(df_tips_filtree.head())

    # --- Analyses et visualisations ---
    st.header("Analyses et Visualisations")

    # Boxplots pour les pourboires en fonction du jour et du sexe
    st.subheader("Distribution des pourboires en fonction du jour et du sexe")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x="day", y="tip", hue="sex", data=df_tips_filtree, ax=ax)
    plt.xlabel("Jour de la semaine")
    plt.ylabel("Pourboire ($)")
    st.pyplot(fig)

    # Histogramme de la distribution des pourboires
    st.subheader("Distribution des pourboires")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df_tips_filtree["tip"], kde=True, ax=ax)
    plt.xlabel("Pourboire ($)")
    plt.ylabel("Fréquence")
    st.pyplot(fig)

    # Diagramme en violon pour les pourboires en fonction du moment de la journée et du fait de fumer
    st.subheader("Distribution des pourboires en fonction du moment de la journée et du fait de fumer")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.violinplot(x="time", y="tip", hue="smoker", data=df_tips_filtree, split=True, ax=ax)
    plt.xlabel("Moment de la journée")
    plt.ylabel("Pourboire ($)")
    st.pyplot(fig)

    # Nuage de points pour la relation entre le montant total de la facture et le pourboire
    st.subheader("Relation entre le montant total de la facture et le pourboire")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x="total_bill", y="tip", hue="size", data=df_tips_filtree, ax=ax)
    plt.xlabel("Montant total de la facture ($)")
    plt.ylabel("Pourboire ($)")
    st.pyplot(fig)