from Block import Block
import time
import threading

class Blockchain:
    def __init__(self, difficulty, broadcast_cb):
        self.difficulty = difficulty
        self.chain = [self.create_genesis_block()]
        self.mempool = [] # Memory pool for transactions that aren't in any block yet
        self.lock = threading.Lock()
        self.currently_mined_block = None
        self.broadcast_cb = broadcast_cb

    def create_genesis_block(self):
        genesis_block = Block(0, "0", time.time(), [])
        return genesis_block

    def compare_replace(self, new_chain_json):
        if len(self.chain) < len(new_chain_json):
            new_chain = [Block.from_json(block_json) for block_json in new_chain_json]

            if Blockchain.is_chain_valid(new_chain, self.difficulty):
                with self.lock:
                    if len(self.chain) >= len(new_chain): # self.chain could have been modified by another thread
                        return

                    if self.currently_mined_block is not None:
                        self.currently_mined_block.stop_mining = True
                        self.currently_mined_block = None
                        print("Mining stopped due to chain replacement.")

                    self.chain = new_chain
                    for block in self.chain:
                        for tx in block.data:
                            if tx in self.mempool:
                                self.mempool.remove(tx)

                    print(f"New blockchain:\n {str(self)}")
            else:
                print(f"Chain is invalid")

    def add_new_transaction(self, transaction):
        if transaction.is_valid():
            with self.lock:
                print(f"Adding new transaction to the mempool:\n {str(transaction)}")
                self.mempool.append(transaction)

                if len(self.mempool) >= 5 and self.currently_mined_block is None:
                    # Create new block, mine it and add it to the blockchain
                    new_block = Block(
                        index=len(self.chain),
                        previous_hash=self.chain[-1].hash,
                        timestamp=time.time(),
                        data=self.mempool.copy()
                    )
                    print("Created new block. Mining it...")
                    self.currently_mined_block = new_block

                    mining_thread = threading.Thread(target=self.start_mining, args=(new_block,))
                    mining_thread.start()
        else:
            print(f"Received invalid transaction")

    def start_mining(self, new_block):
        if new_block.mine_block(self.difficulty):
            with self.lock:
                if not new_block.validate_block(self.chain[-1], self.difficulty):
                    print("Mined block is not valid")
                    self.currently_mined_block = None
                    return

                for tx in new_block.data:
                    if tx not in self.mempool:
                        # Block is invalid - has some transaction that are not in the mempool
                        self.currently_mined_block = None
                        print("Mined block is not valid")
                        return
                for tx in new_block.data:
                    self.mempool.remove(tx)

                self.chain.append(new_block)
                print("New block added to the blockchain.")
                self.currently_mined_block = None

                print("Broadcasting blockchain.")
                self.broadcast_cb()

    def __str__(self):
        blockchain_str = f"\n====================Blockchain========================\n\n"
        blockchain_str += "Mempool (transactions that aren't in any block yet):\n"
        for i in range(0, len(self.mempool)):
            blockchain_str += f"  Mempool Transaction #{i}:\n"
            blockchain_str += str(self.mempool[i])
        blockchain_str += f"\nBlocks:\n"
        for i in range(0, len(self.chain)):
            blockchain_str += f"Block #{i}:\n"
            blockchain_str += str(self.chain[i])
        return blockchain_str

    @staticmethod
    def is_chain_valid(chain, difficulty):
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i-1]
            
            if not current_block.validate_block(previous_block, difficulty):
                return False
        
        return True
