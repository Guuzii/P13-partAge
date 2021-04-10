from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('', login_required(views.MissionBoard.as_view()), name='mission-board'),
    path('details/<uidb64>/', login_required(views.MissionDetails.as_view()), name='mission-details'),
    path('manage/<uidb64>/', login_required(views.MissionManagement.as_view()), name='mission-manage'),
    path('create/', login_required(views.MissionCreate.as_view()), name='mission-create'),
]