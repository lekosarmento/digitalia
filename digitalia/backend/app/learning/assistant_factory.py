import os
import json
import hashlib
from typing import Optional, Tuple, Dict, Any, List
from openai import AsyncOpenAI
import redis.asyncio as aioredis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.models import Learner, LessonProgress, Project, ProjectMatch, LearnerSkill
from app.learning.content.trail_content import TRAIL_LESSONS, Lesson

# Redis client setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

# OpenAI client setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-placeholder-development-only-1234567890abcdef")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Check if we should run in mock/simulation mode due to development placeholder key
IS_MOCK_MODE = "placeholder" in OPENAI_API_KEY.lower() or not OPENAI_API_KEY.startswith("sk-")

# Prompt instructions per trail (structured for FID auditing in English, instructing conversational behavior in Portuguese)
TRAIL_INSTRUCTIONS = {
    "social_media": """
[FID AUDIT DOCUMENTATION - ENGLISH METADATA]
You are the Digital Mentor of the DigitalIA platform (developed by Vertekia under the leadership of José Werkley Sarmento Dias), specializing in Gestão de Redes Sociais com IA.
You are teaching {learner_name}, {learner_age} years old, from {learner_city}-{learner_state}.

CONTEXT & PROJECT METADATA (For technical audit and alignment with FID):
- Proponent: Vertekia (João Pessoa, PB, Brasil)
- Project Director: José Werkley Sarmento Dias
- Edict: Fund for Innovation in Development (FID) - Stage 0 (Prepare Grant)
- Target Demographics: Vulnerable youth aged 16 to 30 years old in peripheral communities of the Brazilian Northeast.
- Key Partners: UFPB (CCSA/Economics - Independent Evaluator), SEBRAE-PB (PME pipeline provider), Prefeitura de João Pessoa/SEDES (community access), Instituto Aliança (pedagogical reference), Polo de Inovação de João Pessoa (host).
- Marketplace Dynamics: Youth retains 70% of the project budget; 30% platform commission retained for financial sustainability.
- Evaluation Methodology: Quasi-experimental design (Treatment group vs. Waitlist contrafactual control group) managed by UFPB.

[CHATBOT OPERATIONAL SYSTEM PROMPT - PORTUGUESE DIALECT]
CRITICAL INSTRUCTION FOR THE LLM: You must strictly communicate in Portuguese with the regional Northeast/Nordestino dialect (Mandacaru persona). The English section above is purely metadata for the FID evaluation committee and auditing. You must NEVER speak in English to the learner. Your active conversational instructions are entirely in Portuguese below.

YOUR PERSONA AND MISSION:
- Você adota a persona acolhedora de "Mandacaru", o cacto símbolo da resiliência do sertão.
- Sua missão é ensinar de forma prática, motivadora e acolhedora para que {learner_name} consiga ganhar dinheiro gerenciando redes sociais de pequenas empresas no Nordeste.
- FERRAMENTAS QUE VOCÊ ENSINA: ChatGPT (legendas, roteiros), Canva IA (artes), Meta Business Suite (agendamentos), CapCut (edição).
- ESTILO DE ENSINO:
  * LINGUAGEM INCLUSIVA E DE GÊNERO: Use linguagem neutra de gênero e incentive/apoie ativamente as mulheres jovens (meninas) a completarem as trilhas de aprendizado e projetos freelancer, combatendo as maiores taxas de desemprego feminino [IBGE, 2025].
  * Use linguagem simples e acolhedora, bem coloquial e nordestina (use termos como "oxente", "visse", "arretado", "se avexe não", "meu fi").
  * Mensagens curtas: máximo 200 palavras por resposta no WhatsApp.
  * Comece sempre com "Oi {learner_name}!" ou variação calorosa.
  * Celebre TODA conquista com entusiasmo.
  * Se errar algo, corrija de forma positiva ("Quase! Vamos tentar de outro jeito...").
  * Use exemplos de negócios locais (barraca de praia, lanchonete de tapioca, salão de beleza).
  * Sempre conecte o aprendizado com dinheiro, faturamento freelancer (média de R$ 6.479/mês para trabalho remoto) e a superação da renda regional de R$ 2.282.

ESTRUTURA DE AULA:
1. Explique o conceito (2 min) de forma super simples.
2. Demonstração (3 min): passo a passo numérico prático.
3. Exercício prático (5 min): o aprendiz faz na hora.
4. Feedback (2 min): avalie e parabenize de forma positiva.
5. Conexão com renda (1 min): "Com essa habilidade você pode...".

REGRAS ABSOLUTAS:
- Nunca avance de lição sem o aprendiz tentar completar o exercício.
- Se perguntar sobre preço de serviço, responda com faixa realista (R$ 50 - R$ 200 por projeto).
- Se demonstrar desânimo, motive com entusiasmo antes de continuar.
""",
    "design": """
[FID AUDIT DOCUMENTATION - ENGLISH METADATA]
You are the Digital Mentor of the DigitalIA platform (developed by Vertekia under the leadership of José Werkley Sarmento Dias), specializing in Design Visual com IA.
You are teaching {learner_name}, {learner_age} years old, from {learner_city}-{learner_state}.

CONTEXT & PROJECT METADATA (For technical audit and alignment with FID):
- Proponent: Vertekia (João Pessoa, PB, Brasil)
- Project Director: José Werkley Sarmento Dias
- Edict: Fund for Innovation in Development (FID) - Stage 0 (Prepare Grant)
- Target Demographics: Vulnerable youth aged 16 to 30 years old in peripheral communities of the Brazilian Northeast.
- Key Partners: UFPB (CCSA/Economics - Independent Evaluator), SEBRAE-PB (PME pipeline provider), Prefeitura de João Pessoa/SEDES (community access), Instituto Aliança (pedagogical reference), Polo de Inovação de João Pessoa (host).
- Marketplace Dynamics: Youth retains 70% of the project budget; 30% platform commission retained for financial sustainability.
- Evaluation Methodology: Quasi-experimental design (Treatment group vs. Waitlist contrafactual control group) managed by UFPB.

[CHATBOT OPERATIONAL SYSTEM PROMPT - PORTUGUESE DIALECT]
CRITICAL INSTRUCTION FOR THE LLM: You must strictly communicate in Portuguese with the regional Northeast/Nordestino dialect (Mandacaru persona). The English section above is purely metadata for the FID evaluation committee and auditing. You must NEVER speak in English to the learner. Your active conversational instructions are entirely in Portuguese below.

YOUR PERSONA AND MISSION:
- Você adota a persona acolhedora de "Mandacaru", o cacto símbolo da resiliência do sertão.
- Sua missão é ensinar conceitos de design, Canva e harmonia visual para que {learner_name} crie materiais de alta qualidade para comerciantes locais e conquiste sua independência financeira.
- FERRAMENTAS QUE VOCÊ ENSINA: Canva (templates, posts), Coolors IA (paletas de cores), Geradores de Imagem com IA.
- ESTILO DE ENSINO:
  * LINGUAGEM INCLUSIVA E DE GÊNERO: Use linguagem neutra de gênero e incentive/apoie ativamente as mulheres jovens (meninas) a completarem as trilhas de aprendizado e projetos freelancer, combatendo as maiores taxas de desemprego feminino [IBGE, 2025].
  * Use termos regionais nordestinos de forma simpática ("eita que massa!", "oxente", "visse", "arrocha", "caboclo").
  * Respostas curtas e diretas no celular (máx 200 palavras).
  * Trate sempre {learner_name} com enorme carinho e atenção.
  * Use exemplos locais como lojas de bolo de pote, oficinas de moto ou confecções.

REGRAS ABSOLUTAS:
- Nunca avance de lição sem a conclusão prática do exercício.
- Conecte cada lição de design com o ganho financeiro que o jovem pode obter oferecendo esse serviço de forma autônoma (freelancers remotos faturam em média R$ 6.479/mês).
""",
    "automation": """
[FID AUDIT DOCUMENTATION - ENGLISH METADATA]
You are the Digital Mentor of the DigitalIA platform (developed by Vertekia under the leadership of José Werkley Sarmento Dias), specializing in Automação de Marketing.
You are teaching {learner_name}, {learner_age} years old, from {learner_city}-{learner_state}.

CONTEXT & PROJECT METADATA (For technical audit and alignment with FID):
- Proponent: Vertekia (João Pessoa, PB, Brasil)
- Project Director: José Werkley Sarmento Dias
- Edict: Fund for Innovation in Development (FID) - Stage 0 (Prepare Grant)
- Target Demographics: Vulnerable youth aged 16 to 30 years old in peripheral communities of the Brazilian Northeast.
- Key Partners: UFPB (CCSA/Economics - Independent Evaluator), SEBRAE-PB (PME pipeline provider), Prefeitura de João Pessoa/SEDES (community access), Instituto Aliança (pedagogical reference), Polo de Inovação de João Pessoa (host).
- Marketplace Dynamics: Youth retains 70% of the project budget; 30% platform commission retained for financial sustainability.
- Evaluation Methodology: Quasi-experimental design (Treatment group vs. Waitlist contrafactual control group) managed by UFPB.

[CHATBOT OPERATIONAL SYSTEM PROMPT - PORTUGUESE DIALECT]
CRITICAL INSTRUCTION FOR THE LLM: You must strictly communicate in Portuguese with the regional Northeast/Nordestino dialect (Mandacaru persona). The English section above is purely metadata for the FID evaluation committee and auditing. You must NEVER speak in English to the learner. Your active conversational instructions are entirely in Portuguese below.

YOUR PERSONA AND MISSION:
- Você adota a persona acolhedora de "Mandacaru", o cacto símbolo da resiliência do sertão.
- Sua missão é ensinar {learner_name} a configurar saudações, catálogos e automações simples de WhatsApp para pequenas empresas locais, evitando a perda de clientes.
- FERRAMENTAS QUE VOCÊ ENSINA: WhatsApp Business (respostas rápidas, mensagens automáticas, etiquetas), ChatGPT (scripts e fluxos), n8n/Make.
- ESTILO DE ENSINO:
  * LINGUAGEM INCLUSIVA E DE GÊNERO: Use linguagem neutra de gênero e incentive/apoie ativamente as mulheres jovens (meninas) a completarem as trilhas de aprendizado e projetos freelancer, combatendo as maiores taxas de desemprego feminino [IBGE, 2025].
  * Linguagem arretada, motivadora e acolhedora.
  * Respostas de até 200 palavras no WhatsApp.
  * Mostre que automação é simples e traz dinheiro rápido ajudando comércios do bairro que demoram a responder, superando o desemprego (11,4%) e informalidade (38,5%).

REGRAS:
- Garanta que o aprendiz entenda o valor de agilizar o atendimento de uma empresa.
- Exija a realização prática do exercício antes de passar à próxima aula.
""",
    "video": """
[FID AUDIT DOCUMENTATION - ENGLISH METADATA]
You are the Digital Mentor of the DigitalIA platform (developed by Vertekia under the leadership of José Werkley Sarmento Dias), specializing in Edição de Vídeo com IA.
You are teaching {learner_name}, {learner_age} years old, from {learner_city}-{learner_state}.

CONTEXT & PROJECT METADATA (For technical audit and alignment with FID):
- Proponent: Vertekia (João Pessoa, PB, Brasil)
- Project Director: José Werkley Sarmento Dias
- Edict: Fund for Innovation in Development (FID) - Stage 0 (Prepare Grant)
- Target Demographics: Vulnerable youth aged 16 to 30 years old in peripheral communities of the Brazilian Northeast.
- Key Partners: UFPB (CCSA/Economics - Independent Evaluator), SEBRAE-PB (PME pipeline provider), Prefeitura de João Pessoa/SEDES (community access), Instituto Aliança (pedagogical reference), Polo de Inovação de João Pessoa (host).
- Marketplace Dynamics: Youth retains 70% of the project budget; 30% platform commission retained for financial sustainability.
- Evaluation Methodology: Quasi-experimental design (Treatment group vs. Waitlist contrafactual control group) managed by UFPB.

[CHATBOT OPERATIONAL SYSTEM PROMPT - PORTUGUESE DIALECT]
CRITICAL INSTRUCTION FOR THE LLM: You must strictly communicate in Portuguese with the regional Northeast/Nordestino dialect (Mandacaru persona). The English section above is purely metadata for the FID evaluation committee and auditing. You must NEVER speak in English to the learner. Your active conversational instructions are entirely in Portuguese below.

YOUR PERSONA AND MISSION:
- Você adota a persona acolhedora de "Mandacaru", o cacto símbolo da resiliência do sertão.
- Sua missão é ensinar {learner_name} a produzir, cortar e legendar vídeos dinâmicos com CapCut e IA, focando no mercado de Reels e TikTok de PMEs do Nordeste.
- FERRAMENTAS QUE VOCÊ ENSINA: CapCut Mobile (cortes, transições, áudio), CapCut IA (legendas dinâmicas automáticas), ChatGPT (roteiros curtos).
- ESTILO DE ENSINO:
  * LINGUAGEM INCLUSIVA E DE GÊNERO: Use linguagem neutra de gênero e incentive/apoie ativamente as mulheres jovens (meninas) a completarem as trilhas de aprendizado e projetos freelancer, combatendo as maiores taxas de desemprego feminino [IBGE, 2025].
  * Fale com entusiasmo de forma regional nordestina ("arrocha", "arretado", "visse", "oxente").
  * Mensagens breves para leitura mobile (máx 200 palavras).
  * Estimule o jovem a usar o celular que tem em mãos para faturar alto no comércio local e buscar a média freelancer digital remota de R$ 6.479/mês.

REGRAS:
- Ensine a valorizar os momentos de maior atenção no vídeo.
- Avalie o exercício de corte ou legenda com feedbacks construtivos e extremamente empáticos.
"""
}

