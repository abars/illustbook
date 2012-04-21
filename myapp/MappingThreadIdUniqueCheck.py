#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ユニークチェック用(get_or_insertで使用)
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users

from myapp.Bbs import Bbs
from myapp.MesThread import MesThread

class MappingThreadIdUniqueCheck(db.Model):
	bbs = db.ReferenceProperty(Bbs)
	thread = db.ReferenceProperty(MesThread)
	salt = db.StringProperty()
