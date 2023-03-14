import os
import urllib.parse

from prefect import task, flow, get_run_logger
import requests
import mysql.connector

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from bs4 import BeautifulSoup
import encapsulated

now = datetime.now()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}

logger = get_run_logger()


@task(name="log-example-task", log_prints=True)
def example():
    logger.info("hello")


@task(name='scraping-news-title', log_prints=True)
def scraping_google_news_title():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    service = Service(executable_path=ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.implicitly_wait(10)  # 웹 페이지가 로딩 될 때까지 10초는 기다림

    driver.maximize_window()  # 화면 최대화
    keyword = 'it 정책'
    last_page = 10
    for i in range(0, int(last_page) * 10, 10):
        driver.get(
            f"https://www.google.com/search?q={keyword}&tbm=nws&ei=Rl-PY9_4O8qCoASVqJCIDQ&"
            f"start={i}&sa=N&ved=2ahUKEwjfs8P8puX7AhVKAYgKHRUUBNE4HhDy0wN6BAgBEAQ&biw=1536&bih=708&dpr=1.25")
    names = driver.find_elements(By.CSS_SELECTOR, ".mCBkyc")
    links = driver.find_elements(By.CSS_SELECTOR, '.WlydOe')
    date = driver.find_elements(By.CSS_SELECTOR, '.OSrXXb')
    if '일 전' in date:
        pass
    else:
        real_date = now.date()
        pass
        # TODO: SQL에 저장하기


@task(name='scraping-naver-news', log_prints=True)
def scraping_naver_news_title():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(3)

    search_urls, searched_pages_number, keyword = encapsulated.make_certain_url()
    logger.info(f'fetching {searched_pages_number} pages of the searched result in keyword: {keyword}')
    naver_urls = encapsulated.get_naver_news_urls(headers, driver, search_urls)
    news_titles = list()
    summaries = list()
    contents = list()
    written_time = list()

    # TODO: Need to work on mapping
    for news_link in naver_urls:
        title, summary, content, recorded_time = encapsulated.get_naver_news_title_and_content(headers, news_link)
        news_titles.append(title)
        summaries.append(summary)
        contents.append(content)
        written_time.append(recorded_time)

    news_data = {'time': written_time, 'urls': naver_urls, 'news_title': news_titles, 'summary_from_news': summaries}
    news_content = {'news_title': news_titles, 'content': contents}
    return news_data, news_content


@task(log_prints=True, name='store_data1')
def store_news_data_without_content(news_data):
    connection = mysql.connector.connect(
        host = os.getenv('DATABASE_HOST', 'database'),
        user = os.getenv('DATABASE_USER', 'root'),
        password = os.getenv('DATABASE_PASSWORD', 'mariadb'),
        database = os.getenv('DATABASE_SCHEMA', 'internet_news'),
    )
    cursor = connection.cursor()
    sql = 'insert into conversations(written_date, title, news_summary, url) values (%s, %s, %s, %s)'
    logger.info('inserting naver news data')
    cursor.executemany(sql, news_data)
    connection.commit()


@task(log_prints=True, name='summarizing article')
def summarize_article(news_content):
    pass


@task(log_prints=True, name='store_data2')
def store_summarized_news_data(ai_summary):
    connection = mysql.connector.connect(
        host = os.getenv('DATABASE_HOST', 'database'),
        user = os.getenv('DATABASE_USER', 'root'),
        password = os.getenv('DATABASE_PASSWORD', 'mariadb'),
        database = os.getenv('DATABASE_SCHEMA', 'internet_news'),
    )
    cursor = connection.cursor()
    sql = 'insert into conversations(title, ai_summary) values (%s, %s)'
    logger.info('inserting ai summarized news data')
    cursor.executemany(sql, ai_summary)
    connection.commit()


@flow(name="log-example-flow", log_prints=True)
def logger_flow():
    news_data, news_contents = scraping_naver_news_title()
    store_news_data_without_content(news_data)


if __name__ == '__main__':
    logger_flow()

