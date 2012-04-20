#!-*- coding:utf-8 -*-
#!/usr/bin/env python
# News

import os
import time
import sys
import urllib

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
#ニュースの表示
#--------------------------------------------------------

class NewsAccount(webapp.RequestHandler):
  @staticmethod
  def get_news():
    data=memcache.get("news_list")
    if data is None:
      return "ニュースの取得に失敗しました。<BR>"
    return data

  def get(self):
    SetUtf8.set()
    
    rss_list=NewsRss.all()
    
    page=self.request.get("page")

    template_values = {
      'rss_list': rss_list,
      'news': NewsAccount.get_news()
    }          
    path = os.path.join(os.path.dirname(__file__), 'news_account.htm')
    self.response.out.write(template.render(path, template_values))
    return

  def post(self):
    url=self.request.get("url")
    query = NewsRss.all()
    query.filter("url =",url)
    mes="<A HREF='news_update'>"
    import re
    update=0
    try:
        if(re.match("http.*",url) and (re.match(".*rdf",url) or re.match(".*rss",url)  or re.match(".*rss/",url) or re.match(".*xml",url) or re.match(".*default",url) or re.match(".*feed/",url) or re.match(".*comment",url))):
            count=query.count()
            if(count!=0) :
                if("news_rss_add"==self.request.get("mode")):
                    mes+="既に存在しています"
                else:
                    query[0].delete()
                    mes+="削除しました"
                    update=1
            else:
                if("news_rss_add"==self.request.get("mode")):
                    news=NewsRss()
                    news.url=url
                    news.put()
                    mes+="登録しました"
                    update=1
                else:
                    mes+="該当するURLが存在しません"
        else:
            mes+="このURLはRSSではありません(httpで始まりかつ拡張子がxmlかrdfかdefaultかfeed/かrss/かcommentである必要があります)"
    except:
        mes+="データベースアクセスに失敗"
    mes+="</A>"
    template_values = {
      'alert_msg': mes,
      'side_active_news': "_active",
    }          
    #path = os.path.join(os.path.dirname(__file__), 'cre_alert.htm')
    self.response.out.write(mes)#template.render(path, template_values))
    
        
