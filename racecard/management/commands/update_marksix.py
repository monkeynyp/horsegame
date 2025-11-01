from django.core.management.base import BaseCommand
from racecard.models import Marksix_hist,LottoTrioSearch, Marksix_user_rec
from datetime import datetime
from django.db.models import Q, Max
from django.core.mail import send_mail
from django.utils import timezone
from django.db import models
from sklearn.neighbors import KNeighborsRegressor
import math
from django.contrib.auth import get_user_model

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
                    # After updating user records for this draw, generate and save KNN-based chart prediction
            
            try:
                pred_rec = marksix_predict()
                if pred_rec:
                    self.stdout.write(self.style.SUCCESS(f"Marksix prediction (Chart) saved for draw {pred_rec.Draw}"))
            except Exception as e:
                # Do not fail the whole command for prediction errors
                self.stdout.write(self.style.WARNING(f"marksix_predict failed: {e}"))
        
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

        # After updating trio search, generate KNN predictions for next draw and save as a "Chart" user rec
        try:
            marksix_pred = marksix_predict()
            if marksix_pred:
                self.stdout.write(self.style.SUCCESS(f"Marksix prediction saved for draw {marksix_pred.Draw}"))
        except Exception as ex:
            # avoid failing the whole command if prediction has an issue
            self.stdout.write(self.style.WARNING(f"marksix_predict failed: {ex}"))
 
def calculate_days_difference(record_date):
    # Convert record_date to a datetime object if it's not already
    if isinstance(record_date, str):
        record_date = datetime.strptime(record_date, '%Y-%m-%d').date()

    # Get the current date
    current_date = datetime.now().date()

    # Calculate the difference in days
    days_difference = (current_date - record_date).days

    return days_difference

def marksix_predict(id='1'):
    """
    Predict next number for No1..No7 using sliding-window KNN (window=5)
    and save the predicted 7-number record to Marksix_user_rec with User='Chart'.
    Returns the created/updated Marksix_user_rec instance.
    """
    import math
    from sklearn.neighbors import KNeighborsRegressor
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from django.db.models import Max

    # Determine next draw seed based on largest Draw value
    largest_draw = Marksix_hist.objects.aggregate(largest_draw=models.Max('Draw'))['largest_draw']
    if not largest_draw:
        raise ValueError("No existing draws found in Marksix_hist")

    # remove slash and increment
    draw_without_slash = largest_draw.replace('/', '')
    try:
        seed_no = int(draw_without_slash) + 1
    except ValueError:
        raise ValueError(f"Cannot parse largest_draw '{largest_draw}' to integer")

    draw_string = str(seed_no).zfill(5)  # zero-pad if needed
    next_draw = f"{draw_string[:2]}/{draw_string[2:]}"

    update_date = timezone.now().date()

    predicted_numbers = {}
    used_numbers = set()
    window = 5  # sliding window length

    def clamp_and_fix(val):
        """Ensure integer within 1..49 and return int."""
        try:
            iv = int(math.ceil(val))
        except Exception:
            iv = 1
        if iv < 1:
            iv = 1
        if iv > 49:
            iv = ((iv - 1) % 49) + 1
        return iv

    def find_nearest_available(start, used):
        """Search outward from start for the nearest number in 1..49 not in used."""
        start = int(start) if start is not None else 1
        for offset in range(0, 50):
            cand1 = start + offset
            cand2 = start - offset
            if 1 <= cand1 <= 49 and cand1 not in used:
                return cand1
            if 1 <= cand2 <= 49 and cand2 not in used:
                return cand2
        return 1

    # For each No1..No7, build prediction
    for idx in range(1, 8):
        listNo = f"No{idx}"

        qs = Marksix_hist.objects.order_by('Date').values_list(listNo, flat=True)
        # Convert and remove None
        data_list = [int(x) for x in qs if x is not None]

        predicted = None

        # If insufficient data for sliding-window, fallback to most recent if exists
        if len(data_list) <= window:
            if data_list:
                predicted = data_list[-1]
            else:
                predicted = 1  # fallback if totally empty

            # ensure in range and unique
            predicted = clamp_and_fix(predicted)
            if predicted in used_numbers:
                predicted = find_nearest_available(predicted, used_numbers)

        else:
            # Build sliding-window X,y
            X = []
            y = []
            for j in range(len(data_list) - window):
                X.append(data_list[j:j + window])
                y.append(data_list[j + window])

            # Try KNN with neighbors 5 (as used in view). If fails, try 3 then 9
            tried = False
            for n_neighbors in (5, 3, 9):
                try:
                    knn = KNeighborsRegressor(n_neighbors=n_neighbors)
                    knn.fit(X, y)
                    pred_val = knn.predict([data_list[-window:]])[0]
                    cand = clamp_and_fix(pred_val)
                    # If cand not used, accept
                    if cand not in used_numbers:
                        predicted = cand
                        tried = True
                        break
                    # else try next n_neighbors
                except Exception:
                    # skip and try next n_neighbors
                    continue

            # If still not accepted, pick nearest available around last observed
            if (predicted is None) or (predicted in used_numbers):
                base = data_list[-1] if data_list else 1
                base = clamp_and_fix(base)
                nearest = find_nearest_available(base, used_numbers)
                predicted = nearest

        # ensure predicted integer and uniqueness with wrap-around increment
        predicted = clamp_and_fix(predicted)
        while predicted in used_numbers:
            predicted += 1
            if predicted > 49:
                predicted = 1

        used_numbers.add(predicted)
        predicted_numbers[listNo] = predicted

    # Build defaults to save; attempt to set fields No1..No7, User/Draw/Date
    defaults = {
        'Draw': next_draw,
        'Date': update_date,
        'No1': predicted_numbers.get('No1'),
        'No2': predicted_numbers.get('No2'),
        'No3': predicted_numbers.get('No3'),
        'No4': predicted_numbers.get('No4'),
        'No5': predicted_numbers.get('No5'),
        'No6': predicted_numbers.get('No6'),
        'No7': predicted_numbers.get('No7'),
    }

    # Ensure we use a real User object for the ForeignKey. Create a system user "Chart" if missing.
    User = get_user_model()
    chart_user, created_user = User.objects.get_or_create(
        username='Chart',
        defaults={'email': 'chart@example.com', 'is_active': False}
    )

    # Determine next seq = last seq + 1 to satisfy NOT NULL constraint
    last_seq = Marksix_user_rec.objects.aggregate(max_seq=Max('seq'))['max_seq'] or 0
    defaults['seq'] = int(last_seq) + 1

    # Save/update the predicted record tied to that user
    lotto_rec, created = Marksix_user_rec.objects.update_or_create(
        user=chart_user,
        Draw=next_draw,
        defaults=defaults
    )

    return lotto_rec
