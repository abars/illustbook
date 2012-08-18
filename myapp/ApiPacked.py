#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#まとめてリクエストを出す
#copyright 2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import logging

from urlparse import urlparse

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api.users import User

from django.utils import simplejson

webapp.template.register_template_library('templatetags.django_filter')

from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert

from myapp.ApiBookmark import ApiBookmark
from myapp.ApiUser import ApiUser
from myapp.ApiObject import ApiObject
from myapp.ApiFeed import ApiFeed

class RequestHandlerHook():
	args={}
	host=""

	def get(self,value):
		if(self.args.has_key(value)):
			return self.args[value]
		return None

class HttpHandlerHook():
	request = RequestHandlerHook()

class ApiPacked(webapp.RequestHandler):
	def get(self):
		SetUtf8.set()
		
		#Query文字列を取得
		query=self.request.query_string;

		#RESULT
		result_dic={}
		request_no=0
		
		#APIリクエストに分解
		api_list=query.split(":")
		for api in api_list:
			#APIの引数を取得
			args=api.split("&")
			
			#引数をDictionaryに分解
			api_args={}
			for arg in args:
				params=arg.split("=")
				if(len(params)>=2):
					api_args[params[0]]=params[1]
			
			#呼び出しAPIのクラス名を決定
			if(api_args.has_key("class")):
				#ダミーリクエストハンドラーを作成
				req=HttpHandlerHook()
				req.request.args=api_args
				req.request.host=self.request.host

				#API呼び出し
				dic=None
				if(api_args["class"]=="api_bookmark"):
					dic=ApiBookmark.get_core(req)
				if(api_args["class"]=="api_user"):
					dic=ApiUser.get_core(req)
				if(api_args["class"]=="api_feed"):
					dic=ApiFeed.get_core(req)
				
				if(dic==None):
					logging.error("UnknownClass:"+api_args["class"])
				else:
					result_dic["request"+str(request_no)]=dic
					request_no=request_no+1
	
		ApiObject.write_json_core(self,result_dic)


