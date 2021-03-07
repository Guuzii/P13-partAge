from django.urls import path

from . import views

urlpatterns = [
    path('', views.MessageInbox.as_view(), name='message-inbox'),
]