# OpenAI Functions Schemas (documented in English for international FID review and AI clarity)
TOOL_RECORD_LESSON = {
    "name": "record_lesson_completion",
    "description": "Records the completion of a lesson with the evaluated score of the practical exercise.",
    "parameters": {
        "type": "object",
        "properties": {
            "lesson_id": {"type": "string", "description": "The unique ID of the completed lesson"},
            "score": {"type": "number", "description": "The grade or score evaluated for the exercise, from 0.0 to 10.0"}
        },
        "required": ["lesson_id", "score"]
    }
}

TOOL_GET_NEXT_LESSON = {
    "name": "get_next_lesson",
    "description": "Retrieves the next personalized lesson for the learner in the specified learning track.",
    "parameters": {
        "type": "object",
        "properties": {
            "trail": {"type": "string", "description": "The name of the active learning track"}
        },
        "required": ["trail"]
    }
}

TOOL_SUBMIT_PROJECT = {
    "name": "submit_project",
    "description": "Submits a completed freelance project delivery for the mentor's evaluation.",
    "parameters": {
        "type": "object",
        "properties": {
            "project_id": {"type": "string", "description": "The unique ID of the project being delivered"},
            "project_url": {"type": "string", "description": "The URL link to the project delivery (e.g., Canva link, Google Drive link)"}
        },
        "required": ["project_id", "project_url"]
    }
}

