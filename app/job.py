from bs4 import BeautifulSoup
from pynytimes import NYTAPI
import requests
import time
import sys
import os
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path  

load_dotenv()

api_key = os.getenv("API_KEY")

nyt = NYTAPI(api_key, parse_dates=True)
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

def search_articles():
    '''
    Returns links of articles based on query 
    '''
    article_urls = []
    articles = nyt.article_search(query = "Impeachment", results = 30) #results are in multiples of 10
    for article in articles:
        article_urls.append(article['web_url'])
    return article_urls

def scrape_articles(article_urls):
    '''
    Scrapes each URL and returns full text of article 
    '''
    df = pd.DataFrame()
    text = []
    for link in article_urls:
        response=requests.get(link, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        section = soup.find("section", attrs={"name": "articleBody"})
        text.append(section.text)
    df['url'] = article_urls
    df['text'] = text
    filepath = Path('./sample_data.csv')  
    filepath.parent.mkdir(parents=True, exist_ok=True)  
    df.to_csv(filepath)  


def main():
    list_of_articles = search_articles()
    scrape_articles(list_of_articles)
    
if __name__ == '__main__':
    main()