#!-*- coding:utf-8 -*-
#!/usr/bin/env python
# News

import os
import time
import sys
import urllib
import re

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import memcache

from SetUtf8 import SetUtf8
from NewsRss import NewsRss
   
#--------------------------------------------------------
#ニュースの更新
#--------------------------------------------------------

class NewsUpdate(webapp.RequestHandler):
  def get(self):
    SetUtf8.set()
    
    try:
        query = NewsRss.all()
        news_rsss=query.fetch(limit=1000,offset=0)
    except:
        self.response.out.write("no rss found")
        return    
    
    entry_list=[]
    rss=""
    for news_rss in news_rsss:
        try:
            url=news_rss.url
            d=self.parse_feed(url)
            for entry in d.entries:
                if(re.match("PR:",entry.title) or re.match("[PR]",entry.title)):
                    continue;
                entry.date="<A HREF='"+d.feed.link+"' TARGET=_BLANK>"+d.feed.title+"</A>"
                entry_list.append(entry)
            rss+="<A HREF='"+d.feed.link+"' TARGET=_BLANK>"+d.feed.title+"</A>"
        except:
            rss+="取得失敗"
        rss+="（"+news_rss.url+"）<BR>"        
    entry_list.sort(lambda x, y: cmp(y.updated_parsed, x.updated_parsed))

    news=[]
    cnt=0
    for entry in entry_list:
        news.append("<A HREF='"+entry.link+"' TARGET=_BLANK>"+entry.title+"</A>／"+entry.date+"<BR>")
        cnt=cnt+1
        if(cnt>=7):
        	break

	template_values = {
		'news_list':news
	}
	path = os.path.join(os.path.dirname(__file__), 'news_core.htm')
	render=template.render(path, template_values)
		
	memcache.set("news_list",render,60*60*3)

    self.response.out.write("<A HREF='news_account'>updated finish</A><BR><BR>"+render)

  def parse_feed(self,url):
    import feedparser
    result = urlfetch.fetch(url)
    if result.status_code == 200:
        d=feedparser.parse(result.content)
    else:
        return null
    if d.bozo == 1:
        return null
    return d    
