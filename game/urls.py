from django.urls import path
from .views import claw_machine, main, submit_score, prize, feedback, submit_feedback, upload_prizes

urlpatterns = [
    path('', main, name='main'),
    path('claw_machine/', claw_machine, name='claw_machine'),
    path('submit-score/', submit_score, name='submit_score'),
    path('prize', prize, name='prize'),
    path('feedback', feedback, name='feedback'),
    path('submit-feedback/', submit_feedback, name='submit_feedback'),
    path('upload-prizes/', upload_prizes, name='upload_prizes'),
]
