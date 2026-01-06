#!/usr/bin/env python3
"""
Demonstração Multi-Time Integrada

Este script demonstra o funcionamento completo da Autonomous Data Agency
com múltiplos times colaborando em um projeto real.

Funcionalidades demonstradas:
1. Múltiplos times de agentes (PO, Data Engineering, DevOps, Data Science, QA)
2. Sistema de comunicação entre times
3. Validação anti-alucinação robusta
4. Fluxo completo de projeto

Execute com: python demo_multi_team.py
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuração
os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

# Imports
from core.teams_factory import (
    TeamsFactory, TeamType, get_teams_factory, TEAM_CONFIGS
)
from core.hallucination_detector import (
    HallucinationDetector, get_hallucination_detector, HallucinationSeverity
)
from core.team_communication import (
    TeamCommunicationHub, get_communication_hub, MessageType, MessagePriority
)
from core.knowledge.knowledge_base import get_knowledge_base
from core.knowledge.project_memory import get_project_memory, MemoryType

# Tenta importar OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ============================================================================
# FUNÇÕES DE UTILIDADE
# ============================================================================

def print_header(title: str, char: str = "=") -> None:
    """Imprime um cabeçalho formatado."""
    print(f"\n{char * 70}")
    print(f"  {title}")
    print(f"{char * 70}")


def print_section(title: str) -> None:
    """Imprime uma seção formatada."""
    print(f"\n--- {title} ---\n")


def print_team_box(team_name: str, content: str) -> None:
    """Imprime uma caixa com conteúdo de um time."""
    lines = content.split('\n')
    max_len = max(len(line) for line in lines)
    width = max(max_len + 4, len(team_name) + 10)
    
    print(f"\n┌{'─' * width}┐")
    print(f"│ 🏢 {team_name:<{width-5}} │")
    print(f"├{'─' * width}┤")
    
    for line in lines[:15]:  # Limita a 15 linhas
        print(f"│ {line:<{width-2}} │")
    
    if len(lines) > 15:
        print(f"│ {'... (mais linhas omitidas)':<{width-2}} │")
    
    print(f"└{'─' * width}┘")


def call_llm(model: str, system_prompt: str, user_prompt: str) -> str:
    """Chama um modelo de LLM ou retorna resposta simulada."""
    if not OPENAI_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
        return simulate_response(model, user_prompt)
    
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[AVISO] Usando resposta simulada: {e}")
        return simulate_response(model, user_prompt)


def simulate_response(model: str, prompt: str) -> str:
    """Simula resposta de LLM."""
    if "requisitos" in prompt.lower() or "product owner" in prompt.lower():
        return """
## Análise de Requisitos

### Requisitos Funcionais
1. Sistema de coleta de dados de clientes
2. Análise de comportamento de compra
3. Motor de recomendações personalizadas
4. Notificações via WhatsApp/SMS

### Requisitos Não-Funcionais
- Tempo de resposta < 2s
- Disponibilidade 99.9%
- Conformidade com LGPD
"""
    elif "arquitetura" in prompt.lower() or "data engineering" in prompt.lower():
        return """
## Proposta de Arquitetura

### Stack Tecnológico
- **Ingestão**: Airbyte + Python connectors
- **Processamento**: Apache Airflow + dbt
- **Armazenamento**: PostgreSQL + S3
- **Analytics**: Metabase

### Pipeline
1. Extração diária dos dados do ERP
2. Transformação com dbt (staging -> marts)
3. Carga no data warehouse
4. Atualização dos dashboards
"""
    elif "devops" in prompt.lower() or "infraestrutura" in prompt.lower():
        return """
## Plano de Infraestrutura

### Ambiente
- **Cloud**: AWS (custo otimizado)
- **Containers**: Docker + ECS
- **CI/CD**: GitHub Actions

### Monitoramento
- CloudWatch para métricas
- Alertas via Slack
- Logs centralizados

### Estimativa de Custo
- ~$200/mês para MVP
"""
    elif "data science" in prompt.lower() or "ml" in prompt.lower():
        return """
## Proposta de Machine Learning

### Modelos Planejados
1. **Recomendação**: Collaborative filtering
2. **Previsão de Churn**: Random Forest
3. **Segmentação**: K-Means clustering

### Ferramentas
- scikit-learn para modelos
- MLflow para tracking
- FastAPI para serving

