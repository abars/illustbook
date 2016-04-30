#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#一時投稿画像構造体
#copyright 2013 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users

class TempImage(db.Model):
	image = db.BlobProperty()
	thumbnail = db.BlobProperty()
	args = db.StringProperty()
	date = db.DateTimeProperty(auto_now=True)
