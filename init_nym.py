import os
import argparse
import configparser
from plenum.common.signer_did import DidSigner
from stp_core.crypto.util import randomSeed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="Generate a NYM and a configure named nym.config in this path ")
    parser.add_argument('--name', required=True, help='node name')
    parser.add_argument("--role",required=False ,help='Role of a user NYM record.You can choose: TRUSTEE STEWARD TRUST_ANCHOR. The default is client.')
    parser.add_argument("--fromnym",required=False , help='The did who signed this role.  ')    
    parser.add_argument('--seed', required=False, type=str,
                        help='seed for keypair.Please don\'t forget it. You would better choose it by yourself.Or it wouble a random.')

    args = parser.parse_args()
    
    roles = set(['TRUSTEE','STEWARD','TRUST_ANCHOR','CLIENT'])
    role = args.role
    if not args.role :
        role ='CLIENT'
    if not role in roles :
        print('ERROR! Please reset the role')
        os._exit(0)

    myseed = args.seed
    if not myseed:
        myseed = randomSeed().decode()
        print("Generating keys for random seed", myseed)
    else :
        print("Generating keys for provided seed", myseed)
    
    signer = DidSigner(seed=myseed.encode())  
    nym = signer.identifier
    verkey = signer.verkey  

    cf = configparser.ConfigParser()
    cf.read('nym.config')

    if not cf.has_section(args.name):
        cf.add_section(args.name)

    cf.set(args.name,'role',role)
    cf.set(args.name,'nym',nym)
    print('the nym is',nym)
    cf.set(args.name,'verkey',verkey)  
    fromnym = args.fromnym  if args.fromnym else ""
    cf.set(args.name,'from',fromnym)

    with open('nym.config', 'w') as fw:
        cf.write(fw)                                                                                                                                                                  
