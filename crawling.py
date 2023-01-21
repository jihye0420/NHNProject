import os
import ssl
import traceback
import urllib.parse
import urllib.request
import re
from datetime import datetime, timedelta

# from pytz import timezone
import pytz
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()
from nhn.models import Post

# 파일 쓰기 (print문)
import sys
sys.stdout = open('stdout.txt', 'w', encoding='utf-8')


def convert_to_date_utc(category, pub_date):
    if type(pub_date) == str:
        if category == 'iam_school':
            pub_date = datetime.strptime(pub_date, '%Y.%m.%d') # 문자열을 출력
            print('before', pub_date)
            # # Set the time zone for KST
            # kst = pytz.timezone('Asia/Seoul')

            # Convert the KST datetime to UTC
            pub_date = pub_date.astimezone(pytz.utc)

            print('after', pub_date)
            print(type(pub_date))
        elif category=='naver_blog':
            pub_date = datetime.strptime(pub_date, '%Y. %m. %d. %H:%M') # 문자열을 출력
            print('before', pub_date)
            pub_date = pub_date.astimezone(tz=pytz.utc)
            print('after', pub_date)
            print(type(pub_date))
            pass
        elif category == 'bbc_news':
            pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S GMT')
            print('after', pub_date)
    # utc = kst - timedelta(hours=9)
    return pub_date



def get_driver():
    # 구글은 분당 4회이상 접근 허용하지 않기 때문에 sleep을 길게 준다.
    # time.sleep(100)

    # local chrome path
    # path = "/usr/share/AISpera/merge_crawler/chromedriver"  # >> 나의 로컬 환경:/homejhhwang/updateWork/PIT/chromedriver vs 서버 환경:/usr/share/AISpera/google_news/chromedriver"
    driver = webdriver.Chrome()
    return driver


# 아이엠스쿨 기관 프로필 크롤링 완료
def crawling_iam_school(iam_school_url):
    result = []
    post_links = [] # 각 url 리스트
    # url = 'https://school.iamservice.net/organization/1674/group/2001892'
    url = iam_school_url

    # # bs으로는 파싱이 안되는 html 코드
    # response = requests.get(url)
    # html = response.text
    # soup = BeautifulSoup(html, 'lxml')
    # links = soup.find_all('a', attrs={'class':'btn_detail'}) # a 요소 태그 다 추출
    # print(links)

    try:
        driver = get_driver()
        driver.get(url)
        driver.implicitly_wait(5) # 5초간 waiting
        soup = BeautifulSoup(driver.page_source, 'lxml')
        # print(soup)
        # print("=============================================================")
        posts = soup.find_all('div', attrs={'class':'bx_cont'}) # a 요소 태그 다 추출
        links = soup.find_all('a', attrs={'class':'btn_detail'}) # a 요소 태그 다 추출

        for post in posts:
            post_one_dict = {}
            post_one_dict['title'] = post.find('h4', attrs={'class': 'tit_cont'}).get_text()
            post_one_dict['body'] = post.find('p', attrs={'class': 'desc'})
            post_one_dict['url'] = post.find('a', attrs={'class': 'btn_detail'})['href']
            post_one_dict['published_date'] = convert_to_date_utc('iam_school', post.find('p', attrs={'class': 'txt_date type'}).find_all('span')[-1].get_text())
            files = post.find_all('span', attrs={'class': 'name'})
            post_one_dict['attatched_file_title'] = []
            # print(post_one_dict['attatched_file_title'])
            for f in files:
                f = f.get_text()
                post_one_dict['attatched_file_title'].append(f)
            # print(post_one_dict['attatched_file_title'])
            result.append(post_one_dict)

        for i in result:
            print("i: ", i)
        print(result)

    except Exception as ex:
        print("driver error: ", ex)
        print(traceback.format_exc())  # 에러스택 정보를 string으로 변환


    # url = 'https://school.iamservice.net/articles/view/135952777'

    # bs으로는 파싱이 안되는 html 코드
    # response = requests.get(url)
    # html = response.text
    # soup = BeautifulSoup(html, 'lxml')
    # # print(soup)
    # post_title = soup.find('div', attrs={'class': 'title'})
    # post_body = soup.find('div', attrs={'class': 'articleViewer'}).contents
    # print('post_title: ', post_title)
    # print('post_body: ', post_body)

    # driver = get_driver()
    # driver.get(url)
    # driver.implicitly_wait(5) # 5초간 waiting
    # soup = BeautifulSoup(driver.page_source, 'lxml')
    # post_title = soup.find('div', attrs={'class': 'title'})
    # post_body = soup.find('div', attrs={'class':'articleViewer'}).contents
    # print('post_title: ', post_title)
    # print('post_body: ', post_body)
    # post_file_name = soup.find('div', attrs={'class': 'title'})


def clean_text(text):
    text = text.replace("\n", " ")  # 공백 제거
    text = text.replace('\u200b', '')
    text = text.replace("\'", "\'")
    # text = re.sub(r"\'", "'", text)
    text = re.sub(r"â\x80¦", "...", text)
    # text = re.sub('[a-zA-Z]', '', text)
    # text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]','', text)
    return text


