import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    String, Integer, Numeric, Boolean, Date, DateTime, ForeignKey, 
    Text, CHAR, LargeBinary, func, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Learner(Base):
    __tablename__ = "learners"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    phone_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    phone_encrypted: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    age: Mapped[Optional[int]] = mapped_column(
        Integer, 
        CheckConstraint("age >= 16 AND age <= 30", name="check_age_range")
    )
    gender: Mapped[Optional[str]] = mapped_column(String(30), CheckConstraint("gender IN ('masculino', 'feminino', 'não-binário', 'prefiro_não_informar')"))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(CHAR(2))
    current_trail: Mapped[Optional[str]] = mapped_column(String(50))
    current_state: Mapped[str] = mapped_column(String(50), server_default="unknown")
    openai_assistant_id: Mapped[Optional[str]] = mapped_column(String(200))
    openai_thread_id: Mapped[Optional[str]] = mapped_column(String(200))
    level: Mapped[int] = mapped_column(Integer, server_default="1")
    completed_projects: Mapped[int] = mapped_column(Integer, server_default="0")
    avg_rating: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    total_earned_brl: Mapped[float] = mapped_column(Numeric(10, 2), server_default="0.00")
    
    # LGPD compliance fields
    consent_given: Mapped[bool] = mapped_column(Boolean, server_default="FALSE")
    consent_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    parental_consent: Mapped[Optional[bool]] = mapped_column(Boolean)
    data_retention_until: Mapped[Optional[datetime.date]] = mapped_column(Date)
    
    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_active_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    anonymized_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    skills: Mapped[List["LearnerSkill"]] = relationship(back_populates="learner", cascade="all, delete-orphan")
    completed_trails: Mapped[List["CompletedTrail"]] = relationship(back_populates="learner", cascade="all, delete-orphan")
    lesson_progresses: Mapped[List["LessonProgress"]] = relationship(back_populates="learner", cascade="all, delete-orphan")
    matches: Mapped[List["ProjectMatch"]] = relationship(back_populates="learner", cascade="all, delete-orphan")
    certificates: Mapped[List["Certificate"]] = relationship(back_populates="learner", cascade="all, delete-orphan")
    conversations: Mapped[List["Conversation"]] = relationship(back_populates="learner", cascade="all, delete-orphan")


class LearnerSkill(Base):
    __tablename__ = "learner_skills"

    learner_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id", ondelete="CASCADE"), primary_key=True)
    skill: Mapped[str] = mapped_column(String(50), primary_key=True)
    level: Mapped[float] = mapped_column(Numeric(4, 1), server_default="0.0")
    last_updated: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    learner: Mapped["Learner"] = relationship(back_populates="skills")


class CompletedTrail(Base):
    __tablename__ = "completed_trails"

    learner_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id", ondelete="CASCADE"), primary_key=True)
    trail: Mapped[str] = mapped_column(String(50), primary_key=True)
    completed_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    certificate_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=True))

    # Relationships
    learner: Mapped["Learner"] = relationship(back_populates="completed_trails")


class LessonProgress(Base):
    __tablename__ = "lesson_progress"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    learner_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    trail: Mapped[Optional[str]] = mapped_column(String(50))
    lesson_id: Mapped[Optional[str]] = mapped_column(String(100))
    score: Mapped[Optional[float]] = mapped_column(Numeric(4, 1))
    time_spent_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    attempts: Mapped[int] = mapped_column(Integer, server_default="1")
    completed_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    learner: Mapped["Learner"] = relationship(back_populates="lesson_progresses")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    cnpj: Mapped[Optional[str]] = mapped_column(String(14))
    contact_name: Mapped[Optional[str]] = mapped_column(String(200))
    email: Mapped[Optional[str]] = mapped_column(String(200), unique=True)
    phone_hash: Mapped[Optional[str]] = mapped_column(String(64))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(CHAR(2))
    avg_rating: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    total_projects: Mapped[int] = mapped_column(Integer, server_default="0")
    is_verified: Mapped[bool] = mapped_column(Boolean, server_default="FALSE")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    projects: Mapped[List["Project"]] = relationship(back_populates="company", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    required_trail: Mapped[Optional[str]] = mapped_column(String(50))
    required_skills: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    complexity: Mapped[Optional[int]] = mapped_column(Integer, CheckConstraint("complexity BETWEEN 1 AND 10"))
    budget_brl: Mapped[Optional[float]] = mapped_column(Numeric(8, 2))
    hours_needed: Mapped[Optional[float]] = mapped_column(Numeric(4, 1))
    deadline_days: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), server_default="open")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    company: Mapped["Company"] = relationship(back_populates="projects")
    matches: Mapped[List["ProjectMatch"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class ProjectMatch(Base):
    __tablename__ = "project_matches"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    project_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"))
    learner_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"))
    match_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 1))
    status: Mapped[str] = mapped_column(String(20), server_default="proposed")
    learner_rating: Mapped[Optional[float]] = mapped_column(Numeric(3, 2))
    payment_id: Mapped[Optional[str]] = mapped_column(String(200))
    learner_earned_brl: Mapped[Optional[float]] = mapped_column(Numeric(8, 2))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    project: Mapped["Project"] = relationship(back_populates="matches")
    learner: Mapped["Learner"] = relationship(back_populates="matches")


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    learner_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"))
    trail: Mapped[Optional[str]] = mapped_column(String(50))
    level: Mapped[Optional[int]] = mapped_column(Integer, CheckConstraint("level BETWEEN 1 AND 3"))
    tx_hash: Mapped[Optional[str]] = mapped_column(String(200))
    contract_address: Mapped[Optional[str]] = mapped_column(String(200))
    token_id: Mapped[Optional[int]] = mapped_column(Integer)
    issued_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    metadata_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Relationships
    learner: Mapped["Learner"] = relationship(back_populates="certificates")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    learner_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    wa_message_id: Mapped[Optional[str]] = mapped_column(String(200))
    direction: Mapped[Optional[str]] = mapped_column(String(10), CheckConstraint("direction IN ('inbound', 'outbound')"))
    content_type: Mapped[str] = mapped_column(String(20), server_default="text")
    content_encrypted: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    openai_thread_id: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    learner: Mapped["Learner"] = relationship(back_populates="conversations")
