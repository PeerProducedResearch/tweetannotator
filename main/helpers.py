import pandas as pd
import plotly.offline as py
import plotly.graph_objs as go
from .models import Tweet
from django.utils.translation import gettext_lazy as _


def df_from_tweets(only_symptoms=False):
    dates = []
    if only_symptoms == True:
        iterator = Tweet.objects.exclude(tweetannotation__symptom='no')
    else:
        iterator = Tweet.objects.all()
    for i in iterator:
        dates.append(i.date)
    df = pd.DataFrame(data={
        'date': dates,
        'has_symptom': dates})
    df['date'] = pd.to_datetime(df['date'])
    adf = df.groupby(['date']).count()
    adf['has_symptom_mean_3'] = adf.rolling('3d').mean()['has_symptom']
    adf = adf.reset_index()
    return adf


def create_graph():
    tweets_symptoms = pd.read_csv('static/tweets_mention_symptoms.csv', sep=';')
    urgences = pd.read_csv('static/urgences.csv', sep=';')
    tweets_symptoms['day'] = pd.to_datetime(tweets_symptoms['day'])
    urgences['date_de_passage'] = pd.to_datetime(urgences['date_de_passage'])
    all_tweets_df = df_from_tweets()
    symptom_tweets_df = df_from_tweets(only_symptoms=True)
    div = plot_symptoms_urgences_with_ma(tweets_symptoms, urgences, all_tweets_df, symptom_tweets_df)
    return div


def plot_symptoms_urgences_with_ma(tweets_symptoms, urgences, all_tweets, symptom_tweets_df):
    traces = []
    traces.append(go.Scatter(
        x=all_tweets['date'],
        y=all_tweets['has_symptom'].values,
        mode='lines',
        name=_('Tweets symptoms unfiltered'),
        opacity=0.3,
        line=dict(color='orange'),
        yaxis="y1"))
    traces.append(go.Scatter(
        x=all_tweets['date'],
        y=all_tweets['has_symptom_mean_3'].values,
        mode='lines',
        line=dict(color='orange'),
        name=_('Tweets symptoms unfiltered (avg 3d)'),
        yaxis="y1"))
    traces.append(go.Scatter(
        x=symptom_tweets_df['date'],
        y=symptom_tweets_df['has_symptom'].values,
        mode='lines',
        name=_('Tweets symptoms filtered'),
        opacity=0.3,
        line=dict(color='blue'),
        yaxis="y1"))
    traces.append(go.Scatter(
        x=symptom_tweets_df['date'],
        y=symptom_tweets_df['has_symptom_mean_3'].values,
        mode='lines',
        line=dict(color='blue'),
        name=_('Tweets symptoms filtered (avg 3d)'),
        yaxis="y1"))
    traces.append(go.Scatter(
        x=urgences.date_de_passage,
        y=urgences['nbre_pass_corona'],
        mode='lines',
        name=_('Passages to emergencies'),
        opacity=0.3,
        line=dict(color='black'),
        yaxis="y2"))
    traces.append(go.Scatter(
        x=urgences.date_de_passage,
        y=urgences['nbre_pass_corona' + '_mean_3'],
        mode='lines',
        name=_('Passages to emergencies (avg 3d)'),
        line=dict(color='black'),
        yaxis="y2"))
    layout = go.Layout(
        title=_("Evolution of mentions of symptoms and emergencies related to COVID in Ile-de-France "),
        legend={"x": 1.1, "y": 1},
        yaxis=dict(title=_('Number of tweets')),
        yaxis2=dict(
            title=_('Number of emergencies related to COVID'),
            overlaying='y',
            side='right'))

    fig = go.Figure(traces, layout)
    fig.add_shape(dict(type="rect",
                       yref='paper',
                       x0='2020-03-17',
                       y0=0,
                       x1='2020-05-11',
                       y1=1,
                       fillcolor="LightSalmon",
                       opacity=0.2,
                       layer='below',
                       line_width=0))

    fig.update_layout(annotations=[dict(
        x='2020-04-15',
        y=0.95,
        yref="paper",
        text=_("Lockdown (France)"), showarrow=False)])
    div = py.plot(fig, auto_open=False, output_type='div')
    return div
