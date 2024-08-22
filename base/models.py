from typing import Iterable
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    username = models.CharField(max_length=255,default='username')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255,null=True)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=50,choices=[('male','male'),('female','female'),('others','others')])
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Artist(models.Model):
    name = models.CharField(max_length=255)
    dob = models.DateField()
    gender = models.CharField(max_length=50,choices=[('male','male'),('female','female'),('others','others')])
    address = models.CharField(max_length=255)
    first_release_year = models.DateField()
    no_of_albums_released = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)



class Music(models.Model):
    artist_id = models.ForeignKey(Artist,on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    album_name = models.CharField(max_length=255)
    genre = models.CharField(max_length=50,choices=[('rnb','rnb'),('country','country'),('classic','classic'),('rock','rock'),('jazz','jazz')])
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
