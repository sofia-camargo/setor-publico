# Documentação de Implantação da Inteligência Artificial — SIGDEI / GAFIA (Subsídio para o TAP)

> **IMPORTANTE:** Este documento descreve de forma completa a arquitetura, os modelos de linguagem, as tecnologias, as regras de negócio, a governança (LGPD) e as especificações técnicas da implantação de Inteligência Artificial no **Sistema de Gestão do Departamento de Desenvolvimento Econômico de Iracemápolis (SIGDEI — Projeto Interdisciplinar IV / Equipe GAFIA)**, estruturado para uso direto no **Termo de Abertura do Projeto (TAP)**, **Dicionário da EAP** e documentação acadêmica.

---

## 1. Visão Geral e Justificativa do Módulo de IA

A implantação da Inteligência Artificial no **SIGDEI** teve como propósito disponibilizar um **Assistente Inteligente em Linguagem Natural (NLP)** com arquitetura **RAG Híbrida (*Retrieval-Augmented Generation*) 100% local (*On-Premises*)**.

No contexto da administração pública municipal (atendimentos do **SEBRAE Aqui**, **Banco do Povo**, **PAT** e **PROCON**), o uso de APIs externas em nuvem apresenta barreiras financeiras (custo recorrente por token) e legais (**Lei Geral de Proteção de Dados — LGPD**, devido ao tráfego de dados empresariais e administrativos). A solução implantada resolve ambos os problemas ao processar **toda a indexação, busca semântica e geração de respostas localmente** no servidor da aplicação.

---

## 2. Arquitetura Técnica Implantada

### 2.1. Fluxo Completo de Processamento (Arquitetura RAG Híbrida)

```text
[1. Usuário Autenticado no Frontend (assistente.html / assistente.js)]
        │  Envia: Pergunta em linguagem natural + Período (início/fim) + Token JWT
        ▼
[2. API Django REST (/api/v1/assistente/perguntar/)]
        │
        ├─► [3. Controle de Acesso (RBAC e Visão Estratégica)]
        │       Valida perfil (Administrador, Gestor ou Secretário com Visão Estratégica)
        │       e filtra automaticamente os registros pelo setor do usuário logado.
        │
        ├─► [4A. Coleta Estruturada Autorizada (ORM Django - Banco de Dados)]
        │       Serializa Setores, Equipe/Usuários, Indicadores, Lançamentos (Atividade),
        │       Atendimentos anonimizados, Projetos, Tarefas, Ofícios e IC-01 a IC-04
        │       (removendo CNPJ, razão social e hashes de senha).
        │
        ├─► [4B. Busca Documental Local (.local_index / LlamaIndex)]
        │       Recupera os trechos mais relevantes dos PDFs e Markdown do projeto
        │       (TAP, Dicionário da EAP, Cronograma, Matriz RACI, PDM e README).
        │
        ▼
[5. Ranqueamento Semântico e Léxico (rank_passages)]
        │  Combina e ordena os trechos mais relevantes do banco e dos documentos
        ▼
[6. Geração da Resposta em Linguagem Natural]
        ├─► 6A. LLM Local via Ollama (qwen2.5:1.5b / llama3.2:3b com temperature=0)
        └─► 6B. Motor NLP Local Integrado (local_nlp_answer - Contingência Instantânea)
        │
        ▼
[7. Validação Anti-Vazamento e Citação de Fontes]
        Descarta qualquer referência fora do escopo autorizado e retorna ao navegador
        a resposta em português acompanhada das fontes auditáveis.
```

### 2.2. Componentes Principais do Código Implantado

- **Indexação e Busca Vetorial Documental (`gafia_docs.py`):**
  - Extrai o texto de arquivos `.pdf`, `.docx`, `.txt`, `.md` e `.csv` das pastas `sistema/docs/` (atualmente com 7 PDFs oficiais do projeto: Cronograma, Dicionário da EAP v01 e v02, Matriz RACI, PDM e TAP v02 e v03), `sistema/README.md` e `documentos/`.
  - Fragmenta os documentos em blocos (*chunks*) de **512 tokens** com sobreposição (*overlap*) de **64 tokens**.
  - Gera *embeddings* vetoriais locais com o modelo `nomic-embed-text` e persiste o índice em `.local_index/` (`docstore.json`, `default__vector_store.json` e `manifest.json` com verificação de integridade via hash **SHA-256**).
