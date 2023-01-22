import os
import re
import time
import traceback
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from nhn.models import Post

# 파일 쓰기 (print문)
import sys

sys.stdout = open('stdout.txt', 'w', encoding='utf-8')


# todo: 데이터 검증 작업 확인
# todo: body 데이터 검증 확인
# db insert 확인
# 출력문 확인
# 리드미 작성
# 한번 실행해보기

def convert_to_date_utc(category, pub_date):
    if type(pub_date) == str:
        if category == 'iam_school':
            pub_date = datetime.strptime(pub_date, '%Y.%m.%d')  # 문자열을 출력
            print('pub_date: ', pub_date)
            kst = pytz.timezone('Asia/Seoul')
            kst_time = kst.localize(pub_date)
            pub_date = kst_time.astimezone(pytz.utc)
            print('after: ', pub_date)
        elif category == 'naver_blog':
            pub_date = datetime.strptime(pub_date, '%Y. %m. %d. %H:%M')  # 문자열을 출력
            print('pub_date: ', pub_date)
            kst = pytz.timezone('Asia/Seoul')
            kst_time = kst.localize(pub_date)
            pub_date = kst_time.astimezone(pytz.utc)
            print('after: ', pub_date)
        elif category == 'bbc_news':
            pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
            print('pub_date: ', pub_date)
            utc = pytz.timezone('UTC')
            pub_date = utc.localize(pub_date)
            # pub_date = pub_date.replace(tz=pytz.utc)
            print('after: ', pub_date)
    return pub_date


def clean_text(text):
    text = text.replace("\n", "")  # 공백 제거
    text = text.replace('\u200b', '')
    text = text.replace("\'", "'")
    # text = re.sub(r"\'", "'", text)
    text = re.sub(r"â\x80¦", "...", text)
    # text = re.sub('[a-zA-Z]', '', text)
    # text = re.sub('[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]','', text)
    return text


def get_driver():
    # 구글은 분당 4회이상 접근 허용하지 않기 때문에 sleep을 길게 준다.
    # time.sleep(2)

    # local chrome path
    # path = "/usr/share/AISpera/merge_crawler/chromedriver"  # >> 나의 로컬 환경:/homejhhwang/updateWork/PIT/chromedriver vs 서버 환경:/usr/share/AISpera/google_news/chromedriver"
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


# 아이엠스쿨 기관 프로필 크롤링 완료
def crawling_iam_school(iam_school_url):
    result = []
    url = iam_school_url

    # # bs으로는 파싱이 안되는 html 코드
    # response = requests.get(url)
    # html = response.text
    # soup = BeautifulSoup(html, 'lxml')
    # links = soup.find_all('a', attrs={'class':'btn_detail'}) # a 요소 태그 다 추출
    # print(links)

    try:
        driver = get_driver()
        driver.implicitly_wait(5)  # 5초간 waiting
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        posts = soup.find_all('div', attrs={'class': 'bx_cont'})  # a 요소 태그 다 추출

        for post in posts:
            post_one_dict = {}
            post_one_dict['title'] = post.find('h4', attrs={'class': 'tit_cont'}).get_text()
            # post_one_dict['body'] = post.find('p', attrs={'class': 'desc'})
            post_one_dict['url'] = post.find('a', attrs={'class': 'btn_detail'})['href']
            post_one_dict['published_datetime'] = convert_to_date_utc('iam_school', post.find('p', attrs={
                'class': 'txt_date type'}).find_all('span')[-1].get_text())
            post_one_dict['attachment_list'] = []
            files = post.find_all('span', attrs={'class': 'name'})
            for f in files:
                f = f.get_text()
                post_one_dict['attachment_list'].append(f)
            driver.get(post_one_dict['url'])
            soup = BeautifulSoup(driver.page_source, 'lxml')
            body = soup.find('div', attrs={'class': 'articleViewer'}).find_all('p')
            temp_body = ''
            for j in body:
                temp_body += str(j)
            post_one_dict['body'] = temp_body
            result.append(post_one_dict)

        # for i in result:
        #     print("i: ", i)
        return result
    except Exception as ex:
        print("error: ", ex)
        print(traceback.format_exc())  # 에러스택 정보를 string으로 변환
        return None


