#!/usr/bin/env python
#-*- coding: utf-8 -*-

from framework.web import get, view
from framework.db import with_connection
from models import User,Blog

@view('content.html')
@get('/')
@with_connection
def test_blogs():
    blogs = Blog.find_all()
    users = User.find_all()
    return dict()

