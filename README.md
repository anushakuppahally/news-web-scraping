# News Web Scraping

## Installation 

Create a copy of this and clone/download to your local computer. Then, navigate there from the command-line. 

```sh
cd ~/Desktop/news-web-scraping/
```

Use Anaconda to create and activate a new virtual environment, perhaps called "scraping-env":

```sh
conda create -n scraping-env python=3.9
conda activate scraping-env
```

Then, within an active virtual environment, install package dependencies:

```sh
pip install -r requirements.txt
```

## Configuration

Sign up for a NYT developer's account and create a new app. Locate the API key for your app. Create a new file called .env and paste the following values inside, using your own credentials: 

`API_KEY="____"`

## Usage


```sh
python -m app.job

```