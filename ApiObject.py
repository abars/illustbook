#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#オブジェクト管理、キャッシュ機構含む、一番重要
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime

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
from MesThread import MesThread
from MappingId import MappingId
from Bbs import Bbs
from BbsConst import BbsConst
from Bookmark import Bookmark
from StackFeedData import StackFeedData
from UTC import UTC
from JST import JST

class ApiObject(webapp.RequestHandler):

#-------------------------------------------------------------------
#日付計算
#-------------------------------------------------------------------

	@staticmethod
	def get_date_str(value):
		tmp=value.replace(tzinfo=UTC()).astimezone(JST())
		return ""+str(tmp.year)+"/"+str(tmp.month)+"/"+str(tmp.day)

#-------------------------------------------------------------------
#user object
#-------------------------------------------------------------------

	@staticmethod
	def create_user_object(req,one):
		icon_url="http://"+req.request.host+"/show_icon?key="+one.user_id
		profile_url="http://"+req.request.host+"/mypage?user_id="+one.user_id
		name=one.name
		if(not name):
			name="noname"
		one_dic={"user_id":one.user_id,"name":name,"homepage":one.homepage,"icon_url":icon_url,"profile_url":profile_url}
		return one_dic
	
	@staticmethod
	def get_bookmark_of_user_id(user_id):
		ret=memcache.get(BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_BOOKMARK_CACHE_HEADER+user_id)
		if(ret):
			return ret
		return ApiObject.get_bookmark_from_datastore(user_id)
	
	@staticmethod
	def get_bookmark_list(user_id_list):
		cached_bookmark=memcache.get_multi(user_id_list,key_prefix=BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_BOOKMARK_CACHE_HEADER)
		bookmark_list={}
		for user_id in user_id_list:
			if(user_id in cached_bookmark):
				bookmark_list[user_id]=cached_bookmark[user_id]
			else:
				bookmark_list[user_id]=ApiObject.get_bookmark_from_datastore(user_id)
		return bookmark_list
	
	@staticmethod
	def get_bookmark_from_datastore(user_id):
		#データストアから読込
		query=Bookmark.all().filter("user_id =",user_id)
		target_bookmark=None
		try:
			target_bookmark=query.fetch(1)[0]
		except:
			target_bookmark=None
		
		#サムネイル作成
		ApiObject.create_user_thumbnail(target_bookmark)

		#memcachedに格納
		memcache.set(BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_BOOKMARK_CACHE_HEADER+user_id,target_bookmark,60*60*12)
		return target_bookmark
	
	#サムネイルを作成
	#pilが必要
	#sudo port install jpeg
	#sudo easy_install pilでインストール
	@staticmethod
	def create_user_thumbnail(bookmark):
		#bookmark.thumbnail_created=0
		if(bookmark and bookmark.icon and (not bookmark.thumbnail_created)):
			img = images.Image(bookmark.icon)
			img.resize(width=180, height=180)
			img.im_feeling_lucky()
			try:
				bookmark.icon=img.execute_transforms(output_encoding=images.PNG)
				bookmark.icon_content_type = 'image/png'
				bookmark.thumbnail_created=1
				bookmark.put()
			except:
				img=None

	@staticmethod
	def get_bookmark_of_user_id_for_write(user_id):
		#データストアから実体を読込(書き込み用)
		bookmark=None
		try:
			bookmark=Bookmark.all().filter("user_id =",user_id)
		except:
			return None
		
		if(bookmark.count()==0):
			bookmark=Bookmark()
			#bookmark.owner=user #deleted
			bookmark.user_id=user_id#bookmark.owner.user_id()
			bookmark.put()
		else:
			bookmark=bookmark.fetch(1)
			bookmark=bookmark[0]
		
		if(not bookmark.thread_key_list):
			bookmark.thread_key_list=[]
		if(not bookmark.bbs_key_list):
			bookmark.bbs_key_list=[]
		if(not bookmark.app_key_list):
			bookmark.app_key_list=[]

		if(not bookmark.user_list):
			bookmark.user_list=[]

		return bookmark;

