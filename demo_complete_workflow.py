#!/usr/bin/env python3
"""
Demo: Complete Workflow - Autonomous Data Agency v4.0

Este script demonstra o fluxo completo de trabalho da agência:

1. Cliente faz uma solicitação
2. PO analisa e cria requisitos
3. PM cria cronograma com dependências
4. ARQUITETURA define a solução (PRIMEIRO - decisões estratégicas)
5. Times executam em paralelo quando possível
6. QA valida cada entrega tecnicamente
7. PO valida se atende ao negócio
8. Ciclo continua até conclusão

Fluxo:
  Cliente → PO → PM → ARQUITETURA → [Data Eng | DevOps | Data Science] → QA → PO → ✓
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.llm_config import get_llm, LLMProvider, LLM_CONFIGS
from core.pm_orchestrator import get_pm_orchestrator, ProjectPhase
from core.validation_workflow import get_validation_workflow
from core.team_communication import get_communication_hub
from core.hallucination_detector import get_hallucination_detector
from core.knowledge import get_knowledge_manager


def print_header(title: str, char: str = "="):
    """Imprime um cabeçalho formatado."""
    print(f"\n{char * 70}")
    print(f"  {title}")
    print(f"{char * 70}")


def print_phase(phase: str, description: str):
    """Imprime uma fase do workflow."""
    print(f"\n{'─' * 70}")
    print(f"📍 FASE: {phase}")
    print(f"   {description}")
    print(f"{'─' * 70}")


def print_team_action(team: str, action: str, details: str = ""):
    """Imprime uma ação de um time."""
    icons = {
        "PO": "📋",
        "PM": "📊",
        "Architecture": "🏗️",
        "Data Engineering": "⚙️",
        "DevOps": "🔧",
        "Data Science": "🧠",
        "QA": "🔍",
        "Client": "👤"
    }
    icon = icons.get(team, "📌")
    print(f"\n{icon} [{team}] {action}")
    if details:
        for line in details.split("\n"):
            print(f"   {line}")


def simulate_llm_response(prompt: str, agent_name: str, llm_provider: str) -> str:
    """Simula resposta de LLM (em produção, chamaria a API real)."""
    # Em produção, isso seria uma chamada real à API do LLM
    responses = {
        "architecture": """
**Arquitetura Proposta: Sistema de Análise de Clientes**

1. **Cloud Provider:** AWS (melhor custo-benefício para o volume)
   - Alternativa: GCP se preferir BigQuery

2. **Componentes:**
   - Ingestão: Apache Airflow + Airbyte
   - Storage: S3 (raw) + Delta Lake (processed)
   - Processamento: Apache Spark on EMR Serverless
   - Serving: PostgreSQL (operacional) + Redis (cache)
   - ML: MLflow + SageMaker endpoints

3. **Estimativa de Custos:**
   - Desenvolvimento: ~$200/mês
   - Produção: ~$500-800/mês (dependendo do volume)

4. **Escalabilidade:**
   - Horizontal: Auto-scaling no EMR e ECS
   - Vertical: Upgrade de instâncias conforme necessidade

5. **Portabilidade:**
   - Containers Docker para todas as aplicações
   - Terraform para IaC (facilita migração)
   - Formatos abertos (Parquet, Delta) evitam lock-in
""",
        "data_engineering": """
**Plano de Implementação: Data Pipelines**

1. **Ingestão:**
   - Conector SQL Server → S3 (Airbyte)
   - Processamento de Excel → Parquet (Python + Pandas)
   - Frequência: Diária (batch) com opção de near-real-time

2. **Transformações:**
   - Bronze: Dados raw em Parquet
   - Silver: Dados limpos e validados
   - Gold: Modelos dimensionais para analytics

3. **Orquestração:**
   - Airflow DAGs para cada pipeline
   - Alertas via Slack/Email em caso de falha

4. **Qualidade de Dados:**
   - Great Expectations para validações
   - Testes de schema, completude, unicidade
""",
        "devops": """
**Plano de Infraestrutura**

1. **Provisionamento:**
   - Terraform modules para AWS
   - VPC com subnets públicas e privadas
   - Security groups restritivos

2. **CI/CD:**
   - GitHub Actions para pipelines
   - Ambientes: dev, staging, prod
   - Deploy automatizado com aprovação manual para prod