### Timeline
- Semana 1-2: Feature engineering
- Semana 3-4: Treinamento e validação
- Semana 5: Deploy
"""
    elif "qa" in prompt.lower() or "teste" in prompt.lower():
        return """
## Estratégia de Testes

### Níveis de Teste
1. **Unitários**: pytest (cobertura > 80%)
2. **Integração**: Testes de API
3. **Data Quality**: Great Expectations

### Validações de Dados
- Schema validation
- Null checks
- Range validation
- Referential integrity

### Automação
- Testes em cada PR
- Smoke tests pós-deploy
"""
    else:
        return f"[Resposta simulada para: {prompt[:50]}...]"


# ============================================================================
# CLASSE DO TIME INTEGRADO
# ============================================================================

class IntegratedTeam:
    """Time integrado com comunicação e validação."""
    
    def __init__(self, team_type: TeamType):
        self.config = TEAM_CONFIGS[team_type]
        self.team_type = team_type
        self.name = self.config.name
        self.domain = self.config.domain
        
        # Componentes
        self.kb = get_knowledge_base()
        self.detector = get_hallucination_detector()
        self.hub = get_communication_hub()
        
        # Registra no hub
        self.hub.register_team(self.domain)
    
    def process_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Processa uma tarefa com o time."""
        
        # Atualiza status
        self.hub.update_team_context(
            self.domain,
            current_task=task[:100],
            status="processing"
        )
        
        # Obtém conhecimento
        kb_context = ""
        try:
            practices = self.kb.get_best_practices(self.domain)
            if practices:
                kb_context = self.kb.format_for_prompt(self.domain)[:1500]
        except:
            pass
        
        # Coleta respostas dos agentes operacionais
        responses = []
        for agent in self.config.operational_agents:
            system_prompt = f"""Você é {agent.name}, um {agent.role}.
Especialização: {agent.specialization}

CONHECIMENTO BASE:
{kb_context}

Forneça uma análise técnica detalhada e específica."""
            
            response = call_llm(
                model=agent.llm_model,
                system_prompt=system_prompt,
                user_prompt=task
            )
            
            responses.append({
                "agent": agent.name,
                "model": agent.llm_model,
                "response": response
            })
        
        # Consolida com o agente mestre
        master = self.config.master_config
        consolidation_prompt = f"""Você é {master.name}, líder do time de {self.name}.

TAREFA ORIGINAL:
{task}

RESPOSTAS DOS AGENTES:
{self._format_responses(responses)}

CONHECIMENTO BASE:
{kb_context}

Por favor:
1. Analise criticamente cada resposta
2. Identifique os melhores pontos
3. Consolide uma resposta final
4. Remova informações redundantes ou incorretas"""
        
        consolidated = call_llm(
            model=master.llm_model,
            system_prompt="Você é um líder técnico experiente.",
            user_prompt=consolidation_prompt
        )
        
        # Valida contra alucinações
        validation = self.detector.validate_response(
            response=consolidated,
            domain=self.domain,
            context=kb_context,
            other_responses=[r["response"] for r in responses]
        )
        
        # Atualiza status
        self.hub.update_team_context(
            self.domain,
            status="completed",
            decisions=[{"task": task[:50], "result": "completed"}]
        )
        
        return {
            "team": self.name,
            "domain": self.domain,
            "individual_responses": responses,
            "consolidated_response": consolidated,
            "validation": validation.to_dict(),
            "is_valid": validation.is_valid,
            "score": validation.overall_score
        }
    
    def _format_responses(self, responses: List[Dict]) -> str:
        """Formata respostas para o prompt."""
        return "\n\n".join([
            f"### {r['agent']} ({r['model']}):\n{r['response']}"
            for r in responses
        ])


# ============================================================================
# ORQUESTRADOR MULTI-TIME
# ============================================================================

