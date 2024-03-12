from django.shortcuts import render

# Create your views here.


def index_action(request): 
    context = {} 
    return render(request, "game/index.html", context)



def play_action(request): 
    context = {} 
    return render(request, "game/play.html", context) 