3. **Monitoramento:**
   - CloudWatch para métricas e logs
   - Grafana dashboards
   - PagerDuty para alertas críticos
""",
        "qa": """
**Relatório de Validação QA**

✅ Testes Unitários: 47/47 passando
✅ Testes de Integração: 12/12 passando
✅ Testes de Data Quality: 8/8 passando
✅ Cobertura de Código: 85%
✅ Vulnerabilidades de Segurança: 0 críticas, 2 baixas
✅ Performance: Dentro dos limites (p99 < 500ms)

**Recomendações:**
- Resolver as 2 vulnerabilidades baixas antes do release
- Aumentar cobertura para 90% no próximo sprint
""",
        "po": """
**Validação de Negócio**

✅ Requisito 1: Análise de perfil de cliente - ATENDIDO
✅ Requisito 2: Recomendações de produtos - ATENDIDO
✅ Requisito 3: Integração WhatsApp - ATENDIDO
✅ Requisito 4: Lembretes de aniversário - ATENDIDO
✅ Requisito 5: Previsão de próxima compra - ATENDIDO

**Feedback do Cliente:**
"O sistema atende às necessidades. Gostaria de adicionar 
análise de sazonalidade no próximo sprint."

**Decisão:** APROVADO para release
"""
    }
    return responses.get(agent_name.lower().replace(" ", "_"), f"Resposta simulada de {agent_name}")


def run_complete_workflow():
    """Executa o workflow completo da agência."""
    
    print_header("AUTONOMOUS DATA AGENCY - WORKFLOW COMPLETO v4.0")
    print(f"\n🕐 Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Inicializa componentes
    pm = get_pm_orchestrator()
    workflow = get_validation_workflow()
    comm_hub = get_communication_hub()
    hallucination_detector = get_hallucination_detector()
    knowledge_manager = get_knowledge_manager()
    
    # =========================================================================
    # FASE 1: SOLICITAÇÃO DO CLIENTE
    # =========================================================================
    print_phase("1 - SOLICITAÇÃO DO CLIENTE", "Cliente apresenta sua necessidade")
    
    client_request = """
    Eu quero ter um bot de análise de clientes para ter o perfil dele para saber 
    o que ele comprou, o que ele pode comprar mais, quando ele compra, qual será 
    a próxima compra dele em estimativa, que produtos ele compra e quais ele 
    poderia comprar, lembretes de aniversário e datas especiais para chamar o 
    cliente e para ter mais proximidade dele, e com tudo isso aumentar minhas 
    vendas e criar ou melhorar fidelidade do meu cliente.
    
    Fontes de dados: SQL Server e arquivos Excel
    Canal de comunicação: WhatsApp e SMS
    """
    
    print_team_action("Client", "Apresenta solicitação:", client_request.strip())
    
    # =========================================================================
    # FASE 2: ANÁLISE DO PO
    # =========================================================================
    print_phase("2 - ANÁLISE DO PO", "Product Owner analisa e estrutura requisitos")
    
    print_team_action("PO", "Analisa solicitação e extrai requisitos")
    
    requirements = {
        "functional": [
            "Análise de perfil de cliente (histórico de compras)",
            "Sistema de recomendação de produtos relacionados",
            "Previsão de próxima compra (ML)",
            "Lembretes automáticos (aniversário, datas especiais)",
            "Integração com WhatsApp/SMS para comunicação"
        ],
        "non_functional": [
            "LGPD compliance (dados pessoais criptografados)",
            "Disponibilidade 99.5%",
            "Latência < 2s para recomendações",
            "Escalável para 100k clientes"
        ],
        "data_sources": ["SQL Server", "Excel"],
        "has_ml": True,
        "has_streaming": False,
        "has_analytics": True,
        "data_volume": "medium",
        "team_size": 3
    }
    
    print_team_action("PO", "Requisitos estruturados:", f"""
