import configparser
import operator
import argparse
import os

from indy_common.config_util import getConfig
from indy_common.config_helper import ConfigHelper, NodeConfigHelper
from ledger.genesis_txn.genesis_txn_file_util import create_genesis_txn_init_ledger
from indy_common.txn_util import getTxnOrderedFields

from stp_core.common.util import adict
from plenum.common.member.member import Member
from plenum.common.member.steward import Steward

def setup_clibase_dir( config, network_name):
    cli_base_net = os.path.join(os.path.expanduser(config.CLI_NETWORK_DIR), network_name)
    if not os.path.exists(cli_base_net):
        os.makedirs(cli_base_net, exist_ok=True)
    return cli_base_net

def init_domain_ledger(appendToLedgers, genesis_dir, config, domainTxnFieldOrder):
    domain_txn_file = config.domainTransactionsFile
    domain_ledger = create_genesis_txn_init_ledger(genesis_dir, domain_txn_file)
    if not appendToLedgers:
        domain_ledger.reset()
    return domain_ledger

genesis_protocol_version = None

def domain(domainLedger , nyms):
    seq_no = 1
    trustee_txn = Member.nym_txn(nyms[0].nym,verkey = nyms[0].verkey,
                                 role='0',seq_no=seq_no,
                                 protocol_version=genesis_protocol_version)
    seq_no += 1
    domainLedger.add(trustee_txn)

    roles = {'TRUSTEE':'0','STEWARD':'2','TRUST_ANCHOR':'101'}
 
    for d in nyms[1:]:
        if operator.eq('CLIENT', d.role):
            nym_txn = Member.nym_txn(d.nym, verkey=d.verkey ,
                                    creator = d.fromnym ,seq_no=seq_no,
                                    protocol_version=genesis_protocol_version)
        else:
            nym_txn = Member.nym_txn(d.nym, verkey=d.verkey ,role = roles[d.role],
                                    creator = d.fromnym ,seq_no=seq_no,
                                    protocol_version=genesis_protocol_version)
        seq_no +=1
        domainLedger.add(nym_txn)
        print(nym_txn)
    domainLedger.stop()      

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="Generate the domain_genesis with nym.config")    
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
     
    print(args.appendToLedgers)  
    nyms = [] 

    cf = configparser.ConfigParser()
    cf.read('nym.config')

    i=0    
    for st in cf.sections() :
        
        if i == 0:
            if not operator.eq('TRUSTEE',cf.get(st,'role')) :
                print('The first nym must be a TRUSTEE') 
                os._exit(0)
        i+=1

        d=adict()
        d.name = st
        d.nym = cf.get(st,'nym')
        d.fromnym= cf.get(st,'from')
        d.role = cf.get(st,'role')
        d.verkey = cf.get(st,'verkey')
        
        nyms.append(d)

    print(nyms)
    
    getConfig().NETWORK_NAME = args.network

    chroot = None
    config_helper = ConfigHelper(getConfig(),chroot = chroot)
    os.makedirs(config_helper.genesis_dir, exist_ok=True)
    genesis_dir = config_helper.genesis_dir
    keys_dir = config_helper.keys_dir
    print(keys_dir)
    domainLedger = init_domain_ledger(args.appendToLedgers, genesis_dir,
                                       getConfig(), getTxnOrderedFields())
    domain(domainLedger , nyms)
    
    
    genesis_dir = setup_clibase_dir(getConfig(), args.network)
    keys_dir = os.path.join(genesis_dir, "keys")
    
    domainLedger = init_domain_ledger(args.appendToLedgers, genesis_dir,
                                          getConfig(), getTxnOrderedFields())
    domain(domainLedger ,nyms)
