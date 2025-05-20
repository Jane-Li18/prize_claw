import os
import uuid
from django.db import models

def prize_image_upload_to(instance, filename):
    # Extract the file extension
    ext = os.path.splitext(filename)[1]
    # Generate a unique filename using uuid
    unique_filename = f"{uuid.uuid4()}{ext}"
    return f"prizes/{unique_filename}"

class Prize(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to=prize_image_upload_to, null=True, blank=True)
    probability = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Game(models.Model):
    player_name = models.CharField(max_length=100)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE, null=True, blank=True)
    won = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.player_name} - {self.prize if self.prize else 'No Prize'}"
    

class Leaderboard(models.Model):
    player_name = models.CharField(max_length=100)
    score = models.IntegerField(default=0)  # Store the player's score
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player_name} - {self.score}"

