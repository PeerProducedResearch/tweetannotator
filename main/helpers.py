import pandas as pd
import plotly.offline as py
import plotly.graph_objs as go


def create_graph():
    tweets_symptoms = pd.read_csv('static/tweets_mention_symptoms.csv', sep=';')
    urgences = pd.read_csv('static/urgences.csv', sep=';')
    tweets_symptoms['day'] = pd.to_datetime(tweets_symptoms['day'])
    urgences['date_de_passage'] = pd.to_datetime(urgences['date_de_passage'])
    div = plot_symptoms_urgences_with_ma(tweets_symptoms, urgences)
    return div


def plot_symptoms_urgences_with_ma(tweets_symptoms, urgences):
    traces = []
    traces.append(go.Scatter(
        x=tweets_symptoms['day'],
        y=tweets_symptoms['has_symptom'].values,
        mode='lines',
        name='Tweets symptoms unfiltered',
        opacity=0.3,
        line=dict(color='red'),
        yaxis="y1"))
    traces.append(go.Scatter(
        x=tweets_symptoms['day'],
        y=tweets_symptoms['has_symptom_mean_3'].values,
        mode='lines',
        line=dict(color='red'),
        name='Tweets symptoms unfiltered (avg 3d)',
        yaxis="y1"))
    traces.append(go.Scatter(
        x=urgences.date_de_passage,
        y=urgences['nbre_pass_corona'],
        mode='lines',
        name='Passages to emergencies',
        opacity=0.3,
        line=dict(color='green'),
        yaxis="y2"))
    traces.append(go.Scatter(
        x=urgences.date_de_passage,
        y=urgences['nbre_pass_corona' + '_mean_3'],
        mode='lines',
        name='Passages to emergencies (avg 3d)',
        line=dict(color='green'),
        yaxis="y2"))
    layout = go.Layout(
        title="Evolution of mentions of symptoms and emergencies related to COVID in Ile-de-France ",
        legend={"x": 1.1, "y": 1},
        yaxis=dict(title='Number of tweets'),
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
        x='2020-04-15',
        y=0.95,
        yref="paper",
        text="Lockdown (France)", showarrow=False)])
    div = py.plot(fig, auto_open=False, output_type='div')
    return div
