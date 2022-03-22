import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
#import nltk
#nltk.download('stopwords')
from wordcloud import WordCloud, STOPWORDS
from bs4 import BeautifulSoup as bs
import requests
from streamlit_lottie import st_lottie
import re
from time import sleep
#import plotly.express as px
#******************************************************************************************************************
                                            #STREAMLIT SECTION
#********************************************************************************************************************
#Streamlit page settings
st.set_page_config(page_title="At-glance", page_icon=":eyeglasses:", initial_sidebar_state='expanded')

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Import logo animation from lotties
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_chart = load_lottieurl('https://assets9.lottiefiles.com/packages/lf20_i2eyukor.json')
st_lottie(lottie_chart, speed=1, height=100, key="initial")

#Title column alignment manipulation
row0_spacer1, row0_1, row0_spacer2, row0_2  = st.columns((1.8,2.8,.2,5.3))
row0_1.title('GLANCE-IT ')

row0_1.markdown(':sunglasses:***_Your movie review at a glance_***:sunglasses:')
#with row0_1:
    #st.write('___')

row1_spacer1, row1_1, row1_spacer2 = st.columns((.1,7.3,.1))

with row1_1:

    st.write("""**Hello! Welcome to Glance-it!** This app scrapes a few reviews of your favorite movies from IMDb
              (but does not store the data) and converts it to easy to view graphs. The app lets you know (based on other user's reviews)
              if a movie is worth your time and money. Also, the app shows the percentage of users that find the movie either 
              **interesting**, **cool**, **not cool** or **boring**. Why don't you dig in and see for yourself? Have fun!  """)
    st.markdown("**PS:** the reviews are based on individual's view about the movie and their opinions may not be final ")
    st.write("___")

#**************************************************************************
row2_spacer1, row2_1, row2_spacer2 = st.columns((3,7.3,3))

with row2_1:
    search_header = st.subheader("Search movie title")
    title = st.text_input("Enter movie title", value= "red sparrow",max_chars=30, help="Clear the default title...Enter movie title and press ENTER")



st.write("**Reviews for the movie :  **", title)
st.write("___")


#SCRAPING AND DATA PROCESSING
#*************************************************************************

# This function loads the key in our text file as list
def get_keys ():
    '''Load pagination keys from a text file '''
    f = open("IMDB_key_a.txt", "r")
    key = f.read()
    f.close()
    items = key.split(',')
    return items
#Extract keys
keys=[i for i in get_keys()]
key = keys[0:5]

#Grab user movie title to search for
def join_string(string):
    '''Returns title entered by user'''
    user_query =string.split(' ')
    user_string=' '.join(user_query)
    return user_string

#Search user_query using IMDB search tool and
#Get the movie link to extract movie code
def get_movie_code():
    '''This method return movie code of movie title entered by user'''
    search_url = requests.get('https://www.imdb.com/find?q='+join_string(title))
    soup_search = bs(search_url.content)
    #soup_search.status_code == 200
        
    for item in soup_search:
        link= list(soup_search.find('td', class_="result_text").a['href'][7:-1])
        link_w = ''.join(link)
            
        if link_w.startswith('tt', 0, 2):
            return str(link_w)
        else:
            return 'Movie not found. Try another movie title \nEnter correct movie Title'
    

#Getting reviews from landing page
@st.cache
def get_review ():
    title_ = []
    text_ = []
    ratings =  []
    
    url = 'https://www.imdb.com/title/'+get_movie_code()+'/reviews'
    review_url = requests.get(url)
    #if (review_url.status_code == 200):
        
    soup_review = bs(review_url.content)

    content = soup_review.find('div', class_="lister-list")

    for titles in content.find_all('a', class_='title'):
        title = titles.get_text()
        title_.append(title)

    for texts  in content.find_all('div', class_="text show-more__control"):
        text = texts.get_text(separator=' ', strip=True)
        text_.append(text)

    for rating  in content.find_all('span',class_="rating-other-user-rating" ):
        rating_ = rating.get_text(separator=' ',strip=True)
        ratings.append(rating_[0:2])
    
    data = {'Title': title_, 'Review': text_, 'Ratings': ratings}
    return data

df_1 = pd.concat([pd.Series(v, name=k) for k, v in get_review().items()], axis=1)

#Getting paginated reviews
@st.cache(suppress_st_warning = True)
def get_review_paginated ():
    title_ = []
    text_ = []
    ratings =  []
    
    
    for x in key:
            url2 = 'https://www.imdb.com/title/'+get_movie_code()+'/reviews/_ajax?ref_=undefined&paginationKey='+x
            
            review_url2 = requests.get(url2)
            sleep(0.2)
            #if (review_url2.status_code==200):
            soup_review2 = bs(review_url2.content)

            content2 = soup_review2.find('div', class_="lister-list") #review-container

            for titles2 in content2.find_all('a', class_='title'):
                title2 = titles2.get_text()
                title_.append(title2)

            for texts2  in content2.find_all('div', class_="text show-more__control"):
                text2 = texts2.get_text(separator=' ', strip=True)
                text_.append(text2)

            for rating2  in content2.find_all('span',class_="rating-other-user-rating" ):
                rating_2 = rating2.get_text(separator=' ',strip=True)
                ratings.append(rating_2[0:2])
                
    data = {'Title': title_, 'Review': text_, 'Ratings': ratings}
    return data

