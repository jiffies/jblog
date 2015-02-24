#!/usr/bin/env python
#-*- coding: utf-8 -*-
import config
import hashlib,uuid
from framework.db import with_connection
from models import User,Blog
from framework.web import get, post, ctx, view, interceptor, seeother, notfound
from framework.apis import api, Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError
import os.path
import os, re, time, base64, hashlib, logging
from config import configs
import sae.storage
import markdown2
_COOKIE_NAME = 'jblog'
_COOKIE_KEY = configs.session.secret
CHUNKSIZE = 8192
UPLOAD_PATH='upload'
SAE_BUCKET = 'code4awesome'
@view('content.html')
@get('/')
def all_blogs():
    blogs = Blog.find_all()
    for blog in blogs:
        blog.content = markdown2.markdown(blog.content)
    main = blogs[0]
    sub = blogs[1:]
    #if not config.SAE:
        #for blog in sub:
            #os.path.join('..',blog.image)
    user = ctx.request.user
    return dict(main=main,sub=sub,user=user)

@view('signin.html')
@get('/signin')
def signin():
    user = ctx.request.user
    return dict(user=user)


def make_signed_cookie(id, password, max_age):
    # build cookie string by: id-expires-md5
    expires = str(int(time.time() + (max_age or 86400)))
    L = [id, expires, hashlib.md5('%s-%s-%s-%s' % (id, password, expires, _COOKIE_KEY)).hexdigest()]
    return '-'.join(L)
#@api
@post('/api/authenticate')
def authenticate():
    i = ctx.request.input(remember='')
    email = i.email.strip().lower()
    password = i.password
    remember = i.remember
    user = User.find_first('where email=?', email)
    if user is None:
        raise APIError('auth:failed', 'email', 'Invalid email.')
    elif user.password != password:
        raise APIError('auth:failed', 'password', 'Invalid password.')
    # make session cookie:
    max_age = 604800 if remember=='true' else None
    cookie = make_signed_cookie(user.id, user.password, max_age)
    ctx.response.set_cookie(_COOKIE_NAME, cookie, max_age=max_age)
    user.password = '******'
    raise seeother('/')
    return user


def parse_signed_cookie(cookie_str):
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        id, expires, md5 = L
        if int(expires) < time.time():
            return None
        user = User.get(id)
        if user is None:
            return None
        if md5 != hashlib.md5('%s-%s-%s-%s' % (id, user.password, expires, _COOKIE_KEY)).hexdigest():
            return None
        return user
    except:
        return None

@interceptor('/')
def user_interceptor(next):
    logging.info('try to bind user from session cookie...')
    user = None
    cookie = ctx.request.cookies.get(_COOKIE_NAME)
    if cookie:
        logging.info('parse session cookie...')
        user = parse_signed_cookie(cookie)
        if user:
            logging.info('bind user <%s> to session...' % user.email)
    ctx.request.user = user
    return next()


@get('/signout')
def signout():
    ctx.response.delete_cookie(_COOKIE_NAME)
    raise seeother('/')


def check_admin():
    user = ctx.request.user
    if user and user.admin:
        return
    raise APIPermissionError('No permission.')

from sae.ext.storage import monkey
monkey.patch_all() 
#模拟文件系统，/s/bucket_name/object/name
#@api
@post('/api/blogs')
def api_create_blog():
    check_admin()
    i = ctx.request.input(title='', content='')
    logging.info(i)
    title = i.title.strip()
    content = i.content.strip()
    image = i.image
    logging.info("upload image name:%s,type:%s" % (image.filename,type(image.filename)))
    if not title:
        raise APIValueError('name', 'name cannot be empty.')
    #if not summary:
        #raise APIValueError('summary', 'summary cannot be empty.')
    if not content:
        raise APIValueError('content', 'content cannot be empty.')
    filename = os.path.join(UPLOAD_PATH,hashlib.md5(image.filename.encode('utf-8')).hexdigest()+uuid.uuid4().hex)
    if 'SERVER_SOFTWARE' in os.environ:
       conn = sae.storage.Connection() 
       bucket = conn.get_bucket(SAE_BUCKET)
       bucket.put_object(filename,image.file)
       filename = bucket.generate_url(filename)
       logging.info(filename)
    else:
        with open(filename,'w') as f:
            chunk = image.file.read(CHUNKSIZE)
            while chunk:
                f.write(chunk)
                chunk = image.file.read(CHUNKSIZE)

    user = ctx.request.user
    blog = Blog(user_id=user.id,  title=title,  content=content,image=filename)
    blog.insert()
    raise seeother('/')
    return blog

@view("add_blog.html")
@get('/manage/add_blog')
def add_blog():
    user = ctx.request.user
    return dict(user=user)


@interceptor('/manage/')
def manage_interceptor(next):
    user = ctx.request.user
    if user and user.admin:
        return next()
    raise seeother('/signin')

@view("blog.html")
@get('/blog/:id')
def blog(id):
    blog = Blog.get(id)
    blog.content = markdown2.markdown(blog.content)
    if 'SERVER_SOFTWARE' not in os.environ:
        blog.image = '/'+blog.image
    if blog:
        return dict(blog=blog)
    raise notfound()