- **Pipeline RAG Híbrido e Motor NLP Local (`sistema/backend/ai_docs/rag.py`):**
  - Combina em tempo real os **dados estruturados do banco de dados** (filtrados pelas permissões do usuário logado) com os **55 blocos documentais** extraídos no `.local_index/docstore.json`.
  - Conta com um **Motor NLP Local Conversacional** (`local_nlp_answer`) que responde de forma curta, direta e determinística mesmo quando o serviço externo do Ollama não está em execução, garantindo **100% de disponibilidade**.
- **Cálculo Oficial de Indicadores Cruzados (`sistema/backend/sector/cross_indicators.py` e `ai_docs/dashboard.py`):**
  - Calcula no backend, a partir dos registros cronológicos de `Atendimento` vinculados por `Empresa`, os quatro indicadores estratégicos multissetoriais:
    - **IC-01 (Taxa de Conversão SEBRAE → Crédito):** Percentual de empresas orientadas pelo SEBRAE Aqui que obtiveram liberação de crédito posterior no Banco do Povo (`CNPJ atendidos no SEBRAE com crédito liberado depois ÷ CNPJ atendidos no SEBRAE × 100`).
    - **IC-02 (Vagas Geradas por Crédito):** Vagas abertas no PAT após liberação de crédito pela mesma empresa, por cada R$ 100 mil liberados (`Vagas abertas após liberação de crédito ÷ (crédito liberado no período / 100.000)`).
    - **IC-03 (Jornada Completa de Fomento):** Quantidade de empresas que percorreram SEBRAE Aqui → Banco do Povo (crédito) → PAT (vagas) em ordem cronológica.
    - **IC-04 (Atendimento Multissetorial Integrado):** Percentual de empresas atendidas em pelo menos dois dos setores de fomento (`CNPJ em pelo menos 2 setores ÷ CNPJ atendidos nos setores de fomento × 100`).
- **Análise Exploratória de Tendências e Projetos (`sistema/backend/ai_docs/insights.py`):**
  - Serializa lançamentos de indicadores, atendimentos e prazos de projetos/tarefas (sem dados pessoais ou empresariais) para identificação qualitativa de tendências, anomalias e riscos de atraso.
- **Endpoints Autenticados da API (`sistema/backend/ai_docs/views.py` e `urls.py`):**
  - `GET /api/v1/assistente/status/` e `POST /api/v1/assistente/perguntar/` (Chat unificado RAG/NLP)
  - `GET /api/v1/dashboard/cruzados/` e `POST /api/v1/dashboard/cruzados/perguntar/` (Indicadores cruzados IC-01 a IC-04)
  - `POST /api/v1/dashboard/perguntar/` (Consulta aos lançamentos manuais do dashboard)
  - `GET /api/v1/analise-ia/status/` e `POST /api/v1/analise-ia/perguntar/` (Análise qualitativa de indicadores e projetos)
  - `GET /api/v1/documentos/status/` e `POST /api/v1/documentos/perguntar/` (Consulta documental dedicada)

---

## 3. Modelos de Linguagem e Tecnologias Utilizadas

### 3.1. Modelos de Inteligência Artificial (Executados via Ollama Local)
1. **`qwen2.5:1.5b` (Qwen 2.5 de 1,5 bilhão de parâmetros)** — **Modelo Principal do Assistente RAG e Análise IA:**
   - Utilizado no chat unificado (`ai_docs/rag.py`) e na análise exploratória de indicadores e projetos (`ai_docs/insights.py`).
   - Escolhido por oferecer alto desempenho em língua portuguesa, respeito rigoroso à formatação JSON e execução leve em CPU (sem exigir placa de vídeo dedicada).
