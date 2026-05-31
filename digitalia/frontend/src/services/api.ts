// API Service for DigitalIA Frontend Integration

export interface LearnerSkill {
  skill: string;
  level: number;
  last_updated: string;
}

export interface CompletedTrail {
  trail: string;
  completed_at: string;
  certificate_id?: string;
}

export interface LessonProgress {
  trail: string;
  lesson_id: string;
  score: number;
  time_spent_minutes: number;
  attempts: number;
  completed_at: string;
}

export interface Certificate {
  id: string;
  trail: string;
  level: number;
  tx_hash: string;
  contract_address: string;
  token_id: number;
  issued_at: string;
  metadata_url: string;
}

export interface LearnerData {
  id: string;
  first_name: string;
  age: number;
  city: string;
  state: string;
  current_trail: string;
  current_state: string;
  level: number;
  completed_projects: number;
  avg_rating: number;
  total_earned_brl: number;
  skills: LearnerSkill[];
  completed_trails: CompletedTrail[];
  lesson_progresses: LessonProgress[];
  certificates: Certificate[];
}

export interface ProjectCompany {
  company_name: string;
  city: string;
  state: string;
  is_verified: boolean;
  avg_rating: number;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  required_trail: string;
  required_skills: Record<string, number>;
  complexity: number;
  budget_brl: number;
  hours_needed: number;
  deadline_days: number;
  status: string;
  created_at: string;
  company: ProjectCompany;
}

// Secret key for HMAC-SHA256 simulation
const WEBHOOK_SECRET = "digitalia_secret_key_2026";

// Helper to simulate HMAC hex signature
function simulateHmacSha256(message: string, secret: string): string {
  // Simple deterministic hash simulation for frontend showcase
  let hash = 0;
  const combined = message + secret;
  for (let i = 0; i < combined.length; i++) {
    const char = combined.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash |= 0; // Convert to 32bit integer
  }
  
  // Convert to beautiful pseudo-hex format of 64 characters
  const hexChars = "0123456789abcdef";
  let result = "sha256=";
  let currentSeed = Math.abs(hash);
  for (let i = 0; i < 64; i++) {
    currentSeed = (currentSeed * 16807) % 2147483647;
    result += hexChars[currentSeed % 16];
  }
  return result;
}

// Realistic Mocks
const MOCK_LEARNER: LearnerData = {
  id: "d9b23b32-cd22-4822-b5e1-88f1faefc7aa",
  first_name: "Thiago Silva",
  age: 22,
  city: "Recife",
  state: "PE",
  current_trail: "Desenvolvimento Full Stack React & Node",
  current_state: "Focado em Projetos Práticos",
  level: 3,
  completed_projects: 4,
  avg_rating: 4.85,
  total_earned_brl: 3850.00,
  skills: [
    { skill: "React.js", level: 8.5, last_updated: "2026-05-28" },
    { skill: "TypeScript", level: 7.8, last_updated: "2026-05-29" },
    { skill: "Tailwind CSS", level: 9.2, last_updated: "2026-05-25" },
    { skill: "Node.js & Express", level: 6.5, last_updated: "2026-05-20" },
    { skill: "PostgreSQL & Prisma", level: 7.0, last_updated: "2026-05-27" }
  ],
  completed_trails: [
    { trail: "Fundamentos de Programação", completed_at: "2026-04-10", certificate_id: "c1" },
    { trail: "CSS Avançado & Responsividade", completed_at: "2026-05-02", certificate_id: "c2" }
  ],
  lesson_progresses: [
    { trail: "React Avançado", lesson_id: "Introdução a Hooks customizados", score: 9.5, time_spent_minutes: 45, attempts: 1, completed_at: "2026-05-28" },
    { trail: "React Avançado", lesson_id: "Gerenciamento de Estado Global", score: 8.8, time_spent_minutes: 60, attempts: 2, completed_at: "2026-05-29" }
  ],
  certificates: [
    {
      id: "cert-9f54-4a91",
      trail: "Fundamentos de Programação",
      level: 1,
      tx_hash: "0x8fa4c67dbd3e7d56e7fae45b801de2046db2a549fae67272782b7db53bc894ae",
      contract_address: "0x2c14112e3e7f4c9c10bbdf322de32cb9fae67891",
      token_id: 1024,
      issued_at: "2026-04-10T18:30:00Z",
      metadata_url: "https://ipfs.io/ipfs/QmZ3A87f9daB"
    },
    {
      id: "cert-cd22-b5e1",
      trail: "CSS Avançado & Responsividade",
      level: 2,
      tx_hash: "0x12fa9db58a6fdf39cb9a456ee892bf4e6fa189c4a5e2f7b8ab20de9a84bfde99",
      contract_address: "0x2c14112e3e7f4c9c10bbdf322de32cb9fae67891",
      token_id: 1148,
      issued_at: "2026-05-02T20:15:00Z",
      metadata_url: "https://ipfs.io/ipfs/QmX9b6faef5c"
    }
  ]
};

