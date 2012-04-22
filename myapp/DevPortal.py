#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#イラストブック　デベロッパーポータル
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime

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
from myapp.AppPortal import AppPortal
from myapp.AppCode import AppCode
from myapp.ApiObject import ApiObject
from myapp.MappingId import MappingId
from myapp.AddBookmark import AddBookmark
from myapp.BbsConst import BbsConst

class DevPortal(webapp.RequestHandler):
	@staticmethod
	def load_initial_css_code(bbs):
		template_values = {
			'bbs': bbs
		}
		path = os.path.join(os.path.dirname(__file__), '../template_custom/style_user.htm')
		return template.render(path, template_values)

	@staticmethod
	def check_id_available(main,app_id):
		if(app_id=="" or MappingId.key_format_check(app_id)):
			main.response.out.write(Alert.alert_msg("アプリIDは半角英数である必要があります。",main.request.host))
			return False
		query=AppCode.all().filter("app_id =",app_id)
		if(query.count()==0):
			return True
		main.response.out.write(Alert.alert_msg("このアプリIDは既に使われています。",main.request.host))
		return False

	@staticmethod
	def add_new_app(main,user):
		app=AppCode()
		app.user_id=user.user_id()
		author="none"
		bookmark=ApiObject.get_bookmark_of_user_id(app.user_id)
		if(bookmark and bookmark.name):
			author=bookmark.name
		app.author=author
		app.js_code=""
		app.css_code=""
		app.app_name=main.request.get("app_name")
		app.app_id=main.request.get("app_id")
		app.mode=int(main.request.get("mode"))
		app.plugin_args=""
		app.app_guide=""
		app.is_public=0
		app.create_date=datetime.datetime.today()
		if(not DevPortal.check_id_available(main,app.app_id)):
			return
		if(app.app_name==""):
			main.response.out.write(Alert.alert_msg("アプリ名は必須です。",main.request.host))
			return False
		app.put()
		return True
	
	@staticmethod
	def update_app(main,user):
		app_key=main.request.get("app_key")
		app=None
		try:
			app=db.get(app_key)
		except:
			app=None

		no_permit=0
		if(not(app) or not(app.user_id==user.user_id())):
			no_permit=1

		if(main.request.get("code")):
			if(no_permit):
				dic={"status":"failed","message":"アプリを保存する権限がありません"}
				return dic
			if(app.mode==BbsConst.APP_MODE_CSS):
				app.css_code=main.request.get("code")
			else:
				app.js_code=main.request.get("code")
			app.put()
			dic={"status":"success","message":""}
			return dic
		
		if(no_permit):
			main.response.out.write(Alert.alert_msg("アプリを保存する権限がありません。",main.request.host))
			return
		if(app.app_id!=main.request.get("app_id")):
			if(not DevPortal.check_id_available(main,main.request.get("app_id"))):
				return
		app.author=main.request.get("author")
		app.app_name=main.request.get("app_name")
		app.app_id=main.request.get("app_id")
		app.app_guide=main.request.get("app_guide")
		app.is_public=int(main.request.get("is_public"))
		app.mode=int(main.request.get("mode"))
		app.ranking_order=int(main.request.get("ranking_order"))
		app.ranking_key=main.request.get("ranking_key")
		app.plugin_args=main.request.get("plugin_args")
		if(app.is_public):
			if(not app.public_date):
				app.public_date=datetime.datetime.today()
		if(not app.bookmark_count):
			app.bookmark_count=0
		if(main.request.get("icon")):
			app.icon=db.Blob(main.request.get("icon"))
			img = main.request.body_file.vars['icon']
			app.icon_content_type=img.headers['content-type']
		if(main.request.get("image")):
			if(main.request.get("image_id")==""):
				main.response.out.write(Alert.alert_msg("画像リソースにはIDが必要です。",main.request.host))
				return
			app.image_blob_list.append(db.Blob(main.request.get("image")))
			img = main.request.body_file.vars['image']
			app.image_type_list.append(img.headers['content-type'])
			app.image_id_list.append(main.request.get("image_id"))
		
		app.put()
		
		if(main.request.get("redirect")):
			main.redirect(str(main.request.get("redirect")))
		else:
			if(main.request.get("image")):
				main.redirect(str("./dev?page=info&app_key="+str(app.key())))
			else:
				main.redirect(str("./dev"))
		return None


	@staticmethod
	def delete_app(req):
		app_key=None
		if(req.request.get("app_key")):
			app_key=req.request.get("app_key")
		app=db.get(app_key)
		user = users.get_current_user()
		if(app and user and app.user_id==user.user_id()):
			app.delete()
		else:
			req.response.out.write(Alert.alert_msg("アプリが見つからないか削除する権限がありません。",req.request.host))
			return True
		return False
	
	@staticmethod
	def delete_image(req):
		app_key=None
		if(req.request.get("app_key")):
			app_key=req.request.get("app_key")
		app=db.get(app_key)
		user = users.get_current_user()
		if(app and user and app.user_id==user.user_id()):
			image_id=req.request.get("image_id")
			index_no=app.image_id_list.index(image_id)
			app.image_id_list.pop(index_no)
			app.image_blob_list.pop(index_no)
			app.image_type_list.pop(index_no)
			app.put()
			if(req.request.get("bbs_key")):
				req.redirect(str("./dev?page=info&app_key="+str(app.key())+"&bbs_key="+req.request.get("bbs_key")))
			else:
				req.redirect(str("./dev?page=info&app_key="+str(app.key())))
		else:
			req.response.out.write(Alert.alert_msg("アプリが見つからないか削除する権限がありません。",req.request.host))
		
	def post(self):
		SetUtf8.set()

		page=None
		if(self.request.get("page")):
			page=self.request.get("page")
		
		user = users.get_current_user()
		if(not user):
			if(page=="update"):
				dic={"status":"failed","message":"アプリを登録するにはログインする必要があります。"}
				ApiObject.write_json_core(self,dic)
				return
			else:
				self.response.out.write(Alert.alert_msg("アプリを登録するにはログインする必要があります。",self.request.host))
				return
		
		if(page=="update"):
			dic=DevPortal.update_app(self,user)
			if(dic==None):
				return
			ApiObject.write_json_core(self,dic)
			return
		
		if(page=="submit"):
			if(not DevPortal.add_new_app(self,user)):
				return

		DevPortal.ret(self,"top")
		
	def get(self):
		SetUtf8.set()

		page="top"
		if(self.request.get("page")):
			page=self.request.get("page")
		
		if(page=="delete"):
			if(DevPortal.delete_app(self)):
				return
			page="top"
		
		if(page=="del_image"):
			DevPortal.delete_image(self)
			return

		DevPortal.ret(self,page)
	
	@staticmethod
	def ret(req,page):
		if(req.request.get("redirect")):
			req.redirect(str(req.request.get("redirect")))
			return
	
		user = users.get_current_user()

		my_app_list=None
		if(user):
			my_app_list=AppCode.all().filter("user_id =",user.user_id()).fetch(limit=100,offset=0)
		
		if user:
			url_log = users.create_logout_url(req.request.url)
		else:
			url_log = users.create_login_url(req.request.url)

		app_key=None
		if(req.request.get("app_key")):
			app_key=req.request.get("app_key")
		
		bbs_key=None
		if(req.request.get("bbs_key")):
			bbs_key=req.request.get("bbs_key")

		app=None
		if(app_key):
			app=db.get(app_key)

		app_code=""
		if(app):
			app_code=app.js_code
		
		css_code=""
		if(app):
			css_code=app.css_code
			if(not css_code or css_code==""):
				css_code=DevPortal.load_initial_css_code(None)

		if(app_code==""):
			if(app and app.mode==BbsConst.APP_MODE_PLUGIN):
				app_code=AppPortal.load_sample_app("feedplugin.js")
			else:
				app_code=AppPortal.load_sample_app("helloworld.js")
		if(app_code=="puzzle"):
			app_code=AppPortal.load_sample_app("15puzzle.js")
		if(app_code=="feed"):
			app_code=AppPortal.load_sample_app("feedplugin.js")

		if(page=="edit"):
			app_code=cgi.escape(app_code.encode("utf-8"))
		
		sample_code=AppPortal.load_sample_app("helloworld.js")
		sample_code=cgi.escape(sample_code.encode("utf-8"))
		sample_code_plugin=AppPortal.load_sample_app("feedplugin.js")
		sample_code_plugin=cgi.escape(sample_code_plugin.encode("utf-8"))
		sample_code_css=DevPortal.load_initial_css_code(None)
		sample_code_css=cgi.escape(sample_code_css.encode("utf-8"))
		
		logined=0
		if(user):
			logined=1

		host_url="http://"+MappingId.mapping_host(req.request.host)+"/";
		
		template_values = {
			'host': host_url,
			'my_app_list': my_app_list,
			'sample_code': sample_code,
			'sample_code_plugin': sample_code_plugin,
			'sample_code_css': sample_code_css,
			'page': page,
			'app': app,
			'app_code': app_code,
			'css_code': css_code,
			'url_log': url_log,
			'logined': logined,
			'bbs_key': bbs_key,
			'user': users.get_current_user(),
			'redirect_url': req.request.path
		}
		
		url='../html/dev.html'
		if(page=="edit"):
			url='../html/dev/dev_edit.html'
		if(page=="info"):
			url='../html/dev/dev_info.html'
		
		path = os.path.join(os.path.dirname(__file__), url)
		req.response.out.write(template.render(path, template_values))
			
