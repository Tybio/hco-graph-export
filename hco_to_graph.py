import networkx as nx
import matplotlib.pyplot as plt
import json
import requests
import argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

### Commandline Stuff ###

argParser = argparse.ArgumentParser()
argParser.add_argument("-1", "--layer1", action='store_true',  help="Add Layer1 information to output")
argParser.add_argument("-3", "--layer3", action='store_true', help="Add Layer3 information to output")
argParser.add_argument("-o", "--outfile", help="Output file name", required=True, default="stdout")

args = argParser.parse_args()
outfile = args.outfile
### Server Address ###
hco_server = '192.168.56.11'
### API Root ###
shql_api = f"https://{hco_server}/api/v2/shql/"

### Build query for  topology information from HCO via SHQL ###
if args.layer3: qLOGTopo = 'link[.layer = "R_LOGICAL"] | view ("portA-Name": .portA.device.name, "portA-ID": .id, "portB-Name": .portB.device.name, "portB-ID": .id)'
if args.layer1: qOPTTopo = 'link[.layer = "OMS"] | view ( "oportA-Name": .portA.device.name, "oportA-type": .portA.device.vendor, "oportB-Name": .portB.device.name, "oportB-type": .portB.device.vendor)'
session = requests.Session()

### Run query ###
if args.layer3: rLOGTopo = session.post(shql_api, data=qLOGTopo, verify=False, auth=('admin', 'admin'), headers={'Content-Type': 'text/plain'})
if args.layer1: rOPTTopo = session.post(shql_api, data=qOPTTopo, verify=False, auth=('admin', 'admin'), headers={'Content-Type': 'text/plain'})

### Transform response to json ###
if args.layer3: dLOGTopo = rLOGTopo.json()
if args.layer1: dOPTTopo = rOPTTopo.json()

### Start networkx graph instance ###
N=nx.Graph()

### Iterate over the L3 topology returned and insert it into the graph ###
if args.layer3:
  for link in dLOGTopo:
    firstNode = link["portA-Name"]
    secondNode = link["portB-Name"]
    
    if not firstNode in N: N.add_node(firstNode, type=firstNode[:2])
    if not secondNode in N: N.add_node(secondNode, type=secondNode[:2])
    
    N.add_edge(link["portA-Name"], link["portB-Name"])


### Iterate over the L1 topology returned and insert it into the graph ###
if args.layer1:
  for link in dOPTTopo:
    firstROADM = link["oportA-Name"]
    secondROADM = link["oportB-Name"]
    
    if not firstROADM in N: N.add_node(firstROADM, type=link["oportA-type"])
    if not secondROADM in N: N.add_node(secondROADM, type=link["oportB-type"])
    
    if not N.has_edge(firstROADM, secondROADM): N.add_edge(link["oportA-Name"], link["oportB-Name"])

### Write out a json topology ###
with open(outfile, 'w') as f:
    json.dump(nx.node_link_data(N), f)
