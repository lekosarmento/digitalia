# DIGITALIA — Capacitação Digital com IA para Jovens de Comunidades Periféricas do Nordeste

> **⚠️ DOCUMENTO CONFIDENCIAL E PROTEGIDO**
> Este documento contém informações proprietárias e estratégicas de projeto. Sua leitura, reprodução, distribuição ou utilização para qualquer fim sem autorização expressa do autor é estritamente proibida. O acesso a este documento implica a aceitação de obrigações de confidencialidade equivalentes às de um **Non-Disclosure Agreement (NDA)**. Qualquer violação estará sujeita às sanções previstas na legislação brasileira (Lei 9.279/96, Lei 12.965/14 e correlatas).

**Autor:** José Werkley Sarmento Dias
**Organização:** ANENO — João Pessoa, Paraíba, Brasil
**Edital-alvo:** Fund for Innovation in Development (FID) — Inovação Social
**Versão:** 1.0 | **Data:** Maio/2026
**Classificação:** CONFIDENCIAL — NDA OBRIGATÓRIO

---

## 🤖 INSTRUÇÕES PARA AGENTES DE IDE

Este arquivo é o documento-mestre do projeto **DigitalIA**. Ele deve ser usado como contexto primário para geração de código, arquitetura, testes e documentação. Siga rigorosamente as especificações abaixo. Ao iniciar qualquer tarefa:

1. Leia **toda** esta especificação antes de gerar qualquer código
2. Use **Python 3.12+** para o backend e **TypeScript + React** para o frontend
3. A interface principal do aprendiz é o **WhatsApp** — toda UX deve ser pensada para mobile first com telas pequenas e dados limitados
4. O chatbot de IA é o produto central — invista em **qualidade de prompt engineering**
5. Todas as strings para o usuário final em **português brasileiro coloquial** — evitar termos técnicos sem explicação
6. Implemente **tracking granular** de progresso do aprendiz (cada interação conta)
7. O sistema de **matching** deve priorizar equidade: empoderar jovens com menos experiência dando-lhes primeiros projetos mais simples
8. Nunca armazene dados pessoais de menores de 18 anos sem autorização parental explícita
9. O backend deve suportar **20.000+ usuários simultâneos** no WhatsApp — use async em todo lugar
10. Use **Feature Flags** para habilitar funcionalidades por grupo de teste

---

## 1. VISÃO GERAL DO PROJETO

**DigitalIA** é uma plataforma de capacitação digital e empregabilidade que ensina jovens de 16 a 30 anos de comunidades periféricas nordestinas a usar ferramentas de inteligência artificial para oferecer serviços profissionais digitais. A formação acontece inteiramente via WhatsApp e web app leve, eliminando a barreira do computador. Um sistema de matching inteligente conecta aprendizes certificados com PMEs que precisam de serviços digitais acessíveis.

### Problema Central
- 87,2% dos nordestinos usam internet mas com qualidade e renda gerada muito abaixo do potencial
- Jovens periféricos têm smartphones mas não acessam o mercado de trabalho digital por falta de formação e rede de contatos
- Mercado freelancer paga R$ 35–200/projeto em design, social media e automação — mas jovens não sabem chegar até esse mercado
- 1,7 milhão de trabalhadores em plataformas digitais no Brasil em 2024 (IBGE) — mas concentrados em centros urbanos

### Solução
Plataforma que oferece:
- **Trilhas de microaprendizagem** entregues via chatbot GPT-4o no WhatsApp (lições de 5–10 min)
- **Projetos remunerados reais** a partir da 3ª semana
- **Sistema de matching** que conecta aprendizes certificados a PMEs nordestinas
- **Portfólio digital automático** gerado ao longo da jornada
- **Certificação digital** (blockchain Polygon) reconhecida por parceiros empresariais

---

## 2. ARQUITETURA DO SISTEMA

### 2.1 Visão Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                        APRENDIZ                                  │
│               WhatsApp (principal)  ←→  Web App                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │ Meta Cloud API (webhook)
┌──────────────────────▼──────────────────────────────────────────┐
│                  CONVERSATION ROUTER                             │
│         Identifica usuário → Estado → Intent → Handler           │
└────────┬──────────────┬───────────────────────┬─────────────────┘
         │              │                       │
┌────────▼──┐   ┌───────▼────────┐   ┌─────────▼────────────┐
│  LEARNING  │   │  PROJECT       │   │  PROFILE &           │
│  ENGINE    │   │  MARKETPLACE   │   │  CERTIFICATION       │
│ (GPT-4o   │   │ (Matching ML)  │   │  (Blockchain)        │
│  Assistants)  └────────────────┘   └──────────────────────┘
└────────┬──┘
         │
