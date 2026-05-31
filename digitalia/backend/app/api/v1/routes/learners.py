import hashlib
import logging
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.models import Learner
from app.core.lgpd import encrypt_data, decrypt_data, MinorProtection
from app.services.portfolio_generator import generate_portfolio
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Esquemas Pydantic ---
class LearnerCreate(BaseModel):
    phone: str = Field(..., description="Número de telefone (somente números, ex: 5511999999999)")
    first_name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=16, le=30, description="Idade recomendada: 16 a 30 anos")
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    current_trail: Optional[str] = Field(None, max_length=50)
    consent_given: bool = Field(False, description="Consentimento do usuário para uso dos dados")
    parental_consent: Optional[bool] = Field(None, description="Consentimento dos pais (obrigatório se menor de 18)")

class LearnerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=16, le=30)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    current_trail: Optional[str] = Field(None, max_length=50)
    current_state: Optional[str] = Field(None, max_length=50)
    consent_given: Optional[bool] = None
    parental_consent: Optional[bool] = None

class LearnerResponse(BaseModel):
    id: str
    phone: str
    first_name: Optional[str]
    age: Optional[int]
    city: Optional[str]
    state: Optional[str]
    current_trail: Optional[str]
    current_state: str
    level: int
    completed_projects: int
    total_earned_brl: float
    consent_given: bool
    consent_date: Optional[datetime]
    parental_consent: Optional[bool]
    data_retention_until: Optional[object] # Pode ser datetime.date
    created_at: datetime
    last_active_at: datetime

    class Config:
        from_attributes = True

class PortfolioResponse(BaseModel):
    learner_id: str
    file_key: str
    format: str
    s3_url: str
    size_bytes: int

# --- Endpoints ---

@router.post("/", response_model=LearnerResponse, status_code=status.HTTP_201_CREATED)
async def create_learner(payload: LearnerCreate, db: AsyncSession = Depends(get_db)):
    """
    Cria um novo Aprendiz (Learner) garantindo conformidade com a LGPD e criptografia de dados sensíveis.
    """
    phone_sanitized = "".join(filter(str.isdigit, payload.phone))
    phone_hash = hashlib.sha256(phone_sanitized.encode("utf-8")).hexdigest()

    # Verificar duplicidade
    stmt = select(Learner).where(Learner.phone_hash == phone_hash)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aprendiz com este número de telefone já está cadastrado."
        )

    # Validar conformidade de consentimento LGPD para menores de idade
    if payload.age:
        if payload.age < 16 or payload.age > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A idade do jovem deve estar estritamente entre 16 e 30 anos para participação no projeto."
            )
        if MinorProtection.requires_parental_consent(payload.age):
            if not payload.parental_consent or not payload.consent_given:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Para menores de 18 anos, o consentimento do próprio usuário E o consentimento parental são obrigatórios."
                )
        else:
            if not payload.consent_given:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="O consentimento de dados deve ser concedido."
                )

    # Calcular prazos de retenção LGPD
    now_utc = datetime.now(timezone.utc)
    retention_date = MinorProtection.calculate_retention_date(now_utc) if payload.consent_given else None

    # Criptografar dados sensíveis
    phone_encrypted = encrypt_data(phone_sanitized)

    # Instanciar modelo
    new_learner = Learner(
        phone_hash=phone_hash,
        phone_encrypted=phone_encrypted,
        first_name=payload.first_name or "Aprendiz",
        age=payload.age,
        city=payload.city,
        state=payload.state.upper() if payload.state else None,
        current_trail=payload.current_trail,
        current_state="onboarding",
        consent_given=payload.consent_given,
        consent_date=now_utc if payload.consent_given else None,
        parental_consent=payload.parental_consent,
        data_retention_until=retention_date,
        level=1,
        completed_projects=0,
        total_earned_brl=0.00
    )

    db.add(new_learner)
    await db.flush() # Gerar ID do banco
    
    # Montar resposta decodificada para exibição
    response_data = new_learner.__dict__.copy()
    response_data["id"] = str(new_learner.id)
    response_data["phone"] = phone_sanitized
    
    return response_data

