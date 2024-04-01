from django.shortcuts import render

# Create your views here.
import requests
from django.http import JsonResponse

def move_piece_action(request):
    x = request.GET.get('x', 0)  # Default to 0 if not provided
    y = request.GET.get('y', 0)  # Default to 0 if not provided
    print(f"{x} {y}")
    try:
        flask_url = 'http://localhost:5000/move_piece'
        response = requests.get(flask_url, params={'x': x, 'y': y})
        return JsonResponse({'status': 'success', 'data': response.json()})
    except requests.exceptions.RequestException as e:
        # Handle connection error
        print(e)
        return JsonResponse({'status': 'error', 'message': str(e)})


def index_action(request): 
    context = {} 
    return render(request, "game/index.html", context)



def play_action(request): 
    context = {} 
    return render(request, "game/play.html", context) 