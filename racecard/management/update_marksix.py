from django.core.management.base import BaseCommand
from racecard.models import Marksix_hist
from datetime import datetime

class Command(BaseCommand):
    help = 'Create a new Marksix record'

    def handle(self, *args, **options):
        # Prompt for the new Marksix information
        input_string = input("Enter the new Marksix information (format: '25/001\t2025-01-02\t9,23,42,44,45,46\t22'): ")

        # Break down the input string
        try:
            draw, date_str, numbers_str, special_number = input_string.split('\t')
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            numbers = numbers_str.split(',')

            if len(numbers) != 6:
                self.stdout.write(self.style.ERROR('Invalid number of regular numbers. There should be exactly 6 numbers.'))
                return

            # Create a new Marksix_hist record
            marksix_record = Marksix_hist(
                Draw=draw,
                Date=date,
                No1=int(numbers[0]),
                No2=int(numbers[1]),
                No3=int(numbers[2]),
                No4=int(numbers[3]),
                No5=int(numbers[4]),
                No6=int(numbers[5]),
                Special=int(special_number)
            )
            marksix_record.save()

            self.stdout.write(self.style.SUCCESS('Successfully created new Marksix record.'))

        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'Error parsing input: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An unexpected error occurred: {e}'))