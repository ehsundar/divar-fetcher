drop trigger if exists posts_update_updated_at on posts;
drop function if exists posts_updated_at;
alter table posts
    drop created_at,
    drop updated_at;
