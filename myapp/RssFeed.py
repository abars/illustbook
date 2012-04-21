#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#RSSを作成する
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import memcache

from django.utils import feedgenerator

from SetUtf8 import SetUtf8
from MappingId import MappingId
from Bbs import Bbs
from MesThread import MesThread
from Entry import Entry
from BbsConst import BbsConst

class RssFeed(webapp.RequestHandler):
	@staticmethod
	def generate_feed(bbs,bbs_key):
		url=MappingId.get_usr_url("http://www.illustbook.net/",bbs)
		feed=feedgenerator.Rss201rev2Feed(title=bbs.bbs_name,link=url,feed_url=url,description=bbs.summary,language="ja")
		
		if(bbs.bbs_mode==BbsConst.BBS_MODE_NO_IMAGE):
			entry_query = Entry.all().filter('bbs_key =',bbs)
			entry_query.order('-date')
			all_entry = entry_query.fetch(limit=20)
			for entry in all_entry:
				thread=entry.thread_key
				url2=url+str(thread.key())+".html"
				txt=""+entry.editor+"("+str(entry.date)+")<BR>"
				
				if(entry.illust_reply):
					txt+="<IMG SRC='http://www.illustbook.net/img?img_id='"
					txt+=str(entry.illust_reply_image_key.key())+"'><BR>"
				txt+=entry.content

				for res in entry.res_list:
					response=db.get(res)
					txt+="<BR><BR>"+response.editor+"("+str(response.date)+")<BR>"
					txt+=""+response.content+"<BR>"
				
				feed.add_item(title=thread.title,link=url2,description=txt,author_email="",author_name=entry.editor,author_link=entry.homepage_addr,pubdate=entry.date)
		else:		
			thread_query = MesThread.all().filter('bbs_key =', bbs)
			thread_query.order('-create_date')			
			all_threads = thread_query.fetch(limit=20)

			for thread in all_threads:
				url2=url+str(thread.key())+".html"
				if(thread.image_key):
					thumbnail="http://www.illustbook.net/img?img_id="+str(thread.image_key.key())
					feed.add_item(title=thread.title,link=url2,description="<IMG SRC="+thumbnail+"><BR>"+thread.summary,author_email="",author_name=thread.author,author_link=thread.homepage_addr,pubdate=thread.create_date)
		result=feed.writeString('utf-8')
		
		return result

	def get(self,bbs_key):
		SetUtf8.set()
		bbs_key_original=bbs_key

		#キャッシュに存在するか判定
		result=memcache.get("feed_"+bbs_key_original)
		#result=None
		if(not result):
			#キャッシュに存在しない場合はRSS作成
			
			#掲示板取得
			bbs_key=MappingId.mapping(bbs_key)
			bbs=None
			try:
				bbs=db.get(bbs_key)
			except:
				bbs=None
			if(bbs==None):
				self.error(404)
				return
			
			#feedを作成
			result=RssFeed.generate_feed(bbs,bbs_key)
			
			#キャッシュに入れる
			memcache.set("feed_"+bbs_key_original,result,60*60*3)	#3時間
			
		self.response.headers['Content-Type']='text/xml; charset=utf-8'
		self.response.out.write(result)
		

