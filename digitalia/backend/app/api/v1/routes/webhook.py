import os
import hmac
import hashlib
import logging
from typing import Optional
from fastapi import APIRouter, Request, Header, HTTPException, Query, Depends, status
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.database import get_db
from app.models.models import Learner, Conversation
from app.core.lgpd import encrypt_data
from app.services.whisper_service import transcribe_audio

logger = logging.getLogger(__name__)
router = APIRouter()

WA_APP_SECRET = os.getenv("WA_APP_SECRET", "digitalia_app_secret_placeholder")
WA_VERIFY_TOKEN = os.getenv("WA_VERIFY_TOKEN", "digitalia_verify_token_default")
WA_ACCESS_TOKEN = os.getenv("WA_ACCESS_TOKEN", "")

# Modelo Pydantic para o contrato de dados simplificado (interoperabilidade com Agente 3)
class WebhookPayload(BaseModel):
    phone: str = Field(..., description="Número de telefone do aprendiz (somente dígitos)")
    message_type: str = Field(..., description="Tipo da mensagem: text, audio ou image")
    content: str = Field("", description="Conteúdo textual da mensagem (ou texto transcrito)")
    media_url: Optional[str] = Field(None, description="URL da mídia de áudio/imagem")

def verify_hmac_signature(payload: bytes, signature_header: str) -> bool:
    """
    Valida a assinatura HMAC SHA-256 enviada pela Meta Cloud API.
    """
    if not signature_header:
        return False
    
    # O cabeçalho vem no formato: sha256=hash_hexadecimal
    if signature_header.startswith("sha256="):
        signature = signature_header.split("sha256=")[1]
    else:
        signature = signature_header
        
    expected_signature = hmac.new(
        WA_APP_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

async def get_whatsapp_media_url(media_id: str) -> str:
    """
    Busca a URL de download da mídia usando a Meta Graph API.
    """
    if not WA_ACCESS_TOKEN:
        logger.warning("WA_ACCESS_TOKEN não está configurado. Não é possível consultar a Graph API.")
        return ""
    
    url = f"https://graph.facebook.com/v18.0/{media_id}"
    headers = {"Authorization": f"Bearer {WA_ACCESS_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("url", "")
            else:
                logger.error(f"Erro na Graph API ao consultar mídia {media_id}. Status: {response.status_code}, Detalhes: {response.text}")
                return ""
        except Exception as e:
            logger.error(f"Exceção ao consultar Graph API para mídia {media_id}: {str(e)}")
            return ""

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """
    Validação de token da Meta Cloud API (GET handshake).
    """
    if hub_mode == "subscribe" and hub_verify_token == WA_VERIFY_TOKEN:
        logger.info("Webhook verificado com sucesso pelo handshake do WhatsApp.")
        return Response(content=hub_challenge, media_type="text/plain")
    logger.warning("Falha na verificação do handshake do WhatsApp.")
    return Response(content="Verification failed", status_code=403)

@router.post("/webhook")
async def receive_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None, alias="x-hub-signature-256"),
    db: AsyncSession = Depends(get_db)
):
    """
    Recebe eventos do WhatsApp Cloud API (Meta) ou JSON direto no formato do contrato de dados.
    """
    body_bytes = await request.body()
    
    # 1. Se contiver a assinatura X-Hub-Signature-256, tratamos como payload da Meta
    if x_hub_signature_256:
        if not verify_hmac_signature(body_bytes, x_hub_signature_256):
            logger.warning("Assinatura HMAC inválida para evento da Meta.")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")
        
        try:
            payload_json = await request.json()
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body")
        
        return await process_meta_payload(payload_json, db)
        
    # 2. Caso contrário, assumimos que é uma requisição simplificada seguindo o contrato
    else:
        try:
            payload_json = await request.json()
            payload = WebhookPayload(**payload_json)
        except Exception as e:
            logger.error(f"Erro ao decodificar JSON do contrato simplificado: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Corpo da requisição inválido para o contrato de dados.")
        
        return await process_simplified_payload(payload, db)

