#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#
# 旧ランキング
# 現在はAPIに移行
# 日付だけ使われている

import datetime
import sys
import traceback

from google.appengine.ext import db
from google.appengine.api import memcache

from Entry import Entry
from MesThread import MesThread
from TopPageCache import TopPageCache

from UTC import UTC
from JST import JST
from BbsConst import BbsConst

import datetime

class ApplauseCache():
	@staticmethod
	def invalidate_new():
		return

	@staticmethod
	def get_date_str(value):
		tmp=value.replace(tzinfo=UTC()).astimezone(JST())
		return ""+str(tmp.year)+"/"+str(tmp.month)+"/"+str(tmp.day)

	@staticmethod
	def limit_title_string(title):
		length=10
		title=unicode(title,'utf-8') 
		if len(title) >= length: 
			title=title[:length] + '...' 
		return title
	