# 네이버 블로그 크롤링 완료
def crawling_naver_blog():
    result = []
    post_links = [] # 각 url 리스트
    url = 'https://blog.naver.com/PostList.nhn?blogId=sntjdska123&from=postList&categoryNo=51'

    try:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        posts = soup.find('ul', attrs={'class':'thumblist'}).find_all('li', attrs={'class':'item'})

        # url 링크
        for post in posts:
            post_links.append(post.find('a', attrs={'class': 'link pcol2'})['href'])
        # print(post_links)

        # 각 페이지 들어가서 반복할일!
        for post_url in post_links:
            url = 'https://blog.naver.com'+post_url
            response = requests.get(url)
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            post_one_dict = {}
            post_one_dict['title'] = soup.find('div', attrs={'class': 'pcol1'}).get_text().strip()

            # todo: 선택 0) html text
            body = soup.find('div', attrs={'class': 'se-main-container'}).get_text().strip()
            body = clean_text(body)
            # print(body)
            post_one_dict['body'] = body
            print("=============================================================================")


            # todo: 선택1) html 본문 전체
            # print("body: ", body)
            # post_one_dict['body'] = body
            # print("=============================================================================")


            # todo: 선택2) html 본문 text **
            # # post_text_pattern = re.compile(r'se-component se-text [\w]') # 대안
            # # body = soup.find('div', attrs={'class': 'se-main-container'}).find_all('div', attrs={'class': post_text_pattern}) # 대안
            # p_text_pattern = re.compile(r'se-text-paragraph [\w]') # **
            # body = soup.find('div', attrs={'class': 'se-main-container'}).find_all('p', attrs={'class': p_text_pattern}) # **
            #
            # temp_body = ''
            # for j in body:
            #     # print(j.contents[0].find(text=True))
            #     print(j.get_text())
            #     temp_body += j.get_text()
            #     temp_body = temp_body.replace('\u200b', '')
            #     post_one_dict['body'] = temp_body
            # print("=============================================================================")

            # todo: url 형태 맞추기
            post_one_dict['url'] = url
            post_one_dict['published_date'] = convert_to_date_utc('naver_blog', soup.find('span', attrs={'class': 'se_publishDate pcol2'}).get_text())

            # todo: 첨부파일이 있는 블로그 글 찾기
            # files = post.find_all('span', attrs={'class': 'name'})
            post_one_dict['attatched_file_title'] = []
            # for f in files:
            #     f = f.get_text()
            #     post_one_dict['attatched_file_title'].append(f)
            result.append(post_one_dict)

        for i in result:
            print("i: ", i)
            print('======================================================')
        print(result)
    except Exception as ex:
        print("driver error: ", ex)
        print(traceback.format_exc())  # 에러스택 정보를 string으로 변환


def crawling_news():
    result = []
    post_links = [] # 각 url 리스트
    url = 'http://feeds.bbci.co.uk/news/rss.xml'

    try:
        response = requests.get(url)
        page = response.text
        soup = BeautifulSoup(page, 'xml')
        # print(soup)
        posts = soup.find_all('item')
        # print(posts)

        # driver = get_driver()
        # driver.get(url)
        # driver.implicitly_wait(5)  # 5초간 waiting
        # soup = BeautifulSoup(driver.page_source, 'lxml')
        # posts = soup.find_all('div', attrs={'id': 'item'})
        # print(posts)
        # print("=============================================================")
        # posts = soup.find_all('div', attrs={'class': 'bx_cont'})  # a 요소 태그 다 추출
        # links = soup.find_all('a', attrs={'class': 'btn_detail'})  # a 요소 태그 다 추출

        for post in posts:
            post_one_dict = {}
            temp_body = ''

            post_one_dict['url'] = post.find('link').get_text()
            post_one_dict['title'] = post.find('title').get_text()
            post_one_dict['published_date'] = convert_to_date_utc('bbc_news' ,post.find('pubDate').get_text())
            # files = post.find_all('span', attrs={'class': 'name'})
            post_one_dict['attatched_file_title'] = []
            # for f in files:
            #     f = f.get_text()
            #     post_one_dict['attatched_file_title'].append(f)
            # # print(post_one_dict['attatched_file_title'])

            # post_links.append(post.find('link').get_text())
            response = requests.get(post_one_dict['url'])
            page = response.text
            soup = BeautifulSoup(page, 'lxml')
            print("Encoding method :", soup.original_encoding)

            body = soup.find('article').find_all('div', attrs={'data-component': 'text-block'})
            for b in body:
                temp_body += b.get_text()
            post_one_dict['body'] = clean_text(temp_body)
            result.append(post_one_dict)

        # for link in post_links:
        #     response = requests.get(link)
        #     page = response.text
        #     soup = BeautifulSoup(page, 'lxml')
        #     posts = soup.find('article').find_all('div', attrs={'data-component': 'text-block'})
        #     temp_body = ''
        #     for post in posts:
        #         temp_body += post.get_text()
        #     post_one_dict['body'] = temp_body
        #     # print(temp_body)
        #     # print(post_one_dict)

        for i in result:
            print("i: ", i)
            print('==========================================================================')
        print(result)
    except Exception as ex:
        print("driver error: ", ex)
        print(traceback.format_exc())  # 에러스택 정보를 string으로 변환


# def insert_data_db(crawled_data_list):
#     Post.objects.
#     return

if __name__ == '__main__':
    iam_school_list = ['https://school.iamservice.net/organization/1674/group/2001892', 'https://school.iamservice.net/organization/19710/group/2091428']
    for iam_school in iam_school_list:
        crawling_iam_school(iam_school)
    #
    # naver_blog_list = ['https://blog.naver.com/PostList.nhn?blogId=sntjdska123&from=postList&categoryNo=51']
    # crawling_naver_blog()

    # crawling_news()

    # todo: date time (timezone)
    # DB insert 하는 로직 (중복 방지)