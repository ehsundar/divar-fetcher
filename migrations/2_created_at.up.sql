alter table posts
    add created_at timestamp default now(),
    add updated_at timestamp default current_timestamp;

create or replace function posts_updated_at()
    returns trigger as
$$
begin
    new.updated_at = now();
    return new;
end;
$$ language 'plpgsql';

create trigger posts_update_updated_at
    before update
    on posts
    for each row
execute procedure posts_updated_at();
