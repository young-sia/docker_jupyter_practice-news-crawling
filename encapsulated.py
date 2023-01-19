from bs4 import BeautifulSoup
import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)


def make_page_num(num):
    if num == 1:
        return num
    elif num == 0:
        return num+1
    else:
        return num+9*(num-1)


def make_url(search, start_pg, end_pg):
    if start_pg == end_pg:
        start_page = make_page_num(start_pg)
        url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(start_page)
        print("생성url: ", url)
        return url
    else:
        urls = []
        for i in range(start_pg, end_pg+1):
            page = make_page_num(i)
            url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(page)
            urls.append(url)
        print("생성url: ", urls)

        return urls


def make_certain_url():
    search = 'it정책'
    # 검색 시작할 페이지 입력
    page = 1  # ex)1 =1페이지,2=2페이지...
    # 검색 종료할 페이지 입력
    page2 = 2

    # naver url 생성
    search_urls = make_url(search, page, page2)

    return search_urls


def get_naver_news_urls(headers, driver, search_urls):
    naver_urls = list()

    for i in search_urls:
        driver.get(i)
        time.sleep(1)  # 대기시간 변경 가능
        original_html = requests.get(i, headers = headers)
        # html = BeautifulSoup(original_html.text, "html.parser")
        news_urls = driver.find_elements(By.CSS_SELECTOR, 'a.info')

        # 네이버 기사 눌러서 제목 및 본문 가져오기#
        # 네이버 기사가 있는 기사 css selector 모아오기
        # news_urls = driver.find_elements(By.CSS_SELECTOR, 'news. info')
        print(f'look into news.info page: {i}')

        # 위에서 생성한 css selector list 하나씩 클릭하여 본문 url얻기
        for click in news_urls:
            click.click()

            # 현재 탭에 접근
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3)  # 대기시간 변경 가능

            # 네이버 뉴스 url만 가져오기

            url = driver.current_url
            # print(url)

            if "news.naver.com" in url:
                naver_urls.append(url)
            else:
                pass

            # 현재 탭 닫기
            driver.close()

            # 다시처음 탭으로 돌아가기
            driver.switch_to.window(driver.window_handles[0])
        print(f'all successful {len(naver_urls)}')
    # print(naver_urls)

    return naver_urls


def get_naver_news_title_and_content(headers, naver_url):
    original_html = requests.get(naver_url, headers=headers)
    html = BeautifulSoup(original_html.text, "html.parser")

    # 검색결과확인시
    # print(html)

    # 뉴스 제목 가져오기
    news_title = html.select("#title_area > span")
    # list합치기
    news_title = ''.join(str(news_title))
    # html태그제거
    pattern1 = '<[^>]*>'
    news_title = re.sub(pattern = pattern1, repl = '', string = news_title)

    # 요약내용
    summary = html.select("#dic_area > div > div")
    # 기사 텍스트만 가져오기
    # list합치기
    summary = ''.join(str(summary))
    summary = re.sub(pattern = pattern1, repl = '', string = summary)
    pattern2 = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""
    summary = summary.replace(pattern2, '')

    # 뉴스 본문 가져오기
    content = html.select("#newsct_article")
    # 기사 텍스트만 가져오기
    # list합치기
    content = ''.join(str(content))

    # html태그제거 및 텍스트 다듬기
    content = re.sub(pattern = pattern1, repl = '', string = content)
    pattern2 = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""
    content = content.replace(pattern2, '')

    news_record_time = html.select_one('#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > '
                                       'div.media_end_head_info_datestamp > div:nth-child(1) > span').text

    print(news_record_time)

    return news_title, summary, content, news_record_time


def main():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(3)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}

    search_urls = make_certain_url()
    print('made certain urls')
    naver_urls = get_naver_news_urls(headers, driver, search_urls)

    # 시험용
    # naver_urls = ['https://n.news.naver.com/mnews/article/003/0011648494?sid=101',
    # 'https://n.news.naver.com/mnews/article/015/0004801565?sid=105']

    titles = list()
    summaries = list()
    contents = list()
    written_time = list()
    for news_link in naver_urls:
        title, summary, content, recorded_time = get_naver_news_title_and_content(headers, news_link)
        titles.append(title)
        summaries.append(summary)
        contents.append(content)
        written_time.append(recorded_time)

    print(titles)
    print(summaries)
    print(contents)
    print(written_time)


if __name__ == '__main__':
    main()
