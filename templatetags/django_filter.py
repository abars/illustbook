#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#テンプレートエンジンから参照する関数
#copyright 2010-2012 ABARS all rights reserved.
#---------------------------------------------------

import datetime
import sys
import traceback
import re

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
register = webapp.template.create_template_register()

from myapp.UTC import UTC
from myapp.JST import JST
from myapp.Bookmark import Bookmark
from myapp.ApiObject import ApiObject
from myapp.BbsConst import BbsConst
from myapp.TimeProgress import TimeProgress

#-----------------------------------------------------------------
# 時間取得
#-----------------------------------------------------------------

def time_JST_format(value,mode):
	tmp=value.replace(tzinfo=UTC()).astimezone(JST())
	if(not mode):
		return ""+str(tmp.year)+"年"+str(tmp.month)+"月"+str(tmp.day)+"日"+str(tmp.hour)+"時"+str(tmp.minute)+"分"
	if(mode==1):
		return ""+str(tmp.year)+"年"+str(tmp.month)+"月"+str(tmp.day)+"日"+str(tmp.hour)+"時"
	if(mode==2):
		return ""+str(tmp.year)+"年"+str(tmp.month)+"月"+str(tmp.day)+"日"

	if(mode==10):
		return ""+str(tmp.month)+"月"+str(tmp.day)+"日"+str(tmp.hour)+"時"
	if(mode==11):
		return ""+str(tmp.month)+"月"+str(tmp.day)+"日"
	return "NO FORMAT"

def time_JST(value):
	return time_JST_format(value,0)

def time_JST_short(value):
	return time_JST_format(value,10)

def time_JST_progress(value):
	return TimeProgress.get_date_diff_str(value,"前")
	
#-----------------------------------------------------------------
#絵で返信
#-----------------------------------------------------------------

def reply_with_except(entry,host):
	try:
		ret="<a href='"+host
		if(entry.bbs_key.short and entry.bbs_key.short!="None") :
			ret+=str(entry.bbs_key.short)
		else:
			ret+="usr/"+str(entry.bbs_key.key())
		ret+="/"
		if(entry.thread_key.short):
			ret+=entry.thread_key.short
		else:
			ret+=str(entry.thread_key.key())
		ret+=".html' class='imagelink'>"
		ret+="<img src='"+host+"thumbnail/"+str(entry.illust_reply_image_key.key())+".jpg' border='0' "
		ret+="alt='"+str(entry.thread_key.title)+"'>/"
		ret+="</a>"
	except:
		return ""#+traceback.format_exc()
	return ret

def image_key_with_except(thread):
	try:
		return str(thread.image_key.key())
	except:
		return ""

#-----------------------------------------------------------------
#新着コメント表記
#-----------------------------------------------------------------

def comment_with_except(entry,host):
	return comment_with_except_core(entry,host,0)

def comment_with_except_no_hour(entry,host):
	return comment_with_except_core(entry,host,1)

def comment_with_except_core(entry,host,no_hour):
	try:
		ret="<a href='"+host;
		if(entry["short"] and entry["short"]!="None") :
			ret+=str(entry["short"])
		else:
			ret+="usr/"+str(entry["bbs_key"])
		ret+="/"
		ret+=str(entry["thread_key"])
		ret+=".html' class='decnone'>"
		title=str(entry["thread_title"])
		ret+=title
		ret+="<br/>"
		ret+=time_JST_progress(entry["date"])
		ret+=" "+entry["editor"]
		ret+="</a> "
	except:
		return "title get error"+traceback.format_exc()
	return ret

def admin_comment_with_except(entry):
	try:
		ret="<a href='./usr/"
		ret+=str(entry.bbs_key.key())+"/"
		ret+=str(entry.thread_key.key())
		ret+=".html' target='_BLANK'>"
		ret+=entry.content
		ret+="</a>"
	except:
		return "error "+traceback.format_exc()
	return ret

