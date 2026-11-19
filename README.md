# GAFIA / SIGDEI — projeto integrado

O código recebido em `setor-publico-main.zip` foi incorporado em `sistema/`. O projeto agora tem a interface SIGDEI, o backend Django, os documentos acadêmicos do sistema e o assistente documental local do GAFIA na mesma pasta de trabalho. Abra **esta pasta raiz** no Codex ou no Antigravity para realizar alterações.

## Onde está cada parte

| Caminho | Conteúdo |
| --- | --- |
| `sistema/backend/` | API Django de usuários, setores, indicadores, projetos e ofícios |
| `sistema/frontend/` | Interface HTML, CSS e JavaScript do SIGDEI |
| `sistema/docs/` | PDFs e imagem de documentação recebidos no ZIP |
| `origem/setor-publico-2.0/` | Cópia integral descompactada do ZIP, incluindo dependências, histórico Git, banco de teste, backup e lista de integrantes |
| `origem/setor-publico-main.zip` | Arquivo original preservado sem alterações |
| `documentos/` | Arquivos adicionais que você quiser disponibilizar ao assistente |
| `gafia_docs.py` | Indexação e consulta local com LlamaIndex e Ollama |
| `fluxo_n8n_chat_dashboard_gafia.json` | Protótipo anterior em n8n, sem integração ativa |

O menu **Assistente** oferece quatro consultas diretas ao Django: indicadores cruzados IC-01 a IC-04, lançamentos manuais do dashboard, análise IA de indicadores e projetos, e documentos. O modo cruzado exige permissão individual de visão estratégica; os modos de análise, dashboard e documentos exigem perfil Administrador ou Gestor. O Django calcula os ICs oficiais antes de responder e nunca envia CNPJ ao modelo. Não é preciso executar `gafia_docs.py serve` dentro do SIGDEI. A versão independente em `web/` continua disponível para testes locais.

## Primeiro uso no Windows

Instale Python 3.11 ou 3.12 e Ollama. Abra PowerShell nesta pasta raiz e execute:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r sistema\backend\requirements.txt
ollama pull llama3.2:3b
ollama pull nomic-embed-text
.\.venv\Scripts\python.exe gafia_docs.py index
.\.venv\Scripts\python.exe sistema\backend\manage.py migrate
.\.venv\Scripts\python.exe sistema\backend\manage.py bootstrap_admin
```

O índice inclui automaticamente `sistema/README.md`, os PDFs de `sistema/docs/` e arquivos PDF, DOCX, TXT, MD e CSV colocados em `documentos/`. Os arquivos gerados (`.venv/`, `.local_index/` e banco SQLite local) ficam fora do Git. Reexecute `index` quando mudar os documentos.

Para consultar **somente o dashboard**, o índice documental não é necessário. A tela envia pergunta e período a `POST /api/v1/dashboard/perguntar/`; o backend agrega os lançamentos do setor autorizado. O modo **Indicadores cruzados IC-01 a IC-04** usa `GET /api/v1/dashboard/cruzados/` para mostrar os valores calculados e `POST /api/v1/dashboard/cruzados/perguntar/` para responder no chat. O Ollama (`GAFIA_CHAT_MODEL`, em `OLLAMA_URL`, padrão `http://127.0.0.1:11434`) seleciona quais ICs respondem à pergunta; o backend monta o texto e os números finais. Se estiver desligado, perguntas centrais sobre IC-01 a IC-04 recebem uma resposta direta com os valores calculados no backend.

O modo **Análise IA de indicadores e projetos** usa `GET /api/v1/analise-ia/status/` e `POST /api/v1/analise-ia/perguntar/`. O backend filtra registros brutos pelo setor autorizado e período, retira dados de empresas e os envia ao Ollama local. O modelo interpreta possíveis anomalias, tendências e sinais qualitativos de atraso; a resposta cita somente referências presentes nos registros enviados. Esse modo não calcula os ICs oficiais e não produz probabilidade numérica de atraso. Os dados fictícios de setembro e outubro servem para demonstrar o fluxo, mas não sustentam uma previsão estatística confiável. O modelo padrão deste modo é `qwen2.5:1.5b` (`GAFIA_INSIGHTS_MODEL`), escolhido para execução local mais leve; em outro computador, instale-o com `ollama pull qwen2.5:1.5b`. O login no site do Ollama ou a conexão com GitHub não substituem o download do modelo local.

Para testar, selecione **Análise IA de indicadores e projetos**, período `2026-09-01` a `2026-10-26`, e pergunte “Há tendência nas Oficinas realizadas entre setembro e outubro?” ou “Quais projetos parecem em risco de atraso?”. Perguntas focadas em um indicador dão ao modelo um contexto menor e citações mais claras. Uma pergunta ampla pode receber a resposta de que o histórico não sustenta uma conclusão.

### Dados fictícios para testes

