# Start-network-scripts
#### There are some scripts helping you build the indy network with docker .
 ---
## At first, we will build the test network and you will know how to use the scripts.

##### (1) **download and enter this file** 
```
 git clone https://github.com/zixian5/indy-start-scripts.git
 cd indy-start-scripts
```
##### (2) **build a docker image with indy-startlocal.dockerfile**
```
docker build -f indy-startlocal.dockerfile -t indy_start .
```
##### (3) **build  the container and find its name.**
```
docker run -itd -p 9701-9708:9701-9708 indy_start
docker ps 
```
>Remember the container's name that shows.
##### (4) **copy this folder into the container**
```
docker cp ../indy-start-scripts/ {container's name}:/home/indy/start
```
##### (5) **enter the container and enter the folder that we will use** 
```
docker exec -it {container's name} bash
cd /home/indy/start
```
##### (6) **init some nyms with init_nym.py.**
This script can generate the configure about nyms into the nym.config. And the nym.config will be used to generate the domain_transactions_genesis.

>**Please remeber the first nym you generate must be a TRUSTEE**.

If you want more information about this script, please run 
           ```  python3 init_nym.py -h   ```
           
>And now, we'll build the nyms that are in the test network.
```
python3 init_nym.py --name Trustee --role TRUSTEE --seed 000000000000000000000000Trustee1
```
 Now ,it will generate a TRUSTEE into the nym.config. Please read it and remeber the parameter nym .

>Then ,we'll generate four STEWARDs.

```
python3 init_nym.py --name Steward1 --role STEWARD --seed 000000000000000000000000Steward1 --fromnym V4SGRU86Z58d6TV7PBUe6f
python3 init_nym.py --name Steward2 --role STEWARD --seed 000000000000000000000000Steward2 --fromnym V4SGRU86Z58d6TV7PBUe6f
python3 init_nym.py --name Steward3 --role STEWARD --seed 000000000000000000000000Steward3 --fromnym V4SGRU86Z58d6TV7PBUe6f
python3 init_nym.py --name Steward4 --role STEWARD --seed 000000000000000000000000Steward4 --fromnym V4SGRU86Z58d6TV7PBUe6f
```
You can run vim nym.config , and find the configure.
##### (7) **init the nodes' keys with init_node_keys_tofile.py.**
This script can generate the key file and its path is */var/lib/indy/sandbox/keys* .
And it will generate the key's information into the node.config ,it will be used to generate the pool_transactions_genesis.
If you want more information about this script, please run
        ``` python3 init_node_keys_tofile.py -h ```
```
python3 init_node_keys_tofile.py --name Node4 --seed 000000000000000000000000000Node4
python3 init_node_keys_tofile.py --name Node3 --seed 000000000000000000000000000Node3
python3 init_node_keys_tofile.py --name Node3 --seed 000000000000000000000000000Node3
python3 init_node_keys_tofile.py --name Node1 --seed 000000000000000000000000000Node1
```
##### (8) **init the nodes' information with init_node_base.py.**
```
python3 init_node_base.py --name Node1 --fromnym Th7MpTaRZVRYnPiabds81Y --ip 127.0.0.1 --node_port 9701 --client_port 9702
python3 init_node_base.py --name Node2 --fromnym EbP4aYNeTHL6q385GuVpRV --ip 127.0.0.1 --node_port 9703 --client_port 9704
python3 init_node_base.py --name Node3 --fromnym 4cU41vWW82ArfxJxHkzXPG --ip 127.0.0.1 --node_port 9705 --client_port 9706 
 python3 init_node_base.py --name Node4 --fromnym TWwCRQRZ2ZHMJFn9TzLp7W --ip 127.0.0.1 --node_port 9707 --client_port 9708
```
You can run vim node.config.
##### (9) **generate pool_transactions_genesis and domain_transactions_genesis** 
```
python3 generate_domain_genesis.py 
python3 generate_pool_genesis.py 
```
##### (10) **start four nodes**.
```
/usr/bin/supervisord
```
This command will run forever. So if you want to control the container, please run ``` docker exec -it {container's name} bash ``` again.

##### (11) **test the network with sdk.**
There are several sdks you can use and you can choose the language .
One import thing is that you need to change the ip in the genesis configure file. In this sample ,we use '127.0.0.1'.
 Here are some samples:

       1.a java sample(https://github.com/blokaly/indy-java-cli)
       2.offical sdks and samples (https://github.com/hyperledger/indy-sdk/)
 ----
#### Now if you want build the network in your own way ,there are several place needing to be changed.
  (1) Using the indy-start-local.dockerfile instead and modify the  config in /etc/supervisord.conf 
 
(2) Every one who joins the network can generate the nym by using his own seed. So after generating the nyms, they need exchanging them and modify the nym.config by using vim. But everyone' s nym.config must be same and the first role must be TRUSTEE.
   
 (3) Using init_node_base.py and init_node_keys_tofile.py to generate the config and keys file for the node running in local. However, other node's config you need add them into the node.config by yourself.
>One important thing is that you need to change the parameter islocal from 'True' to 'False'.
   
  (4) And then ,you can generate genesis file and test your network.
