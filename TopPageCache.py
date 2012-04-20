from google.appengine.ext import db
from google.appengine.api import users

class TopPageCache(db.Model):
	#count
	bbs_n=db.IntegerProperty()
	illust_n=db.IntegerProperty()
	
	#tracking
	day_list = db.StringListProperty()
	illust_cnt_list = db.ListProperty(int)
	bbs_cnt_list = db.ListProperty(int)
	entry_cnt_list = db.ListProperty(int)
	user_cnt_list = db.ListProperty(int)
	
	#tracking date
	date = db.DateTimeProperty(auto_now=True)
