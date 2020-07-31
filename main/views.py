from django.shortcuts import render, redirect
import uuid
import random
from .models import Tweet, TweetAnnotation
from django.db.models import Max
from django.http import HttpResponse
# Create your views here.
from .helpers import create_graph


def get_random_tweet(uuid):
    if TweetAnnotation.objects.filter(uuid=uuid).count() < 3:
        tweets = Tweet.objects.exclude(
            tweetannotation=None
        ).exclude(tweetannotation__uuid=uuid)
    else:
        tweets = Tweet.objects.exclude(tweetannotation__uuid=uuid)
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
    context = {'tweet': tweet, 'tweet_annotations': tweet_annotations}

    return render(request, 'main/index.html', context)


def about(request):
    return render(request, 'main/about.html')


def analysis(request):
    return render(request, 'main/analysis.html')


def annotate(request, tweet_id, answer):
    tweet = Tweet.objects.get(id=tweet_id)
    ta = TweetAnnotation.objects.create(
        tweet=tweet,
        symptom=answer,
        uuid=request.session.get('uuid', ''))
    ta.save()
    return redirect('/')


def graph(request):
    graph = create_graph()
    return HttpResponse(graph)


def download_annotations(requests):
    csv = "tweet_id;symptom;uuid;timestamp\n"
    for i in TweetAnnotation.objects.all():
        csv += "{};{};{};{}\n".format(
            i.tweet.tweet_id,
            i.symptom,
            i.uuid,
            i.created
        )

    response = HttpResponse(csv, content_type='text')
    response['Content-Disposition'] = "attachment; filename=%s" % "annotations.csv"
    return response
