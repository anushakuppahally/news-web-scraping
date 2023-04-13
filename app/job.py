from bs4 import BeautifulSoup
from pynytimes import NYTAPI
import requests
import time
import datetime
import sys

import os
from pathlib import Path  
from dotenv import load_dotenv

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

import spacy
import eng_spacysentiment

import base64
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition, ContentId

load_dotenv()

#securing environment variables
API_KEY = os.getenv("API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL_ADDRESS = os.getenv("SENDER_ADDRESS")
SENDEE_EMAIL_ADDRESS = os.getenv("SENDEE_ADDRESS")

nlp = eng_spacysentiment.load() #loading sentiment analysis model

nyt = NYTAPI(API_KEY, parse_dates=True)
headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}

def test_html():
    '''
    Creates file with HTML output of a sample article
    '''
    link = "https://www.nytimes.com/2023/01/14/business/media/tv-historical-dramas-fictional.html"
    response=requests.get(link, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    file = open("html.txt", "w")
    soup_html = repr(soup.prettify())
    file.write(soup_html)
    file.close

def search_articles(topic, num):
    '''
    Returns links of articles based on query and dates from user input 
    List of parameters: https://pynytimes.michadenheijer.com/search/article-search
    Two rate limits per API: 500 requests per day and 5 requests per minute
    '''
    article_urls = []
    articles = nyt.article_search(
        query = topic, 
        results = num, #results are in multiples of 10
        dates = {
        "begin": datetime.datetime(2020, 1, 16), #dates of first impeachment trial 
        "end": datetime.datetime(2020, 12, 31)
        }, 
        options = {
        "sort": "newest" 
        }
    ) 

    for article in articles:
        article_urls.append(article['web_url'])
    return article_urls
    

def scrape_articles(article_urls):
    '''
    Scrapes each URL and returns full text of article 
    '''
    df = pd.DataFrame()
    text = []
    pos_sentiment = []
    print("EXECUTING QUERY")
    for link in article_urls:
        response=requests.get(link, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        section = soup.find("section", attrs={"name": "articleBody"}) #finding full article text
        text.append(section.text)
        sentiment = nlp(section.text).cats['positive'] #finding positive sentiment 
        pos_sentiment.append(sentiment)

    df['url'] = article_urls
    df['text'] = text
    df['pos_sentiment'] = pos_sentiment
    filepath = Path('./sample_data.csv')  
    filepath.parent.mkdir(parents=True, exist_ok=True)  
    df.to_csv(filepath)  
    print("-------------")
    print("CSV CREATED")

def email_report():
    """
    Creates an email report with summary statistics and a word cloud
    """
    script_dir = os.path.dirname(__file__)
    reports_dir = os.path.join(script_dir,"..", 'reports/ ')
    
    #create word cloud
    df = pd.read_csv('sample_data.csv')
    
    wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(str(df['text']))
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    cloud_file_name = "wordcloud.png"
    plt.savefig(reports_dir + cloud_file_name)

    #email
    subject="[Email Report]: Sentiment Analysis"
        
    html=f"<h2>Analysis of [results] NYT Articles about [query]</h3>"

    html+=f"<h3>World Cloud</h3>"
        
    html+=f"<h4>See the attached image for a word cloud</h4>"

    html+=f"<h3>Summary Statistics</h3>"

    html+=f"<h4>Here are the summary statistics of the query:</h4>"

    min_sentiment = min(df['pos_sentiment'])
    html+="<p>The minimum positive sentiment is {min_sentiment}.</p>"

    average_sentiment = np.mean(df['pos_sentiment'])
    html+="<p>The average positive sentiment is {average_sentiment}.</p>"

    median_sentiment = np.median(df['pos_sentiment'])
    html+="<p>The median positive sentiment is {median_sentiment}.</p>"

    max_sentiment = max(df['pos_sentiment'])
    html+="<p>The maximum positive sentiment is {max_sentiment}.</p>"

    sd_sentiment = np.std(df['pos_sentiment'])
    html+="<p>The standard deviation of positive sentiment is {sd_sentiment}.</p>"
    

    client = SendGridAPIClient(SENDGRID_API_KEY) 
    message = Mail(from_email=SENDER_EMAIL_ADDRESS, to_emails=SENDEE_EMAIL_ADDRESS, subject=subject, html_content=html)

    #attaching word cloud
    with open(reports_dir + cloud_file_name, 'rb') as f:
        data = f.read()
        f.close()
    encoded_img1 = base64.b64encode(data).decode()
        
    message.attachment = Attachment(
    file_content = FileContent(encoded_img1),
    file_type = FileType('image/png'), 
    file_name = FileName('wordcloud.png'), 
    disposition = Disposition('inline'),
    content_id = ContentId('Attachment 1')
    )

    response = client.send(message)
    print(response.status_code) #202 means success

def main():
    query = input("Enter a query: ")
    results = int(input("How many articles do you want to query (multiples of 10)?: "))
    list_of_articles = search_articles(query, results)
    scrape_articles(list_of_articles)
    #email_report()
    
if __name__ == '__main__':
    main()