class MultiTeamOrchestrator:
    """Orquestra múltiplos times em um projeto."""
    
    def __init__(self):
        self.hub = get_communication_hub()
        self.memory = get_project_memory()
        self.teams: Dict[str, IntegratedTeam] = {}
        
        # Inicializa times principais
        for team_type in [
            TeamType.PRODUCT_OWNER,
            TeamType.DATA_ENGINEERING,
            TeamType.DEVOPS,
            TeamType.DATA_SCIENCE,
            TeamType.QA
        ]:
            team = IntegratedTeam(team_type)
            self.teams[team.domain] = team
    
    def run_project(self, client_request: str, project_name: str) -> Dict[str, Any]:
        """Executa um projeto completo com todos os times."""
        
        results = {
            "project_name": project_name,
            "started_at": datetime.now().isoformat(),
            "phases": [],
            "communications": [],
            "final_deliverables": []
        }
        
        # Cria projeto na memória
        project_id = f"proj_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.memory.create_project(
            project_id=project_id,
            name=project_name,
            client_name="Cliente",
            description=client_request[:200]
        )
        
        print_header("AUTONOMOUS DATA AGENCY - PROJETO MULTI-TIME")
        print(f"Projeto: {project_name}")
        print(f"ID: {project_id}")
        print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # ========== FASE 1: PRODUCT OWNER ==========
        print_header("FASE 1: ANÁLISE DO PRODUCT OWNER", "─")
        
        po_result = self.teams["product_owner"].process_task(
            f"Analise os requisitos do cliente e crie user stories:\n\n{client_request}"
        )
        
        print_team_box("Product Owner Team", po_result["consolidated_response"][:800])
        print(f"\n✓ Validação: {'PASSOU' if po_result['is_valid'] else 'REQUER REVISÃO'} (Score: {po_result['score']:.0%})")
        
        results["phases"].append({
            "phase": "requirements",
            "team": "product_owner",
            "result": po_result
        })
        
        # Handoff para Data Engineering
        self.hub.handoff_task(
            from_team="product_owner",
            to_team="data_engineering",
            task_description="Requisitos aprovados. Iniciar design de arquitetura de dados.",
            deliverables=["Arquitetura de dados", "Design de pipeline"],
            context={"requirements": po_result["consolidated_response"][:500]}
        )
        results["communications"].append("PO -> Data Engineering: Handoff de requisitos")
        
        # ========== FASE 2: DATA ENGINEERING ==========
        print_header("FASE 2: ARQUITETURA DE DADOS", "─")
        
        de_result = self.teams["data_engineering"].process_task(
            f"""Com base nos requisitos, projete a arquitetura de dados:

REQUISITOS:
{po_result["consolidated_response"][:800]}

SOLICITAÇÃO ORIGINAL:
{client_request}"""
        )
        
        print_team_box("Data Engineering Team", de_result["consolidated_response"][:800])
        print(f"\n✓ Validação: {'PASSOU' if de_result['is_valid'] else 'REQUER REVISÃO'} (Score: {de_result['score']:.0%})")
        
        results["phases"].append({
            "phase": "architecture",
            "team": "data_engineering",
            "result": de_result
        })
        
        # Solicita ajuda do DevOps
        collab_id = self.hub.request_help(
            from_team="data_engineering",
            topic="Infraestrutura para pipeline de dados",
            description="Precisamos de infraestrutura para hospedar o pipeline",
            required_expertise=["cloud", "kubernetes", "ci/cd"]
        )
        results["communications"].append(f"Data Engineering solicita ajuda: {collab_id}")
        
        # ========== FASE 3: DEVOPS ==========
        print_header("FASE 3: INFRAESTRUTURA E DEVOPS", "─")
        
        devops_result = self.teams["devops"].process_task(
            f"""Projete a infraestrutura para suportar o pipeline de dados:

ARQUITETURA PROPOSTA:
{de_result["consolidated_response"][:800]}

REQUISITOS:
- Ambiente de desenvolvimento e produção
- CI/CD automatizado
- Monitoramento e alertas"""
        )
        
        print_team_box("DevOps Team", devops_result["consolidated_response"][:800])
        print(f"\n✓ Validação: {'PASSOU' if devops_result['is_valid'] else 'REQUER REVISÃO'} (Score: {devops_result['score']:.0%})")
        
        results["phases"].append({
            "phase": "infrastructure",
            "team": "devops",
            "result": devops_result
        })
        
        # Responde à colaboração
        self.hub.respond_to_collaboration(
            collaboration_id=collab_id,
            team_name="devops",
            response=devops_result["consolidated_response"][:500]
        )
        
        # ========== FASE 4: DATA SCIENCE ==========
        print_header("FASE 4: MACHINE LEARNING", "─")
        
        ds_result = self.teams["data_science"].process_task(
            f"""Projete os modelos de ML para o sistema:

CONTEXTO:
{client_request}

DADOS DISPONÍVEIS (baseado na arquitetura):
{de_result["consolidated_response"][:500]}

REQUISITOS:
- Modelos de recomendação
- Previsões de comportamento
- Segmentação de clientes"""
        )
        
        print_team_box("Data Science Team", ds_result["consolidated_response"][:800])
        print(f"\n✓ Validação: {'PASSOU' if ds_result['is_valid'] else 'REQUER REVISÃO'} (Score: {ds_result['score']:.0%})")
        
        results["phases"].append({
            "phase": "machine_learning",
            "team": "data_science",
            "result": ds_result
        })
        
        # ========== FASE 5: QA ==========
        print_header("FASE 5: QUALIDADE E TESTES", "─")
        
        qa_result = self.teams["qa"].process_task(
            f"""Defina a estratégia de testes para o projeto:

COMPONENTES A TESTAR:
1. Pipeline de dados: {de_result["consolidated_response"][:300]}
2. Infraestrutura: {devops_result["consolidated_response"][:300]}
3. Modelos de ML: {ds_result["consolidated_response"][:300]}

REQUISITOS:
- Testes automatizados
- Validação de qualidade de dados
- Testes de performance"""
        )
        
        print_team_box("QA Team", qa_result["consolidated_response"][:800])
        print(f"\n✓ Validação: {'PASSOU' if qa_result['is_valid'] else 'REQUER REVISÃO'} (Score: {qa_result['score']:.0%})")
        
        results["phases"].append({
            "phase": "quality_assurance",
            "team": "qa",
            "result": qa_result
        })
        
        # ========== RESUMO FINAL ==========
        print_header("RESUMO DO PROJETO")
        
        # Calcula métricas
        total_phases = len(results["phases"])
        valid_phases = sum(1 for p in results["phases"] if p["result"]["is_valid"])
        avg_score = sum(p["result"]["score"] for p in results["phases"]) / total_phases
        
        print(f"""
📊 MÉTRICAS DO PROJETO
{'─' * 40}
  Fases completadas: {total_phases}
  Fases válidas: {valid_phases}/{total_phases}
  Score médio de validação: {avg_score:.0%}
  Comunicações entre times: {len(results['communications'])}

📋 TIMES ENVOLVIDOS
{'─' * 40}""")
        
        for phase in results["phases"]:
            team = phase["team"]
            score = phase["result"]["score"]
            status = "✓" if phase["result"]["is_valid"] else "⚠"
            print(f"  {status} {team}: {score:.0%}")
        
        print(f"""
📨 COMUNICAÇÕES
{'─' * 40}""")
        for comm in results["communications"]:
            print(f"  → {comm}")
        
        # Armazena decisões na memória
        for phase in results["phases"]:
            self.memory.store_decision(
                project_id=project_id,
                decision_key=f"{phase['phase']}_decision",
                decision=phase["result"]["consolidated_response"][:200],
                rationale=f"Validação: {phase['result']['score']:.0%}",
                alternatives=[]
            )
        
        results["completed_at"] = datetime.now().isoformat()
        results["metrics"] = {
            "total_phases": total_phases,
            "valid_phases": valid_phases,
            "average_score": avg_score,
            "communications_count": len(results["communications"])
        }
        
        print_header("PROJETO CONCLUÍDO COM SUCESSO")
        
        return results


# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

def main():
    """Executa a demonstração multi-time."""
    
    # Solicitação do cliente
    client_request = """
    Preciso de um sistema completo de análise e fidelização de clientes para minha loja.
    
    O sistema deve:
    1. Coletar dados de compras dos clientes (do meu sistema de vendas)
    2. Analisar o perfil de cada cliente (o que compra, quando, quanto gasta)
    3. Fazer recomendações de produtos relacionados
    4. Enviar lembretes de aniversário e datas especiais via WhatsApp
    5. Prever qual será a próxima compra do cliente
    6. Sugerir promoções personalizadas para aumentar vendas
    
    Restrições:
    - Orçamento limitado (preferência por ferramentas open source)
    - Time pequeno (2 desenvolvedores)
    - Preciso estar em conformidade com a LGPD
    - Prazo de 3 meses para o MVP
    """
    
    # Cria e executa o orquestrador
    orchestrator = MultiTeamOrchestrator()
    results = orchestrator.run_project(
        client_request=client_request,
        project_name="Sistema de Fidelização de Clientes"
    )
    
    # Gera relatório de comunicação
    print("\n" + orchestrator.hub.generate_communication_report())
    
    return results


if __name__ == "__main__":
    main()
