#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ユーザのアイコン制御
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.BbsConst import BbsConst

class UserIcon(db.Model):
	user_id = db.StringProperty()
	icon = db.BlobProperty()
	icon_content_type = db.StringProperty()
	date = db.DateTimeProperty(auto_now=True)
	
	#アイコン変更時はdeleteしてputするのでmemcached.deleteは不要
