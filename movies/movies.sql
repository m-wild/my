------------------- diary ------------------- 
-- drop table movies_diary;
create table movies_diary (
    date    datetime not null,
    name    text     not null,
    year    int      not null,
    rating  numeric  not null,
    rewatch boolean  not null default false,
    primary key (date, name, year)
);

-- import process:
-- sqlite> .mode csv
-- sqlite> .import C:/users/wilds/Downloads/letterboxd-tehmantra-2019-12-18-06-59-utc/diary.csv movies_diary_staging
select * from movies_diary_staging;

-- copy staging to main table
insert or ignore into movies_diary 
    (date, name, year, rating, rewatch)
select 
       strftime('%s', "Watched Date"),
       Name,
       Year,
       Rating,
       case when Rewatch = 'Yes' then 1 else 0 end
from movies_diary_staging;
drop table movies_diary_staging;

------------------- ratings -------------------
-- drop table movies_ratings;
create table movies_ratings (
    name   text     not null,
    year   int      not null,
    uri    text     not null,
    rating numeric  not null,
    primary key (name, year)
);

-- import process:
-- sqlite> .mode csv
-- sqlite> .import C:/users/wilds/Downloads/letterboxd-tehmantra-2019-12-18-06-59-utc/ratings.csv movies_ratings_staging
select * from movies_ratings_staging;

-- copy staging to main table
insert or replace into movies_ratings
    (name, year, uri, rating)
select
    Name, Year, "Letterboxd URI", Rating
from movies_ratings_staging;
drop table movies_ratings_staging;




------------------- visualisation -------------------


select 
    date(date, 'unixepoch') as date,
    name, year, rating, rewatch
from movies_diary;


select *
from movies_ratings
order by rating desc;

