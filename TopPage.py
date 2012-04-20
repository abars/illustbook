from google.appengine.ext import db

from Counter import Counter
from Analyze import Analyze

class TopPage(db.Model):
	counter = db.ReferenceProperty(Counter,None,"top_counter")
	analyze = db.ReferenceProperty(Analyze,None,"top_analyze")

	moper_counter = db.ReferenceProperty(Counter,None,"moper_counter")
	moper_analyze = db.ReferenceProperty(Analyze,"moper_analyze")

	about_counter = db.ReferenceProperty(Counter,None,"about_counter")
	about_analyze = db.ReferenceProperty(Analyze,None,"about_analyze")

	guide_counter = db.ReferenceProperty(Counter,None,"guide_counter")
	guide_analyze = db.ReferenceProperty(Analyze,None,"guide_analyze")

	mypage_counter = db.ReferenceProperty(Counter,None,"mypage_counter")
	mypage_analyze = db.ReferenceProperty(Analyze,None,"mypage_analyze")

	ranking_counter = db.ReferenceProperty(Counter,None,"ranking_counter")
	ranking_analyze = db.ReferenceProperty(Analyze,None,"ranking_analyze")

	link_counter = db.ReferenceProperty(Counter,None,"link_counter")
	link_analyze = db.ReferenceProperty(Analyze,None,"link_analyze")

	local_counter = db.ReferenceProperty(Counter,None,"local_counter")
	local_analyze = db.ReferenceProperty(Analyze,None,"local_analyze")

	questionnaire_counter = db.ReferenceProperty(Counter,None,"questionnaire_counter")
	questionnaire_analyze = db.ReferenceProperty(Analyze,None,"questionnaire_analyze")

	date = db.DateTimeProperty(auto_now=True)
