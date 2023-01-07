# Module-1-Create a Cryptocurrency

# Importing the libraries
import datetime
# her blok zaman damgasına sahip olacaktır
import hashlib
# verilerin özet fonksiyonu kullanılarak şifrelenmesi
import json
# Blokları kodlamak için bu kütüphanedeki dumps fonksiyonlarını kullanacağız
from flask import Flask, jsonify ,request
# request merkezi olmayan blok zinciri ağımızdaki bazı düğümleri birbirine bağlayacktır.ayrıca ağdaki düğümlerde bulunan zincirleri tarayıp en uzun olanı alacakatır
import requests
# Ağdaki her düğüm için bir adres oluşturmak ve bu düğümlerin her birinin URL'sini duraklatmak için UUID ve URL ayrıştırma işlevlerdir.
from uuid import uuid4
from urllib.parse import urlparse
# Flask sınıfının nesnesi bizim web uygulamamız olacaktır.
# jsonify,blok zincirimizle etkileşime girdiğimizde postman'daki mesajları döndürmek için kullanacağımzı bir işlevdir.

# Part-1-Building a Blockchain
# Burada daha çok kripto para işlevi kazandırılacaktır
# Bir blockchain'i kriptopara'ya çevirmek
# bir blockchaini kripto para yapan nedir?=işlemler yapılabiliyor olmasıdır.

# İlk aşamada blockchaine işlemleri ekleyceğiz ve ondan sonraki aşamada merkezi olmayan ağda bulunan her düğümde aynı blockchain var mı diye mutabakat protokolleri kullanacağız.
# oluşturulan blokzincire işlem ekleme ve fikir birliği sağlama ile kriptopara oluşturulur

# işlemler blok çıkartıldıktan sonra bloğa eklenirler
# işlemler bloğa eklendikten sonra aynı işlemler bir daha eklenmesin diye liste boşaltılmalı ve yeni işlemler için hazır olmalıdır.
 

#sadece tüm düğümlerin herhangi bir zamanda aynı zinciri içerdiğinden emin olmak için kullanılan algoritmalra fikir birliği algoritması yani consensüs algoritması denir
#dolayısıyla herhangi bir düğümde yeni bir blok çıkarıldığında, o düğüm etrafında gerçekleşen bazı yeni işlemleri karşılmak için,merkezi olmayan ağdaki diğer tüm düğümlerin de aynı zincirle güncellendiğinden emin olmalıyız
#Blockchainin temel prensibi de budur vazgeçilmezdir


class Blockchain: # Blockchain classı

    # Constructor ## Self sınıf içierisinde metotlara,parametrelere ulaşmak için kullanılır.
    def __init__(self): # İlklendirilmiş fonksiyon
    
        self.chain = []  # Blokları içeren zincir
        self.transactions = [] # işlemeler bloğa eklenmden önce onları bir yerde tutmamız lazım,işlemler blok içinde doğmazlar sonradan eklenirler
        self.create_block(proof = 1, previous_hash = '0')  # Genesis block
        self.nodes = set()  # Düğümleri yani merkeziyetsiz ağın kullanıcılarını ekliyoruz ve argüman olarak da bir düğümün adreslerinin olması gerekiyor.düğümleri liste olarak tutamayız çunkü düğümlerin bir sırası yok 
        

    def create_block(self, proof, previous_hash):  # Blok Oluşturma
        block = {'index': len(self.chain) + 1, # Kaçıncı zincir
                 'timestamp': str(datetime.datetime.now()), # Tarih-zaman damgası
                 'proof': proof, # İş kanıtı.Yani proof_of_work fonksiyonundan elde edilen sayı
                 'previous_hash': previous_hash, # Bir önceki hash
                 'transactions': self.transactions} # Listedeki yapılan işlemleri gösterecek
        self.transactions = [] #Listeyi boşalttık
        self.chain.append(block)  # Bloğu zincire ekleme
        return block  # Postmanda bloğun döndürülmesi

    # Herhangi bir anda uğraştığımız mevcut zincirin son bloğunu almak için kullanılacak
    def get_previous_block(self):
        return self.chain[-1] # Son bloğu döndürüyoruz pythonda son böyledir
    
    # Çözmesi zor doğrulaması kolay bir problem iş kanıtı ile sağlanacak 
    def proof_of_work(self, previous_proof): # İş kanıtı Fonksiyonu.oluşturulacak nesne uygulayacak.Önceki kanıt madencilerin yeni kanıtı bulmak için dikkate almaları gerekir
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
            if hash_operation[:4] != '0000': #ilk dört karakterin sıfıra eşit olma durumu
                return False
            previous_block = block
            block_index += 1
        return True
