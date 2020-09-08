#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import plotly.offline as py
import plotly.graph_objs as go
from .models import Tweet
from django.utils.translation import gettext_lazy as _


def df_all_tweets():
    dates = []
    iterator = Tweet.objects.all()
    for i in iterator:
        dates.append(i.date)
    df = pd.DataFrame(data={
        'date': dates,
        'has_symptom': dates})
    df['date'] = pd.to_datetime(df['date'])
    df = df.groupby(['date']).count().reset_index()
    return df
   

def compute_positive_rate():
    df = pd.DataFrame.from_records(TweetAnnotation.objects.all().                                    values_list('tweet__tweet_id','tweet__date','symptom','uuid','created'),
                                    columns=['tweet_id','date','symptom','uuid','timestamp'])
    df=df[(df['symptom'].notna()) & (df['uuid'].notna())]
    ids_yes = ids_yes.groupby(['tweet_id','date','symptom']).count()
    ids_yes=pd.DataFrame(ids_yes['uuid'] / ids_yes.groupby('tweet_id')['uuid'].transform('sum')).reset_index()
    ids_yes=ids_yes.loc[(ids_yes['symptom']=='yes')&(ids_yes['uuid']>=0.5),'id_str']
    ids_yes=ids_yes.groupby('date').count().reset_index().rename(columns={'uuid':'nb_yes'})
    df=df.groupby('date').count().reset_index().rename(columns={'uuid':'nb_annotations'})
    df=pd.merge(df,ids_yes, on='date',how='outer')
    df['percent_yes']=df['nb_yes']/df['nb_annotations']
    return df
    
def df_from_tweets(only_sympotms=False):
    if only_symptoms == True:
        df_yes=compute_positive_rate()
        df_all=df_all_tweets()
        df=pd.merge(df_all, df_yes, how='outer',on='date')
        df['has_symptom']=df['percent_yes']*df['has_symptom']
    adf=df
    adf = adf.apply(lambda x: x/adf['has_symptom'].sum())
    idx = pd.date_range(adf.index[0], adf.index[-1])
    adf = adf.reindex(idx, fill_value=0)
    print(adf)
    adf['has_symptom_mean_3'] = adf.rolling('7d').mean()['has_symptom']
    adf = adf.reset_index()
    print(adf)
    return adf

def create_graph():
    urgences = pd.read_csv('static/urgences.csv', sep=';')
    urgences['date_de_passage'] = pd.to_datetime(urgences['date_de_passage'])
    all_tweets_df = df_from_tweets()
    symptom_tweets_df = df_from_tweets(only_symptoms=True)
    div = plot_symptoms_urgences_with_ma(urgences, all_tweets_df, symptom_tweets_df)
    return div


def plot_symptoms_urgences_with_ma(urgences, all_tweets, symptom_tweets_df):
    traces = []
    traces.append(go.Scatter(
        x=all_tweets['index'],
        y=all_tweets['has_symptom_mean_3'].values,
        mode='lines',
        line=dict(color='orange'),
        name='Tweets symptoms unfiltered (avg 7d)',
        yaxis="y1"))
    traces.append(go.Scatter(
        x=symptom_tweets_df['index'],
        y=symptom_tweets_df['has_symptom_mean_3'].values,
        mode='lines',
        line=dict(color='blue'),
        name='Tweets symptoms filtered (avg 7d)',
        yaxis="y1"))
    traces.append(go.Scatter(
        x=urgences.date_de_passage,
        y=urgences['nbre_pass_corona' + '_mean_3'],
        mode='lines',
        name='Passages to emergencies (avg 3d)',
        line=dict(color='black'),
        yaxis="y2"))
    layout = go.Layout(
        title="Evolution of mentions of symptoms and emergencies related to COVID in Ile-de-France ",
        legend={"x": 1.1, "y": 1},
        yaxis=dict(title='Fraction of tweets with symptoms'),
        yaxis2=dict(
            title='Number of emergencies related to COVID',
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
        x='2020-04-30',
        y=0.95,
        yref="paper",
        text="Lockdown (France)", showarrow=False)])
    div = py.plot(fig, auto_open=False, output_type='div')
    return div

