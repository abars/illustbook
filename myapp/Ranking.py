#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ランキング
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import datetime;
import time;
import json;

from google.appengine.ext import db
from google.appengine.api.labs import taskqueue

from myapp.BbsConst import BbsConst
from myapp.ApiObject import ApiObject
from myapp.MesThread import MesThread

class Ranking(db.Model):
	#カウンターの加算時と、拍手時、ブックマーク時にスレッドとユーザを追加する
	thread_list = db.ListProperty(db.Key,indexed=False)
	user_list = db.StringListProperty(indexed=False)
	
	#イラストのランキング結果と、ユーザのランキング結果を格納
	#ランキングの更新はBackendで行う
	ranking_list = db.ListProperty(db.Key,indexed=False)
	user_id_ranking_list = db.StringListProperty(indexed=False)
	user_ranking_list = db.StringListProperty(indexed=False)

	#掲示板のオーナーランクは廃止
	#owner_list = db.StringListProperty(indexed=False)
	#owner_ranking_list = db.StringListProperty(indexed=False)
	#owner_id_ranking_list = db.StringListProperty(indexed=False)

	date = db.DateTimeProperty(auto_now=True,indexed=False)
	
	def reset(self):
		self.thread_list=[]
	
	def _add_rank_core(self,key,key_list,n):
		if(not key):
			return
		content_len=len(key_list)
		while(content_len>=n):
			key_list.pop(0)
			content_len=content_len-1
		key_list.append(key)
	
	@staticmethod
	def add_rank_global(thread,score):	
		headers={'X-AppEngine-FailFast' : 'true'} #新規インスタンスの作成の抑制
		try:
			taskqueue.add(url="/add_ranking_score",params={"thread":str(thread.key()),"score":score},queue_name="score",headers=headers)
		except:
			logging.warning("ranking score taskqueue add failed")

	def add_rank(self,thread,score):
		if(thread.illust_mode==BbsConst.ILLUSTMODE_ILLUST):
			for cnt in range(score):
				self._add_rank_core(thread.key(),self.thread_list,BbsConst.THREAD_RANKING_RECENT)
				self._add_rank_core(thread.user_id,self.user_list,BbsConst.USER_RANKING_RECENT)
				#self._add_rank_core(thread.bbs_key.user_id,self.owner_list,BbsConst.USER_RANKING_RECENT)
			self.put()

	def get_sec(self,now):
		return int(time.mktime(now.timetuple()))

	def create_rank(self,req):
		self.create_thread_rank()
		
		rank=self.create_user_rank(self.user_list,req)
		self.user_ranking_list=rank["user"]
		self.user_id_ranking_list=rank["user_id"]
		
		#rank=self.create_user_rank(self.owner_list)
		#self.owner_ranking_list=rank["user"]
		#self.owner_id_ranking_list=rank["user_id"]

		self.owner_list = []
		self.owner_ranking_list = []
		self.owner_id_ranking_list = []
		
		self.put()
	
	def create_user_rank(self,user_list,req):
		rank_user={}
		
		for user_id in user_list:
			if(user_id):
				if(rank_user.has_key(user_id)):
					rank_user[user_id]=rank_user[user_id]+1
				else:
					rank_user[user_id]=1

		ranking_list=[]
		user_id_list=[]

		no=1
		for k, v in sorted(rank_user.items(), key=lambda x:x[1], reverse=True):
			bookmark=ApiObject.get_bookmark_of_user_id(k)
			if(not bookmark):
				continue
			if(bookmark and bookmark.disable_rankwatch):
				continue
			name=bookmark.name
			profile=bookmark.profile
			
			query=db.Query(MesThread)
			query=query.filter("illust_mode =",BbsConst.ILLUSTMODE_ILLUST)
			query=query.filter("user_id =",k).order("-create_date")
			try:
				thread_list=query.fetch(offset=0,limit=1)
				req_for_host=None
				thread=ApiObject.create_thread_object(req_for_host,thread_list[0])
				thumbnail_url=thread["thumbnail_url"]
				thread_url=thread["thread_url"]
			except:
				thumbnail_url=""
				thread_url=""

			dic={"no":no,"user_id":k,"name":name,"thumbnail_url":thumbnail_url,"thread_url":thread_url}
			no=no+1

			try:
				ranking_list.append(json.dumps(dic))
			except:
				ranking_list.append("overflow")

			user_id_list.append(k)

			if(len(ranking_list)>=BbsConst.USER_RANKING_MAX):
				break

		return {"user":ranking_list,"user_id":user_id_list}
	
	def create_thread_rank(self):
		#ハッシュにthread_keyを入れていく
		rank={}
		for thread in self.thread_list:
			if(rank.has_key(thread)):
				rank[thread]=rank[thread]+1
			else:
				rank[thread]=1
		
		#1次ランキングを作成
		first_ranking_list=[]
		for k, v in sorted(rank.items(), key=lambda x:x[1], reverse=True):
			if(v>=1):
				first_ranking_list.append(k)
				if(len(first_ranking_list)>=BbsConst.THREAD_RANKING_MAX*2):
					break
		
		#1次ランキングに出現したもののスコア補正（全てでthreadの実体を取得すると重いので）
		for k in first_ranking_list:
			#スレッドの実体を取得
			thread=ApiObject.get_cached_object(k)
			
			#イラストモードだけ
			if(not thread or thread.illust_mode!=BbsConst.ILLUSTMODE_ILLUST):
				rank[k]=0
				continue
			
			#経過日数
			day_left=(self.get_sec(datetime.datetime.now())-self.get_sec(thread.create_date))/60/60/24
			day_left=day_left/7+1	#1週間で1/2
		
		#ランキング作成
		self.ranking_list=[]
		for k, v in sorted(rank.items(), key=lambda x:x[1], reverse=True):
			self.ranking_list.append(k)
			if(len(self.ranking_list)>=BbsConst.THREAD_RANKING_MAX):
				break
		
	def get_rank(self,offset,limit):
		if(not self.ranking_list):
			return []
		return self.ranking_list[offset:offset+limit]
	
	def get_rank_core(self,user_id,list):
		try:
			return list.index(user_id)+1
		except:
			return 0
	
	def get_user_rank(self,user_id):
		return self.get_rank_core(user_id,self.user_id_ranking_list)

	def get_owner_rank(self,user_id):
		return 1#self.get_rank_core(user_id,self.owner_id_ranking_list)
		
