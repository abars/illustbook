#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#Pinterest表示
#copyright 2013 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import random
import logging
import urllib
import math

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.Bbs import Bbs
from myapp.Counter import Counter
from myapp.Alert import Alert
from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8
from myapp.Entry import Entry
from myapp.OwnerCheck import OwnerCheck
from myapp.RecentCommentCache import RecentCommentCache
from myapp.CssDesign import CssDesign
from myapp.BbsConst import BbsConst
from myapp.MappingThreadId import MappingThreadId
from myapp.MesThread import MesThread
from myapp.RecentTag import RecentTag
from myapp.ApiObject import ApiObject
from myapp.SearchTag import SearchTag
from myapp.ApiFeed import ApiFeed
from myapp.ApiUser import ApiUser
from myapp.MaintenanceCheck import MaintenanceCheck
from myapp.SiteAnalyzer import SiteAnalyzer

class Pinterest(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		#メンテナンス画面
		is_maintenance=0
		if(MaintenanceCheck.is_appengine_maintenance()):
			is_maintenance=1
		
		#BBS COUNT
		cache=SiteAnalyzer.get_cache()
		bbs_n=cache["bbs_n"]
		illust_n=cache["illust_n"]

		#User
		user = users.get_current_user()
		unit=32

		order="hot"
		if(self.request.get("order")):
			order=self.request.get("order")
		
		page=1
		if(self.request.get("page")):
			page=int(self.request.get("page"))

		tag=""
		if(self.request.get("tag")):
			tag=self.request.get("tag")

		user_id=""
		if(self.request.get("user_id")):
			user_id=self.request.get("user_id")

		page_mode="index"
		view_user=None
		view_user_profile=None
		tag_list_view_n=5

		if(user_id!=""):
			thread_list=ApiUser.user_get_thread_list(self,user_id)
			page_mode="user"
			view_user=ApiUser.user_get_user(self,user_id)
			view_user_profile=ApiUser.user_get_profile(self,user_id)
			tag_list=SearchTag.get_recent_tag("pinterest")
			next_query="user_id="+user_id
		else:
			if(tag!=""):
				query = db.Query(MesThread,keys_only=True)
				query.filter('illust_mode =', BbsConst.ILLUSTMODE_ILLUST)
				query.order('-create_date')
				query.filter('tag_list =', tag)
				cnt=query.count(limit=100)
				thread_key_list = query.fetch(limit=unit, offset=(page-1)*unit)
				thread_list=ApiObject.create_thread_object_list(self,thread_key_list,"pinterest")
				tag_list=SearchTag.update_recent_tag(tag,cnt,"pinterest")
				next_query="tag="+tag
				page_mode="tag"
				tag_list_view_n=100
			else:
				thread_list=ApiFeed.feed_get_thread_list(self,order,(page-1)*unit,unit)
				tag_list=SearchTag.get_recent_tag("pinterest")
				next_query="order="+order

		#iPhoneかどうか
		is_iphone=CssDesign.is_iphone(self)

		template_values = {
			'host': "./",
			'user': user,
			'order': order,
			'tag_list': tag_list,
			'thread_list': thread_list,
			'redirect_url': self.request.path,
			'next_page': page+1,
			'next_query': next_query,
			'page_mode': page_mode,
			'tag': tag,
			'tag_list_view_n': tag_list_view_n,
			'view_user': view_user,
			'view_user_profile': view_user_profile,
			'is_iphone': is_iphone,
			'top_page': True,
			'bbs_n': bbs_n,
			'illust_n': illust_n
		}
		path = os.path.join(os.path.dirname(__file__), '../html/pinterest.html')
		self.response.out.write(template.render(path, template_values))