┌────────▼──────────────────────────────────────────────────────┐
│                    DATA LAYER                                   │
│   PostgreSQL  │  Redis (sessões/cache)  │  S3 (portfólios)     │
└───────────────────────────────────────────────────────────────┘
```

### 2.2 Stack Tecnológico

| Camada | Tecnologia | Versão | Papel |
|--------|-----------|--------|-------|
| Backend API | FastAPI | 0.115+ | API REST + Webhook handler |
| Runtime | Python | 3.12+ | Backend |
| IA/Chatbot | OpenAI Assistants API | v2 | Tutoria personalizada |
| IA/Transcrição | OpenAI Whisper | v2 | Transcrição de áudios WA |
| LLM Orquestração | LangChain | 0.2+ | Chains, memory, tools |
| Frontend | React + TypeScript + Vite | 18+ | Dashboard web leve |
| CSS | Tailwind CSS | 3.4+ | Mobile first |
| Database | PostgreSQL | 16+ | Principal |
| Cache/Sessões | Redis | 7.2+ | Estado das conversas WA |
| Queue | Celery | 5.3+ | Jobs assíncronos |
| Pagamentos | Mercado Pago API | — | Pix sem taxa |
| Certificação | Polygon (blockchain) | — | Certificados imutáveis |
| Storage | AWS S3 | — | Portfólios e vídeos |
| Containerização | Docker + Compose | 24+ | |

### 2.3 Estrutura de Diretórios

```
digitalia/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── routes/
│   │   │       │   ├── webhook.py        # WhatsApp webhook (principal)
│   │   │       │   ├── learners.py       # CRUD de aprendizes
│   │   │       │   ├── projects.py       # Marketplace de projetos
│   │   │       │   ├── matching.py       # API de matching
│   │   │       │   ├── certificates.py   # Emissão de certificados
│   │   │       │   └── companies.py      # Empresas/clientes
│   │   ├── core/
│   │   │   ├── security.py               # JWT, hashing
│   │   │   ├── lgpd.py                   # Consentimento, menores
│   │   │   └── feature_flags.py          # Feature toggles
│   │   ├── learning/                     # Motor de aprendizagem ⭐
│   │   │   ├── assistant_factory.py      # Cria Assistants por aprendiz
│   │   │   ├── conversation_manager.py   # Gerencia estado da conversa
│   │   │   ├── trail_manager.py          # Trilhas de conteúdo
│   │   │   ├── progress_tracker.py       # Tracking de progresso
│   │   │   └── content/                  # Conteúdo das trilhas
│   │   │       ├── trail_content.py      # Conteúdo das 4 trilhas
│   │   │       ├── trail_social.py       # Gestão de redes sociais
│   │   │       ├── trail_design.py       # Design visual com IA
│   │   │       ├── trail_video.py        # Criação de conteúdo em vídeo
│   │   │       └── trail_automation.py   # Automação de marketing
│   │   ├── marketplace/
│   │   │   ├── matching_engine.py        # ML de matching ⭐
│   │   │   ├── project_manager.py        # Criação e gestão de projetos
│   │   │   └── payment_service.py        # Pix via Mercado Pago
│   │   ├── services/
│   │   │   ├── whatsapp_service.py       # Envio de msgs WA
│   │   │   ├── whisper_service.py        # Transcrição de áudios
│   │   │   ├── portfolio_generator.py    # Gera portfólio automaticamente
│   │   │   └── blockchain_service.py     # Certificados Polygon
│   │   ├── models/
│   │   │   ├── learner.py                # Aprendiz (LGPD-aware)
│   │   │   ├── company.py                # Empresa cliente
│   │   │   ├── project.py                # Projeto freelancer
│   │   │   ├── match.py                  # Match aprendiz-projeto
│   │   │   ├── certificate.py            # Certificado digital
│   │   │   └── conversation.py           # Histórico de conversa
│   │   └── tasks/
│   │       ├── send_daily_lesson.py      # Lição diária agendada
│   │       ├── generate_portfolio.py     # Atualiza portfólio
│   │       └── process_payments.py       # Processar pagamentos Pix
│   ├── tests/
│   ├── alembic/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProgressDashboard.tsx     # Dashboard do aprendiz
│   │   │   ├── ProjectCard.tsx           # Card de projeto disponível
│   │   │   ├── PortfolioView.tsx         # Portfólio público
│   │   │   ├── CertificateCard.tsx       # Exibir certificados
│   │   │   └── CompanyDashboard.tsx      # Painel da empresa
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Learner.tsx               # Área do aprendiz
│   │   │   ├── Marketplace.tsx           # Marketplace de projetos
│   │   │   └── Company.tsx               # Área da empresa
│   ├── public/
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 3. MÓDULOS PRINCIPAIS — ESPECIFICAÇÃO DETALHADA

### 3.1 Motor de Aprendizagem — OpenAI Assistants API (`assistant_factory.py`)

**Conceito:** Cada aprendiz tem seu próprio **Assistant** criado na OpenAI, com instruções personalizadas e memória de thread. O assistant persiste o contexto da conversa entre sessões (via thread_id armazenado no Redis).

**Tools disponíveis para o Assistant:**

| Tool | Descrição | Trigger |
|------|-----------|---------|
| `record_lesson_completion` | Registra lição concluída + score | Ao finalizar exercício |
| `get_next_lesson` | Busca próxima lição personalizada | Após concluir ou pedir "próximo" |
| `submit_project_for_review` | Submete projeto para mentor | Ao enviar link/arquivo |
| `check_available_projects` | Lista projetos disponíveis para o perfil | Ao perguntar "tem projeto?" |
| `get_learner_progress` | Retorna progresso completo | Ao pedir "meu progresso" |
| `request_human_mentor` | Escalona para mentor humano | Quando IA não consegue ajudar |