def show_bookmark(thread_key):
	try:
		thread=db.get(thread_key)
	except:
		return "error "+traceback.format_exc()
	if(not thread):
		return "deleted ";	
	if(not thread.bbs_key):
		return "deleted ";
	text="<a href='"
	if(thread.bbs_key.short):
		text+="./"+thread.bbs_key.short+"/"
	else:
		text+="./usr/"+thread.bbs_key.key+"/"
	if(thread.short):
		text+=""+thread.short
	else:
		text+=""+thread.key
	text+=".html"
	text+="' class='imagelink'><IMG SRC='"
	text+="./thumbnail/"
	text+=""+thread.image
	text+=".jpg' border='0'/></a>";
	return text

def show_bookmark_bbs(bbs_key):
	try:
		bbs=db.get(bbs_key)
	except:
		return "error "+traceback.format_exc()
	if(not bbs):
		return "deleted";
	text="<a href='"
	if(bbs.short):
		text+="./"+bbs.short+"/"
	else:
		text+="./usr/"+str(bbs.key())+"/"
	text+="' >";
	text+=bbs.bbs_name
	text+="</a>"
	
	text+="<a href='show_bookmark?bbs_key="+str(bbs.key())+"'</a>　"
	if(bbs.bookmark_count):
		text+="<small>("+str(bbs.bookmark_count)
		if(bbs.bookmark_count==1):
			text+="user"
		else:
			text+="users"
		text+=")</small>"
	text+="</a>"
	
	return text

def div(value):
	return value/60

#-----------------------------------------------------------------
#ブックマーク
#-----------------------------------------------------------------

def add_bookmark_core(command,search,count):
	txt=""

	if(count):
		txt+='<a href="'+search
		txt+='" class="g-button mini">'
		txt+='<i class="icon-star"></i>'+str(count)
		txt+='</a>'

	txt+='<a href="javascript:'+command+'" class="g-button mini">'
	txt+='<i class="icon-plus"></i>ブックマーク'
	txt+='</a>'

	return txt

def add_bookmark_thread(thread,host):
	command="AddBookmark('"+host+"','"+str(thread.key())+"')"
	search=""+host+'show_bookmark?thread_key='+str(thread.key())
	count=thread.bookmark_count
	return add_bookmark_core(command,search,count)

def add_bookmark_bbs(bbs,host):
	command="bbs_add_bookmark('"+bbs.bbs_name+"','"+str(bbs.key())+"','"+host+"')";
	search=""+host+'show_bookmark?bbs_key='+str(bbs.key())
	count=bbs.bookmark_count
	return add_bookmark_core(command,search,count)

#-----------------------------------------------------------------
#アプリ表示
#-----------------------------------------------------------------

def show_app_core(app,size,size2):
	txt='<div style="background-color:#ffffff;width:'+str(size2)+'px;min-height:'+str(size2)+'px;padding:4px;float:left;">'
	txt+='<a href="app?mode=play&app_id='+app.app_id+'"><img src="app?mode=icon&app_id='+app.app_id+'" width='+str(size)+'px height='+str(size)+'px class="app_icon"></a>'
	style='margin-bottom: 2px;font-size: .85em;font-weight: bold;font-family: arial,helvetica,osaka,\'MS PGothic\',sans-serif;color: #004B91;'
	txt+='<p style="margin-top:4px;"><a href="app?mode=play&app_id='+app.app_id+'" style="'+style+'">'+app.app_name+'</a><br/>'
	txt+='<a href="show_bookmark?app_key='+str(app.key())+'">';
	txt+=str(app.bookmark_count)
	if(app.bookmark_count==1):
		txt+='user'
	else:
		txt+='users'
	txt+='</a>';
	txt+='</p>'
	txt+='</div>'
	return txt

def show_app(app):
	return show_app_core(app,80,100)

def show_app_iphone(app):
	return show_app_core(app,70,70)

def show_app_mypage(app):
	txt=""
	try:
		app=db.get(app)
	except:
		return "アプリ取得エラー";
	txt+='<a href="app?mode=play&app_id='+app.app_id+'">';
	txt+='<img src="app?mode=icon&app_id='+app.app_id+'" width="50px" height="50px" class="app_icon_small">'
	#txt+=str(app.app_name)
	txt+='</a>';
	return txt

