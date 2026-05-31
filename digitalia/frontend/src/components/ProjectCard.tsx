import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Briefcase, DollarSign, Calendar, Clock, BarChart3, 
  CheckCircle2, Sparkles, Building2, ShieldCheck, ArrowRight, X
} from 'lucide-react';
import { Project } from '../services/api';

interface ProjectCardProps {
  project: Project;
  learnerSkills: { skill: string; level: number }[];
  onApply: (projectId: string) => Promise<void>;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ project, learnerSkills, onApply }) => {
  const [isApplying, setIsApplying] = useState(false);
  const [isApplied, setIsApplied] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  // Calculate matching score based on required skills vs learner skills
  const calculateMatch = () => {
    let matchedCount = 0;
    let totalScore = 0;
    const reqSkills = Object.entries(project.required_skills);
    
    if (reqSkills.length === 0) return 100;

    reqSkills.forEach(([skill, reqLevel]) => {
      const learnerSkill = learnerSkills.find(s => s.skill.toLowerCase() === skill.toLowerCase());
      if (learnerSkill) {
        matchedCount++;
        // If learner's skill level is >= required level, add full point, otherwise proportional
        const skillRatio = Math.min(learnerSkill.level / reqLevel, 1.2); 
        totalScore += skillRatio;
      }
    });

    const skillMatchRatio = reqSkills.length > 0 ? (matchedCount / reqSkills.length) : 0;
    const levelMatchRatio = matchedCount > 0 ? (totalScore / matchedCount) : 0;
    
    // Weighted match: 60% skills presence, 40% proficiency matching
    const finalScore = Math.round(((skillMatchRatio * 0.6) + (levelMatchRatio * 0.4)) * 100);
    return Math.min(finalScore, 100);
  };

  const matchScore = calculateMatch();
  
  // Custom colors based on match rating
  const getMatchColor = (score: number) => {
    if (score >= 85) return 'from-brand-emerald-glow to-brand-cyan-glow text-brand-emerald-glow border-brand-emerald-neon/30';
    if (score >= 60) return 'from-brand-purple-glow to-brand-cyan-glow text-brand-cyan-glow border-brand-cyan-neon/30';
    return 'from-brand-amber-glow to-brand-rose-glow text-brand-amber-glow border-brand-amber-neon/30';
  };

  const handleApplyClick = async () => {
    setIsApplying(true);
    // Simulate API delay for match submisson
    await new Promise(resolve => setTimeout(resolve, 1500));
    await onApply(project.id);
    setIsApplying(false);
    setIsApplied(true);
  };

  return (
    <>
      <motion.div 
        layout
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -15 }}
        whileHover={{ y: -4 }}
        className="glass-card rounded-2xl overflow-hidden glass-card-hover border border-white/5 shadow-glass flex flex-col h-full relative"
      >
        {/* Match Percentage Top Badge */}
        <div className="absolute top-4 right-4 z-10">
          <div className="px-3 py-1.5 rounded-full text-xs font-bold font-mono tracking-wider glass-card border flex items-center gap-1.5 shadow-lg bg-black/60">
            <Sparkles className="w-3 h-3 text-brand-cyan-glow animate-pulse" />
            <span>Match:</span>
            <span className={`bg-gradient-to-r ${getMatchColor(matchScore)} bg-clip-text text-transparent`}>
              {matchScore}%
            </span>
          </div>
        </div>

        <div className="p-6 flex-grow">
          {/* Company and Verification */}
          <div className="flex items-center gap-2 mb-3 text-brand-slate-400 text-xs">
            <div className="p-1 rounded-md bg-brand-slate-900 border border-white/5">
              <Building2 className="w-3.5 h-3.5 text-brand-purple-glow" />
            </div>
            <span className="font-semibold text-brand-slate-200">{project.company.company_name}</span>
            {project.company.is_verified && (
              <ShieldCheck className="w-4 h-4 text-brand-cyan-glow" title="Empresa Verificada" />
            )}
            <span className="ml-auto text-brand-slate-400 font-mono text-[10px]">
              ★ {project.company.avg_rating.toFixed(1)}
            </span>
          </div>

          {/* Project Title */}
          <h3 className="text-lg font-bold text-white leading-snug mb-3 pr-20 group-hover:text-brand-purple-glow transition-colors">
            {project.title}
          </h3>

          {/* Project Description (Truncated) */}
          <p className="text-brand-slate-400 text-xs leading-relaxed mb-5 line-clamp-3">
            {project.description}
          </p>

          {/* Required Skills Badges */}
          <div className="mb-6">
            <span className="text-[10px] uppercase font-bold tracking-wider text-brand-slate-400 block mb-2">Habilidades Requeridas</span>
            <div className="flex flex-wrap gap-1.5">
              {Object.entries(project.required_skills).map(([skill, level]) => {
                const hasSkill = learnerSkills.some(s => s.skill.toLowerCase() === skill.toLowerCase());
                return (
                  <span 
                    key={skill} 
                    className={`text-[10px] font-mono px-2 py-1 rounded-md border ${
                      hasSkill 
                        ? 'bg-brand-purple-deep/40 text-brand-purple-glow border-brand-purple-neon/20' 
                        : 'bg-brand-slate-950 text-brand-slate-400 border-white/5'
                    }`}
                  >
                    {skill} (Nível {level.toFixed(0)})
                  </span>
                );
              })}
            </div>
          </div>

          {/* Financials & Timeline Info */}
          <div className="grid grid-cols-2 gap-3 p-3.5 rounded-xl bg-brand-abyss/60 border border-white/5">
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-brand-emerald-deep/40 border border-brand-emerald-neon/15">
                <DollarSign className="w-3.5 h-3.5 text-brand-emerald-glow" />
              </div>
              <div>
                <span className="text-[9px] text-brand-slate-400 block uppercase font-semibold">Orçamento</span>
                <span className="text-xs font-bold text-brand-emerald-glow font-mono">
                  R$ {project.budget_brl.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-brand-cyan-deep/40 border border-brand-cyan-neon/15">
                <Calendar className="w-3.5 h-3.5 text-brand-cyan-glow" />
              </div>
              <div>
                <span className="text-[9px] text-brand-slate-400 block uppercase font-semibold">Prazo Máximo</span>
                <span className="text-xs font-bold text-white font-mono">{project.deadline_days} dias</span>
              </div>
            </div>

            <div className="flex items-center gap-2 mt-1">
              <div className="p-1.5 rounded-lg bg-brand-purple-deep/40 border border-brand-purple-neon/15">
                <Clock className="w-3.5 h-3.5 text-brand-purple-glow" />
              </div>
              <div>
                <span className="text-[9px] text-brand-slate-400 block uppercase font-semibold">Dedicação</span>
                <span className="text-xs font-bold text-brand-slate-200 font-mono">{project.hours_needed} horas</span>
              </div>
            </div>

            <div className="flex items-center gap-2 mt-1">
              <div className="p-1.5 rounded-lg bg-brand-slate-900 border border-white/5">
                <BarChart3 className="w-3.5 h-3.5 text-brand-slate-400" />
              </div>
              <div>
                <span className="text-[9px] text-brand-slate-400 block uppercase font-semibold">Complexidade</span>
                <span className="text-xs font-bold text-white font-mono">{project.complexity}/10</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-5 pt-0 border-t border-white/5 bg-brand-slate-950/20 flex gap-2">
          <button 
            onClick={() => setShowDetails(true)}
            className="flex-1 py-2 px-3 rounded-xl border border-white/10 hover:border-white/20 text-xs font-medium text-brand-slate-200 hover:text-white transition-all text-center"
          >
            Detalhes
          </button>
          
          <button 
            disabled={isApplying || isApplied}
            onClick={handleApplyClick}
            className={`flex-1 py-2 px-3 rounded-xl font-semibold text-xs transition-all duration-300 flex items-center justify-center gap-1.5 shadow-md ${
              isApplied
                ? 'bg-brand-emerald-deep border border-brand-emerald-neon/30 text-brand-emerald-glow'
                : 'bg-gradient-to-r from-brand-purple-neon to-brand-cyan-neon hover:from-brand-purple-glow hover:to-brand-cyan-glow text-white hover:shadow-glass-glow-purple'
            }`}
          >
            {isApplying ? (
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : isApplied ? (
              <>
                <CheckCircle2 className="w-3.5 h-3.5" />
                Candidatado
              </>
            ) : (
              <>
                Match Rápido
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>
      </motion.div>

      {/* Project Details Modal */}
      <AnimatePresence>
        {showDetails && (
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
            {/* Backdrop */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowDetails(false)}
              className="absolute inset-0 bg-brand-abyss/85 backdrop-blur-md"
            />
            
            {/* Modal Box */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="glass-card w-full max-w-lg rounded-2xl overflow-hidden border border-white/10 shadow-2xl relative z-10 max-h-[85vh] flex flex-col"
            >
              {/* Header */}
              <div className="p-6 pb-4 border-b border-white/5 flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2 text-xs text-brand-slate-400">
                    <span className="font-semibold text-brand-slate-200">{project.company.company_name}</span>
                    {project.company.is_verified && <ShieldCheck className="w-3.5 h-3.5 text-brand-cyan-glow" />}
                    <span>• {project.company.city}, {project.company.state}</span>
                  </div>
                  <h2 className="text-xl font-bold text-white leading-tight">
                    {project.title}
                  </h2>
                </div>
                <button 
                  onClick={() => setShowDetails(false)}
                  className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/5 text-brand-slate-400 hover:text-white transition-all ml-4"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Content Body (Scrollable) */}
              <div className="p-6 overflow-y-auto space-y-5 flex-grow">
                {/* Description */}
                <div>
                  <h4 className="text-xs uppercase font-bold text-brand-slate-400 tracking-wider mb-2">Descrição do Projeto</h4>
                  <p className="text-brand-slate-300 text-sm leading-relaxed whitespace-pre-line">
                    {project.description}
                  </p>
                </div>

                {/* Requirements & Matching Metas */}
                <div className="p-4 rounded-xl bg-brand-slate-900/40 border border-white/5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-brand-slate-400 font-medium">Afinidade Geral</span>
                    <span className={`text-sm font-bold bg-gradient-to-r ${getMatchColor(matchScore)} bg-clip-text text-transparent`}>
                      {matchScore}% Compatível
                    </span>
                  </div>
                  <div className="w-full bg-brand-slate-950 h-2 rounded-full overflow-hidden border border-white/5">
                    <div 
                      className={`h-full bg-gradient-to-r ${
                        matchScore >= 85 
                          ? 'from-brand-emerald-neon to-brand-cyan-neon' 
                          : 'from-brand-purple-neon to-brand-cyan-neon'
                      }`}
                      style={{ width: `${matchScore}%` }}
                    />
                  </div>
                  <p className="text-[11px] text-brand-slate-400 leading-normal">
                    Este score representa a convergência entre suas habilidades atuais registradas e as especificações técnicas da vaga de trabalho sob demanda.
                  </p>
                </div>

                {/* Details Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3.5 rounded-xl bg-brand-abyss border border-white/5">
                    <span className="text-[10px] text-brand-slate-400 uppercase font-semibold block mb-1">Pagamento (PIX/BRL)</span>
                    <span className="text-base font-bold text-brand-emerald-glow font-mono">
                      R$ {project.budget_brl.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-brand-abyss border border-white/5">
                    <span className="text-[10px] text-brand-slate-400 uppercase font-semibold block mb-1">Prazo de Entrega</span>
                    <span className="text-base font-bold text-white font-mono">{project.deadline_days} dias</span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-brand-abyss border border-white/5">
                    <span className="text-[10px] text-brand-slate-400 uppercase font-semibold block mb-1">Tempo Estimado</span>
                    <span className="text-base font-bold text-white font-mono">{project.hours_needed} horas</span>
                  </div>
                  <div className="p-3.5 rounded-xl bg-brand-abyss border border-white/5">
                    <span className="text-[10px] text-brand-slate-400 uppercase font-semibold block mb-1">Nível Mínimo do Learner</span>
                    <span className="text-base font-bold text-brand-purple-glow font-mono">Lvl 2+</span>
                  </div>
                </div>

                {/* Skills Analysis */}
                <div>
                  <h4 className="text-xs uppercase font-bold text-brand-slate-400 tracking-wider mb-2.5">Habilidades Comparativas</h4>
                  <div className="space-y-2">
                    {Object.entries(project.required_skills).map(([skill, reqLevel]) => {
                      const learnerSkill = learnerSkills.find(s => s.skill.toLowerCase() === skill.toLowerCase());
                      const hasSkill = !!learnerSkill;
                      const levelDiff = hasSkill ? (learnerSkill.level - reqLevel) : -reqLevel;
                      
                      return (
                        <div key={skill} className="flex items-center justify-between text-xs py-1.5 border-b border-white/5">
                          <span className="font-mono text-brand-slate-200">{skill}</span>
                          <div className="flex items-center gap-3">
                            <span className="text-brand-slate-400">Requerido: {reqLevel.toFixed(0)}</span>
                            <span className={hasSkill ? 'text-brand-purple-glow font-semibold' : 'text-brand-rose-glow font-medium'}>
                              Seu nível: {hasSkill ? learnerSkill.level.toFixed(1) : 'Não possui'}
                            </span>
                            <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono ${
                              levelDiff >= 0 
                                ? 'bg-brand-emerald-deep/40 text-brand-emerald-glow' 
                                : 'bg-brand-rose-deep/40 text-brand-rose-glow'
                            }`}>
                              {levelDiff >= 0 ? `+${levelDiff.toFixed(1)}` : levelDiff.toFixed(1)}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="p-6 border-t border-white/5 bg-brand-slate-950/40 flex gap-3">
                <button 
                  onClick={() => setShowDetails(false)}
                  className="flex-1 py-3 px-4 rounded-xl border border-white/10 hover:border-white/20 text-xs font-semibold text-brand-slate-200 transition-all"
                >
                  Voltar
                </button>
                
                <button 
                  disabled={isApplying || isApplied}
                  onClick={handleApplyClick}
                  className={`flex-[2] py-3 px-4 rounded-xl font-semibold text-xs transition-all duration-300 flex items-center justify-center gap-2 shadow-lg ${
                    isApplied
                      ? 'bg-brand-emerald-deep border border-brand-emerald-neon/30 text-brand-emerald-glow'
                      : 'bg-gradient-to-r from-brand-purple-neon to-brand-cyan-neon hover:from-brand-purple-glow hover:to-brand-cyan-glow text-white'
                  }`}
                >
                  {isApplying ? (
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : isApplied ? (
                    <>
                      <CheckCircle2 className="w-4 h-4" />
                      Candidatura Confirmada
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 text-white animate-pulse" />
                      Aceitar Proposta de Match
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};
