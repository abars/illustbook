#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#アクセス解析を表示

import os
import re

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users

from MesThread import MesThread
from Bbs import Bbs
from MappingId import MappingId
from SetUtf8 import SetUtf8
from TopPage import TopPage
from Alert import Alert

class AnalyzeAccess(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()
		
		toppage_query = TopPage.all()
		page_name=""
		bbs=None

		if(self.request.get("bbs_key")=="top"):
			analyze=toppage_query[0].analyze.get_referer()
			page_name="トップページ"

		if(self.request.get("bbs_key")=="top_moper_guide"):
			analyze=toppage_query[0].moper_analyze.get_referer()
			page_name="モッパーの使い方"

		if(self.request.get("bbs_key")=="top_about"):
			analyze=toppage_query[0].about_analyze.get_referer()
			page_name="スタートガイド"

		if(self.request.get("bbs_key")=="top_guide"):
			analyze=toppage_query[0].guide_analyze.get_referer()
			page_name="お絵かきツールの使い方"

		if(self.request.get("bbs_key")=="top_mypage"):
			analyze=toppage_query[0].mypage_analyze.get_referer()
			page_name="マイページ"

		if(self.request.get("bbs_key")=="top_ranking"):
			analyze=toppage_query[0].ranking_analyze.get_referer()
			page_name="ランキング"

		if(self.request.get("bbs_key")=="top_link"):
			analyze=toppage_query[0].link_analyze.get_referer()
			page_name="お絵かきリンク集"

		if(self.request.get("bbs_key")=="top_local"):
			analyze=toppage_query[0].link_analyze.get_referer()
			page_name="ローカルツール"

		if(self.request.get("bbs_key")=="top_questionnaire"):
			analyze=toppage_query[0].link_analyze.get_referer()
			page_name="アンケート"
		
		user=None
		if(page_name==""):
			try:
				bbs = db.get(self.request.get("bbs_key"))
			except:
				bbs=None
			if(bbs==None):
				self.response.out.write(Alert.alert_msg_notfound(self.request.host))
				return

			user = users.get_current_user()
			if(user):
				if(bbs.user_id!=user.user_id()):
					user=None
		
			if(self.request.get("mode")):
				if(self.request.get("mode")=="delete"):
					if(user):
						bbs.analyze.reset()
						bbs.analyze.put()
						bbs.counter.reset_ip()
						bbs.counter.put()

			analyze=bbs.analyze.get_referer()
			page_name=bbs.bbs_name;

		analyze=re.sub("\"","\\\"",analyze)
		
		host_url ="./"
		template_values = {
			'host': host_url,
			'bbs': bbs,
			'page_name': page_name,
			'analyze_data':analyze,
			'user': user
			}
		path = os.path.join(os.path.dirname(__file__), 'html/mes_analyze.html')
		self.response.out.write(template.render(path, template_values))

