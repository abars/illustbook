#!/usr/bin/python
# -*- coding: utf-8 -*-
# Gooogle Analytics API

import argparse
import sys
import logging
import httplib2

from google.appengine.api import memcache

from apiclient.errors import HttpError
from apiclient import sample_tools
from oauth2client.client import AccessTokenRefreshError

from apiclient import discovery
from oauth2client import appengine
from oauth2client import client

from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials

class AnalyticsGet():
  def create_session(self):
    KEY = "privatekey.pem"
    SCOPES = [
      'https://www.googleapis.com/auth/analytics',
      'https://www.googleapis.com/auth/analytics.edit',
      'https://www.googleapis.com/auth/analytics.manage.users',
      'https://www.googleapis.com/auth/analytics.readonly',
    ]
    SERVICE_ACCOUNT = "151632435710-r4lljmm28b1t25n00js4m01b34qr1npm@developer.gserviceaccount.com"

    key = open(KEY).read()

    credentials = SignedJwtAssertionCredentials(SERVICE_ACCOUNT,
                        key,
                        scope=SCOPES)
   
    http = httplib2.Http()
    #httplib2.debuglevel = True
    http = credentials.authorize(http)

    service = build('analytics', 'v3', http=httplib2.Http(memcache))

    self.http=http
    self.service=service

  def get(self,mode,bbs_name,start_date,end_date):
    http=self.http
    service=self.service

    self.result_cnt=50
    if(bbs_name==".*"):
      self.result_cnt=400

    # Try to make a request to the API. Print the results or handle errors.
    try:
      first_profile_id = self.get_first_profile_id(service,http)
      if not first_profile_id:
        logging.error ('Could not find a valid profile for this user.')
        return []
      else:
        if(mode=="page"):
          results = self.get_page(service, first_profile_id, http, bbs_name , start_date , end_date)
        if(mode=="access"):
          results = self.get_access(service, first_profile_id, http, bbs_name , start_date , end_date)
        if(mode=="ref"):
          results = self.get_ref(service, first_profile_id, http, bbs_name , start_date , end_date)
        if(mode=="keyword"):
          results = self.get_keywords(service, first_profile_id, http, bbs_name , start_date , end_date)
        result_json = self.get_results(results)
        return result_json

    except TypeError, error:
      # Handle errors in constructing a query.
      logging.error ('There was an error in constructing your query : %s' % error)
      return []

    except HttpError, error:
      # Handle API errors.
      logging.error ('Arg, there was an API error : %s : %s' %
             (error.resp.status, error._get_reason()))
      return []

    except AccessTokenRefreshError:
      # Handle Auth errors.
      logging.error ('The credentials have been revoked or expired, please re-run '
             'the application to re-authorize')
      return []

  def get_first_profile_id(self,service,http):
    accounts = service.management().accounts().list().execute(http=http)

    if accounts.get('items'):
      firstAccountId = accounts.get('items')[0].get('id')
      webproperties = service.management().webproperties().list(
          accountId=firstAccountId).execute(http=http)

      if webproperties.get('items'):
        firstWebpropertyId = "UA-8633292-4"

        profiles = service.management().profiles().list(
            accountId=firstAccountId,
            webPropertyId=firstWebpropertyId).execute(http=http)

        if profiles.get('items'):
          return profiles.get('items')[0].get('id')

    return None

  def get_access(self,service, profile_id, http, bbs_name, start_date, end_date):
    return service.data().ga().get(
        ids='ga:' + profile_id,
        start_date=start_date,
        end_date=end_date,
        metrics='ga:pageviews',
        dimensions='ga:date',
        sort='ga:date',
        filters='ga:pagePath=~/'+bbs_name+'/*',
        start_index='1',
        max_results='1000').execute(http=http)

  def get_keywords(self,service, profile_id, http, bbs_name, start_date, end_date):
    return service.data().ga().get(
        ids='ga:' + profile_id,
        start_date=start_date,
        end_date=end_date,
        metrics='ga:pageviews',
        dimensions='ga:keyword',
        sort='-ga:pageviews',
        filters='ga:pagePath=~/'+bbs_name+'/*',
        start_index='1',
        max_results=str(self.result_cnt)).execute(http=http)

  def get_page(self,service, profile_id, http, bbs_name, start_date, end_date):
    return service.data().ga().get(
        ids='ga:' + profile_id,
        start_date=start_date,
        end_date=end_date,
        metrics='ga:pageviews',
        dimensions='ga:pageTitle,ga:pagePath',
        sort='-ga:pageviews',
        filters='ga:pagePath=~/'+bbs_name+'/.*\.html',
        start_index='1',
        max_results=str(self.result_cnt)).execute(http=http)

  def get_ref(self,service, profile_id, http, bbs_name, start_date, end_date):
    return service.data().ga().get(
        ids='ga:' + profile_id,
        start_date=start_date,#'2014-01-01',
        end_date=end_date,#'2014-05-23',
        metrics='ga:pageviews',
        dimensions='ga:source,ga:referralPath',
        sort='-ga:pageviews',
        filters='ga:pagePath=~/'+bbs_name+'/*',
        start_index='1',
        max_results=str(self.result_cnt)).execute(http=http)

  def get_results(self,results):
    # Get header.
    output_header = []
    for header in results.get('columnHeaders'):
      output_header.append(header.get('name'))

    # Get data table.
    result_json = []
    if results.get('rows', []):
      for row in results.get('rows'):
        output_cols = []
        no = 0
        dict = {}
        for cell in row:
          output_cols.append(cell)
          dict[output_header[no]]=output_cols[no]
          no=no+1
        result_json.append(dict)
    else:
      return []
    return result_json