@router.get("/", response_model=List[LearnerResponse])
async def list_learners(db: AsyncSession = Depends(get_db)):
    """
    Lista todos os Aprendizes cadastrados, descriptografando seus números de telefone de forma segura.
    """
    stmt = select(Learner)
    result = await db.execute(stmt)
    learners = result.scalars().all()

    response_list = []
    for l in learners:
        phone_decrypted = decrypt_data(l.phone_encrypted)
        data = l.__dict__.copy()
        data["id"] = str(l.id)
        data["phone"] = phone_decrypted
        response_list.append(data)
        
    return response_list

@router.get("/{learner_id}", response_model=LearnerResponse)
async def get_learner(learner_id: str, db: AsyncSession = Depends(get_db)):
    """
    Exibe os detalhes de um Aprendiz específico.
    """
    try:
        stmt = select(Learner).where(Learner.id == learner_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de ID inválido.")
        
    result = await db.execute(stmt)
    learner = result.scalars().first()
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aprendiz não encontrado.")

    phone_decrypted = decrypt_data(learner.phone_encrypted)
    data = learner.__dict__.copy()
    data["id"] = str(learner.id)
    data["phone"] = phone_decrypted
    return data

@router.put("/{learner_id}", response_model=LearnerResponse)
async def update_learner(learner_id: str, payload: LearnerUpdate, db: AsyncSession = Depends(get_db)):
    """
    Atualiza as informações cadastrais de um Aprendiz.
    """
    try:
        stmt = select(Learner).where(Learner.id == learner_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de ID inválido.")

    result = await db.execute(stmt)
    learner = result.scalars().first()
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aprendiz não encontrado.")

    # Atualizar campos se fornecidos
    if payload.first_name is not None:
        learner.first_name = payload.first_name
    if payload.age is not None:
        if payload.age < 16 or payload.age > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A idade do jovem deve estar estritamente entre 16 e 30 anos para participação no projeto."
            )
        learner.age = payload.age
    if payload.city is not None:
        learner.city = payload.city
    if payload.state is not None:
        learner.state = payload.state.upper()
    if payload.current_trail is not None:
        learner.current_trail = payload.current_trail
    if payload.current_state is not None:
        learner.current_state = payload.current_state

    # Se mudar consentimento, recalcula prazos de retenção LGPD
    if payload.consent_given is not None:
        learner.consent_given = payload.consent_given
        if payload.consent_given:
            now_utc = datetime.now(timezone.utc)
            learner.consent_date = now_utc
            learner.data_retention_until = MinorProtection.calculate_retention_date(now_utc)
        else:
            learner.consent_date = None
            learner.data_retention_until = None

    if payload.parental_consent is not None:
        learner.parental_consent = payload.parental_consent

    # Verificar se as novas configurações permanecem conformes com menor de idade
    if learner.age and MinorProtection.requires_parental_consent(learner.age):
        if not learner.consent_given or not learner.parental_consent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inconsistência LGPD: Menor de idade exige consentimento do próprio usuário e consentimento dos pais."
            )

    await db.flush()
    
    phone_decrypted = decrypt_data(learner.phone_encrypted)
    data = learner.__dict__.copy()
    data["id"] = str(learner.id)
    data["phone"] = phone_decrypted
    return data

@router.delete("/{learner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_learner(learner_id: str, db: AsyncSession = Depends(get_db)):
    """
    Remove fisicamente os dados de um Aprendiz sob demanda.
    """
    try:
        stmt = select(Learner).where(Learner.id == learner_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de ID inválido.")

    result = await db.execute(stmt)
    learner = result.scalars().first()
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aprendiz não encontrado.")

    await db.delete(learner)
    await db.flush()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/{learner_id}/portfolio", response_model=PortfolioResponse)
async def generate_learner_portfolio(learner_id: str, format_type: str = "pdf", db: AsyncSession = Depends(get_db)):
    """
    Gera o portfólio mock do aprendiz e faz o upload para o LocalStack S3, retornando a URL gerada.
    """
    try:
        stmt = select(Learner).where(Learner.id == learner_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de ID inválido.")

    result = await db.execute(stmt)
    learner = result.scalars().first()
    if not learner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aprendiz não encontrado.")

    if format_type not in ["pdf", "image", "png"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato não suportado. Use 'pdf' ou 'image'.")

    try:
        portfolio_info = await generate_portfolio(str(learner.id), format_type=format_type)
        return portfolio_info
    except Exception as e:
        logger.error(f"Erro ao gerar portfólio no S3 para aprendiz {learner_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno de integração com LocalStack S3: {str(e)}")
