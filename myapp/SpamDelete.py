#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スパム一括削除
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------


import re

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db

from SetUtf8 import SetUtf8;
from BbsConst import BbsConst;
from Alert import Alert
from Entry import Entry
from SpamCheck import SpamCheck
from RecentCommentCache import RecentCommentCache
from MesThread import MesThread
from OwnerCheck import OwnerCheck

class SpamDelete(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		user = users.get_current_user()
		
		is_admin=0
		if(user):
			if(OwnerCheck.is_admin(user)):
				is_admin=1
		
		if(not is_admin):
			self.response.out.write(Alert.alert_msg("管理者権限が必要です。",self.request.host));
			return

		checkcode=SpamCheck.get_check_code()		

		query=Entry.all()
		thread=None
		try:
			thread=db.get(checkcode)
		except:
			thread=None
		if(thread):
			query.filter("thread_key =",thread)
		entrys=query.fetch(limit=1000)
		
		ret=0
		aborted=""

		for entry in entrys:
			if(SpamCheck.check_with_thread(entry,checkcode)):
				entry.delete()
				ret=ret+1
				if(ret>=250):
					aborted="ABORTED"
					break;

		RecentCommentCache.invalidate(None);
		self.response.out.write(Alert.alert_msg("<H2>SPAM DELETE RESULT</H2>"+aborted+"<H2>TOTAL</H2>DELETE CNT:"+str(ret),self.request.host))		

