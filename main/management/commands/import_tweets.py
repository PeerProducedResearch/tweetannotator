from django.core.management.base import BaseCommand
import pandas as pd
from main.models import Tweet


class Command(BaseCommand):
    help = "Import tweets from a file"

    def handle(self, *args, **options):
        df = pd.read_csv('covid_mars_utf.csv',sep="\n",header=None)
        for i in df[0]:
            t, _ = Tweet.objects.get_or_create(text=i)
            t.save()
