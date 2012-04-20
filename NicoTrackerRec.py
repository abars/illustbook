from google.appengine.ext import db
from google.appengine.api import users

class NicoTrackerRec(db.Model):
	title = db.StringProperty()
	url = db.StringProperty()
	id = db.StringProperty()
	day_list = db.StringListProperty()
	play_cnt_list  = db.StringListProperty()
	comment_cnt_list = db.StringListProperty()
	play_cnt_now = db.IntegerProperty()
	comment_cnt_now = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now=True)

