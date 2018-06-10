'''
These tools are designed to serve as a wrapper to the EVE ESI API to simplify
common activites into general python functions.
'''
__author__ = "Avenhor Hastmena"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Avenhor Hastmena"
__email__ = "avenhor@gmail.com"
__status__ = "Development"

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import requests as r, json
from datetime import datetime
import pickle
import networkx as nx

auth_base = "https://login.eveonline.com/oauth/token"
avenhor_client_id = ""
avenhor_client_secret = ""
avenhor_refresh_token = ""
grant_type = "refresh_token"
avenhor_char_id = ''
avenhor_data = {'client_id': avenhor_client_id, 'client_secret': avenhor_client_secret, 'refresh_token': avenhor_refresh_token, 'grant_type': grant_type}
concord = ['Avada','Chibi','Haimeh','Mishi','Pahineh','Asabona','Chidah','Sendaya','Shamahi','Sooma','Adeel','Groothese','Mormelot','Olide','Kemerk','Pakhshi','Tekaima','Yulai','Agil','Ipref','Kihtaled','Neyi','Keproh','Rannoze','Zatamaka','Arvasaras','Autaris','Jan','Vellaine','Geffur','Hilfhurmur','Lumegen','Oppold','Tratokard','Arlulf','Brundakur','Nedegulf','Stirht','Altbrard','Half','Hedaleolfarber','Istodard','Aeditide','Egbinger','Klingt','Aulbres','Barleguet','Assiettes','Esmes','Goinard','Lermireve','Raeghoscon','Hatakani','Iivinen','Tennen','Yashunen','Mastakomon','Uchoshi']
query_base = 'https://esi.tech.ccp.is/latest/'
api_data = None
#G = nx.Graph # a basic graph that holds the entire eve universe

# These caches will reduce the number of API calls to various endpoints
id_cache = {} # dict of int: string
name_cache = {} # dict of string:int
sec_cache = {}
kills_cache = {}
kills_cache_timestamp = None
system_cache = {} # dict of string:int
id_cache_miss = 0
id_cache_hit = 0
name_cache_miss = 0
name_cache_hit = 0

def makePickles():
	'''
	Pickles vars identified by a dictionary to a local file
	to facilitate cacheing and reduction of API calls.
	'''
    pickle_dict = {'id':id_cache,'name':name_cache,'sec':sec_cache,'kills':kills_cache,
                   'kills_age':kills_cache_timestamp,'system':system_cache,'eve_map':G}
    with open('dill.pkl','wb') as f:
        pickle.dump(pickle_dict,f)
        
def eatPickles():
	'''
	Retrieves pickled vars from local file
	'''
    global id_cache
    global name_cache
    global sec_cache
    global kills_cache
    global kills_cache_timestamp
    global system_cache
    global G
    
    with open('dill.pkl','rb') as f:
        pickle_dict = pickle.load(f)
        
    id_cache = pickle_dict['id']
    name_cache = pickle_dict['name']
    sec_cache = pickle_dict['sec']
    kills_cache = pickle_dict['kills']
    kills_cache_timestamp = pickle_dict['kills_age']
    system_cache = pickle_dict['system']
    G = pickle_dict['eve_map']
    
def getContracts(id):
	'''
	Returns request object containing contracts for
	character specified by the id parameter
	'''
    return r.get(query_base + 'characters/' + id + '/contracts', headers = api_data)

def getLocation(id):
	'''
	Returns the system id of the current location for the 
	character specified by the id paramter
	'''
    response = r.get(query_base + 'characters/' + id + '/location', headers = api_data)
    return response.json()['solar_system_id']

def idToName(id):
	'''
	Returns the name mapped to the entity
	specified by the id parameter
	'''
    global name_cache
    # TODO: handle lists of IDs
    if int(id) in id_cache: # this won't work for lists of IDs
        return id_cache[int(id)]
    api_body = str(id)
    response = r.post(query_base + 'universe/names/', headers=api_data, data = '[' + api_body + ']')
    data = response.json()[0]
    name = data['name']
    if data['category'] == 'solar_system':
        if name not in system_cache:
            system_cache[name] = int(id)
    elif data['category'] == 'character':
        if name not in name_cache:
            name_cache[name] = int(id)
    return name

