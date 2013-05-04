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
import random
import logging
import urllib
import math

from google.appengine.ext.webapp import template
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
			tag_string=tag_string+tag+","
		return tag_string

	@staticmethod
	def _create_document(thread):
		return search.Document(
			doc_id=str(thread.key()),
			fields=[
				search.TextField(name='author', value=thread.author),
				search.TextField(name='title', value=thread.title),
				search.TextField(name='category', value=thread.category),
				search.TextField(name='tag', value=SearchThread._tag_compaction(thread.tag_list)),
				search.HtmlField(name='summary', value=thread.summary),
				search.DateField(name='date', value=thread.create_date)
			])

	@staticmethod
	def _create_document_entry(entry):
		res_text=""
		for res_key in entry.res_list:
			try:
				res=db.get(res_key)
			except:
				continue
			res_text+=""+res.content+" from "+res.editor+"<br/>"

		return search.Document(
			doc_id=str(entry.key()),
			fields=[
				search.TextField(name='editor', value=entry.editor),
				search.TextField(name='content', value=entry.content),
				search.TextField(name='response', value=res_text),
				search.DateField(name='date', value=entry.create_date)
			])


	@staticmethod
	def add_index(thread):
		if(thread.search_index_version):
			if(thread.search_index_version==BbsConst.SEARCH_THREAD_VERSION):
				return
		document=SearchThread._create_document(thread)
		try:
			search.Index(name=BbsConst.SEARCH_THREAD_INDEX_NAME).put(document)
		except search.Error:
			logging.exception('Search Put failed')
		thread.search_index_version=BbsConst.SEARCH_THREAD_VERSION
		thread.put()

	@staticmethod
	def add_index_entry(entry):
		if(entry.search_index_version):
			if(entry.search_index_version==BbsConst.SEARCH_ENTRY_VERSION):
				return
		document=SearchThread._create_document_entry(entry)
		try:
			search.Index(name=BbsConst.SEARCH_ENTRY_INDEX_NAME).put(document)
		except search.Error:
			logging.exception('Search Put failed')

		entry.search_index_version=BbsConst.SEARCH_ENTRY_VERSION
		entry.put()

	@staticmethod
	def search(query,page,unit,index):
		sort_options = search.SortOptions(
			expressions=[
				search.SortExpression(expression='date', direction=search.SortExpression.DESCENDING, default_value=0)
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



