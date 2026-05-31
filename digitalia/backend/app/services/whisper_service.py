import os
import tempfile
import httpx
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-placeholder-development-only-1234567890abcdef")
WA_ACCESS_TOKEN = os.getenv("WA_ACCESS_TOKEN", "")

# Inicializar o cliente assíncrono da OpenAI
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def transcribe_audio(media_url: str) -> str:
    """
    Baixa áudio da WhatsApp Cloud API (ou outra URL de mídia),
    salva em um arquivo .ogg temporário, transcreve usando a Whisper API
    e retorna o texto transcrito.
    """
    if not media_url:
        raise ValueError("URL da mídia de áudio não foi fornecida.")

    logger.info(f"Iniciando download do áudio de: {media_url}")

    # Definir headers de autorização para WhatsApp Cloud API se aplicável
    headers = {}
    if "graph.facebook.com" in media_url and WA_ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {WA_ACCESS_TOKEN}"

    # Baixar o áudio de forma assíncrona
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(media_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Erro ao baixar mídia do WhatsApp. Status: {response.status_code}, Detalhes: {response.text}")
            raise Exception(f"Falha ao baixar áudio do WhatsApp. Status HTTP: {response.status_code}")
        audio_bytes = response.content

    # Gravar o áudio em arquivo temporário com extensão .ogg
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_audio:
        temp_audio.write(audio_bytes)
        temp_path = temp_audio.name

    logger.info(f"Áudio salvo temporariamente em: {temp_path}. Enviando para Whisper...")

    try:
        # Fazer a transcrição usando a API Whisper da OpenAI
        with open(temp_path, "rb") as audio_file:
            transcription = await openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        logger.info("Transcrição concluída com sucesso.")
        return transcription.text
    except Exception as e:
        logger.error(f"Erro na Whisper API: {str(e)}")
        raise e
    finally:
        # Garantir remoção do arquivo temporário
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as cleanup_err:
                logger.warning(f"Não foi possível remover arquivo temporário {temp_path}: {cleanup_err}")
