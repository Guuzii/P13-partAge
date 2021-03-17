from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('', login_required(views.MissionBoard.as_view()), name='mission-board'),
]