Funcionais: {len(requirements['functional'])} requisitos
Não-funcionais: {len(requirements['non_functional'])} requisitos
Fontes de dados: {', '.join(requirements['data_sources'])}
Inclui ML: {'Sim' if requirements['has_ml'] else 'Não'}
""")
    
    # =========================================================================
    # FASE 3: PLANEJAMENTO DO PM
    # =========================================================================
    print_phase("3 - PLANEJAMENTO DO PM", "Project Manager cria cronograma e dependências")
    
    print_team_action("PM", "Cria projeto e gera cronograma")
    
    # Cria o projeto
    project = pm.create_project(
        project_id="proj_cliente_bot_001",
        project_name="Bot de Análise de Clientes",
        description="Sistema de análise e recomendação para fidelização",
        client_requirements=client_request
    )
    
    # Gera cronograma
    execution_plan = pm.analyze_requirements_and_create_schedule(
        project_id="proj_cliente_bot_001",
        requirements=requirements
    )
    
    print_team_action("PM", "Cronograma gerado:", f"""
Total de tarefas: {execution_plan['total_tasks']}
Horas estimadas: {execution_plan['total_estimated_hours']}h
Duração estimada: {execution_plan['pm_analysis']['estimated_duration_weeks']} semanas
Checkpoints de validação: {execution_plan['pm_analysis']['validation_checkpoints']}
""")
    
    print("\n📋 Ordem de Execução (respeitando dependências):")
    for level in execution_plan["execution_levels"]:
        parallel = "⚡ Paralelo" if level["can_parallelize"] else "→ Sequencial"
        print(f"\n   Nível {level['level']} ({parallel}):")
        for task in level["tasks"]:
            print(f"      [{task['assigned_team']:15}] {task['name']}")
    
    # =========================================================================
    # FASE 4: ARQUITETURA (CRÍTICO - SEMPRE PRIMEIRO)
    # =========================================================================
    print_phase("4 - ARQUITETURA", "Time de Arquitetura define a solução técnica")
    
    print_team_action("Architecture", "Analisa requisitos e propõe arquitetura")
    
    # Busca conhecimento relevante
    arch_knowledge = knowledge_manager.get_knowledge_for_agent(
        domain="architecture",
        task="Definir arquitetura para sistema de análise de clientes com ML",
        project_id="proj_cliente_bot_001"
    )
    
    # Simula resposta do time de arquitetura
    arch_response = simulate_llm_response("", "architecture", "gpt-4.1-mini")
    
    # Valida contra alucinações
    validation = hallucination_detector.validate_response(
        response=arch_response,
        domain="architecture"
    )
    
    print_team_action("Architecture", "Proposta de Arquitetura:", arch_response.strip())
    
    print(f"\n   🛡️ Validação Anti-Alucinação:")
    print(f"      Score de Confiança: {validation.overall_score:.1%}")
    print(f"      Válido: {'✅ Sim' if validation.is_valid else '❌ Não'}")
    
    # Submete para validação
    arch_validation = workflow.submit_for_validation(
        task_id="task_arch_001",
        task_name="Definição de Arquitetura de Solução",
        task_type="architecture",
        assigned_team="architecture",
        deliverables=["Documento de Arquitetura", "Estimativa de Custos", "Diagrama"],
        original_requirements=requirements["functional"] + requirements["non_functional"],
        test_results={
            "all_tests_passed": True,
            "documentation_complete": True,
            "security_vulnerabilities": False
        }
    )
    
    # =========================================================================
    # FASE 5: EXECUÇÃO PARALELA (após arquitetura aprovada)
    # =========================================================================
    print_phase("5 - EXECUÇÃO PARALELA", "Times executam tarefas em paralelo")
    
    # Registra comunicação entre times
    comm_hub.register_team("architecture")
    comm_hub.register_team("data_engineering")
    comm_hub.register_team("devops")
    comm_hub.register_team("data_science")
    comm_hub.register_team("qa")
    
    comm_hub.handoff_task(
        from_team="architecture",
        to_team="data_engineering",
        task_description="Implementar pipelines conforme arquitetura aprovada",
        deliverables=["Pipelines ETL", "Testes", "Documentação"],
        context={"architecture_doc": "arch_v1.0", "priority": "high"}
    )
    
    comm_hub.handoff_task(
        from_team="architecture",
        to_team="devops",
        task_description="Provisionar infraestrutura AWS",
        deliverables=["Terraform", "Kubernetes", "Monitoring"],
        context={"architecture_doc": "arch_v1.0", "priority": "high"}
    )
    
    # Data Engineering
    print_team_action("Data Engineering", "Implementa pipelines de dados")
    de_response = simulate_llm_response("", "data_engineering", "gpt-4.1-nano")
    print(f"   {de_response[:200]}...")
    
    # DevOps (em paralelo)
    print_team_action("DevOps", "Provisiona infraestrutura")
    devops_response = simulate_llm_response("", "devops", "gemini-2.5-flash")
    print(f"   {devops_response[:200]}...")
    
    # Validação do QA para Data Engineering
    de_validation = workflow.submit_for_validation(
        task_id="task_de_001",
        task_name="Implementação de Data Pipelines",
        task_type="data_pipeline",
        assigned_team="data_engineering",
        deliverables=["Pipelines ETL", "Testes", "Documentação"],
        original_requirements=["Ingerir dados SQL Server", "Processar Excel", "Criar modelo dimensional"],
        test_results={
            "all_tests_passed": True,
            "data_quality_score": 0.95,
            "documentation_complete": True,
            "security_vulnerabilities": False
        }
    )
    
    # =========================================================================
    # FASE 6: DATA SCIENCE (após pipelines prontos)
    # =========================================================================
    print_phase("6 - DATA SCIENCE", "Time de ML desenvolve modelos preditivos")
    
    print_team_action("Data Science", "Desenvolve modelo de recomendação e previsão")
    
    # Solicita ajuda do time de Data Engineering
    comm_hub.request_help(
        from_team="data_science",
        topic="Feature Engineering",
        description="Preciso de features agregadas de compras por cliente",
        required_expertise=["sql", "spark"]
    )
    
    print("""
   📊 Modelos desenvolvidos:
      1. Recomendação de produtos (Collaborative Filtering)
      2. Previsão de próxima compra (Time Series + XGBoost)
      3. Segmentação de clientes (K-Means)
   
   📈 Métricas:
      - Recomendação: Precision@10 = 0.78
      - Previsão: MAPE = 12%
      - Segmentação: Silhouette Score = 0.65
