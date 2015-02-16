#!/usr/bin/env python
#-*- coding:utf-8 -*-

import time,uuid
from framework.db import next_id
from framework.orm import Model,StringField,BooleanField,FloatField,TextField

class User(Model):
    __table__ = "users"

    id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
    email = StringField(updatable=False,ddl='varchar(50)')
    password = StringField(ddl='varchar(50)')
    admin = BooleanField()
    created_at = FloatField(updatable=False,default=time.time)

class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
    user_id = StringField(updatable=False,ddl='varchar(50)')
    title = StringField(ddl='varchar(50)')
    content = TextField()
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(updatable=False,default=time.time)
