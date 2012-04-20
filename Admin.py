#!-*- coding:utf-8 -*-
#!/usr/bin/env python
#管理ページ
#

import re
import os
import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db

from MesThread import MesThread
from BbsConst import BbsConst
from Bbs import Bbs
from Entry import Entry
from SetUtf8 import SetUtf8
from UTC import UTC
from JST import JST
from PageGenerate import PageGenerate
from SiteAnalyzer import SiteAnalyzer
from OwnerCheck import OwnerCheck

webapp.template.register_template_library('templatetags.django_filter')

class Admin(webapp.RequestHandler):
	#remove
	def count_bbs(self,bbs,mode):
		new_bbs_count=[]
		cnt=0
		day_str=""
		before_day=""
		
		first_skip=1

		for one_bbs in bbs:
			try:
				if(mode==1):
					tmp=one_bbs.create_date	#entry
				else:
					if(mode==2):
						tmp=one_bbs.create_date	#thread
					else:
						tmp=one_bbs.create_date	#bbs
				tmp=tmp.replace(tzinfo=UTC()).astimezone(JST())
			except:
				continue

			bbs_day=str(tmp.month)+"/"+str(tmp.day)
			if(bbs_day==before_day):
				cnt=cnt+1
			else:
				if(cnt!=0):
					if(first_skip):
						first_skip=0	#当日は未確定なのでスキップ
					else:
						new_bbs_count.insert(0,str(cnt))
						new_bbs_count.insert(0,day_str)

				day_str=""+str(tmp.month)+"月"+str(tmp.day)+"日"
				week=tmp.weekday()
				week_jp=["月","火","水","木","金","土","日"]
				day_str+="("+week_jp[week]+")"
				
				before_day=bbs_day
				
				cnt=1

		#当日は表示しない
		if(cnt!=0):
			new_bbs_count.insert(0,str(cnt))
			new_bbs_count.insert(0,day_str)

		no=0
		select=0
		new_bbs_count_str=""
		for data in new_bbs_count:
			if(select==0):
				new_bbs_count_str+="data.setValue("+str(no)+",0,'"+data+"');\n";
			else:
				new_bbs_count_str+="data.setValue("+str(no)+",1,"+data+");\n";
				no=no+1
			select=1-select

		return "data.addRows("+str(no)+");\n"+new_bbs_count_str
		
	def get(self):
		user = users.get_current_user()
		is_admin=0
		is_high_admin=0
		account="ログインしていない状態"
		if(user):
			account="アカウント"+user.email()
			is_admin=1
			if(OwnerCheck.is_admin(user)):
				is_high_admin=1

		SetUtf8.set()

		thread_query = MesThread.all().order('-create_date')
		cnt=thread_query.count(10000)

		thread_page_unit=12
		thread_page=1
		if self.request.get("page"):
			thread_page = int(self.request.get("page"))
		thread_page_list=PageGenerate.generate_page(thread_page,cnt,thread_page_unit)

		thread_query.filter("illust_mode =",1)
		thread=thread_query.fetch(limit=thread_page_unit,offset=(thread_page-1)*thread_page_unit)
		
		new_moper_query=MesThread.all().order("-create_date")
		new_moper_query.filter("illust_mode =",2)
		new_moper=new_moper_query.fetch(limit=12)

		comment=None
		try:
			comment_query = Entry.all().order('-create_date')
			comment_query.filter("del_flag =", 1)
			comment=comment_query.fetch(limit=5)
		except:
			None

		entry=None
		try:
			entry_query = Entry.all().order('-create_date')
			entry_query.filter("illust_reply =",1)
			entry=entry_query.fetch(limit=thread_page_unit)
		except:
			None
		
#		new_bbs=None
#		try:
#			new_bbs_query = Bbs.all().order("-create_date")
#			new_bbs=new_bbs_query.fetch(limit=40)
#		except:
#			None

#		update_bbs=None	#投稿されたコメント
#		try:
#			update_bbs_query = Entry.all().order('-create_date')
#			update_bbs=update_bbs_query.fetch(limit=100)
#		except:
#			None

#		new_illust=None
#		try:
#			new_illust_query = MesThread.all().order("-create_date")
#			new_illust=new_illust_query.fetch(limit=200)
#		except:
#			None

#		new_bbs_count=self.count_bbs(new_bbs,0)
#		update_bbs_count=self.count_bbs(update_bbs,1)
#		new_illust_count=self.count_bbs(new_illust,2)
		
		new_bbs_count=SiteAnalyzer.create_graph(self,0);
		new_illust_count=SiteAnalyzer.create_graph(self,1);
		new_entry_count=SiteAnalyzer.create_graph(self,2);
		new_user_count=SiteAnalyzer.create_graph(self,3);

		today_start = datetime.datetime.today()
		week_start = today_start - datetime.timedelta(days=7)
		month1_start = today_start - datetime.timedelta(days=31)
		#month6_start = today_start - datetime.timedelta(days=31*6)
		
		weekly=Bbs.all().filter("date >=",week_start).count(limit=10000)
		monthly=Bbs.all().filter("date >=",month1_start).count(limit=10000)
		#monthly6=Bbs.all().filter("date >=",month6_start).count(limit=10000)
		
		host_url ="./"
		template_values = {
			'host': host_url,
			'threads':thread,
			'moper_threads':new_moper,
			'entries':entry,
			'comment':comment,
			'new_bbs_count':new_bbs_count,
			'new_entry_count':new_entry_count,
			'new_illust_count':new_illust_count,
			'new_user_count':new_user_count,
			'is_admin':is_admin,
			'is_high_admin': is_high_admin,
			'account':account,
			'url_logout':users.create_logout_url("./admin"),
			'url_login':users.create_login_url("./admin"),
			'page_list':thread_page_list,
			'page_url_base':"./admin?page=",
			'page':thread_page,
			'weekly':weekly,
			'monthly':monthly,
			#'monthly6':monthly6,
			}
		path = os.path.join(os.path.dirname(__file__), 'admin.htm')
		render=template.render(path, template_values)
		self.response.out.write(render)		

