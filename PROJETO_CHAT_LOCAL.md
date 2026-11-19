# GAFIA: chat local com consulta a documentos

Este projeto adiciona um chat em Python que responde perguntas a partir de arquivos locais. Ele usa **Ollama** para executar os modelos no computador e **LlamaIndex** para localizar trechos relevantes dos documentos. Não precisa de VPS, chave de API ou envio dos documentos a um serviço de IA externo.

O chat documental agora está ligado ao backend Django e ao menu do SIGDEI em `sistema/`. O fluxo n8n existente em `fluxo_n8n_chat_dashboard_gafia.json` trata dos indicadores cruzados do dashboard e permanece separado. As instruções completas de execução do sistema integrado estão em `README.md`.

## Como funciona

```text
documentos/ + sistema/docs/ + sistema/README.md
    → extração do texto
    → divisão em trechos + embeddings locais
    → índice persistido em .local_index/
    → pergunta no navegador
    → busca dos 3 trechos mais próximos
    → Llama 3.2 3B via Ollama
    → resposta + nomes dos arquivos e páginas disponíveis
```

O índice precisa ser recriado quando um arquivo for incluído, removido ou alterado. O programa detecta isso e pede nova indexação. PDFs que contêm apenas imagens precisam passar por OCR antes de serem indexados; o projeto não inclui OCR.

Cada pergunta é consultada de forma independente. A interface mantém as mensagens na tela durante a sessão, mas ainda não usa perguntas anteriores como contexto nem salva o histórico.

## Requisitos

- Windows 10/11 ou Linux, Python 3.11 ou 3.12 e Ollama instalado.
- Para a máquina descrita (16 GB de RAM, i5 de 11ª geração e vídeo integrado), comece com `llama3.2:3b`. O processamento pode ser lento em CPU; evite indexar muitos arquivos de uma vez no primeiro teste.
- Espaço em disco para os modelos, dependências Python, documentos e índice.

Modelos necessários no Ollama:

```powershell
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Use os modelos **locais** do Ollama. Confira se o aplicativo está aberto antes de indexar ou conversar.

## Instalação no Windows

Abra PowerShell na pasta deste projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Os PDFs recebidos já estão em `sistema/docs/` e entram no índice automaticamente, junto com `sistema/README.md`. Coloque arquivos adicionais em `documentos/`. Subpastas são aceitas. Os formatos ativados são `.pdf`, `.docx`, `.txt`, `.md` e `.csv`. Arquivos adicionados em `documentos/` não são incluídos no Git por padrão.

Depois execute:

```powershell
.\.venv\Scripts\python.exe gafia_docs.py index
.\.venv\Scripts\python.exe gafia_docs.py serve
```

Abra **http://127.0.0.1:8765** no navegador. Para testar pelo terminal:

```powershell
.\.venv\Scripts\python.exe gafia_docs.py ask "Qual é o assunto dos documentos?"
```

Ao mudar documentos ou modelos, rode `index` novamente. O servidor independente `serve` precisa ser reiniciado; o backend Django recarrega o índice quando o manifesto muda. O índice local fica em `.local_index/` e não é enviado ao Git.

Se `python` não estiver instalado no Windows, instale Python 3.11/3.12 e abra um terminal novo. O comando `py -3.11` pode substituir `python` na criação do ambiente virtual, se o Python Launcher estiver disponível.

## Rodar no Google Antigravity

O Antigravity abre uma **pasta de projeto local** e oferece um terminal integrado. Adicione esta pasta (`gafia`) a um projeto no Antigravity e escolha **Local mode** para trabalhar sobre os mesmos arquivos. No terminal dele, execute exatamente os comandos de instalação, indexação e inicialização acima. Mantenha o Ollama rodando no mesmo computador.

O chat independente abre em **http://127.0.0.1:8765**. O chat integrado aparece no menu **Assistente** do SIGDEI depois de iniciar Django e o frontend conforme o `README.md`. Ele não aparece automaticamente como conversa dentro da interface do agente Antigravity. Se você clonar o repositório em outra máquina, copie os arquivos adicionais de `documentos/` e recrie o índice nessa máquina.

Guia oficial do Antigravity: https://antigravity.google/docs/getting-started

## Configuração opcional

As variáveis de ambiente permitem trocar os modelos ou o endereço do Ollama:

```powershell
$env:GAFIA_CHAT_MODEL = "llama3.2:3b"
$env:GAFIA_EMBED_MODEL = "nomic-embed-text"
$env:OLLAMA_URL = "http://127.0.0.1:11434"
```

Por padrão, o chat independente aceita conexões apenas do próprio computador (`127.0.0.1`). Para um teste em rede local, é possível definir `GAFIA_CHAT_TOKEN` e iniciar com `serve --host 0.0.0.0`; o campo de token aparece na página. Essa opção usa HTTP simples. A versão integrada no SIGDEI exige JWT e perfil Administrador ou Gestor. Nenhuma das duas versões separa permissões por documento; isso precisa ser implementado antes de incluir documentos restritos de setores diferentes.

## Estrutura

| Arquivo/pasta | Função |
| --- | --- |
| `gafia_docs.py` | Comandos de indexação, perguntas e servidor local |
| `web/` | Interface do chat no navegador |
| `documentos/` | Arquivos de entrada fornecidos pelo usuário |
| `sistema/docs/` | Documentos recebidos no ZIP e indexados automaticamente |
| `sistema/backend/ai_docs/` | Rotas autenticadas usadas pelo frontend SIGDEI |
| `.local_index/` | Índice gerado e persistido localmente |
| `requirements.txt` | Dependências Python |
| `README_fluxo_n8n.md` | Fluxo existente dos indicadores do dashboard |

## Próximos passos para o GAFIA

1. Indexar os PDFs recebidos e conferir a extração de texto e as fontes das respostas.
2. Definir quais usuários podem consultar cada conjunto de documentos. Essa regra deve ser aplicada pelo backend **antes da busca**, como já foi previsto para os indicadores do dashboard.
3. Se desejado, combinar respostas de documentos com os snapshots autorizados dos indicadores.
4. Adicionar OCR para PDFs digitalizados, atualização automática do índice e auditoria de perguntas/respostas quando esses requisitos forem definidos.

Referências técnicas: [leitura de arquivos no LlamaIndex](https://developers.llamaindex.ai/python/framework/module_guides/loading/simpledirectoryreader/), [persistência do índice](https://developers.llamaindex.ai/python/framework/module_guides/storing/customization/) e [RAG local com Ollama](https://developers.llamaindex.ai/python/examples/cookbooks/local_rag_with_chroma_and_ollama/).
