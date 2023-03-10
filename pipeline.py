import os
from prefect import task, flow, get_run_logger
import requests
import mysql.connector

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import encapsulated

now = datetime.now()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}


@task(name="log-example-task", log_prints=True)
def example():
    logger = get_run_logger()
    logger.info("hello")


@task(name='scraping-naver-news', log_prints=True)
def scraping_naver_news_title():
    logger = get_run_logger()
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(3)

    search_urls, searched_pages_number, keyword = encapsulated.make_certain_url()
    logger.info(f'fetching {searched_pages_number} pages of the searched result in keyword: {keyword}')
    # naver_urls = encapsulated.get_naver_news_urls(headers, driver, search_urls)
    naver_urls = ['https://n.news.naver.com/mnews/article/003/0011648494?sid=101',
                  'https://n.news.naver.com/mnews/article/015/0004801565?sid=105']
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

    news_data = {'written_date': written_time, 'url': naver_urls, 'title': news_titles, 'summary': summaries}
    news_content = {'news_title': news_titles, 'content': contents}
    return news_data, news_content


@task(log_prints=True, name='store_data1')
def store_news_data_without_content(news_data):
    logger = get_run_logger()
    connection = mysql.connector.connect(
        host = os.getenv('DATABASE_HOST', 'database'),
        user = os.getenv('DATABASE_USER', 'root'),
        password = os.getenv('DATABASE_PASSWORD', 'mariadb'),
        database = os.getenv('DATABASE_SCHEMA', 'naver_news'),
    )
    cursor = connection.cursor()
    sql = 'insert into naver_news(written_date, title, news_summary, url) values (%s, %s, %s, %s)'
    logger.info('inserting naver news data')
    records = []
    for count in range(len(news_data['title'])):
        records.append((
            news_data['written_date'][count],
            news_data['title'][count],
            news_data['summary'][count],
            news_data['url'][count]

        ))
    cursor.executemany(sql, records)
    connection.commit()


@task(log_prints=True, name='summarizing article')
def summarize_article(news_content):
    pass


@task(log_prints=True, name='store_data2')
def store_summarized_news_data(ai_summary):
    logger = get_run_logger()
    connection = mysql.connector.connect(
        host = os.getenv('DATABASE_HOST', 'database'),
        user = os.getenv('DATABASE_USER', 'root'),
        password = os.getenv('DATABASE_PASSWORD', 'mariadb'),
        database = os.getenv('DATABASE_SCHEMA', 'ai_summarized_news'),
    )
    cursor = connection.cursor()
    sql = 'insert into ai_summarized_news(title, ai_summary) values (%s, %s)'
    logger.info('inserting ai summarized news data')
    cursor.executemany(sql, ai_summary)
    connection.commit()


@flow(name="my-flow", log_prints=True)
def logger_flow():
    logger = get_run_logger()
    logger.info('start scraping')
    news_data, news_contents = scraping_naver_news_title()
    store_news_data_without_content(news_data)


if __name__ == '__main__':
    logger_flow()

