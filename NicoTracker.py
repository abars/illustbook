#!-*- coding:utf-8 -*-
#!/usr/bin/env python
# NicoTracker

import os
import time
import sys
import urllib
import re
import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import memcache

from SetUtf8 import SetUtf8
from NicoTrackerRec import NicoTrackerRec
from NicoTrackerBookmark import NicoTrackerBookmark

from UTC import UTC
from JST import JST
from Alert import Alert

#--------------------------------------------------------
#NicoTracker
#--------------------------------------------------------

webapp.template.register_template_library('templatetags.django_filter')

class NicoTracker(webapp.RequestHandler):
	@staticmethod
	def get_day_string(tmp):
		tmp=tmp.replace(tzinfo=UTC()).astimezone(JST())
		day_str=""+str(tmp.year)+"年"+str(tmp.month)+"月"+str(tmp.day)+"日"
		week=tmp.weekday()
		week_jp=["月","火","水","木","金","土","日"]
		day_str+="("+week_jp[week]+")"
		return day_str
	
	def update_url(self,url):
		#ID取得
		id=""
		m = re.search(r"http://www.nicovideo.jp/watch/([a-z0-9]*)", url)
		if(m):
			id=m.group(1)
		else:
			return None

		#サーチ
		query=NicoTrackerRec.all().filter("id = ",id)
		if(query.count()==0):
			rec=NicoTrackerRec()
		else:
			rec=query[0]
		
		#初期設定
		rec.url=url
		rec.id=id
		
		return self.update_core(rec,False)
	
	def update_core(self,rec,force):
		#1日単位で習得
		if(rec.date and len(rec.day_list)>=1 and not force):
			day1_str=NicoTracker.get_day_string(rec.date)
			day2_str=NicoTracker.get_day_string(datetime.datetime.today())
			if(day1_str==day2_str):
				return rec

		#ニコニコ動画からHTMLを取得
		try:
			result = urlfetch.fetch("http://www.nicovideo.jp/watch/"+rec.id)
		except:
			return rec

		#コメント数と再生数を取得
		play_n=""
		comment_n=""
		title=""
		
		if result.status_code == 200:
			m = re.search(r"再生数：<strong>([0-9,]*)</strong>", result.content)
			if(m):
				play_n=m.group(1)
				play_n=play_n.replace(",","");

			m = re.search(r"コメント数：<strong>([0-9,]*)</strong>", result.content)
			if(m):
				comment_n=m.group(1)
				comment_n=comment_n.replace(",","");

			m = re.search(r"<title>(.*)</title>", result.content)
			if(m):
				title=m.group(1)
		
		#取得失敗
		if(play_n=="" or comment_n=="" or title==""):
			return None
		
		#書き込み
		day_str=NicoTracker.get_day_string(datetime.datetime.today())
		
		rec.title=title#+" "+day1_str+"/"+day2_str
		rec.play_cnt_list.insert(0,play_n)
		rec.comment_cnt_list.insert(0,comment_n)
		rec.day_list.insert(0,day_str)
		
		#ランキング用
		try:
			rec.play_cnt_now=int(play_n)
			rec.comment_cnt_now=int(comment_n)
		except:
			a=None
		
		rec.put()

		return rec
	
	def auto_update(self):
		query=NicoTrackerRec.all()
		rec_list=query.fetch(limit=10000)
		for rec in rec_list:
			self.update_core(rec,False)
	
	@staticmethod
	def create_graph(day_list,play_cnt_list):
		play_cnt_graph=""
		day_list_len=len(day_list)
		for i in range(0,day_list_len):
			day_str="data.setValue("+str(i)+",0,'"+day_list[day_list_len-1-i]+"');\n";
				
			play_cnt_graph+=day_str
			play_cnt_graph+="data.setValue("+str(i)+",1,"+str(play_cnt_list[day_list_len-1-i])+");\n";
				
		play_cnt_graph="data.addRows("+str(day_list_len)+");\n"+play_cnt_graph
		return play_cnt_graph

