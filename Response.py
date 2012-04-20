#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#コメントへのコメント構造体
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users

class Response(db.Model):
	editor = db.StringProperty()
	content = db.TextProperty()
	user_id = db.StringProperty()	#Submitter
	homepage_addr = db.StringProperty() #Reserved
	date = db.DateTimeProperty(auto_now=True)