""")
    
    # =========================================================================
    # FASE 7: VALIDAÇÃO FINAL
    # =========================================================================
    print_phase("7 - VALIDAÇÃO FINAL", "QA e PO validam a solução completa")
    
    # QA Final
    print_team_action("QA", "Executa validação técnica final")
    qa_response = simulate_llm_response("", "qa", "gpt-4.1-mini")
    print(qa_response)
    
    # PO Final
    print_team_action("PO", "Valida atendimento aos requisitos de negócio")
    po_response = simulate_llm_response("", "po", "gpt-4.1-mini")
    print(po_response)
    
    # =========================================================================
    # RESUMO FINAL
    # =========================================================================
    print_header("RESUMO DO PROJETO", "═")
    
    project_status = pm.get_project_status("proj_cliente_bot_001")
    workflow_summary = workflow.get_workflow_summary()
    comm_summary = comm_hub.get_all_team_statuses()
    
    print(f"""
📋 Projeto: {project['name']}
📅 Status: CONCLUÍDO

📊 Métricas de Execução:
   • Tarefas criadas: {execution_plan['total_tasks']}
   • Horas estimadas: {execution_plan['total_estimated_hours']}h
   • Duração: {execution_plan['pm_analysis']['estimated_duration_weeks']} semanas

✅ Validações:
   • Total de submissões: {workflow_summary['total_submissions']}
   • Aprovadas: {workflow_summary['approved']}
   • QA Score médio: {workflow_summary['qa_summary'].get('average_quality_score', 0):.1%}
   • PO Score médio: {workflow_summary['po_summary'].get('average_business_value', 0):.1%}

📡 Comunicação entre Times:
   • Times registrados: {len(comm_summary)}
   • Handoffs realizados: 2
   • Colaborações ativas: 1

🏗️ Arquitetura Final:
   • Cloud: AWS
   • Orquestração: Apache Airflow
   • Storage: S3 + Delta Lake
   • ML: MLflow + SageMaker
   • Custo estimado: $500-800/mês

📱 Entregas:
   ✓ Pipeline de ingestão (SQL Server + Excel)
   ✓ Modelo de recomendação de produtos
   ✓ Previsão de próxima compra
   ✓ Sistema de lembretes (aniversário)
   ✓ Integração WhatsApp/SMS
   ✓ Dashboard de métricas
""")
    
    print_header("FIM DA DEMONSTRAÇÃO", "═")
    print(f"\n🕐 Término: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    run_complete_workflow()
