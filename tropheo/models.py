from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


"""
Game Models
models related to playstation games and their stats.
"""

class Game(models.Model):
    PLATFORMS = (
        ('ps3', 'PlayStation 3'),
        ('ps4', 'PlayStation 4'),
        ('vita', 'PlayStation Vita')
    )
    id = models.CharField(primary_key=True, max_length=99)
    simple_id = models.CharField(max_length=99)
    title = models.CharField(max_length=99)
    platform = models.CharField(max_length=4, choices=PLATFORMS)
    maturity_rating = models.CharField(max_length=5)
    genre = models.CharField(max_length=150)
    top_genre = models.CharField(max_length=150)
    release_date = models.DateField()
    publisher = models.CharField(max_length=99)
    critic_score = models.PositiveSmallIntegerField()
    user_score = models.PositiveSmallIntegerField()
    platinum = models.PositiveSmallIntegerField()
    gold = models.PositiveSmallIntegerField()
    silver = models.PositiveSmallIntegerField()
    bronze = models.PositiveSmallIntegerField()
    points = models.PositiveSmallIntegerField()
    image_url = models.URLField()

    def __str__(self):
        return self.title


class Ngame(models.Model):
    class Meta:
      managed = False

    PLATFORMS = (
        ('ps3', 'PlayStation 3'),
        ('ps4', 'PlayStation 4'),
        ('vita', 'PlayStation Vita')
    )
    id = models.CharField(primary_key=True, max_length=99)
    simple_id = models.CharField(max_length=99)
    title = models.CharField(max_length=99)
    platform = models.CharField(max_length=4, choices=PLATFORMS)
    maturity_rating = models.CharField(max_length=5)
    genre = models.CharField(max_length=150)
    top_genre = models.CharField(max_length=150)
    release_date = models.DateField()
    publisher = models.CharField(max_length=99)
    critic_score = models.FloatField()
    user_score = models.FloatField()
    platinum = models.PositiveSmallIntegerField()
    gold = models.PositiveSmallIntegerField()
    silver = models.PositiveSmallIntegerField()
    bronze = models.PositiveSmallIntegerField()
    points = models.PositiveSmallIntegerField()
    weighted_points = models.FloatField()
    image_url = models.URLField()
    weighted_score = models.FloatField()
    score = models.FloatField()

class GameStats(models.Model):
    class Meta:
      managed = False

    platform = models.CharField(primary_key=True, max_length=5)
    critic_mean = models.FloatField()
    critic_stdev = models.FloatField()
    user_mean = models.FloatField()
    user_stdev = models.FloatField()


"""
User Models
models related to user profiles and user settings.
"""

class Profile(models.Model):
    """
    User Profile Model
    extend the User model to have a few other data fields, all optional?
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    psn_id = models.CharField(max_length=16, blank=True)
    avatar = models.URLField()
    is_plus = models.BooleanField(default=False)
    level = models.IntegerField(default=0)
    level_progress = models.IntegerField(default=0)
    game_count = models.IntegerField(default=0)
    platinum = models.IntegerField(default=0)
    gold = models.IntegerField(default=0)
    silver = models.IntegerField(default=0)
    bronze = models.IntegerField(default=0)
    is_private = models.BooleanField(default=False)
    is_empty = models.BooleanField(default=True)
    played_games = models.ManyToManyField(Ngame)


    def _get_game_genres(self):
        genre_data = {}
        for game in self.played_games.all():
            for genre in list(game.genre.split(',')):
                if genre not in genre_data:
                    genre_data[genre] = 1
                else:
                    genre_data[genre] += 1

        return genre_data

    def _get_played_game_ids(self):
        return [game.id for game in self.played_games.all()]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
        # Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


"""
Utilities
models for special functions
"""
class UserAgent(models.Model):
    user_agent = models.CharField(primary_key=True, max_length=250)
