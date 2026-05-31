import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  User, Award, Briefcase, DollarSign, Sparkles, MessageSquare, Send, 
  Settings, ExternalLink, RefreshCw, Smartphone, CheckCircle, Database, Lock, AlertTriangle
} from 'lucide-react';
import { api, LearnerData, Project } from '../services/api';
import { ProjectCard } from './ProjectCard';

interface ProgressDashboardProps {
  learnerData: LearnerData | null;
  projects: Project[];
  loading: boolean;
  onRefresh: () => Promise<void>;
  onViewPortfolio: () => void;
}

export const ProgressDashboard: React.FC<ProgressDashboardProps> = ({
  learnerData,
  projects,
  loading,
  onRefresh,
  onViewPortfolio
}) => {
  const [waMessage, setWaMessage] = useState('');
  const [sendingWa, setSendingWa] = useState(false);
  const [webhookLogs, setWebhookLogs] = useState<{
    time: string;
    message: string;
    signature: string;
    status: 'success' | 'failed' | 'simulated';
    response: any;
  }[]>([]);

  // Pre-fill simulator
  const [selectedSimText, setSelectedSimText] = useState('Quero ver meus projetos recomendados!');

  const handleSimulateWebhook = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!waMessage.trim() || !learnerData) return;

    setSendingWa(true);
    const messageToSend = waMessage;
    setWaMessage('');

    try {
      // Simulate sending WhatsApp message using the actual api webhook triggers
      const result = await api.triggerWebhookMessage(
        '558199999999', // learner phone
        messageToSend
      );

      setWebhookLogs(prev => [
        {
          time: new Date().toLocaleTimeString('pt-BR'),
          message: messageToSend,
          signature: result.signature,
          status: result.success ? (result.serverResponse?.msg_id ? 'success' : 'simulated') : 'failed',
          response: result.serverResponse || { warning: "Servidor real offline, simulador ativado." }
        },
        ...prev
      ]);
    } catch (e) {
      console.error(e);
    } finally {
      setSendingWa(false);
    }
  };

  const handleSelectSimText = (text: string) => {
    setWaMessage(text);
  };

  // Skeleton loading screen for high premium aesthetic
  if (loading || !learnerData) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Skeleton Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-white/5 pb-6">
          <div className="space-y-2">
            <div className="h-7 w-48 bg-slate-800 rounded-lg animate-pulse" />
            <div className="h-4 w-72 bg-slate-850 rounded-lg animate-pulse" />
          </div>
          <div className="h-10 w-32 bg-slate-800 rounded-xl animate-pulse" />
        </div>

        {/* Skeleton Grid Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="glass-card p-6 rounded-2xl border border-white/5 space-y-3">
              <div className="h-4 w-20 bg-slate-800 rounded animate-pulse" />
              <div className="h-8 w-28 bg-slate-850 rounded-lg animate-pulse" />
            </div>
          ))}
        </div>

        {/* Skeleton Content Body */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div className="h-6 w-36 bg-slate-850 rounded animate-pulse" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[...Array(2)].map((_, i) => (
                <div key={i} className="glass-card h-64 rounded-2xl border border-white/5 animate-pulse" />
              ))}
            </div>
          </div>
          <div className="space-y-6">
            <div className="h-6.5 w-40 bg-slate-850 rounded animate-pulse" />
            <div className="glass-card h-80 rounded-2xl border border-white/5 animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 relative">
      {/* Background neon lights */}
      <div className="absolute top-0 right-1/3 w-[300px] h-[300px] bg-brand-purple-neon/5 rounded-full blur-[90px] pointer-events-none" />
      <div className="absolute bottom-1/3 left-1/4 w-[300px] h-[300px] bg-brand-cyan-neon/5 rounded-full blur-[90px] pointer-events-none" />

      {/* Header Banner Section */}
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-white/5 pb-6"
      >
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Sparkles className="w-4 h-4 text-brand-purple-glow animate-pulse" />
            <span className="text-xs uppercase font-bold tracking-widest text-brand-purple-glow">Área do Estudante</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Olá, {learnerData.first_name}!
          </h1>
          <p className="text-brand-slate-400 text-xs mt-1">
            Status do Perfil: <span className="text-brand-cyan-glow font-medium animate-pulse">● {learnerData.current_state}</span>
          </p>
        </div>

        {/* Global actions */}
        <div className="flex items-center gap-3 w-full md:w-auto">
          <button 
            onClick={onRefresh}
            className="p-2.5 rounded-xl border border-white/10 hover:border-white/20 text-brand-slate-400 hover:text-white transition-all bg-brand-slate-900/30"
            title="Atualizar dados"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          
          <button 
            onClick={onViewPortfolio}
            className="flex-grow md:flex-none py-2.5 px-4 rounded-xl bg-gradient-to-r from-brand-purple-neon via-brand-purple-glow to-brand-cyan-neon hover:shadow-glass-glow-purple text-white text-xs font-semibold flex items-center justify-center gap-2 transition-all"
          >
            <User className="w-4 h-4" />
            Ver Portfólio Público
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>
      </motion.div>

      {/* Grid Stats Block */}
      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 lg:grid-cols-4 gap-4"
      >
        {/* Nível Card */}
        <div className="glass-card p-5 rounded-2xl border border-white/5 relative overflow-hidden flex flex-col justify-between h-28 group">
          <div className="absolute top-0 right-0 w-16 h-16 bg-brand-purple-neon/5 rounded-full blur-lg group-hover:bg-brand-purple-neon/10 transition-all" />
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-brand-slate-400 uppercase font-bold tracking-wider">Nível do Aluno</span>
            <Award className="w-4 h-4 text-brand-purple-glow" />
          </div>
          <div className="mt-2">
            <span className="text-2xl font-extrabold text-white font-mono">Lvl {learnerData.level}</span>
            <span className="text-[9px] text-brand-purple-glow block font-semibold mt-0.5">Gold Practitioner</span>
          </div>
        </div>

        {/* Jobs Concluídos Card */}
        <div className="glass-card p-5 rounded-2xl border border-white/5 relative overflow-hidden flex flex-col justify-between h-28 group">
          <div className="absolute top-0 right-0 w-16 h-16 bg-brand-emerald-neon/5 rounded-full blur-lg group-hover:bg-brand-emerald-neon/10 transition-all" />
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-brand-slate-400 uppercase font-bold tracking-wider">Jobs Concluídos</span>
            <Briefcase className="w-4 h-4 text-brand-emerald-glow" />
          </div>
          <div className="mt-2">
            <span className="text-2xl font-extrabold text-white font-mono">{learnerData.completed_projects}</span>
            <span className="text-[9px] text-brand-emerald-glow block font-semibold mt-0.5">Aprovados via Smart-Contract</span>
          </div>
        </div>

        {/* Total Earned Card */}
        <div className="glass-card p-5 rounded-2xl border border-white/5 relative overflow-hidden flex flex-col justify-between h-28 group">
          <div className="absolute top-0 right-0 w-16 h-16 bg-brand-cyan-neon/5 rounded-full blur-lg group-hover:bg-brand-cyan-neon/10 transition-all" />
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-brand-slate-400 uppercase font-bold tracking-wider">Total Ganho (BRL)</span>
            <DollarSign className="w-4 h-4 text-brand-cyan-glow" />
          </div>
          <div className="mt-2">
            <span className="text-2xl font-extrabold text-brand-emerald-glow font-mono">
              R$ {learnerData.total_earned_brl.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </span>
            <span className="text-[9px] text-brand-cyan-glow block font-semibold mt-0.5">Pagamento Instantâneo PIX</span>
          </div>
        </div>

        {/* Média Card */}
        <div className="glass-card p-5 rounded-2xl border border-white/5 relative overflow-hidden flex flex-col justify-between h-28 group">
          <div className="absolute top-0 right-0 w-16 h-16 bg-brand-amber-neon/5 rounded-full blur-lg group-hover:bg-brand-amber-neon/10 transition-all" />
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-brand-slate-400 uppercase font-bold tracking-wider">Score Geral</span>
            <span className="text-xs text-brand-amber-glow font-extrabold font-mono">★</span>
          </div>
          <div className="mt-2">
            <span className="text-2xl font-extrabold text-white font-mono">{learnerData.avg_rating.toFixed(2)}</span>
            <span className="text-[9px] text-brand-amber-glow block font-semibold mt-0.5">Avaliação das Empresas</span>
          </div>
        </div>
      </motion.div>

      {/* Main Panel grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left column (2/3 width) - Available matches */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-bold text-white tracking-wide flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-brand-cyan-glow" />
              Seus Matches de Projetos Recomendados
            </h2>
            <span className="text-xs text-brand-slate-400 font-medium">
              {projects.length} projetos disponíveis
            </span>
          </div>

          {projects.length === 0 ? (
            <div className="glass-card p-12 text-center rounded-2xl border border-white/5 space-y-3">
              <Briefcase className="w-8 h-8 text-brand-slate-400 mx-auto" />
              <p className="text-brand-slate-200 text-sm font-medium">Nenhum projeto aberto encontrado.</p>
              <p className="text-brand-slate-400 text-xs max-w-sm mx-auto">
                Continue estudando as trilhas de aprendizado para que novas empresas combinem com seu portfólio!
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {projects.map((project) => (
                <ProjectCard
                  key={project.id}
                  project={project}
                  learnerSkills={learnerData.skills}
                  onApply={async (id) => {
                    // Simulate application update trigger
                    console.log(`Candidatura para ${id}`);
                  }}
                />
              ))}
            </div>
          )}

          {/* Education list & stats in the left bottom */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
            {/* Skills checklist */}
            <div className="glass-card p-6 rounded-2xl border border-white/5 space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-brand-slate-200">Habilidades Adquiridas</h3>
              <div className="space-y-3">
                {learnerData.skills.map((skill) => (
                  <div key={skill.skill} className="flex items-center justify-between py-1.5 border-b border-white/5">
                    <span className="text-xs font-mono text-brand-slate-200">{skill.skill}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-brand-slate-950 h-1.5 rounded-full overflow-hidden border border-white/5">
                        <div 
                          className="h-full bg-gradient-to-r from-brand-purple-neon to-brand-cyan-neon"
                          style={{ width: `${skill.level * 10}%` }}
                        />
                      </div>
                      <span className="text-[10px] font-mono text-brand-purple-glow font-bold">{skill.level.toFixed(1)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Blockchain NFT Proofs */}
            <div className="glass-card p-6 rounded-2xl border border-white/5 space-y-4 flex flex-col justify-between">
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wider text-brand-slate-200 mb-3.5">
                  Certificados Blockchain (ERC-721)
                </h3>
                <div className="space-y-3">
                  {learnerData.certificates.slice(0, 2).map((cert) => (
                    <div key={cert.id} className="p-3 bg-brand-slate-950 rounded-xl border border-white/5 flex items-center justify-between">
                      <div className="truncate pr-4">
                        <span className="text-[9px] uppercase font-bold text-brand-cyan-glow bg-brand-cyan-deep/40 px-1.5 py-0.5 rounded border border-brand-cyan-neon/20 mr-1.5">
                          Lvl {cert.level}
                        </span>
                        <span className="text-xs font-medium text-white truncate">{cert.trail}</span>
                        <span className="text-[9px] text-brand-slate-400 block font-mono mt-0.5">Token ID: #{cert.token_id}</span>
                      </div>
                      <Award className="w-5 h-5 text-brand-cyan-glow flex-shrink-0" />
                    </div>
                  ))}
                </div>
              </div>
              
              <button 
                onClick={onViewPortfolio}
                className="w-full mt-3 py-2 text-center text-xs font-semibold text-brand-cyan-glow hover:underline flex items-center justify-center gap-1.5 border border-brand-cyan-neon/20 hover:border-brand-cyan-neon/40 rounded-xl transition-all"
              >
                Ver todos os certificados
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Right column (1/3 width) - Webhook sandbox simulator */}
        <div className="space-y-6">
          <div className="glass-card rounded-2xl border border-brand-purple-neon/20 overflow-hidden shadow-2xl relative">
            <div className="absolute top-0 right-0 w-32 h-32 bg-brand-purple-neon/5 rounded-full blur-xl pointer-events-none" />
            
            {/* Simulator Header */}
            <div className="p-5 border-b border-white/5 bg-brand-purple-deep/15 flex items-center gap-2">
              <Smartphone className="w-4 h-4 text-brand-purple-glow animate-bounce" />
              <div>
                <h3 className="text-sm font-bold text-white">Simulador WhatsApp DigitalIA</h3>
                <p className="text-[10px] text-brand-slate-400">Interação de IA via Webhook Integrado</p>
              </div>
              <span className="ml-auto flex items-center gap-1 text-[9px] font-bold text-brand-emerald-glow bg-brand-emerald-deep/40 px-2 py-0.5 rounded-full border border-brand-emerald-neon/20">
                <Database className="w-2.5 h-2.5 animate-pulse" />
                Live API
              </span>
            </div>

            {/* Sandbox details */}
            <div className="p-5 space-y-4">
              <p className="text-xs text-brand-slate-400 leading-normal">
                Dispare mensagens para simular o comportamento do assistente. O frontend injeta uma assinatura HMAC no cabeçalho <span className="text-brand-purple-glow font-mono text-[10px]">X-Hub-Signature-256</span> correspondente ao body, validando a segurança do webhook.
              </p>

              {/* Suggestions Chips */}
              <div className="space-y-2">
                <span className="text-[10px] uppercase font-bold text-brand-slate-400 block">Atalhos rápidos para simular:</span>
                <div className="flex flex-wrap gap-1.5">
                  {[
                    'Quero atualizar minha skill de React!',
                    'Quais são meus certificados?',
                    'Qual o meu saldo acumulado?'
                  ].map((text) => (
                    <button
                      key={text}
                      onClick={() => handleSelectSimText(text)}
                      className="text-[10px] text-brand-slate-200 bg-brand-slate-900 border border-white/5 hover:border-brand-purple-neon/30 px-2.5 py-1 rounded-lg transition-all"
                    >
                      {text}
                    </button>
                  ))}
                </div>
              </div>

              {/* Chat Input Field Form */}
              <form onSubmit={handleSimulateWebhook} className="flex gap-2">
                <input
                  type="text"
                  value={waMessage}
                  onChange={(e) => setWaMessage(e.target.value)}
                  placeholder="Envie uma mensagem..."
                  disabled={sendingWa}
                  className="flex-grow text-xs rounded-xl px-3 py-2.5 glass-input font-medium"
                />
                
                <button
                  type="submit"
                  disabled={sendingWa || !waMessage.trim()}
                  className="p-2.5 rounded-xl bg-gradient-to-r from-brand-purple-neon to-brand-cyan-neon text-white hover:shadow-glass-glow-purple disabled:opacity-50 disabled:shadow-none transition-all flex items-center justify-center"
                >
                  {sendingWa ? (
                    <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </button>
              </form>
            </div>

            {/* HMAC security warning display */}
            <div className="p-4 mx-5 bg-brand-slate-950/70 border border-white/5 rounded-xl flex items-start gap-2.5 text-[10px] leading-relaxed text-brand-slate-400">
              <Lock className="w-3.5 h-3.5 text-brand-purple-glow mt-0.5 flex-shrink-0" />
              <div>
                <span className="font-bold text-brand-slate-200 block mb-0.5">Segurança Ativada</span>
                Chave Simétrica: <span className="font-mono text-brand-purple-glow">digitalia_secret_key_2026</span>
              </div>
            </div>

            {/* Message log panel */}
            <div className="p-5 border-t border-white/5">
              <span className="text-[10px] uppercase font-bold text-brand-slate-400 block mb-3.5">Histórico do Simulador Webhook</span>
              
              <div className="space-y-4 max-h-[220px] overflow-y-auto pr-1">
                {webhookLogs.length === 0 ? (
                  <div className="text-center py-6 text-brand-slate-400 text-xs">
                    <MessageSquare className="w-6 h-6 text-brand-slate-400 mx-auto opacity-50 mb-1" />
                    Nenhuma mensagem enviada.
                  </div>
                ) : (
                  webhookLogs.map((log, idx) => (
                    <div key={idx} className="p-3 bg-brand-slate-950/40 border border-white/5 rounded-xl space-y-2">
                      <div className="flex justify-between items-center text-[10px]">
                        <span className="text-brand-slate-400">{log.time}</span>
                        <span className="text-brand-cyan-glow font-mono font-semibold">HMAC OK</span>
                      </div>
                      
                      <div className="text-xs text-white bg-brand-purple-deep/10 border border-brand-purple-neon/15 p-2 rounded-lg leading-relaxed">
                        <span className="text-[9px] uppercase font-bold block text-brand-purple-glow mb-0.5">Mensagem Enviada:</span>
                        {log.message}
                      </div>

                      <div className="space-y-1">
                        <span className="text-[9px] uppercase font-bold block text-brand-slate-400">HMAC SHA-256 Header:</span>
                        <div className="text-[8px] font-mono text-brand-amber-glow break-all bg-black/40 p-1.5 rounded border border-white/5">
                          {log.signature}
                        </div>
                      </div>

                      <div className="text-[9px] bg-black/20 p-2 rounded-lg text-brand-slate-400 font-mono">
                        <span className="text-[8px] uppercase font-bold block text-brand-emerald-glow mb-1">Server Response:</span>
                        <pre className="overflow-x-auto text-[8px] font-mono whitespace-pre-wrap">
                          {JSON.stringify(log.response, null, 2)}
                        </pre>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
