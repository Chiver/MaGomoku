"""
URL configuration for magomoku project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from game import views 

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index_action, name="index"), 
    path("play", views.play_action, name="play"),
    path("move_piece_action", views.move_piece_action, name="move"),
    path("physical_placement_action", views.physical_placement_action, name="physical"), 
    path("fetch_physical_move_action", views.fetch_physical_move_action, name="fetch")
    # path("update_piece_action", views.update_piece_action, name="update") 
]
