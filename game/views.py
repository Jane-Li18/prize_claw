import random, os, uuid
from django.shortcuts import render, redirect, get_object_or_404
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Prize, Game, Leaderboard
from .forms import PrizeForm
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

from supabase import create_client, Client

SUPABASE_URL = "https://lfhkgzpnkeaspxglxqdf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxmaGtnenBua2Vhc3B4Z2x4cWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc3OTA5ODUsImV4cCI6MjA2MzM2Njk4NX0.fdJXMHmfMs0EH-rA0rl2CaWAv9DevdpKr1j7B3MZhSo"  # Get from Supabase → Project Settings → API

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@csrf_exempt
def submit_feedback(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            feedback = data.get('feedback', '').strip()
            rating = data.get('rating', '0').strip()

            if not email or not feedback:
                return JsonResponse({'error': 'Both email and feedback are required.'}, status=400)

            # Send email (your existing code)
            subject = f"Prize Claw Feedback: {email}"
            message = f"Email: {email}\n\nRating: {rating}\n\nFeedback:\n{feedback}"
            recipient_list = ['shanelee.jabonillo18@gmail.com']
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False
            )
            
            return JsonResponse({'success': True, 'message': 'Feedback submitted successfully!'}, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Failed to send feedback: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def weighted_random_choice(prizes):
    # Include all prizes, even those with probability 0.0
    valid_prizes = [prize for prize in prizes if prize.probability >= 0.0]

    if not valid_prizes:
        return None  # No valid prizes to choose from

    # Adjust weights for prizes
    adjusted_weights = []
    for prize in valid_prizes:
        weight = prize.probability
        # Increase weight for low-probability prizes significantly
        if 0.1 <= weight < 0.5:  # Low chance prizes
            weight *= 2  # Increase their weight significantly
        elif 0.5 <= weight < 0.8:  # Medium chance prizes
            weight *= 1.2  # Increase their weight moderately
        # High chance prizes remain unchanged
        adjusted_weights.append(weight)

    total_weight = sum(adjusted_weights)

    if total_weight <= 0:
        return None  # Avoid division by zero or invalid selection

    rand = random.uniform(0, total_weight)

    cumulative_weight = 0
    for i, prize in enumerate(valid_prizes):
        cumulative_weight += adjusted_weights[i]
        if rand < cumulative_weight:
            return prize

    return None


def claw_machine(request):
    # Always include the 4 built-in prizes
    built_in_prizes = [
        {'name': 'Pink Rabbit', 'image': os.path.join(settings.STATIC_URL, 'prizes/Pink_Rabbit.png')},
        {'name': 'MisterX', 'image': os.path.join(settings.STATIC_URL, 'prizes/MisterX.png')},
        {'name': 'Grizzly', 'image': os.path.join(settings.STATIC_URL, 'prizes/Grizzly.png')},
        {'name': 'Wairobot', 'image': os.path.join(settings.STATIC_URL, 'prizes/Wairobot.png')},
    ]

    # Fetch all prizes with probability > 0.0
    valid_prizes = Prize.objects.filter(probability__gt=0.0)

    # Select at least one rare prize (0.1 to 0.5)
    rare_prizes = [prize for prize in valid_prizes if 0.1 <= prize.probability < 0.5]
    active_prizes = []
    selected_rare_prize = None  # Initialize to None

    if rare_prizes:  # If there are rare prizes available
        selected_rare_prize = random.choice(rare_prizes)
        active_prizes.append({
            'name': selected_rare_prize.name,
            'image': selected_rare_prize.image  # Use direct URL, not .url
        })

    # Fill the rest of the prizes to ensure total is 6
    while len(active_prizes) < (6 - len(built_in_prizes)):
        selected_prize = weighted_random_choice(valid_prizes)
        if selected_prize and (selected_rare_prize is None or selected_rare_prize.name != selected_prize.name):
            active_prizes.append({
                'name': selected_prize.name,
                'image': selected_prize.image  # Use direct URL
            })

    # Combine built-in and database prizes
    all_prizes = built_in_prizes + active_prizes

    # Shuffle the combined list to randomize positions
    random.shuffle(all_prizes)

    # Return JSON if requested via API
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'prizes': all_prizes})

    return render(request, 'game/claw_machine.html', {'prizes': all_prizes})


