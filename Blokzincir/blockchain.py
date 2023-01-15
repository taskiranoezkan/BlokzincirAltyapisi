# Module-1-Create a Blockchain

# Importing the libraries
import datetime
# her blok zaman damgasına sahip olacaktır
import hashlib
# verilerin özet fonksiyonu kullanılarak şifrelenmesi
import json
# Blokları kodlamak için bu kütüphanedeki dumps fonksiyonlarını kullanacağız
from flask import Flask, jsonify
# Flask sınıfının nesnesi bizim web uygulamamız olacaktır.
# jsonify,blok zincirimizle etkileşime girdiğimizde postman'daki mesajları döndürmek için kullanacağımzı bir işlevdir.

# Part-1-Building a Blockchain


class Blockchain: # Blockchain classı

    # Constructor ## Self sınıf içierisinde metotlara,parametrelere ulaşmak için kullanılır.
    def __init__(self): # İlklendirilmiş fonksiyon
        self.chain = []  # Blokları içeren zincir
        self.create_block(proof=1, previous_hash='0')  # Genesis block

    def create_block(self, proof, previous_hash):  # Blok Oluşturma
        block = {"index": len(self.chain)+1, # Kaçıncı zincir
                 "timestamp": str(datetime.datetime.now()), # Tarih-zaman damgası
                 "proof": proof, # İş kanıtı.Yani proof_of_work fonksiyonundan elde edilen sayı
                 "previous_hash": previous_hash} #Bİr önceki hash
        self.chain.append(block)  # Bloğu zincire ekleme
        return block  # Postmanda bloğun döndürülmesi

    # Herhangi bir anda uğraştığımız mevcut zincirin son bloğunu almak için kullanılacak
    def get_previous_block(self):
        return self.chain[-1] # Son bloğu döndürüyoruz pythonda son böyledir
    
    # Çözmesi zor doğrulaması kolay bir problem iş kanıtı ile sağlanacak 
    def  proof_of_work(self, previous_proof): # İş kanıtı Fonksiyonu.oluşturulacak nesne uygulayacak.Önceki kanıt madencilerin yeni kanıtı bulmak için dikkate almaları gerekir
        new_proof = 1 # 1'den başlatarak deneme yanılma yoluyla doğru kanıtı bulmaya çalışıyoruz
        check_proof = False # Bulunan kanıtın doğru olup olmaması durumunu kontrol eder
        
        while check_proof is False: # Doğru kanıt yani sayının bulunması için döngüyü başlattık 
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest() # Hash fonksiyonu olan sha-256 64 karakterlik 16'lık sistem kullanır ve ilk 4 karakterin "0" olmasını istiyoruz
            # Baştaki "0" miktarının artması problemi zorlaştıracaktır.Encode ile bulunan proof sha-256 ile tekrardan şifreleniyor.Hexdigest ile bulunan sayının şifrelenmesi 16'lık sistemde olması amaçlandı
            if hash_operation[:4] == '0000': # İlk karakterin "0" olması kontrol edildi 
                check_proof = True
            else:
                new_proof +=1   
        return new_proof
    
    def hash(self, block): #Blokların hash edilemsi için fonskiyon 
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    # -1-Burada kontol edeceğimiz ilk şey her bloğun bir önceki hash'inin bir önceki bloğun hash'ine eşit olup olmadığıdır
    # -2-İkinci durum ise her bloğun ispatının bu iş ispatı fonksiyonunda tannımladığımız iş ispatı problemimize göre geçerli olup olmadığıdır
    def is_chain_valid(self, chain): # Blok zincirimizin geçerli olup olmadığını kontrol edecek olan chain validation fonksiyonu
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index] # Mevcut bloğu aldık
            if block['previous_hash'] != self.hash(previous_block): # -1-
                return False
            previous_proof = previous_block['proof'] # -2-
            proof = block['proof']        
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
        
# Part-2-Mining Our Blockchain

## Creating a web App
app = Flask(__name__) # Flask ile bir web uygulamsı oluşturduk
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False 

## Creating a Blockchain
blockchain = Blockchain() # Nesne oluşturarak blockchain yarattık

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message' : 'Tebrikler,Blok çıkardınız!',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash']}
    return jsonify(response),200 

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
        response = {'chain' : blockchain.chain,
                    'length' : len(blockchain.chain)}
        return jsonify(response),200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200



# Runnuing the app
app.run(host= '0.0.0.0', port = 5000) #yerel sunucuda  5000 portunda çalışıyor












