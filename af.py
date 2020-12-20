import requests, json
from bs4 import BeautifulSoup

def default_response():
    return 'Sorry, I had trouble doing what you asked. Please try again with something else.'


def get_location():
    '''
    URL = "https://https://api.eu.amazonalexa.com/v1/devices/{}/settings" \
           "/address".format(this.event.context.System.device.deviceID')
    TOKEN = this.event.context.System.apiAccessToken #token kind: 'eyJ0eX9OTWJ2ZDRaQkJlSmxNYnBHUmLA.......'
    HEADER = {'Accept': 'application/json',
             'Authorization': 'Bearer {}'.format(TOKEN)}
    r = requests.get(URL, headers=HEADER)
    r = r.json()
    full_loc = r['addressLine1'] + r['city'] + r['districtOrCounty'] + r['stateOrRegion'] + r['postalCode']
    '''
    return 'Laxmeshwar, India'


def get_geocode(query_town):
    if query_town is None:
        return '15.114502906799316,75.464599609375'
    else:
        global key
        key = '<YOUR_API_KEY>'
        locn = requests.get('http://dev.virtualearth.net/REST/v1/Locations/{}?maxResults=1&key={}'.format(str(query_town),str(key)))
        locn = locn.json()
        if locn['statusCode'] == 200:
            geocor = locn['resourceSets'][0]['resources'][0]['point']['coordinates']
            geocor = ','.join(map(str,geocor))
            return geocor
        else:
            return None


def get_bbox(target):
    global key
    key = '<YOUR_API_KEY>'
    loc = requests.get('http://dev.virtualearth.net/REST/v1/Locations/{}?maxResults=1&key={}'.format(str(target),str(key)))
    loc = loc.json()
    if loc['statusCode'] == 200:
        corners = loc['resourceSets'][0]['resources'][0]['bbox']
        corners = ','.join(map(str,corners))
        return corners
    else:
        return None


def get_city_info(query):
    """Return a response JSON for a GET call from `request`."""
    # type: (str, Dict) -> Dict
    url = 'https://www.google.com/search?&q={}'.format(str(query))
    req = requests.get(url) 
    soup = BeautifulSoup(req.text, "html.parser")
    info = soup.find("div", class_='BNeawe s3v9rd AP7Wnd').text
    return info.strip('Wikipedia')


def get_road_info(query):
    bbox_pts = get_bbox(query)
    if bbox_pts is None:
        return default_response()
    else:
        incidents = requests.get('http://dev.virtualearth.net/REST/v1/Traffic/Incidents/{}?key={}'.format(str(bbox_pts),str(key)))
        incidents = incidents.json()
        if incidents['statusCode'] != 200:
            return default_response()
    incidents = incidents['resourceSets'][0]['resources']
    alerts = len(incidents)
    severities = ['LowImpact', 'Minor', 'Moderate', 'Serious']
    incident_types = ['Accident', 'Congestion', 'DisabledVehicle', 'MassTransit', 'Miscellaneous', 'OtherNews', 'PlannedEvent', 'RoadHazard', 'Construction', 'Alert', 'Weather']
    if alerts<1:
        return 'Hey, good to go! No important updates on roads around.'
    else:
        resp = "Hey, found {} road related updates for you. \n".format(str(alerts))
        if alerts > 5:
            resp = resp + "I am listing top 5 by priority for you. \n"
        upd = []
        for i in range(min(alerts,5)):
            incident = incidents[i]
            severity = severities[incident['severity']-1]
            incident_type = incident_types[incident['type']-1]
            incident_info = incident['description']
            info = "{}) {} information about {}: {} ".format(str(i+1), str(severity), str(incident_type),str(incident_info))
            if incident['roadClosed'] == False:
                msg = 'However, road is open. \n'
            else:
                msg = 'So, road is closed. \n'
            upd.append(info + msg)
        return resp + ''.join(map(str,upd))


