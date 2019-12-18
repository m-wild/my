-- drop table music_scrobbles;
create table if not exists music_scrobbles (
    date        datetime not null,
    artist      text     not null,
    artist_mbid text     null,
    album       text     null,
    album_mbid  text     null,
    track       text     not null,
    track_mbid  text     null
);

-- this can only be unique where date > 0 due to bad data from last.fm
-- prevents us from having a pkey on the table
create unique index uq_music_scrobbles on music_scrobbles (date, artist, album, track) where (date > 0);

-- normalize bad dates
update music_scrobbles set date = 0
where date(date, 'unixepoch') = '1970-01-01';

-- remove duplicate scrobbles
delete from music_scrobbles 
where rowid in
(
    select rowid
    from music_scrobbles
    where date > 0
    group by date, artist, album, track
    having count(1) > 1
);

-- null out empty strings
update music_scrobbles set track_mbid = null where nullif(track_mbid, '') is null;
update music_scrobbles set album_mbid = null where nullif(album_mbid, '') is null;
update music_scrobbles set artist_mbid = null where nullif(artist_mbid, '') is null;


select *
from music_scrobbles
order by date desc ;


select max(date) from music_scrobbles;

select datetime(date, 'unixepoch', 'localtime') as date, artist, album, track
from music_scrobbles
where date > 0
order by date desc;

select count(1) from music_scrobbles;

select artist, count(1)
from music_scrobbles
group by artist
order by count(1) desc
limit 10;


select artist, count(1)
from music_scrobbles
where strftime('%Y', date, 'unixepoch') = '2019'
group by artist
order by count(1) desc
limit 10;

