# Assistente do dashboard GAFIA no n8n

O arquivo `fluxo_n8n_chat_dashboard_gafia.json` contém um fluxo importável para o chat do sistema. Ele atende ao recorte inicial de indicadores cruzados IC-01 a IC-04 do projeto de Iracemápolis. A estrutura foi importada e reexportada em uma instância de teste n8n 2.16.1: os 8 nós, 7 conexões e parâmetros foram preservados.

## Caminho dos dados

```text
Chat do sistema → backend autenticado → webhook n8n
  → validação de pergunta/período
  → backend consulta views autorizadas e devolve agregados do dashboard
  → modelo redige resposta baseada apenas no snapshot
  → n8n anexa origem (setor, período e view)
  → backend registra pergunta, resposta e views
  → chat recebe a resposta
```

O backend, não o modelo, deve decidir o que o usuário pode ler. Ele deve validar o token recebido, verificar a permissão individual de **visão estratégica** e executar consultas somente nas views fechadas de IC-01 a IC-04. Administrador sem essa permissão não recebe acesso. O endpoint deve enviar ao n8n apenas dados agregados, sem CNPJ, razão social ou identificação de empresas reclamadas no PROCON. O modelo não executa SQL.

## O que configurar após importar

**Antes de importar:** confira o indicador de conexão no canto superior direito do editor. Se ele mostrar `Offline`, recarregue a página e espere a conexão voltar. Enquanto a instância estiver offline, o editor pode mostrar nós padrão como `?` e ocultar as conexões. Se continuar offline, o responsável pela instância provisória precisa restabelecer o serviço/conexão do editor. A VPS definitiva não é necessária para desenhar ou importar este fluxo.

1. Crie um workflow novo no n8n e use **Import from File** para selecionar `fluxo_n8n_chat_dashboard_gafia.json`. Descarte o fluxo anterior que apareceu com ícones `?`.
2. Confira que o canvas mostra 8 nós reconhecidos e conectados. Se aparecer `?`, a sua instância não está carregando um dos nós padrão ou usa uma versão incompatível; nesse caso, precisamos da mensagem exibida ao clicar em um desses blocos para ajustar à instalação específica.
3. Nos nós **Consultar snapshot autorizado** e **Registrar auditoria**, troque `https://SEU-BACKEND` pela URL interna HTTPS da API Python. Esses dois endpoints são um **contrato proposto**; o PDF não fornece rotas implementadas.
4. No nó **Redigir resposta com IA**, selecione uma credencial n8n **Header Auth** com nome de cabeçalho `Authorization` e valor `Bearer SUA_CHAVE_OPENAI`. A chave fica na credencial, nunca no JSON do fluxo.
5. Mantenha o webhook acessível apenas ao backend/proxy do sistema; aplique limite de requisições. A interface do usuário deve chamar o backend, que encaminha a requisição ao n8n. O backend deve passar o token do usuário no cabeçalho `Authorization`.
6. Teste pela URL de teste do webhook. Depois publique o fluxo e use a URL de produção, que tem o caminho `/webhook/gafia/chat-dashboard`.

## Contrato de entrada

```http
POST /webhook/gafia/chat-dashboard
Authorization: Bearer <token do usuário autenticado>
Content-Type: application/json
```

```json
{
  "question": "Quantas empresas atendidas pelo SEBRAE chegaram ao crédito no trimestre?",
  "period_start": "2026-07-01",
  "period_end": "2026-09-30",
  "session_id": "sessao-123"
}
```

`session_id` é opcional. A validação inicial exige pergunta de até 1000 caracteres, datas ISO e token Bearer. A API do snapshot deve **revalidar** token, período e permissão; a validação do n8n não substitui autorização no backend.

## Contrato proposto para o backend

`POST /api/ai/dashboard-snapshot` recebe `period_start` e `period_end` e o cabeçalho `Authorization`. Exemplo de resposta estrutural, **sem valores fictícios**:

```json
{
  "period": {"start": "2026-07-01", "end": "2026-09-30"},
  "generated_at": "2026-10-19T12:00:00-03:00",
  "indicators": [
    {
      "id": "IC-01",
      "name": "Trilha de fomento SEBRAE → Banco do Povo",
      "value": null,
      "unit": "%",
      "sector_sources": ["SEBRAE", "Banco do Povo"],
      "view": "nome_da_view_aprovada",
      "details": {}
    }
  ]
}
```

O valor acima é um molde; o endpoint deve retornar números reais calculados dos atendimentos. `details` pode incluir somente agregados aprovados que ajudem a responder perguntas. A implementação deve limitar o tamanho do snapshot e devolver apenas os indicadores do período escolhido. Quando não houver dados, devolva `indicators: []`, sem simular valores.

`POST /api/ai/chat-audit` recebe `question`, `answer`, `views`, `period` e `session_id`, com o mesmo token. Ele deve registrar também o usuário autenticado no backend e a data/hora. Se a gravação falhar, o fluxo falha e não envia uma resposta apresentada como auditada.

Resposta entregue ao chat:

```json
{
  "answer": "Texto em português baseado nos dados retornados",
  "sources": [
    {
      "indicator_id": "IC-01",
      "sector": ["SEBRAE", "Banco do Povo"],
      "view": "nome_da_view_aprovada",
      "period": {"start": "2026-07-01", "end": "2026-09-30"}
    }
  ],
  "period": {"start": "2026-07-01", "end": "2026-09-30"},
  "generated_at": "2026-10-19T12:00:00-03:00"
}
```

## Critérios de aceite

- Usuário sem visão estratégica recebe 403 do backend e o modelo não é chamado.
- Uma pergunta sobre IC-01 a IC-04 recebe resposta com período, setor e view de origem.
- Período sem registros produz uma resposta de ausência de dados, sem números estimados.
- A auditoria registra pergunta, resposta, usuário e views consultadas.
- Nenhum identificador de empresa reclamada no PROCON chega ao modelo.

A apresentação cita detecção de anomalias e previsão de risco de projetos. Essas funções podem ser fluxos futuros, após existirem views, dados e critérios de validação próprios; o chat acima cobre a consulta aos indicadores cruzados exigida para a primeira versão.
