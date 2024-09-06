import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as nb

# uber data transformation

df=pd.read_csv('uber.csv', delimiter=",") 
df['Date/Time'] = pd.to_datetime(df['Date/Time'], format='%m/%d/%Y %H:%M:%S')

def get_dom(dt):
    return dt.day

df["day"]=df["Date/Time"].map(get_dom)

def get_weekday(dt):
    return dt.weekday()

df["weekday"]=df["Date/Time"].map(get_weekday) 

def get_hour(dt):
    return dt.hour 

df["hour"]=df["Date/Time"].map(get_hour)

# sidebar
    ## logo
from PIL import Image

uber_logo = Image.open('Uber.png')
sidebar = st.image(uber_logo)

st.sidebar.title(
    "BIENVENU Samuel"
    )

my_pic = Image.open('CV.jpg')
with st.sidebar:
    st.image(my_pic, caption= "Engineering Student")

with st.sidebar:
    st.markdown("[![Foo](https://logosmarcas.net/wp-content/uploads/2020/04/Linkedin-Logo-650x366.png)](https://fr.linkedin.com/)")
    st.write("xxxxxx@protonmail.com")

st.title('Displaying data elements with code snippets :')
#st.dataframe
code_1 = st.dataframe(df.style.highlight_max(axis=0))

st.code(code_1, language='python')