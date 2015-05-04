#!/usr/bin/env python
#-*- coding: utf-8 -*-
from urlparse import urlparse
import config
import hashlib,uuid
from framework.db import with_connection
from models import User,Blog,Tag,BlogTag
from models import *
from framework.web import get, post, ctx, view, interceptor, seeother, notfound
from framework.apis import api, Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError
import os.path
import os, re, time, base64, hashlib, logging
from config import configs
import sae.storage
import markdown2
from framework import db
import random
_COOKIE_NAME = 'jblog'
_COOKIE_KEY = configs.session.secret
CHUNKSIZE = 8192
UPLOAD_PATH='upload'
SAE_BUCKET = configs.storage['bucket']

def tag_count_add(tag):
    tag.number+=1
    tag.update()

def tag_count_min(tag):
    tag.number-=1
    if tag.number == 0:
        tag.delete()
    else:
        tag.update()

def get_blog_head(content):
    length = len(content)
    if length > 50:
        length = length / 5
        return content[:length]+'\n\n...\n\n'
    else:
        return content

def render_blogs(blogs):
    #length = len(blogs)
    #main_blogs = random.sample(blogs,length/2)
    for blog in blogs:
        #if blog in main_blogs:
            #blog.main = True
        if 'SERVER_SOFTWARE' not in os.environ:
            blog.image = '/'+blog.image
        blog.content = get_blog_head(blog.content) 
        blog.content = markdown2.markdown(blog.content,extras=["code-friendly"])
        tags = get_tags_from_blog(blog)
        if tags:
            blog.tag = tags[0]
        else:
            blog.tag = Tag(name=u"未分类")
    return blogs


@view('content.html')
@get('/')
def all_blogs():
    blogs = Blog.find_all()
    blogs = sorted(blogs,key=lambda blog:blog.created_at,reverse=True)
    blogs = render_blogs(blogs)
    user = ctx.request.user
    return dict(blogs=blogs,user=user)

@view('content.html')
@get('/tag/:tag_id')
def tag_blogs(tag_id):
    tag = Tag.get(tag_id)
    if not tag:
        raise notfound()
    blogs = get_blogs_from_tag(tag)
    blogs = render_blogs(blogs)
    user = ctx.request.user
    return dict(blogs=blogs,user=user)

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
    back_last_page(2)



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

def upload(image):
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
    return filename

def delete_upload(filename):
    if 'SERVER_SOFTWARE' in os.environ:
       conn = sae.storage.Connection() 
       bucket = conn.get_bucket(SAE_BUCKET)
       filename = urlparse(filename).path[1:]
       bucket.delete_object(filename)
    else:
        if os.path.isfile(filename):
            os.remove(filename)
    logging.info("remove file %s." % filename)

def add_tags(blog_id,tags):
    if not tags:
        return
    if not tags[0]:
        return
    for tag in tags:
        t=Tag.find_by('where name=?',tag)
        if t:
            t = t[0]
        if not t:
            t = Tag(name=tag)
            t.insert()
        bt = BlogTag(blog_id=blog_id,tag_id=t.id)
        tag_count_add(t)
        bt.insert()
        logging.info("######add tag %s----%s" % (blog_id,tag))



@post('/api/blogs')
def api_create_blog():
    check_admin()
    i = ctx.request.input(title='', content='')
    logging.info(i)
    title = i.title.strip()
    content = i.content.strip()
    image = i.image
    tags = i.tags.strip()
    if image:
        logging.info("upload image name:%s,type:%s" % (image.filename,type(image.filename)))
    if not title:
        raise APIValueError('name', 'name cannot be empty.')
    #if not summary:
        #raise APIValueError('summary', 'summary cannot be empty.')
    if not content:
        raise APIValueError('content', 'content cannot be empty.')
    if not image:
        raise APIValueError('image', 'image cannot be empty.')
    filename = upload(image)
    user = ctx.request.user
    blog = Blog(user_id=user.id,  title=title,  content=content,image=filename)
    blog.insert()
    add_tags(blog.id,tags.split(' '))
    raise seeother('/blog/%s' % blog.id)

@view("add_blog.html")
@get('/manage/add_blog')
def add_blog():
    user = ctx.request.user
    return dict(user=user)