def main(request):
    # Fetch only prizes with probability > 0.1
    prizes = Prize.objects.filter(probability__gt=0.0)
    leaderboard = Leaderboard.objects.order_by('-score')[:10]
    return render(request, 'game/main.html', {'prizes': prizes, 'leaderboard': leaderboard})


def feedback(request):
    prizes = Prize.objects.all()
    leaderboard = Leaderboard.objects.order_by('-score')[:10]
    return render(request, 'game/feedback.html', {'prizes': prizes, 'leaderboard': leaderboard})

def prize(request):
    prizes = Prize.objects.all().order_by('-created_at')
    leaderboard = Leaderboard.objects.order_by('-score')[:10]

    if request.method == 'POST':
        if 'delete_prize' in request.POST:
            prize_id = request.POST.get('delete_prize')
            prize = get_object_or_404(Prize, id=prize_id)
            prize.delete()
            messages.success(request, 'Prize deleted successfully!')
            return redirect('prize')
        
        # Handle form submission for adding a prize
        else:
            form = PrizeForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Prize added successfully!')
                return redirect('prize')
    else:
        # Initialize an empty form for GET requests
        form = PrizeForm()

    # Render the template with prizes, leaderboard, and form
    return render(request, 'game/prize.html', {
        'prizes': prizes,
        'leaderboard': leaderboard,
        'form': form
    })


@csrf_exempt
def submit_score(request):
    if request.method == 'POST':
        player_name = request.POST.get('player_name')
        score = request.POST.get('score')

        print(f"Received score submission: Player Name = {player_name}, Score = {score}")
        
        Leaderboard.objects.create(player_name=player_name, score=score)

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


# @csrf_exempt
# def upload_prizes(request):
#     if request.method == 'POST':
#         try:
#             for file, name, probability in zip(
#                 request.FILES.getlist('files'),
#                 request.POST.getlist('prize_name'),
#                 request.POST.getlist('probability')
#             ):
#                 if not name.strip():
#                     return JsonResponse({'status': 'error', 'message': 'Prize name cannot be empty.'}, status=400)

#                 # Create prize - the image will be automatically handled by Django
#                 Prize.objects.create(
#                     name=name.strip(),
#                     probability=float(probability),
#                     image=file  # Just pass the file directly
#                 )

#             return JsonResponse({'status': 'success', 'message': 'Prizes uploaded successfully!'})
#         except Exception as e:
#             logger.error(f"Error saving prize: {str(e)}")
#             return JsonResponse({'status': 'error', 'message': f'Error saving prize: {str(e)}'}, status=500)

@csrf_exempt
def upload_prizes(request):
    if request.method == 'POST':
        try:
            for file, name, probability in zip(
                request.FILES.getlist('files'),
                request.POST.getlist('prize_name'),
                request.POST.getlist('probability')
            ):
                if not name.strip():
                    return JsonResponse({'status': 'error', 'message': 'Prize name cannot be empty.'}, status=400)

                # Generate a unique filename
                ext = os.path.splitext(file.name)[1]
                unique_filename = f"{str(uuid.uuid4())[:8]}{ext}"
                
                # Upload path should not include the bucket name
                file_path = unique_filename  # Just the filename, no "prizes/" prefix

                # Upload to Supabase
                file_content = file.read()
                
                try:
                    res = supabase.storage.from_("prizes").upload(
                        path=file_path,
                        file=file_content,
                        file_options={"content-type": file.content_type}
                    )
                    
                    # Construct the correct public URL
                    image_url = f"{SUPABASE_URL}/storage/v1/object/public/prizes/{file_path}"
                    
                    # Save to database
                    Prize.objects.create(
                        name=name.strip(),
                        probability=float(probability),
                        image=image_url
                    )
                    
                except Exception as upload_error:
                    logger.error(f"Supabase upload error: {str(upload_error)}")
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'File upload failed: {str(upload_error)}'
                    }, status=500)

            return JsonResponse({'status': 'success', 'message': 'Prizes uploaded successfully!'})
            
        except Exception as e:
            logger.error(f"Error saving prize: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error', 
                'message': f'Error: {str(e)}'
            }, status=500)




def magic_eight_ball(request):
    # Fetch only prizes with probability > 0.1
    prizes = Prize.objects.filter(probability__gt=0.0)
    leaderboard = Leaderboard.objects.order_by('-score')[:10]
    return render(request, 'game/main.html', {'prizes': prizes, 'leaderboard': leaderboard})
