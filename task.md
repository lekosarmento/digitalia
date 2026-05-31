# Checklist de Execução — DigitalIA

- `[ ]` uncompleted tasks
- `[/]` in progress tasks
- `[x]` completed tasks

## Fase A: Sequencial - Banco de Dados, Docker e Migrations [x]
- [x] Criar docker-compose.yml com Postgres 16, Redis 7.2, LocalStack e Celery
- [x] Criar backend/requirements.txt com dependências fixadas
- [x] Criar .env com credenciais de desenvolvimento locais e chaves seguras
- [x] Criar backend/scripts/create_s3_buckets.sh para auto-inicializar o LocalStack
- [x] Criar backend/scripts/init_db.sql para preparar extensões do Postgres
- [x] Criar backend/app/models/models.py com schema SQLAlchemy completo
- [x] Inicializar e rodar migrations com Alembic

## Fase B: Paralelo - Core Backend, IA Engine, Segurança [x]
- [x] Implementar Agente 2 (Core Backend: FastAPI, webhook, Whisper, S3)
- [x] Implementar Agente 3 (IA Engine: Assistants API v2, State Machine, image fallback)
- [x] Implementar Agente 4 (Segurança: LGPD, AES-256-GCM, menor consentimento, JWT)

## Fase C: Paralelo - Frontend Dashboard [x]
- [x] Implementar Agente 5 (Frontend React/Vite/TS/Tailwind com endpoints alinhados e HMAC)

## Fase D: Sequencial - Integração & Testes [x]
- [x] Criar script test_webhook_payload.py para simulação de WhatsApp HMAC
- [x] Criar test_matching_engine.py para testes unitários de similaridade e equidade
- [x] Resolver conflitos de interface e rodar testes de integração
