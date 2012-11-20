#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#putとdeleteのフック
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from myapp.BbsConst import BbsConst

class CachedDbModel(db.Model):
	def put(self):
		db.Model.put(self)
		if(self.key()):
			memcache.delete(BbsConst.OBJECT_CACHE_HEADER+str(self.key()))

	def delete(self):
		memcache.delete(BbsConst.OBJECT_CACHE_HEADER+str(self.key()))
		db.Model.delete(self)