def author_name_thread(thread,host):
	return author_name_core(thread.user_id,thread.homepage_addr,thread.author,host)

def author_name_comment(entry,host):
	return author_name_core(entry.user_id,entry.homepage_addr,entry.editor,host)

def user_id_to_user_name(user_id):
	bookmark=ApiObject.get_bookmark_of_user_id(user_id)
	if(bookmark):
		return bookmark.name
	return "未登録"

def author_name_core(user_id,homepage_addr,author,host):
	txt=""
	style="color:#444;"
	if user_id:
		txt+='<a href="'
		txt+=host
		txt+='mypage?user_id='
		txt+=user_id
		txt+='" class="g-button mini" style="'+style+'">'
		txt+=author
		txt+='</a>'
		return txt
	if homepage_addr:
		txt+='<a href="'
		txt+=''+homepage_addr
		txt+='"'
		txt+=' class="g-button mini" style="'+style+'">'
		txt+=author
		txt+="</a>"
		return txt
	return author

def separate_nico(name):
	return name.split(" ‐ ")[0]

#-----------------------------------------------------------------
#ブックマークバー
#-----------------------------------------------------------------

def login_url(redirect_url):
	return users.create_login_url(redirect_url)

def logout_url(redirect_url):
	return users.create_logout_url(redirect_url)

def new_feed_count(obj):
	if(not obj):
		return ""
	if(type(obj)==Bookmark):
		bookmark=obj
	else:
		bookmark=ApiObject.get_bookmark_of_user_id(str(obj.user_id()))
		if(not bookmark):
			return ""
	if(not bookmark.new_feed_count):
		return ""
	return "("+str(bookmark.new_feed_count)+")"

#-----------------------------------------------------------------
#スパムフィルタ
#-----------------------------------------------------------------

def set_seed(no):
	return BbsConst.SUBMIT_SEED

#-----------------------------------------------------------------
#URLの自動リンク
#-----------------------------------------------------------------

def auto_link(summary):
	#Chromeのiframeのeditableがbrではなくdivを生成する問題の対策
	#フォントを変えた場合のdivも削ってしまってdivで閉じれなくなるので断念
	#summary=summary.replace('<div>', '<br/>')
	#summary=summary.replace('</div>', '')
	
	#改行コードの修正
	summary=summary.replace('<br>', '<br/>')

	#自動リンク
	#PlaneText以外に適用すると変な挙動になるので、
	#aタグが含まれていない場合のみに適用する
	if(not(re.match(r'<a',summary))):
		compiled_line = re.compile("(http://[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+)")
		summary = compiled_line.sub(r'<a href=\1 target="_BLANK">\1</a>', summary)

	return summary

#-----------------------------------------------------------------
#サムネイルのサイズ
#-----------------------------------------------------------------

def thumbnail2_width(thread,is_iphone):
	if(is_iphone):
		return 148
	return 200

def thumbnail2_height(thread,is_iphone):
	width=thumbnail2_width(thread,is_iphone)
	try:
		return thread["height"]*width/thread["width"]
	except:
		return width

#-----------------------------------------------------------------
#フィルタ登録
#-----------------------------------------------------------------

register.filter(time_JST)
register.filter(time_JST_format)
register.filter(time_JST_short)
register.filter(time_JST_progress)
register.filter(comment_with_except)
register.filter(comment_with_except_no_hour)
register.filter(reply_with_except)
register.filter(image_key_with_except)
register.filter(div)
register.filter(admin_comment_with_except)
register.filter(show_bookmark)
register.filter(show_bookmark_bbs)
register.filter(add_bookmark_bbs)
register.filter(add_bookmark_thread)
register.filter(show_app)
register.filter(show_app_iphone)
register.filter(show_app_mypage)
register.filter(author_name_thread)
register.filter(author_name_comment)
register.filter(user_id_to_user_name)
register.filter(separate_nico)
register.filter(login_url)
register.filter(logout_url)
register.filter(new_feed_count)
register.filter(set_seed)
register.filter(auto_link)
register.filter(thumbnail2_width)
register.filter(thumbnail2_height)
