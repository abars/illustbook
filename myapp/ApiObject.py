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
import json
import logging

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.api.users import User

from myapp.SetUtf8 import SetUtf8
from myapp.Alert import Alert
from myapp.MesThread import MesThread
from myapp.MappingId import MappingId
from myapp.Bbs import Bbs
from myapp.BbsConst import BbsConst
from myapp.Bookmark import Bookmark
from myapp.StackFeedData import StackFeedData
from myapp.UTC import UTC
from myapp.JST import JST
from myapp.Entry import Entry
from myapp.TimeProgress import TimeProgress
from myapp.ImageFile import ImageFile
from myapp.SearchThread import SearchThread
from myapp.CssDesign import CssDesign

class ApiObject(webapp.RequestHandler):

#-------------------------------------------------------------------
#user object
#-------------------------------------------------------------------

	@staticmethod
	def create_user_object_fast(req,user_id):
		icon_url="http://"+req.request.host+"/show_icon?key="+user_id
		profile_url="http://"+req.request.host+"/mypage?user_id="+user_id
		one_dic={"user_id":user_id,"name":"unknown","homepage":"unknown","icon_url":icon_url,"profile_url":profile_url}
		return one_dic

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
		key=BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_BOOKMARK_CACHE_HEADER+user_id
		ret=memcache.get(key)
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
		query=db.Query(Bookmark,keys_only=True).filter("user_id =",user_id)
		target_bookmark=None

		#count=query.count(limit=2)
		#if(count>=2):
		#	logging.error("bookmark duplicate error user_id="+str(user_id))

		try:
			target_bookmark=db.get(query.fetch(1)[0])	#強い整合性を保証
		except:
			target_bookmark=None
		
		#サムネイル作成
		ApiObject.create_user_thumbnail(target_bookmark)
		
		#memcachedに格納
		try:
			memcache.set(BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_BOOKMARK_CACHE_HEADER+user_id,target_bookmark,BbsConst.OBJECT_CACHE_TIME)
		except:
			mee=None
		return target_bookmark

	@staticmethod
	def get_bookmark_of_user_id_for_write(user_id):
		#データストアから実体を読込(書き込み用)
		bookmark=None
		try:
			bookmark=db.Query(Bookmark,keys_only=True).filter("user_id =",user_id)
		except:
			return None
		
		count=bookmark.count(limit=2)
		if(count>=2):
			#keynameの設定でduplicateは起きなくなったはず
			logging.error("bookmark duplicate error user_id="+str(user_id))

			#もし起きる場合は古いデータなので以下で削除のこと
			#duplicate_bookmark=bookmark.fetch(2)
			#db.get(duplicate_bookmark[1]).delete()
			#logging.error("deleted duplicated one")

		if(count==0):
			#同じuser_idでduplicateが起きないようにするためにkey_nameを設定
			#昔のbookmarkにはkey_nameは設定していないので注意
			bookmark=Bookmark(key_name=BbsConst.KEY_NAME_BOOKMARK+user_id)
			bookmark.user_id=user_id
			bookmark.put()
		else:
			bookmark=bookmark.fetch(1)
			bookmark=db.get(bookmark[0])	#強い整合性を保証
		
		if(not bookmark.thread_key_list):
			bookmark.thread_key_list=[]
		if(not bookmark.bbs_key_list):
			bookmark.bbs_key_list=[]
		if(not bookmark.app_key_list):
			bookmark.app_key_list=[]

		if(not bookmark.user_list):
			bookmark.user_list=[]

		return bookmark;

	@staticmethod
	def get_follower_list(user_id):
		follower_string=memcache.get(BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_FOLLOWER_HEADER+user_id)
		if(not follower_string):
			query=Bookmark.all().filter("user_list =",user_id)
			follower=query.fetch(limit=1000)
			follower_string=[]
			for one_user in follower:
				follower_string.append(one_user.user_id)
			memcache.set(BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_FOLLOWER_HEADER+user_id,follower_string,BbsConst.OBJECT_CACHE_TIME)
		return follower_string
	
	@staticmethod
	def invalidate_follower_list(user_id):
		memcache.delete(BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_FOLLOWER_HEADER+user_id)
	
	#サムネイルを作成
	#  pilが必要
	#  sudo port install jpeg
	#  sudo easy_install pilでインストール
	@staticmethod
	def create_user_thumbnail(bookmark):
		#UserIconクラスに退避していた画像をBookmarkクラスに復元
		#user_icon_exist=False
		#try:
		#	if(bookmark and bookmark.user_icon):
		#		user_icon_exist=True
		#except:
		#	user_icon_exist=False
		#if(user_icon_exist):
		#	if(not bookmark.icon):
		#		bookmark.icon=bookmark.user_icon.icon
		#		bookmark.put()
		#	bookmark.user_icon.delete()
		#	bookmark.user_icon=None
		
		#180pxサムネイル作成
		if(bookmark and bookmark.icon and (not bookmark.thumbnail_created)):
			thumb=ImageFile.create_thumbail(180,180,bookmark.icon,"png")
			if(thumb):
				bookmark.icon=thumb["code"]
				bookmark.icon_content_type = thumb["content_type"]
				bookmark.thumbnail_created=BbsConst.USER_ICON_THUMBNAIL_CREATED
				bookmark.put()
			else:
				return False
		
		#50pxサムネイル作成
		if(bookmark and bookmark.icon and (not bookmark.icon_mini)):
			thumb=ImageFile.create_thumbail(50,50,bookmark.icon,"png")
			if(thumb):
				bookmark.icon_mini=thumb["code"]
				bookmark.icon_mini_content_type = thumb["content_type"]
				bookmark.put()
			else:
				return False

		return True

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

		#文字だけのスレッドを含むか
		only_image_thread=True
		#if(bbs_id=="search" or bbs_id=="pinterest"):
		#	only_image_thread=False
		
		#スレッドをJSON形式に変換しながら格納
		dic=[]
		cnt=0
		for thread in thread_list:
			bbs=bbs_list[cnt]
			cnt=cnt+1
			one_dic=ApiObject._create_thread_object_core(req,thread,bbs,only_image_thread)	#文字だけのスレッドは含まない
			if(not bbs_id or (bbs_id=="search")):
				if(one_dic and one_dic["disable_news"]):
					continue
			if(bbs_id and bbs_id=="search"):
				if(thread.illust_mode==BbsConst.ILLUSTMODE_MOPER):
					continue
			if(bbs_id and (bbs_id=="search" or bbs_id=="pinterest")):
				if(one_dic and one_dic["violate_terms"]):
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
	def is_frozen_thread(thread):
		if(thread and thread.user_id):
			#logging.error(str(thread.user_id))
			bookmark=ApiObject.get_bookmark_of_user_id(thread.user_id)
			if(bookmark):
				if(bookmark.frozen):
					return True
		return False
	
	@staticmethod
	def _create_thread_object_core(req,thread,bbs,only_image_thread):
		if(not thread or not bbs):
			return None
		if(not thread.cached_image_key and only_image_thread):
			return None
		if(bbs.del_flag):
			return None

		disable_news=0
		violate_terms=0
		if(bbs.disable_news):
			disable_news=1
		if(bbs.violate_terms):
			disable_news=1
		if(thread.violate_terms):
			disable_news=1
			violate_terms=1
		if(thread.violate_photo):
			disable_news=1

		#4分未満の画像でアップロードでもない場合は新着に非表示
		#アップロード時は-1、iPhone時は0が入る
		#if(thread.draw_time and thread.draw_time!=-1 and thread.draw_time<240):
		#	disable_news=1

		adult=0
		if(thread.adult):
			adult=thread.adult

		if(bbs.short and bbs.short=="mopersample" and thread.illust_mode!=BbsConst.ILLUSTMODE_MOPER):
			disable_news=1;

		if(req):
			url_header="http://"+req.request.host
		else:
			url_header="."

		thumbnail_url=""
		thumbnail2_url=""
		if(thread.cached_image_key):
			thumbnail_url=url_header+"/thumbnail/"+str(thread.cached_image_key)
			thumbnail2_url=url_header+"/thumbnail2/"+str(thread.cached_image_key)
			if(thread.illust_mode==BbsConst.ILLUSTMODE_MOPER):
				thumbnail_url+=".gif"
				thumbnail2_url=thumbnail_url
			else:
				thumbnail_url+=".jpg"
				thumbnail2_url+=".jpg"

			#サムネイルの作成に失敗している場合は再作成を促す
			if(thread.thumbnail2_version!=BbsConst.THUMBNAIL2_VERSION):
				memcache.delete(BbsConst.OBJECT_CACHE_HEADER+str(thread.key()))

		if(bbs.del_flag):
			thumbnail_url=""
			thumbnail2_url=""

		create_date=TimeProgress.get_date_str(thread.create_date)

		thread_url=url_header+"/"
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
			image_url=url_header+"/img/"+str(thread.cached_image_key)+".jpg"
		#if(bbs.dont_permit_app or 
		if(bbs.del_flag):	#アプリでの画像データの参照を禁止
			image_url=""

		app=0
		if(thread.applause):
			app=thread.applause

		comment_cnt=0
		if(thread.comment_cnt):
			comment_cnt=thread.comment_cnt

		summary=ApiObject.truncate_html(thread.summary)

		user_id=""
		if(thread.user_id):
			user_id=thread.user_id

		tag_list=[]
		if(thread.tag_list):
			tag_list=thread.tag_list

		bookmark_cnt=0
		if(thread.bookmark_count):
			bookmark_cnt=thread.bookmark_count

		bbs_title=bbs.bbs_name
		bbs_url=ApiObject._get_bbs_url(req,bbs)

		one_dic={"title":thread.title,"summary":summary,"author":thread.author,
		"user_id":user_id,"thumbnail_url":thumbnail_url,"thumbnail2_url":thumbnail2_url,
		"image_url":image_url,"create_date":create_date,"thread_url":thread_url,
		"applause":app,"bookmark":bookmark_cnt,"comment":comment_cnt,"key":str(thread.key()),
		"disable_news":disable_news,"tag":tag_list,"width":thread.width,"height":thread.height,
		"version":thread.thumbnail2_version,"violate_terms":violate_terms,"create_date_original":thread.create_date,
		"bbs_title":bbs_title,"bbs_url":bbs_url,"adult":adult}
		
		return one_dic