2. **`llama3.2:3b` (Llama 3.2 de 3 bilhões de parâmetros, da Meta)** — **Modelo de Consultas Documentais e Dashboard:**
   - Utilizado no indexador/consulta documental (`gafia_docs.py`) e nas consultas dedicadas de indicadores do dashboard (`ai_docs/dashboard.py`).
3. **`nomic-embed-text`** — **Modelo de Embeddings Vetoriais:**
   - Responsável por transformar os blocos de texto dos PDFs e documentos em vetores numéricos para a busca por similaridade semântica no **LlamaIndex**.
4. **Motor NLP Local Integrado (`local_nlp_answer` em Python/Django):**
   - Motor determinístico embarcado no backend que analisa a intenção da pergunta e responde instantaneamente com base no ORM do Django e no `docstore.json`, atuando como contingência de alta disponibilidade.

### 3.2. Matriz Tecnológica Completa

| Camada | Tecnologia / Modelo | Função no Sistema |
| --- | --- | --- |
| **Linguagem e Backend** | Python 3.14.10 + Django 5.2 + Django REST Framework | Regras de negócio, autenticação JWT, filtro por setor (RBAC), cálculos exatos e endpoints da API |
| **Orquestração RAG** | LlamaIndex (`llama-index-core`) | Leitura de PDFs/Markdown, chunking (512 tokens), indexação vetorial e recuperação de contexto |
| **Servidor de IA Local** | Ollama (`http://127.0.0.1:11434`) | Execução local dos modelos de linguagem e de embeddings sem uso de nuvem |
| **LLM RAG / Análise** | `qwen2.5:1.5b` (`temperature=0`) | Geração de respostas em português com saída JSON estrita e baixa latência em CPU |
| **LLM Dashboard / Docs** | `llama3.2:3b` (`temperature=0`) | Seleção de indicadores e redação baseada em snapshots fechados e documentos |
| **Modelo de Embeddings** | `nomic-embed-text` | Vetorização semântica dos documentos oficiais do projeto |
| **Frontend** | HTML5, CSS3, JavaScript Vanilla (`assistente.html` / `assistente.js`) | Interface de chat responsiva com seleção de período e exibição das fontes consultadas |

---

## 4. Governança, Segurança da Informação e Conformidade LGPD

1. **Isolamento do Banco de Dados (Zero Text-to-SQL):** O modelo de IA **nunca** recebe acesso ao banco de dados nem executa consultas SQL. Toda leitura é feita pelo ORM do Django com filtros estritos de permissão.
2. **Controle de Acesso Baseado em Perfil e Setor (RBAC):**
   - **Administradores** consultam dados consolidados de todos os setores.
   - **Gestores** recebem no contexto da IA exclusivamente os registros do seu próprio setor (`id_setor`).
   - **Indicadores Cruzados (IC-01 a IC-04)** exigem a permissão individual `visao_estrategica=True`.
   - **Colaboradores** sem permissão de gestão são bloqueados na camada de view (`HTTP 403 Forbidden`).
3. **Anonimização de Dados Empresariais e Pessoais (LGPD):**
   - O cruzamento entre setores por CNPJ ocorre exclusivamente dentro do backend Python. O contexto enviado à IA contém apenas agregados ou eventos anonimizados (`atendimento:1`, `projeto:2`), **jamais expondo CNPJ, razão social ou hashes de senha**.
4. **Prevenção contra Alucinação Matemática:**
   - A IA é proibida de calcular percentuais ou taxas por conta própria. Todos os indicadores (somas mensais e IC-01 a IC-04) são pré-calculados pelo Django. Quando um denominador é zero, o sistema informa explicitamente que o índice é **"não calculável"**.
5. **Mitigação de *Prompt Injection* e Validação de Citações:**
   - Os prompts de sistema tratam perguntas e documentos estritamente como dados. Qualquer referência citada pelo modelo que não pertença ao conjunto autorizado daquela requisição (`allowed`) é descartada antes da resposta.

---

## 5. Textos Prontos para Preenchimento do TAP (Termo de Abertura do Projeto)

