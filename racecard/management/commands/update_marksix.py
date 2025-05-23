from django.core.management.base import BaseCommand
from racecard.models import Marksix_hist,LottoTrioSearch, Marksix_user_rec
from datetime import datetime
from django.db.models import Q
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Create a new Marksix record'

    def handle(self, *args, **options):
        # Prompt for the new Marksix information
        input_string = input("Enter the new Marksix information (format: '25/001\t2025-01-02\t9,23,42,44,45,46\t22'): ")
        
        # Debugging output
        print(f"Input string: {input_string}")
        
        # Break down the input string
        try:
            draw, date_str, numbers_str, special_number = input_string.split('\t')
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            numbers = numbers_str.split(',')

            if len(numbers) != 6:
                self.stdout.write(self.style.ERROR('Invalid number of regular numbers. There should be exactly 6 numbers.'))
                return

            # Create or update a Marksix_hist record
            marksix_record, created = Marksix_hist.objects.update_or_create(
                Draw=draw,
                defaults={
                    'Date': date,
                    'No1': int(numbers[0]),
                    'No2': int(numbers[1]),
                    'No3': int(numbers[2]),
                    'No4': int(numbers[3]),
                    'No5': int(numbers[4]),
                    'No6': int(numbers[5]),
                    'No7': int(special_number)
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS('Successfully created new Marksix record.'))
            else:
                self.stdout.write(self.style.SUCCESS('Successfully updated existing Marksix record.'))
        # Validate the Hit number of User's Record
            user_records = Marksix_user_rec.objects.all()

            for user_record in user_records:
                score = 0
                user_numbers = [user_record.No1, user_record.No2, user_record.No3, user_record.No4, user_record.No5, user_record.No6]
                result_numbers = [marksix_record.No1, marksix_record.No2, marksix_record.No3, marksix_record.No4, marksix_record.No5, marksix_record.No6]
                print(user_numbers)
                for num in user_numbers:
                    print(num,result_numbers)
                    if num in result_numbers:
                        score += 1

                    if num == marksix_record.No7:
                        score += 0.5
                        
                    print("Score is:", score)
                if score == 3:
                    user_record.Hit7 += 1
                elif score == 3.5:
                    user_record.Hit6 += 1
                elif score == 4:
                    user_record.Hit5 += 1
                elif score == 4.5:
                    user_record.Hit4 += 1
                elif score == 5:
                    user_record.Hit3 += 1
                elif score == 5.5:
                    user_record.Hit2 += 1
                elif score == 6:
                    user_record.Hit1 += 1
                user_record.save()
                if score >= 3:
                    send_mail(
                        'Congratulations!',
                        f'Congratulations! Your Marksix record {user_numbers} has hit a score of {score}.',
                        'from@example.com',
                        [user_record.user.email],
                        fail_silently=False,
                    )
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'Error parsing input: {e}'))

# Find the oldest combination
# Step 1: Fetch the first 20 records from LottoTrioSearch ordered by Diff_days in descending order
        
        top_20_records = LottoTrioSearch.objects.order_by('-Diff_days')[:50]
        #print(top_20_records)

        # Extract No1, No2, No3 into an array of number lists
        number_lists = [[record.No1, record.No2, record.No3] for record in top_20_records]
        #print("Number Lists:", number_lists)

        # Step 2: Run the loop of top_20_records with the following logic
        for number_list in number_lists:
            condition = (
                Q(No1=number_list[0]) | Q(No2=number_list[0]) | Q(No3=number_list[0]) | Q(No4=number_list[0]) | Q(No5=number_list[0]) | Q(No6=number_list[0]) | Q(No7=number_list[0])
            ) & (
                Q(No1=number_list[1]) | Q(No2=number_list[1]) | Q(No3=number_list[1]) | Q(No4=number_list[1]) | Q(No5=number_list[1]) | Q(No6=number_list[1]) | Q(No7=number_list[1])
            ) & (
                Q(No1=number_list[2]) | Q(No2=number_list[2]) | Q(No3=number_list[2]) | Q(No4=number_list[2]) | Q(No5=number_list[2]) | Q(No6=number_list[2]) | Q(No7=number_list[2])
            )

            record = Marksix_hist.objects.filter(condition).distinct().last()
            freq = Marksix_hist.objects.filter(condition).count()
            if record:
                diff = calculate_days_difference(record.Date)
                freq = Marksix_hist.objects.filter(condition).count()

                lotto_trio_search, created = LottoTrioSearch.objects.update_or_create(
                    Draw=draw,
                    No1=number_list[0],
                    No2=number_list[1],
                    No3=number_list[2],
                    Freq=freq,
                    defaults={
                        'Search_date': datetime.now().date(),
                        'Diff_days': diff
                    }
                )

 
def calculate_days_difference(record_date):
    # Convert record_date to a datetime object if it's not already
    if isinstance(record_date, str):
        record_date = datetime.strptime(record_date, '%Y-%m-%d').date()

    # Get the current date
    current_date = datetime.now().date()

    # Calculate the difference in days
    days_difference = (current_date - record_date).days

    return days_difference