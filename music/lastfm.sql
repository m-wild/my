create table if not exists music_scrobbles (
    date        datetime not null,
    artist      text     not null,
    artist_mbid text     null,
    album       text     null,
    album_mbid  text     null,
    track       text     not null,
    track_mbid  text     null
);

-- remove duplicate scrobbles
delete from music_scrobbles 
where rowid in
(
    select rowid
    from music_scrobbles
    group by date, artist, album, track
    having count(1) > 1
);


select max(date) from music_scrobbles

select datetime(date, 'unixepoch', 'localtime') as date, artist, album, track
from music_scrobbles
order by date asc;

select count(1) from music_scrobbles;

select artist, count(1)
from music_scrobbles
group by artist
order by count(1) desc
limit 10;

