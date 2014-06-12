#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#旧アクセス解析　削除予定
#---------------------------------------------------

from google.appengine.ext import db

class Analyze(db.Model):
	bbs_key =db.ReferenceProperty()
	ip = db.StringProperty(indexed=False)
	adr = db.StringListProperty(indexed=False)
	content = db.StringListProperty(indexed=False)
	date = db.DateTimeProperty(auto_now=True,indexed=False)
	
