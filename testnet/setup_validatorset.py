#!/usr/bin/python3

import os
import subprocess
import sys
from shutil import copyfile

num_nodes = int(sys.argv[1])

def run_cmd(args, cwd=None):
    p = subprocess.Popen(args, cwd=cwd)
    p.wait()

print('Generating Docker config volume folders for {num_nodes} hbbft nodes'.format(num_nodes=num_nodes))

generator_dir = '../../openethereum/ethcore/engines/hbbft/hbbft_config_generator'

cmd = ['cargo', 'run', str(num_nodes), "Docker"]
if len(sys.argv) > 2:
    cmd.append(sys.argv[2])

run_cmd(cmd, generator_dir)

# The location of the hbbft-posdao-contracts repository clone.
posdao_contracts_dir = '../../hbbft-posdao-contracts'
# The JSON file with initialization data produced by hbbft_config_generator, relative to the hbbft-posdao-contracts folder.
init_data_file = '../openethereum/ethcore/engines/hbbft/hbbft_config_generator/keygen_history.json'

os.environ["NETWORK_NAME"] = "DPoSChain"
os.environ["NETWORK_ID"] = "101"
os.environ["OWNER"] = "0x32e4e4c7c5d1cea5db5f9202a9e4d99e56c91a24"
os.environ["FIRST_VALIDATOR_IS_UNREMOVABLE"] = "true"
os.environ["STAKING_EPOCH_DURATION"] = "80"
os.environ["STAKE_WITHDRAW_DISALLOW_PERIOD"] = "10"
os.environ["COLLECT_ROUND_LENGTH"] = "20"

# Invoke the hbbft chain spec generation script
cmd = ['node', 'scripts/make_spec_validatorset.js', init_data_file]
run_cmd(cmd, posdao_contracts_dir)

# Output of chain spec generation
spec_file = '../../hbbft-posdao-contracts/spec_validatorset.json'

# Set up validator nodes
for i in range(1, num_nodes + 1):
    print("Setting up config for node {}".format(i))
    os.makedirs("nodes/node{}/data/network".format(i), exist_ok=True)
    os.makedirs("nodes/node{}/data/keys/DPoSChain".format(i), exist_ok=True)
    copyfile(generator_dir + "/hbbft_validator_{}.toml".format(i), "nodes/node{}/node.toml".format(i))
    copyfile(generator_dir + "/hbbft_validator_key_{}".format(i), "nodes/node{}/data/network/key".format(i))
    copyfile(generator_dir + "/reserved-peers", "nodes/node{}/reserved-peers".format(i))
    copyfile(spec_file, "nodes/node{}/spec.json".format(i))
    copyfile(generator_dir + "/password.txt", "nodes/node{}/password.txt".format(i))
    copyfile(generator_dir + "/hbbft_validator_key_{}.json".format(i), "nodes/node{}/data/keys/DPoSChain/hbbft_validator_key.json".format(i))    
    
# Set up Rpc node
os.makedirs("nodes/rpc_node", exist_ok=True)
copyfile(generator_dir + "/rpc_node.toml", "nodes/rpc_node/node.toml")
copyfile(generator_dir + "/reserved-peers", "nodes/rpc_node/reserved-peers")
copyfile(spec_file, "nodes/rpc_node/spec.json")
