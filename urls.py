#!/usr/bin/env python
#-*- coding: utf-8 -*-

from framework.web import get, view
from framework.db import with_connection
from models import User,Blog

@view('content.html')
@get('/')
def all_blogs():
    blogs = Blog.find_all()
    main = blogs[0]
    sub = blogs[1:]
    return dict(main=main,sub=sub)

@view('signin.html')
@get('/signin')
def signin():
    return dict()
