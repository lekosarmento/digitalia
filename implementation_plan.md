# Plano de Implementação Oficial — Projeto DigitalIA

O **DigitalIA** é uma plataforma de capacitação digital e empregabilidade para jovens de 16 a 30 anos de comunidades periféricas do Nordeste brasileiro. O sistema funciona via WhatsApp (orquestrado pela API de Assistants v2 da OpenAI e transcrição Whisper) e um Web App leve para portfólios, matching e painel administrativo.

Este plano detalha a arquitetura técnica, as fases sequenciais/paralelas e a orquestração dos múltiplos agentes especialistas.

---

## 🤖 1. Estratégia de Execução e Ordem das Fases

Para eliminar a dependência oculta e evitar conflitos de escopo (como importações de modelos inexistentes ou contratos divergentes), a execução está estruturada em **quatro fases sequenciais e paralelas**:

```mermaid
graph TD
    Parent[Antigravity - Orquestrador] -->|Define & Executa| F1[Fase A: Sequencial - Banco de Dados]
    F1 -->|Tabelas Prontas| F2[Fase B: Paralelo - Core, IA e Segurança]
    F1 -->|Tabelas Prontas| F3[Fase C: Paralelo - Frontend]
    F2 -->|Código Backend Pronto| F4[Fase D: Sequencial - Integração & Testes]
    F3 -->|Frontend Integrado| F4

    subgraph Fase A
        A1[Agente 1: DB Expert - models.py + Alembic + Docker]
    end

    subgraph Fase B
        B1[Agente 2: Core Backend - Webhooks, WhatsApp, Whisper]
        B2[Agente 3: IA Engine - Assistants API v2, State Machine]
        B3[Agente 4: Segurança LGPD - AES-256-GCM, Consentimento, JWT]
    end

    subgraph Fase C
        C1[Agente 5: Frontend React - Vite, TS, Tailwind CSS]
    end

    subgraph Fase D
        D1[Orquestrador: Testes Integrados, Correção de Interfaces, Mocking de Payloads]
    end
```

---

### 📅 Cronograma de Agentes e Escopos de Trabalho

#### **FASE A: Sequencial (~1 a 2 hours)**
*   **Agente 1 (`digitalia-db-expert`)**:
    *   **Escopo**: Configuração do banco assíncrono com SQLAlchemy (`models.py`), migrations iniciais com Alembic e infraestrutura Docker Compose completa.
    *   **Mitigação de Inicialização LocalStack/Postgres**:
        *   Criação de `backend/scripts/create_s3_buckets.sh` para inicializar automaticamente o bucket `digitalia-portfolios` no LocalStack ao subir o compose.
        *   Criação de `backend/scripts/init_db.sql` para preparar o banco PostgreSQL, habilitando a extensão de UUID (`pgcrypto` / `uuid-ossp`) e criando esquemas necessários.
    *   **Especificação Estrita do `requirements.txt`**:
        *   Para evitar dependências incompletas nas fases paralelas, o Agente 1 gerará o `requirements.txt` com as seguintes bibliotecas obrigatórias:
            ```text
            fastapi
            uvicorn[standard]
            sqlalchemy[asyncio]
            asyncpg
            alembic
            redis
            celery
            boto3
            openai
            python-jose[cryptography]
            cryptography
            httpx
            pytest
            pytest-asyncio
            ```
    *   **Containers Docker**:
        1. `postgres:16` (Banco principal).
        2. `redis:7.2` (Sessões e máquina de estados do chatbot).
        3. `localstack/localstack` (Emulação local do AWS S3 com auto-inicialização de buckets).
        4. `celery` + `worker` (Processamento de tarefas em segundo plano).
    *   **Entregável**: Banco de dados e infraestrutura de suporte online localmente, com todas as tabelas criadas, buckets S3 criados automaticamente e prontos para importação.

#### **FASE B: Paralelo (~3 a 4 horas)**
*   **Agente 2 (`digitalia-backend-core`)**:
    *   **Escopo**: FastAPI, roteamento geral, download de áudio/mídia Meta, Whisper Service para transcrição de áudio, integração com o LocalStack S3 (boto3 configurado com `endpoint_url`).
    *   **Entregável**: Servidor FastAPI funcional com rotas expostas e processamento de mídias integrado ao S3 local.
*   **Agente 3 (`digitalia-ai-learning-engine`)**:
    *   **Escopo**: Conexão com OpenAI Assistants API v2, máquina de estados do WhatsApp (`LearnerState`), gerenciador de conversas com cache no Redis (TTL de 24h) e Function Calling do Assistant.
    *   **Alinhamento de Contrato de Webhook & Fallback de Imagem**:
        *   O Agente 3 trabalhará estritamente com o seguinte contrato fixado de entrada de dados para mensagens de chat:
            ```json
            {
              "phone": "str",
              "message_type": "str (text | audio | image)",
              "content": "str (texto ou link temporário da mídia)",
              "media_url": "str | null"
            }
            ```
        *   **Regra de Imagem**: Fica explicitado no prompt/lógica do Agente 3 que, caso `message_type == 'image'`, o sistema **não** tentará realizar transcrição (Whisper) e responderá imediatamente com uma mensagem simpática e instrutiva de fallback: *"Que legal a sua foto! Mas para eu te entender melhor, por favor me mande um texto ou me mande um áudio me explicando tudo!"*, evitando crashes ou comportamentos erráticos.
    *   **Entregável**: Lógica de conversação inteligente via WhatsApp com persistência, navegação pelas lições e tratamento seguro de mídias.
