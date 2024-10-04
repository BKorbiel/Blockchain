from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature, encode_dss_signature
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend

class Wallet:
    def __init__(self, private_key=None, public_key=None):
        if private_key and public_key:
            self.private_key = self.load_private_key(private_key)
            self.public_key = self.load_public_key(public_key)
            return

        # Generating ECDSA keys
        self.private_key = ec.generate_private_key(ec.SECP256K1())
        self.public_key = self.private_key.public_key()
        print(f"Generated new keys. Please store them safely")
        print(f"Public key: {self.get_public_key().decode('utf-8')}")
        print(f"Private key: {self.get_private_key().decode('utf-8')}")

    def sign_transaction(self, transaction_data):
        signature = self.private_key.sign(transaction_data.encode('utf-8'), ec.ECDSA(hashes.SHA256()))
        return signature

    def get_public_key(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def get_private_key(self):
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    def load_private_key(self, private_key_str):
        return serialization.load_pem_private_key(
            private_key_str.encode('utf-8'),
            password=None,
            backend=default_backend()
        )

    def load_public_key(self, public_key_str):
        return serialization.load_pem_public_key(
            public_key_str.encode('utf-8'),
            backend=default_backend()
        )

    @staticmethod
    def verify_signature(public_key_bytes, transaction_data, signature):
        public_key = serialization.load_pem_public_key(public_key_bytes)
        try:
            public_key.verify(signature, transaction_data.encode('utf-8'), ec.ECDSA(hashes.SHA256()))
            return True
        except InvalidSignature:
            return False
