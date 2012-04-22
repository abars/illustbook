#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#イラストブックアプリ　ポータル
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import urllib

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api.users import User

webapp.template.register_template_library('templatetags.django_filter')

from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert
from myapp.AppCode import AppCode
from myapp.ApiObject import ApiObject
from myapp.MesThread import MesThread
from myapp.MappingId import MappingId
from myapp.BbsConst import BbsConst
from myapp.CssDesign import CssDesign

class AppPortal(webapp.RequestHandler):
	@staticmethod
	def get_app(app_id):
		app=AppCode.all().filter("app_id =",app_id)
		if(app.count()==0):
			return None
		return app[0]
	
	@staticmethod
	def get_app_key(app_id):
		app=AppPortal.get_app(app_id)
		if(app==None):
			return None
		return str(app.key())

	def get(self):
		SetUtf8.set()
		
		mode=None
		if(self.request.get("mode")):
			mode=self.request.get("mode")
		
		app_key=None
		if(self.request.get("app_key")):
			app_key=self.request.get("app_key")
		if(self.request.get("app_id")):
			app_key=AppPortal.get_app_key(self.request.get("app_id"))
		
		if(mode=="icon"):
			app = db.get(app_key)
			if(app.icon):
				self.response.headers['Content-Type'] = str(app.icon_content_type)
				self.response.out.write(app.icon)
			else:
				self.redirect(str("./static_files/app/app_icon.png"))
			return
		
		AppPortal.ret(self,mode,app_key)
	
	@staticmethod
	def load_sample_app(filename):
		code = open('./api/'+filename).read()
		return code
	
	@staticmethod
	def add_support_forum(main,app):
		if(not app.support_forum and app.is_public):
			thread=MesThread()
			bbs_key=MappingId.mapping(BbsConst.APP_SUPPORT_BBS_ID)
			if(bbs_key==""):
				#return False
				main.response.out.write(Alert.alert_msg("サポートフォーラムBBS[ID:"+BbsConst.APP_SUPPORT_BBS_ID+"]が見つかりません。",main.request.host))
				return True

			bbs=db.get(bbs_key)
			thread.bbs_key=bbs
			thread.title=app.app_name
			thread.author=app.author
			thread.summary=app.app_name+"のサポートフォーラムです。"
			thread.user_id=app.user_id
			thread.illust_mode=BbsConst.ILLUSTMODE_NONE
			thread.create_date=datetime.datetime.today()
			thread.comment_cnt=0
			thread.date=datetime.datetime.today()

			thread.put()
			
			app.support_forum=thread
			app.put()

		#if(not app.support_forum.score):
		#	app.support_forum.score = None
		#	app.support_forum.put()
		
		return False
	
	@staticmethod
	def get_plugin_code(main,app_key,app):
		host=main.request.host
		plugin_code=""
		if(app_key and app and app.app_id):
			args=""
			if(app.plugin_args):
				args=app.plugin_args
			plugin_code="<iframe src='http://"+host+"/app?mode=plugin&app_id="+app.app_id+"&"+args+"' frameborder='0' scrolling='no' width='100%'></iframe>"
		return plugin_code
	
	@staticmethod
	def get_app_list(is_portal):
		hot_app_list=None
		hot_plugin_list=None
		hot_css_list=None
		new_app_list=None
		if(is_portal):
			hot_app_list=AppCode.all().filter("is_public =",1).filter("mode =",BbsConst.APP_MODE_APP).order("-bookmark_count").fetch(limit=10,offset=0)
			hot_plugin_list=AppCode.all().filter("is_public =",1).filter("mode =",BbsConst.APP_MODE_PLUGIN).order("-bookmark_count").fetch(limit=10,offset=0)
			hot_css_list=AppCode.all().filter("is_public =",1).filter("mode =",BbsConst.APP_MODE_CSS).order("-bookmark_count").fetch(limit=10,offset=0)
			new_app_list=AppCode.all().filter("is_public =",1).order("-public_date").fetch(limit=10,offset=0)
		return {"hot_app":hot_app_list,"hot_plugin":hot_plugin_list,"hot_css":hot_css_list,"new_app":new_app_list};

	@staticmethod
	def ret(main,mode,app_key):

		is_play=0
		if(mode=="play"):
			is_play=1

		is_run=0
		if(mode=="run"):
			is_run=1
		
		is_code=0
		if(mode=="code"):
			is_code=1

		is_plugin=0
		if(mode=="plugin"):
			is_plugin=1
		
		is_portal=1
		if(is_play or is_code or is_run or is_plugin):
			is_portal=0
		
		app_list=AppPortal.get_app_list(is_portal)
		
		app=None
		if(app_key and (is_play or is_code or is_run or is_plugin)):
			app=db.get(app_key)

		plugin_code=AppPortal.get_plugin_code(main,app_key,app)
		
		app_code=""
		if(app):
			if(app.mode==2):
				app_code=app.css_code
			else:
				app_code=app.js_code
			if(AppPortal.add_support_forum(main,app)):
				return
		if(is_code):
			app_code=cgi.escape(app_code.encode("utf-8"))

		user = users.get_current_user()
		logined=0
		if(user):
			logined=1
		if user:
			url_log = users.create_logout_url(main.request.url)
		else:
			url_log = users.create_login_url(main.request.url)

		#iPhoneモードかどうか
		is_iphone=CssDesign.is_iphone(main)

		template_values = {
			'host': "./",
			'hot_app_list': app_list["hot_app"],
			'hot_plugin_list': app_list["hot_plugin"],
			'hot_css_list': app_list["hot_css"],
			'new_app_list': app_list["new_app"],
			'is_play': is_play,
			'is_portal': is_portal,
			'is_code': is_code,
			'app_code': app_code,
			'app': app,
			'plugin_code': plugin_code,
			'url_log': url_log,
			'logined': logined,
			'is_iphone': is_iphone,
			'user': users.get_current_user(),
			'redirect_url': main.request.path
		}
		
		url='../html/app.html'
		if(is_run or is_plugin):
			url='../html/app/app_run.html'
		
		path = os.path.join(os.path.dirname(__file__), url)
		main.response.out.write(template.render(path, template_values))
			
