# News Web Scraping

## Installation 

Create a copy of this and clone/download to your local computer. Then, navigate there from the command-line. 

```sh
cd ~/Desktop/news-web-scraping/
```

Use venv to create and activate a new virtual environment, perhaps called "env":

```sh
python3 -m venv env
source env/bin/activate
```

Then, within an active virtual environment, install package dependencies:

```sh
python3 -m pip install -r requirements.txt
```

## Configuration

Sign up for a NYT developer's account and create a new app. Locate the API key for your app. Also create a SendGrid account, configure your account's email address (i.e. SENDER_ADDRESS), and obtain an API key (i.e. SENDGRID_API_KEY). Create a new file called .env and paste the following values inside, using your own credentials: 

`API_KEY="____"`
`SENDER_ADDRESS="_______________"`
`SENDGRID_API_KEY="_______________"`

## Usage


```sh
python3 -m app.job
```