from django.core.management.base import BaseCommand
import pandas as pd
from main.models import Tweet


class Command(BaseCommand):
    help = "Import tweets from a file"

    def handle(self, *args, **options):
        df = pd.read_csv('static/list_covid_symptoms.testing.csv', sep=";")
        for i, row in df.iterrows():
            t, _ = Tweet.objects.get_or_create(
                text=row['anonymized_text'],
                tweet_id=row['id_str'],
                date=row['day'])
            t.save()
