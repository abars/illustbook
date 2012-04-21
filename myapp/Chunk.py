#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#1MBを超えるファイルを管理するためのチャンク
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users

from myapp.Bbs import Bbs
from myapp.ThreadImage import ThreadImage

class Chunk(db.Model): 
	bbs_key = db.ReferenceProperty(Bbs)
	data = db.BlobProperty() 
	index = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now=True)