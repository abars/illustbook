#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#最近投稿されたコメントの一覧を作成する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import db
from google.appengine.api import memcache

from Entry import Entry
from MesThread import MesThread
from BbsConst import BbsConst

class RecentCommentCache():
	@staticmethod
	def get_entry(bbs):
		key=BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_ENTRY_CACHE_HEADER
		
		display_n=8
		if(bbs):
			key+=str(bbs.key())
			if(bbs.recent_comment_n):
				display_n=bbs.recent_comment_n
		if(display_n<0):
			return None
		data = memcache.get(key)
		if data is not None:
			return data
		else:
			entry_query = Entry.all().order("-date");
			entry_query.filter("del_flag =",1)
			if(bbs):
				entry_query.filter('bbs_key =', bbs)
			entry_list=entry_query.fetch(display_n);
			entry_array=[]
			for entry in entry_list:
				try:
					if(not bbs and entry.thread_key.bbs_key.disable_news):
						continue;
					thread_key=str(entry.thread_key.key())
					if(entry.thread_key.short):
						thread_key=entry.thread_key.short
					editor=entry.editor
					if(entry.last_update_editor):	#for res update
						editor=entry.last_update_editor
					mee={'short': str(entry.thread_key.bbs_key.short),
							'bbs_key' : str(entry.thread_key.bbs_key.key()),
							'thread_key':thread_key,
							'thread_title':str(entry.thread_key.title)+"("+editor+")",
							'date':entry.date}
					entry_array.append(mee)
				except:
					mee=""
			memcache.add(key, entry_array, 60*60*24)
			return entry_array
		
	@staticmethod
	def invalidate(bbs):
		key=BbsConst.OBJECT_CACHE_HEADER+BbsConst.OBJECT_ENTRY_CACHE_HEADER
		if(bbs):
			memcache.delete(key+str(bbs.key()))
		memcache.delete(key)
