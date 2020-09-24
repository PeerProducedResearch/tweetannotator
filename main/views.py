from django.shortcuts import render, redirect
import uuid
import random
from .models import Tweet, TweetAnnotation
from django.http import HttpResponse
# Create your views here.
from .helpers import create_graph
import pandas as pd
import datetime
from django.db.models import Count


def get_random_tweet(uuid):
    if TweetAnnotation.objects.filter(uuid=uuid).count() < 3:
        tweets = list(Tweet.objects.exclude(
            tweetannotation=None
        ).exclude(tweetannotation__uuid=uuid).values_list('tweet_id'))
    else:
        # tweets = Tweet.objects.exclude(tweetannotation__uuid=uuid) ### commented out to get current tweets
        # tweets = Tweet.objects.exclude(tweetannotation__uuid=uuid).filter(date__gte=datetime.date(2020,7,1))

        # get all IDs of tweets with little ratings
        tweets_little_rated = list(Tweet.objects.all().annotate(
            num_annotations=Count('tweetannotation')).filter(num_annotations__lt=2).values_list('tweet_id',flat=True))

        # get all IDs of tweets with consensus
        df = pd.DataFrame.from_records(TweetAnnotation.objects.all().values_list('tweet__tweet_id','tweet__date','symptom','uuid','created'),
                                        columns=['tweet_id','date','symptom','uuid','timestamp'])
        df = df[(df['symptom'].notna()) & (df['uuid'].notna())]
        df_counted = df.groupby(['tweet_id']).count()
        potential_ids = list(df_counted.loc[df_counted['date'] > 1].index)

        grouped_annotations = df.groupby(['tweet_id','date','symptom']).count()
        grouped_annotations = pd.DataFrame(grouped_annotations['uuid'] / grouped_annotations.groupby('tweet_id')['uuid'].transform('sum')).reset_index()
        grouped_annotations = grouped_annotations.set_index(keys='tweet_id')
        grouped_annotations = grouped_annotations[grouped_annotations.index.isin(potential_ids)]
        consensus_ids = set(grouped_annotations.loc[grouped_annotations['uuid'] > 0.67].index)

        # remove all consensus tweets from list of all potential tweets
        tweets = list(set(potential_ids) - consensus_ids)
        # add back the tweets that haven't been rated twice yet
        tweets = tweets + tweets_little_rated
    tl = len(tweets)
    if tl == 0:
        tweets = Tweet.objects.exclude(tweetannotation__uuid=uuid).values_list('tweet_id')
        tl = len(tweets)
    tweet_pos = random.randint(0,tl-1)
    tweet = tweets[tweet_pos]
    tweet = Tweet.objects.get(tweet_id=tweet)
    return tweet


def index(request):

    if not request.session.get('uuid', ''):
        request.session['uuid'] = str(uuid.uuid4())
    tweet = get_random_tweet(request.session['uuid'])
    tweet.text = tweet.text.strip(";;")
    tweet_annotations = TweetAnnotation.objects.all().order_by('-created')[:5]
    annotation_count = TweetAnnotation.objects.all().count()
    context = {
        'tweet': tweet,
        'tweet_annotations': tweet_annotations,
        'annotation_count': annotation_count}

    return render(request, 'main/index.html', context)


def about(request):
    return render(request, 'main/about.html')


def analysis(request):
    return render(request, 'main/analysis.html')


def annotate(request, tweet_id, answer):
    tweet = Tweet.objects.get(id=tweet_id)
    uuid = request.session.get('uuid', '')
    if uuid and tweet.tweetannotation_set.filter(uuid=uuid).count() == 0:
        ta = TweetAnnotation.objects.create(
            tweet=tweet,
            symptom=answer,
            uuid=uuid)
        ta.save()
    return redirect('/')


def graph(request):
    graph = create_graph()
    return HttpResponse(graph)


def download_annotations(requests):
    data = pd.DataFrame.from_records(TweetAnnotation.objects.all().values_list('tweet__tweet_id','symptom','uuid','created'),columns=['tweet_id','symptom','uuid','timestamp'])
    response = HttpResponse(data.to_csv(sep=';', index=False), content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename=%s" % "annotations.csv"
    return response
