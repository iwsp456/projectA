import os
from django.db import connection
import csv
import sys
import django

# from traitlets import default

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject.settings")
django.setup()

from wordcloudTest.models import *  # django.setup() 이후에 임포트해야 오류가 나지 않음

def django_db_upload():
    subway = ['hongikUniv', 'moran', 'pangyo']
    for s in subway :
        CSV_PATH_PRODUCTS = '..\\data\\' + s + '.csv'
        
        file = open(CSV_PATH_PRODUCTS, encoding = 'utf-8')
        data_reader = csv.reader(file)
        next(data_reader,None)
        for row in data_reader:
            if s == 'hongikUniv':
                HongikUniv.objects.create(
                    content = row
                )
            elif s == 'moran' :
                Moran.objects.create(
                    content = row
                )
            else :
                Pangyo.objects.create(
                    content = row
                )
            print(row[0])
        file.close()

django_db_upload()

