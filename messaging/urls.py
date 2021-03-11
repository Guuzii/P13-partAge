from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('', login_required(views.MessageInbox.as_view()), name='message-inbox'),
    path('conversation/<uidb64>/', login_required(views.MessageConversation.as_view()), name='message-conv'),
]