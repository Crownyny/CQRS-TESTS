create schema if not exists cqrs;

create table if not exists post (
    id BIGSERIAL primary key,
    content varchar not null
);

create table if not exists comment (
    id BIGSERIAL primary key,
    content varchar not null,
    post_id bigint not null,
    foreign key (post_id) references post (id)
);

create table if not exists comment_reaction (
    id BIGSERIAL primary key,
    emoji varchar not null,
    comment_id bigint not null,
    foreign key (comment_id) references comment (id)
);