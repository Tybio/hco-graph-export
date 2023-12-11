import json
import argparse
import networkx as nx
import requests
######################
#   Config Crap      #
######################
### Server Address ###
HCO_SERVER = '192.168.1.103'
### URL ###
target = f"https://{HCO_SERVER}/api/v2/shql/"

### Commandline Stuff ###

argParser = argparse.ArgumentParser()
argParser.add_argument(
    "-1", "--layer1", 
    action='store_false',
    help="Add Layer1 information to output"
    )

argParser.add_argument(
    "-3", "--layer3", 
    action='store_false',
    help="Add Layer3 information to output"
    )

argParser.add_argument(
    "-o", "--outfile", 
    help="Output file name",
    default="output.json"
    )

args = argParser.parse_args()
outfile = args.outfile

### Start networkx graph instance ###
N=nx.Graph()



### Funtion to deal with http crud ###

def post_query(data=None):
    session = requests.Session()
    response = session.post(target,
                            data=data,
                            verify=False,
                            auth=('admin', 'admin'),
                            headers={'Content-Type': 'text/plain'}
                            )
    output = response.json()
    return output

def check_node(d, v, l):
    nrole = 'Core'
    if not d in N and l == 'Layer3':
        if 'ER' in d:
            nrole = 'Edge'
        N.add_node(d, role=nrole, vendor=v)
    if not d in N and l == 'Layer1':
        N.add_node(d, role='ROADM', vendor=v)
    return True

if args.layer3:
    D_L3TOPO = post_query(data='link[.layer = "R_PHYSICAL"] |'
                          'view ("A-Name": .portA.device.name,'
                          '"A-Vendor": .portA.device.vendor,'
                          '"B-Name": .portB.device.name,'
                          '"B-Vendor": .portB.device.vendor,'
                          '"role": .role)'
                         )
    for link in D_L3TOPO:
        check_node(link["A-Name"], link["A-Vendor"], 'Layer3')
        check_node(link["B-Name"], link["B-Vendor"], 'Layer3')
        N.add_edge(link["A-Name"], link["B-Name"], role=link["role"])

if args.layer1:
    D_OTOPO = post_query(data='link[.layer = "OMS"] |'
                         'view ( "A-Name": .portA.device.name,'
                         '"A-Vendor": .portA.device.vendor,'
                         '"B-Name": .portB.device.name,'
                         '"B-Vendor": .portB.device.vendor)'
                         )
    for link in D_OTOPO:
        check_node(link["A-Name"], link["A-Vendor"], 'Layer1')
        check_node(link["B-Name"], link["B-Vendor"], 'Layer1')
        N.add_edge(link["A-Name"], link["B-Name"], role='L1_Link')



if args.layer1 and args.layer3:
    D_CLINK = post_query(data='link[.layer = "ETH" and .role = "CROSS_LINK"] |'
                         'view ( "NodeA": .portA.device.name,'
                         '"NodeB": .portB.device.name)'
                         )
    for link in D_CLINK:
        if link["NodeA"] in N and link["NodeB"] in N:
            N.add_edge(link["NodeA"], link["NodeB"], role='Cross_link')

print(f"Nodes: {N.number_of_nodes()}")
print(f"Edges: {N.number_of_edges()}")
### Write out a json topology ###
with open(outfile, "w", encoding="utf-8") as f:
    json.dump(nx.node_link_data(N), f, indent=4)
