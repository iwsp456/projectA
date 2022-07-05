from django.apps import AppConfig
from tensorflow import keras
import pandas as pd
from sklearn.model_selection import train_test_split
from eunjeon import Mecab
import numpy as np
import re
import tensorflow as tf
import keras
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

class SinglePagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'single_pages'
    model = keras.models.load_model('./model.h5')

    hongdae = pd.read_csv('./홍대1.csv')
    moran = pd.read_csv('./모란1.csv')
    gangnam = pd.read_csv('./판교1.csv')

    total_data = pd.concat([hongdae, moran, gangnam])

    def ready(self):
        pass