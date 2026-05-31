import os
import hashlib
import datetime
from typing import Optional
from sqlalchemy import select, update

from app.database import async_session
from app.models.models import Learner
from app.learning.assistant_factory import redis_client, process_learner_message
from app.core.lgpd import encrypt_data

class ConversationManager:
    """
    Gerencia a maquina de estados das interacoes com o WhatsApp para os aprendizes do DigitalIA.
    Estados da maquina:
      UNKNOWN -> ONBOARDING_NAME -> ONBOARDING_AGE -> ONBOARDING_CITY -> ONBOARDING_TRAIL -> LGPD_CONSENT -> ACTIVE_LEARNING
    
    Usa o Redis como cache de sessoes operacionais com TTL de 24 horas, reativado a cada interacao,
    garantindo otimizacao e alta escalabilidade em conformidade com a LGPD.
    """

    async def handle_webhook_message(self, payload: dict) -> str:
        """
        Processa o contrato da mensagem recebida do webhook do WhatsApp:
        {
            "phone": "str",
            "message_type": "str",
            "content": "str",
            "media_url": "str|null"
        }
        
        Retorna a string da resposta correspondente adaptada ao dialeto nordestino coloquial.
        """
        phone = payload.get("phone", "").strip()
        message_type = payload.get("message_type", "text").strip().lower()
        content = payload.get("content", "").strip()
        media_url = payload.get("media_url")

        # 1. Regra de Negocio Fallback de Imagem Imediato (sem transcrever)
        if message_type == "image":
            return (
                "Que legal a sua foto! Mas para eu te entender melhor, por favor me mande "
                "um texto ou me mande um áudio me explicando tudo!"
            )

        if not phone:
            return "Erro: Telefone de origem não identificado."

        # 2. Obter hash do telefone para buscas anonimas no banco (LGPD compliance)
        phone_hash = hashlib.sha256(phone.encode("utf-8")).hexdigest()
        cache_key = f"wa_session:{phone_hash}"

        # 3. Tentar recuperar dados do cache Redis para alta performance
        session_data = await redis_client.hgetall(cache_key)
        
        # Atualizar/Reativar TTL de 24 horas (86400 segundos) no Redis a cada interacao
        await redis_client.expire(cache_key, 86400)

        learner_id = None
        state = "unknown"

        if session_data and "learner_id" in session_data:
            learner_id = session_data["learner_id"]
            state = session_data.get("state", "unknown")
        else:
            # Se nao estiver no Redis, buscar ou criar no PostgreSQL de forma segura
            async with async_session() as db_session:
                res = await db_session.execute(
                    select(Learner).where(Learner.phone_hash == phone_hash)
                )
                learner = res.scalar_one_or_none()
                
                if not learner:
                    # Criar novo perfil anonimo de aprendiz (Art. 14 LGPD)
                    learner = Learner(
                        phone_hash=phone_hash,
                        phone_encrypted=encrypt_data(phone),
                        current_state="unknown",
                        level=1
                    )
                    db_session.add(learner)
                    await db_session.commit()
                    await db_session.refresh(learner)

                learner_id = str(learner.id)
                state = learner.current_state or "unknown"

            # Cachear a sessao no Redis com TTL de 24 horas
            await redis_client.hset(cache_key, mapping={
                "learner_id": learner_id,
                "state": state
            })
            await redis_client.expire(cache_key, 86400)

        # 4. Processamento da Maquina de Estados
        response_text = ""

        if state == "unknown":
            response_text = (
                "Eita, que coisa boa te ver por aqui! Meu nome é Mandacaru, sou o assistente de aprendizagem do *DigitalIA* "
                "e vou te ajudar a aprender habilidades digitais arretadas e ganhar um dinheirinho extra com internet! 🚀\n\n"
                "Pra começar de forma simples, me diga uma coisa: qual é o seu primeiro nome, visse?"
            )
            await self._update_state(learner_id, cache_key, "onboarding_name")

        elif state == "onboarding_name":
            name = content.strip().title()
            if len(name) < 2:
                response_text = "Se avexe não, digite seu nome certinho para eu poder te cadastrar:"
            else:
                async with async_session() as db_session:
                    await db_session.execute(
                        update(Learner).where(Learner.id == learner_id).values(first_name=name)
                    )
                    await db_session.commit()
                
                response_text = (
                    f"Massa demais, {name}! Prazer em te conhecer! 😊\n\n"
                    "Agora me diga: quantos anos você tem? (Lembrando que nossa plataforma atende jovens a partir de 16 anos, tá certo?)"
                )
                await self._update_state(learner_id, cache_key, "onboarding_age")

        elif state == "onboarding_age":
            try:
                # Extrair os numeros digitados
                age_digits = "".join(filter(str.isdigit, content))
                age = int(age_digits) if age_digits else 0
            except ValueError:
                age = 0

            if age < 16 or age > 100:
                response_text = (
                    "Ops! Por motivos de segurança e termos de uso, o *DigitalIA* atende apenas jovens "
                    "a partir de 16 anos. Por favor, digite uma idade válida (ex: 18):"
                )
            else:
                async with async_session() as db_session:
                    await db_session.execute(
                        update(Learner).where(Learner.id == learner_id).values(age=age)
                    )
                    await db_session.commit()
                
                response_text = (
                    "Show de bola! Cabra inteligente! ⚡\n\n"
                    "E onde você mora, visse? Me diga sua cidade e a sigla do estado. "
                    "Exemplo: *João Pessoa - PB* ou *Recife - PE*:"
                )
                await self._update_state(learner_id, cache_key, "onboarding_city")

        elif state == "onboarding_city":
            city_state = content.strip()
            city = city_state
            state_sigla = "PB"
            
            # Separador simples
            if "-" in city_state:
                parts = city_state.split("-")
                city = parts[0].strip().title()
                state_sigla = parts[1].strip().upper()[:2]
            elif "," in city_state:
                parts = city_state.split(",")
                city = parts[0].strip().title()
                state_sigla = parts[1].strip().upper()[:2]

            async with async_session() as db_session:
                await db_session.execute(
                    update(Learner).where(Learner.id == learner_id).values(city=city, state=state_sigla)
                )
                await db_session.commit()

            response_text = (
                "Perfeito! Agora chegou a hora mais arretada: escolher qual trilha digital você quer começar hoje! 🎓\n\n"
                "Responda apenas com o *NÚMERO* da opção que quer fazer:\n\n"
                "1️⃣ *Gestão de Redes Sociais*\n"
                "   Crie legendas, posts e organize calendários.\n"
                "   💰 Ganhe R$ 300 - R$ 800 por cliente fixo!\n\n"
                "2️⃣ *Design Visual com IA*\n"
                "   Aprenda Canva IA e monte marcas e posts lindos.\n"
                "   💰 Ganhe R$ 35 - R$ 150 por projeto visual!\n\n"
                "3️⃣ *Automação de Marketing*\n"
                "   Automatize o WhatsApp de lojas locais com IA.\n"
                "   💰 Ganhe R$ 150 - R$ 500 por automação!\n\n"
                "4️⃣ *Criação de Conteúdo em Vídeo*\n"
                "   Edite Reels e vídeos curtos fantásticos com CapCut.\n"
                "   💰 Ganhe R$ 50 - R$ 200 por vídeo editado!"
            )
            await self._update_state(learner_id, cache_key, "onboarding_trail")

        elif state == "onboarding_trail":
            choice = content.strip()
            trail_map = {
                "1": "social_media",
                "2": "design",
                "3": "automation",
                "4": "video"
            }
            
            selected_trail = trail_map.get(choice)
            if not selected_trail:
                response_text = (
                    "Se avexe não, mas responda apenas com o *NÚMERO* da trilha correspondente! "
                    "Escolha entre as opções 1, 2, 3 ou 4:"
                )
            else:
                async with async_session() as db_session:
                    await db_session.execute(
                        update(Learner).where(Learner.id == learner_id).values(current_trail=selected_trail)
                    )
                    await db_session.commit()

                response_text = (
                    "Excelente escolha! Essa trilha é arretada de boa e tem muito mercado! 🚀\n\n"
                    "Para sua segurança e conformidade legal, precisamos que você autorize a plataforma a coletar e tratar seus dados "
                    "de progresso, nome e contatos conforme a Lei Geral de Proteção de Dados (LGPD).\n\n"
                    "Você aceita nossos termos de privacidade para começar?\n\n"
                    "Responda:\n"
                    "✅ *SIM* para aceitar e começar agora\n"
                    "❌ *NÃO* para recusar"
                )
                await self._update_state(learner_id, cache_key, "lgpd_consent")

        elif state == "lgpd_consent":
            answer = content.strip().lower()
            if any(yes in answer for yes in ["sim", "aceito", "quero", "ok", "yes", "✅", "autorizo"]):
                # Coleta e termo consentido em conformidade com a LGPD
                async with async_session() as db_session:
                    res_learner = await db_session.execute(select(Learner).where(Learner.id == learner_id))
                    learner = res_learner.scalar_one()
                    age = learner.age or 18
                    
                    consent_date = datetime.datetime.now(datetime.timezone.utc)
                    retention_date = (consent_date + datetime.timedelta(days=730)).date()
                    
                    await db_session.execute(
                        update(Learner).where(Learner.id == learner_id).values(
                            consent_given=True,
                            consent_date=consent_date,
                            data_retention_until=retention_date,
                            parental_consent=True if age < 18 else None
                        )
                    )
                    await db_session.commit()
                
                await self._update_state(learner_id, cache_key, "active_learning")
                
                welcome_msg = (
                    "Maravilha! Seus dados estão seguros com a gente e em total conformidade com a LGPD! 🔒🛡️\n\n"
                    "Seja muito bem-vindo ao *DigitalIA*! Bora arrochar nos estudos! 🚀\n\n"
                )
                
                # Disparar imediatamente a lição inicial
                lesson_msg = await process_learner_message(
                    learner_id=learner_id,
                    message_text="proxima"
                )
                response_text = welcome_msg + lesson_msg
            else:
                response_text = (
                    "Se avexe não, meu fi. Entendemos a preocupação, mas para podermos salvar seu progresso, "
                    "te indicar projetos freelancers reais e emitir seu certificado em blockchain, a gente precisa que você concorde. "
                    "Se mudar de ideia e quiser liberar seu acesso, responda *SIM*!"
                )

        elif state == "active_learning":
            # Encaminhar a mensagem ao Assistant Factory do ChatGPT-4o
            response_text = await process_learner_message(
                learner_id=learner_id,
                message_text=content,
                audio_id=content if message_type == "audio" else None
            )

        else:
            response_text = "Oi! Como posso ajudar você? Se quiser continuar suas lições, mande *'proxima'*!"

        return response_text

    async def _update_state(self, learner_id: str, cache_key: str, new_state: str):
        """Atualiza o estado no cache Redis e no PostgreSQL de forma consistente."""
        # 1. Cache
        await redis_client.hset(cache_key, "state", new_state)
        # 2. Banco
        async with async_session() as db_session:
            await db_session.execute(
                update(Learner).where(Learner.id == learner_id).values(current_state=new_state)
            )
            await db_session.commit()
