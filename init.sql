CREATE TABLE google_news(
    id bigint auto_increment PRIMARY KEY,
    dates DATE,
    title varchar(512),
    content ,
);

CREATE TABLE summary_news(
    id bigint auto_increment PRIMARY KEY,
    dates DATE,
    title varchar(512),
    summary varchar(512) ,
);