#-------------------------------------------------------------------
#thread object
#-------------------------------------------------------------------

	@staticmethod
	def create_thread_object_list(req,thread_key_list,bbs_id):
		#スレッドを取得
		first_thread_list=ApiObject.get_cached_object_list(thread_key_list)
		
		#スレッドから参照されるBBSを取得
		bbs_list=[]
		thread_list=[]
		for thread in first_thread_list:
			if(thread and thread.cached_bbs_key):	#BBSが削除された場合を考慮
				thread_list.append(thread)
				bbs_list.append(thread.cached_bbs_key)
		bbs_list=ApiObject.get_cached_object_list(bbs_list)
		
		#スレッドをJSON形式に変換しながら格納
		dic=[]
		cnt=0
		for thread in thread_list:
			bbs=bbs_list[cnt]
			cnt=cnt+1
			one_dic=ApiObject._create_thread_object_core(req,thread,bbs,True)	#文字だけのスレッドは含まない
			if(not bbs_id):
				if(one_dic["disable_news"]):
					continue
			if(one_dic):
				dic.append(one_dic)
		
		return dic

	#画像を含むスレッドのオブジェクトを作成
	@staticmethod
	def create_thread_object(req,thread):
		thread=ApiObject.get_cached_object(thread)
		bbs=ApiObject.get_cached_object(thread.cached_bbs_key)
		return ApiObject._create_thread_object_core(req,thread,bbs,True)	#文字だけのスレッドは含まない

	#画像を含まないスレッドも含んだスレッドのオブジェクトを作成
	@staticmethod
	def _create_thread_object_with_only_message_thread(req,thread):
		thread=ApiObject.get_cached_object(thread)
		bbs=ApiObject.get_cached_object(thread.cached_bbs_key)
		return ApiObject._create_thread_object_core(req,thread,bbs,False)	#文字だけのスレッドも含む
	
	@staticmethod
	def _create_thread_object_core(req,thread,bbs,only_image_thread):
		if(not thread):
			return None
		if(not thread.cached_image_key and only_image_thread):
			return None

		disable_news=0
		if(bbs.disable_news or bbs.del_flag ):
			disable_news=1
		if(thread.adult or thread.violate_terms or thread.violate_photo):
			disable_news=1

		if(bbs.short and bbs.short=="mopersample" and thread.illust_mode!=BbsConst.ILLUSTMODE_MOPER):
			disable_news=1;

		thumbnail_url=""
		if(thread.cached_image_key):
			thumbnail_url="http://"+req.request.host+"/thumbnail/"+str(thread.cached_image_key)
			if(thread.illust_mode==BbsConst.ILLUSTMODE_MOPER):
				thumbnail_url+=".gif"
			else:
				thumbnail_url+=".jpg"
		create_date=ApiObject.get_date_str(thread.create_date)

		thread_url="http://"+req.request.host+"/"
		if(bbs.short):
			thread_url+=bbs.short+"/"
		else:
			thread_url+="usr/"+str(bbs.key())+"/"
		if(thread.short):
			thread_url+=thread.short+".html"
		else:
			thread_url+=str(thread.key())+".html"

		image_url=""
		if(thread.cached_image_key):
			image_url="http://"+req.request.host+"/img/"+str(thread.cached_image_key)+".jpg"
		if(bbs.dont_permit_app):	#アプリでの画像データの参照を禁止
			image_url=""

		app=0
		if(thread.applause):
			app=thread.applause

		bookmark_cnt=0
		if(thread.bookmark_count):
			bookmark_cnt=thread.bookmark_count
		one_dic={"title":thread.title,"author":thread.author,"thumbnail_url":thumbnail_url,"image_url":image_url,"create_date":create_date,"thread_url":thread_url,"applause":app,"bookmark":bookmark_cnt,"key":str(thread.key()),"disable_news":disable_news}
		
		return one_dic

#-------------------------------------------------------------------
#bbs object
#-------------------------------------------------------------------

	@staticmethod
	def create_bbs_object(req,bbs):
		bookmark_cnt=0
		if(bbs.bookmark_count):
			bookmark_cnt=bbs.bookmark_count
		
		bbs_url="http://"+req.request.host+"/"
		if(bbs.short):
			bbs_url+=bbs.short+"/"
		else:
			bbs_url+="usr/"+str(bbs.key())+"/"
		
		one_dic={"title":bbs.bbs_name,"bbs_url":bbs_url,"bookmark":bookmark_cnt,"key":str(bbs.key())}
		return one_dic

