from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Lesson:
    id: str
    trail: str
    module_number: int
    lesson_number: int
    title: str
    concept_text: str           # Explicação (max 200 chars para WA)
    demo_steps: List[str]       # Passo a passo numerado
    exercise: str               # O que o aprendiz deve fazer
    exercise_success_criteria: str  # Como o AI avalia o sucesso
    tools_used: List[str]       # Ferramentas utilizadas na lição

# Lista e mapeamento de lições por trilha
TRAIL_LESSONS: Dict[str, List[Lesson]] = {
    "social_media": [
        Lesson(
            id="social_m1_l1",
            trail="social_media",
            module_number=1,
            lesson_number=1,
            title="Criando a Primeira Legenda com ChatGPT",
            concept_text=(
                "Legenda arretada atrai cliente e vende mais, visse? Com o ChatGPT tu cria legendas "
                "profissionais num piscar de olhos, sem precisar quebrar a cabeça com as palavras!"
            ),
            demo_steps=[
                "1. Acesse chat.openai.com (gratuito) ou use no celular.",
                "2. Digite: 'Crie uma legenda para o Instagram de uma lanchonete de tapioca em João Pessoa. Use tom descontraído, emojis, 3 hashtags nordestinas e no máximo 150 palavras.'",
                "3. Veja o que ele criou, mude o que achar melhor e pronto! Menos de 1 minuto."
            ],
            exercise=(
                "Agora é a tua vez, meu fi! Escolha um comércio da tua rua (um mercadinho, salão ou lanchonete) "
                "e crie uma legenda usando o ChatGPT. Mande a legenda pronta aqui pra mim!"
            ),
            exercise_success_criteria=(
                "A legenda enviada precisa conter: identificação clara do negócio, tom adequado de comunicação, "
                "pelo menos 2 hashtags e estar escrita em português compreensível, sem passar de 200 palavras."
            ),
            income_connection=(
                "O trabalho digital remoto remunerado paga em média R$ 6.479/mês (2.7x mais que presencial!). Dominar a "
                "escrita de legendas de redes sociais te ajuda a superar a renda média do Nordeste que é de R$ 2.282 "
                "(uma defasagem de 36% contra a média nacional). Cada pacote mensal com 4 legendas para um comércio do "
                "bairro pode te render de R$ 100 a R$ 250, construindo seu caminho rumo à renda remota!"
            ),
            tools_used=["ChatGPT"]
        ),
        Lesson(
            id="social_m1_l2",
            trail="social_media",
            module_number=1,
            lesson_number=2,
            title="Planejando Posts com Calendário Editorial",
            concept_text=(
                "Postar sem rumo não dá engajamento! Um calendário inteligente garante presença "
                "toda semana. O cliente adora organização e profissionalismo!"
            ),
            demo_steps=[
                "1. Abra o ChatGPT e peça: 'Gere ideias de post para 3 dias da semana (segunda, quarta e sexta) para um pet shop local.'",
                "2. Separe as ideias: Segunda (dica útil), Quarta (meme de pet) e Sexta (oferta de banho e tosa).",
                "3. Organize num calendário simples por semana."
            ],
            exercise=(
                "Desenhe um mini calendário de 3 posts semanais para uma barbearia ou salão de beleza de bairro. "
                "Me escreva os temas de cada um dos 3 posts (ex: segunda, quarta, sexta) e mande aqui!"
            ),
            exercise_success_criteria=(
                "O aprendiz deve enviar um plano com exatamente 3 dias descritos, cada um com um tema diferente e "
                "relevante para o nicho de beleza/estética."
            ),
            income_connection=(
                "A informalidade atinge 38,5% dos jovens ocupados de 18 a 29 anos no Nordeste. Gerenciar calendários editoriais "
                "para pequenas empresas locais te ajuda a escapar do desemprego jovem (que atinge 11,4% no país) e a construir "
                "sua própria receita. Cada cliente de bairro te paga entre R$ 200 e R$ 400/mês para manter os posts organizados!"
            ),
            tools_used=["ChatGPT"]
        )
    ],
    "design": [
        Lesson(
            id="design_m1_l1",
            trail="design",
            module_number=1,
            lesson_number=1,
            title="Seu Primeiro Post Bonitão no Canva",
            concept_text=(
                "Um design atraente enche os olhos do cliente! No Canva, com a ajuda dos templates "
                "inteligentes, tu cria artes profissionais mesmo que nunca tenha feito um desenho na vida."
            ),
            demo_steps=[
                "1. Acesse canva.com pelo navegador ou baixe o app.",
                "2. Digite na busca: 'Instagram post promoção de pizza'.",
                "3. Selecione um template massa, edite o texto com o nome da pizzaria e insira uma imagem apetitosa.",
                "4. Clique em baixar no formato PNG ou JPEG."
            ],
            exercise=(
                "Monte uma arte simples de promoção (pode ser pizza, hambúrguer, roupa ou qualquer serviço) no Canva. "
                "Use um template gratuito, tire um print ou salve a imagem e me mande uma descrição textual ou o link da arte aqui!"
            ),
            exercise_success_criteria=(
                "O aluno deve enviar uma descrição detalhada de como ficou seu design (cores, fontes e texto) ou um link de compartilhamento do Canva, provando que conseguiu alterar o template padrão."
            ),
            income_connection=(
                "A média de faturamento de profissionais digitais freelancers remotos no Brasil atinge R$ 6.479/mês. Criar artes "
                "bonitas no Canva abre as portas para esse mercado promissor de trabalho independente. Um pacote inicial com "
                "6 posts simples para comércios locais pode te render R$ 150 a R$ 300, impulsionando a economia do seu bairro!"
            ),
            tools_used=["Canva"]
        ),
        Lesson(
            id="design_m1_l2",
            trail="design",
            module_number=1,
            lesson_number=2,
            title="Escolhendo Cores Arretadas com IA",
            concept_text=(
                "Cores transmitem emoção, caboclo! Usar a IA de paleta de cores como o Coolors.co ajuda "
                "a escolher a combinação perfeita que combina com a marca sem parecer carnaval."
            ),
            demo_steps=[
                "1. Acesse coolors.co/generate no celular.",
                "2. Aperte espaço (ou toque na tela) para gerar combinações harmônicas aleatórias.",
                "3. Trave uma cor que você curtir e gere o resto combinando com ela.",
                "4. Copie os códigos hexadecimais (ex: #FF5733)."
            ],
            exercise=(
                "Gere uma paleta de 3 cores no Coolors para uma marca de bolos caseiros. "
                "Escreva os códigos hexadecimais ou descreva as cores (ex: rosa doce, marrom chocolate, creme) e me envie!"
            ),
            exercise_success_criteria=(
                "O aprendiz deve enviar pelo menos 3 cores com seus códigos hexadecimais correspondentes ou descrições claras que façam sentido harmônico para o nicho alimentício sugerido."
            ),
            income_connection=(
                "Pequenas marcas locais estão ansiosas para se profissionalizarem e pagam de R$ 150 a R$ 350 por identidade visual "
                "de cores básica e mini manual de marca. É a sua chance de superar a barreira da renda presencial nordestina "
                "(de R$ 2.282) trabalhando do seu próprio celular, sem as barreiras e custos de deslocamento urbano!"
            ),
            tools_used=["Coolors IA", "Canva"]
        )
    ],
    "automation": [
        Lesson(
            id="auto_m1_l1",
            trail="automation",
            module_number=1,
            lesson_number=1,
            title="Criando Mensagem de Saudação Automática",
            concept_text=(
                "Perder cliente porque demorou a responder? De jeito nenhum! "
                "As respostas automáticas garantem que o cliente se sinta acolhido no mesmo segundo."
            ),
            demo_steps=[
                "1. Abra o WhatsApp Business (aplicativo gratuito de negócios).",
                "2. Vá em Configurações da Empresa > Mensagem de Saudação.",
                "3. Ative a opção de envio automático para novos contatos.",
                "4. Escreva uma mensagem simpática com o ChatGPT, cheia de energia e objetiva."
            ],
            exercise=(
                "Crie um texto de saudação automática super acolhedor para uma oficina de motos ou salão de beleza. "
                "Mande a mensagem prontinha aqui pra mim!"
            ),
            exercise_success_criteria=(
                "A mensagem de saudação deve incluir o nome da empresa, uma pergunta aberta de como pode ajudar (ex: 'Como podemos te ajudar hoje?') e um tom de cordialidade regionalizado."
            ),
            income_connection=(
                "Evitar a perda de clientes por demoras no atendimento é crucial para PMEs locais. Cobrar uma taxa única de "
                "R$ 150 a R$ 300 por essa configuração rápida de WhatsApp Business te afasta da informalidade juvenil "
                "(que atinge 38,5% no país) e coloca dinheiro de forma imediata na sua conta!"
            ),
            tools_used=["WhatsApp Business", "ChatGPT"]
        ),
        Lesson(
            id="auto_m1_l2",
            trail="automation",
            module_number=1,
            lesson_number=2,
            title="Fluxo de Atendimento com Respostas Rápidas",
            concept_text=(
                "Ganhe tempo arretado! O recurso de respostas rápidas (/atalho) deixa as informações frequentes "
                "como pix, endereço e cardápio a um clique de distância."
            ),
            demo_steps=[
                "1. No WhatsApp Business, acesse Respostas Rápidas.",
                "2. Crie o atalho '/pix' e insira a chave Pix e instruções de pagamento da empresa.",
                "3. Salve e teste digitando o atalho em uma conversa simulada."
            ],
            exercise=(
                "Escreva um atalho '/entrega' explaining fictícias taxas de entrega para bairros da sua cidade. "
                "Escreva o atalho e a mensagem de resposta rápida correspondente e envie para mim!"
            ),
            exercise_success_criteria=(
                "O aprendiz deve indicar o comando (ex: /entrega) e a mensagem de resposta rápida detalhando as opções de frete ou bairros atendidos."
            ),
            income_connection=(
                "Organizar respostas automáticas e cadastrar atalhos frequentes no WhatsApp Business de um comércio de bairro "
                "custa cerca de R$ 200 a R$ 300 por projeto. Esse serviço de otimização rápida ajuda a reter o capital "
                "circulante dentro da própria comunidade nordestina!"
            ),
            tools_used=["WhatsApp Business"]
        )
    ],
    "video": [
        Lesson(
            id="video_m1_l1",
            trail="video",
            module_number=1,
            lesson_number=1,
            title="Cortando Vídeo como um Profissional no CapCut",
            concept_text=(
                "Vídeo dinâmico retém a atenção do povo, oxente! Com o CapCut no celular, "
                "você remove os silêncios e erros em segundos, deixando o Reels bem animado."
            ),
            demo_steps=[
                "1. Baixe e abra o aplicativo gratuito CapCut.",
                "2. Importe um vídeo curto gravado no celular.",
                "3. Use a ferramenta 'Dividir' para separar as partes com silêncios ou gaguejadas e delete essas partes.",
                "4. Exporte o vídeo na resolução 1080p."
            ],
            exercise=(
                "Grave ou selecione um vídeo de teste de 15 segundos falando sobre o seu dia. Faça pelo menos 2 cortes nele "
                "para remover os respiros lentos. Mande um texto me explicando como foi sua experiência com a ferramenta de corte!"
            ),
            exercise_success_criteria=(
                "O aluno deve descrever textualmente a experiência detalhando onde cortou e qual foi a melhoria na fluidez do vídeo."
            ),
            income_connection=(
                "A criação de vídeos e Reels comerciais é o mercado de maior crescimento digital no Nordeste brasileiro. A edição "
                "de vídeos curtos no CapCut pode te render de R$ 50 a R$ 120 por vídeo finalizado. Com alguns clientes regulares, "
                "você conquista sua autonomia financeira contra a defasagem de renda regional!"
            ),
            tools_used=["CapCut Mobile"]
        ),
        Lesson(
            id="video_m1_l2",
            trail="video",
            module_number=1,
            lesson_number=2,
            title="Legendas Dinâmicas Automáticas com CapCut",
            concept_text=(
                "Mais de 80% das pessoas assistem aos vídeos no mudo nas redes. "
                "Colocar legendas automáticas bonitas é a chave do sucesso para qualquer criador!"
            ),
            demo_steps=[
                "1. Abra seu vídeo editado no CapCut.",
                "2. Vá no menu Texto > Legendas Automáticas.",
                "3. Selecione a fonte em português e clique em Iniciar.",
                "4. Escolha um estilo chamativo (como texto amarelo ou contorno preto) e salve."
            ],
            exercise=(
                "Gere legendas automáticas em um vídeo de teste no CapCut. Escolha um estilo chamativo e me descreva "
                "quais cores e fontes você aplicou para deixar o texto legível e atraente!"
            ),
            exercise_success_criteria=(
                "O aprendiz deve explicar as opções estéticas que escolheu no CapCut para melhorar a leitura do vídeo (ex: fonte negrito, cores chamativas como amarelo ou branco com borda)."
            ),
            income_connection=(
                "Vídeos com legendas dinâmicas geram muito mais retenção. Oferecer legendagem inteligente com IA para vídeos "
                "de infoprodutores ou marcas locais rende de R$ 60 a R$ 150 adicionais por vídeo finalizado, conectando você à "
                "média salarial de R$ 6.479 do mercado remoto freelancer digital!"
            ),
            tools_used=["CapCut Mobile"]
        )
    ]
}
