#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#拍手
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.Entry import Entry
from myapp.Response import Response
from myapp.MesThread import MesThread
from myapp.BbsConst import BbsConst
from myapp.ThreadImage import ThreadImage
from myapp.SpamCheck import SpamCheck
from myapp.Alert import Alert
from myapp.OwnerCheck import OwnerCheck
from myapp.RecentCommentCache import RecentCommentCache
from myapp.MappingId import MappingId
from myapp.Alert import Alert
from myapp.Ranking import Ranking

class Applause(webapp.RequestHandler):
	def get(self):
		try:
			thread = db.get(self.request.get("thread_key"))
			bbs = db.get(self.request.get("bbs_key"))
		except:
			thread=None
			bbs=None
		
		if(thread==None or bbs==None):
			self.response.out.write(Alert.alert_msg("拍手対象のスレッドが見つかりません。",self.request.host));
			return
		
		if(self.request.remote_addr!=thread.applause_ip and self.request.remote_addr!=thread.applause_ip2 and self.request.remote_addr!=thread.applause_ip3 and self.request.remote_addr!=thread.applause_ip4):
			if thread.applause:
				thread.applause=thread.applause+1
			else:
				thread.applause=1
			thread.applause_ip4=thread.applause_ip3
			thread.applause_ip3=thread.applause_ip2
			thread.applause_ip2=thread.applause_ip
			thread.applause_ip=self.request.remote_addr
			thread.applause_date=datetime.datetime.today()
			thread.put()

			if(bbs.applause_n) :
				bbs.applause_n=bbs.applause_n+1
			else:
				bbs.applause_n=1
			bbs.put()

			Ranking.add_rank_global(thread,BbsConst.SCORE_APPLAUSE)

		if(self.request.get("mode")=="bbs"):
			order = self.request.get("order")
			page = self.request.get("page")
			self.redirect(str(MappingId.get_usr_url("./",bbs)+"?order="+order+"&page="+page))
		else:	
			thread_url=self.request.get("thread_key")
			if(thread.short):
				thread_url=thread.short
			self.redirect(str(MappingId.get_usr_url("./",bbs)+thread_url+".html"))
		