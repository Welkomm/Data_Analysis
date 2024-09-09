import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as nb
import matplotlib.pyplot as plt
import seaborn as sns
# test 

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

st.title('Uber Data extract :')
#st.dataframe

st.dataframe(df.head())

st.subheader('Frequency by Day of the Month')
fig, ax = plt.subplots()
df['day'].plot.hist(bins=30, rwidth=0.8, range=(0.5, 30.5), ax=ax)
ax.set_xlabel('Days of the month')
ax.set_title('Frequency by DoM - Uber - April 2014')
st.pyplot(fig)

# Frequency by hour of the day
st.subheader('Frequency by Hour of the Day')
fig, ax = plt.subplots()
df['hour'].plot.hist(bins=24, range=(-0.5, 23.5), ax=ax)
ax.set_xlabel('Hour of the day')
ax.set_title('Frequency by Hour - Uber - April 2014')
st.pyplot(fig)

# Frequency by day of the week
st.subheader('Frequency by Day of the Week')
fig, ax = plt.subplots()
df['weekday'].value_counts().sort_index().plot(kind='bar', ax=ax)
ax.set_xlabel('Day of the week')
ax.set_ylabel('Frequency')
ax.set_title('Frequency by Day of the Week - Uber - April 2014')
st.pyplot(fig)

# Line plot for frequency by day of the month
def count_rows(rows):
  return len(rows) 
by_date = df.groupby('day').apply(count_rows)

st.subheader('Line Plot - Frequency by Day of the Month')
fig, ax = plt.subplots()
ax.plot(by_date)
ax.set_xlabel('Days of the month')
ax.set_ylabel('Frequency')
ax.set_title('Line plot - Uber - April 2014')
st.pyplot(fig)


# Frequency by day of the month - More readable bar plot
st.subheader('Frequency by Day of the Month - More Readable Bar Plot')
fig, ax = plt.subplots(figsize=(25, 15))
ax.bar(range(1, 31), by_date.sort_values())
ax.set_xticks(range(1, 31))
ax.set_xticklabels(by_date.sort_values().index)
ax.set_xlabel('Date of the month', fontsize=20)
ax.set_ylabel('Frequency', fontsize=20)
ax.set_title('Frequency by DoM - Uber - April 2014', fontsize=20)
st.pyplot(fig)

# Frequency by hour of the day
st.subheader('Frequency by Hour of the Day')
fig, ax = plt.subplots()
ax.hist(df['hour'], bins=24, range=(-0.5, 23.5))
ax.set_xlabel('Hour of the day')
ax.set_ylabel('Frequency')
ax.set_title('Frequency by Hour - Uber - April 2014')
st.pyplot(fig)

df2 = df.groupby(['weekday', 'hour']).apply(count_rows).unstack()

# Heatmap by hour and weekday
st.subheader('Heatmap by Hour and Weekday')
fig, ax = plt.subplots(figsize=(12, 8))
heatmap = sns.heatmap(df2, linewidths=.5, ax=ax)
ax.set_title('Heatmap by Hour and Weekdays - Uber - April 2014', fontsize=15)
heatmap.set_yticklabels(('Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'), rotation='horizontal')
st.pyplot(fig)