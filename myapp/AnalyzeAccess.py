#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#掲示板のアクセス解析を表示
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import os
import re
import datetime

import template_select

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users

from myapp.MesThread import MesThread
from myapp.Bbs import Bbs
from myapp.MappingId import MappingId
from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert
from myapp.Counter import Counter
from myapp.CssDesign import CssDesign
from myapp.AnalyticsGet import AnalyticsGet
from myapp.OwnerCheck import OwnerCheck

class AnalyzeAccess(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()

		page_name=""
		mode="access"
		if(self.request.get("mode")):
			mode=self.request.get("mode")

		bbs=None

		user=None
		if(page_name==""):
			try:
				bbs = db.get(self.request.get("bbs_key"))
			except:
				bbs=None
			if(bbs==None):
				Alert.alert_msg_notfound(self)
				return

			user = users.get_current_user()
			if(user):
				if(bbs.user_id!=user.user_id()):
					user=None
		
			page_name=bbs.bbs_name;

		analytics=AnalyticsGet()
		analytics.create_session()

		if(self.request.get("start_date")):
			start_date=self.request.get("start_date")
		else:
			start_date=str(datetime.date.today()+datetime.timedelta(days=-31))

		if(self.request.get("end_date")):
			end_date=self.request.get("end_date")
		else:
			end_date=str(datetime.date.today()+datetime.timedelta(days=-1))

		bbs_id=bbs.short
		is_admin=OwnerCheck.is_admin(user)
		if(is_admin):
			if(self.request.get("bbs_id")):
				bbs_id=self.request.get("bbs_id")
				if(bbs.short!=bbs_id):
					page_name=bbs_id

		page_list=None
		ref_list=None
		keyword_list=None
		access_list=None

		show_analyze=False
		if(user or bbs.short=="sample"):
			show_analyze=True
		
		if(show_analyze):
			if(mode=="page"):
				page_list=analytics.get("page",bbs_id,start_date,end_date)
			if(mode=="ref"):
				ref_list=analytics.get("ref",bbs_id,start_date,end_date)
			if(mode=="keyword"):
				keyword_list=analytics.get("keyword",bbs_id,start_date,end_date)
			if(mode=="access"):
				access_list=analytics.get("access",bbs_id,start_date,end_date)

		quota_error=(mode=="access" and not access_list)
		
		redirect_api="analyze?start_date="+start_date+"&amp;end_date="+end_date+"&amp;bbs_id="+bbs_id+"&amp;bbs_key="+str(bbs.key())+"&amp;"

		host_url ="./"
		template_values = {
			'host': host_url,
			'mode': mode,
			'redirect_api': redirect_api,
			'quota_error': quota_error,
			'bbs': bbs,
			'bbs_id': bbs_id,
			'page_name': page_name,
			'is_admin': is_admin,
			'user': user,
			'show_analyze': show_analyze,
			'ref_list': ref_list,
			'page_list': page_list,
			'keyword_list': keyword_list,
			'access_list': access_list,
			'start_date': start_date,
			'end_date': end_date,
			'is_iphone': CssDesign.is_iphone(self),
			'is_tablet': CssDesign.is_tablet(self),
			'is_english': CssDesign.is_english(self),
			'redirect_url': self.request.path,
			}
		path = '/html/analyze.html'
		self.response.out.write(template_select.render(path, template_values))

