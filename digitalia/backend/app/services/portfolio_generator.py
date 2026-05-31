import os
import boto3
import logging
import asyncio
from botocore.exceptions import ClientError
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Configurações AWS / LocalStack S3
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "mock_key")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "mock_secret")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
LOCALSTACK_URL = os.getenv("LOCALSTACK_URL", "http://localhost:4566")
S3_BUCKET_PORTFOLIOS = os.getenv("S3_BUCKET_PORTFOLIOS", "digitalia-portfolios")

# Inicialização do cliente Boto3 S3 apontando para o LocalStack se fornecido
def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=LOCALSTACK_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    )

def _generate_and_upload_sync(learner_id: str, format_type: str = "pdf") -> Dict[str, Any]:
    """
    Função síncrona auxiliar executada em thread dedicada para não bloquear o loop de eventos assíncrono.
    """
    s3_client = get_s3_client()
    format_type = format_type.lower()
    
    # 1. Garantir que o bucket existe
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_PORTFOLIOS)
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "404":
            logger.info(f"Bucket {S3_BUCKET_PORTFOLIOS} não existe. Criando bucket...")
            try:
                s3_client.create_bucket(Bucket=S3_BUCKET_PORTFOLIOS)
            except Exception as create_err:
                logger.error(f"Erro ao criar o bucket {S3_BUCKET_PORTFOLIOS}: {str(create_err)}")
                raise create_err
        else:
            logger.error(f"Erro ao verificar bucket {S3_BUCKET_PORTFOLIOS}: {str(e)}")
            raise e

    # 2. Gerar conteúdo fictício (mock) válido em termos de formato básico
    if format_type == "pdf":
        # Estrutura em bytes de um arquivo PDF mínimo válido
        content = (
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R >>\nendobj\n"
            b"4 0 obj\n<< /Length 57 >>\nstream\n"
            b"BT\n/F1 24 Tf\n100 700 Td\n(DigitalIA - Portfolio do Aprendiz) Tj\nET\n"
            b"endstream\n"
            b"endobj\n"
            b"xref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000210 00000 n\n"
            b"trailer\n<< /Size 5 /Root 1 0 R >>\n"
            b"startxref\n318\n%%EOF\n"
        )
        content_type = "application/pdf"
    elif format_type in ["image", "png"]:
        # Estrutura em bytes de uma imagem PNG transparente de 1x1 pixel válida
        content = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
            b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        content_type = "image/png"
        format_type = "png"
    else:
        raise ValueError("Formato não suportado. Escolha entre 'pdf' ou 'image'.")

    # 3. Definir a chave do arquivo no S3
    file_key = f"portfolios/{learner_id}/portfolio.{format_type}"
    
    # 4. Fazer upload para o S3
    try:
        logger.info(f"Fazendo upload do portfólio mock ({format_type}) para s3://{S3_BUCKET_PORTFOLIOS}/{file_key}")
        s3_client.put_object(
            Bucket=S3_BUCKET_PORTFOLIOS,
            Key=file_key,
            Body=content,
            ContentType=content_type
        )
    except Exception as e:
        logger.error(f"Falha ao fazer upload do portfólio no S3: {str(e)}")
        raise e

    # 5. Gerar a URL pública do objeto (no LocalStack)
    # Formato padrão: http://localhost:4566/digitalia-portfolios/portfolios/{learner_id}/portfolio.{format_type}
    s3_url = f"{LOCALSTACK_URL}/{S3_BUCKET_PORTFOLIOS}/{file_key}"
    
    return {
        "learner_id": learner_id,
        "file_key": file_key,
        "format": format_type,
        "s3_url": s3_url,
        "size_bytes": len(content)
    }

async def generate_portfolio(learner_id: str, format_type: str = "pdf") -> Dict[str, Any]:
    """
    Interface assíncrona para gerar e fazer upload do portfólio de um aprendiz.
    Executa a chamada síncrona do boto3 no thread pool do asyncio.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _generate_and_upload_sync, learner_id, format_type)