@interceptor('/')
def remember_last_page_interceptor(next):
    if ctx.request.path_info.startswith('/static') or ctx.request.path_info.startswith('/upload'):
        return next()
    referer_url = ctx.request.path_info
    remembered = ctx.request.cookie('referer_url')
    if remembered:
        array = remembered.split(',')
        if len(array) > 15:
            array = array[:15]
        remembered = ','.join(array)
    logging.info("#############@@@@@@@2")
    logging.info('remembered=%s, referer_url=%s ' % (remembered,referer_url))
    if referer_url:
        if remembered:
            ctx.response.set_cookie('referer_url',','.join([referer_url,remembered]))
        else:
            ctx.response.set_cookie('referer_url',referer_url)
    return next()

def back_last_page(back_index):
    referer_url = ctx.request.cookie('referer_url')
    logging.info('##############%s ' % referer_url)
    ctx.response.delete_cookie('referer_url')
    if referer_url:
        try:
            url=referer_url.split(',')[back_index-1]
        except IndexError:
            raise seeother('/')
        logging.info('##############%s ' % url)
        raise seeother(url)
    else:
        raise seeother('/')

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
    if not blog:
        raise notfound()
    blog.content = markdown2.markdown(blog.content,extras=["code-friendly"])
    if 'SERVER_SOFTWARE' not in os.environ:
        blog.image = '/'+blog.image
    tags = get_tags_from_blog(blog)
    blog.tags = tags
    tags = all_tags()
    return dict(blog=blog,user=ctx.request.user,tags=tags)

@view("edit_blog.html")
@get('/manage/edit/:id')
def edit_blog(id):
    blog = Blog.get(id)
    if not blog:
        raise notfound()
    tags = get_tags_from_blog(blog)
    return dict(blog=blog,user=ctx.request.user,tags=tags)

#delete one blog's some blogtag relationship.
def remove_blogtag(blog,remove):
    if not remove:
        return
    remove_string = "','".join(remove)
    s='delete from blogtag where blogtag.blog_id="%s" and blogtag.tag_id in (\'%s\')' % (blog.id,remove_string)
    logging.info('#########')
    logging.info(s)
    db.update(s)
    for tag_id in remove:
        tag = Tag.get(tag_id)
        tag_count_min(tag)

    
def update_tags(blog,tag_checkbox,tags):
    origin = get_tags_from_blog(blog)
    origin_ids = [tag.id for tag in origin]
    origin_names = [tag.name for tag in origin]

    #remove用的id
    remove = list(set(origin_ids).difference(set(tag_checkbox)))
    remove_blogtag(blog,remove)
    #add用的name
    if tags and tags[0]:
        add = list(set(tags).difference(set(origin_names)))
        add_tags(blog.id,add)

    

@post('/manage/edit/:id')
def api_edit_blog(id):
    check_admin()
    i = ctx.request.input()
    logging.info(i)
    title = i.title.strip()
    content = i.content.strip()
    image = i.image
    tags = i.tags
    try:
        tag_checkbox = ctx.request.gets('tag_checkbox')
    except KeyError:
        tag_checkbox = []
    logging.info("##################")
    logging.info(tag_checkbox)
    if not title:
        raise APIValueError('name', 'name cannot be empty.')
    if not content:
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog.get(id)
    if not blog:
        raise notfound()
    blog.title = title
    blog.content = content
    if image:
        delete_upload(blog.image)
        filename = upload(image)
        blog.image = filename
    blog.update()
    update_tags(blog,tag_checkbox,tags.split(' '))
    raise seeother('/blog/%s' % blog.id)

@api
@post('/manage/delete/:id')
def delete_blog(id):
    check_admin()
    blog = Blog.get(id)
    if not blog:
        raise notfound()
    tags = get_tags_from_blog(blog)
    remove = [tag.id for tag in tags]
    remove_blogtag(blog,remove)
    delete_upload(blog.image)
    blog.delete()
    return {'data':'/'}

@view('tag_cloud.html')
@get('/tagcloud')
def tag_cloud():
    tags = all_tags()
    user = ctx.request.user
    return dict(user=user,tags=tags)
    

@view('about.html')
@get('/about')
def about():
    user = ctx.request.user
    return dict(user=user)
    


