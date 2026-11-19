![Status](https://img.shields.io/badge/STATUS-CONCLUÍDO-success?style=for-the-badge)
<div align="center">
  
# Plataforma Inteligente para Análise e Gestão de Processos

### Departamento de Desenvolvimento Econômico • Prefeitura Municipal de Iracemápolis

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Django](https://img.shields.io/badge/Django-REST%20Framework-green?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?logo=postgresql)
![ODS 9](https://img.shields.io/badge/ODS-9-orange)

Sistema desenvolvido por estudantes do 5º período de Sistemas de Informação da Fundação Hermínio Ometto para apoiar a modernização da gestão pública municipal.

</div>

---

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [Arquitetura](#️-arquitetura)
- [Dashboards](#-dashboards)
- [Requisitos Não Funcionais](#-requisitos-não-funcionais)
- [Endpoints Principais](#-principais-endpoints)
- [Estrutura de Dados](#-estrutura-de-dados)
- [Metodologia](#-metodologia)
- [Equipe](#-equipe-gafia)
- [Links](#-links)

---

# 📌 Sobre o Projeto

O projeto foi desenvolvido no âmbito da disciplina de **Projeto Interdisciplinar III**, da Fundação Hermínio Ometto, alinhado ao tema:

> **Plataforma Inteligente para Monitoramento e Otimização de Infraestruturas Sustentáveis**

e ao **Objetivo de Desenvolvimento Sustentável (ODS 9) – Indústria, Inovação e Infraestrutura**.

A solução tem como objetivo modernizar os processos do Departamento de Desenvolvimento Econômico por meio da centralização de informações, acompanhamento de indicadores, gestão de projetos e controle documental.

A plataforma permite que colaboradores dos setores:

- 👷🏽 PAT
- 📈 SEBRAE
- ⚖️ PROCON
- 💰 Banco do Povo

registrem atividades, projetos e produções, enquanto gestores acompanham resultados através de dashboards e relatórios gerenciais.

---

# ✨ Funcionalidades

## 👤 Gestão de Usuários

- Cadastro de usuários
- Edição de usuários
- Exclusão de usuários
- Controle de níveis de acesso
- Login e autenticação
- Alteração de senha
- Consulta e filtros

## 📊 Gestão de Indicadores

- Cadastro de indicadores
- Registro de atividades
- Dashboards automáticos
- Cards métricos
- Filtros por período
- Filtros por setor
- Exportação de relatórios PDF

## 📄 Gestão de Ofícios

- Cadastro de ofícios
- Numeração automática
- Associação automática de usuário e setor
- Consulta e filtros
- Rastreabilidade documental

## 📁 Gestão de Projetos

- Cadastro de projetos
- Gestão de tarefas
- Controle de prioridade
- Tags de status
- Barra de progresso
- Cronograma de execução
- Controle por setor

---

# 🛠️ Tecnologias Utilizadas

<div align="center">

<img src="https://skillicons.dev/icons?i=python,django,postgresql,html,css,js,git,github,vscode" />

</div>

### Backend

- Python
- Django
- Django REST Framework

### Frontend

- HTML5
- CSS3
- JavaScript

### Banco de Dados

- PostgreSQL

### Controle de Versão

- Git
- GitHub

---

# 🧱 Arquitetura

```text
Frontend Web
      │
      ▼
 REST API Django
      │
      ▼
 PostgreSQL
```

A comunicação ocorre através de requisições HTTP/HTTPS entre cliente e servidor.

---

# 📈 Dashboards

O sistema gera dashboards automaticamente de acordo com o tipo do indicador.

| Tipo do Indicador | Visualização |
|-------------------|--------------|
| Número | 📊 Gráfico de Barras |
| Tempo | 📈 Gráfico de Linha |
| Porcentagem | 🍩 Gráfico Donut |

---

# 🔐 Requisitos Não Funcionais

- ✅ Autenticação obrigatória
- ✅ Senhas criptografadas
- ✅ Compatibilidade HTTPS
- ✅ Responsividade
- ✅ Integração REST API
- ✅ Interface intuitiva
- ✅ Controle de permissões

---

# 📡 Principais Endpoints

## Setores

```http
POST /setores/
GET /setores/
PUT /setores/{id}/
DELETE /setores/{id}/
```

## Usuários

```http
POST /usuarios/
GET /usuarios/
PUT /usuarios/{id}/
DELETE /usuarios/{id}/
```

## Projetos

```http
POST /projetos/
GET /projetos/
PUT /projetos/{id}/
DELETE /projetos/{id}/
```

## Indicadores

```http
POST /indicadores/
GET /indicadores/
PUT /indicadores/{id}/
DELETE /indicadores/{id}/
```

---

# 📥 Exemplo JSON

### Cadastro de Usuário

```json
{
  "nome": "João Silva",
  "funcao": "Auxiliar Administrativo",
  "matricula": 202610,
  "id_setor": 1
}
```

---

# 🔄 Metodologia

### Modelo de Desenvolvimento

- Modelo Evolutivo
- Scrum
- Metodologias Ágeis

### Cerimônias

- Sprint Planning
- Daily Scrum
- Sprint Review
- Sprint Retrospective

---

# 👥 Equipe GAFIA

<table>
<tr>
<td align="center">

### Sofia Camargo Nunes

<a href="https://www.linkedin.com/in/sofia-camargo-nunes-a64185304/">
<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"/>
</a>

</td>

<td align="center">

### Giovana Jacobucci

<a href="https://www.linkedin.com/in/giovana-jacobucci/">
<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"/>
</a>

</td>

<td align="center">

### Kael Vicente Dipres

<a href="https://www.linkedin.com/in/kael-vicente-dipres-781343385/">
<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"/>
</a>

</td>

<td align="center">

### Virna Karina do Amaral Pereira

<a href="https://www.linkedin.com/in/virna-amaral-39018b298/">
<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"/>
</a>

</td>
</tr>
</table>

---

# 🔗 Links

### 📅 Cronograma do Projeto

[📌 Acessar Cronograma](https://github.com/users/sofia-camargo/projects/2/views/1)

---

# 📚 Considerações Finais

A plataforma foi concebida para apoiar a transformação digital da administração pública municipal, promovendo:

- Centralização de informações;
- Monitoramento de indicadores;
- Gestão de projetos;
- Rastreabilidade documental;
- Apoio à tomada de decisões.

Dessa forma, contribui para uma gestão pública mais eficiente, organizada e alinhada aos princípios de inovação tecnológica e desenvolvimento sustentável.

---

<div align="center">

### 👩🏻‍💻 Desenvolvido pela Equipe GAFIA

**Fundação Hermínio Ometto • Sistemas de Informação • 2026**

</div>
