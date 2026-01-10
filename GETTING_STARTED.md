# Getting Started with Autonomous Data Agency v7.0

Este guia vai ajudá-lo a começar a usar o framework Autonomous Data Agency rapidamente.

## 🚀 Quick Start (Docker - Recomendado)

A maneira mais rápida de testar é usando Docker:

```bash
# Clone o repositório
git clone https://github.com/michael-eng-ai/autonomous-data-agency.git
cd autonomous-data-agency

# Configure a chave do Gemini
export GOOGLE_API_KEY=sua_chave_aqui

# Execute
docker-compose up --build
```

Acesse:
- **Interface Web**: http://localhost:5173
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs

## 📦 Instalação Local

### 1. Requisitos

- Python 3.11+
- Node.js 18+
- Google API Key (Gemini)

### 2. Backend (API)

```bash
# Clone e acesse o diretório
git clone https://github.com/michael-eng-ai/autonomous-data-agency.git
cd autonomous-data-agency

# Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Dependências
pip install -r requirements.txt

# Configure o .env
echo "GOOGLE_API_KEY=sua_chave_aqui" > .env

# Execute a API
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend (Web)

```bash
# Em outro terminal
cd web
npm install
npm run dev
```

## 🎯 Como Usar

### Via Interface Web

1. Acesse http://localhost:5173
2. Digite sua solicitação no chat, por exemplo:
   - "Quero criar um sistema de e-commerce com React e Python"
   - "Preciso de uma API de autenticação com FastAPI"
   - "Quero um dashboard de analytics com dados de vendas"

3. Acompanhe o progresso:
   - **Painel Central**: Status do processamento
   - **Painel Direita**: Log de eventos em tempo real

4. Quando finalizado, baixe o projeto gerado!

### Via API REST

```bash
# Iniciar um projeto via chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Criar uma API REST para gestão de tarefas"}'

# Ver status do projeto
curl http://localhost:8000/api/project/status

# Listar arquivos gerados
curl http://localhost:8000/api/project/files

# Finalizar e gerar pacote
curl -X POST "http://localhost:8000/api/project/finalize?format=zip"

# Baixar o pacote
curl -O http://localhost:8000/api/project/download?path=<caminho_do_zip>
```

### Via Código Python

```python
from core.agency_orchestrator import get_agency_orchestrator

# Inicializa o orquestrador
orchestrator = get_agency_orchestrator()

# Inicia um projeto
orchestrator.start_project(
    project_name="Minha API",
    client_request="Criar uma API REST para gestão de usuários",
    project_type="api_only"
)

# Executa times
po_output = orchestrator.execute_team("product_owner", "Analisar requisitos")
pm_output = orchestrator.execute_team("project_manager", f"Planejar: {po_output.final_output}")

# Finaliza e gera pacote
package_path = orchestrator.finalize_project("zip")
print(f"Projeto disponível em: {package_path}")
```

## 👥 Times Disponíveis

O framework possui **15 times especializados** com **60+ agentes**:

| Time | Descrição | Quando Usar |
|------|-----------|-------------|
| `product_owner` | Análise de requisitos e escopo | Sempre (1º time) |
| `project_manager` | Planejamento e gestão | Sempre (2º time) |
| `architecture` | Decisões técnicas | Projetos complexos |
| `frontend` | Interface web | Apps web |
| `backend` | Lógica de servidor | APIs, microservices |
| `mobile` | Apps mobile | iOS/Android |
| `fullstack` | Full-stack development | Projetos integrados |
| `database` | Modelagem de dados | Sistemas com DB |
| `data_engineering` | Pipelines de dados | Data projects |
| `data_science` | Machine Learning | ML projects |
| `data_analytics` | BI e Analytics | Dashboards |
| `devops` | Infraestrutura | Deploy, CI/CD |
| `qa` | Qualidade | Todos os projetos |
| `security` | Segurança | APIs expostas |
| `ux_ui` | Design | Apps com UI |

## 📁 Tipos de Projeto

```python
from core.project_generator import ProjectType

# Tipos disponíveis
ProjectType.WEB_APP        # Frontend + Backend
ProjectType.API_ONLY       # Apenas API REST
ProjectType.DATA_PIPELINE  # ETL/ELT
ProjectType.ML_PROJECT     # Machine Learning
ProjectType.MOBILE_APP     # Apps mobile
ProjectType.FULLSTACK      # Projeto completo
ProjectType.MICROSERVICES  # Arquitetura distribuída
```

## 📂 Estrutura de Projeto Gerado

Quando você finaliza um projeto, ele é salvo em `projects/`:

```
projects/proj_20260110_123456_meu_projeto/
├── docs/
│   ├── requisitos.md           # Análise do PO
│   ├── plano_projeto.md        # Plano do PM
│   ├── arquitetura.md          # Decisões técnicas
│   └── especificacoes/
├── src/
│   ├── frontend/               # Código frontend
│   ├── backend/                # Código backend
│   └── ...
├── tests/
│   └── test_plan.md            # Plano de testes
├── infra/
│   └── docker/                 # Configurações Docker
├── .agency/
│   └── project_state.json      # Estado do projeto
├── README.md
└── .gitignore
```

## 🔧 Configuração do LLM

Por padrão, usamos **Gemini 2.5 Flash**. Para configurar:

```python
# config/llm_config.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(role: str = "default", temperature_override: float = None):
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=temperature_override or 0.7,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
```

## 🐛 Troubleshooting

### API não inicia

```bash
# Verifique se o ambiente virtual está ativo
source venv/bin/activate

# Verifique a chave do Gemini
echo $GOOGLE_API_KEY

# Reinstale dependências
pip install -r requirements.txt --force-reinstall
```

### Frontend não conecta à API

```bash
# Verifique se a API está rodando
curl http://localhost:8000/health

# Verifique CORS no navegador
# A API deve estar em localhost:8000
```

### Erro de importação de módulos

```bash
# Certifique-se de estar no diretório raiz
cd autonomous-data-agency

# Adicione ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 📚 Próximos Passos

1. **Explore a API**: Acesse http://localhost:8000/docs
2. **Personalize times**: Edite arquivos em `teams/`
3. **Adicione conhecimento**: Adicione YAMLs em `knowledge/`
4. **Integre sistemas**: Use os eventos WebSocket

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m 'Add: minha feature'`
4. Push: `git push origin feature/minha-feature`
5. Abra um Pull Request

---

Happy building with Autonomous Data Agency! 🤖
