#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#データ保存系の公開API
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

from django.utils import simplejson

from SetUtf8 import SetUtf8
from Alert import Alert
from ApiObject import ApiObject
from ApiPerpetuationData import ApiPerpetuationData
from AddBookmark import AddBookmark
from AppCode import AppCode

class ApiPerpetuation(webapp.RequestHandler):

#-------------------------------------------------------------------
#保存
#-------------------------------------------------------------------

	@staticmethod
	def get_app_key(req):
		app_key2=""
		if("Referer" in req.request.headers):
			header=req.request.headers['Referer']
			pair_list=header.split("&")
			for pair in pair_list:
				div=pair.split("=")
				if(div[0]=="app_key"):
					app_key2=div[1]
				if(div[0]=="app_id"):
					query=AppCode.all().filter("app_id =",div[1])
					app_key2=str(query[0].key())
		return app_key2

	@staticmethod
	def put_data(req):
		#ユーザ認証
		user = users.get_current_user()
		if(not user or user.user_id()!=req.request.get("user_id")):
			dic={"status":"failed","message":"保存するユーザ権限がありません。"}
			return dic

		#アプリ認証
		app_key=req.request.get("app_key")
		app_key2=ApiPerpetuation.get_app_key(req)
		header=""
		if(app_key!=app_key2):
			dic={"status":"failed","message":"保存するアプリ権限がありません。"}#+header+" "+app_key+" vs "+app_key2}
			return dic

		#保存
		data=ApiPerpetuation.get_one_data(req,1)
		try:
			data.text_data=req.request.get("text_data")
			data.int_data=int(req.request.get("int_data"))
			data.put()
		except:
			dic={"status":"failed","message":"保存に失敗しました。"}
			return dic
		dic={"status":"success","message":""}
		return dic

#-------------------------------------------------------------------
#読込
#-------------------------------------------------------------------

	@staticmethod
	def get_ranking(req):
		app_key=req.request.get("app_key")
		data_key=req.request.get("data_key")
		order=req.request.get("order")
		query=ApiPerpetuationData.all()
		query.filter("app_key =",db.get(app_key))
		query.filter("data_key =",data_key)
		if(order=="ascending"):
			query.order("int_data")
			query.filter("int_data !=",0)
		else:
			query.order("-int_data")
		data_list=query.fetch(limit=10,offset=0)
		dic=[]
		for data in data_list:
			one_user=data.user_id
			bookmark=ApiObject.get_bookmark_of_user_id(one_user)
			if(bookmark):
				one_dic=ApiObject.create_user_object(req,bookmark)
				one_dic["text_data"]=data.text_data
				one_dic["int_data"]=data.int_data
				dic.append(one_dic)
		dic={"status":"success","message":"","response":dic}
		return dic
	
	@staticmethod
	def get_data(req):
		data=ApiPerpetuation.get_one_data(req,0)
		if(data==None):
			dic={"status":"nodata","message":"保存されているデータが存在しません。"}
			return dic
		dic={"user_id":data.user_id,"data_key":data.data_key,"text_data":data.text_data,"int_data":data.int_data}
		dic={"status":"success","message":"","response":dic}
		return dic
	
	@staticmethod
	def get_one_data(req,create_new):
		app_key=req.request.get("app_key")
		data_key=req.request.get("data_key")
		user_id=req.request.get("user_id")
		query=ApiPerpetuationData.all()
		query.filter("app_key =",db.get(app_key))
		query.filter("data_key =",data_key)
		query.filter("user_id =",user_id)
		if(query.count()>=1):
			return query[0];
		if(create_new==0):
			return None;
		data=ApiPerpetuationData()
		data.app_key=db.get(app_key)
		data.user_id=user_id
		data.data_key=data_key
		return data
	
#-------------------------------------------------------------------
#main
#-------------------------------------------------------------------

	def post(self):
		#日本語対応
		SetUtf8.set()
		if(ApiObject.check_api_capacity(self)):
			return
		
		#パラメータ取得
		method=""
		if(self.request.get("method")):
			method=self.request.get("method");
		
		#返り値
		dic={"status":"failed","message":"methodが見つかりません"}

		#ユーザクラス
		if(method=="putData"):
			dic=ApiPerpetuation.put_data(self)
			
		ApiObject.write_json_core(self,dic)

	def get(self):
		#日本語対応
		SetUtf8.set()
		if(ApiObject.check_api_capacity(self)):
			return

		#パラメータ取得
		method=""
		if(self.request.get("method")):
			method=self.request.get("method");
		
		#返り値
		dic={"status":"failed","message":"methodが見つかりません"}

		if(method=="getData"):
			dic=ApiPerpetuation.get_data(self)
		if(method=="getRanking"):
			dic=ApiPerpetuation.get_ranking(self)

		ApiObject.write_json_core(self,dic)
