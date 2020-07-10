from django.shortcuts import render, redirect
import uuid
import random
from .models import Tweet, TweetAnnotation
from django.db.models import Max
# Create your views here.
from django.http import HttpResponse


def get_random_tweet():
    max_id = Tweet.objects.all().aggregate(max_id=Max("id"))['max_id']
    while True:
        pk = random.randint(1, max_id)
        tweet = Tweet.objects.filter(pk=pk).first()
        if tweet:
            return tweet


def index(request):
    tweet = get_random_tweet()
    tweet.text = tweet.text.strip(";;")
    tweet_annotations = TweetAnnotation.objects.all()
    context = {'tweet': tweet, 'tweet_annotations': tweet_annotations}

    print(request.session.keys())
    if not request.session.get('uuid', ''):
        request.session['uuid'] = str(uuid.uuid4())
    print(request.session.get('uuid'))
    return render(request, 'main/index.html', context)


def annotate(request, tweet_id, answer):
    tweet = Tweet.objects.get(id=tweet_id)
    answer = bool(answer)
    ta = TweetAnnotation.objects.create(
        tweet=tweet,
        symptom=answer,
        uuid=request.session.get('uuid', ''))
    ta.save()
    return redirect('/')
