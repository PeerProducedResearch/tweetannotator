from django.shortcuts import render, redirect
import uuid
import random
from .models import Tweet, TweetAnnotation
from django.http import HttpResponse
# Create your views here.
from .helpers import create_graph
import pandas as pd
import datetime


def get_random_tweet(uuid):
    if TweetAnnotation.objects.filter(uuid=uuid).count() < 3:
        tweets = Tweet.objects.exclude(
            tweetannotation=None
        ).exclude(tweetannotation__uuid=uuid)
    else:
        # tweets = Tweet.objects.exclude(tweetannotation__uuid=uuid) ### commented out to get current tweets
        Tweet.objects.exclude(tweetannotation__uuid=uuid).filter(date__gte=datetime.date(2020,7,1))
    tl = len(tweets)
    if tl == 0:
        tweets = Tweet.objects.exclude(tweetannotation__uuid=uuid)
        tl = len(tweets)
    tweet_pos = random.randint(0,tl-1)
    tweet = tweets[tweet_pos]
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