def get_weather(place_query, session_query):
    url = 'https://www.google.com/search?q={}+weather+{}'.format(str(place_query), str(session_query))
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    temp = soup.find("div", class_='BNeawe iBp4i AP7Wnd').text
    obs = soup.find("div", class_='BNeawe tAd8D AP7Wnd').text
    obs = obs.partition('\n')[-1]
    if 'now' in session_query:
        resp = 'Temperature is {} and overall it is {}.'.format(str(temp),str(obs))
    elif temp == '':
        cmt = obs.partition('High:')[0]
        intm = obs.partition('Low: ')[0]
        high_temp = intm.partition('High:')[-1]
        low_temp = obs.partition('Low: ')[-1]
        resp = 'Overall it would be {} with temperature as high as {} and as low as {}.'.format(str(cmt),str(high_temp),str(low_temp))
    else:
        cmt = obs.partition('High:')[0]
        intm = obs.partition('Low: ')[0]
        high_temp = intm.partition('High:')[-1]
        low_temp = obs.partition('Low: ')[-1]
        resp = 'Temperature is {}. Overall it is {} with temperature as high as {} and as low as {}.'.format(str(temp),str(cmt),str(high_temp),str(low_temp))

    return resp


def get_nearby_entities(locality_query, entity_query):
    lat, lon = locality_query.partition(',')[0], locality_query.partition(',')[-1]
    if entity_query is None:
        res = requests.get('https://api.tomtom.com/search/2/nearbySearch/.JSON?key=<YOUR_API_KEY>&lat={}&lon={}&limit=4&ofs=1&countrySet=IN&categorySet=7376,9927,9902'.format(str(lat),str(lon)))
        ent_type = 'attractions or must-visit places'
        ent_not = 'I assumed that you were searching for attractions or must-visit places. \n'
    else:
        res = requests.get('https://api.tomtom.com/search/2/categorySearch/{}.JSON?key=<YOUR_API_KEY>&lat={}&lon={}&limit=4&ofs=1&countrySet=IN'.format(str(entity_query),str(lat),str(lon)))
        ent_type = entity_query
        ent_not = ''
    
    if res.status_code != 200:
        return default_response()
    else:
        res = res.json()
        t_res = res['summary']['totalResults']
        sumry = 'Found {} {} nearby. '.format(str(t_res),str(ent_type))
        count = min(t_res, 4)
        if count < 1:
            return ent_not + "But, couldn't find any {} nearby.".format(str(ent_type))
        else:
            if t_res > 4:
                sumry = sumry + 'Listing nearest 4 by distance for you. \n'
            adrs = []
            for i in range(count):
                ent = res['results'][i]['poi']['name']
                adr1 = res['results'][i]['address']['streetName']
                adr2 = res['results'][i]['address']['localName']
                dist = res['results'][i]['dist']
                adrs.append(str(i+1)+') '+ent+', '+adr1+', '+adr2+' at a distance of approx. {} metre. '.format(int(dist)))
            return sumry + '\n'.join(map(str,adrs))


def get_entities(ent_query, city_query, duration_query):
    duration = duration_query.partition('PT')[-1]
    if ent_query is None:
        ent_query = 'SeeDo'
        ent_note = 'I assumed that you were searching for attractions or must-visit places. \n'
    else:
        ent_note = ''
    
    if 'H' in duration or 'D' in duration or 'W' in duration or 'Y' in duration:
        mins = 60
        note = 'Your time duration query exceeds 60 minutes, and so by default I am assuming it as 60 minutes. \n'
    elif 'S' in duration:
        mins = 2
        note = 'Your time duration query is not more than 2 minutes, and so by default I am assuming it as 2 minutes. \n'
    else:
        mins = int(duration.partition('M')[0])
        note = ''
    
    global key
    key = '<YOUR_API_KEY>'
    res = requests.get('http://dev.virtualearth.net/REST/v1/Routes/LocalInsights?waypoint={}&maxTime={}&timeUnit=minute&type={}&key={}'.format(str(city_query),str(mins),str(ent_query),str(key)))
    res = res.json()
    if res['statusCode'] != 200:
        return default_response()
    else:
        res = res['resourceSets'][0]['resources'][0]['categoryTypeResults'][0]
        t_res = len(res['entities'])
        count = min(t_res, 4)
        sumry = res['categoryTypeSummary'].strip(' ') + ' time. '
        if count < 1:
            return ent_note + "But, couldn't find any."
        else:
            resp = []
            if t_res > 4:
                sumry = sumry + 'Listing nearest 4 by time for you. \n'
            for i in range(count):
                enty = str(i+1) + ') ' + res['entities'][i]['entityName'].strip(' ')
                resp.append(enty)
            return ent_note + note + sumry + ', \n'.join(map(str,resp))


def get_resolved_value(request, slot_name):
    """Resolve the slot name from the request."""
    # type: (IntentRequest, str) -> Union[str, None]
    try:
        return request.intent.slots[slot_name].value
    except (AttributeError, ValueError, KeyError, IndexError):
        return None
