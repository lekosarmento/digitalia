import os
import hashlib
import datetime
from typing import Optional, List
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configurações JWT obtidas de variáveis de ambiente
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "CRÍTICO: A variável de ambiente JWT_SECRET_KEY não está definida. "
        "Defina-a no arquivo .env antes de iniciar a aplicação. "
        "Use: python -c \"import secrets; print(secrets.token_hex(32))\""
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas por padrão para persistência mobile

security_scheme = HTTPBearer()

def get_password_hash(password: str) -> str:
    """
    Gera um hash PBKDF2-HMAC-SHA256 seguro para a senha com um salt de 16 bytes.
    Retorna o hash no formato salt_hex:hash_hex para armazenamento seguro e compatibilidade instantânea.
    """
    if not password:
        raise ValueError("A senha não pode estar vazia.")
    salt = os.urandom(16)
    db_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return f"{salt.hex()}:{db_hash.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto claro fornecida coincide com o hash PBKDF2 armazenado.
    """
    if not plain_password or not hashed_password:
        return False
    try:
        salt_hex, hash_hex = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        actual_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, 100000)
        return actual_hash == expected_hash
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """
    Gera um token JWT contendo os claims passados e a expiração calculada.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decodifica e valida o token JWT. Lança JWTError se o token for inválido ou expirado.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

class RoleChecker:
    """
    Dependência reutilizável para o FastAPI que atua no controle de acesso baseado em Roles (RBAC).
    Permite filtrar acessos para os claims customizados: 'learner', 'company', 'mentor', 'admin'.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> dict:
        token = credentials.credentials
        try:
            payload = decode_access_token(token)
            role = payload.get("role")
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token não possui a claim de 'role' configurada."
                )
            if role not in self.allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acesso negado. Essa operação requer uma das seguintes credenciais: {', '.join(self.allowed_roles)}"
                )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acesso inválido ou expirado."
            )

# Dependências de Roles pré-definidas para facilidade de importação nas rotas
allow_learner = RoleChecker(["learner", "admin"])
allow_company = RoleChecker(["company", "admin"])
allow_mentor = RoleChecker(["mentor", "admin"])
allow_admin = RoleChecker(["admin"])
