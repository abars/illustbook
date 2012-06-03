#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ランキング
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import datetime;
import time;

from google.appengine.ext import db

from myapp.BbsConst import BbsConst
from myapp.ApiObject import ApiObject

class Ranking(db.Model):
	thread_list = db.ListProperty(db.Key)
	user_list = db.StringListProperty()
	owner_list = db.StringListProperty()
	
	ranking_list = db.ListProperty(db.Key)
	owner_ranking_list = db.StringListProperty()
	user_ranking_list = db.StringListProperty()

	date = db.DateTimeProperty(auto_now=True)
	
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
	
	def add_rank(self,thread):
		if(thread.illust_mode==BbsConst.ILLUSTMODE_ILLUST):
			self._add_rank_core(thread.key(),self.thread_list,BbsConst.THREAD_RANKING_RECENT)
			self._add_rank_core(thread.bbs_key.user_id,self.owner_list,BbsConst.USER_RANKING_RECENT)
			self._add_rank_core(thread.user_id,self.user_list,BbsConst.USER_RANKING_RECENT)
			self.put()

	def get_sec(self,now):
		return int(time.mktime(now.timetuple()))

	def create_rank(self):
		self.create_thread_rank()
		self.user_ranking_list=self.create_user_rank(self.user_list)
		self.owner_ranking_list=self.create_user_rank(self.owner_list)
		self.put()
	
	def create_user_rank(self,user_list):
		rank_user={}
		
		for user_id in user_list:
			if(user_id):
				if(rank_user.has_key(user_id)):
					rank_user[user_id]=rank_user[user_id]+1
				else:
					rank_user[user_id]=1

		ranking_list=[]
		for k, v in sorted(rank_user.items(), key=lambda x:x[1], reverse=True):
			ranking_list.append(k)
			if(len(ranking_list)>=BbsConst.USER_RANKING_MAX):
				break

		return ranking_list
	
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
			
			#拍手とブックマークスコアを加算
			if(thread.applause):
				rank[k]=rank[k]+thread.applause/day_left
			if(thread.bookmark_count):
				rank[k]=rank[k]+thread.bookmark_count/day_left
		
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
		cnt=1
		for i in list:
			if(i==user_id):
				return cnt
			cnt=cnt+1
		return 0
	
	def get_user_rank(self,user_id):
		return self.get_rank_core(user_id,self.user_ranking_list)

	def get_owner_rank(self,user_id):
		return self.get_rank_core(user_id,self.owner_ranking_list)
		
