from django.urls import path
from . import views

'''
urls.py에서 views.py로
'''

urlpatterns = [
    path('', views.index, name='index'),
    path('ner_list/<int:content_id>/', views.ner, name='ner'),
    path('ner_list/', views.ner_list, name='ner_list'),
    path('mrc_list/<int:content_id>/', views.mrc, name='mrc'),
    path('mrc_list/', views.mrc_list, name='mrc_list'),
]