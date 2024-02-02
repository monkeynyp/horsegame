import csv
from django.core.management.base import BaseCommand
from racecard.models import UserTips  # Replace 'YourModel' with the actual model name

class Command(BaseCommand):
    help = 'Update data from CSV files to SQLite database'

    def handle(self, *args, **options):
        # Your logic to read and update data from CSV files
        file_paths = ['data/predict_race_place_log1.csv', 'data/predict_race_place_log1.csv']

        for file_path in file_paths:
            with open(file_path, 'r') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                for row in csv_reader:
                    # Your logic to update the database
                    UserTips.objects.update_or_create(
                        # Map CSV columns to model fields
                        field1=row['csv_column1'],
                        field2=row['csv_column2'],
                        # ...
                    )

        self.stdout.write(self.style.SUCCESS('Data updated successfully.'))