# API GAFIA - Sistema de Gerenciamento de Projetos

Este repositório contém a API REST desenvolvida para a 2ª Fase do Projeto Interdisciplinar. A aplicação foi construída utilizando o framework Django e Django Rest Framework, com persistência de dados em um banco PostgreSQL operando em arquitetura de rede local.

## 1. Engenharia de Software e Modelagem

### Refinamento de Artefatos
Os modelos de dados foram refinados para garantir a integridade referencial. O sistema utiliza chaves estrangeiras (Foreign Keys) para conectar Setores, Usuários e Projetos, impedindo a criação de registros órfãos e garantindo a consistência das informações.

### Diagrama de Casos de Uso (UML)
O sistema foi projetado para permitir que o ator principal (Administrador/Sistema) realize as operações fundamentais de gestão:
- Manter Setores (CRUD)
- Gerenciar Usuários e Responsáveis
- Controlar Ciclo de Vida de Projetos

### Requisitos Funcionais Principais
- RF01: Permitir o cadastro de setores com sigla e nome.
- RF02: Vincular usuários a setores específicos via ID.
- RF03: Registrar projetos associados a um usuário responsável.

---

## 2. Estrutura da API e Endpoints (CRUD)

A API segue o padrão REST, utilizando os métodos HTTP GET para consulta e POST para criação.

### Endpoints de Setores
- **GET /setores/**: Lista todos os setores cadastrados.
- **POST /setores/**: Cadastra um novo setor.
  - Entrada: `{"nome_setor": "string", "sigla": "string"}`

### Endpoints de Usuários
- **GET /usuarios/**: Lista todos os usuários e seus vínculos.
- **POST /usuarios/**: Cadastra um novo colaborador.
  - Entrada: `{"nome": "string", "funcao": "string", "matricula": int, "id_setor": int}`

### Endpoints de Projetos
- **GET /projetos/**: Consulta a lista de projetos ativos.
- **POST /projetos/**: Registra um novo projeto.
  - Entrada: `{"nome_projeto": "string", "data_inicio": "YYYY-MM-DD", "data_prazo": "YYYY-MM-DD", "status": "string", "id_responsavel": int}`

---

## 3. Configuração Técnica e Banco de Dados

### Conexão PostgreSQL
A API está configurada para se conectar a uma instância remota do PostgreSQL. A configuração de rede foi validada para permitir o tráfego na porta 5432, com autenticação via MD5/Trust configurada no arquivo pg_hba.conf do servidor de banco.

### Instalação
1. Clone o repositório.
2. Crie e ative o ambiente virtual (venv).
3. Instale as dependências: `pip install -r requirements.txt`.
4. Configure as credenciais de banco no arquivo `settings.py`.
5. Execute o servidor: `python manage.py runserver`.

## 4. Testes
Todas as rotas foram exaustivamente testadas via Postman, validando tanto os casos de sucesso (200 OK / 201 Created) quanto o tratamento de erros de integridade (400 Bad Request), garantindo que a lógica de negócio está alinhada à modelagem de dados.
"""