*   **Agente 4 (Revisado — Foco em LGPD)**:
    *   **Escopo**: Segurança pura e privacidade. Implementação de criptografia AES-256-GCM em repouso no banco para PII (telefone, nome e histórico de mensagens), lógica de consentimento parental de menores de 18 anos, JWT com claims de permissão, rate limiting e **Mock total de Blockchain** (retornando UUIDs imutáveis como `tx_hash` para os certificados).
    *   **Entregável**: Barreira criptográfica LGPD e mock de certificados funcional, eliminando taxas de gas e dependência da Polygon no MVP.

#### **FASE C: Paralelo (Pode começar junto com B)**
*   **Agente 5 (`digitalia-frontend-architect`)**:
    *   **Escopo**: Frontend em React + TypeScript + Vite + Tailwind CSS. Dashboard do Aprendiz (mobile-first, leve e otimizado para celulares) com visualização do progresso das lições e do portfólio público gerado.
    *   **Alinhamento de Endpoints e Autenticação de Webhook**:
        *   Para mitigar divergências com o Agente 2, o frontend utilizará paths de API padronizados:
            *   `GET /api/v1/learners/me/data` (Exportar dados do perfil)
            *   `GET /api/v1/projects/available` (Lista projetos de matching)
            *   `POST /api/v1/webhook` (Injeção de payloads de simulação do WhatsApp)
        *   **Aviso de Assinatura HMAC**: O Agente 5 é explicitamente instruído de que o endpoint de webhook exige o cabeçalho `X-Hub-Signature-256` contendo um HMAC válido. Testes de simulação locais originados do frontend de testes devem enviar uma assinatura HMAC-SHA256 gerada ou passar pela ferramenta de bypass de ambiente sandbox de desenvolvimento.
    *   **Entregável**: Interface web integrada às APIs REST respeitando o contrato e autenticação de segurança predefinidos.

#### **FASE D: Integração e Testes (Agente Orquestrador)**
*   **Papel de Antigravity (Nós)**:
    *   **Escopo**: Integração fina de todas as entregas dos subagentes, resolução de incompatibilidades de imports, e validação dos 3 testes críticos.
    *   **Testes e Ferramentas**:
        1. Criação do script `/scratch/test_webhook_payload.py` para disparar payloads Meta simulados, assinados localmente com HMAC-SHA256, testando o webhook sem depender da aprovação da Meta.
        2. Execução de testes automatizados com `pytest` para validar o Matching Engine de similaridade por cosseno com o boost de equidade.

---

## 🛠️ 2. Gerenciamento de Credenciais de Desenvolvimento (`.env`)

Para garantir que a aplicação rode localmente sem falhas de inicialização, configuraremos o `.env` com valores seguros padrão de desenvolvimento:

*   **`SECRET_KEY`**: Gerada automaticamente via gerador seguro de 256 bits (`openssl rand -hex 32`).
*   **`DATABASE_URL`**: `postgresql+asyncpg://postgres:postgres@localhost:5432/digitalia`.
*   **`REDIS_URL`**: `redis://localhost:6379/0`.
*   **`AWS_ENDPOINT_URL`**: `http://localhost:4566` (Apontando diretamente para o LocalStack).
*   **`OPENAI_API_KEY`**: Placeholder padrão que, se vazio, aciona automaticamente nossa camada de **graceful fallback** (simulando Whisper e Assistants localmente para testes sem custo).

---

## 📂 3. Lista de Arquivos a Criar e Modificar

Todos os arquivos serão criados na pasta de trabalho de forma estruturada:

### **Fase A (Sequencial)**
*   `D:\Editais\FID\digitalia\docker-compose.yml` (Infraestrutura)
*   `D:\Editais\FID\digitalia\backend\requirements.txt` (Dependências Python)
*   `D:\Editais\FID\digitalia\.env` (Credenciais locais)
*   `D:\Editais\FID\digitalia\backend\app\models\models.py` (Schema SQLAlchemy)
*   `D:\Editais\FID\digitalia\backend\scripts\create_s3_buckets.sh` (Setup LocalStack)
*   `D:\Editais\FID\digitalia\backend\scripts\init_db.sql` (Setup DB)

### **Fase B & C (Paralelo)**
*   `D:\Editais\FID\digitalia\backend\app\services\whisper_service.py` (Whisper)
*   `D:\Editais\FID\digitalia\backend\app\api\v1\routes\webhook.py` (FastAPI Webhook)
*   `D:\Editais\FID\digitalia\backend\app\learning\assistant_factory.py` (Assistants)
*   `D:\Editais\FID\digitalia\backend\app\learning\conversation_manager.py` (Máquina de Estados)
*   `D:\Editais\FID\digitalia\backend\app\core\lgpd.py` (Criptografia AES-256-GCM)
*   `D:\Editais\FID\digitalia\backend\app\marketplace\matching_engine.py` (Matching de Equidade)
*   `D:\Editais\FID\digitalia\frontend\package.json` (Dependências do React)
*   `D:\Editais\FID\digitalia\frontend\src\components\ProgressDashboard.tsx` (UI Mobile)

### **Fase D (Integração)**
*   `D:\Editais\FID\digitalia\scratch\test_webhook_payload.py` (Simulador Meta Webhook)
*   `D:\Editais\FID\digitalia\backend\tests\test_matching_engine.py` (Testes automatizados do Matching)
