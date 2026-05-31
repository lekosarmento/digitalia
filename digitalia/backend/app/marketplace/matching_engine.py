import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any, Union, Optional

@dataclass
class MatchResult:
    project_id: str
    match_score: float              # Pontuação de 0 a 100
    match_reasons: List[str]        # Razões do match em português brasileiro coloquial e assertivo
    estimated_earnings_brl: float   # 70% do orçamento total do projeto direcionado ao aprendiz
    difficulty_match: str           # "ideal", "desafiador", "simples demais"

def get_val(obj: Any, key: str, default: Any = None) -> Any:
    """
    Função utilitária e resiliente para buscar valores em dicionários
    ou atributos em instâncias de objetos (incluindo modelos SQLAlchemy).
    """
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)

def match_learner_to_projects(
    learner: Union[Dict[str, Any], Any],
    available_projects: List[Union[Dict[str, Any], Any]],
    top_k: int = 5
) -> List[MatchResult]:
    """
    Calcula o matching ideal entre um aprendiz e uma lista de projetos disponíveis.
    Implementa similaridade de cosseno com correções de equidade social e incentivo para iniciantes.
    
    Dimensões do vetor de características (8 dimensões):
    - [0..4] Skills do perfil (social_media, design, video, automation, copywriting) / 10.0
    - [5] Horas semanais disponíveis do aprendiz vs carga necessária do projeto (normalizado)
    - [6] Projetos concluídos (experiência) normalizado
    - [7] Avaliação média (rating) normalizada
    """
    SKILL_KEYS = ["social_media", "design", "video", "automation", "copywriting"]

    # 1. Extração de informações do Aprendiz
    completed_trails = get_val(learner, "completed_trails", [])
    completed_trails_str = []
    for ct in completed_trails:
        if isinstance(ct, str):
            completed_trails_str.append(ct)
        else:
            completed_trails_str.append(get_val(ct, "trail", ""))

    current_trail = get_val(learner, "current_trail", "")
    learner_skills_raw = get_val(learner, "skills", {})
    
    # Conversão resiliente de skills do aprendiz (suporta lista de modelos ou dict)
    skills_dict = {}
    if isinstance(learner_skills_raw, dict):
        skills_dict = {k: float(v) for k, v in learner_skills_raw.items()}
    elif isinstance(learner_skills_raw, list):
        for s in learner_skills_raw:
            skills_dict[get_val(s, "skill")] = float(get_val(s, "level", 0.0))

    # Construção do vetor do Aprendiz
    learner_skill_vec = [skills_dict.get(k, 0.0) / 10.0 for k in SKILL_KEYS]
    
    hours_available = float(get_val(learner, "hours_available_weekly", 20.0) or 20.0)
    hours_val = min(hours_available, 40.0) / 40.0
    
    completed_proj = int(get_val(learner, "completed_projects", 0) or 0)
    completed_val = min(completed_proj, 20.0) / 20.0
    
    avg_r = get_val(learner, "avg_rating")
    avg_r_val = float(avg_r) / 5.0 if avg_r is not None and float(avg_r) > 0 else 0.5
    
    learner_vector = np.array(learner_skill_vec + [hours_val, completed_val, avg_r_val]).reshape(1, -1)
    learner_level = int(get_val(learner, "level", 1) or 1)

    results = []

    for project in available_projects:
        required_trail = get_val(project, "required_trail")
        
        # Filtro eliminatório de hard skills:
        # O aprendiz deve possuir a trilha concluída ou ser a sua trilha atual
        if required_trail and required_trail not in completed_trails_str + [current_trail]:
            continue

        # 2. Extração de informações do Projeto
        req_skills = get_val(project, "required_skills", {}) or {}
        project_skill_vec = [req_skills.get(k, 0.0) / 10.0 for k in SKILL_KEYS]
        
        hours_n = float(get_val(project, "hours_needed", 10.0) or 10.0)
        hours_n_val = min(hours_n, 40.0) / 40.0
        
        complexity = int(get_val(project, "complexity", 1) or 1)
        complexity_val = complexity / 10.0
        
        # Tentativa de buscar avaliação do cliente (Rating do Cliente ou da Empresa vinculada)
        client_r = get_val(project, "client_rating")
        if client_r is None:
            company = get_val(project, "company")
            if company:
                client_r = get_val(company, "avg_rating")
        
        client_r_val = float(client_r) / 5.0 if client_r is not None and float(client_r) > 0 else 0.5
        
        project_vector = np.array(project_skill_vec + [hours_n_val, complexity_val, client_r_val]).reshape(1, -1)

        # 3. Cálculo da Similaridade de Cosseno de forma resiliente
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            base_score = float(cosine_similarity(learner_vector, project_vector)[0][0])
        except ImportError:
            # Algoritmo de fallback em Numpy puro caso o scikit-learn não esteja disponível
            norm_l = np.linalg.norm(learner_vector)
            norm_p = np.linalg.norm(project_vector)
            if norm_l == 0 or norm_p == 0:
                base_score = 0.0
            else:
                base_score = float(np.dot(learner_vector, project_vector.T)[0][0] / (norm_l * norm_p))

        # 4. Princípio de Equidade & Ajustes Finos (Boosts e Penalidades)
        # Boost de 15% para primeiros projetos simples (foco em iniciantes)
        has_equity_boost = False
        if completed_proj < 3 and complexity <= 3:
            base_score += 0.15
            has_equity_boost = True

        # Boost de 10% adicional de equidade de gênero para mulheres jovens
        # IBGE 2025: mulheres de 18-29 no Nordeste têm taxa de desemprego 4pp acima dos homens (15,4% vs 11,4%)
        has_gender_boost = False
        gender = get_val(learner, "gender")
        if gender in ["feminino", "female"]:
            base_score += 0.10
            has_gender_boost = True
            
        # Penalidade de 10% se o projeto for excessivamente simples para um aprendiz muito experiente
        if completed_proj > 10 and complexity < 3:
            base_score -= 0.10

        # Garantir limite estatístico da pontuação
        base_score = max(0.0, min(1.0, base_score))
        match_score_pct = round(base_score * 100.0, 1)

        # 5. Análise de Dificuldade
        diff_gap = complexity - learner_level
        if abs(diff_gap) <= 1:
            difficulty_match = "ideal"
        elif diff_gap > 1:
            difficulty_match = "desafiador"
        else:
            difficulty_match = "simples demais"

        # 6. Geração de Razões do Match (Justificativas humanas e acolhedoras)
        reasons = []
        if required_trail:
            trail_display = required_trail.replace("_", " ").title()
            reasons.append(f"Projeto alinhado com a sua trilha de {trail_display}.")
        
        if difficulty_match == "ideal":
            reasons.append("A complexidade é ideal para o seu nível de capacitação atual.")
        elif difficulty_match == "desafiador":
            reasons.append("Este projeto trará um desafio técnico enriquecedor para acelerar seu aprendizado.")
        
        if client_r is not None and float(client_r) >= 4.5:
            reasons.append("Cliente com reputação excelente e muito acolhedor para a nossa comunidade.")
            
        if has_equity_boost:
            reasons.append("Iniciativa de Equidade: selecionado especialmente por ser perfeito para construir seu portfólio inicial.")
            
        if has_gender_boost:
            reasons.append("Iniciativa de Equidade de Gênero: bônus ativo para combater as disparidades regionais de desocupação jovem feminina [IBGE, 2025].")

        # Divisão financeira do DigitalIA: 70% da remuneração é transferida ao jovem aprendiz
        budget = float(get_val(project, "budget_brl", 0.0) or 0.0)
        estimated_earnings = budget * 0.70

        results.append(MatchResult(
            project_id=str(get_val(project, "id")),
            match_score=match_score_pct,
            match_reasons=reasons,
            estimated_earnings_brl=round(estimated_earnings, 2),
            difficulty_match=difficulty_match
        ))

    # Retorna os top-k projetos com maiores pontuações de similaridade
    return sorted(results, key=lambda x: x.match_score, reverse=True)[:top_k]
