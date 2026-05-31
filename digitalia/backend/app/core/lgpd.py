import os
import base64
import datetime
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Chave deve ter exatamente 32 bytes (256 bits) para AES-256
ENCRYPTION_KEY_STR = os.getenv("LGPD_ENCRYPTION_KEY", "digitalia_secure_key_32bytes_long!")
if len(ENCRYPTION_KEY_STR.encode()) < 32:
    import hashlib
    ENCRYPTION_KEY = hashlib.sha256(ENCRYPTION_KEY_STR.encode()).digest()
else:
    ENCRYPTION_KEY = ENCRYPTION_KEY_STR.encode()[:32]

def encrypt_data(data: str) -> bytes:
    """
    Criptografa uma string usando AES-256-GCM e retorna os bytes do ciphertext contendo o nonce acoplado.
    Utilizado para proteger dados sensíveis de usuários (PII) antes de persistir no PostgreSQL.
    """
    if not data:
        return b""
    aesgcm = AESGCM(ENCRYPTION_KEY)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data.encode("utf-8"), None)
    return nonce + ciphertext

def decrypt_data(encrypted_data: bytes) -> str:
    """
    Descriptografa bytes criptografados usando AES-256-GCM (extraindo o nonce dos primeiros 12 bytes)
    e retorna a string original em texto claro.
    """
    if not encrypted_data:
        return ""
    if len(encrypted_data) < 12:
        raise ValueError("Dados criptografados inválidos ou corrompidos.")
    aesgcm = AESGCM(ENCRYPTION_KEY)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
    return decrypted.decode("utf-8")

class MinorProtection:
    """
    Implementação síncrona de proteção para menores de 18 anos no DigitalIA.
    Garante conformidade estrita com o Artigo 14 da LGPD (Tratamento de dados de crianças e adolescentes).
    """

    @staticmethod
    def requires_parental_consent(age: int) -> bool:
        """
        Retorna True se o usuário tiver menos de 18 anos, necessitando de consentimento parental.
        O DigitalIA atende jovens a partir de 16 anos.
        """
        return age < 18

    @staticmethod
    def is_compliant(age: int, consent_given: bool, parental_consent: Optional[bool]) -> bool:
        """
        Verifica se a gravação de dados está em conformidade com as regras de consentimento da LGPD:
        - Para menores de 18 anos: requer consentimento do usuário E consentimento parental explícito.
        - Para maiores de 18 anos: requer apenas consentimento explícito do próprio usuário.
        """
        if age < 18:
            return bool(consent_given and parental_consent)
        return bool(consent_given)

    @staticmethod
    def calculate_retention_date(consent_date_val: datetime.datetime) -> datetime.date:
        """
        Define o ciclo de retenção dos dados conforme política de privacidade do DigitalIA.
        Dados são retidos por 2 anos (730 dias) após a concessão de consentimento.
        """
        return (consent_date_val + datetime.timedelta(days=730)).date()