#--------------------------------------------------------
#ブックマーク機能
#--------------------------------------------------------

	@staticmethod
	def get_bookmark(user):
		if(not user):
			return None
		bookmark_query=NicoTrackerBookmark.all().filter("user_id =",user.user_id())
		if(bookmark_query.count()==0):
			bookmark=NicoTrackerBookmark()
			bookmark.user_id=user.user_id()
			bookmark.bookmark_id_list=[]
			bookmark.bookmark_title_list=[]
			bookmark.put()	
			return bookmark
		return bookmark_query[0]
	
	@staticmethod
	def add_bookmark(bookmark,key,title):
		if(not bookmark):
			return
		if(bookmark.bookmark_id_list.count(key)==0):
			bookmark.bookmark_id_list.insert(0,key)
			bookmark.bookmark_title_list.insert(0,title)
			bookmark.put()
	
	@staticmethod
	def del_bookmark(bookmark,key):
		if(not bookmark):
			return
		no=bookmark.bookmark_id_list.index(key)
		bookmark.bookmark_id_list.pop(no)
		bookmark.bookmark_title_list.pop(no)
		bookmark.put()

#--------------------------------------------------------
#メイン
#--------------------------------------------------------

	def get(self):
		SetUtf8.set()
		
		#ブックマーク制御
		user = users.get_current_user()
		bookmark=NicoTracker.get_bookmark(user)
		if(self.request.get("add_bookmark")):
			NicoTracker.add_bookmark(bookmark,self.request.get("id"),self.request.get("title"))
		if(self.request.get("del_bookmark")):
			NicoTracker.del_bookmark(bookmark,self.request.get("id"))
		url_log = users.create_logout_url(self.request.uri)
		if(not user):
			url_log = users.create_login_url(self.request.uri)
			
		url = ""#http://www.nicovideo.jp/watch/sm15521745"
		if(self.request.get("url")):
			url=self.request.get("url")
		
		if(url==""):
			rec=None
		else:
			if(url=="update_all"):
				rec=self.auto_update()
			else:
				rec=self.update_url(url)
		
		play_cnt_graph=""
		comment_cnt_graph=""
		list_tbl=""
		if(rec):
			#GRAPH
			play_cnt_graph=NicoTracker.create_graph(rec.day_list,rec.play_cnt_list);
			comment_cnt_graph=NicoTracker.create_graph(rec.day_list,rec.comment_cnt_list);
			
			#TABLE
			no=0
			for day in rec.day_list:
				list_tbl+="<TR><TD>"+day+"</TD>"
				list_tbl+="<TD>"+rec.play_cnt_list[no]+"</TD>"
				list_tbl+="<TD>"+rec.comment_cnt_list[no]+"</TD></TR>\n"
				no=no+1
		
		query=NicoTrackerRec.all()
		rec_cnt=query.count()
		rec_list=query.order("-play_cnt_now").fetch(limit=10)
		
		bookmark_list=[]
		if(bookmark):
			for i in range(0,len(bookmark.bookmark_id_list)):
				playcnt=0
				try:
					playcnt=NicoTrackerRec.all().filter("id =",bookmark.bookmark_id_list[i])[0].play_cnt_now
				except:
					playcnt=0
				if(playcnt==None):
					playcnt=0
				url_base="http://www.nicovideo.jp/watch/"
				
				#del_button="<div class='delete_button' onClick='click_delete(\""
				del_button="<img src='static_files/nicotra/book.gif' onClick='click_delete(\""
				del_button+=bookmark.bookmark_id_list[i]
				del_button+="\",\""+url+"\");'>";
				#del_button+="del</div>";
				
				title=bookmark.bookmark_title_list[i].split(" ‐ ")[0]
				#if(len(title)>=30):
				#	title=title[0:30]+"…"
				
				bookmark_list.append(del_button+"<A HREF='nico_tracker?url="+url_base+bookmark.bookmark_id_list[i]+"'>"+title+"</A>　"+str(playcnt)+"[play]　");
		
		is_anim_icon=self.request.get("is_anim_icon")

		host_url =self.request.host
		template_values = {
			'host': host_url,
			'rec': rec,
			'rec_list': rec_list,
			'url': url,
			'play_cnt_graph': play_cnt_graph,
			'comment_cnt_graph': comment_cnt_graph,
			'list_tbl': list_tbl,
			'rec_cnt': rec_cnt,
			'user': user,
			'bookmark_list': bookmark_list,
			'url_log': url_log,
			'is_anim_icon': is_anim_icon
			}
		
		path = os.path.join(os.path.dirname(__file__), 'nico_tracker.html')
		render=template.render(path, template_values)
		self.response.out.write(render)		


