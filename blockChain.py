from datetime import time
import hashlib
import json

class blockchain():
    def __init__(self,gen=False):
        if gen:
            self.blocks = []
        else:
            with open("LandRegistryDatabase.json",'r') as f:
                self.blocks = json.load(f)
        self.__secret = ''
        self.__difficulty = 4 
        i = 0
        while True:
            _hash = hashlib.sha256(str( str(i)).encode('utf-8')).hexdigest()
            if(_hash[:self.__difficulty] == '0'*self.__difficulty):
                self.__secret = _hash
                break
            i+=1
    def create_block(self,prod_id="nil",role="nil",mfdate="nil",exdate="nil",mrp="nil",pname="nil",cat="nil",dis="nil"):
        block = {
            'index': len(self.blocks),
            'product_id': prod_id,
            "role":role,
            "mfdate":mfdate,
            "exdate":exdate,
            "mrp":mrp,
            "pname":pname,
            "cat":cat,
            "dis":dis,
            'timestamp': str(time())
        }
        if(block['index'] == 0):
            block['previous_hash'] = self.__secret # for genesis block
            block['dis'] ="This is a genesis block"
        else:
            block['previous_hash'] = self.blocks[-1]['hash']
        i = 0
        while True:
            block['nonce'] = i
            _hash = hashlib.sha256(str(block).encode('utf-8')).hexdigest()
            if(_hash[:self.__difficulty] == '0'*self.__difficulty):
                block['hash'] = _hash
                break
            i+=1
        self.blocks.append(block)
        with open("LandRegistryDatabase.json",'w') as f:
            json.dump(self.blocks,f)
        
    def validate_blockchain(self):
        valid = True
        n = len(self.blocks)-1
        i = 0
        while(i<n):
            if(self.blocks[i]['hash'] != self.blocks[i+1]['previous_hash']):
                valid = False
                break
            i+=1
        if valid: return True
        else: return False
    def show_blockchain(self):
        for block in self.blocks: 
            print(block)
    def check_id(self,prod_id):
        check_block=[]
        for block in self.blocks:
            if block['product_id']==prod_id:
                check_block.append(block)
        return check_block
