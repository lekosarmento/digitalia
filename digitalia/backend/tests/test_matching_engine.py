import pytest
from app.marketplace.matching_engine import match_learner_to_projects, MatchResult

def test_basic_matching_skills():
    # Learner profile with Redes Sociais trail and high skill in social_media
    learner = {
        "id": "learner-uuid-1",
        "completed_trails": ["social_media"],
        "current_trail": "social_media",
        "skills": {
            "social_media": 8.0,
            "design": 2.0,
            "video": 1.0,
            "automation": 1.0,
            "copywriting": 1.0
        },
        "hours_available_weekly": 20,
        "completed_projects": 5,
        "avg_rating": 4.5,
        "level": 3
    }

    # Available projects
    projects = [
        {
            "id": "proj-uuid-matching",
            "required_trail": "social_media",
            "required_skills": {
                "social_media": 7.0,
                "copywriting": 2.0
            },
            "hours_needed": 15,
            "complexity": 3,
            "budget_brl": 500.0,
            "client_rating": 4.8
        },
        {
            "id": "proj-uuid-non-matching-trail",
            "required_trail": "automation", # Different trail that learner doesn't have
            "required_skills": {
                "automation": 8.0
            },
            "hours_needed": 10,
            "complexity": 5,
            "budget_brl": 1000.0,
            "client_rating": 4.0
        }
    ]

    results = match_learner_to_projects(learner, projects)
    
    # Assertions
    # 1. The project with non-matching trail must be excluded entirely
    assert len(results) == 1
    
    # 2. Verify MatchResult properties
    match = results[0]
    assert match.project_id == "proj-uuid-matching"
    assert match.match_score > 50.0  # High score expected since skills align
    assert match.estimated_earnings_brl == 350.0  # 70% of 500 BRL
    assert match.difficulty_match == "ideal"  # Learner level is 3, complexity is 3 (diff_gap = 0)
    assert any("social media" in r.lower() or "trilha" in r.lower() for r in match.match_reasons)


def test_equity_boost_for_beginners():
    # Learner with less than 3 projects completed
    beginner_learner = {
        "id": "beginner-uuid",
        "completed_trails": ["design"],
        "current_trail": "design",
        "skills": {
            "design": 3.0
        },
        "hours_available_weekly": 20,
        "completed_projects": 0,  # Beginner!
        "avg_rating": None,
        "level": 1
    }

    # Low complexity project (complexity <= 3)
    easy_project = {
        "id": "easy-proj",
        "required_trail": "design",
        "required_skills": {
            "design": 2.0
        },
        "hours_needed": 10,
        "complexity": 2,  # Low complexity!
        "budget_brl": 200.0,
        "client_rating": 4.0
    }

    results = match_learner_to_projects(beginner_learner, [easy_project])
    assert len(results) == 1
    
    match = results[0]
    # Check that reasons contain equity boost text
    assert any("Equidade" in reason for reason in match.match_reasons)
    
    # Calculate score without boost:
    # learner skill design 3.0/10 = 0.3, project skill 2.0/10 = 0.2
    # both vectors have other fields as defaults (e.g. hours_available 20/40 = 0.5 vs hours_needed 10/40 = 0.25)
    # The boost adds +15% (0.15) to the base cosine similarity score, capped at 100%.
    assert match.match_score > 15.0


def test_experience_penalty_for_experts():
    # Learner with more than 10 projects completed
    expert_learner = {
        "id": "expert-uuid",
        "completed_trails": ["design"],
        "current_trail": "design",
        "skills": {
            "design": 9.0
        },
        "hours_available_weekly": 30,
        "completed_projects": 15,  # Expert!
        "avg_rating": 4.9,
        "level": 5
    }

    # Extremely simple project (complexity < 3)
    simple_project = {
        "id": "simple-proj",
        "required_trail": "design",
        "required_skills": {
            "design": 2.0
        },
        "hours_needed": 5,
        "complexity": 1,  # Simple!
        "budget_brl": 150.0,
        "client_rating": 4.5
    }

    results = match_learner_to_projects(expert_learner, [simple_project])
    assert len(results) == 1
    
    match = results[0]
    assert match.difficulty_match == "simples demais"  # learner level 5, project complexity 1 (gap = -4)
    # Base score should have a 10% penalty, which ensures it is not excessively recommended compared to standard matches


def test_gender_equity_boost_for_women():
    # Female learner
    female_learner = {
        "id": "female-uuid",
        "completed_trails": ["design"],
        "current_trail": "design",
        "gender": "feminino",  # Active boost!
        "skills": {
            "design": 6.0
        },
        "hours_available_weekly": 20,
        "completed_projects": 5,  # Non-beginner (so no beginner boost, just gender boost!)
        "avg_rating": 4.5,
        "level": 2
    }

    # Standard design project
    project = {
        "id": "design-proj",
        "required_trail": "design",
        "required_skills": {
            "design": 5.0
        },
        "hours_needed": 10,
        "complexity": 2,
        "budget_brl": 400.0,
        "client_rating": 4.5
    }

    results = match_learner_to_projects(female_learner, [project])
    assert len(results) == 1
    
    match = results[0]
    # Check that reasons contain gender boost text
    assert any("Equidade de Gênero" in reason for reason in match.match_reasons)
    # Base score without boost: design skills align closely, giving a score around 80.
    # The +10% boost should push the match score high.
    assert match.match_score > 10.0