const MOCK_PROJECTS: Project[] = [
  {
    id: "proj-1",
    title: "E-Commerce Landing Page com Carrinho Local",
    description: "Criação de uma landing page moderna e responsiva para uma cooperativa local de artesãos de barro de Caruaru. A página deve exibir o catálogo de produtos e permitir que o cliente adicione itens a um carrinho simulado e envie o pedido diretamente para o WhatsApp do vendedor.",
    required_trail: "CSS Avançado & Responsividade",
    required_skills: { "Tailwind CSS": 8.0, "React.js": 7.0 },
    complexity: 4,
    budget_brl: 1200.00,
    hours_needed: 16,
    deadline_days: 7,
    status: "open",
    created_at: "2026-05-29T10:00:00Z",
    company: {
      company_name: "Artesanatos Nordeste",
      city: "Caruaru",
      state: "PE",
      is_verified: true,
      avg_rating: 4.9
    }
  },
  {
    id: "proj-2",
    title: "Dashboard Financeiro para MEI com Controle Tributário",
    description: "Desenvolver um painel financeiro interativo para microempreendedores individuais. Deve conter gráficos de receitas/despesas mensais, cálculo automatizado do DAS mensal com base no faturamento e alerta de limite do MEI anual. Interface elegante com modo dark.",
    required_trail: "Desenvolvimento Full Stack React & Node",
    required_skills: { "React.js": 8.0, "TypeScript": 7.5, "PostgreSQL & Prisma": 7.0 },
    complexity: 6,
    budget_brl: 2500.00,
    hours_needed: 30,
    deadline_days: 14,
    status: "open",
    created_at: "2026-05-30T09:30:00Z",
    company: {
      company_name: "Contabiliza Tech",
      city: "São Paulo",
      state: "SP",
      is_verified: true,
      avg_rating: 4.7
    }
  },
  {
    id: "proj-3",
    title: "API de Agendamento Integrada com Google Calendar",
    description: "Implementar uma API em Node.js com TypeScript para controle de agendamentos em clínicas médicas. A API deve realizar o fluxo completo de CRUD de agendamentos, verificação de conflitos de horários e sincronização bidirecional em tempo real com a agenda do Google via OAuth2.",
    required_trail: "Desenvolvimento Full Stack React & Node",
    required_skills: { "Node.js & Express": 8.0, "TypeScript": 8.0, "PostgreSQL & Prisma": 7.5 },
    complexity: 8,
    budget_brl: 3200.00,
    hours_needed: 40,
    deadline_days: 20,
    status: "open",
    created_at: "2026-05-28T14:00:00Z",
    company: {
      company_name: "HealthConnect",
      city: "Belo Horizonte",
      state: "MG",
      is_verified: false,
      avg_rating: 4.5
    }
  }
];

export const api = {
  // GET /api/v1/learners/me/data
  getLearnerData: async (): Promise<LearnerData> => {
    try {
      const response = await fetch('/api/v1/learners/me/data');
      if (!response.ok) throw new Error('Falha ao obter dados reais');
      return await response.json();
    } catch (e) {
      console.warn("API de Produção indisponível, servindo Mock do Learner...", e);
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 800));
      return MOCK_LEARNER;
    }
  },

  // GET /api/v1/projects/available
  getAvailableProjects: async (): Promise<Project[]> => {
    try {
      const response = await fetch('/api/v1/projects/available');
      if (!response.ok) throw new Error('Falha ao obter projetos reais');
      return await response.json();
    } catch (e) {
      console.warn("API de Produção indisponível, servindo Mock de Projetos...", e);
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 950));
      return MOCK_PROJECTS;
    }
  },

  // POST /api/v1/webhook
  // Simulates a WhatsApp message sent to our Webhook endpoint, with automated HMAC-SHA256 signature
  triggerWebhookMessage: async (
    phone: string,
    messageText: string,
    isIncoming: boolean = true
  ): Promise<{ success: boolean; signature: string; payload: any; serverResponse?: any }> => {
    const payload = {
      object: "whatsapp",
      entry: [
        {
          id: "WHATSAPP_BUSINESS_ACCOUNT_ID",
          changes: [
            {
              value: {
                messaging_product: "whatsapp",
                metadata: {
                  display_phone_number: "558199999999",
                  phone_number_id: "PHONE_NUMBER_ID"
                },
                contacts: [
                  {
                    profile: { name: "Thiago Silva" },
                    wa_id: phone
                  }
                ],
                messages: [
                  {
                    from: phone,
                    id: `wamid.HBgMNTU4MTk5OTk5OTk5NRUCABEYEkJGOTQ1NzcyQTc3RDUzM0ZFMAA=`,
                    timestamp: Math.floor(Date.now() / 1000).toString(),
                    text: { body: messageText },
                    type: "text"
                  }
                ]
              },
              field: "messages"
            }
          ]
        }
      ]
    };

    const payloadString = JSON.stringify(payload);
    const signature = simulateHmacSha256(payloadString, WEBHOOK_SECRET);

    try {
      const response = await fetch('/api/v1/webhook', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Hub-Signature-256': signature
        },
        body: payloadString
      });
      
      let serverResponse = null;
      if (response.ok) {
        serverResponse = await response.json();
      }
      
      return {
        success: response.ok,
        signature,
        payload,
        serverResponse
      };
    } catch (e) {
      console.warn("API de Webhook real indisponível. Simulando sucesso local...", e);
      await new Promise(resolve => setTimeout(resolve, 1200));
      return {
        success: true,
        signature,
        payload,
        serverResponse: { status: "received", msg_id: "wamid.simulated_ok", processed_by: "DigitalIA Agent" }
      };
    }
  }
};
