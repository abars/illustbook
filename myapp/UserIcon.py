#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ユーザのアイコンを退避させていたが、
#パフォーマンスが出ないのでBookmarkに戻したので、
#実質的には使っていない
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.BbsConst import BbsConst
from myapp.CachedDbModel import CachedDbModel

class UserIcon(CachedDbModel):
	user_id = db.StringProperty()
	icon = db.BlobProperty()
	icon_content_type = db.StringProperty()
	date = db.DateTimeProperty(auto_now=True)