### 5.1. Objetivo do Módulo de IA (Para o campo "Objetivos / Descrição do Produto")
> Implantar no sistema SIGDEI um Assistente Inteligente baseado em Processamento de Linguagem Natural (NLP) e arquitetura RAG Híbrida (Retrieval-Augmented Generation) com execução 100% local, permitindo que gestores, secretários e administradores consultem, por meio de perguntas em português natural, documentos técnicos do projeto, indicadores setoriais, atendimentos, andamento de projetos/tarefas e indicadores estratégicos cruzados (IC-01 a IC-04), com citação auditável das fontes e respeito integral às permissões de cada perfil.

### 5.2. Entregáveis Principais (Para o campo "Principais Entregas / Pacotes da EAP 1.8")
1. **Indexador Documental Local (`gafia_docs.py` e `.local_index/`):** Pipeline de extração textual, fragmentação e indexação vetorial de arquivos PDF e Markdown com validação de integridade via SHA-256.
2. **Motor de Cálculo de Indicadores Cruzados (`cross_indicators.py`):** Apuração automatizada e auditável das métricas multissetoriais IC-01 (SEBRAE → Crédito), IC-02 (Vagas PAT por R$ 100 mil de crédito), IC-03 (Jornada SEBRAE → Crédito → PAT) e IC-04 (Integração Multissetorial).
3. **API de Assistente RAG Híbrido e NLP (`ai_docs`):** Endpoints REST autenticados via JWT que unificam dados estruturados do banco de dados e documentos indexados, com anonimização LGPD e motor NLP local de contingência.
4. **Interface Web do Assistente (`assistente.html` / `assistente.js`):** Tela integrada ao painel do SIGDEI com filtro de período, histórico de mensagens em sessão e exibição transparente das fontes utilizadas em cada resposta.

### 5.3. Premissas (Para o campo "Premissas do Projeto")
- Execução integralmente local (On-Premises) utilizando Python 3.14, Django REST Framework, LlamaIndex e Ollama (`qwen2.5:1.5b`, `llama3.2:3b` e `nomic-embed-text`), sem custos de API externa ou dependência de conectividade com provedores de nuvem.
- Disponibilidade de documentos em formato digital com texto selecionável (PDFs textuais, Markdown, DOCX, TXT ou CSV).

### 5.4. Restrições (Para o campo "Restrições do Projeto")
- Dados identificáveis de empresas (CNPJ e razão social) e credenciais de usuários não podem ser enviados ao modelo de linguagem sob nenhuma hipótese (conformidade LGPD).
- O modelo de IA não deve realizar cálculos matemáticos de indicadores nem acessar diretamente o banco de dados; todo cálculo oficial deve ser processado e validado pelo backend Django.
- O acesso ao assistente é restrito aos perfis autorizados (Administrador, Gestor e usuários com permissão de Visão Estratégica).

### 5.5. Riscos Identificados e Respostas Planejadas (Para a Matriz de Riscos do TAP)

| Risco Identificado | Impacto | Resposta / Mitigação Implantada |
| --- | --- | --- |
| **Lentidão ou indisponibilidade do servidor Ollama em computadores sem placa de vídeo dedicada (GPU)** | Médio | Adoção de modelo compacto (`qwen2.5:1.5b`) e implantação de um **Motor NLP Local Integrado** no Django (`local_nlp_answer`), que responde instantaneamente às perguntas do sistema mesmo se o Ollama estiver offline. |
| **Alucinação da IA ou erro em cálculos de indicadores públicos** | Alto | Configuração de `temperature=0`, pré-cálculo de todos os indicadores no backend Python (`cross_indicators.py` e `dashboard.py`) e validação estrita do schema JSON retornado. |
| **Vazamento de dados entre setores ou exposição de CNPJ** | Alto | Filtragem prévia no ORM do Django pelo `id_setor` do usuário autenticado, remoção de CNPJ/razão social antes da montagem do prompt e descarte automático de referências fora do escopo autorizado. |
| **Desatualização do índice após inclusão de novos PDFs** | Baixo | Geração de manifesto com hashes SHA-256 (`manifest.json`) que detecta automaticamente alterações nos arquivos e recarrega o índice no backend. |
