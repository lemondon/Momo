#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import urllib
import urllib2
import json
import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

BASE_URL = 'https://graph.facebook.com/v2.11'
LOVE_CALCULATOR_TOKEN = 'RnItXxPrMjmshYiCtTzC920HBA4Ep1XNgDCjsny6U1NWfzDSZU'


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {'page_title': "Find My Lover"}
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


def safe_get(url):
    try:
        return json.load(urllib2.urlopen(url))
    except urllib2.HTTPError, e:
        print 'The server couln\'t fulfill the request.'
        print 'Error code: ', e.code
    except urllib2.URLError, e:
        print 'We failed to reach a server'
        print 'Reason: ', e.reason
    return None


def get_profiles_by_name(name, token):
    if name is '':
        name = '""'
    params = urllib.urlencode({"access_token": token, 'q': name, 'type': 'user'})
    url = '{}/search?{}'.format(BASE_URL, params)
    result = safe_get(url)['data'][:5]
    response = []
    for u in result:
        url, name = get_user_info(u['id'], token)
        response.append({'url': url, 'name': name, 'id': id})
    return response


def get_user_info(id, token):
    params = urllib.urlencode({"access_token": token, 'fields': 'picture,name,id'})
    url = '{}/{}?{}'.format(BASE_URL, id, params)
    result = safe_get(url)
    return result["picture"]["data"]["url"], result["name"]


def get_match_rating(fname, sname):
    if fname is '':
        fname = ''
    elif sname is '':
        sname = ''
    params = urllib.urlencode({'fname': fname, 'sname': sname})
    request = urllib2.Request('https://love-calculator.p.mashape.com/getPercentage?{}'.format(params),
                              headers={'X-Mashape-Key': LOVE_CALCULATOR_TOKEN, 'Accept': 'application/json'})
    result = safe_get(request)
    return result['result'], int(result['percentage'])


class MatchHandler(webapp2.RequestHandler):
    def get(self):
        token = self.request.params.get('access_token')
        id = self.request.params.get('id')
        query = self.request.params.get('name', '')
        my_pic, my_name = get_user_info(id, token)
        suggestions = get_profiles_by_name(query, token)
        word, percentage = get_match_rating(my_name.split()[0], query)

        template_values = {'page_title': "Find My Lover",
                           'token': token,
                           'id': id,
                           'suggestions': suggestions,
                           'word': word,
                           'name': query,
                           'percentage': percentage,
                           'my_name': my_name,
                           'my_pic': my_pic}
        template = JINJA_ENVIRONMENT.get_template('result.html')
        self.response.write(template.render(template_values))


application = webapp2.WSGIApplication([('/', MainHandler), ('/result', MatchHandler)], debug=True)