#-------------------------------------------------------------------
#app object
#-------------------------------------------------------------------

	@staticmethod
	def create_app_object(req,app):
		icon_url="http://"+req.request.host+"/app?mode=icon&app_key="+str(app.key())
		app_url="http://"+req.request.host+"/app?mode=play&app_key="+str(app.key())
		one_dic={"app_id":app.app_id,"name":app.app_name,"icon_url":icon_url,"app_url":app_url,"key":str(app.key())}
		return one_dic

#-------------------------------------------------------------------
#feed object
#-------------------------------------------------------------------

	@staticmethod
	def _get_feed_user_list(feed_list):
		user_list=[]
		for feed in feed_list:
			if(feed==None):
				continue
			if(feed.from_user_id and user_list.count(feed.from_user_id)==0):
				user_list.append(feed.from_user_id)
			if(feed.to_user_id and user_list.count(feed.to_user_id)==0):
				user_list.append(feed.to_user_id)
			if(feed.user_key and user_list.count(feed.user_key)==0):
				user_list.append(feed.user_key)
		return user_list
		
	@staticmethod
	def _get_feed_bbs_list(feed_list):
		bbs_list=[]
		for feed in feed_list:
			if(feed==None):
				continue
			try:
				bbs_object_key=StackFeedData.bbs_key.get_value_for_datastore(feed)
				if(bbs_list.count(bbs_object_key)==0):
					bbs_list.append(bbs_object_key)
			except:
				None
		return bbs_list
	
	@staticmethod
	def _get_feed_thread_list(feed_list):
		thread_list=[]
		for feed in feed_list:
			if(feed==None):
				continue
			try:
				thread_object_key=StackFeedData.thread_key.get_value_for_datastore(feed)
				if(thread_list.count(thread_object_key)==0):
					thread_list.append(thread_object_key)
			except:
				None
		return thread_list

	@staticmethod
	def create_feed_object_list(req,feed_list):
		#出現するユーザと掲示板を全てリストアップ
		user_list=ApiObject._get_feed_user_list(feed_list)
		bbs_list=ApiObject._get_feed_bbs_list(feed_list)
		thread_list=ApiObject._get_feed_thread_list(feed_list)
		
		#ユーザ情報をまとめて取得
		bookmark_hash=ApiObject.get_bookmark_list(user_list)
		user_hash={}
		for i in range(len(user_list)):
			user_object=bookmark_hash[user_list[i]]
			if(user_object):
				to_user=ApiObject.create_user_object(req,user_object)
			else:
				to_user=None
			user_hash[user_list[i]]=to_user
		
		#掲示板情報をまとめて取得
		bbs_hash=ApiObject.get_cached_object_hash(bbs_list)

		#スレッド情報をまとめて取得
		thread_hash=ApiObject.get_cached_object_hash(thread_list)
		
		#オブジェクト作成
		dic=[]
		for feed in feed_list:
			if(feed==None):
				continue
			one_dic=ApiObject.create_feed_object(req,feed,user_hash,bbs_hash,thread_hash)
			if(one_dic==None):
				continue
			dic.append(one_dic)
		return dic

	@staticmethod
	def create_feed_object(req,feed,user_hash,bbs_hash,thread_hash):
		#送信元ユーザ取得
		from_user=""
		if(feed.from_user_id):
			from_user=user_hash[feed.from_user_id]

		#送信先ユーザ取得
		to_user=""
		if(feed.to_user_id):
			to_user=user_hash[feed.to_user_id]

		#フォローユーザ取得
		follow_user=""
		if(feed.user_key):
			follow_user=user_hash[feed.user_key]
		
		#イベント発生掲示板取得
		bbs_object_key=StackFeedData.bbs_key.get_value_for_datastore(feed)
		bbs=""
		bbs_object=None
		if(bbs_object_key):
			bbs_object=bbs_hash[bbs_object_key]
			if(bbs_object):
				bbs=ApiObject.create_bbs_object(req,bbs_object)
			
		#イベント発生スレッド取得
		thread_object_key=StackFeedData.thread_key.get_value_for_datastore(feed)
		thread=""
		if(thread_object_key):
			thread_object=thread_hash[thread_object_key]
			if(thread_object):
				only_image=False
				thread=ApiObject._create_thread_object_core(req,thread_object,bbs_object,only_image)

		#発生日取得
		create_date=ApiObject.get_date_str(feed.create_date)
		
		#オブジェクトを返す
		one_dic={"mode":feed.feed_mode,"from_user":from_user,"to_user":to_user,"follow_user":follow_user,"bbs":bbs,"thread":thread,"message":feed.message,"create_date":create_date,"key":str(feed.key())}
		return one_dic

