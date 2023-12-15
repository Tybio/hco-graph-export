"""Module containing SHQL API Calls formatted for use in python scripts"""


def r_physical_graph():
    """Defines SHQL Query formatted for importing Layer-3 topology into networkx"""
    value = ('link[.layer = "R_PHYSICAL"] |'
             'view ("A-Name": .portA.device.name,'
             '"A-Vendor": .portA.device.vendor,'
             '"B-Name": .portB.device.name,'
             '"B-Vendor": .portB.device.vendor,'
             '"role": .role)'
             )
    return value

def oms_graph():
    """Defines SHQL Query formatted for importing Layer-1 topology into networkx"""
    value = ('link[.layer = "OMS"] |'
             'view ( "A-Name": .portA.device.name,'
             '"A-Vendor": .portA.device.vendor,'
             '"B-Name": .portB.device.name,'
             '"B-Vendor": .portB.device.vendor)'
             )
    return value

def eth_graph():
    """Defines SHQL Query formatted for importing Crosslinks into networkx
        Only valid if r_physical_graph and oms_graph are used to build topologies"""
    value = ('link[.layer = "ETH" and .role = "CROSS_LINK"] |'
             'view ( "NodeA": .portA.device.name,'
             '"NodeB": .portB.device.name)'
             )
    return value
