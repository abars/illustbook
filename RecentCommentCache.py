#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from google.appengine.ext import db
from google.appengine.api import memcache

from Entry import Entry
from MesThread import MesThread

class RecentCommentCache():
	@staticmethod
	def get_entry(bbs):
		key="recent_entry8_"
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
		if(bbs):
			key="recent_entry8_"+str(bbs.key())
			memcache.delete(key)
		key="recent_entry8_"
		memcache.delete(key)