```python
from openai import AsyncOpenAI
import json
from typing import Optional

client = AsyncOpenAI()

TRAIL_INSTRUCTIONS = {
    "social_media": """
Você é o Mentor Digital do DigitalIA, especializado em Gestão de Redes Sociais com IA.
Você está ensinando {learner_name}, {learner_age} anos, de {learner_city}-{learner_state}.

MISSÃO: Ensinar de forma prática e acolhedora para que {learner_name} consiga ganhar
dinheiro gerenciando redes sociais de pequenas empresas no Nordeste.

FERRAMENTAS QUE VOCÊ ENSINA:
- ChatGPT: criar legendas, textos e roteiros de forma profissional
- Canva IA: criar posts, stories e carrosséis com IA
- Meta Business Suite: agendar posts e analisar métricas
- CapCut: editar vídeos e reels profissionalmente
- Later/Buffer: calendário editorial automatizado

ESTILO DE ENSINO:
- Use linguagem simples e acolhedora, próxima à realidade nordestina
- Mensagens curtas: máximo 200 palavras por resposta no WhatsApp
- Comece sempre com "Oi {learner_name}!" ou variação
- Celebre TODA conquista com entusiasmo
- Se errar algo, corrija de forma positiva ("Quase! Vamos tentar de outro jeito...")
- Use exemplos de negócios locais (barraca de praia, restaurante, salão)
- Sempre conecte o aprendizado com dinheiro: "Com isso você pode cobrar R$ X"

ESTRUTURA DE AULA:
1. Conceito (2 min): Explicação simples do que é e por que importa
2. Demonstração (3 min): Mostre o passo a passo
3. Exercício prático (5 min): O aprendiz faz na hora
4. Feedback (2 min): Avalie e parabenize
5. Conexão com renda (1 min): "Com essa habilidade você pode..."

REGRAS ABSOLUTAS:
- Nunca avance sem o aprendiz completar o exercício
- Se o aprendiz mandar áudio, reconheça e responda ao conteúdo
- Se perguntar sobre preço de serviço, sempre responda com faixa realista
- Se demonstrar desânimo, motive com casos reais de sucesso antes de continuar
""",
    "design": "...",       # Similar para Trilha Design
    "automation": "...",   # Similar para Trilha Automação
    "video": "..."         # Similar para Trilha Vídeo/Conteúdo
}

async def create_or_get_assistant(
    learner_id: str,
    trail: str,
    learner_profile: dict
) -> tuple[str, str]:
    """
    Cria ou recupera o Assistant OpenAI para um aprendiz.

    Returns:
        Tuple (assistant_id, thread_id)
    """
    # Verificar se já existe no Redis
    cache_key = f"assistant:{learner_id}:{trail}"
    cached = await redis.hgetall(cache_key)

    if cached:
        return cached["assistant_id"], cached["thread_id"]

    # Criar novo assistant personalizado
    instructions = TRAIL_INSTRUCTIONS[trail].format(
        learner_name=learner_profile["first_name"],
        learner_age=learner_profile["age"],
        learner_city=learner_profile["city"],
        learner_state=learner_profile["state"]
    )

    assistant = await client.beta.assistants.create(
        name=f"Mentor DigitalIA — {learner_profile['first_name']}",
        instructions=instructions,
        model="gpt-4o",
        tools=[
            {"type": "function", "function": TOOL_RECORD_LESSON},
            {"type": "function", "function": TOOL_GET_NEXT_LESSON},
            {"type": "function", "function": TOOL_SUBMIT_PROJECT},
            {"type": "function", "function": TOOL_CHECK_PROJECTS},
            {"type": "function", "function": TOOL_GET_PROGRESS},
        ]
    )

    # Criar thread de conversa
    thread = await client.beta.threads.create()

    # Cachear no Redis (persistente)
    await redis.hset(cache_key, mapping={
        "assistant_id": assistant.id,
        "thread_id": thread.id
    })

    return assistant.id, thread.id

async def process_learner_message(
    learner_id: str,
    message_text: Optional[str] = None,
    audio_id: Optional[str] = None,
    image_url: Optional[str] = None
) -> str:
    """
    Processa mensagem do aprendiz e retorna resposta do assistant.

    Suporta texto, áudio (transcrição Whisper) e imagem (revisão de projeto).
    """
    learner = await get_learner(learner_id)
    assistant_id, thread_id = await create_or_get_assistant(
        learner_id, learner.current_trail, learner.profile
    )

    # Processar áudio se necessário
    if audio_id:
        message_text = await transcribe_whatsapp_audio(audio_id)

    # Construir content da mensagem
    content = []
    if message_text:
        content.append({"type": "text", "text": message_text})
    if image_url:
        content.append({"type": "image_url", "image_url": {"url": image_url}})

    # Adicionar mensagem à thread
    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )

    # Executar o assistant
    run = await client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        timeout=30
    )

    # Processar tool calls se necessário
    if run.status == "requires_action":
        tool_outputs = await handle_tool_calls(run.required_action.submit_tool_outputs.tool_calls)
        run = await client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

    # Extrair resposta final
    messages = await client.beta.threads.messages.list(thread_id=thread_id, limit=1)
    response_text = messages.data[0].content[0].text.value

    # Registrar no banco
    await log_conversation(learner_id, message_text or "[áudio]", response_text)

    return response_text
```

### 3.2 Gerenciador de Conversas WhatsApp (`conversation_manager.py`)

**Máquina de estados do aprendiz:**

```
UNKNOWN → ONBOARDING_NAME → ONBOARDING_AGE → ONBOARDING_CITY →
ONBOARDING_TRAIL_SELECTION → LGPD_CONSENT → ACTIVE_LEARNING →
PROJECT_AVAILABLE → PROJECT_IN_PROGRESS → CERTIFIED
```

