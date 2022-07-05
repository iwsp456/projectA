from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect


'''
views.py를 통해서 target.html로
'''

def index(request):
    return render(request, 'wordcloudTest/index.html')
