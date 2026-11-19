# Sistema de Gestão do Departamento de Desenvolvimento Econômico — Iracemápolis/SP

> Este é o README recebido com o código original. Para executar a versão integrada com o assistente documental local, use [as instruções da pasta GAFIA](../README.md). Os comandos de execução mais abaixo são um rascunho do projeto original.

Projeto Interdisciplinar (PI-IV) — Sistemas de Informação - Fundação Hermínio Ometto (FHO)

## Sobre o projeto

O Departamento de Desenvolvimento Econômico da Prefeitura Municipal de Iracemápolis (SP) não dispõe de ferramentas tecnológicas que permitam centralizar e acompanhar, de forma eficiente, as informações produzidas pelos seus diferentes setores. Isso dificulta tanto a gestão do dia a dia quanto a análise estratégica do desenvolvimento econômico do município.

Este projeto propõe um **sistema web** para auxiliar os gestores públicos na conferência de cumprimento de metas e na análise da realidade do desenvolvimento municipal, com foco em criação de empresas, geração de vagas de emprego e fortalecimento do empreendedorismo local.

O projeto está alinhado ao **Objetivo de Desenvolvimento Sustentável (ODS) nº 9** — Indústria, Inovação e Infraestrutura — da Agenda 2030 da ONU.

##  Objetivos

- Centralizar os registros de produção dos setores do Departamento (SEBRAE-Aqui, PAT, Banco do Povo e PROCON).
- Permitir o acompanhamento de indicadores de desempenho por setor, com dashboards e relatórios.
- Cruzar informações entre setores para gerar indicadores estratégicos (ex.: empresas atendidas pelo SEBRAE-Aqui e financiadas pelo Banco do Povo que geraram vagas registradas no PAT).
- Disponibilizar um assistente com IA para consultas em linguagem natural sobre os indicadores cruzados.

##  Setores contemplados

| Setor | Função |
|---|---|
| **SEBRAE-Aqui** | Orientação e capacitação de micro e pequenas empresas/MEIs |
| **PAT** (Posto de Atendimento ao Trabalhador) | Intermediação de mão de obra e cadastro de vagas de emprego |
| **Banco do Povo** | Concessão de microcrédito a empreendedores locais |
| **PROCON** | Defesa e orientação ao consumidor |

##  Funcionalidades principais

- Autenticação e controle de acesso por perfil (administrador, gestor, colaborador).
- Cadastro e acompanhamento de indicadores por setor, com visualização em dashboard (gráficos de barra, linha e donut, conforme o tipo de dado).
- Registro e numeração automática de ofícios.
- Gestão de projetos e tarefas por setor, com status visual (em andamento, concluído no prazo, atrasado).
- Cadastro de empresas por CNPJ, com vínculo automático entre setores que já atenderam a mesma empresa.
- Relatório de impacto cruzado entre setores.
- Assistente de IA para consultas em linguagem natural sobre os indicadores.

##  Tecnologias utilizadas

- **Backend:** Python
- **Frontend:** HTML5, CSS3, JavaScript
- **Banco de dados:** PostgreSQL (administrado via DBeaver)
- **Automação de fluxos:** n8n
- **IA / busca semântica:** LlamaIndex + OpenAI ou Llama
- **Hospedagem:** VPS

##  Estrutura do repositório

```
/docs         → documentação do projeto (requisitos, BPMN, TAP)
/backend      → código-fonte da API
/frontend     → código-fonte da interface web
/database     → scripts e modelagem do banco de dados
```

> A estrutura será ajustada conforme a organização real do repositório, assim que o desenvolvimento começar.

##  Como executar o projeto

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd <nome-do-repositorio>

# Configure as variáveis de ambiente (banco de dados, chaves de API etc.)
cp .env.example .env

# Instale as dependências do backend
cd backend
pip install -r requirements.txt

# Execute as migrações do banco de dados
# (comando a definir conforme ORM/ferramenta escolhida)

# Inicie o servidor
python main.py
```

> Modelo inicial. Será atualizado com os comandos reais assim que a stack estiver definida e implementada.

##  Equipe

| Nome | Papel |
|---|---|
| Giovana Jacobucci | Engenheira de IA e Dados |
| Kael Vicente Dipres | Scrum Master |
| Kaio Bueno de Camargo | Desenvolvedor Back-end (IA)/ QA |
| Sofia Camargo Nunes | Product Owner e Arquiteta de Software |
| Virna Karina do Amaral | Desenvolvedora Front-end |

##  Documentação

A documentação completa do projeto (proposta, requisitos funcionais e não-funcionais, regras de negócio, diagramas BPMN e critérios de aceite) está disponível na pasta [`/docs`](./docs).

##  Licença

Projeto acadêmico desenvolvido para a disciplina de Projeto Interdisciplinar IV. Uso restrito a fins educacionais, salvo autorização em contrário.