#-------------------------------------------------------------------
#Access over capacity
#-------------------------------------------------------------------

	@staticmethod
	def check_api_capacity(req):
		return False
		
		#以下は重いので問題がおこるまでは省略
	
		limit_sec=3
		limit_api=10
		
		name="api_capacity_"+str(req.request.remote_addr)
		exist=memcache.get(name)
		if(exist):
			cnt=memcache.get(name+"_cnt")
			if(not cnt):
				cnt=1
			cnt=cnt+1
			memcache.set(name+"_cnt",cnt,limit_sec)
			if(cnt>=limit_api):
				ApiObject.write_json_core(req,{"status":"overcapacity","message":"APIアクセス回数制限を超えました。"})
				return True
		
		#set
		memcache.set(name,True,limit_sec)
		memcache.set(name+"_cnt",1,limit_sec)
		return False

#-------------------------------------------------------------------
#range
#-------------------------------------------------------------------

	@staticmethod
	def offset_and_limit(req,key_list):
		offset=0
		if(req.request.get("offset")):
			offset=int(req.request.get("offset"))
		
		limit=10
		if(req.request.get("limit")):
			limit=int(req.request.get("limit"))
		
		return key_list[offset:offset+limit]

#-------------------------------------------------------------------
#thread and bbs cache
#-------------------------------------------------------------------

	#更新を伴わない処理の場合はキャッシュから読み込む
	#キャッシュの内容はbbs.put()とthread.put()で自動的に無効化される

	@staticmethod
	def get_cached_object_hash(all_threads):
		cache=ApiObject.get_cached_object_list(all_threads)
		thread_hash={}
		for i in range(len(all_threads)):
			thread_hash[all_threads[i]]=cache[i]
		return thread_hash

	@staticmethod
	def get_cached_object_list(all_threads):
		#全てのスレッドのキーを取得
		key_list=[]
		for thread in all_threads:
			key_list.append(str(thread))
		
		#まとめて取ってくる
		cache_list=memcache.get_multi(key_list,key_prefix=BbsConst.OBJECT_CACHE_HEADER)
		
		#キャッシュヒットしたものはキャッシュから、
		#ヒットしなかったものはdbから取ってくる
		all_threads_cached=[]
		for thread in all_threads:
			if(str(thread) in cache_list):
				data=cache_list[str(thread)]
				all_threads_cached.append(data)
			else:
				data=ApiObject.get_datastore_object(thread)
				all_threads_cached.append(data)
				cache_list[str(thread)]=data	#このループで同じものが参照された場合のため
		
		return all_threads_cached

	@staticmethod
	def get_cached_object(thread):
		if(not thread):
			return None
		if(type(thread)==db.Key or type(thread)==str):
			thread_key=str(thread)
		else:
			thread_key=str(thread.key())
		ret=memcache.get(BbsConst.OBJECT_CACHE_HEADER+thread_key)
		if(ret):
			return ret
		return ApiObject.get_datastore_object(thread)
	
	@staticmethod
	def get_datastore_object(thread):
		if(type(thread)==db.Key or type(thread)==str):
			try:
				thread=db.get(thread);
			except:
				return None
		if(not thread):
			return None
		if(type(thread)==MesThread):
			image_key=MesThread.image_key.get_value_for_datastore(thread)
			if(image_key):
				thread.cached_image_key=str(image_key)
			bbs_key=MesThread.bbs_key.get_value_for_datastore(thread)
			if(bbs_key):
				thread.cached_bbs_key=str(bbs_key)
		memcache.set(BbsConst.OBJECT_CACHE_HEADER+str(thread.key()),thread,BbsConst.OBJECT_CACHE_TIME)
		return thread

#-------------------------------------------------------------------
#json return
#-------------------------------------------------------------------

	@staticmethod
	def write_json(req,dic):
		dic={"response":dic,"status":"success","message":""}
		ApiObject.write_json_core(req,dic)
	
	@staticmethod
	def write_json_core(req,dic):
		#JSONPかどうか
		callback_func=None
		if(req.request.get("callback")):
			callback_func=req.request.get("callback")
		
		#JSON作成
		json = simplejson.dumps(dic, ensure_ascii=False)
		req.response.content_type = 'application/json'
		
		#JSONP作成
		if(callback_func):
			json=""+callback_func+"("+json+")"
		
		#返却
		req.response.out.write(json)