# 네이버 블로그 크롤링 완료
def crawling_naver_blog(naver_blog_url):
    result = []
    post_links = []  # 각 url 리스트
    url = naver_blog_url

    try:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        posts = soup.find('ul', attrs={'class': 'thumblist'}).find_all('li', attrs={'class': 'item'})

        # url 링크
        for post in posts:
            post_links.append(post.find('a', attrs={'class': 'link pcol2'})['href'])

        # 각 페이지 들어가서 반복할일!
        for post_url in post_links:
            url = 'https://blog.naver.com' + post_url
            response = requests.get(url)
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            post_one_dict = {}
            post_one_dict['title'] = soup.find('div', attrs={'class': 'pcol1'}).get_text().strip()

            # todo: 선택 0) html text **
            # body = soup.find('div', attrs={'class': 'se-main-container'}).get_text().strip()
            # body = clean_text(body)
            # post_one_dict['body'] = body

            # todo: 선택1) html 본문 전체
            # print("body: ", body)
            # post_one_dict['body'] = body
            # print("=============================================================================")

            # todo: 선택2) html 본문 text **
            p_text_pattern = re.compile(r'se-text-paragraph [\w]')  # **
            body = soup.find('div', attrs={'class': 'se-main-container'}).find_all('p', attrs={
                'class': p_text_pattern})  # **
            temp_body = ''
            for j in body:
                if j.get_text() == '\u200b':
                    continue
                else:
                    temp_body += str(j.contents[0])
            post_one_dict['body'] = temp_body

            post_one_dict['url'] = url
            post_one_dict['published_datetime'] = convert_to_date_utc('naver_blog', soup.find('span', attrs={
                'class': 'se_publishDate pcol2'}).get_text())

            # todo: 첨부파일이 있는 블로그 글 찾기
            post_one_dict['attachment_list'] = []
            # files = post.find_all('span', attrs={'class': 'name'})
            # for f in files:
            #     f = f.get_text()
            #     post_one_dict['attachment_list'].append(f)
            result.append(post_one_dict)

        # for i in result:
        #     print("i: ", i)
        return result
    except Exception as ex:
        print("error: ", ex)
        print(traceback.format_exc())  # 에러스택 정보를 string으로 변환
        return None


# bbc 뉴스 홈페이지 크롤링 완료
def crawling_news(news_url):
    result = []
    url = news_url

    try:
        response = requests.get(url)
        page = response.text
        soup = BeautifulSoup(page, 'xml')
        posts = soup.find_all('item')

        for post in posts:
            post_one_dict = {}
            temp_body = ''

            post_one_dict['url'] = post.find('link').get_text()
            post_one_dict['title'] = post.find('title').get_text()
            post_one_dict['published_datetime'] = convert_to_date_utc('bbc_news', post.find('pubDate').get_text())
            post_one_dict['attachment_list'] = []
            # files = post.find_all('span', attrs={'class': 'name'})
            # for f in files:
            #     f = f.get_text()
            #     post_one_dict['attachment_list'].append(f)
            # # print(post_one_dict['attachment_list'])
            response = requests.get(post_one_dict['url'])
            page = response.text
            soup = BeautifulSoup(page, 'lxml')
            body = soup.find('article').find_all('div', attrs={'data-component': 'text-block'})
            for j in body:
                temp_body += str(j.find('p'))
            # todo: text만
            # for b in body:
            #     temp_body += b.get_text()
            post_one_dict['body'] = clean_text(temp_body)
            result.append(post_one_dict)
        # for i in result:
        #     # print("i: ", i)
        return result
    except Exception as ex:
        print("error: ", ex)
        print(traceback.format_exc())  # 에러스택 정보를 string으로 변환
        return None


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


if __name__ == '__main__':
    # iam_school_list = ['https://school.iamservice.net/organization/1674/group/2001892',
    #                    'https://school.iamservice.net/organization/19710/group/2091428']
    # # iam_school_list = ['https://school.iamservice.net/organization/1674/group/2001892']
    # for iam_school in iam_school_list:
    #     print("시작")
    #     # crawling_iam_school(iam_school)
    #     insert_data_db(category=iam_school, crawled_data_list=crawling_iam_school(iam_school))
    # 
    # naver_blog_list = ['https://blog.naver.com/PostList.nhn?blogId=sntjdska123&from=postList&categoryNo=51',
    #                    'https://blog.naver.com/PostList.nhn?blogId=hellopolicy&from=postList&categoryNo=168']
    # # naver_blog_list = ['https://blog.naver.com/PostList.nhn?blogId=sntjdska123&from=postList&categoryNo=51']
    # for naver_blog in naver_blog_list:
    #     print("시작")
    #     # crawling_naver_blog(naver_blog)
    #     insert_data_db(category=naver_blog, crawled_data_list=crawling_naver_blog(naver_blog))
    # 
    # news_url = 'http://feeds.bbci.co.uk/news/rss.xml'
    # # crawling_news(news_url)
    # insert_data_db(category=news_url, crawled_data_list=crawling_news(news_url))

    # 전체 크롤링
    crawling_url_list = [
        'https://school.iamservice.net/organization/1674/group/2001892',
        'https://school.iamservice.net/organization/19710/group/2091428',
        'https://blog.naver.com/PostList.nhn?blogId=sntjdska123&from=postList&categoryNo=51',
        'https://blog.naver.com/PostList.nhn?blogId=hellopolicy&from=postList&categoryNo=168',
        'http://feeds.bbci.co.uk/news/rss.xml',
    ]
    retry_crawling_url = []
    for crawling_url in crawling_url_list:
        print("시작")
        if 'iamservice' in crawling_url:
            result_list = crawling_iam_school(crawling_url)
            print(result_list)
        elif 'naver' in crawling_url:
            result_list = crawling_naver_blog(crawling_url)
            print(result_list)
        elif 'bbci' in crawling_url:
            result_list = crawling_news(crawling_url)
            print(result_list)
        insert_data_db(category=crawling_url, crawled_data_list=result_list)
        time.sleep(1)