```python
from enum import Enum

class LearnerState(str, Enum):
    UNKNOWN = "unknown"
    ONBOARDING_NAME = "onboarding_name"
    ONBOARDING_AGE = "onboarding_age"
    ONBOARDING_CITY = "onboarding_city"
    ONBOARDING_TRAIL = "onboarding_trail_selection"
    LGPD_CONSENT = "lgpd_consent"
    ACTIVE_LEARNING = "active_learning"
    PROJECT_AVAILABLE = "project_available"
    PROJECT_IN_PROGRESS = "project_in_progress"
    CERTIFIED = "certified"
    PAUSED = "paused"

class ConversationManager:
    """
    Gerencia o fluxo completo de conversas do aprendiz no WhatsApp.
    Estado armazenado no Redis com TTL de 24h (reativado a cada mensagem).
    """

    TRAIL_OPTIONS_MESSAGE = """
Ótimo, {name}! Agora escolha sua trilha de aprendizagem:

1️⃣ *Gestão de Redes Sociais*
   Crie conteúdo, gerencie Instagram e TikTok de empresas
   💰 Ganhe R$ 300–800/mês por cliente

2️⃣ *Design Visual com IA*
   Crie logos, posts e materiais com Canva IA e Adobe Firefly
   💰 Ganhe R$ 35–150 por projeto

3️⃣ *Automação de Marketing*
   Automatize processos com n8n, Make e ChatGPT
   💰 Ganhe R$ 150–500 por automação

4️⃣ *Criação de Conteúdo em Vídeo*
   Edite vídeos e reels profissionais com CapCut IA
   💰 Ganhe R$ 50–200 por vídeo

Responda com o número da trilha que quer começar!
"""

    async def handle_message(
        self,
        phone_hash: str,
        message: dict
    ) -> list[dict]:
        """
        Processa mensagem e retorna lista de mensagens de resposta.
        Cada item pode ser texto, template, imagem ou documento.
        """
        learner = await self._get_or_create_learner(phone_hash)
        state = LearnerState(learner.state)

        if state == LearnerState.UNKNOWN:
            return await self._handle_onboarding_start(learner)

        elif state in (
            LearnerState.ONBOARDING_NAME,
            LearnerState.ONBOARDING_AGE,
            LearnerState.ONBOARDING_CITY,
            LearnerState.ONBOARDING_TRAIL,
            LearnerState.LGPD_CONSENT
        ):
            return await self._handle_onboarding_step(learner, state, message)

        elif state == LearnerState.ACTIVE_LEARNING:
            # Delegar ao Assistant GPT-4o
            response_text = await process_learner_message(
                learner_id=learner.id,
                message_text=message.get("text"),
                audio_id=message.get("audio_id"),
                image_url=message.get("image_url")
            )
            return [{"type": "text", "body": response_text}]

        # ... demais estados
```

### 3.3 Transcrição de Áudios WhatsApp (`whisper_service.py`)

O WhatsApp é usado intensamente com mensagens de áudio no Nordeste. A transcrição é essencial para acessibilidade.

```python
import httpx
from openai import AsyncOpenAI
import tempfile

client = AsyncOpenAI()
META_GRAPH_BASE = "https://graph.facebook.com/v18.0"

async def transcribe_whatsapp_audio(
    audio_id: str,
    wa_token: str,
    language: str = "pt"
) -> str:
    """
    Baixa áudio do WhatsApp e transcreve com Whisper.

    WhatsApp entrega áudios em formato OGG/Opus.
    Whisper aceita: mp3, mp4, mpeg, mpga, m4a, wav, webm, ogg.

    Args:
        audio_id: ID do áudio no Meta Graph API
        wa_token: Token de acesso Meta
        language: Idioma (padrão: português)

    Returns:
        Texto transcrito
    """
    # 1. Obter URL temporária do áudio
    headers = {"Authorization": f"Bearer {wa_token}"}
    async with httpx.AsyncClient() as client_http:
        media_info = await client_http.get(
            f"{META_GRAPH_BASE}/{audio_id}",
            headers=headers
        )
        audio_url = media_info.json()["url"]

        # 2. Baixar o arquivo de áudio
        audio_response = await client_http.get(audio_url, headers=headers)
        audio_bytes = audio_response.content

    # 3. Transcrever com Whisper
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    with open(tmp_path, "rb") as audio_file:
        transcription = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,
            response_format="text"
        )

    return transcription.strip()
```

### 3.4 Sistema de Matching (`matching_engine.py`)

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass

@dataclass
class MatchResult:
    project_id: str
    match_score: float          # 0–100
    match_reasons: list[str]    # Por que este match foi feito
    estimated_earnings_brl: float
    difficulty_match: str       # "ideal", "desafiador", "simples demais"

def match_learner_to_projects(
    learner: dict,
    available_projects: list[dict],
    top_k: int = 5
) -> list[MatchResult]:
    """
    Faz matching entre aprendiz e projetos disponíveis.

    Critérios de matching:
    - Compatibilidade de skills (40%): skills do aprendiz vs. requisitos do projeto
    - Dificuldade adequada (25%): nível do projeto vs. progresso do aprendiz
    - Disponibilidade de tempo (20%): horas disponíveis vs. carga do projeto
    - Histórico e avaliações (15%): track record do aprendiz

    Princípio de equidade: aprendizes iniciantes recebem projetos simples
    de clientes bem avaliados para construir confiança e portfólio.
    """
    SKILL_KEYS = ["social_media", "design", "video", "automation", "copywriting"]

    learner_vector = np.array([
        learner["skills"].get(k, 0) / 10 for k in SKILL_KEYS
    ] + [
        min(learner["hours_available_weekly"], 40) / 40,
        min(learner["completed_projects"], 20) / 20,
        learner["avg_rating"] / 5.0 if learner["avg_rating"] else 0.5
    ]).reshape(1, -1)

    results = []
    for project in available_projects:
        # Verificar compatibilidade básica de trilha
        if project["required_trail"] not in learner["completed_trails"] + [learner["current_trail"]]:
            continue

        project_vector = np.array([
            project["required_skills"].get(k, 0) / 10 for k in SKILL_KEYS
        ] + [
            project["hours_needed"] / 40,
            project["complexity"] / 10,
            project["client_rating"] / 5.0
        ]).reshape(1, -1)

        base_score = float(cosine_similarity(learner_vector, project_vector)[0][0])

        # Bonus por equidade: boost projetos simples para iniciantes
        if learner["completed_projects"] < 3 and project["complexity"] <= 3:
            base_score += 0.15  # Boost de 15% para primeiros projetos

        # Penalidade se projeto é muito simples para experiente
        if learner["completed_projects"] > 10 and project["complexity"] < 3:
            base_score -= 0.10

        # Gerar razões do match em português
        reasons = []
        if project["required_trail"] == learner["current_trail"]:
            reasons.append(f"Projeto alinhado com sua trilha de {project['required_trail']}")
        if project["complexity"] <= learner["level"]:
            reasons.append("Dificuldade compatível com seu nível atual")
        if project["client_rating"] >= 4.5:
            reasons.append("Cliente bem avaliado — ótimo para seu portfólio")

        # Determinar adequação de dificuldade
        diff_gap = project["complexity"] - learner["level"]
        if abs(diff_gap) <= 1:
            difficulty_match = "ideal"
        elif diff_gap > 1:
            difficulty_match = "desafiador"
        else:
            difficulty_match = "simples demais"

        results.append(MatchResult(
            project_id=project["id"],
            match_score=round(min(base_score * 100, 100), 1),
            match_reasons=reasons,
            estimated_earnings_brl=project["budget_brl"] * 0.70,  # 70% para o aprendiz
            difficulty_match=difficulty_match
        ))

    return sorted(results, key=lambda x: x.match_score, reverse=True)[:top_k]