df_2 = pd.concat([pd.Series(v, name=k) for k, v in get_review_paginated().items()], axis=1)

#Merge data from landing page review and paginated reviews
main_df = pd.concat([df_1, df_2], ignore_index = True)
#Remove duplicates and drop empty rows
main_df = main_df.dropna().drop_duplicates()
#Reset index
main_df=main_df.reset_index(drop=True)
#remove next line character
main_df.replace(r'\n',' ', regex=True, inplace=True) 

# LABEL RATING AS INTERESTING (8-10)...COOL (5-7)...NOT COOL (3-4)...OR BORING (1-2)
def recommender (word):
   
    if int(word) >= 8 :
        return "Interesting"  
    elif int(word) >= 5 and int(word) < 8 :
        return "Cool"
    elif int(word) >= 3 and int(word) < 5 :
        return "Not Cool"   
    else :
        return "Boring"

main_df ['Recommendation'] = main_df['Ratings'].apply(lambda x: recommender(x))

# ADD SIDEBAR
add_selectbox = st.sidebar.selectbox(
    "What would you like to see?",
    ("Recommendation", "Ratings", "Wordcloud","Table")
)

#Progress bar
my_bar = st.progress(0)

for percent_complete in range(1,100,5):
     sleep(0.1)
     my_bar.progress(percent_complete + 1)
my_bar.empty()

#Show bar chart of movie recommendation
if add_selectbox == "Recommendation":
    st.sidebar.write("""Recommendation shows you what viewers think about the movie. Viewers rate it from INTERESTING to BORING. """)
    st.write("**_Recommendation base on review_**")
        ## BAR CHART for Recommendation
    labels = main_df['Recommendation'].unique()
    colors = sns.color_palette("Set2") #choosing color

    fig, ax = plt.subplots(figsize=(10,4)) 
    wedges = ax.bar(x=main_df['Recommendation'].unique(), height=main_df["Recommendation"].value_counts(), width=0.8, color= colors)

    plt.show()
    st.pyplot(fig)
    st.write("___")

    #Show Movie average rating card
    st.write("**_Average Movie Rating_**")
    fig3, ax3 = plt.subplots(figsize=(2.6,1))
    wedges = ax3.text(0.6, 0.7, str(main_df.Ratings.astype(int).mean().round(2)) + "/10", size=40, rotation=360,
             ha="center", va="center",
            bbox=dict(boxstyle="round",
                       ec=(.5, 0.5, 0.5),
                      fc=(.2, 0.8, 0.8),
                       )
             )

    plt.axis('off')
    plt.show()
    st.pyplot(fig3)
    st.write("___")

#Show pie chart of ratings
if add_selectbox == "Ratings":
    st.sidebar.write("""This is a rating distribution showing the percentage of viewers who rated the movie (this is limited to the data collected). """)
    st.write("**_Rating Distribution_**")
    labels = main_df['Ratings'].unique()

    fig1, ax1 = plt.subplots(figsize=(4,4))

    colors = sns.color_palette("bright") #choosing color

    wedges, texts, autotexts = ax1.pie(main_df.Ratings.value_counts(), autopct='%1.1f%%',wedgeprops = { 'linewidth' : 1, 'edgecolor' : 'white' },
                shadow=False, startangle=180, pctdistance=0.7, radius=1.0, colors=colors)

    ax1.legend(wedges, labels,
            title="Ratings",
            loc="center left",
            bbox_to_anchor=(1, -0.5, 1, 2.0))

    plt.setp(autotexts, size=10, weight="bold")


    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        #plt.title("Ratings Distribution")
    plt.show()
    st.pyplot(fig1)

#Show Wordcloud of popular words or phrase mentioned in review title
if add_selectbox == "Wordcloud":
    st.sidebar.write("""Wordcloud gives you an idea of the frequently mentioned word or phrase pertaining to the movie. """)
    st.write("**_Frequent words mentioned in review title_**")
    text = main_df['Title'].values

    stopwords = set(STOPWORDS)
    stopwords.add('film thus')
    stopwords.add("movie")

    fig2, ax2 = plt.subplots(figsize=(4,4))
    ax2 = WordCloud(width=400, height=200, max_words=25, stopwords=stopwords, random_state=20).generate(str(text).lower())
    
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.imshow(ax2)
    #plt.title('Popular words in Title')
    st.pyplot(fig2)

#Show Table of Top or Last review
if add_selectbox == "Table":
    st.sidebar.write("""Table gives you the first ten reviews made by viewers """)
    top_last = st.radio(
     "Top reviews or last reviews",
     ('Top', 'Last'))
    
    num_val =st.sidebar.slider('Number of reviews to see', 0, 10, 5)
   

    if top_last == 'Top':
      df = main_df.head(num_val)
      
    if top_last == 'Last':
      df = main_df.tail(num_val)
    
    st.dataframe(df)

