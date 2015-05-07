-- This file is use for sae.
-- generating SQL for users:
create table `users` (
  `id` varchar(50) not null,
  `email` varchar(50) not null,
  `password` varchar(50) not null,
  `admin` bool not null,
  `created_at` real not null,
  primary key(`id`)
)  charset=utf8;

-- generating SQL for blogs:
create table `blogs` (
  `id` varchar(50) not null,
  `user_id` varchar(50) not null,
  `title` varchar(50) not null,
  `content` text not null,
  `image` varchar(500) not null,
  `created_at` real not null,
  primary key(`id`)
)  charset=utf8;

-- generating SQL for tags:
create table `tags` (
  `id` varchar(50) not null,
    `name` varchar(50) not null,
  `number` bigint not null,
  primary key(`id`)
  )default charset=utf8;

-- generating SQL for blogtag:
create table `blogtag` (
  `id` varchar(50) not null,
    `blog_id` varchar(50) not null,
  `tag_id` varchar(50) not null,
    primary key(`id`)
)default charset=utf8;

