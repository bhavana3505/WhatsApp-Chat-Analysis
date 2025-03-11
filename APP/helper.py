from urlextract import URLExtract
from wordcloud import WordCloud
import string
from collections import Counter
from nltk.corpus import stopwords
nltk.download('stopwords')
import pandas as pd

import re
from collections import Counter
import emoji



def fetchStarts(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user_name']==selected_user]

    num_msg = df.shape[0]

    words = []
    for msg in df['msg']:
        words.extend(msg.split())

    num_words = len(words)

    num_media=df[df['msg']=="<Media omitted>"].shape[0]


    links=[]
    extractor=URLExtract()
    for msg in df['msg']:
        links.extend(extractor.find_urls(msg))

    num_links=len(links)

    start_date = df['date'].min()
    end_date = df['date'].max()

    from dateutil.relativedelta import relativedelta


    # Calculate the difference between the start and end dates using relativedelta
    difference = relativedelta(end_date, start_date)

    # Extract the difference in years, months, and days
    years = difference.years
    months = difference.months
    days = difference.days

    # Format the result as "X years, Y months, Z days"
    num_time = f"{years} Y, {months} M, {days} D"



    return num_msg, num_words,num_media,num_links,num_time


def fetchMostBusyUsers(df):
    X = df['user_name'].value_counts()

    df = round(df['user_name'].value_counts()/df.shape[0]*100,2).reset_index().rename(columns={"user_name":"name","count":"percent"})

    return X,df

def createWordCloud(selected_user,df):

    if selected_user!="Overall":
        df=df[df['user_name']==selected_user]

    temp = df[df['user_name'] != "Group Notification"]
    temp = temp[temp['msg'] != "<Media omitted>"]

    # Define stopwords
    stop_words = stopwords.words('english')

    def removeStopwords(msg):
        y=[]
        for word in msg.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc=WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['msg']=temp['msg'].apply(removeStopwords)
    df_wc=wc.generate(temp['msg'].str.cat(sep=" "))

    return df_wc


def most_common_words(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user_name']==selected_user]

    temp = df[df['user_name'] != "Group Notification"]
    temp = temp[temp['msg'] != "<Media omitted>"]

    # Define stopwords
    stop_words = stopwords.words('english')
    # Define punctuation marks
    punctuation = string.punctuation

    words = []
    for msg in temp['msg']:  # Assuming `temp['msg']` contains the messages
        for word in msg.lower().split():
            # Remove punctuation marks and check if the word is not a stop word
            word = word.strip(punctuation)
            if word and word not in stop_words:
                words.append(word)

    # Get the 20 most common words
    return pd.DataFrame(Counter(words).most_common(20))


def emoji_helper(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user_name']==selected_user]

    def extract_emojis(msg):
        # Find all emojis and exclude emojis in the specified Unicode ranges
        exclude_range = re.compile(r'[\U0001FAE0-\U0001FAFF,\U0001f979]')

        return [c for c in msg if c in emoji.EMOJI_DATA and not exclude_range.search(c)]

    # Example usage
    emojis = []
    for msg in df['msg']:  # Assuming `df['msg']` contains the messages
        emojis.extend(extract_emojis(msg))

    # Counting the emojis
    return pd.DataFrame(Counter(emojis).most_common(20))


def mothly_time_line(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user_name']==selected_user]
    df['month_num'] = df['date'].dt.month
    time_line = df.groupby(['year', 'month_num', "month"]).count()['msg'].reset_index()
    time = []
    for i in range(time_line.shape[0]):
        time.append(time_line['month'][i] + "-" + str(time_line['year'][i]))

    time_line["time"] = time

    return time_line

def week_activity_map(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user_name']==selected_user]

    return df['day_name'].value_counts()

def monthly_activity_map(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user_name']==selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user_name']==selected_user]

    return df.pivot_table(index='day_name', columns='period', values='msg', aggfunc='count').fillna(0)
