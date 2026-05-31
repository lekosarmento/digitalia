import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Award, ShieldCheck, MapPin, Share2, Copy, Check, ExternalLink, 
  ArrowLeft, Cpu, Sparkles, Star, Rocket, CheckCircle, Code2, HeartHandshake
} from 'lucide-react';
import { LearnerData } from '../services/api';

interface PortfolioViewProps {
  learnerData: LearnerData;
  onBackToDashboard?: () => void;
}

export const PortfolioView: React.FC<PortfolioViewProps> = ({ learnerData, onBackToDashboard }) => {
  const [copied, setCopied] = useState(false);

  const handleShare = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getLevelBadge = (level: number) => {
    switch (level) {
      case 1: return { name: 'Bronze Practitioner', color: 'from-amber-600 to-amber-700 text-amber-100' };
      case 2: return { name: 'Silver Architect', color: 'from-slate-400 to-slate-500 text-slate-100' };
      case 3: return { name: 'Gold Specialist', color: 'from-brand-purple-neon to-brand-cyan-neon text-white font-semibold' };
      default: return { name: 'Elite Champion', color: 'from-brand-emerald-neon to-brand-cyan-neon text-white' };
    }
  };

  const badge = getLevelBadge(learnerData.level);

  return (
    <div className="min-h-screen bg-brand-abyss text-slate-100 relative py-12 px-4 md:px-8">
      {/* Background Radial Lights */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-brand-purple-neon/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-brand-cyan-neon/5 rounded-full blur-[120px] pointer-events-none" />

      {/* Main Container */}
      <div className="max-w-4xl mx-auto space-y-8 relative">
        {/* Nav Back Header (Conditional) */}
        {onBackToDashboard && (
          <motion.button 
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            onClick={onBackToDashboard}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/5 text-xs text-brand-slate-400 hover:text-white transition-all"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar ao Dashboard
          </motion.button>
        )}

        {/* Portfolio Card Wrapper */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="glass-card rounded-3xl overflow-hidden border border-white/10 shadow-2xl relative"
        >
          {/* Cover Header Image Background Gradient */}
          <div className="h-44 bg-gradient-to-r from-brand-purple-deep via-brand-slate-900 to-brand-cyan-deep relative flex items-end">
            <div className="absolute inset-0 bg-black/40" />
            <div className="absolute top-4 right-4 flex gap-2">
              <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold tracking-widest uppercase bg-black/60 border border-brand-cyan-neon/20 text-brand-cyan-glow flex items-center gap-1.5">
                <Cpu className="w-3 h-3 text-brand-cyan-glow animate-pulse" />
                Validado via Blockchain
              </span>
            </div>
          </div>

          {/* Profile Details Block */}
          <div className="px-6 md:px-10 pb-8 relative">
            {/* Profile Avatar Grid */}
            <div className="flex flex-col md:flex-row items-center md:items-end -mt-16 mb-6 gap-6">
              {/* Animated Avatar Circle with Initials */}
              <div className="w-28 h-28 rounded-2xl bg-gradient-to-tr from-brand-purple-neon to-brand-cyan-neon p-[3px] shadow-2xl relative">
                <div className="w-full h-full rounded-[21px] bg-brand-obsidian flex items-center justify-center text-3xl font-extrabold text-white">
                  {learnerData.first_name.split(' ').map(n => n[0]).join('')}
                </div>
                <div className="absolute -bottom-1.5 -right-1.5 p-1 rounded-lg bg-brand-cyan-neon text-brand-abyss shadow-lg border border-brand-obsidian">
                  <ShieldCheck className="w-4 h-4 text-brand-abyss fill-brand-abyss" />
                </div>
              </div>

              {/* Text Info */}
              <div className="text-center md:text-left flex-grow space-y-1">
                <div className="flex flex-col md:flex-row items-center gap-2.5">
                  <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                    {learnerData.first_name}
                  </h1>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] uppercase font-bold tracking-wider bg-gradient-to-r ${badge.color}`}>
                    {badge.name}
                  </span>
                </div>

                <div className="flex flex-wrap justify-center md:justify-start items-center gap-x-4 gap-y-1.5 text-xs text-brand-slate-400">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-brand-cyan-glow" />
                    {learnerData.city}, {learnerData.state}
                  </span>
                  <span>•</span>
                  <span>{learnerData.age} anos</span>
                  <span>•</span>
                  <span className="text-brand-purple-glow font-medium">{learnerData.current_trail}</span>
                </div>
              </div>

              {/* Share/Connect Buttons */}
              <div className="flex gap-2 w-full md:w-auto mt-4 md:mt-0">
                <button 
                  onClick={handleShare}
                  className="flex-1 md:flex-none py-2.5 px-4 rounded-xl border border-white/10 hover:border-white/20 text-xs font-semibold text-brand-slate-200 hover:text-white transition-all flex items-center justify-center gap-2 bg-brand-slate-900/50"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4 text-brand-emerald-glow" />
                      Copiado!
                    </>
                  ) : (
                    <>
                      <Share2 className="w-4 h-4 text-brand-slate-400" />
                      Compartilhar
                    </>
                  )}
                </button>
                <a
                  href={`https://wa.me/558199999999?text=Olá%20${encodeURIComponent(learnerData.first_name)},%20vi%20seu%20portfólio%20na%20DigitalIA%20e%20gostaria%20de%20conversar.`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 md:flex-none py-2.5 px-5 rounded-xl bg-gradient-to-r from-brand-purple-neon to-brand-cyan-neon hover:from-brand-purple-glow hover:to-brand-cyan-glow text-white text-xs font-semibold hover:shadow-glass-glow-purple transition-all flex items-center justify-center gap-2"
                >
                  <HeartHandshake className="w-4 h-4" />
                  Contratar
                </a>
              </div>
            </div>

            {/* Quick Metrics Bar */}
            <div className="grid grid-cols-3 gap-3 p-4 rounded-2xl bg-brand-slate-900/30 border border-white/5 mb-8 text-center">
              <div>
                <span className="text-[10px] text-brand-slate-400 uppercase font-semibold block mb-0.5">Nível</span>
                <span className="text-lg font-bold text-white tracking-wide">
                  Lvl {learnerData.level}
                </span>
              </div>
              <div className="border-x border-white/5">
                <span className="text-[10px] text-brand-slate-400 uppercase font-semibold block mb-0.5">Jobs Concluídos</span>
                <span className="text-lg font-bold text-brand-emerald-glow font-mono">
                  {learnerData.completed_projects}
                </span>
              </div>
              <div>
                <span className="text-[10px] text-brand-slate-400 uppercase font-semibold block mb-0.5">Score de Avaliação</span>
                <span className="text-lg font-bold text-brand-amber-glow font-mono flex items-center justify-center gap-1">
                  ★ {learnerData.avg_rating.toFixed(2)}
                </span>
              </div>
            </div>

            {/* Grid Layout Content */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* Left Column: Skills list */}
              <div className="md:col-span-1 space-y-6">
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-brand-slate-200 mb-4 flex items-center gap-2">
                    <Code2 className="w-4 h-4 text-brand-purple-glow" />
                    Skills Autênticas
                  </h3>
                  
                  <div className="space-y-4">
                    {learnerData.skills.map((skill) => (
                      <div key={skill.skill} className="space-y-1.5">
                        <div className="flex justify-between text-xs">
                          <span className="font-mono text-brand-slate-200">{skill.skill}</span>
                          <span className="text-brand-purple-glow font-semibold">{skill.level.toFixed(1)}/10</span>
                        </div>
                        <div className="w-full bg-brand-slate-950 h-1.5 rounded-full overflow-hidden border border-white/5">
                          <div 
                            className="h-full bg-gradient-to-r from-brand-purple-neon to-brand-cyan-neon"
                            style={{ width: `${skill.level * 10}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <hr className="border-white/5" />

                {/* Verification block */}
                <div className="p-4 rounded-xl bg-brand-purple-deep/10 border border-brand-purple-neon/20 space-y-2">
                  <div className="flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-brand-purple-glow" />
                    <span className="text-xs font-bold text-brand-purple-glow uppercase tracking-wider">Garantia DigitalIA</span>
                  </div>
                  <p className="text-[11px] text-brand-slate-400 leading-relaxed">
                    Todas as habilidades expostas acima foram atestadas por avaliações práticas automatizadas, corrigidas pela IA e validadas por empresas reais parceiras do DigitalIA.
                  </p>
                </div>
              </div>

              {/* Right Column: Certificates and History */}
              <div className="md:col-span-2 space-y-6">
                {/* Certificates Block */}
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-brand-slate-200 mb-4 flex items-center gap-2">
                    <Award className="w-4 h-4 text-brand-cyan-glow" />
                    Certificados em Blockchain (NFTs)
                  </h3>

                  <div className="space-y-4">
                    {learnerData.certificates.map((cert) => (
                      <div 
                        key={cert.id}
                        className="p-4 rounded-xl bg-brand-slate-950 border border-white/5 hover:border-brand-cyan-neon/30 transition-all flex flex-col gap-3 group relative overflow-hidden"
                      >
                        <div className="absolute top-0 right-0 w-24 h-24 bg-brand-cyan-neon/5 rounded-full blur-xl pointer-events-none group-hover:bg-brand-cyan-neon/10 transition-all" />
                        
                        <div className="flex justify-between items-start gap-4">
                          <div>
                            <span className="text-[9px] uppercase font-bold tracking-widest text-brand-cyan-glow bg-brand-cyan-deep/40 px-2 py-0.5 rounded border border-brand-cyan-neon/20">
                              Nível {cert.level}
                            </span>
                            <h4 className="text-sm font-bold text-white mt-1 group-hover:text-brand-cyan-glow transition-colors">
                              {cert.trail}
                            </h4>
                            <p className="text-[10px] text-brand-slate-400 mt-0.5">
                              Emitido em {new Date(cert.issued_at).toLocaleDateString('pt-BR')}
                            </p>
                          </div>
                          
                          <Award className="w-8 h-8 text-brand-cyan-glow opacity-80 group-hover:scale-110 transition-transform" />
                        </div>

                        {/* Tx Info and Blockchain Details */}
                        <div className="pt-2 border-t border-white/5 flex flex-col gap-1.5 text-[10px] font-mono text-brand-slate-400">
                          <div className="flex items-center justify-between">
                            <span>Hash Transação:</span>
                            <span className="text-brand-slate-200 truncate max-w-[200px]" title={cert.tx_hash}>
                              {cert.tx_hash.slice(0, 10)}...{cert.tx_hash.slice(-10)}
                            </span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span>Smart Contract:</span>
                            <span className="text-brand-slate-200 truncate max-w-[200px]" title={cert.contract_address}>
                              {cert.contract_address.slice(0, 8)}...{cert.contract_address.slice(-8)}
                            </span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span>Token ID:</span>
                            <span className="text-brand-cyan-glow font-bold">
                              #{cert.token_id} (ERC-721)
                            </span>
                          </div>
                        </div>

                        {/* IPFS Meta Link */}
                        <a 
                          href={cert.metadata_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-[10px] text-brand-cyan-glow flex items-center gap-1 hover:underline mt-1 w-fit"
                        >
                          Ver metadados no IPFS
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    ))}
                  </div>
                </div>

                <hr className="border-white/5" />

                {/* History Trail completions */}
                <div>
                  <h3 className="text-sm font-bold uppercase tracking-wider text-brand-slate-200 mb-4 flex items-center gap-2">
                    <Rocket className="w-4 h-4 text-brand-emerald-glow" />
                    Jornada Acadêmica
                  </h3>

                  <div className="relative pl-6 border-l border-white/5 space-y-6">
                    {learnerData.completed_trails.map((t, idx) => (
                      <div key={t.trail} className="relative">
                        {/* Bullet point indicator */}
                        <div className="absolute -left-[30px] top-1.5 w-3 h-3 rounded-full bg-brand-emerald-neon border border-brand-abyss shadow-glass-glow-emerald" />
                        
                        <div>
                          <h4 className="text-xs font-bold text-brand-slate-200">
                            Trilha Concluída: <span className="text-brand-emerald-glow">{t.trail}</span>
                          </h4>
                          <p className="text-[10px] text-brand-slate-400 mt-0.5">
                            Completada em {new Date(t.completed_at).toLocaleDateString('pt-BR')}
                          </p>
                        </div>
                      </div>
                    ))}

                    <div className="relative">
                      {/* Interactive current trail item */}
                      <div className="absolute -left-[30px] top-1.5 w-3 h-3 rounded-full bg-brand-purple-neon border border-brand-abyss animate-ping" />
                      <div className="absolute -left-[30px] top-1.5 w-3 h-3 rounded-full bg-brand-purple-neon border border-brand-abyss" />
                      
                      <div>
                        <h4 className="text-xs font-bold text-brand-purple-glow">
                          Trilha em Andamento: {learnerData.current_trail}
                        </h4>
                        <p className="text-[10px] text-brand-slate-400 mt-0.5">
                          Status: {learnerData.current_state}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Footer info brand */}
        <div className="text-center text-xs text-brand-slate-400">
          <p>© 2026 DigitalIA Ecosystem. Conectando Jovens de Escola Pública à Nova Economia Digital.</p>
          <p className="text-[10px] text-white/10 mt-1">Blockchain Powered Certifications. Smart Contracts deployed on Arbitrum Nova.</p>
        </div>
      </div>
    </div>
  );
};
