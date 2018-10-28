#!/usr/bin/python3

import argparse
import os.path
import configparser


from plenum.common.keygen_utils import initNodeKeysForBothStacks
from plenum.common.constants import CLIENT_STACK_SUFFIX

from indy_common.config_util import getConfig
from indy_common.config_helper import NodeConfigHelper


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate configuration for a node's stacks "
                    "by taking the node's ip client and from "
                    "And it will generate node.config in this file path")

    parser.add_argument('--name', required=True, help='node name')
    parser.add_argument('--fromnym', required=False ,help='the NYM who signs the node')
    parser.add_argument('--ip',required=False, help='Node ip. Default = 127.0.0.1')
    parser.add_argument('--node_port',required=True ,help='Node port')
    parser.add_argument('--client_port',required=True ,help='client port')
    parser.add_argument('--services',required=False, help='The service of the NOde.VALIDATOR is the only supported one now')
    args = parser.parse_args()	    

    node_ip ='127.0.0.1' if not args.ip else args.ip

    print("Node-stack name is", args.name)
        
    cf = configparser.ConfigParser()
    cf.read('node.config')

    if not cf.has_section(args.name):
        cf.add_section(args.name)
    
    fromnym = args.fromnym if args.fromnym else ''
    cf.set(args.name,'from',fromnym)
    cf.set(args.name,'node_ip',node_ip)
    cf.set(args.name,'node_port',args.node_port)
    cf.set(args.name,'client_ip',node_ip)
    cf.set(args.name,'client_port',args.client_port)
    cf.set(args.name,'services','VALIDATOR')
    cf.set(args.name,'islocal','True')

    with open('node.config', 'w') as fw:
            cf.write(fw)



    



