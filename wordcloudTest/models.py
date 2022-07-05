from django.db import models

# Create your models here.

class Moran(models.Model):
    content = models.TextField(blank = True, null = True)

class Pangyo(models.Model):
    content = models.TextField(blank = True, null = True)

class HongikUniv(models.Model):
    content = models.TextField(blank = True, null = True)