#-------------------------------------------------------------------
#bbs object
#-------------------------------------------------------------------
	
	@staticmethod
	def _get_bbs_url(req,bbs):
		if(req):
			bbs_url="http://"+req.request.host+"/"
		else:
			bbs_url="."
		if(bbs.short):
			bbs_url+=bbs.short+"/"
		else:
			bbs_url+="usr/"+str(bbs.key())+"/"
		return bbs_url

	@staticmethod
	def create_bbs_object(req,bbs):
		if(not bbs):
			return None
	
		bookmark_cnt=0
		if(bbs.bookmark_count):
			bookmark_cnt=bbs.bookmark_count

		bbs_url=ApiObject._get_bbs_url(req,bbs)
		
		thumbnail_url=""
		if(bbs.cached_thumbnail_key and not bbs.del_flag):
			thumbnail_url="http://"+req.request.host+"/thumbnail/"+bbs.cached_thumbnail_key+".jpg"
		one_dic={"title":bbs.bbs_name,"bbs_url":bbs_url,"bookmark":bookmark_cnt,"key":str(bbs.key()),"thumbnail_url":thumbnail_url,"mode":bbs.bbs_mode}
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
	def _get_feed_entry_list(feed_list):
		entry_list=[]
		for feed in feed_list:
			if(feed==None):
				continue
			if(feed.feed_mode!="new_comment_thread"):
				continue
			try:
				entry_key=StackFeedData.entry_key.get_value_for_datastore(feed)
				if(entry_list.count(entry_key)==0):
					entry_list.append(entry_key)
				response_key=StackFeedData.response_key.get_value_for_datastore(feed)
				if(entry_list.count(response_key)==0):
					entry_list.append(response_key)
			except:
				None
		return entry_list

	@staticmethod
	def create_feed_object_list(req,feed_list,feed_key_list):
		#出現するユーザと掲示板を全てリストアップ
		user_list=ApiObject._get_feed_user_list(feed_list)
		bbs_list=ApiObject._get_feed_bbs_list(feed_list)
		thread_list=ApiObject._get_feed_thread_list(feed_list)
		entry_list=ApiObject._get_feed_entry_list(feed_list)
		
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
		
		#掲示板情報とスレッド情報をまとめて取得
		object_hash=ApiObject.get_cached_object_hash(bbs_list+thread_list+entry_list)

		#オブジェクト作成
		dic=[]
		feed_n=len(feed_list)
		for i in range(feed_n):
			feed=feed_list[i]
			feed_key=feed_key_list[i]
			one_dic=ApiObject.create_feed_object(req,feed,user_hash,object_hash,feed_key)
			if(one_dic==None):
				continue
			dic.append(one_dic)
		return dic

	@staticmethod
	def truncate_html(message):
		TAG_RE = re.compile(r'<[^>]+>')
		message=TAG_RE.sub('', message)

		TAG_SP = re.compile(r'&nbsp;')
		message=TAG_SP.sub(' ', message)

		split_length=40
		if(len(message)>=split_length):
			message=message[0:split_length]
			message=""+message+"..."
		return message

	@staticmethod
	def create_feed_object(req,feed,user_hash,object_hash,feed_key):
		#フィードが削除された
		if(feed==None):
			deleted_feed={"mode":"deleted","from_user":"","to_user":"","follow_user":"","bbs":"","thread":"","message":"ツイートは削除されました。","create_date":"","key":str(feed_key)}
			return deleted_feed

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
			bbs_object=object_hash[bbs_object_key]
			if(bbs_object):
				bbs=ApiObject.create_bbs_object(req,bbs_object)
			else:
				bbs=None
			if(not bbs):
				bbs={"title":"","bbs_url":""}	#deleted bbs
			
		#イベント発生スレッド取得
		thread_object_key=StackFeedData.thread_key.get_value_for_datastore(feed)
		thread=""
		if(thread_object_key):
			thread_object=object_hash[thread_object_key]
			if(thread_object):
				only_image=False
				thread=ApiObject._create_thread_object_core(req,thread_object,bbs_object,only_image)
			else:
				thread=None
			if(not thread):
				thread={"title":"","thread_url":""}	#deleted thread

		#発生日取得
		is_english=CssDesign.is_english(req)
		create_date=TimeProgress.get_date_diff_str(feed.create_date,"",is_english)
		
		#コメントを取得
		message=feed.message
		if(feed.feed_mode=="new_comment_thread"):
			message=ApiObject._get_entry_comment(feed,object_hash)

		#オブジェクトを返す
		one_dic={"mode":feed.feed_mode,"from_user":from_user,"to_user":to_user,"follow_user":follow_user,"bbs":bbs,"thread":thread,"message":message,"create_date":create_date,"key":str(feed.key())}
		return one_dic

	@staticmethod
	def _get_entry_comment(feed,object_hash):
		comment_deleted=False

		entry_key=StackFeedData.entry_key.get_value_for_datastore(feed)
		entry=object_hash[entry_key]
		#entry=ApiObject.get_cached_object(entry_key)
		if(entry_key):
			if(not entry or entry.del_flag==BbsConst.ENTRY_DELETED):
				comment_deleted=True

		#レス投稿フィードの場合のみres_keyを持つ
		#コメント投稿フィードの場合はres_keyにはNoneが入っている
		res_key=StackFeedData.response_key.get_value_for_datastore(feed)
		#res=ApiObject.get_cached_object(res_key)
		res=object_hash[res_key]
		if(res_key):
			if(not res):	#レスが削除された
				comment_deleted=True

		message=""
		if(comment_deleted):
			message="deleted"
		else:
			if(res):
				message=res.content
			else:
				if(entry):
					message=entry.content

		message=ApiObject.truncate_html(message)
		
		if(not comment_deleted):
			if(entry and not res):
				if(entry.illust_reply):
					image_key=Entry.illust_reply_image_key.get_value_for_datastore(entry)
					message="<img src='/thumbnail/"+str(image_key)+".jpg'/><br/>"+message

		return message

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
		
		limit=BbsConst.PINTEREST_MYPAGE_PAGE_UNIT
		if(req.request.get("limit")):
			limit=int(req.request.get("limit"))

		if(req.request.get("page")):
			page=int(req.request.get("page"))
			offset=limit*(page-1)
		
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
		
		#メモリからまとめて取得
		cache_list=memcache.get_multi(key_list,key_prefix=BbsConst.OBJECT_CACHE_HEADER)
		
		#キャッシュヒットしなかったものをDBに問い合わせる
		require_key_list=[]
		require_key_map={}
		for thread in all_threads:
			if(not (str(thread) in cache_list)):
				if(not (str(thread) in require_key_map)):
					if(thread):
						require_key_map[str(thread)]=len(require_key_list)
						one_key=thread
						if(type(one_key)==str):
							one_key=db.Key(encoded=one_key)
						require_key_list.append(one_key)

		object_list=[]
		if(len(require_key_list)):
			object_list=db.get(require_key_list)

		#キャッシュヒットしたものはキャッシュから、
		#ヒットしなかったものはdbから取ってくる
		all_threads_cached=[]
		put_multi_dic={}
		for thread in all_threads:
			if(str(thread) in cache_list):
				#キャッシュから取得
				data=cache_list[str(thread)]
				all_threads_cached.append(data)
			else:
				#dbから取得
				if(thread):
					no=require_key_map[str(thread)]
					data=object_list[no]
					ApiObject._update_object(data)
				else:
					data=None
				#data=ApiObject._get_datastore_object_no_mem_set(thread)
				all_threads_cached.append(data)
				cache_list[str(thread)]=data	#このループで同じものが参照された場合のため
				put_multi_dic[str(thread)]=data

		#メモリにまとめて格納
		if(len(put_multi_dic)):
			try:
				memcache.set_multi(put_multi_dic,key_prefix=BbsConst.OBJECT_CACHE_HEADER,time=BbsConst.OBJECT_CACHE_TIME)
			except:
				logging.warning("memset_multi_overflow trap")

		return all_threads_cached

	@staticmethod
	def get_cached_object(ds_obj):
		if(not ds_obj):
			return None
		if(type(ds_obj)==db.Key or type(ds_obj)==str):
			ds_obj_key=str(ds_obj)
		else:
			ds_obj_key=str(ds_obj.key())
		ret=memcache.get(BbsConst.OBJECT_CACHE_HEADER+ds_obj_key)
		if(ret):
			return ret
		return ApiObject.get_datastore_object(ds_obj)

	@staticmethod
	def _get_cached_entry_key(ds_obj):
		if(not ds_obj.comment_cnt):
			return []	#コメント数が0の場合は高速化のためQueryを走らせない
		query=db.Query(Entry,keys_only=True).filter("thread_key =",ds_obj).filter("del_flag =",1)
		if(ds_obj.bbs_key.default_comment_order==1):
			query.order("-create_date")
		else:
			query.order("-date")
		entry_list=query.fetch(limit=100)
		return entry_list

	@staticmethod
	def _update_thread(ds_obj):
		image_key=MesThread.image_key.get_value_for_datastore(ds_obj)
		if(image_key):
			ds_obj.cached_image_key=str(image_key)
			ImageFile.create_thumbnail2(ds_obj)

		bbs_key=MesThread.bbs_key.get_value_for_datastore(ds_obj)
		if(bbs_key):
			ds_obj.cached_bbs_key=str(bbs_key)
			
		#コメント一覧を取得
		#コメント更新時にはcached_entry_key=Noneで代入される
		if not ds_obj.cached_entry_key_enable:
			ds_obj.cached_entry_key=ApiObject._get_cached_entry_key(ds_obj)
			ds_obj.cached_entry_key_enable=True
			ds_obj.put()

		#検索インデックスに追加
		SearchThread.add_index(ds_obj)

	@staticmethod
	def _update_entry(ds_obj):
		#検索インデックスに追加
		SearchThread.add_index_entry(ds_obj)

	@staticmethod
	def _update_bbs(ds_obj):
		#現在はスレッド追加時にcached_thumbnail_keyを上書きしている
		#将来的にDSの以降などでkeyが変わる場合は以下のifをTrueにしてキャッシュを全更新すること
		if not ds_obj.cached_thumbnail_key:
			try:
				recent_thread=MesThread.all().filter("bbs_key =",ds_obj).order("-create_date").fetch(limit=1)
				if(recent_thread):
					image=recent_thread[0].image_key;
					if(image):
						ds_obj.cached_thumbnail_key=str(image.key());
						ds_obj.put()
			except:
				ds_obj.cached_thumbnail_key=""

		#スレッド数を更新する
		#スレッドの追加時にcached_threads_numにNoneが代入される
		if not ds_obj.cached_threads_num:
			ds_obj.cached_threads_num=MesThread.all().filter("bbs_key =",ds_obj).count()
			ds_obj.put()

	@staticmethod
	def _update_object(ds_obj):
		if(type(ds_obj)==MesThread):
			ApiObject._update_thread(ds_obj)
		if(type(ds_obj)==Entry):
			ApiObject._update_entry(ds_obj)
		if(type(ds_obj)==Bbs):
			ApiObject._update_bbs(ds_obj)

	@staticmethod
	def _get_datastore_object_no_mem_set(ds_obj):
		#keyの場合は実データを取得してくる
		if(type(ds_obj)==db.Key or type(ds_obj)==str):
			try:
				ds_obj=db.get(ds_obj);
			except:
				return None

		#データが見つからなかった
		if(not ds_obj):
			return None

		#データの更新
		ApiObject._update_object(ds_obj)

		return ds_obj

	@staticmethod
	def get_datastore_object(ds_obj):
		ds_obj=ApiObject._get_datastore_object_no_mem_set(ds_obj)
		if(ds_obj==None):
			return None
		try:
			memcache.set(BbsConst.OBJECT_CACHE_HEADER+str(ds_obj.key()),ds_obj,BbsConst.OBJECT_CACHE_TIME)
		except:
			logging.warning("memset_overflow trap")
		return ds_obj

#-------------------------------------------------------------------
#json return
#-------------------------------------------------------------------

	@staticmethod
	def write_json(req,dic):
		dic=ApiObject.add_json_success_header(dic)
		ApiObject.write_json_core(req,dic)
	
	@staticmethod
	def add_json_success_header(dic):
		return {"response":dic,"status":"success","message":""}
	
	class JsonDatetimeEncoder(json.JSONEncoder):
		def default(self, obj):
			if isinstance(obj, datetime.datetime):
				return str(obj)
			return json.JSONEncoder.default(self, obj)

	@staticmethod
	def write_json_core(req,dic):
		#JSONPかどうか
		callback_func=None
		if(req.request.get("callback")):
			callback_func=req.request.get("callback")
		
		#JSON作成
		json_code = json.dumps(dic, cls = ApiObject.JsonDatetimeEncoder)
		req.response.content_type = 'application/json'
		
		#JSONP作成
		if(callback_func):
			json_code=""+callback_func+"("+json_code+")"
		
		#返却
		req.response.out.write(json_code)