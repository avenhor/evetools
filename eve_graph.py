'''
This tool creates a new Graph object and populates it using the all systems
list obtained from the ESI API.

This module requires the Networkx library available at the following URL:
https://networkx.github.io or via pip:
pip install networkx
'''
__author__ = "Avenhor Hastmena"
__copyright__ = "Copyright 2018"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Avenhor Hastmena"
__email__ = "avenhor@gmail.com"
__status__ = "Development"

from time import sleep
import sys
import requests as r
import networkx
'''
processed_systesm stores systems that have been added to the graph and all edges identified
Useful if this process must be restarted, but additional handling must be added if running
this code outside of a Jupyter or iPython notebook so that the list does not get clobbered
each time this code is invoked

If using this code as a module, declare the list locally and implement a system to protect
it while loading the graph. Pickling is a good idea in this case
'''
processed_systems = [] # need to handle this per above note
G = nx.Graph() # Graph object
AU = 149597900
LY =  9460730472580800
LYk = LY/1000

class GetOutOfLoop( Exception ):
    pass

def load_graph():
	'''
	Iterates over the list of all systems obtained from the
	universe/systems endpoint
	'''
	global processed_systems
	global G

	counter = 0
	error_nodes = {}
	
	query_base = 'https://esi.tech.ccp.is/latest/'
	all_systems = r.get(query_base + 'universe/systems')

	for u in all_systems.json():
		try:
			if counter % 1000 == 0 and counter != 0:
				print('Taking a break')
				sleep(5)
			counter += 1
			if u in processed_systems:
				print('@',end='')
				continue
			tmp = r.get(query_base + 'universe/systems/' + str(u))
			for x in tmp.json()['stargates']:
				try:
					resp = r.get(query_base + 'universe/stargates/' + str(x))
					v = resp.json()['destination']['system_id']
				except Exception as e:
					print('\nCaught exception getting neighbor of {} via stargate {}'.format(u,x))
					print('Exception: {}'.format(e))
					print('Sleeping for 5 seconds before retry')
					sleep(5)
	#                 raise GetOutOfLoop
				if G.has_node(u):                
					if G.has_edge(u,v):
						print('.',end='')
						continue
					else:
	#                     print('\nAdding edge {}:{}'.format(u,v))
						print('-',end='')
				else:
					print('+',end='')
	#                 print('\nAdding system {}'.format(u))
				try:
					print('+',end='')
	#                 print('\tAdding edge to {} via {}'.format(v,x))
					G.add_edge(tmp.json()['system_id'],v)
				except AttributeError as e:
					print(str(e))
					raise GetOutOfLoop
				except KeyboardInterrupt as kb:
					print(kb)
					raise GetOutOfLoop
				except:
					print("Caught an exception when processing {}, stargate {}".format(u,x))
					print("Request response: {}".format(resp.text))
					error_nodes[u + ':' + x] = resp.text
			processed_systems.append(u)
		except GetOutOfLoop:
			print('Breaking out of loops')
			break
		except Exception as ex:
			print('Caught some other error after {} nodes'.format(counter))
			print(ex)

def getSystemInfo(sys_id):
	'''
	Returns a requests result object from the universe/systems/{system_id}
	endpoint for the systems specified by the sys_id parameter

	This function should only be called by the getSystemPosition function
	'''
    return r.get(query_base + 'universe/systems/' + str(sys_id))

def getSystemPosition(sys_id):
	'''
	Returns a tuple of the x,y,z coordinates for a system position
	obtained from the system information result object
	'''
    return tuple(getSystemInfo(sys_id).json()['position'].values())

def addAllEdgeWeights():
	'''
	Iterates over all_systems list and adds edge weights to 
	the edges in the graph using the distance calculations
	in LYk as the measure
	'''
	global G

	for e in list(G.edges()):
		try:
			distance = calcDistance(getSystemPosition(e[0]),getSystemPosition(e[1]))/LYk
			G.add_edge(e[0],e[1],weight = distance)
		except:
			print('Caught exception {}.\nRetrying in 5 seconds'.format(_))
			sleep(5)

def calcDistance(p1,p2):
	'''
	Calculated the distance between two points and returns the
	results with a kilometer unit base
	'''
    x1,y1,z1 = p1
    x2,y2,z2 = p2
    
    return(math.sqrt(((x1-x2)**2) + ((y1-y2)**2) + ((z1-z2)**2))/1000)

'''
If you are not using this as a module, remove/comment the next section
'''
if __name__ == '__main__':
	exit
