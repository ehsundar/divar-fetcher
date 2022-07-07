create table if not exists posts
(
    token             varchar(10) primary key,
    title             text,
    description       text,

    credit            int check ( credit > 0 ),
    rent              float check ( rent > 0 ),

    surface           int,
    age               int,
    rooms             int,

    phone             varchar(11),
    additional_phones varchar(11)[],

    image_count int
);

create index if not exists credit_asc on posts using btree (credit asc);
create index if not exists rent_asc on posts using btree (rent asc);
