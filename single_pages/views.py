import random

from django.shortcuts import render, redirect
from .models import NerData, MrcData, InstaData, LstmData
from django.core.paginator import Paginator
from django.db import connection
from . import apps
import tensorflow as tf
from eunjeon import Mecab
from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from tensorflow import keras
from sklearn.model_selection import train_test_split
import numpy as np
import re
import ast
import codecs
from urllib.parse import unquote
from collections import Counter

'''
views.py를 통해서 target.html로
'''

def index(request):
    return render(request, 'single_pages/index.html')

def lstm(new_sentence):

    total_data = apps.SinglePagesConfig.total_data

    total_data.drop_duplicates(subset=['content'], inplace=True)
    train_data, test_data = train_test_split(total_data, test_size=0.25, random_state=777)

    train_data.drop_duplicates(subset=['content'], inplace=True)  # reviews 열에서 중복인 내용이 있다면 중복 제거
    train_data['content'] = train_data['content'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]", "")
    train_data['content'].replace('', np.nan, inplace=True)
    train_data = train_data.dropna(how='any')  # Null 값 제거

    test_data.drop_duplicates(subset=['content'], inplace=True)  # 중복 제거
    test_data['content'] = test_data['content'].str.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]", "")  # 정규 표현식 수행
    test_data['content'].replace('', np.nan, inplace=True)  # 공백은 Null 값으로 변경
    test_data = test_data.dropna(how='any')  # Null 값 제거

    mecab = Mecab()

    stopwords = ['도', '는', '다', '의', '가', '이', '은', '한', '에', '하', '고', '을', '를', '인', '듯', '과', '와', '네', '들', '듯', '지', '임', '게']

    train_data['tokenized'] = train_data['content'].apply(mecab.morphs)
    train_data['tokenized'] = train_data['tokenized'].apply(lambda x: [item for item in x if item not in stopwords])

    test_data['tokenized'] = test_data['content'].apply(mecab.morphs)
    test_data['tokenized'] = test_data['tokenized'].apply(lambda x: [item for item in x if item not in stopwords])

    # h_words = np.hstack(train_data[train_data.label == 0]['tokenized'].values)
    # m_words = np.hstack(train_data[train_data.label == 1]['tokenized'].values)
    # j_words = np.hstack(train_data[train_data.label == 2]['tokenized'].values)

    X_train = train_data['tokenized'].values
    y_train = train_data['label'].values
    X_test = test_data['tokenized'].values
    y_test = test_data['label'].values

    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(X_train)

    threshold = 2
    total_cnt = len(tokenizer.word_index)  # 단어의 수
    rare_cnt = 0  # 등장 빈도수가 threshold보다 작은 단어의 개수를 카운트
    total_freq = 0  # 훈련 데이터의 전체 단어 빈도수 총 합
    rare_freq = 0  # 등장 빈도수가 threshold보다 작은 단어의 등장 빈도수의 총 합

    # 단어와 빈도수의 쌍(pair)을 key와 value로 받는다.
    for key, value in tokenizer.word_counts.items():
        total_freq = total_freq + value

        # 단어의 등장 빈도수가 threshold보다 작으면
        if (value < threshold):
            rare_cnt = rare_cnt + 1
            rare_freq = rare_freq + value

    vocab_size = total_cnt - rare_cnt + 2

    tokenizer = Tokenizer(vocab_size, oov_token='OOV')
    tokenizer.fit_on_texts(X_train)
    # X_train = tokenizer.texts_to_sequences(X_train)
    # X_test = tokenizer.texts_to_sequences(X_test)

    model = apps.SinglePagesConfig.model

    max_len = 200

    new_sentence = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣 ]','', new_sentence)
    new_sentence = mecab.morphs(new_sentence) # 토큰화
    new_sentence = [word for word in new_sentence if not word in stopwords] # 불용어 제거

    encoded = tokenizer.texts_to_sequences([new_sentence]) # 정수 인코딩
    pad_new = pad_sequences(encoded, maxlen = max_len, padding='pre') # 패딩
    score = model.predict(pad_new) # 예측
    score = np.argmax(score)

    if score == 0 :
        answer = '홍대입니다'
    elif score == 1 :
        answer = '모란입니다'
    elif score == 2 :
        answer = '판교입니다'
    else :
        answer = '학습된 데이터에 없습니다'

    return answer

def mrc(request, content_id):

    data_obj = MrcData.objects.order_by('pk').last()
    lstm_obj = LstmData.objects.order_by('pk').last()
    content = InstaData.objects.get(id=content_id)

    context = {
        'data': data_obj,
        'content': content,
        'lstm_answer': lstm_obj,
    }

    if request.method == 'POST':
        temp_content = request.POST.get('content')
        temp_question = request.POST.get('question')

        # 입력 데이터 구조 정의
        input_data = {'context' : [temp_content], 'question' : [temp_question]}
        temp_answer = mrc_run(input_data)
        lstm_answer = lstm(temp_content)

        # MrcData 객체 생성
        data_obj = MrcData(content=temp_content, question=temp_question, answer=temp_answer)
        lstm_obj = LstmData(answer=lstm_answer)
        lstm_obj.save()
        data_obj.save()


        return redirect('mrc', content_id)

    return render(request, 'single_pages/mrc.html', context)

