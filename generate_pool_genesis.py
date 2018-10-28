import os
import argparse
import operator
import configparser

from indy_common.config_util import getConfig
from indy_common.config_helper import ConfigHelper, NodeConfigHelper
from ledger.genesis_txn.genesis_txn_file_util import create_genesis_txn_init_ledger
from indy_common.txn_util import getTxnOrderedFields

from stp_core.common.util import adict
from plenum.common.member.member import Member
from plenum.common.member.steward import Steward

from plenum.common.test_network_setup import TestNetworkSetup

nodeParamsFileName = 'indy.env'

def setup_clibase_dir( config, network_name):
    cli_base_net = os.path.join(os.path.expanduser(config.CLI_NETWORK_DIR), network_name)
    if not os.path.exists(cli_base_net):
        os.makedirs(cli_base_net, exist_ok=True)
    return cli_base_net

def init_pool_ledger(appendToLedgers, genesis_dir, config):
        pool_txn_file = config.poolTransactionsFile
        pool_ledger = create_genesis_txn_init_ledger(genesis_dir, pool_txn_file)
        if not appendToLedgers:
            pool_ledger.reset()
        return pool_ledger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="Generate the pool_genesis with node.config")
    parser.add_argument('--network',
                            help='Network name (default sandbox)',
                            type=str,
                            default="sandbox",
                            required=False)
    parser.add_argument(
            '--appendToLedgers',
            help="Determine if ledger files needs to be erased "
            "before writing new information or not. Must be True or false",
            action='store_true')

    args = parser.parse_args()

    nodes = []
   
    cf = configparser.ConfigParser()
    cf.read('node.config')

    for st in cf.sections() :
        d = adict()
        d.name = st
        d.node_ip = cf.get(st,'node_ip')
        d.client_ip = cf.get(st,'client_ip')
        d.node_port = cf.get(st,'node_port')
        d.client_port = cf.get(st,'client_port')
        d.dest = cf.get(st,'dest')
        d.bls_key = cf.get(st,'bls_key')
        d.bls_pop = cf.get(st, 'bls_pop')
        d.fromnym = cf.get(st, 'from')
        d.services = cf.get(st,'services')
        d.islocal = cf.get(st,'islocal')
        nodes.append(d)
    print(nodes)

    getConfig().NETWORK_NAME = args.network

    chroot = None
    config_helper = ConfigHelper(getConfig(),chroot = chroot)
    os.makedirs(config_helper.genesis_dir, exist_ok=True)
    genesis_dir = config_helper.genesis_dir
    keys_dir = config_helper.keys_dir

    poolLedger = init_pool_ledger(args.appendToLedgers, genesis_dir, getConfig())    

    genesis_dir = setup_clibase_dir(getConfig(), args.network)
    keys_dir = os.path.join(genesis_dir, "keys")
    poolLedger1 = init_pool_ledger(args.appendToLedgers, genesis_dir, getConfig())    

    genesis_protocol_version = None

    seq_no = 1
    for nd in nodes:
        if operator.eq('False',nd.islocal):
            config = getConfig()
            config_helper = ConfigHelper(config, chroot=None)
            os.makedirs(config_helper.keys_dir+'/'+nd.name+'/bls_keys', exist_ok=True)  
            with open(config_helper.keys_dir+'/'+nd.name+'/bls_keys'+'/bls_pk','w+')            as f:
                f.write(d.bls_key)          
        else:
            if nd.node_ip != '127.0.0.1':
                    paramsFilePath = os.path.join(getConfig().GENERAL_CONFIG_DIR                                                 , nodeParamsFileName)
                    print('Nodes will not run locally, so writing {}'.format(paramsFilePath))
                    TestNetworkSetup.writeNodeParamsFile(paramsFilePath, nd.name                   ,"0.0.0.0", nd.port,
                    "0.0.0.0", nd.client_port)
    
        node_txn = Steward.node_txn(nd.fromnym,nd.name,nd.dest,
                                    nd.node_ip,int(nd.node_port),
                                    int(nd.client_port),
                                    blskey=nd.bls_key, 
                                    bls_key_proof=nd.bls_pop,
                                    seq_no=seq_no,
                                    protocol_version=genesis_protocol_version)
        
        seq_no +=1
        poolLedger.add(node_txn)
        poolLedger1.add(node_txn)

poolLedger.stop()
poolLedger1.stop() 

