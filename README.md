# TweetAnnotator

A simple _Django_ website that allows people to annotate which crawled tweets that supposedly are about current COVID-19 symptoms are actually describing them. The whole annotation pipeline is supposed to work out in the open: Participants can

- Download all the annotations being done by the crowd
- Get live updates on how the annotations change the predictions and correlations to COVID-19 symptom reports
- [Access the original notebooks for the analyses](https://github.com/InteractionDataLab/covid-twitter-analysis/) and [run them directly in MyBinder](https://mybinder.org/v2/gh/InteractionDataLab/covid-twitter-analysis/master?filepath=notebooks%2Fcovid-analyses.ipynb).

## Setup

Run the following (assuming you already have pipenv and heroku installed)

```
pipenv install
pipenv shell
heroku local:run python manage.py migrate
heroku local:run python manage.py import_tweets
heroku local
```

Your website should be up at `127.0.0.1:5000`.

## i18n

The site is already setup to work multi-lingual. If you change any of the template texts you can get create updated translation files with

```
heroku local:run python manage.py makemessages
```

If you use Transifex for doing the translation do

```
tx push -s
```

to push the latest source language (english). Once the translations are done you can get them and compile for usage via:

```
tx pull
heroku local:run python manage.py compilemessages
```