# buradaki işlem listesi bloğa eklenmemiş işlemlerdir   
    def add_transaction(self, sender, receiver, amount): # İşlemlerin kaydının tutulduğu bir işlev ex:gönderici,alıcı,miktar
        self.transactions.append({'sender': sender, # Gönderici
                                  'receiver': receiver, # Alıcı
                                  'amount': amount}) # Miktar,
        previous_block = self.get_previous_block() # Son bloğu aldık
        return previous_block['index'] + 1 # İşlemler zincirimizin son bloğuna değil de oluşturulacak bloğa eğer ki blok çıkarıldıysa eklenecektir
        
    def add_node(self, adress): #Düğümün kendisini ve adresini tuatacaktır.
        parsed_url =urlparse(adress) # url parse ile adresin url'i ayrıştırldı
        self.nodes.add(parsed_url.netloc) # ayrıştırılan adres düğüm adresleri adındaki kümeye eklendi
     
#Ağın tüm düğümleri arasında en uzun zincirden daha kısa olan herhangi bir zinciri değiştirecek olan bu zincir değiştirme yöntemini oluşturarak fikir birliğii sorununu ele alacağız
#sadce bazı yeni düğümler eklenekle kalmayıp onları birbirine bağlamak ve daha sonra elbette herhangi bir düğümde yeni bir blok çıkarıldığında fikir birliğini uygulamak için talepte bulunduğumuzda merkeziyetsizleştirme işlemi tamamlanacktır
 
# replace_chain fonksiyonunun işleevi merkezi olmayan ağımızdaki tüm düğümlere bakmak olacaktır,bu düğümlerin her birinin zincirini kontrol edecek ardından en uzun zinciri tespit edecektir.
# ve temel olarak en uzun zincirden daha kısa bir zincir içeren herhangi bir düğümde bu zinciri en uzun olanla değiştirecektir
       
    def replace_chain(self): #fikir birliği oluşturmak için oluşturulan fonksiyon,tek parametre almasının nedeni bu fonksiyonu belirli düğümlerde cağıracak olmamızdır. her düğüm blok zincirinin belirli bir sürümünü içerdiğinden güncel olsun ya da olmasın bu zinciri değiştirme işlevini belirli bir düğümün içerisinde uygulamamız lazım.
        network = self.nodes # tüm düğümleri içeren networkümüz dolayısıyla bu bizim düğüm kümemizi alacaktır.
        longest_chain = None # şimdilik en uzun zincirimiz belli değildir lakin ağda tarama yapıp en uzun zinciri bulup bu değişkene atayacağız.
        max_length = len(self.chain) #Şimdilik elimizdeki ugraştığımız zincirin uzunluğu atandı ancak en uzun zincirin uzunluğu alınınca onu değişkene atayacağız.
        for node in network: # Ağın düğümleri üzerinde yineleme yapmak istediğimizden bir for döngüsü kullandık
            response = requests.get(f'http://{node}/get_chain') # her ağdaki düğümlerin port numarasını aldık
            if response.status_code==200:# Http kodu ile her şeyin yolunda olup olmadığı lontrol edildi.
                length=response.json()["length" ] # response'dan chain'in uzunluğu alındı
                chain=response.json()["chain"] # en uzun zincir olup olmama durumuna karşı zincir de alındı.
                if length > max_length and self.is_chain_valid(chain): # Cevaptan gelen uzunluk normal uğraştığımız zincirin uzunluğundan fazla ve blockchain geçerli  ise işlemler yapılacak
                    max_length = length # En uzun zincirin uzunluğunu  aldık
                    longest_chain=chain # en uzun zinciri aldık ki düğümdekilerle değiştirebilelim
                    
        if longest_chain: #en uzun zincir zaten yukarıda güncellenmemişse durumu
            self.chain = longest_chain #kendi düğümümüzdeki chain güncellendi
            return True
        return False #değişiklik olmamışsa en uzun zincir bizim zincirimizdir.

# Part-2-Mining Our Blockchain

# Kripto paranın birkaç kişi arasında yapılan işlemlerin bloklara eklenmesi için temel atılacaktır.
# Yapılan işlemlerin fikir birliği algoritmaları kullanırlarak bloklara eklenmesi gereklidir.
## Creating a web App
app = Flask(__name__) # Flask ile bir web uygulamsı oluşturduk
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False                


#Creating an adress for the node on Port
#Her düğüm için farklı bağlantı noktası gerekli 
node_adress = str(uuid4()).replace('-', '') # Düğüm adresleri için uuı'ten faydalandık fakat düğüm adresinde "-" özel karakteri bulunmamalıdır
# Niçin adres oluşturuldu çünkü madenci olarak bir blok çıkardığında bir miktar para kazanması gerekir 

