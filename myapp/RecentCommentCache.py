#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#最近投稿されたコメントの一覧を作成する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import memcache

from myapp.Entry import Entry
from myapp.MesThread import MesThread
from myapp.BbsConst import BbsConst
from myapp.ApiObject import ApiObject

class RecentCommentCache():
	@staticmethod
	def get_thread(bbs):
		if(not bbs):
			return None

		key=BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_THREAD_CACHE_HEADER+str(bbs.key())

		display_n=8
		if(bbs.recent_thread_n):
			display_n=bbs.recent_thread_n
		if(display_n<0):
			return None

		data = memcache.get(key)
		if data:
			return data

		thread_query = MesThread.all().order("-create_date");
		thread_query.filter('bbs_key =', bbs)
		thread_list=thread_query.fetch(display_n);
		thread_array=[]
		for thread in thread_list:
			mee={'short': str(thread.short),
					'thread_key':str(thread.key()),
					'title':str(thread.title),
					'date':thread.date}
			thread_array.append(mee)
		memcache.add(key, thread_array, BbsConst.SIDEBAR_RECENT_THREAD_CACHE_TIME)
		return thread_array

	@staticmethod
	def get_entry(bbs):
		if(not bbs):
			return None
	
		key=BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_ENTRY_CACHE_HEADER+str(bbs.key())
		
		display_n=8
		if(bbs.recent_comment_n):
			display_n=bbs.recent_comment_n
		if(display_n<0):
			return None

		data = memcache.get(key)
		if data:
			return data
		
		entry_query = db.Query(Entry,keys_only=True)
		entry_query.order("-date");
		entry_query.filter("del_flag =",BbsConst.ENTRY_EXIST)
		entry_query.filter('bbs_key =', bbs)

		entry_key_list=entry_query.fetch(display_n)
		entry_list=ApiObject.get_cached_object_list(entry_key_list)

		thread_key_list=[]
		res_key_list=[]
		thread_to_res={}
		for entry in entry_list:
			thread_key=Entry.thread_key.get_value_for_datastore(entry)
			thread_key_list.append(thread_key)
			res_n=len(entry.res_list)
			if(res_n>=1):
				res_key=entry.res_list[res_n-1]
				res_key_list.append(res_key)
				thread_to_res[thread_key]=res_key
			else:
				thread_to_res[thread_key]=None
		thread_list=ApiObject.get_cached_object_hash(thread_key_list)
		res_list=ApiObject.get_cached_object_hash(res_key_list)

		entry_array=[]
		for entry in entry_list:
			#if(True):
			try:
				thread_key=Entry.thread_key.get_value_for_datastore(entry)
				thread=thread_list[thread_key]
				thread_title=thread.title

				#URLに使用するキーを決定
				if(thread.short):
					thread_short=thread.short
				else:
					thread_short=thread_key

				#レスが付いている場合は一番新しいレスの投稿者名を表示
				if(thread_to_res[thread_key]):
					editor=res_list[thread_to_res[thread_key]].editor
				else:
					editor=entry.editor
				
				mee={'short': str(bbs.short),
						'bbs_key' : str(bbs.key()),
						'thread_key':thread_short,
						'thread_title':thread_title+"("+editor+")",
						'date':entry.date}
				entry_array.append(mee)
			except:
				continue
		
		memcache.add(key, entry_array, BbsConst.SIDEBAR_RECENT_ENTRY_CACHE_TIME)
		return entry_array
		
	@staticmethod
	def invalidate(bbs):
		key=BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_ENTRY_CACHE_HEADER
		if(bbs):
			memcache.delete(key+str(bbs.key()))
		memcache.delete(key)

		key=BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_THREAD_CACHE_HEADER
		if(bbs):
			memcache.delete(key+str(bbs.key()))
		memcache.delete(key)
