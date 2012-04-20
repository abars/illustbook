#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#最近更新されたタグ
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users

class RecentTag(db.Model):
	tag_list = db.StringListProperty()
	score_list = db.StringListProperty()