# my_settings.py

DATABASES = {
    'default':{
        # 1. 사용할 엔진 설정
        'ENGINE' : 'django.db.backends.mysql',
        # 2. 연동할 MySQL의 데이터베이스 이름
        'NAME' : 'django_db',
        # 3. DB 접속 계정명
        'USER' : 'root',
        # 4. DB 패스워드
        'PASSWORD' : '1234',
        # 5. DB 주소
        'HOST' : 'localhost',
        # 6. 포트번호
        'PORT' : '3306',
    }
}
SECRET_KEY = 'django-insecure-6y%jq4263yjvkcgu6s(amp9!j)$po9dpk^x@$x(())vpd2e#zg'