```

### 3.5 Pagamentos via Pix (`payment_service.py`)

```python
import mercadopago
from decimal import Decimal

sdk = mercadopago.SDK(MERCADO_PAGO_ACCESS_TOKEN)

async def create_project_payment(
    project_id: str,
    company_id: str,
    amount_brl: Decimal,
    description: str
) -> dict:
    """
    Cria cobrança Pix para empresa pelo projeto.
    Divisão: 70% aprendiz / 20% plataforma / 10% fundo de bolsas

    Returns:
        Dict com QR Code, chave Pix e prazo de pagamento
    """
    payment_data = {
        "transaction_amount": float(amount_brl),
        "description": f"DigitalIA — {description}",
        "payment_method_id": "pix",
        "payer": {"email": company_email},
        "external_reference": project_id,
        "notification_url": f"{BASE_URL}/api/v1/webhooks/mercadopago"
    }

    response = sdk.payment().create(payment_data)
    payment = response["response"]

    return {
        "payment_id": payment["id"],
        "qr_code": payment["point_of_interaction"]["transaction_data"]["qr_code"],
        "qr_code_base64": payment["point_of_interaction"]["transaction_data"]["qr_code_base64"],
        "pix_key": payment["point_of_interaction"]["transaction_data"]["ticket_url"],
        "expires_at": payment["date_of_expiration"],
        "amount_brl": float(amount_brl),
        "learner_share_brl": float(amount_brl * Decimal("0.70")),
        "platform_share_brl": float(amount_brl * Decimal("0.20")),
        "scholarship_share_brl": float(amount_brl * Decimal("0.10"))
    }
```

---

## 4. BANCO DE DADOS — SCHEMA

```sql
-- Aprendizes (LGPD-aware, suporte a menores)
CREATE TABLE learners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_hash VARCHAR(64) NOT NULL UNIQUE,
    phone_encrypted BYTEA NOT NULL,             -- AES-256-GCM para envio de msgs
    first_name VARCHAR(100),
    age INTEGER CHECK (age >= 16),
    city VARCHAR(100),
    state CHAR(2),
    current_trail VARCHAR(50),
    current_state VARCHAR(50) DEFAULT 'unknown',
    openai_assistant_id VARCHAR(200),           -- ID do Assistant OpenAI
    openai_thread_id VARCHAR(200),              -- ID da Thread ativa
    level INTEGER DEFAULT 1,                    -- 1-10: nível de habilidade
    completed_projects INTEGER DEFAULT 0,
    avg_rating DECIMAL(3,2),
    total_earned_brl DECIMAL(10,2) DEFAULT 0,
    -- LGPD
    consent_given BOOLEAN DEFAULT FALSE,
    consent_date TIMESTAMPTZ,
    parental_consent BOOLEAN,                   -- Obrigatório se age < 18
    data_retention_until DATE,
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_active_at TIMESTAMPTZ DEFAULT NOW(),
    anonymized_at TIMESTAMPTZ
);

-- Habilidades por aprendiz
CREATE TABLE learner_skills (
    learner_id UUID REFERENCES learners(id) ON DELETE CASCADE,
    skill VARCHAR(50) NOT NULL,                 -- "social_media", "design", etc.
    level DECIMAL(4,1) DEFAULT 0.0,             -- 0–10
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (learner_id, skill)
);

-- Trilhas completadas
CREATE TABLE completed_trails (
    learner_id UUID REFERENCES learners(id) ON DELETE CASCADE,
    trail VARCHAR(50) NOT NULL,
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    certificate_id UUID,
    PRIMARY KEY (learner_id, trail)
);

