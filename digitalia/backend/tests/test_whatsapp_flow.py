import asyncio
import json
import os
import sys

# Adiciona o diretório backend ao sys.path para imports funcionarem corretamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine
from app.models.models import Base
from app.learning.conversation_manager import ConversationManager

async def setup_test_db():
    """Garante que as tabelas de teste existem no banco de dados local."""
    async with engine.begin() as conn:
        # Cria as tabelas se não existirem
        await conn.run_sync(Base.metadata.create_all)
    print("Tabelas do banco de dados configuradas com sucesso!")

async def run_simulation():
    # Inicializa tabelas
    await setup_test_db()

    manager = ConversationManager()
    phone_number = "5583999998877"

    print("\n--- SIMULAÇÃO DE JORNADA DO APRENDIZ ---")

    # 1. Saudação inicial
    print("\n[Ação] Jovem envia mensagem inicial...")
    payload1 = {
        "phone": phone_number,
        "message_type": "text",
        "content": "Olá, quero aprender habilidades digitais!"
    }
    resp1 = await manager.handle_webhook_message(payload1)
    print(f"[Sistema]:\n{resp1}")

    # 2. Envio do nome
    print("\n[Ação] Jovem responde com o nome...")
    payload2 = {
        "phone": phone_number,
        "message_type": "text",
        "content": "José"
    }
    resp2 = await manager.handle_webhook_message(payload2)
    print(f"[Sistema]:\n{resp2}")

    # 3. Envio da idade
    print("\n[Ação] Jovem responde com a idade...")
    payload3 = {
        "phone": phone_number,
        "message_type": "text",
        "content": "19"
    }
    resp3 = await manager.handle_webhook_message(payload3)
    print(f"[Sistema]:\n{resp3}")

    # 4. Envio de cidade e estado
    print("\n[Ação] Jovem responde com a cidade...")
    payload4 = {
        "phone": phone_number,
        "message_type": "text",
        "content": "João Pessoa - PB"
    }
    resp4 = await manager.handle_webhook_message(payload4)
    print(f"[Sistema]:\n{resp4}")

    # 5. Escolha de trilha
    print("\n[Ação] Jovem escolhe trilha 1 (Gestão de Redes Sociais)...")
    payload5 = {
        "phone": phone_number,
        "message_type": "text",
        "content": "1"
    }
    resp5 = await manager.handle_webhook_message(payload5)
    print(f"[Sistema]:\n{resp5}")

    # 6. Consentimento LGPD
    print("\n[Ação] Jovem aceita os termos LGPD...")
    payload6 = {
        "phone": phone_number,
        "message_type": "text",
        "content": "SIM, eu concordo"
    }
    resp6 = await manager.handle_webhook_message(payload6)
    print(f"[Sistema]:\n{resp6}")

    # 7. Resposta do exercício da lição 1
    print("\n[Ação] Jovem envia a legenda criada no exercício da Lição 1...")
    payload7 = {
        "phone": phone_number,
        "message_type": "text",
        "content": "Legenda arretada para a Tapiocaria do Biu em Manaíra! Tapioca quentinha com coco e queijo coalho, o melhor do Nordeste. Venha provar! #TapiocaDoBiu #JoaoPessoa #NordesteGostoso"
    }
    resp7 = await manager.handle_webhook_message(payload7)
    print(f"[Sistema]:\n{resp7}")

    # 8. Fallback de Imagem
    print("\n[Ação] Jovem envia uma imagem/foto...")
    payload8 = {
        "phone": phone_number,
        "message_type": "image",
        "content": "foto_do_prato.jpg",
        "media_url": "http://mock-wa-cdn/img123"
    }
    resp8 = await manager.handle_webhook_message(payload8)
    print(f"[Sistema]:\n{resp8}")

if __name__ == "__main__":
    asyncio.run(run_simulation())