async def process_meta_payload(payload: dict, db: AsyncSession) -> JSONResponse:
    """
    Processa o payload oficial estruturado da WhatsApp Cloud API da Meta.
    """
    try:
        # Navegar pela estrutura aninhada da Meta
        entry = payload.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})
        
        if "messages" not in value:
            # Pode ser uma notificação de status de entrega (sent, delivered, read), apenas retornamos 200
            return JSONResponse(content={"status": "ignored_event"}, status_code=200)
            
        message = value.get("messages", [])[0]
        contact = value.get("contacts", [])[0]
        
        phone = message.get("from")  # Telefone do remetente
        message_id = message.get("id")
        msg_type = message.get("type")
        
        phone_sanitized = "".join(filter(str.isdigit, phone))
        content = ""
        media_url = None
        
        if msg_type == "text":
            content = message.get("text", {}).get("body", "")
        elif msg_type == "audio":
            media_id = message.get("audio", {}).get("id")
            media_url = await get_whatsapp_media_url(media_id)
            if media_url:
                content = await transcribe_audio(media_url)
            else:
                content = "[Áudio indisponível - falha ao obter URL de mídia]"
        elif msg_type == "image":
            media_id = message.get("image", {}).get("id")
            media_url = await get_whatsapp_media_url(media_id)
            content = "[Mensagem de Imagem recebida]"
        else:
            content = f"[Mensagem de tipo não suportado: {msg_type}]"
            
        # Salva ou atualiza o aprendiz e a conversa
        await save_conversation_data(
            phone=phone_sanitized,
            message_type=msg_type if msg_type in ["text", "audio", "image"] else "text",
            content=content,
            media_url=media_url,
            wa_message_id=message_id,
            first_name=contact.get("profile", {}).get("name"),
            db=db
        )
        
        return JSONResponse(
            content={
                "phone": phone_sanitized,
                "message_type": msg_type if msg_type in ["text", "audio", "image"] else "text",
                "content": content,
                "media_url": media_url
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Erro ao processar payload da Meta: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar evento da Meta: {str(e)}")

async def process_simplified_payload(payload: WebhookPayload, db: AsyncSession) -> JSONResponse:
    """
    Processa o payload simplificado estruturado seguindo o contrato de dados fixo.
    """
    phone_sanitized = "".join(filter(str.isdigit, payload.phone))
    content = payload.content
    
    # Se for mensagem do tipo audio e não tiver conteúdo transcrito, mas tiver media_url, realiza transcrição
    if payload.message_type == "audio" and not content and payload.media_url:
        try:
            content = await transcribe_audio(payload.media_url)
        except Exception as e:
            logger.error(f"Erro ao transcrever áudio do payload simplificado: {str(e)}")
            content = "[Falha na transcrição do áudio]"
            
    # Salva no banco de dados
    await save_conversation_data(
        phone=phone_sanitized,
        message_type=payload.message_type,
        content=content,
        media_url=payload.media_url,
        wa_message_id=None,
        db=db
    )
    
    return JSONResponse(
        content={
            "phone": phone_sanitized,
            "message_type": payload.message_type,
            "content": content,
            "media_url": payload.media_url
        },
        status_code=200
    )

async def save_conversation_data(
    phone: str,
    message_type: str,
    content: str,
    media_url: Optional[str],
    wa_message_id: Optional[str],
    db: AsyncSession,
    first_name: Optional[str] = None
) -> Learner:
    """
    Busca ou cria o aprendiz pelo hash do telefone em conformidade estrita com a LGPD,
    e insere a nova mensagem no histórico de conversas.
    """
    # 1. Calcular o SHA-256 do telefone
    phone_hash = hashlib.sha256(phone.encode("utf-8")).hexdigest()
    
    # 2. Buscar o aprendiz pelo phone_hash
    stmt = select(Learner).where(Learner.phone_hash == phone_hash)
    result = await db.execute(stmt)
    learner = result.scalars().first()
    
    # 3. Se não existir, criar um novo aprendiz em conformidade com LGPD
    if not learner:
        logger.info(f"Criando novo aprendiz para o telefone com hash {phone_hash}")
        phone_encrypted = encrypt_data(phone)
        
        learner = Learner(
            phone_hash=phone_hash,
            phone_encrypted=phone_encrypted,
            first_name=first_name or "Aprendiz",
            current_state="onboarding",  # Estado inicial padrão
            consent_given=True,          # Consentimento padrão de desenvolvimento ou conforme fluxo
            level=1,
            completed_projects=0,
            total_earned_brl=0.00
        )
        db.add(learner)
        await db.flush()  # Para obtermos o learner.id
    else:
        # Se existir, atualiza timestamp de última atividade
        from datetime import datetime, timezone
        learner.last_active_at = datetime.now(timezone.utc)
        
    # 4. Gravar a conversa criptografada no banco
    content_encrypted = encrypt_data(content)
    
    conversation = Conversation(
        learner_id=learner.id,
        wa_message_id=wa_message_id,
        direction="inbound",
        content_type=message_type,
        content_encrypted=content_encrypted,
        openai_thread_id=learner.openai_thread_id
    )
    db.add(conversation)
    
    # Commit será realizado automaticamente pelo generator get_db ou podemos forçar
    await db.flush()
    
    return learner
