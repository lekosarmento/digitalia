import hmac
import hashlib
import json
import httpx
import sys

import os

# Chave secreta de teste definida no docker-compose.yml para a API
WA_APP_SECRET = "digitalia_app_secret_placeholder"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://api:8000/api/v1/webhook" if os.path.exists("/.dockerenv") else "http://localhost:8000/api/v1/webhook")

def test_meta_webhook_simulation():
    print("\n=== SIMULANDO WEBHOOK META COM ASSINATURA HMAC-SHA256 ===")
    
    # Payload oficial da Meta simplificado
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "entry-id-123",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "5583999998877",
                                "phone_number_id": "phone-id-abc"
                            },
                            "contacts": [
                                {
                                    "profile": {
                                        "name": "Maria Silva"
                                    },
                                    "wa_id": "5583999991122"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "5583999991122",
                                    "id": "wamid.HBgMNTU4Mzk5OTk5MTEyMhUCABEYEjhG...",
                                    "timestamp": "1672531199",
                                    "text": {
                                        "body": "Oi, vim me cadastrar no DigitalIA!"
                                    },
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    # Serializa o corpo em JSON sem espaços extras
    body_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    
    # Calcula a assinatura HMAC SHA-256
    expected_signature = hmac.new(
        WA_APP_SECRET.encode("utf-8"),
        body_bytes,
        hashlib.sha256
    ).hexdigest()
    
    # Adiciona prefixo exigido pela Meta
    signature_header = f"sha256={expected_signature}"
    
    headers = {
        "Content-Type": "application/json",
        "x-hub-signature-256": signature_header
    }
    
    # Faz o POST para o Webhook local
    response = httpx.post(WEBHOOK_URL, content=body_bytes, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response JSON: {response.text}")
    
    if response.status_code == 200:
        print("✅ Sucesso: O webhook da Meta validou a assinatura HMAC e processou com êxito!")
    else:
        print("❌ Erro: O webhook rejeitou a assinatura HMAC ou falhou no processamento.")
        sys.exit(1)

def test_simplified_webhook():
    print("\n=== SIMULANDO WEBHOOK DE CONTRATO SIMPLIFICADO ===")
    
    payload = {
        "phone": "5583999992233",
        "message_type": "text",
        "content": "Quero iniciar a trilha de Automação de Marketing",
        "media_url": None
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Sem x-hub-signature-256 para testar a rota simplificada/direta do sandbox
    response = httpx.post(WEBHOOK_URL, json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response JSON: {response.text}")
    
    if response.status_code == 200:
        print("✅ Sucesso: O contrato simplificado foi processado perfeitamente!")
    else:
        print("❌ Erro: O contrato simplificado falhou.")
        sys.exit(1)

if __name__ == "__main__":
    test_meta_webhook_simulation()
    test_simplified_webhook()
