import base64
import json
import secrets
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_DH_PRIME = int(
    'FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1'
    '29024E088A67CC74020BBEA63B139B22514A08798E3404DD'
    'EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245'
    'E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED'
    'EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D'
    'C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F'
    '83655D23DCA3AD961C62F356208552BB9ED529077096966D'
    '670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B'
    'E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9'
    'DE2BCBF6955817183995497CEA956AE515D2261898FA0510'
    '15728E5A8AACAA68FFFFFFFFFFFFFFFF', 16
)
_DH_GENERATOR = 2


def dh_generate_keypair() -> tuple:
    private_key = secrets.randbelow(_DH_PRIME - 2) + 2
    public_key = pow(_DH_GENERATOR, private_key, _DH_PRIME)
    return private_key, public_key


def dh_derive_key(private_key: int, peer_public_key: int) -> bytes:
    shared_secret = pow(peer_public_key, private_key, _DH_PRIME)
    shared_secret_bytes = shared_secret.to_bytes(256, byteorder='big')
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'nexus-encryption-key',
    )
    return hkdf.derive(shared_secret_bytes)

def dh_encode_public_key(public_key: int) -> str:
    return base64.b64encode(public_key.to_bytes(256, byteorder='big')).decode('ascii')

def dh_decode_public_key(b64: str) -> int:
    return int.from_bytes(base64.b64decode(b64), byteorder='big')

def dh_make_init_message(public_key: int) -> str:
    return json.dumps({"_n": "dh_init", "pub": dh_encode_public_key(public_key)})

def dh_make_resp_message(public_key: int) -> str:
    return json.dumps({"_n": "dh_resp", "pub": dh_encode_public_key(public_key)})

def dh_is_handshake_message(message: str) -> bool:
    return isinstance(message, str) and message.startswith('{"_n":')


# ------------------------------------------------------------------
# AES-256-GCM encryption / decryption
# ------------------------------------------------------------------

_NONCE_SIZE = 12  

def encrypt_message(key: bytes, plaintext: str) -> str:
    nonce = secrets.token_bytes(_NONCE_SIZE)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode('utf-8'), None)
    payload = base64.b64encode(nonce + ciphertext).decode('ascii')
    return json.dumps({"_e": payload})


def decrypt_message(key: bytes, raw: str) -> str:
    try:
        data = json.loads(raw)
        nonce_ct = base64.b64decode(data["_e"])
        nonce, ciphertext = nonce_ct[:_NONCE_SIZE], nonce_ct[_NONCE_SIZE:]
        return AESGCM(key).decrypt(nonce, ciphertext, None).decode('utf-8')
    except Exception as exc:
        raise ValueError(f"Decryption failed: {exc}") from exc


def is_encrypted_message(message: str) -> bool:
    return isinstance(message, str) and message.startswith('{"_e":')