## Creating a Blockchain
blockchain = Blockchain() # Nesne oluşturarak blockchain yarattık

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_adress,receiver='5001 Port Sahibi', amount=1000) # İşlem eklendi bu olay çeşitli fonksiyonlar eklnerek blockchainde tetiklenebilir ve blockchaine işlevsellik katabilir tabi burada minin yapıldığı için işlem eklendi  yani ödül verildi
    block = blockchain.create_block(proof, previous_hash)
    response = {'message' : 'Tebrikler,Blok çıkardınız!',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash'],
                'transactions': block['transactions']} #Normal bir blockchain'i cryptocurrency'e dönüştürürken transactions'ları eklemek gerekli 
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
        response = {'message': 'Zincir geçerli.'}
    else:
        response = {'message': 'Geçersiz zincir.'}
    return jsonify(response), 200

# İşlemler listesinde biriken işlemleri içeren key-value değeri olacaktır
# Yeni bir işlem eklemek için talepte bulunmamız gerekecektir bunu da POST metodu ile yapacağız

# Adding a new transaction to the Blockchain 
# BLockchain' işlem ekleme POST yöntemi kullanarak olur
# POST isetği yanıt almak için bir şey yaratılmasını gerektirir.
@app.route('/add_transaction', methods = ['POST']) #işlemin hangi bloğa eklendiğini de gösterecektir
def add_transaction():
    json = request.get_json(cache=False) # isteğin json formatına dönüştürülmesi ve bu isteğin postman'da çağırılması için json formatına ihtiyaç duyuldu
    transaction_keys = ['sender', 'receiver', 'amount'] #İşlem anahtarları kim yaptı,kime hangi işlem ,tutar
    if not all(key in json for key in transaction_keys): # işlem anahtarları listesindeki tüm anahtarlar json dosyamızda yoksa
        return 'Some elements of the transaction are missing', 400 # http hata kodu ile mesaj verildi
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount']) #işlem tamam ise hata yoksa işlem kazılacak yani mining edilecek olan bloğa eklenecek.yapılan işlemelr json formatında gönderildiği için işlemler kazılacak olan bloğa eklenince json üzerinden eklendi ayrıca hangi bloğa ekleneceği yukarıda add_transaction fonskiyonunda belirlenmiş bir indexe sahip blok olan kazılacak blok seçildi
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201 # İşlem başarılı döndürüldü hata yok mesajı eklendi hata mesajı da json formatında olmalı ki postman da gözüksün



# Part-3-Decentralizing  our Blockchain

# BLok zincirimiz merkezisizleştirilmeli ve bazı yeni düğümleri merkezisizleştirilmiş blok zinciirine bağlanmıs olması gerekli  
# ve bu nedenle birkaç düğümümüz olacağından ağdaki  bazı düğümlerin en güncel blok  zincirine sahip olmaması durumunda fikir birliği uygulamak için bir get isteği olmalı 
# merkezi olmayan ağdaki herhangi bir yeni düğümü bağlamak için bir istek oluştuturulmalı
# en güncel blok zincirini içermeyen herhangi bir düğümde zinciri değiştiren fikir birliğinin uygulanmalı

# Connecting new nodes

@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json(cache=False) # İstediğmiz tüm düğümleri ve adreslerini içerem json dosyasını request kütüphanesinin işlevi kullanılarak alınması için istek gönderildi
    nodes = json.get('nodes') # json.get() metodu ile listede yer alan duğümlerin adreslerini aldık
    if nodes is None: # Düğümlerin olup olmadığını kontrol ediyoruz
        return "No node",400
    for node in nodes: # düğülerin adresleri üzerinde döngü kullanılarak adreslerin brirbirine bağlanması 
        blockchain.add_node(node) # Ekleme için düğüm ekle fonksiyonu kullanıldı
    response = {'message': 'Tüm düğümler zincire bağlandı.', 
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response),201

# Zincirin merkeziyetsizleştirlmesi için 3 düğümden oluşan bir ağ kurulması ile birlikte herhangi birinde mining yapılıp blok çıkarılabilinecektir.

# Zincirin en güncel zincirle değiştirilmesi

@app.route('/replace_chain', methods = ['GET'])
def replace_chain(): # zincirin geçerli olup olmadığını kontrol eden fonksiyona benzer olacak şekilde zinciri güncelleme işlemi yapan method
    is_chain_replaced = blockchain.replace_chain() # en uzun zincir alınıp bir boolean değer elde edildi
    if is_chain_replaced: # elde edilen booleana göre hangi zincirin geçerli zincir olması gerektiğine karar verildi
        response = {'message': 'Düğümlerdeki zincirler farlı olduğundan geçerli olanla değiştirildi.',
                    'new_chain': blockchain.chain }
    else:
        response = {'message': 'En uzun zincire sahip düğüm sizsiniz.',
                    'actual_chain': blockchain.chain }
    return jsonify(response), 200



# Runnuing the app
app.run(host= '0.0.0.0', port = 5001)  # port numarası verilerek işlemlerin farklı düğümlerde de gözükmesi yani merkeziyetsizleştirimesi gerekir 



















