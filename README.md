# NHNProject
nhn 사전 과제

# Install
- [Python 3.10.6](https://www.python.org/downloads/release/python-3106/)
- [SQLite3](https://sqlitebrowser.org/dl/) (SQLite GUI 도구이므로 필수 설치x)

# Requirements
```bash
$ pip list
Package              Version
-------------------- -----------
beautifulsoup4       4.11.1
Django               4.1.5
djangorestframework  3.14.0
lxml                 4.9.2
mysqlclient          2.1.1
pip                  22.3.1
pytz                 2022.7.1
requests             2.28.2
selenium             4.7.2
webdriver-manager    3.8.5
```

# Project Setup
```bash
# 파이썬 설치 필수

# git clone
$ git clone https://github.com/jihye0420/NHNProject.git

# 가상환경 생성
$ cd NHNProject
$ python -m venv .venv

# 가상환경 활성화
$ source .venv/bin/activate  # 맥
$ source .venv/Scripts/activate  # 윈도우

# Then install the dependencies
$ (.venv)$ pip install -r requirements.txt

# Django settings
(.venv)$ python manage.py makemigrations
(.venv)$ python manage.py migrate

# 크롤링 시작
(.venv)$ python crawling.py

# API 호출
(.venv)$ python manage.py runserver
```

# 입력 및 출력 예시
### 입력 : [http://127.0.0.1:8000/group/10](http://127.0.0.1:8000/group/10)
### 출력 :  json

```json
[
    {
        "url": "http://school.iamservice.net/articles/view/135964035",
        "title": "2023학년도 교과서 목록",
        "published_datetime": "2023-01-12T15:00:00Z",
        "body": "<p style=\"text-align: left;\">2023학년도 교과서 목록입니다. </p>",
        "attachment_list": [
            "2023학년도 교과서목록.xls"
        ]
    },

		...
]
```

![image](https://user-images.githubusercontent.com/50284754/213923980-4ce5cb71-abb8-4b72-ba22-b592efe5ce3f.png)

![image](https://user-images.githubusercontent.com/50284754/213923989-a3b7f841-763e-4731-b762-c8c2f49649ac.png)

# 설명

1. 크롬 드라이버 설정 ⇒ 설치하지 않아도 되는 코드를 작성했다.
    
    ```python
    def get_driver():
        # 구글은 분당 4회이상 접근 허용하지 않기 때문에 sleep을 길게 준다.
        # time.sleep(2)
    
        chrome_options = Options()
        # chrome_options.add_argument("headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver
    ```
    
2. 중복 데이터를 확인하는 로직 설정
    
    ```python
    def insert_data_db(category, crawled_data_list):
        # item = crawled_data_list[0]
        for item in crawled_data_list:
            print("item", item)
            if Post.objects.filter(category=category, url=item['url'], title=item['title']).exists():
                print('중복')
                print(Post.objects.filter(category=category, url=item['url'], title=item['title']).first())
                continue
            else:
                print('insert')
                Post(url=item['url'],
                     title=item['title'],
                     published_datetime=item['published_datetime'],
                     body=str(item['body']),
                     attachment_list=",".join(item['attachment_list']),
                     category=category).save()
        return
    ```
    
3. 크롤링 timezone 설정 로직 추가 ⇒ UTC 기준으로 insert되도록 설정했다.
    
    ```python
    def convert_to_date_utc(category, pub_date):
        if type(pub_date) == str:
            if category == 'iam_school':
                pub_date = datetime.strptime(pub_date, '%Y.%m.%d')  # 문자열을 출력
                kst = pytz.timezone('Asia/Seoul')
                kst_time = kst.localize(pub_date)
                pub_date = kst_time.astimezone(pytz.utc)
            elif category == 'naver_blog':
                pub_date = datetime.strptime(pub_date, '%Y. %m. %d. %H:%M')  # 문자열을 출력
                kst = pytz.timezone('Asia/Seoul')
                kst_time = kst.localize(pub_date)
                pub_date = kst_time.astimezone(pytz.utc)
            elif category == 'bbc_news':
                pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
                utc = pytz.timezone('UTC')
                pub_date = utc.localize(pub_date)
        return pub_date
    ```
    
4. DB 구조 설정
![image](https://user-images.githubusercontent.com/50284754/214227556-17153733-10d8-4211-ae8d-0134c3c1798c.png)
