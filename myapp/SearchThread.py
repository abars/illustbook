#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#スレッドの検索
#copyright 2013 ABARS all rights reserved.
#---------------------------------------------------

import cgi
import os
import sys
import re
import datetime
import time;
import random
import logging
import urllib
import math

import template_select
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache

from myapp.BbsConst import BbsConst
from myapp.Bbs import Bbs
from myapp.MesThread import MesThread

from google.appengine.api import search

class SearchThread(webapp.RequestHandler):
	@staticmethod
	def _tag_compaction(tag_list):
		tag_string=""
		for tag in tag_list:
			tag_string=tag_string+tag+" "
		return tag_string

	@staticmethod
	def _number_validate(value):
		if(not value):
			return 0
		return value

	@staticmethod
	def _create_document(thread):
		return search.Document(
			doc_id=str(thread.key()),
			fields=[
				search.TextField(name='author', value=thread.author),
				search.TextField(name='title', value=thread.title),
				search.TextField(name='category', value=thread.category),
				search.TextField(name='tag', value=SearchThread._tag_compaction(thread.tag_list)),
				search.NumberField(name='applause', value=SearchThread._number_validate(thread.applause)),
				search.NumberField(name='bookmark', value=SearchThread._number_validate(thread.bookmark_count)),
				search.NumberField(name='comment', value=SearchThread._number_validate(thread.comment_cnt)),
				search.HtmlField(name='summary', value=thread.summary),
				search.DateField(name='date', value=thread.create_date),
				search.NumberField(name='sec', value=SearchThread._get_sec(thread.create_date))
			])

	@staticmethod
	def _get_sec(now):
		return int(time.mktime(now.timetuple()))

	@staticmethod
	def _create_document_entry(entry):
		res_text=""
		res_list=db.get(entry.res_list)
		for res in res_list:
			comment_no=0
			if(res.comment_no):
				comment_no=res.comment_no
			res_text+=""+str(comment_no)+" "+res.content+" from "+res.editor+"<br/>"

		try:
			thread_key=str(entry.thread_key.key())
			bbs_key=str(entry.bbs_key.key())
		except:
			thread_key=""
			bbs_key=""

		comment_no=0
		if(entry.comment_no):
			comment_no=entry.comment_no

		date=entry.date
		if(entry.create_date):
			date=entry.create_date

		return search.Document(
			doc_id=str(entry.key()),
			fields=[
				search.TextField(name='editor', value=entry.editor),
				search.HtmlField(name='content', value=entry.content),
				search.HtmlField(name='response', value=res_text),
				search.TextField(name='thread_key', value=thread_key),
				search.TextField(name='bbs_key', value=bbs_key),
				search.DateField(name='date', value=date),
				search.NumberField(name='sec', value=SearchThread._get_sec(date)),
				search.NumberField(name='comment_no', value=comment_no)
			])


	@staticmethod
	def add_index(thread):
		if(thread.search_index_version):
			if(thread.search_index_version==BbsConst.SEARCH_THREAD_VERSION):
				return
		document=SearchThread._create_document(thread)
		try:
			search.Index(name=BbsConst.SEARCH_THREAD_INDEX_NAME).put(document)
			thread.search_index_version=BbsConst.SEARCH_THREAD_VERSION
			thread.put()
		except search.Error:
			logging.exception('Search Put failed')

	@staticmethod
	def add_index_entry(entry):
		if(entry.search_index_version):
			if(entry.search_index_version==BbsConst.SEARCH_ENTRY_VERSION):
				return
		document=SearchThread._create_document_entry(entry)
		try:
			search.Index(name=BbsConst.SEARCH_ENTRY_INDEX_NAME).put(document)
			entry.search_index_version=BbsConst.SEARCH_ENTRY_VERSION
			entry.put()
		except search.Error:
			logging.exception('Search Put failed')

	@staticmethod
	def search(query,page,unit,index):
		now_sec=SearchThread._get_sec(datetime.datetime.now())
		reduct='(1+('+str(now_sec)+'-sec)/(3600*24*30))';	#一ヶ月で半分のスコアにする

		sort_options = search.SortOptions(
			expressions=[
				search.SortExpression(expression='(applause+bookmark*5)/'+reduct, direction=search.SortExpression.DESCENDING, default_value=0)
			],limit=1000)
		options = search.QueryOptions(
			limit=unit,
			offset=(page-1)*unit,
			sort_options=sort_options)
		try:
			query=search.Query(
				query_string=query,
				options=options,)
		except:
			return []

		index = search.Index(name=index)

		try:
			results=index.search(query)
		except:
			return []
		
		key_list=[]
		for doc in results:
			key_list.append(db.Key(encoded=str(doc.doc_id)))
		return key_list



