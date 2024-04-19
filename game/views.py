from django.shortcuts import render

# Create your views here.
import requests
from django.http import JsonResponse

from game.models import PlaceEvent

EMPTY_PIECE = "EMPTY"
WHITE_PIECE = "WHITE"
BLACK_PIECE = "BLACK"

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

# If the board detects a new move, this is the endpoint to call. 
# The data format is as follows: (prev, curr, x, y) 
def physical_placement_action(request): 
    prev = request.GET.get('prev', EMPTY_PIECE) 
    curr = request.GET.get('curr', EMPTY_PIECE) 
    x = request.GET.get('x', -1) 
    y = request.GET.get('y', -1) 
    tup = (prev, curr, x, y)
    
    # Check for validity 
    if (prev != EMPTY_PIECE): 
        return JsonResponse({'status': 'error', 'message': f"Previous placement is non-empty {tup}"})
    elif (x == -1 or y == -1): 
        return JsonResponse({'status': 'error', 'message': f"Invalid index {tup}"})
    elif (prev == EMPTY_PIECE and curr == EMPTY_PIECE): 
        return JsonResponse({'status': 'error', 'message': f"Both empty placement {tup}"})
    
    # Place that shit on the board
    PlaceEvent.objects.create(
        prev=prev,
        curr=curr,
        x=int(x),
        y=int(y),
        consumed=False
    )
    return JsonResponse({'status': 'success', 'message': f"DB record placed. {tup}"})

# Used for frontend polling 
def fetch_physical_move_action(request):
    event = PlaceEvent.objects.filter(consumed=False).first()
    if event:
        event.consumed = True
        event.save()
        return JsonResponse({
            "status": "true", 
            "prev": event.prev,
            "curr": event.curr,
            "x": event.x,
            "y": event.y,
            "time_created": event.time_created.strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        # No new moves. 
        return JsonResponse({"status": "false"})


def index_action(request): 
    context = {} 
    return render(request, "game/index.html", context)



def play_action(request): 
    context = {} 
    return render(request, "game/play.html", context) 