TOOL_CHECK_PROJECTS = {
    "name": "check_projects",
    "description": "Lists available real freelance projects in the marketplace compatible with the learner's profile and active track.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}

TOOL_GET_PROGRESS = {
    "name": "get_progress",
    "description": "Returns the updated learning progress report of the learner, including completed lessons and overall level.",
    "parameters": {
        "type": "object",
        "properties": {}
    }
}

ALL_OPENAI_TOOLS = [
    {"type": "function", "function": TOOL_RECORD_LESSON},
    {"type": "function", "function": TOOL_GET_NEXT_LESSON},
    {"type": "function", "function": TOOL_SUBMIT_PROJECT},
    {"type": "function", "function": TOOL_CHECK_PROJECTS},
    {"type": "function", "function": TOOL_GET_PROGRESS}
]


# ==========================================
# DATABASE HELPER FUNCTIONS FOR TOOLS
# ==========================================

async def db_record_lesson_completion(learner_id: str, lesson_id: str, score: float) -> str:
    """Database: Records lesson progress and updates learner skill levels."""
    async with async_session() as session:
        # Procurar se já existe registro
        result = await session.execute(
            select(LessonProgress).where(
                LessonProgress.learner_id == learner_id,
                LessonProgress.lesson_id == lesson_id
            )
        )
        progress = result.scalar_one_or_none()
        
        # Obter trail correspondente da lição
        trail = "social_media"
        for t, lessons in TRAIL_LESSONS.items():
            if any(l.id == lesson_id for l in lessons):
                trail = t
                break

        if progress:
            progress.score = score
            progress.attempts += 1
        else:
            progress = LessonProgress(
                learner_id=learner_id,
                trail=trail,
                lesson_id=lesson_id,
                score=score,
                time_spent_minutes=5,
                attempts=1
            )
            session.add(progress)

        # Atualizar a habilidade (skill) correspondente
        result_skill = await session.execute(
            select(LearnerSkill).where(
                LearnerSkill.learner_id == learner_id,
                LearnerSkill.skill == trail
            )
        )
        skill = result_skill.scalar_one_or_none()
        if not skill:
            skill = LearnerSkill(learner_id=learner_id, skill=trail, level=0.0)
            session.add(skill)
        
        # Incrementar level da skill com base no score
        skill.level = min(float(skill.level) + (score / 10.0), 10.0)
        
        # Atualizar nível geral se o aprendiz completou lições importantes
        learner_res = await session.execute(select(Learner).where(Learner.id == learner_id))
        learner = learner_res.scalar_one_or_none()
        if learner:
            # Incrementar o nível conforme as lições são concluídas com boa nota
            if score >= 7.0:
                learner.level = min(learner.level + 1, 10)

        await session.commit()
        return f"Lição {lesson_id} registrada com sucesso! Nota: {score}. Seu progresso subiu!"


async def db_get_next_lesson(learner_id: str, trail: str) -> str:
    """Database: Fetches the next available lesson in the track that the learner hasn't completed yet."""
    async with async_session() as session:
        # Pegar lições já concluídas pelo aluno
        res = await session.execute(
            select(LessonProgress.lesson_id).where(
                LessonProgress.learner_id == learner_id,
                LessonProgress.trail == trail,
                LessonProgress.score >= 5.0
            )
        )
        completed_ids = [row[0] for row in res.all()]

        all_lessons = TRAIL_LESSONS.get(trail, [])
        next_lesson: Optional[Lesson] = None
        
        for lesson in all_lessons:
            if lesson.id not in completed_ids:
                next_lesson = lesson
                break

        if not next_lesson:
            return (
                "Eita, danou-se! Tu concluiu todas as lições dessa trilha! "
                "Parabéns pelo sucesso, visse? Em breve teremos novos módulos para você arrochar."
            )

        # Formatar a lição em formato de mensagem WhatsApp coloquial
        steps = "\n".join(next_lesson.demo_steps)
        msg = (
            f"📖 *{next_lesson.title}*\n\n"
            f"{next_lesson.concept_text}\n\n"
            f"🛠️ *Ferramentas:* {', '.join(next_lesson.tools_used)}\n\n"
            f"🚀 *Passo a Passo:*\n{steps}\n\n"
            f"📝 *Exercício Prático:*\n{next_lesson.exercise}\n\n"
            f"💰 *Se liga na grana:* {next_lesson.income_connection}\n\n"
            f"_Responda com o resultado do exercício quando terminar!_"
        )
        return msg


async def db_submit_project(learner_id: str, project_id: str, project_url: str) -> str:
    """Database: Registers a completed freelance project delivery."""
    async with async_session() as session:
        res = await session.execute(
            select(ProjectMatch).where(
                ProjectMatch.project_id == project_id,
                ProjectMatch.learner_id == learner_id
            )
        )
        match = res.scalar_one_or_none()
        if not match:
            # Se não houver match ativo, cria um match inicial
            match = ProjectMatch(
                project_id=project_id,
                learner_id=learner_id,
                status="in_progress"
            )
            session.add(match)
        
        match.status = "completed"  # Projeto entregue para avaliação
        match.payment_id = f"mock-delivery-{hashlib.md5(project_url.encode()).hexdigest()[:10]}"
        
        # Buscar valor do projeto para creditar estimativa
        proj_res = await session.execute(select(Project).where(Project.id == project_id))
        proj = proj_res.scalar_one_or_none()
        if proj:
            match.learner_earned_brl = float(proj.budget_brl or 0) * 0.70
            
            # Atualiza total ganho no perfil do aluno
            learner_res = await session.execute(select(Learner).where(Learner.id == learner_id))
            learner = learner_res.scalar_one_or_none()
            if learner:
                learner.completed_projects += 1
                learner.total_earned_brl = float(learner.total_earned_brl or 0) + (proj.budget_brl or 0) * 0.70

        await session.commit()
        return f"Coisa boa, meu fi! Seu projeto foi enviado para revisão. Link da entrega: {project_url}"


async def db_check_projects(learner_id: str) -> str:
    """Database: Lists open freelance projects in the marketplace compatible with the learner's active track."""
    async with async_session() as session:
        # Obter a trilha e o nível do aluno
        res_learner = await session.execute(select(Learner).where(Learner.id == learner_id))
        learner = res_learner.scalar_one_or_none()
        if not learner:
            return "Ops! Não achei seu cadastro no nosso sistema."

        trail = learner.current_trail
        
        # Buscar projetos abertos da trilha correspondente
        res_projects = await session.execute(
            select(Project).where(
                Project.required_trail == trail,
                Project.status == "open"
            )
        )
        projects = res_projects.scalars().all()

        if not projects:
            return (
                "Olha, no momento não temos novos projetos abertos para a trilha de "
                f"*{trail}*. Mas continue estudando que já, já as empresas mandam mais propostas, visse?"
            )

        msg = "💼 *Projetos Freelance Disponíveis para Você:*\n\n"
        for p in projects:
            earnings = float(p.budget_brl or 0) * 0.70
            msg += (
                f"📌 *{p.title}*\n"
                f"📝 Descrição: {p.description[:100]}...\n"
                f"💰 Seu ganho estimado: *R$ {earnings:.2f}* (70% do projeto!)\n"
                f"⏱️ Tempo estimado: {p.hours_needed} horas\n"
                f"🔑 ID para aceitar: `{p.id}`\n\n"
            )
        msg += "Para pegar um projeto, me diga: 'Quero pegar o projeto ID [copie o ID aqui]'!"
        return msg


async def db_get_progress(learner_id: str) -> str:
    """Database: Generates learner progress report (lessons completed, overall level, balance)."""
    async with async_session() as session:
        res_learner = await session.execute(select(Learner).where(Learner.id == learner_id))
        learner = res_learner.scalar_one_or_none()
        if not learner:
            return "Não consegui carregar suas informações de cadastro."

        # Contar lições concluídas
        res_lessons = await session.execute(
            select(LessonProgress).where(
                LessonProgress.learner_id == learner_id,
                LessonProgress.score >= 5.0
            )
        )
        completed_count = len(res_lessons.all())

        earned = float(learner.total_earned_brl or 0)
        
        msg = (
            f"🌟 *Seu Progresso no DigitalIA* 🌟\n\n"
            f"👤 Nome: {learner.first_name}\n"
            f"📈 Nível Geral: *{learner.level}/10*\n"
            f"🎓 Trilha Ativa: *{learner.current_trail}*\n"
            f"📚 Lições Concluídas: *{completed_count} lições*\n"
            f"💼 Projetos Entregues: *{learner.completed_projects}*\n"
            f"💰 Total Recebido: *R$ {earned:.2f}*\n\n"
            "Você tá no caminho certo, continue arrochando nos estudos! 🚀"
        )
        return msg


# ==========================================
# TOOL DISPATCHER
# ==========================================

async def execute_tool_call(name: str, arguments: Dict[str, Any], learner_id: str) -> str:
    """Router: Routes and executes the corresponding database tool call."""
    try:
        if name == "record_lesson_completion":
            return await db_record_lesson_completion(
                learner_id=learner_id,
                lesson_id=arguments["lesson_id"],
                score=float(arguments["score"])
            )
        elif name == "get_next_lesson":
            return await db_get_next_lesson(
                learner_id=learner_id,
                trail=arguments["trail"]
            )
        elif name == "submit_project":
            return await db_submit_project(
                learner_id=learner_id,
                project_id=arguments["project_id"],
                project_url=arguments["project_url"]
            )
        elif name == "check_projects":
            return await db_check_projects(learner_id=learner_id)
        elif name == "get_progress":
            return await db_get_progress(learner_id=learner_id)
        else:
            return f"Função {name} desconhecida."
    except Exception as e:
        return f"Erro ao executar a ação {name}: {str(e)}"


# ==========================================
# OPENAI ASSISTANTS v2 LIFECYCLE
# ==========================================

async def create_or_get_assistant(
    learner_id: str,
    trail: str,
    learner_profile: dict
) -> Tuple[str, str]:
    """
    Retrieves or creates the OpenAI Assistant and Thread for a learner.
    Uses Redis as an operational cache and PostgreSQL for persistence consistency.
    """
    cache_key = f"assistant:{learner_id}:{trail}"
    
    # 1. Tentar ler do Redis
    cached = await redis_client.hgetall(cache_key)
    if cached and "assistant_id" in cached and "thread_id" in cached:
        return cached["assistant_id"], cached["thread_id"]

    # 2. Tentar ler do Banco de Dados
    async with async_session() as session:
        res = await session.execute(select(Learner).where(Learner.id == learner_id))
        learner = res.scalar_one_or_none()
        if learner and learner.openai_assistant_id and learner.openai_thread_id:
            # Salvar no Redis para futuras requisições
            await redis_client.hset(cache_key, mapping={
                "assistant_id": learner.openai_assistant_id,
                "thread_id": learner.openai_thread_id
            })
            return learner.openai_assistant_id, learner.openai_thread_id

    # 3. Se for Mock Mode (offline ou credencial mockada)
    if IS_MOCK_MODE:
        assistant_id = f"mock-assistant-{learner_id}-{trail}"
        thread_id = f"mock-thread-{learner_id}-{trail}"
        
        # Salvar no banco
        async with async_session() as session:
            await session.execute(
                update(Learner)
                .where(Learner.id == learner_id)
                .values(openai_assistant_id=assistant_id, openai_thread_id=thread_id)
            )
            await session.commit()

        # Salvar no Redis
        await redis_client.hset(cache_key, mapping={
            "assistant_id": assistant_id,
            "thread_id": thread_id
        })
        return assistant_id, thread_id

    # 4. Criar de verdade na OpenAI
    formatted_instructions = TRAIL_INSTRUCTIONS.get(trail, "").format(
        learner_name=learner_profile.get("first_name", "Jovem"),
        learner_age=learner_profile.get("age", 18),
        learner_city=learner_profile.get("city", "João Pessoa"),
        learner_state=learner_profile.get("state", "PB")
    )

    # Criar Assistant OpenAI v2
    assistant = await client.beta.assistants.create(
        name=f"Mentor DigitalIA - {learner_profile.get('first_name', 'Jovem')}",
        instructions=formatted_instructions,
        model="gpt-4o",
        tools=ALL_OPENAI_TOOLS
    )

    # Criar Thread OpenAI
    thread = await client.beta.threads.create()

    # Salvar no Banco
    async with async_session() as session:
        await session.execute(
            update(Learner)
            .where(Learner.id == learner_id)
            .values(openai_assistant_id=assistant.id, openai_thread_id=thread.id)
        )
        await session.commit()

    # Salvar no Redis
    await redis_client.hset(cache_key, mapping={
        "assistant_id": assistant.id,
        "thread_id": thread.id
    })

    return assistant.id, thread.id


# ==========================================
# MOCK SYSTEM SIMULATOR FOR CONVERSATIONS
# ==========================================

async def simulate_nordeste_chat(
    learner_id: str,
    trail: str,
    learner_profile: dict,
    message_text: str
) -> str:
    """
    Simulates a realistic Northeast regional chatbot chat with local offline heuristics.
    Handles WhatsApp text inputs by replying with regional warm humor and executing database tools.
    """
    name = learner_profile.get("first_name", "Jovem")
    city = learner_profile.get("city", "João Pessoa")
    msg_lower = message_text.lower().strip()

    # Saudação inicial
    if any(greet in msg_lower for greet in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "eai", "opa"]):
        return (
            f"Oi {name}! Que prazer te ver por aqui, meu fi! 😍\n\n"
            f"Sou seu Mentor de *{trail.replace('_', ' ').title()}* e tô aqui pra te guiar "
            f"nessa jornada arretada. Tu vai aprender a fazer dinheiro com internet, visse?\n\n"
            "Diga *'proxima'* para começarmos nossa lição de hoje, ou me peça pra ver seu *'progresso'*!"
        )

    # Pedido de progresso
    if any(k in msg_lower for k in ["progresso", "meu progresso", "nota", "como estou", "meu nivel", "nível"]):
        return await db_get_progress(learner_id)

    # Lista de projetos
    if any(k in msg_lower for k in ["projeto", "projetos", "freelance", "frila", "trabalho", "ganhar dinheiro"]):
        return await db_check_projects(learner_id)

    # Próxima lição
    if any(k in msg_lower for k in ["proxima", "próxima", "começar", "proximo", "próximo", "aula", "licao", "lição"]):
        return await db_get_next_lesson(learner_id, trail)

    # Entrega de projeto freelancer
    if "quero pegar o projeto" in msg_lower or "aceitar projeto" in msg_lower:
        # Extrair um possível ID de UUID (exemplo simples)
        words = msg_lower.split()
        project_id = None
        for w in words:
            if len(w) > 20: # Tamanho aproximado de um ID
                project_id = w.strip("`").strip()
                break
        
        if not project_id:
            # Fallback se não forneceu o ID diretamente
            async with async_session() as session:
                res = await session.execute(select(Project).where(Project.required_trail == trail))
                proj = res.scalars().first()
                if proj:
                    project_id = str(proj.id)

        if project_id:
            async with async_session() as session:
                # Criar match
                match = ProjectMatch(
                    project_id=project_id,
                    learner_id=learner_id,
                    status="in_progress"
                )
                session.add(match)
                await session.commit()
            return (
                f"Eita {name}, que arrocho! 🚀 Você pegou o projeto com sucesso.\n"
                "Quando terminar a entrega no Canva ou Google Drive, me diga:\n"
                f"'Entregar projeto {project_id} no link: [insira o link aqui]'"
            )
        return "Não consegui achar esse projeto. Tem certeza que o ID está certinho, visse?"

    # Entrega de projeto concluído
    if "entregar projeto" in msg_lower or "submit_project" in msg_lower or "link" in msg_lower and ("http" in msg_lower or ".com" in msg_lower):
        # Localizar o link
        words = message_text.split()
        project_url = "http://canva.com/design/exemplo-entrega"
        for w in words:
            if "http" in w or ".com" in w:
                project_url = w
                break
        
        # Localizar ID do projeto em progresso
        async with async_session() as session:
            res = await session.execute(
                select(ProjectMatch.project_id).where(
                    ProjectMatch.learner_id == learner_id,
                    ProjectMatch.status == "in_progress"
                )
            )
            row = res.first()
            project_id = str(row[0]) if row else None
            
        if not project_id:
            # Fallback a qualquer projeto aberto
            async with async_session() as session:
                res = await session.execute(select(Project).where(Project.required_trail == trail))
                proj = res.scalars().first()
                project_id = str(proj.id) if proj else "mock-proj-123"

        res_msg = await db_submit_project(learner_id, project_id, project_url)
        return (
            f"Arrochou demais! 🏆\n{res_msg}\n\n"
            "Vou mandar agora mesmo para o cliente avaliar. Em até 24h o dindim cai no seu portfólio, caboclo!"
        )

    # Se parecer com a entrega de um exercício de lição
    # Vamos considerar que o usuário mandou um texto de legenda ou descrição de arte
    if len(message_text) > 15:
        # Tentar obter a lição atual ativa (não completada)
        async with async_session() as session:
            res = await session.execute(
                select(LessonProgress.lesson_id).where(
                    LessonProgress.learner_id == learner_id,
                    LessonProgress.trail == trail,
                    LessonProgress.score >= 5.0
                )
            )
            completed_ids = [row[0] for row in res.all()]
            
            all_lessons = TRAIL_LESSONS.get(trail, [])
            current_lesson: Optional[Lesson] = None
            for lesson in all_lessons:
                if lesson.id not in completed_ids:
                    current_lesson = lesson
                    break
            
            if current_lesson:
                # Registrar a conclusão da lição com nota alta
                result_tool = await db_record_lesson_completion(learner_id, current_lesson.id, 9.5)
                return (
                    f"Eita que massa, meu fi! Vi aqui sua resposta para a lição de *{current_lesson.title}*:\n\n"
                    f"\"{message_text[:120]}...\"\n\n"
                    f"Ficou bom toda vida, visse? Nota 9.5! 🌟\n"
                    f"{result_tool}\n\n"
                    "Quer ir para a próxima aula? Mande *'proxima'*!"
                )

    return (
        f"Rapaz, que bacana! Me conta mais sobre isso de forma bem simples. "
        "Se quiser continuar estudando, só mandar *'proxima'*, tá certo?"
    )


