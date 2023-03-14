CREATE TABLE naver_news(
    id bigint auto_increment PRIMARY KEY,
    written_date DATE,
    title varchar(512),
    news_summary varchar(512),
    url varchar(512)
);

CREATE TABLE ai_summarized_news(
    id bigint auto_increment PRIMARY KEY,
    title varchar(512),
    ai_summary varchar(512) ,
);