-- Progresso nas lições
CREATE TABLE lesson_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id UUID REFERENCES learners(id) ON DELETE CASCADE,
    trail VARCHAR(50),
    lesson_id VARCHAR(100),
    score DECIMAL(4,1),
    time_spent_minutes INTEGER,
    attempts INTEGER DEFAULT 1,
    completed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Empresas/clientes
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(200) NOT NULL,
    cnpj VARCHAR(14),
    contact_name VARCHAR(200),
    email VARCHAR(200) UNIQUE,
    phone_hash VARCHAR(64),
    city VARCHAR(100),
    state CHAR(2),
    avg_rating DECIMAL(3,2),
    total_projects INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projetos
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    required_trail VARCHAR(50),
    required_skills JSONB,                      -- {"social_media": 5, "design": 3}
    complexity INTEGER CHECK (complexity BETWEEN 1 AND 10),
    budget_brl DECIMAL(8,2),
    hours_needed DECIMAL(4,1),
    deadline_days INTEGER,
    status VARCHAR(20) DEFAULT 'open',          -- open, matched, in_progress, completed
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Matches aprendiz-projeto
CREATE TABLE project_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    learner_id UUID REFERENCES learners(id),
    match_score DECIMAL(5,1),
    status VARCHAR(20) DEFAULT 'proposed',      -- proposed, accepted, rejected, completed
    learner_rating DECIMAL(3,2),               -- Avaliação da empresa sobre o aprendiz
    payment_id VARCHAR(200),                    -- ID Mercado Pago
    learner_earned_brl DECIMAL(8,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Certificados digitais
CREATE TABLE certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id UUID REFERENCES learners(id),
    trail VARCHAR(50),
    level INTEGER CHECK (level BETWEEN 1 AND 3),
    tx_hash VARCHAR(200),                       -- Hash da transação Polygon
    contract_address VARCHAR(200),
    token_id BIGINT,
    issued_at TIMESTAMPTZ DEFAULT NOW(),
    metadata_url VARCHAR(500)                   -- IPFS URL com metadata do NFT
);

-- Histórico de conversas (criptografado)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    learner_id UUID REFERENCES learners(id) ON DELETE CASCADE,
    wa_message_id VARCHAR(200),
    direction VARCHAR(10) CHECK (direction IN ('inbound', 'outbound')),
    content_type VARCHAR(20) DEFAULT 'text',    -- text, audio, image
    content_encrypted BYTEA,                    -- AES-256-GCM
    openai_thread_id VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 5. CONTEÚDO DAS TRILHAS — ESTRUTURA

### Estrutura de um Módulo

```python
@dataclass
class Lesson:
    id: str
    trail: str
    module_number: int
    lesson_number: int
    title: str
    concept_text: str           # Explicação (max 200 chars para WA)
    demo_steps: list[str]       # Passo a passo numerado
    exercise: str               # O que o aprendiz deve fazer
    exercise_success_criteria: str  # Como o AI avalia o sucesso
    income_connection: str      # Conexão com renda real
    tools_used: list[str]       # Ferramentas utilizadas na lição

# Exemplo: Trilha Social Media — Módulo 1 — Lição 1
SOCIAL_MODULE1_LESSON1 = Lesson(
    id="social_m1_l1",
    trail="social_media",
    module_number=1,
    lesson_number=1,
    title="Criando a Primeira Legenda com ChatGPT",
    concept_text=(
        "Legenda boa = mais curtidas = mais clientes para a empresa. "
        "Com o ChatGPT você cria legendas profissionais em 30 segundos "
        "sem precisar ser escritor!"
    ),
    demo_steps=[
        "1. Acesse chat.openai.com (gratuito)",
        "2. Digite: 'Crie uma legenda para Instagram de uma barraca de tapioca em João Pessoa. "
        "Tom descontraído, com emoji e hashtags. Máx 150 palavras.'",
        "3. Leia o resultado e ajuste o que não combinar com o cliente",
        "4. Pronto! Tempo: menos de 1 minuto"
    ],
    exercise=(
        "Agora é sua vez! Escolha um negócio que você conhece (pode ser da sua rua) "
        "e crie uma legenda com o ChatGPT. Me manda o resultado aqui!"
    ),
    exercise_success_criteria=(
        "A legenda deve ter: tema claro do negócio, tom adequado, "
        "pelo menos 2 hashtags, e menos de 200 palavras."
    ),
    income_connection=(
        "Empresas pagam R$ 50–150 por pacote de 4 legendas por semana. "
        "Com 3 clientes fixos = R$ 150–450/mês só com legendas!"
    ),
    tools_used=["ChatGPT"]
)
```

---

## 6. SEGURANÇA, PRIVACIDADE E LGPD

> Esta seção é **obrigatória** para implementação. Nenhum módulo deve ser desenvolvido sem considerar as regras aqui definidas.

### 6.1 Conformidade com a LGPD (Lei 13.709/2018)

O DigitalIA coleta dados de jovens, incluindo potencialmente **menores de 18 anos**. A proteção de dados de menores é **prioridade máxima** na plataforma.

**Base legal:** Consentimento (Art. 7º, I) + Execução de contrato (Art. 7º, V) para pagamentos

**Dados coletados e tratamento:**

| Dado | Finalidade | Retenção | Risco | Mitigação |
|------|-----------|---------|-------|-----------|
| Número de telefone | Identificação e comunicação | 5 anos | Alto (PII) | AES-256-GCM + hash SHA-256 |
| Nome | Personalização | 5 anos | Médio | Criptografado em repouso |
| Idade | Verificação e personalização | 5 anos | Médio | Verificação parental para <18 |
| Cidade/Estado | Matching geográfico | 5 anos | Baixo | Anonimizado em análises |
| Histórico de conversas | Melhoria do modelo | 2 anos | Alto | Criptografado AES-256-GCM |
| Dados de performance | Certificação e matching | Permanente | Baixo | Anonimizado após saída |
| Dados financeiros (Pix) | Pagamentos | 10 anos (tributário) | Alto | Mercado Pago como processador |

**Proteção especial para menores (Art. 14 LGPD):**
```python
class MinorProtection:
    """
    Implementa proteções especiais para aprendizes menores de 18 anos,
    conforme Art. 14 da LGPD.
    """

    async def check_parental_consent(self, learner_id: str, age: int) -> bool:
        """
        Se aprendiz tem menos de 18 anos, solicita e registra
        consentimento parental explícito antes de qualquer coleta.
        """
        if age >= 18:
            return True

        # Enviar mensagem para o número informado como responsável
        consent_message = """
⚠️ Atenção, responsável!

{minor_name}, de {age} anos, quer aprender a ganhar dinheiro
com habilidades digitais no DigitalIA.

Para participar, precisamos da sua autorização.

Você autoriza? Responda:
✅ SIM — autorizo
❌ NÃO — não autorizo

O DigitalIA não coleta dados de menores sem autorização do responsável.
"""
        # Aguardar resposta por 48h
        # Registrar consentimento ou bloquear cadastro
        pass
```