def ner(request, content_id):

    content_list = mysql_chart_data("single_pages_nerdata")

    data_obj = NerData.objects.order_by('pk').last()
    content = InstaData.objects.get(id=content_id)
    lstm_obj = LstmData.objects.order_by('pk').last()

    m_list = char_data(content_list)
    x_list, y_list = count(m_list)

    context = {
        'data': data_obj,
        'content': content,
        'lstm_answer': lstm_obj,
        'chart_x': x_list,
        'chart_y': y_list,
    }

    if request.method == 'POST':
        temp_content = request.POST.get('content')

        # 입력 데이터 구조 정의
        input_data = {'texts': [temp_content]}
        temp_answer = ner_run(input_data)
        lstm_answer = lstm('%s' % (temp_content))

        # NerData 객체 생성
        data_obj = NerData(content=temp_content, answer=temp_answer)
        data_obj.save()
        lstm_obj = LstmData(answer=lstm_answer)
        lstm_obj.save()

        return redirect('ner', content_id)

    return render(request, 'single_pages/ner.html', context)

def ner_list(request):

    all_content = InstaData.objects.all()

    paginator = Paginator(all_content, 10)
    page = int(request.GET.get('page', 1))
    content_list = paginator.get_page(page)

    context = {
        'content': content_list,
    }
    return render(request, 'single_pages/ner_list.html', context)

def mrc_list(request):

    all_content = InstaData.objects.all()

    paginator = Paginator(all_content, 10)
    page = int(request.GET.get('page', 1))
    content_list = paginator.get_page(page)

    context = {
        'content': content_list,
    }
    return render(request, 'single_pages/mrc_list.html', context)


# module
import json
import requests

# ner
def ner_run(input_data):

    response = requests.post('http://192.168.0.132:7777/ner', json=input_data)

    # try :
    #     response = requests.post('http://192.168.0.132:7777/ner', json=input_data)
    # except :
    #     response = requests.post('http://192.168.0.205:7777/ner', json=input_data)

    results = ast.literal_eval(response.text)
    ner_output = '\n'

    for result in results:
        for (pos, word, tag) in result:
            ner_output += '['+ word +' : '+tag+']\n'
            # output += word+' ('+tag+')\n'
        ner_output += '\n'

    return ner_output

# mrc
def mrc_run(input_data):

    if type(input_data) is dict:

        response = requests.post('http://192.168.0.132:8888/mrc', json=input_data)
        
        # try :
        #     response = requests.post('http://192.168.0.132:8888/mrc', json=input_data)
        # except :
        #     response = requests.post('http://192.168.0.205:8888/mrc', json=input_data)

        mrc_output = ast.literal_eval(response.text)

        for i in mrc_output :
            mrc_output = i.get('answer')

        # score = (output['score'] / 10) * 100
        # if score > 100 : score = 100
        # output['score'] = f"{score:2.2f}%"

        return mrc_output

def char_data(input_data):
    m = Mecab()  # Mecab 호출

    str = listToString(input_data)
    # str = re.sub("[^A-Za-z0-9가-힣 ]","", str)
    m_list = []  # 형태소 분석이 완료된 단어를 저장할 리스트

    extinc_nouns = ["기관", "인공물", "문명", "날짜", "수량", "지역", "시간", "인물", "동물", "물질", "용어"]

    morphs = m.morphs(str)  # Mecab함수로 명사분석
    for i in morphs:  # 분석한 명사만큼 i를 반복
        if len(i) > 1:  # 글자수가 1개인 것은 제외
            if i not in extinc_nouns :
                m_list.append(i)  # 글자수가 2글자 이상이고, 연합뉴스가 아닌것들 리스트에 추가\

    return m_list

# 단어 빈도수 카운터
def count(m_list):  # 단어 빈도수 구하기 함수정의

    x_list = []
    y_list = []

    counts = Counter(m_list)  # 빈도수 체크
    top_counts = counts.most_common(6)  # 명사 중 제일 많이 나온 6개 단어 체크

    for i in top_counts:
        x_list.append(i[0])
        y_list.append(int(i[1]))

    return x_list, y_list

#mysql 쿼리 chart데이터 가져오기
def mysql_chart_data(db_name):

    content_list = []

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT answer FROM %s ORDER BY id DESC LIMIT 1;" %db_name)
        result = cursor.fetchall()
        connection.commit()
        connection.close()
    except:
        connection.rollback()
        print("Failed Selecting in StockList")

    for entry in result:
        content_list.append(entry[0])

    return content_list

#쿼리 받아온 데이터 문자열로 바꾸기
def listToString(str_list):
    result = ""
    for s in str_list:
        result += s + " "
    return result.strip()