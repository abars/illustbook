from google.appengine.ext import db
from google.appengine.api import users

import datetime

class RankingScore(db.Model):
	thread_key=db.ReferenceProperty()
	today_score=db.IntegerProperty()
	yesterday_score=db.IntegerProperty()
	today_date=db.IntegerProperty()
	yesterday_date=db.IntegerProperty()
	illust_mode=db.IntegerProperty()
	
	def init_score(self,key,illust_mode):
		self.today_score=0
		self.yesterday_score=0
		self.today_score=0
		now = datetime.datetime.today()+datetime.timedelta(hours=9)
		now_date=now.day+now.month*31+now.year*400
		self.today_date=now_date
		self.yesterday_date=0
		self.thread_key=key
		self.illust_mode=illust_mode
	
	def update_score(self,score):
		self.today_score=self.today_score+score
		now = datetime.datetime.today()+datetime.timedelta(hours=9)
		now_date=now.day+now.month*31+now.year*400
		if(now_date>=self.today_date+7):
			self.yesterday_score=self.today_score
			self.yesterday_date=self.today_date
			self.today_date=now_date
			self.today_score=0
