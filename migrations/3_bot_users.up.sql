create table if not exists users
(
    chat_id       int primary key,
    last_notified varchar(10) default null
);
insert into users (chat_id)
values (111746494);
