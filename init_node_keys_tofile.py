#!/usr/bin/python3

import argparse
import os.path
import configparser

from plenum.common.keygen_utils import initNodeKeysForBothStacks
from plenum.common.constants import CLIENT_STACK_SUFFIX
from plenum.common.util import hexToFriendly

from indy_common.config_util import getConfig
from indy_common.config_helper import NodeConfigHelper


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate keys for a node's stacks "
                    "by taking the node's name and 2 "
                    "seed values")

    parser.add_argument('--name', required=True, help='node name')
    parser.add_argument('--seed', required=False, type=str,
                        help='seed for keypair')
    parser.add_argument('--force', help='overrides keys', action='store_true')
    args = parser.parse_args()

    print("Node-stack name is", args.name)
    print("Client-stack name is", args.name + CLIENT_STACK_SUFFIX)

    config = getConfig()
    config_helper = NodeConfigHelper(args.name, config)

    os.makedirs(config_helper.keys_dir, exist_ok=True)

    try:
       _, verkey, blskey, key_proof =  initNodeKeysForBothStacks(args.name, config_helper.keys_dir, args.seed, override=args.force)
    except Exception as ex:
        print(ex)
        exit()

    nym=hexToFriendly(verkey.encode())

    cf = configparser.ConfigParser()
    cf.read('node.config')
    
    if not cf.has_section(args.name):
        cf.add_section(args.name)

    cf.set(args.name,'dest',nym)
    cf.set(args.name,'bls_key',blskey)
    cf.set(args.name,'bls_pop',key_proof)

    with open('node.config', 'w') as fw:
            cf.write(fw)  
	