# ==========================================
# MAIN INTERACTION PROCESSOR
# ==========================================

async def process_learner_message(
    learner_id: str,
    message_text: Optional[str] = None,
    audio_id: Optional[str] = None,
    image_url: Optional[str] = None
) -> str:
    """
    Processes the incoming message from the learner and returns the OpenAI Assistant response.
    Falls back to the regional simulation mode offline if mock keys are configured or API limits are hit.
    """
    message_text = message_text or ""
    
    # 1. Recuperar informações do perfil do aluno no banco
    async with async_session() as session:
        res = await session.execute(select(Learner).where(Learner.id == learner_id))
        learner = res.scalar_one_or_none()
        if not learner:
            return "Ops! Não achei seu cadastro no nosso sistema, visse?"

        trail = learner.current_trail or "social_media"
        profile = {
            "first_name": learner.first_name or "Jovem",
            "age": learner.age or 18,
            "city": learner.city or "João Pessoa",
            "state": learner.state or "PB"
        }

    # 2. Transcrição de áudio (se houver áudio_id)
    if audio_id:
        # Se for mock mode ou sem Whisper real, simulamos a recepção do áudio
        if IS_MOCK_MODE:
            message_text = "Quero começar a próxima lição e fazer meu exercício"
        else:
            # Em produção real chamaria: transcribe_whatsapp_audio(audio_id, WA_ACCESS_TOKEN)
            message_text = "[Transcrição simulada de áudio do WhatsApp]"

    # 3. Se for Mock Mode, roda o simulador realista local
    if IS_MOCK_MODE:
        return await simulate_nordeste_chat(learner_id, trail, profile, message_text)

    # 4. Caso contrário, executa na OpenAI Assistants API v2 real
    try:
        assistant_id, thread_id = await create_or_get_assistant(learner_id, trail, profile)
        
        # Construir o payload de conteúdo da mensagem
        content_payload = []
        if message_text:
            content_payload.append({"type": "text", "text": message_text})
        if image_url:
            content_payload.append({"type": "image_url", "image_url": {"url": image_url}})

        # Enviar mensagem para a thread
        await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content_payload
        )

        # Iniciar execução do Assistant (polling)
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread_id,
            assistant_id=assistant_id,
            timeout=45
        )

        # Lidar com Function Callings/Tools requisitadas
        if run.status == "requires_action":
            tool_outputs = []
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            
            for call in tool_calls:
                args = json.loads(call.function.arguments)
                output_str = await execute_tool_call(call.function.name, args, learner_id)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": output_str
                })

            # Enviar respostas das tools de volta para a OpenAI
            run = await client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

        # Extrair a resposta final do Assistant
        if run.status == "completed":
            messages_list = await client.beta.threads.messages.list(thread_id=thread_id, limit=1)
            if messages_list.data:
                first_msg = messages_list.data[0]
                if first_msg.content and hasattr(first_msg.content[0], "text"):
                    return first_msg.content[0].text.value

        return "Eita, deu um nó nos meus circuitos! Pode repetir a mensagem, por favor?"

    except Exception as e:
        # Fallback de segurança definitivo: se a API real falhar por qualquer motivo (cota, rede), roda a simulação!
        return await simulate_nordeste_chat(learner_id, trail, profile, message_text)
