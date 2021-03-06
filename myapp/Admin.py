#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#管理ページ
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import re
import os
import datetime

import template_select

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db

from myapp.MesThread import MesThread
from myapp.BbsConst import BbsConst
from myapp.Bbs import Bbs
from myapp.Entry import Entry
from myapp.SetUtf8 import SetUtf8
from myapp.UTC import UTC
from myapp.JST import JST
from myapp.PageGenerate import PageGenerate
from myapp.SiteAnalyzer import SiteAnalyzer
from myapp.OwnerCheck import OwnerCheck

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

		comment_page=1
		only_comment=0
		if self.request.get("comment_page"):
			comment_page = int(self.request.get("comment_page"))
			only_comment=1

		if(not only_comment):
			thread_query.filter("illust_mode =",1)
			thread=thread_query.fetch(limit=thread_page_unit,offset=(thread_page-1)*thread_page_unit)
		
			new_moper_query=MesThread.all().order("-create_date")
			new_moper_query.filter("illust_mode =",2)
			new_moper=new_moper_query.fetch(limit=12)

			entry=None
			try:
				entry_query = Entry.all().order('-create_date')
				entry_query.filter("illust_reply =",1)
				entry=entry_query.fetch(limit=thread_page_unit,offset=(thread_page-1)*thread_page_unit)
			except:
				None
		else:
			thread=None
			new_moper=None
			entry=None

		comment=None
		try:
			comment_unit=7
			comment_query = Entry.all().order('-create_date')
			comment_query.filter("del_flag =", 1)
			comment=comment_query.fetch(limit=comment_unit,offset=comment_unit*(comment_page-1))
		except:
			None

		if(not only_comment):
			new_bbs_count=SiteAnalyzer.create_graph(self,0);
			new_illust_count=SiteAnalyzer.create_graph(self,1);
			new_entry_count=SiteAnalyzer.create_graph(self,2);
			new_user_count=SiteAnalyzer.create_graph(self,3);

			today_start = datetime.datetime.today()
			week_start = today_start - datetime.timedelta(days=7)
			month1_start = today_start - datetime.timedelta(days=31)
		
			weekly=Bbs.all().filter("date >=",week_start).count(limit=10000)
			monthly=Bbs.all().filter("date >=",month1_start).count(limit=10000)
		else:
			new_bbs_count=0
			new_illust_count=0
			new_entry_count=0
			new_user_count=0
			weekly=0
			monthly=0

		if os.environ["SERVER_SOFTWARE"].find("Development")!=-1:
			new_moper=[]
			
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
			'comment_page':comment_page,
			'only_comment': only_comment
			}
		path = '/html/admin.html'
		render=template_select.render(path, template_values)
		self.response.out.write(render)		