#def nameToId(name):
#	'''
#	Returns the id mapped to the name
#	specified by the name parameter
#	'''
#    global id_cache
#    # TODO: handle lists of names
#    if name in name_cache:
#        return name_cache[name]
#    if name.upper() == 'JITA':
#        id = 30000142
#    else:
#        api_body = '[\"' + name + '\"]'
#        response = r.post(query_base + 'universe/ids/', headers=api_data, data=api_body)
#        id = int(response.json()['systems'][0]['id'])
#    if id not in id_cache:
#        id_cache[id] = name
#    return id

def nameToId(name,qryType):
	'''
	Returns the id mapped to the name
	specified by the name parameter and requires
	an additional parameter to indicate the
	type of the object being queried
	'''
    global id_cache
    # TODO: handle lists of names
    if name in name_cache:
        return name_cache[name]
    if name.upper() == 'JITA':
        id = 30000142
    else:
        api_body = '[\"' + name + '\"]'
        response = r.post(query_base + 'universe/ids/', headers=api_data, data=api_body)
        if qryType.upper() == 'SYSTEM':
            id = int(response.json()['systems'][0]['id'])
        elif qryType.upper() == 'CHAR':
            id = int(response.json()['characters'][0]['id'])
    if id not in id_cache:
        id_cache[id] = name
    return id
    
def printJournal(result):
	'''
	Prints the journal history supplied via
	the result parameter obtained from the 
	wallet/journal API endpoint
	'''
    global id_cache
    cache_hits = 0
    cache_misses = 0
    for x in result.json():
        reason = x['ref_type']
        date = datetime.strptime(x['date'], '%Y-%m-%dT%H:%M:%SZ')
        if ('first_party_id' in x and 'second_party_id' in x):
            if (int(x['first_party_id']) in id_cache):
                cache_hits += 1
                p1 = id_cache[int(x['first_party_id'])]
            else:
                cache_misses += 1
                p1 = idToName(x['first_party_id'])
                id_cache[int(x['first_party_id'])] = p1
            if (int(x['second_party_id']) in id_cache):
                cache_hits += 1
                p2 = id_cache[int(x['second_party_id'])]
            else:
                cache_misses += 1
                p2 = idToName(x['second_party_id'])
                id_cache[int(x['second_party_id'])] = p2
            amount = x['amount']
            print("{}: {}: {}: {:,.2f}\t{}\n\th: {} / m:{}".format(date,p1,p2,amount,reason,cache_hits,cache_misses))    

# This function must be modified to accomodate
# the end user's situation            
def getTokens():
	'''
	Returns an arbitrary length tuple of tokens
	for any number of characters.
	'''
    avenhor_token = r.post(auth_base, data = avenhor_data)
    return (avenhor_token)

def getSecStatus(id):
	'''
	Retrieves and returns the security status
	of the system specified by the id parameter
	'''
    if int(id) in sec_cache:
        return sec_cache[int(id)]
    else:
        sec = r.get(query_base + 'universe/systems/' + str(id)).json()['security_status']
        sec_cache[int(id)] = sec
        return sec
    
def getShipKills():
	'''
	Retrieves the list of kill counts for
	all systems by first checking for a
	current, non-expired cache, or making
	an API call if that fails.
	'''
    global kills_cache
    global kills_cache_timestamp
    if kills_cache_timestamp is not None:        
        diff = datetime.now() - kills_cache_timestamp
        if diff.seconds > 3600:
            print('Generating new kills cache')
            kills = r.get(query_base + 'universe/system_kills/')
            for x in kills.json():
                kills_cache[int(x['system_id'])] = x['ship_kills']
            kills_cache_timestamp = datetime.now()
        else:
            print('Using existing kills cache')
    else:
        print('Generating new kills cache')
        kills = r.get(query_base + 'universe/system_kills/')
        for x in kills.json():
            kills_cache[int(x['system_id'])] = x['ship_kills']
        kills_cache_timestamp = datetime.now()
        