**Direitos dos titulares — endpoints:**
```
GET  /api/v1/learners/me/data      → Exportar todos os dados
GET  /api/v1/learners/me/export    → Download JSON/CSV
PATCH /api/v1/learners/me          → Corrigir dados
DELETE /api/v1/learners/me         → Solicitar exclusão (prazo: 15 dias)
POST /api/v1/learners/me/opt-out   → Revogar consentimento de marketing
```

### 6.2 Segurança de Dados

**Criptografia em repouso:**
- Números de telefone: dupla proteção — SHA-256 hash para lookups + AES-256-GCM para uso operacional
- Histórico de conversas: AES-256-GCM com chave derivada por usuário
- Credenciais de API (OpenAI, Meta, Mercado Pago): AWS Secrets Manager
- Dados de pagamento: nunca armazenados localmente — Mercado Pago como PCI-DSS compliant

**Autenticação e autorização:**
```python
class PermissionLevel(str, Enum):
    LEARNER = "learner"          # Acessa apenas próprios dados
    MENTOR = "mentor"            # Acessa dados dos mentorados
    COMPANY = "company"          # Acessa projetos e resultados
    ADMIN = "admin"              # Acesso total (2FA obrigatório)
    AUDITOR = "auditor"          # Read-only para LGPD compliance

# JWT com claims de permissão
JWT_PAYLOAD_EXAMPLE = {
    "sub": "learner_uuid",
    "role": "learner",
    "exp": "timestamp",
    "jti": "unique_token_id",   # Para revogação
    "lgpd_consent": True,
    "parental_consent": True     # Apenas para menores
}
```

**Segurança do sistema de matching:**
- Dados pessoais do aprendiz nunca expostos à empresa antes da aceitação do match
- Empresa vê apenas: nível de habilidade, trilha concluída, avaliação média, cidade/estado
- Após aceite: empresa recebe primeiro nome + portfólio público
- Número de telefone só compartilhado após assinatura de termo de uso da empresa

**Proteção contra abuso:**
- Limite de 3 projetos simultâneos por aprendiz
- Avaliações de empresa só válidas após confirmação de entrega
- Sistema de denúncia de comportamento inadequado (empresa ou aprendiz)
- Bloqueio automático de empresa com avaliação < 2.0

**Auditoria:**
- Cada acesso a dados de aprendiz gera registro no `audit_log`
- Relatório LGPD automático mensal para o DPO
- Logs de autenticação retidos por 2 anos

### 6.3 Segurança do WhatsApp

```python
import hmac
import hashlib
from fastapi import Request, HTTPException

async def verify_whatsapp_webhook(request: Request) -> bytes:
    """
    Verificação obrigatória de assinatura Meta antes de processar qualquer mensagem.
    Nunca processar payload sem verificação — risco de injeção de mensagens falsas.
    """
    signature = request.headers.get("X-Hub-Signature-256", "")
    body = await request.body()

    if not signature:
        raise HTTPException(403, "Webhook signature missing")

    expected = "sha256=" + hmac.new(
        WA_APP_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(403, "Invalid webhook signature")

    return body
```

**Validações adicionais de segurança:**
- Aceitar webhooks apenas de IPs Meta (whitelist: 31.13.24.0/21, 66.220.144.0/20)
- Tamanho máximo de mensagem: 4096 bytes
- Rate limit: máx 500 mensagens/hora por número de origem
- Validar formato de mensagem antes de processar (schema Pydantic)
- Auditar todas as mensagens com conteúdo suspeito (ML classifier)

### 6.4 Variáveis de Ambiente (`.env.example`)

```bash
# Application
APP_ENV=development
SECRET_KEY=your-256-bit-key
DEBUG=false
ALLOWED_HOSTS=["digitalia.com.br", "api.digitalia.com.br"]
MINOR_MINIMUM_AGE=16
PARENTAL_CONSENT_REQUIRED_BELOW_AGE=18

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/digitalia
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o
OPENAI_WHISPER_MODEL=whisper-1

# WhatsApp
WA_PHONE_NUMBER_ID=your-id
WA_ACCESS_TOKEN=your-token
WA_APP_SECRET=your-secret
WA_VERIFY_TOKEN=your-verify-token

# Mercado Pago
MP_ACCESS_TOKEN=your-mp-token
MP_PUBLIC_KEY=your-mp-public-key
MP_PLATFORM_SHARE_PCT=0.20
MP_SCHOLARSHIP_SHARE_PCT=0.10

# Blockchain (Polygon)
POLYGON_RPC_URL=https://polygon-rpc.com
POLYGON_PRIVATE_KEY=your-wallet-private-key
CERTIFICATE_CONTRACT_ADDRESS=your-contract-address

# AWS
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=sa-east-1
S3_BUCKET_PORTFOLIOS=digitalia-portfolios

# LGPD
DATA_RETENTION_YEARS=5
CONVERSATION_RETENTION_YEARS=2
MINOR_DATA_EXTRA_PROTECTION=true
DPO_EMAIL=dpo@digitalia.com.br
```

---

## 7. ROADMAP DE DESENVOLVIMENTO

