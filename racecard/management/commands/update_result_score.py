from django.core.management.base import BaseCommand
from racecard.models import UserTips,UserScores  # Replace 'YourModel' with the actual model name
from datetime import datetime
import pandas as pd
import os
from django.conf import settings
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField, Window, Max, Subquery, OuterRef
from django.db.models.functions import Lag, RowNumber
from datetime import timedelta


class Command(BaseCommand):
    help = 'Update data from CSV files to SQLite database'
    
    def handle(self, *args, **options):

# Subquery to get the maximum total records
        max_total_records_query = UserScores.objects.all().annotate(
            max_total_records=Max('total_records')
        ).values_list('max_total_records', flat=True)

        max_total_records = max_total_records_query[0] if max_total_records_query else None
        print("Max record:",max_total_records)


        user_tips_data = UserTips.objects.values('user').annotate(
            latest_race_dates=Subquery(
                UserTips.objects.filter(user=OuterRef('user')).order_by('-race_date').values('race_date')[:10]
                ),
                recent_hits=Sum('hit'),
                recent_total=Count('id'),
                recent_dividend=Sum('dividend')
            ).annotate(
            total_records=Count('id'),
            total_hits=Sum('hit'),
            total_dividend=Sum('dividend'),
            hit_weight=ExpressionWrapper(
                0.2 * F('total_hits') / F('total_records')
                + 0.6 * F('recent_hits')/ F('recent_total')
                + 0.2 * F('recent_total') /300,
                output_field=FloatField()
            )
        )
        # Loop through the user tips data and update the user scores
        for user_tip in user_tips_data:
            # Get or create the user score for the user
            user_score, created = UserScores.objects.get_or_create(user_id=user_tip['user'])
            # Update the user score with the total records and total hits
            user_score.total_records = user_tip['total_records']
            user_score.total_hits = user_tip['total_hits']
            user_score.total_dividend=user_tip['total_dividend']
            user_score.hit_weight = user_tip['hit_weight']
            print(user_score.hit_weight)
            print(user_score.total_records)
            print(user_score.total_hits)
            # Save the user score
            user_score.save()