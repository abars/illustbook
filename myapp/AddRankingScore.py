#!-*- coding:utf-8 -*-
#!/usr/bin/env python

#---------------------------------------------------
#ランキングにスコアを追加
#copyright 2013 ABARS all rights reserved.
#---------------------------------------------------

import datetime;
import time;
import json;
import logging;

from google.appengine.ext import db
from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp

from myapp.BbsConst import BbsConst
from myapp.ApiObject import ApiObject
from myapp.MesThread import MesThread
from myapp.Ranking import Ranking

class AddRankingScore(webapp.RequestHandler):
	def post(self):
		try:
			thread=db.get(self.request.get("thread"))
		except:
			thread=None

		if(not thread):
			return

		score=int(self.request.get("score"))
		rank=Ranking.get_by_key_name(BbsConst.THREAD_RANKING_KEY_NAME)
		if(rank==None):
			rank=Ranking.get_or_insert(BbsConst.THREAD_RANKING_KEY_NAME)
		rank.add_rank(thread,score)

		#logging.warning("ranking add")

