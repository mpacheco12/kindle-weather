"""
Weather API Python sample code
Copyright 2019 Oath Inc. Licensed under the terms of the zLib license see https://opensource.org/licenses/Zlib for terms.
$ python --version
Python 2.7.10
"""
import time, uuid, urllib, urllib2
import hmac, hashlib
from base64 import b64encode
import datetime
import json
import codecs

#City name
LOCATION = "medellin"
#Change to false if you want Fahrenheit and mph
METRIC = True


def getCardinal(angle):
	directions = 8
	degree = 360 / directions
	angle = angle + degree/2
	if angle >= (0 * degree) and angle < (1 * degree):
		return "N"
	if angle >= (1 * degree) and angle < (2 * degree):
		return "NE"
	if angle >= (2 * degree) and angle < (3 * degree):
		return "E"
	if angle >= (3 * degree) and angle < (4 * degree):
		return "SE"
	if angle >= (4 * degree) and angle < (5 * degree):
		return "S"
	if angle >= (5 * degree) and angle < (6 * degree):
		return "SW"
	if angle >= (6 * degree) and angle < (7 * degree):
		return "W"
	if angle >= (7 * degree) and angle < (8 * degree):
		return "NW"
	return "N"


"""
Basic info
"""
url = 'https://weather-ydn-yql.media.yahoo.com/forecastrss'
method = 'GET'
app_id = 'app_id'
consumer_key = 'consumer_key'
consumer_secret = 'consumer_secret'
concat = '&'
query = {'location': LOCATION, 'format': 'json'}
if METRIC:
	query['u'] = 'c'
oauth = {
    'oauth_consumer_key': consumer_key,
    'oauth_nonce': uuid.uuid4().hex,
    'oauth_signature_method': 'HMAC-SHA1',
    'oauth_timestamp': str(int(time.time())),
    'oauth_version': '1.0'
}

"""
Prepare signature string (merge all params and SORT them)
"""
merged_params = query.copy()
merged_params.update(oauth)
sorted_params = [k + '=' + urllib.quote(merged_params[k], safe='') for k in sorted(merged_params.keys())]
signature_base_str =  method + concat + urllib.quote(url, safe='') + concat + urllib.quote(concat.join(sorted_params), safe='')

"""
Generate signature
"""
composite_key = urllib.quote(consumer_secret, safe='') + concat
oauth_signature = b64encode(hmac.new(composite_key, signature_base_str, hashlib.sha1).digest())

"""
Prepare Authorization header
"""
oauth['oauth_signature'] = oauth_signature
auth_header = 'OAuth ' + ', '.join(['{}="{}"'.format(k,v) for k,v in oauth.iteritems()])

"""
Send request
"""
url = url + '?' + urllib.urlencode(query)
request = urllib2.Request(url)
request.add_header('Authorization', auth_header)
request.add_header('X-Yahoo-App-Id', app_id)
response = urllib2.urlopen(request).read()
response = json.loads(response)
temp = response['current_observation']['condition']['temperature']
chill =  response['current_observation']['wind']['chill']

image = str(response['current_observation']['condition']['code'])
image_url = 'assets/' + image + '.png'

# Open SVG to process
output = codecs.open('template.svg', 'r', encoding='utf-8').read()
date = response['current_observation']['pubDate']
date = datetime.datetime.fromtimestamp(date)
# Insert icons and temperatures
output = output.replace('TODAY',date.strftime("%a %B %d"))
output = output.replace('TIME',date.strftime("%I:%M: %p"))
output = output.replace('CITY',response['location']['city'])
output = output.replace('HUMID',str(response['current_observation']['atmosphere']['humidity']))
output = output.replace('ICON_ONE',image_url)
output = output.replace('HIGH_ONE',str(temp))
output = output.replace('LOW_ONE',str(chill))
output = output.replace('SUNSET',response['current_observation']['astronomy']['sunset'].rstrip(' pm'))
output = output.replace('SUNRISE',response['current_observation']['astronomy']['sunrise'].rstrip(' am'))
output = output.replace('STATUS',response['current_observation']['condition']['text'])
if chill>=temp:
     output = output.replace('black','white')
     output = output.replace('TEMPYCOORD','310')
else:
	output = output.replace('TEMPYCOORD','270')

output = output.replace('SPEED',str(int(round(float(response['current_observation']['wind']['speed'])))))
output = output.replace('NESW',getCardinal(float(response['current_observation']['wind']['direction'])))
if METRIC:
    output = output.replace('UNIT','km/h')
else:
    output = output.replace('UNIT','mph')

output = output.replace('UNIT','km/h')
codecs.open('weather-processed.svg', 'w', encoding='utf-8').write(output)