Depois das migrações e da criação do Administrador, execute `python sistema/backend/manage.py seed_demo` a partir da raiz. O comando insere 4 setores, 8 indicadores e 32 lançamentos divididos entre **setembro e outubro de 2026**, além de 2 projetos e 6 tarefas. Todos os indicadores, projetos e tarefas recebem o prefixo `[DEMO]`. O comando não altera usuários nem registros existentes e não duplica os dados ao ser executado novamente. Na tela do assistente, selecione o período de `2026-09-01` a `2026-10-26` para consultar os lançamentos; o Ollama precisa estar em execução para redigir a resposta.

Para testar os indicadores cruzados, execute depois `python sistema/backend/manage.py seed_cross_demo`. São criadas 5 empresas com CNPJ sintético validado e 10 atendimentos `[DEMO]` em setembro e outubro de 2026. Para o período de `2026-09-01` a `2026-10-26`, o resultado esperado é IC-01 **66,67% (2/3)**, IC-02 **2,50 vagas por R$ 100 mil**, IC-03 **1 empresa** e IC-04 **80% (4/5)**. O comando não duplica essa amostra.

Em **Atendimentos**, busque a empresa pelo CNPJ ou cadastre-a, depois registre o serviço no setor correspondente. O núcleo comum é empresa, setor, colaborador, data e desfecho. Uma liberação de crédito exige valor e data; uma vaga exige quantidade e data de abertura. O mesmo CNPJ conecta os registros entre setores. CNPJ numérico e alfanumérico têm os dois dígitos verificadores validados.

Os indicadores cruzados são calculados em `sector/cross_indicators.py` a partir de `Atendimento`, sem valores digitados manualmente: IC-01 = empresas SEBRAE com crédito posterior ÷ empresas SEBRAE; IC-02 = vagas abertas após o crédito pela mesma empresa ÷ (crédito liberado / R$ 100 mil); IC-03 = empresas com sequência SEBRAE → liberação de crédito → PAT; IC-04 = empresas em pelo menos dois dos setores SEBRAE, Banco do Povo e PAT ÷ empresas atendidas nesses setores. O PROCON fica fora desse cruzamento porque seu CNPJ é o do fornecedor reclamado. Denominador zero aparece como **não calculável**, sem inventar percentual.

O acesso ao consolidado e ao chat cruzado exige perfil Administrador, Gestor ou Secretário **e** `visao_estrategica=true`, concedida individualmente pelo Administrador na tela de Usuários. O primeiro Administrador não recebe essa permissão automaticamente. No banco local de teste, ela já foi concedida a `GAFIA-ADMIN`. A API retorna apenas agregados e origem por setor/período; não entrega CNPJ ou razão social ao modelo.

Em dois terminais, inicie o backend e o frontend:

```powershell
.\.venv\Scripts\python.exe sistema\backend\manage.py runserver 0.0.0.0:8000
```

```powershell
.\.venv\Scripts\python.exe -m http.server 5500 --bind 0.0.0.0 --directory sistema\frontend
```

No próprio computador, abra `http://127.0.0.1:5500/index.html`. Em outro dispositivo conectado à mesma rede, use o IPv4 atual do computador; nesta rede, `http://10.27.95.125:5500/index.html`. O frontend utiliza automaticamente esse mesmo host para chamar a API. Também é possível iniciar os dois servidores pelo `sistema/iniciar.bat` depois da instalação. O banco de teste presente no ZIP está preservado em `origem/setor-publico-2.0/`; a aplicação integrada usa um banco local novo. `bootstrap_admin` cria o primeiro usuário interativamente e pede a senha sem gravá-la na linha de comando. O modelo local também precisa estar acessível pelo Ollama durante a indexação e as perguntas.

## Antigravity

Adicione a pasta raiz `gafia` como projeto local no Antigravity. Use o terminal integrado para executar os comandos acima. Como o projeto usa arquivos locais, copie `documentos/` e recrie `.local_index/` ao trabalhar em outra máquina. Os PDFs de `sistema/docs/` já estão no projeto.

## Escopo atual

- O assistente responde com base em documentos e informa arquivo/página quando disponível. Cada pergunta é independente; não há memória de conversa ou OCR para PDFs digitalizados.
- O menu do assistente usa uma regra inicial por perfil. Ainda falta definir autorização por documento e auditoria para uso com material restrito.
- O modo legado do dashboard ainda consulta os indicadores e lançamentos manuais de `Atividade`, com filtro por período e setor. O modo cruzado consulta apenas os quatro cálculos derivados de `Atendimento` vinculado a `Empresa`. O modelo recebe agregados fechados e não executa SQL.
- O fluxo n8n permanece apenas como protótipo anterior. As rotas de snapshot e auditoria descritas em `README_fluxo_n8n.md` são contratos propostos, não usados pelo chat atual.
- O arquivo original incluía `.git`, dependências instaladas, caches, um banco SQLite de teste, um backup JSON e uma lista de integrantes com RA. Todos estão preservados em `origem/setor-publico-2.0/`, sem substituir a versão integrada de `sistema/`. A pasta `origem/` fica fora do Git por conter dados locais e histórico próprio; copie-a junto com `gafia` se transferir o projeto para outra máquina.

Detalhes do assistente: [PROJETO_CHAT_LOCAL.md](PROJETO_CHAT_LOCAL.md). Descrição original do sistema: [sistema/README.md](sistema/README.md).
