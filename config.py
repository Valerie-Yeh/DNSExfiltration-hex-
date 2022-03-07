#!/usr/bin/env python3

from dataclasses import dataclass


@dataclass
class es:
    host: str = 'https://192.168.204.134:9200'
    cred: tuple = ('admin', 'admin')
@dataclass
class params:
    alpha: float = 0.5
    beta : float = 0.5


vlan = ['192.168.0.0/16', '140.113.87.0/24']

host = {
    '192.168.1.254': 0.3,         # SDN
    '192.168.1.2'  : 0.5,         # AD server
    '192.168.100.4': 0.3,         # DNS
    '192.168.1.50' : 0.3,         # Logstash
    '192.168.1.60' : 0.3,         # Kibana
    '192.168.1.80' : 0.3,         # ElasticSearch
    '140.113.87.19': 0.5,
    'default'      : 0.1
}

port = {
    22       : 0.9,
    445      : 0.9,
    80       : 0.9,
    443      : 0.9,
    23       : 0.8,
    139      : 0.8,
    21       : 0.8,
    135      : 0.8,
    53       : 0.2,
    'default': 0.1
}
