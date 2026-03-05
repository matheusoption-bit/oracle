# RUNBOOK - oracle

## 1. Objetivo
Este runbook descreve como preparar, executar, observar e manter o `oracle` (orquestrador LangGraph + UI Next.js).

## 2. Pré-requisitos
- Node.js 20+
- pnpm
- Python 3.11+ (recomendado para compatibilidade de wheels)
- Docker Desktop (Phoenix + Postgres local)
- Conta com chaves: Anthropic, Google, OpenAI, E2B, Supabase, Clerk, LangSmith

## 3. Setup Inicial
1. Instalar dependências Node:
   - `pnpm install`
2. Criar/ativar venv Python:
   - Windows: `python -m venv orchestrator/venv`
   - `orchestrator\\venv\\Scripts\\python -m pip install --upgrade pip`
3. Instalar libs Python:
   - `orchestrator\\venv\\Scripts\\python -m pip install -r orchestrator/requirements.txt`
4. Preparar variáveis:
   - `cp .env.example .env` (ou `Copy-Item .env.example .env`)
   - Preencher todos os valores no `.env`

## 4. Infraestrutura
1. Subir observabilidade e banco local:
   - `cd docker`
   - `docker compose up -d`
2. Acessar Phoenix:
   - `http://localhost:6006`

## 5. Execução do Orquestrador
1. Rodar task no oracle:
   - `orchestrator\\venv\\Scripts\\python -m orchestrator.main --task "sua task aqui"`
2. Outputs esperados:
   - `workspace/plan.md`
   - `workspace/todo.md`
   - `workspace/decisions.md`
   - `workspace/tool_outputs/*.json`

## 6. Execução da UI
1. Ambiente de desenvolvimento:
   - `pnpm dev`
2. Tela de operações:
   - `http://localhost:3000/ops`
3. API de disparo:
   - `POST /api/ops` com body `{ "task": "..." }`

## 7. RAG (Supabase + pgvector)
1. Executar SQL de criação de extensão/tabela/índice no Supabase.
2. Confirmar variáveis:
   - `DATABASE_URL`
   - `SUPABASE_URL`
   - `SUPABASE_PASSWORD`
3. Ingestão:
   - Usar `RAGEngine.ingest_repository(...)`
4. Consulta:
   - Usar `RAGEngine.query_codebase(...)`

## 8. Segurança e Segredos
- Nunca commitar `.env`.
- Sem chaves hardcoded no código.
- Opcional recomendado: Doppler para gerenciamento centralizado.

## 9. Verificações Operacionais
- Lint frontend: `pnpm lint`
- Build frontend: `pnpm build`
- Testes Python: `pytest orchestrator/tests/`
- Lint Python: `orchestrator\\venv\\Scripts\\python -m ruff check orchestrator`

## 10. Troubleshooting
- `ModuleNotFoundError` em libs Python:
  - Reinstale requirements no venv correto.
- Erro `pg_config` no `psycopg2-binary`:
  - Use Python versão com wheel disponível (ex.: 3.11) ou instale toolchain/PostgreSQL headers.
- `docker: command not found`:
  - Instale Docker Desktop e reinicie terminal.
- `doppler: command not found`:
  - Instale Doppler CLI e execute `doppler login`.

## 11. Rotina de Operação
1. Validar `.env` e serviços (`docker compose ps`)
2. Rodar uma task simples no orquestrador
3. Verificar logs em `workspace/logs/`
4. Revisar traces no Phoenix
5. Executar checks de lint/build/test antes de merge/deploy