### Fase 1 — MVP (Meses 1–3)
- [ ] Setup: Docker, PostgreSQL, Redis, Celery
- [ ] Webhook WhatsApp com verificação de assinatura
- [ ] Sistema de onboarding (coleta de perfil + consentimento LGPD)
- [ ] Motor de aprendizagem: Assistants API + 4 trilhas (módulo 1 de cada)
- [ ] Transcrição de áudio com Whisper
- [ ] Progress tracker e banco de dados de progresso
- [ ] Piloto: 200 aprendizes em João Pessoa e Campina Grande
- [ ] 20 mentores voluntários cadastrados

**Critérios de aceite Fase 1:**
- Onboarding completo em < 5 mensagens
- Tempo de resposta do chatbot < 3 segundos
- Taxa de conclusão do primeiro módulo > 60%
- 0 dados pessoais expostos em logs

### Fase 2 — Marketplace (Meses 4–6)
- [ ] Sistema de matching (ML engine)
- [ ] Cadastro de empresas/clientes
- [ ] Fluxo completo de projeto (proposta → aceite → entrega → pagamento Pix)
- [ ] Gerador automático de portfólio
- [ ] Dashboard web para aprendiz e empresa
- [ ] Expansão: Recife, Fortaleza, Natal

### Fase 3 — Escala (Meses 7–12)
- [ ] Certificados blockchain (Polygon)
- [ ] Todos os estados do Nordeste
- [ ] Parcerias com SEBRAE e secretarias de educação
- [ ] App mobile React Native
- [ ] Meta: 5.000 aprendizes ativos, R$ 200.000 em projetos realizados/mês

### Fase 4 — Sustentabilidade (Ano 2–3)
- [ ] Modelo freemium para empresas (R$ 150/mês)
- [ ] Licenciamento para prefeituras
- [ ] Expansão para Argentina, Colômbia, Peru (adaptação idioma)

---

## 8. TESTES

```python
# tests/test_matching_engine.py
import pytest
from app.marketplace.matching_engine import match_learner_to_projects

class TestMatchingEngine:

    def test_beginner_gets_simple_projects(self):
        """Iniciante deve receber projetos simples."""
        learner = {
            "skills": {"social_media": 2, "design": 1},
            "hours_available_weekly": 20,
            "completed_projects": 0,
            "avg_rating": None,
            "level": 2,
            "current_trail": "social_media",
            "completed_trails": []
        }
        projects = [
            {"id": "p1", "required_trail": "social_media", "complexity": 2,
             "budget_brl": 150, "hours_needed": 5, "client_rating": 4.8,
             "required_skills": {"social_media": 2}},
            {"id": "p2", "required_trail": "social_media", "complexity": 8,
             "budget_brl": 800, "hours_needed": 40, "client_rating": 4.0,
             "required_skills": {"social_media": 8, "design": 6}}
        ]
        results = match_learner_to_projects(learner, projects)
        # Projeto simples deve aparecer primeiro
        assert results[0].project_id == "p1"
        assert results[0].match_score > results[-1].match_score

    def test_equity_boost_for_first_projects(self):
        """Boost de equidade para primeiros projetos de iniciantes."""
        learner_beginner = {**BASE_LEARNER, "completed_projects": 0, "level": 2}
        learner_expert = {**BASE_LEARNER, "completed_projects": 15, "level": 8}

        simple_project = SIMPLE_PROJECT  # complexity=2

        result_beginner = match_learner_to_projects(learner_beginner, [simple_project])[0]
        result_expert = match_learner_to_projects(learner_expert, [simple_project])[0]

        # Iniciante deve ter score maior em projeto simples (boost de equidade)
        assert result_beginner.match_score > result_expert.match_score

    def test_never_matches_wrong_trail(self):
        """Nunca deve fazer match com trilha que o aprendiz não completou."""
        learner = {**BASE_LEARNER, "current_trail": "social_media", "completed_trails": []}
        design_project = {**BASE_PROJECT, "required_trail": "design"}

        results = match_learner_to_projects(learner, [design_project])
        assert len(results) == 0
```

---

## 9. IMPACTO E MÉTRICAS DE SUCESSO

| Métrica | Ano 1 | Ano 2 | Ano 3 |
|---------|-------|-------|-------|
| Aprendizes onboardados | 1.000 | 3.000 | 5.000 |
| Módulos concluídos | 12.000 | 45.000 | 100.000 |
| Certificados emitidos | 500 | 2.000 | 5.000 |
| Projetos realizados | 1.500 | 8.000 | 20.000 |
| Renda gerada (R$/mês) | R$ 180K | R$ 800K | R$ 2M |
| PMEs atendidas | 400 | 1.200 | 2.500 |
| Taxa de conclusão de módulos | >55% | >65% | >70% |
| NPS (aprendizes) | >65 | >72 | >80 |
| % aprendizes mulheres | >55% | >58% | >60% |

---

## 10. REFERÊNCIAS E FONTES

- OpenAI Assistants API: https://platform.openai.com/docs/assistants/overview
- OpenAI Whisper: https://platform.openai.com/docs/guides/speech-to-text
- WhatsApp Cloud API: https://developers.facebook.com/docs/whatsapp/
- Mercado Pago API: https://www.mercadopago.com.br/developers/
- Polygon (blockchain): https://polygon.technology/
- IBGE PNAD TIC 2024: https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/44031-internet-chega-a-74-9-milhoes-de-domicilios-do-pais-em-2024
- LGPD Lei 13.709/2018: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm
- FID Fund for Innovation: https://fundinnovation.dev/
- SEBRAE: https://www.sebrae.com.br/
- Workana: https://www.workana.com/
- n8n Automação: https://n8n.io/
- Canva API: https://www.canva.com/developers/

---

*Documento gerado em Maio/2026 | Confidencial — NDA Obrigatório*
*© José Werkley Sarmento Dias — Todos os direitos reservados*
