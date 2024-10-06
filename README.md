# Blockchain
A decentralized blockchain system implemented in Python.
Work in Progress

## Table of Contents
* [General Info](#general-information)
* [Network Architecture](#network-architecture)
* [Workflow](#workflow)
* [Future Improvements](#future-improvements)

## General Information
This project implements a simplified blockchain from scratch in Python. The blockchain includes essential features like transaction validation, proof of work (PoW), and peer-to-peer (P2P) networking. 

## Network Architecture
This blockchain operates in a Peer-to-Peer (P2P) network, which is decentralized, meaning there is no central server. Instead, every user in the network serves as both a server and a client simultaneously.

The P2P network of this blockchain is designed so that each node is connected to every other node. Each node locally stores a list of all other peers currently available in the network. When a new node wants to join the network, it must provide the IP address and port of an existing node (assuming the network already exists). The new node then sends a request to that existing node asking for the list of peers (IP addresses and ports). Once it receives the list, the new node broadcasts its presence to all the peers, allowing them to add it to their own peer lists.

When a node leaves the network, it broadcasts a message to all peers, notifying them to update their peer lists accordingly.

## Workflow
#### Node setup
For information on the network architecture and how new nodes are added to an existing network, please refer to the Network Architecture section.

The first node in the network creates the Genesis Block.

When creating a node, a Wallet object is also created to store encryption keys. One can provide their existing encryption keys if available, or the program will generate new ones if none are provided.

When a new node joins the network and broadcasts its presence, other nodes respond by sending their copy of the blockchain. The new node then selects the longest valid blockchain (with the most blocks) from the responses and sets it as its own blockchain copy.

#### Creating Transactions
Transactions store information about the sender’s public key, recipient’s public key, amount, and timestamp. Additionally, the transaction must be signed by the sender with their private key to be valid — the signature is stored in the signature field, and signing is handled by the Wallet class.

Once a transaction is created by a node, it is broadcast to all other nodes. This node, as well as others that receive the new transaction, checks if the transaction is valid (by checking the sender's signature) and if yes then adds it to their mempool, which is stored within the Blockchain class.

#### Mining a Block & Proof of Work
When there are at least 5 transactions in the mempool, the program creates a new block and starts mining it. Blocks contain the following information: index, previous block’s hash, timestamp, the block’s own hash, nonce (Proof of Work number), and data. The data is a list of transactions. The new block is created with all the transactions from the mempool.

Mining a block involves finding the correct nonce value. Initially, the nonce is set to 0 when the block is created. Each change to this number causes the block’s hash to change significantly. Mining is the process of finding a nonce value such that the block’s hash starts with four zeros. Only then is the block considered valid.

A node can mine only one block at a time (mining happens in a separate thread to prevent blocking the program). Mining more than one block simultaneously wouldn’t make sense because the first block to be mined will be added to the blockchain, and any subsequent block being mined doesn’t know the hash of its predecessor, making it invalid.

After mining a block, it is checked to ensure it is valid and that all of its transactions are still in the blockchain’s mempool. If valid, the transactions are removed from the mempool, the new block is added to the chain, and the entire chain of the node that mined the block is broadcasted to other nodes.

#### Consensus Mechanism
The consensus mechanism is that nodes always select the longest chain as the valid one, provided it is correct. A valid chain is one where each block contains the hash of the previous block, its own hash is correctly calculated, and the hash starts with four zeros. If a node receives a valid copy of a longer chain from another node, it adopts it as its own.

If a node was mining a block while accepting a new chain, the mining process is halted. This happens because the block being mined would no longer be valid, as the previous block’s hash has changed.

When a node receives and accepts a new chain, it checks all the transactions contained within it. If any transaction is still in the mempool, it is removed.

## Future Improvements Ideas
#### Lack of Chain Synchronization Mechanism in the Consensus Process
Currently, when a new block is created, a node broadcasts its entire blockchain instead of just the new block, which is inefficient. A synchronization mechanism should be considered, allowing only the newly created blocks to be transmitted. This mechanism should also be able to resolve conflicts when receiving a block whose previous block hash does not match the hash of the last block in the current chain.

#### Fully-Connected Network Architecture
The current network design, where every node connects to every other node, is highly inefficient. Instead, each node should connect to only a few other nodes rather than to all others. The current architecture significantly slows down communication between nodes.

#### Lack of Transaction Sender's Balance Verification
There is currently no mechanism to check if the sender of a transaction has sufficient funds. To implement this, the genesis block could include the initial distribution of funds, and during transaction validation, the entire chain could be traversed to verify that the sender has the necessary funds for the transaction.

#### Blocks Only Store Transactions
At present, blocks can only store transactions. It may be worth considering allowing blocks to store other types of data, such as election votes.

#### Graphical User Interface (GUI)
Currently, the program is only operated through the console. A GUI could be developed to allow users to visualize the current blockchain and to create new transactions more easily.
