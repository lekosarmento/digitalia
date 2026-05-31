import hashlib
import logging
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.models import Company
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# --- Esquemas Pydantic ---
class CompanyCreate(BaseModel):
    company_name: str = Field(..., max_length=200, description="Nome da PME / Empresa")
    cnpj: Optional[str] = Field(None, max_length=14, description="CNPJ (apenas números)")
    contact_name: Optional[str] = Field(None, max_length=200, description="Nome do contato principal")
    email: Optional[str] = Field(None, max_length=200, description="Email de contato")
    phone: Optional[str] = Field(None, description="Telefone de contato (somente números)")
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)

class CompanyUpdate(BaseModel):
    company_name: Optional[str] = Field(None, max_length=200)
    cnpj: Optional[str] = Field(None, max_length=14)
    contact_name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=2)
    is_verified: Optional[bool] = None

class CompanyResponse(BaseModel):
    id: str
    company_name: str
    cnpj: Optional[str]
    contact_name: Optional[str]
    email: Optional[str]
    city: Optional[str]
    state: Optional[str]
    avg_rating: Optional[float]
    total_projects: int
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Endpoints ---

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(payload: CompanyCreate, db: AsyncSession = Depends(get_db)):
    """
    Cria uma nova PME (Company).
    """
    # Validar unicidade do email se fornecido
    if payload.email:
        stmt = select(Company).where(Company.email == payload.email)
        result = await db.execute(stmt)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empresa com este e-mail já está cadastrada."
            )

    # Calcular o hash do telefone se fornecido
    phone_hash = None
    if payload.phone:
        phone_sanitized = "".join(filter(str.isdigit, payload.phone))
        phone_hash = hashlib.sha256(phone_sanitized.encode("utf-8")).hexdigest()

    new_company = Company(
        company_name=payload.company_name,
        cnpj=payload.cnpj,
        contact_name=payload.contact_name,
        email=payload.email,
        phone_hash=phone_hash,
        city=payload.city,
        state=payload.state.upper() if payload.state else None,
        total_projects=0,
        is_verified=False
    )

    db.add(new_company)
    await db.flush() # Gerar ID do banco
    
    response_data = new_company.__dict__.copy()
    response_data["id"] = str(new_company.id)
    return response_data

@router.get("/", response_model=List[CompanyResponse])
async def list_companies(db: AsyncSession = Depends(get_db)):
    """
    Lista todas as PMEs cadastradas.
    """
    stmt = select(Company)
    result = await db.execute(stmt)
    companies = result.scalars().all()
    
    response_list = []
    for c in companies:
        data = c.__dict__.copy()
        data["id"] = str(c.id)
        response_list.append(data)
        
    return response_list

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: str, db: AsyncSession = Depends(get_db)):
    """
    Exibe detalhes de uma PME específica.
    """
    try:
        stmt = select(Company).where(Company.id == company_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de ID inválido.")
        
    result = await db.execute(stmt)
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada.")

    data = company.__dict__.copy()
    data["id"] = str(company.id)
    return data

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(company_id: str, payload: CompanyUpdate, db: AsyncSession = Depends(get_db)):
    """
    Atualiza as informações de uma PME.
    """
    try:
        stmt = select(Company).where(Company.id == company_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de ID inválido.")

    result = await db.execute(stmt)
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada.")

    # Atualizar campos se fornecidos
    if payload.company_name is not None:
        company.company_name = payload.company_name
    if payload.cnpj is not None:
        company.cnpj = payload.cnpj
    if payload.contact_name is not None:
        company.contact_name = payload.contact_name
    if payload.city is not None:
        company.city = payload.city
    if payload.state is not None:
        company.state = payload.state.upper()
    if payload.is_verified is not None:
        company.is_verified = payload.is_verified

    # Validar unicidade do email se alterado
    if payload.email is not None and payload.email != company.email:
        stmt = select(Company).where(Company.email == payload.email)
        res_email = await db.execute(stmt)
        if res_email.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Outra empresa já utiliza este e-mail."
            )
        company.email = payload.email

    # Atualizar hash de telefone se fornecido
    if payload.phone is not None:
        phone_sanitized = "".join(filter(str.isdigit, payload.phone))
        company.phone_hash = hashlib.sha256(phone_sanitized.encode("utf-8")).hexdigest()

    await db.flush()
    
    data = company.__dict__.copy()
    data["id"] = str(company.id)
    return data

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: str, db: AsyncSession = Depends(get_db)):
    """
    Remove uma PME do sistema.
    """
    try:
        stmt = select(Company).where(Company.id == company_id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de ID inválido.")

    result = await db.execute(stmt)
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada.")

    await db.delete(company)
    await db.flush()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
