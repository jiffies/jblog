#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os

import logging; logging.basicConfig(level=logging.INFO)
from framework import db
from framework.web import WSGIApplication,Jinja2TemplateEngine
from config import configs

db.create_engine(**configs.db)
wsgi = WSGIApplication(os.path.dirname(os.path.abspath(__file__)))

template_engine = Jinja2TemplateEngine(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

wsgi.template_engine = template_engine

import urls
wsgi.add_interceptor(urls.user_interceptor)
wsgi.add_module(urls)

if __name__=='__main__':
    wsgi.run(9000,host='0.0.0.0')
else:
    application = wsgi.get_wsgi_application()
