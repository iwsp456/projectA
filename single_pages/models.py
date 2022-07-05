from django.db import models

# Create your models here.

class InstaData(models.Model):
    content = models.TextField()

class NerData(models.Model):
    content = models.TextField()
    answer = models.TextField()

class MrcData(models.Model):
    content = models.TextField()
    question = models.TextField()
    answer = models.TextField()

class LstmData(models.Model):
    answer = models.TextField()