drop database tinyclub;
create database tinyclub character set utf8 collate utf8_general_ci;
use tinyclub;

create table userinfo (
 account     varchar(30)		primary key not null,
 password    varchar(10) 		not null, 
 telephone   varchar(16) 		not null, 

 nickname    varchar(16) 		default '',
 gender      char(1)		 	default '', 
 age	     tinyint(3) unsigned	default 0, 
 city        varchar(24)		default '', 
 hobby       varchar(30)		default '', 
 brief       varchar(400)		default '',
 picture     varchar(100)		default '',
 ctime       timestamp                  not null default current_timestamp,
 lat         double(10,6)               default 0,
 lng         double(10,6) 		default 0 )DEFAULT CHARSET=utf8;

create table activity(
aid	     bigint 	primary key auto_increment,
author	     varchar(30)		default '',

title	     varchar(100)		default '',
cate	     varchar(16)		default '',
body         varchar(1000)		default '',
picture      varchar(100)		default '',

city         varchar(24)                default '',
ctime        timestamp                  not null default current_timestamp,
lat	     double(10,6) 		default 0 ,
lng          double(10,6) 		default 0 )DEFAULT CHARSET=utf8;

create table myactivity(
account     varchar(30)			not null,
aid	    bigint			not null,
mine        char			not null,
ctime       timestamp                   not null default current_timestamp)DEFAULT CHARSET=utf8;

create table reply(
rid		bigint			primary key auto_increment,
aid		bigint			default 0,
fid		bigint			default 0,

ctime        	timestamp               not null default current_timestamp,
author		varchar(30),
title 		varchar(100),
body  		varchar(400))DEFAULT CHARSET=utf8;


create table unread_reply(
author_f	varchar(30)	default '',
fid		bigint          default 0 ,
rid		bigint          default 0 ,
if_activity    	char(1)         default '')DEFAULT CHARSET=utf8;

create table test (
name varchar(10) not null,
age varchar(10));

#create table position (
#account     varchar(16)  	primary key not null,
#lat	       double(10,6)		default 0 ,
#lng         double(10,6) 	default 0 );


#create table groups (
#gid        integer primary key auto_increment,
#name      varchar(16),
#cate      varchar(16),
#brief     text);

#create table mygroup (
#account     varchar(16),
#gid         varchar(16));

#create table myfriend (
#me          varchar(16)		default '',
#he          varchar(16)		default '')

insert into  userinfo (account,password,telephone) values ('123','123','123');
insert into  activity (author,title,body,picture) values ('yilong','测试','这是一个测试帖','resource/activity/1/');
insert into  reply (aid,fid,author,title,body) values (1,0,'yilong','hello','i am reply');
insert into  reply (aid,fid,author,title,body) values (0,1,'yilong','hello','i am reply reply');

SET character_set_client = utf8 ;
SET character_set_connection = utf8 ;
SET character_set_database = utf8 ;
SET character_set_results = utf8 ;
SET character_set_server = utf8 ;
SET collation_connection = utf8_general_ci ;
SET collation_database = utf8_general_ci ;
SET collation_server = utf8_general_ci ;
