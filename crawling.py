import os
import ssl
import traceback
import urllib.parse
import urllib.request
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
# def fetch_clien_latest_data():
#     result = []
#
#     url = 'https://www.clien.net/service/search/board/park?sk=title&sv=%EC%BF%A0%ED%8C%A1'
#     response = requests.get(url)
#     html = response.text
#     soup = BeautifulSoup(html, 'html.parser')
#
#     web_page_link_root = "https://clien.net"
#     list_items = soup.find_all("div", "list_item symph_row")
#
#     for item in list_items:
#         # title
#         title = item.find("span", "subject_fixed")["title"]
#
#         # link
#         page_link_raw = web_page_link_root + item.find("div", "list_title").find("a")["href"]
#         page_link_parts = urlparse(page_link_raw)
#         normalized_page_link = page_link_parts.scheme + '://' + page_link_parts.hostname + page_link_parts.path
#
#         # specific id
#         specific_id = page_link_parts.path.split('/')[-1]
#
#         item_obj = {
#             'title': title,
#             'link': normalized_page_link,
#             'specific_id': specific_id,
#         }
#
#         print(title)
#         result.append(item_obj)
#
#     return result
#
# def add_new_items(crawled_items):
#     last_inserted_items = BoardData.objects.last()
#     if last_inserted_items is None:
#         last_inserted_specific_id = ""
#     else:
#         last_inserted_specific_id = getattr(last_inserted_items, 'specific_id')
#
#     items_to_insert_into_db = []
#     for item in crawled_items:
#         if item['specific_id'] == last_inserted_specific_id:
#             break
#         items_to_insert_into_db.append(item)
#     items_to_insert_into_db.reverse()
#
#     for item in items_to_insert_into_db:
#         print("new item added!! : " + item['title'])
#
#         BoardData(specific_id=item['specific_id'],
#                   title=item['title'],
#                   link=item['link']).save()
#
#     return items_to_insert_into_db
#
#
# if __name__ == '__main__':
#     add_new_items(fetch_clien_latest_data())


# def getRecipeCrawler(element):
#     baseUrl = 'https://haemukja.com/recipes?sort=rlv&name='
#     url = baseUrl + urllib.parse.quote_plus(element)
#     html = urllib.request.urlopen(url, context=ssl._create_unverified_context()).read()
#     soup = BeautifulSoup(html, 'html.parser')
#
#     result = []
#     i = 0
#     for anchor in soup.select('a.call_recipe > strong'):
#         print(anchor.get_text())
#         i += 1
#
#         recipe_obj = {
#             'recipe_ID': i,
#             'recipe_Name': anchor.get_text(),
#             'ingredient_Key': element
#         }
#
#         result.append(recipe_obj)
#
#     return result
#
#
# # insert data into sqlite
# if __name__ == '__main__':
#     recipe_data = getRecipeCrawler("당근")
#     for item in recipe_data:
#         Search_Recipe(recipe_ID=item['recipe_ID'], recipe_Name=item['recipe_Name'],
#                       ingredient_Key=item['ingredient_Key']).save()

def get_driver():
    # 구글은 분당 4회이상 접근 허용하지 않기 때문에 sleep을 길게 준다.
    # time.sleep(100)

    # local chrome path
    # path = "/usr/share/AISpera/merge_crawler/chromedriver"  # >> 나의 로컬 환경:/homejhhwang/updateWork/PIT/chromedriver vs 서버 환경:/usr/share/AISpera/google_news/chromedriver"
    driver = webdriver.Chrome()
    return driver


def crawling_iam_school():
    result = []
    post_links = [] # 각 url 리스트
    url = 'https://school.iamservice.net/organization/1674/group/2001892'

    # # bs으로는 파싱이 안되는 html 코드
    # response = requests.get(url)
    # html = response.text
    # soup = BeautifulSoup(html, 'html.parser')
    # links = soup.find_all('a', attrs={'class':'btn_detail'}) # a 요소 태그 다 추출
    # print(links)

    try:
        driver = get_driver()
        driver.get(url)
        driver.implicitly_wait(5) # 5초간 waiting
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # print(soup)
        # print("=============================================================")
        posts = soup.find_all('div', attrs={'class':'bx_cont'}) # a 요소 태그 다 추출
        links = soup.find_all('a', attrs={'class':'btn_detail'}) # a 요소 태그 다 추출

        for post in posts:
            post_one_dict = {}
            post_one_dict['title'] = post.find('h4', attrs={'class': 'tit_cont'}).get_text()
            post_one_dict['body'] = post.find('p', attrs={'class': 'desc'})
            post_one_dict['url'] = post.find('a', attrs={'class': 'btn_detail'})['href']
            post_one_dict['published_date'] = post.find('p', attrs={'class': 'txt_date type'}).find_all('span')[-1].get_text()
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
    # soup = BeautifulSoup(html, 'html.parser')
    # # print(soup)
    # post_title = soup.find('div', attrs={'class': 'title'})
    # post_body = soup.find('div', attrs={'class': 'articleViewer'}).contents
    # print('post_title: ', post_title)
    # print('post_body: ', post_body)

    # driver = get_driver()
    # driver.get(url)
    # driver.implicitly_wait(5) # 5초간 waiting
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # post_title = soup.find('div', attrs={'class': 'title'})
    # post_body = soup.find('div', attrs={'class':'articleViewer'}).contents
    # print('post_title: ', post_title)
    # print('post_body: ', post_body)
    # post_file_name = soup.find('div', attrs={'class': 'title'})



if __name__ == '__main__':
    crawling_iam_school()
    # 크롤링하는 로직
    # driver 설정하는 로직
    # DB insert 하는 로직 (중복 방지)
    # timezone (time추가)