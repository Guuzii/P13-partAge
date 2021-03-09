from django.urls import path

from . import views

urlpatterns = [
    path('', views.MessageInboxView.as_view(), name='message-inbox'),
]