def loadConcordCache():
	'''
	Loads the Concord systems defined in
	the concord list variable into a
	cache of string:id
	'''
    for x in concord:
        if x not in system_cache:
            system_cache[x] = nameToId(x,'system')
            
def ospConcord(*args):
	'''
	Finds the nearest Concord system and
	caclulates the safest path to it
	'''
    shortest_path = None
    shortest_path_system = ''
    shortest_route = None
    if args is not None and len(args) != 0:
        loc = nameToId(args[0],'system')
    else:
        loc = getLocation(char_id)
    myloc = idToName(loc)
    print('Starting search in {}'.format(myloc))

    for x in concord:
        if x == 'Amarr':
            continue
        if (myloc in system_cache and x in system_cache):
            route = getRoute(system_cache[myloc],system_cache[x],'','secure')
        else:
            route = getRoute(nameToId(myloc,'system'),nameToId(x,'system'),'','secure')
        route_len = len(route.json())
        if shortest_path is None or route_len < shortest_path:
            shortest_path_system = x
            shortest_path = route_len
            shortest_route = route
        if route_len < 10:
            print('***************** {} -> {}'.format(myloc,x))
            printRoute(route)
        print('{}: {}'.format(x,len(route.json())))
    print('*****************')
    print('*****************')
    print('{} is closest system at {} jumps'.format(shortest_path_system,shortest_path))
    print('***************** {} -> {}'.format(myloc,shortest_path_system))
    printRoute(shortest_route)
    
def getRoute(origin,destination,avoid,flag):
    '''
	Finds a route betweenn two systems specified
	by the origin and destination parameters.
	The avoid parameter defines a system of list of
	systems to be avoided.
    The Flag parameter can be shortest,secure,insecure,or blank
    '''
    param = ''
    query = 'route/' + str(origin) + '/' + str(destination)
    if (avoid != '' and avoid is not None):
        param = '/?avoid='
        if isinstance(avoid,int):
            param += str(avoid)
        elif isinstance(avoid,list):
            for a in avoid:
                param += str(a) + ','
            param = param[:-1]
    if (flag != '' and flag is not None):
        if (avoid != '' and avoid is not None):
            param += '&flag='
        else:
            param += '/?flag='
        param += flag
    query = 'route/' + str(origin) + '/' + str(destination) + param
    return r.get(query_base + query, headers=api_data)

def printRoute(route):
	'''
	Prints the route obtained by the getRoute function
	and displays sec and kills info for each system along the route
	'''
    for x in route.json():
        name = ''
        secStatus = 0
        kills = 0
        global kills_cache
        
        # check if system is in id cache
        if int(x) in id_cache:
            name = id_cache[int(x)]
        else:
            name = idToName(x)
            id_cache[int(x)] = name
        # add system to cache if not present
        if name not in system_cache:
            system_cache[name] = int(x)
        # check if id is in system kills cache
        if x in kills_cache:
            kills = kills_cache[x]
        else:
            kills = 0
            kills_cache[x] = 0
        print('{:<20}{:4.1f}\t{:>4} {:>16}'.format(id_cache[int(x)],float(getSecStatus(x)),kills,'kills last hour'))
        
def main():
	'''
	Runs key functions to populate variables that
	have dependents, and pickles them to a local file
	'''
    global api_data
    global char_id
    global token
    global access_token
    
    print('Loading pickled caches...\n')
    eatPickles()
    print('Grabbing tokens...\n')
    avenhor_token, parke_token = getTokens()

    token = avenhor_token
    char_id = avenhor_char_id

    access_token = token.json()['access_token']
    
    api_data = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    
    print('Loading the Concord cache...')
    loadConcordCache()
    print('Checking ship kills cache...')
    getShipKills()
    print('Pickling caches and vars...')
    makePickles()
    print('Done')
    
def refresh_tokens():
	'''
	Refreshes tokens if they've expired
	'''
    print('Grabbing tokens...\n')
    avenhor_token = getTokens()

    token = avenhor_token
    char_id = avenhor_char_id

    access_token = token.json()['access_token']
    
    api_data = {'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'}
    print('Tokens updated')
