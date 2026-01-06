#!/usr/bin/env python3
"""
Demonstração do Workflow Integrado v5.0
=======================================

Este script demonstra o funcionamento completo do Autonomous Data Agency Framework v5.0,
incluindo:
- Time de Governança e LGPD
- Validação de Data Quality
- Observabilidade e FinOps
- Workflow integrado com checkpoints de governança

Cenário: Bot de Análise de Clientes com dados sensíveis (LGPD)
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Adiciona o diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cores para output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_section(text: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*60}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}▶ {text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'─'*60}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def print_table(headers: List[str], rows: List[List[str]]):
    """Imprime uma tabela formatada"""
    col_widths = [max(len(str(row[i])) for row in [headers] + rows) for i in range(len(headers))]
    
    # Header
    header_line = " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers))
    print(f"  {header_line}")
    print(f"  {'-+-'.join('-' * w for w in col_widths)}")
    
    # Rows
    for row in rows:
        row_line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        print(f"  {row_line}")

def main():
    print_header("AUTONOMOUS DATA AGENCY v5.0")
    print_header("Demonstração do Workflow Integrado com Governança")
    
    # =========================================================================
    # FASE 1: INICIALIZAÇÃO DOS COMPONENTES
    # =========================================================================
    print_section("FASE 1: Inicialização dos Componentes")
    
    # Importa os módulos
    print_info("Importando módulos do framework...")
    
    from core.governance_team import get_governance_team, LegalBasis, PIIType
    from core.data_quality import get_data_quality_validator, QualityDimension
    from core.observability_team import get_observability_team
    from core.knowledge import get_knowledge_base
    
    # Inicializa componentes
    governance = get_governance_team()
    quality_validator = get_data_quality_validator()
    observability = get_observability_team()
    knowledge_base = get_knowledge_base()
    
    print_success("Time de Governança e LGPD inicializado")
    print_success("Validador de Data Quality inicializado")
    print_success("Sistema de Observabilidade inicializado")
    print_success("Knowledge Base carregada")
    
    # Registra início no observability
    observability.logger.log(
        level="INFO",
        component="demo",
        action="start",
        message="Iniciando demonstração do workflow integrado v5.0",
        context={"demo": "integrated_v5", "timestamp": datetime.now().isoformat()}
    )
    
    # =========================================================================
    # FASE 2: SOLICITAÇÃO DO CLIENTE
    # =========================================================================
    print_section("FASE 2: Solicitação do Cliente")
    
    client_request = {
        "project_name": "Bot de Análise de Clientes",
        "client": "Empresa XYZ Ltda",
        "description": """
        Sistema de análise de clientes para:
        - Perfil do cliente e histórico de compras
        - Recomendações de produtos relacionados
        - Previsão de próxima compra
        - Lembretes de aniversário e datas especiais
        - Comunicação via WhatsApp/SMS
        """,
        "data_fields": [
            "nome", "email", "cpf", "telefone", "data_nascimento",
            "endereco", "historico_compras", "preferencias"
        ],
        "declared_legal_basis": "contract",
        "retention_period": "5 years",
        "communication_channels": ["whatsapp", "sms", "email"]
    }
    
    print(f"  Projeto: {client_request['project_name']}")
    print(f"  Cliente: {client_request['client']}")
    print(f"  Campos de dados: {', '.join(client_request['data_fields'])}")
    print(f"  Base legal declarada: {client_request['declared_legal_basis']}")
    print(f"  Período de retenção: {client_request['retention_period']}")
    
    # =========================================================================
    # FASE 3: ANÁLISE DE GOVERNANÇA E LGPD
    # =========================================================================
    print_section("FASE 3: Análise de Governança e LGPD")
    
    # 3.1 Classificação de Dados usando o LGPDValidator
    print_info("3.1 Classificando dados (detecção de PII)...")
    
    data_schema = {
        "nome": "string",
        "email": "string",
        "cpf": "string",
        "telefone": "string",
        "data_nascimento": "date",
        "endereco": "string",
        "historico_compras": "array",
        "preferencias": "object"
    }
    
    # Usa o método detect_pii_in_schema do LGPDValidator
    pii_detections = governance.lgpd_validator.detect_pii_in_schema(data_schema)
    
    classification_rows = []
    for detection in pii_detections:
        icon = "🔴" if detection.pii_type in [PIIType.HEALTH, PIIType.BIOMETRIC, PIIType.FINANCIAL] else "🟡"
        classification_rows.append([detection.field_name, detection.pii_type.value, icon, detection.confidence])
    
    # Adiciona campos não-PII
    pii_fields = {d.field_name for d in pii_detections}
    for field in data_schema:
        if field not in pii_fields:
            classification_rows.append([field, "PUBLIC", "🟢", "N/A"])
    
    print_table(["Campo", "Classificação", "Risco", "Confiança"], classification_rows)
    
    pii_count = len(pii_detections)
    sensitive_count = sum(1 for d in pii_detections if d.pii_type in [PIIType.HEALTH, PIIType.BIOMETRIC])
    
    print(f"\n  Resumo: {pii_count} campos PII detectados, {sensitive_count} sensíveis")
    
    # 3.2 Verificação de Base Legal
    print_info("\n3.2 Verificando base legal...")
    
    data_types = list(set(d.pii_type for d in pii_detections))
    is_valid, issues = governance.lgpd_validator.validate_legal_basis(
        data_types=data_types,
        legal_basis=LegalBasis.CONTRACT,
        purpose="Análise de clientes para recomendações e fidelização"
    )
    
    if is_valid:
        print_success(f"Base legal 'CONTRACT' é válida para os tipos de dados")
    else:
        print_error(f"Base legal inválida")
        for issue in issues:
            print_warning(f"  - {issue}")
    
    # 3.3 Recomendações de proteção
    print_info("\n3.3 Recomendações de proteção de dados...")
    
    for detection in pii_detections[:5]:
        print(f"    • {detection.field_name}: {detection.recommendation}")
    
    # 3.4 Direitos do Titular
    print_info("\n3.4 Direitos do titular que devem ser garantidos...")
    
    from core.governance_team import DataSubjectRight
    rights = [
        ("Acesso", "O titular pode solicitar acesso aos seus dados"),
        ("Correção", "O titular pode solicitar correção de dados incorretos"),
        ("Eliminação", "O titular pode solicitar exclusão dos dados"),
        ("Portabilidade", "O titular pode solicitar transferência dos dados"),
        ("Revogação", "O titular pode revogar o consentimento a qualquer momento")
    ]
    
    for i, (name, desc) in enumerate(rights, 1):
        print(f"    {i}. {name}: {desc}")
    
    # Registra no observability
    observability.logger.log(
        level="INFO",
        component="governance",
        action="analysis_complete",
        message="Análise de governança concluída",
        context={
            "pii_fields": pii_count,
            "sensitive_fields": sensitive_count,
            "legal_basis_valid": is_valid
        }
    )
    
    # =========================================================================
    # FASE 4: VALIDAÇÃO DE DATA QUALITY
    # =========================================================================
    print_section("FASE 4: Validação de Data Quality")
    
    # 4.1 Definir schema e regras
    print_info("4.1 Configurando regras de qualidade...")
    
    quality_schema = {
        "nome": {"type": "string", "nullable": False},
        "email": {"type": "string", "nullable": False},
        "cpf": {"type": "string", "nullable": False},
        "telefone": {"type": "string", "nullable": True},
        "data_nascimento": {"type": "date", "nullable": True}
    }
    
    quality_validator.add_standard_rules("clientes", quality_schema)
    
    print_success("Regras de qualidade configuradas")
    print(f"  - Completude: campos obrigatórios")
    print(f"  - Consistência: formato de email e CPF")
    print(f"  - Unicidade: CPF único")
    
    # 4.2 Dados de teste (simulando dados reais)
    print_info("\n4.2 Validando dados de amostra...")
    
    sample_data = [
        {"nome": "João Silva", "email": "joao@email.com", "cpf": "123.456.789-00", "telefone": "(11) 99999-0001", "data_nascimento": "1985-03-15"},
        {"nome": "Maria Santos", "email": "maria@email.com", "cpf": "234.567.890-11", "telefone": "(11) 99999-0002", "data_nascimento": "1990-07-22"},
        {"nome": "Pedro Oliveira", "email": "invalid-email", "cpf": "345.678.901-22", "telefone": None, "data_nascimento": "1988-11-30"},
        {"nome": "", "email": "ana@email.com", "cpf": "456.789.012-33", "telefone": "(11) 99999-0004", "data_nascimento": "1995-01-10"},
        {"nome": "Carlos Ferreira", "email": "carlos@email.com", "cpf": "12345", "telefone": "(11) 99999-0005", "data_nascimento": "1982-09-05"},
    ]
    
    # Valida dados
    quality_report = quality_validator.validate("clientes", sample_data)
    
    print(f"\n  Registros validados: {len(sample_data)}")
    print(f"  Score geral: {quality_report.overall_score:.1%}")
    print(f"  Status: {'✓ APROVADO' if quality_report.passed else '✗ REPROVADO'}")
    
    # Mostra violações
    if quality_report.violations:
        print(f"\n  Violações encontradas ({len(quality_report.violations)}):")
        violation_rows = []
        for v in quality_report.violations[:5]:
            if hasattr(v, 'dimension'):
                violation_rows.append([
                    v.dimension.value if hasattr(v.dimension, 'value') else str(v.dimension),
                    v.rule_id if hasattr(v, 'rule_id') else "N/A",
                    v.severity.value if hasattr(v, 'severity') and hasattr(v.severity, 'value') else "N/A",
                    str(v.affected_records) if hasattr(v, 'affected_records') else "N/A"
                ])
            else:
                violation_rows.append(["N/A", "N/A", "N/A", "N/A"])
        if violation_rows:
            print_table(["Dimensão", "Regra", "Severidade", "Registros"], violation_rows)
    
    # Mostra scores por dimensão
    print("\n  Scores por dimensão:")
    for dim, score_obj in quality_report.dimension_scores.items():
        score = score_obj.score if hasattr(score_obj, 'score') else score_obj
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        color = Colors.GREEN if score >= 0.8 else Colors.WARNING if score >= 0.6 else Colors.FAIL
        print(f"    {dim.ljust(15)} [{bar}] {color}{score:.1%}{Colors.ENDC}")
    
    # =========================================================================
    # FASE 5: ESTIMATIVA DE CUSTOS (FinOps)
    # =========================================================================
    print_section("FASE 5: Estimativa de Custos (FinOps)")
    
    print_info("Calculando estimativa de custos do projeto...")
    
    project_params = {
        "duration_days": 90,
        "llm_calls_per_day": 500,
        "avg_tokens_per_call": 2000,
        "storage_gb": 100,
        "compute_hours_per_day": 12
    }
    
    cost_estimate = observability.costs.estimate_project_cost(project_params)
    
    print(f"\n  Parâmetros do projeto:")
    print(f"    - Duração: {project_params['duration_days']} dias")
    print(f"    - Chamadas LLM/dia: {project_params['llm_calls_per_day']}")
    print(f"    - Storage: {project_params['storage_gb']} GB")
    print(f"    - Compute: {project_params['compute_hours_per_day']}h/dia")
    
    print(f"\n  Estimativa de custos:")
    print(f"    ┌─────────────────────────────────────┐")
    print(f"    │ LLM (API calls)     ${cost_estimate['breakdown']['llm_costs']:>12,.2f} │")
    print(f"    │ Storage             ${cost_estimate['breakdown']['storage_costs']:>12,.2f} │")
    print(f"    │ Compute             ${cost_estimate['breakdown']['compute_costs']:>12,.2f} │")
    print(f"    ├─────────────────────────────────────┤")
    print(f"    │ {Colors.BOLD}TOTAL ESTIMADO      ${cost_estimate['total_estimated']:>12,.2f}{Colors.ENDC} │")
    print(f"    └─────────────────────────────────────┘")
    
    # Recomendações de otimização
    print("\n  Recomendações de otimização:")
    recommendations = [
        "Usar gpt-4.1-nano para tarefas simples (economia de 70%)",
        "Implementar cache de respostas frequentes",
        "Usar spot instances para compute não-crítico",
        "Configurar auto-scaling baseado em demanda"
    ]
    for rec in recommendations:
        print(f"    💡 {rec}")
    
    # =========================================================================
    # FASE 6: VALIDAÇÃO COMPLETA DO PROJETO
    # =========================================================================
    print_section("FASE 6: Validação Completa do Projeto")
    
    print_info("Executando validação completa de governança...")
    
    # Usa o método validate_project do GovernanceTeam
    validation_result = governance.validate_project(
        project_name=client_request["project_name"],
        schema=data_schema,
        legal_basis=LegalBasis.CONTRACT,
        purpose="Análise de clientes para recomendações e fidelização",
        processing_activities=["coleta", "armazenamento", "análise", "comunicação"]
    )
    
    print(f"\n  Score de Compliance: {validation_result.compliance_score:.1%}")
    print(f"  Status LGPD: {validation_result.lgpd_status}")
    print(f"  Aprovado: {'✓ SIM' if validation_result.is_compliant else '✗ NÃO'}")
    
    if validation_result.issues:
        print("\n  Issues encontradas:")
        for issue in validation_result.issues[:5]:
            print_warning(f"    - {issue.get('message', issue)}")
    
    if validation_result.recommendations:
        print("\n  Recomendações:")
        for rec in validation_result.recommendations[:5]:
            print_info(f"    - {rec}")
    
    if validation_result.required_actions:
        print("\n  Ações requeridas:")
        for action in validation_result.required_actions:
            print_error(f"    - {action}")
    
    # =========================================================================
    # FASE 7: SIMULAÇÃO DE EXECUÇÃO COM OBSERVABILIDADE
    # =========================================================================
    print_section("FASE 7: Simulação de Execução com Observabilidade")
    
    print_info("Simulando execução de agentes com monitoramento...")
    
    # Simula ações de agentes
    agents_actions = [
        ("po_master", "analyze_requirements", 1200, True, 1500, "gpt-4.1-mini"),
        ("pm_master", "create_schedule", 800, True, 1200, "gpt-4.1-mini"),
        ("architect_master", "design_architecture", 2500, True, 3000, "gpt-4.1-mini"),
        ("data_engineer_1", "design_pipeline", 1800, True, 2000, "gpt-4.1-nano"),
        ("data_engineer_2", "implement_etl", 2200, True, 2500, "gemini-2.5-flash"),
        ("data_scientist_1", "train_model", 3500, True, 4000, "gpt-4.1-mini"),
        ("qa_validator", "run_tests", 1500, True, 1800, "gpt-4.1-nano"),
    ]
    
    print("\n  Ações executadas:")
    action_rows = []
    total_tokens = 0
    total_duration = 0
    
    for agent, action, duration, success, tokens, model in agents_actions:
        observability.record_agent_action(
            agent_name=agent,
            action=action,
            duration_ms=duration,
            success=success,
            tokens_used=tokens,
            model=model
        )
        total_tokens += tokens
        total_duration += duration
        status = "✓" if success else "✗"
        action_rows.append([agent, action, f"{duration}ms", f"{tokens}", model, status])
    
    print_table(["Agente", "Ação", "Duração", "Tokens", "Modelo", "Status"], action_rows)
    
    print(f"\n  Totais:")
    print(f"    - Duração total: {total_duration/1000:.1f}s")
    print(f"    - Tokens consumidos: {total_tokens:,}")
    print(f"    - Custo estimado: ${total_tokens * 0.00001:.4f}")
    
    # Métricas coletadas
    print("\n  Métricas (4 Golden Signals):")
    metrics = observability.metrics.get_summary()
    
    print(f"    📊 Latência média: {metrics.get('avg_latency_ms', 0):.0f}ms")
    print(f"    📈 Throughput: {metrics.get('requests_per_minute', 0):.1f} req/min")
    print(f"    ❌ Taxa de erros: {metrics.get('error_rate', 0):.1%}")
    print(f"    💾 Saturação: {metrics.get('saturation', 0):.1%}")
    
    # =========================================================================
    # FASE 8: RELATÓRIO FINAL
    # =========================================================================
    print_section("FASE 8: Relatório Final do Projeto")
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                         RELATÓRIO DO PROJETO                              ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║  Projeto: {client_request['project_name']:<59} ║
    ║  Cliente: {client_request['client']:<59} ║
    ║  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<62} ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                           GOVERNANÇA E LGPD                               ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║  Campos PII identificados: {pii_count:<41} ║
    ║  Campos sensíveis: {sensitive_count:<50} ║
    ║  Base legal: {client_request['declared_legal_basis']:<57} ║
    ║  Status LGPD: {validation_result.lgpd_status:<56} ║
    ║  Compliance Score: {validation_result.compliance_score:.1%:<50} ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                           DATA QUALITY                                    ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║  Score geral: {quality_report.overall_score:.1%:<56} ║
    ║  Violações: {len(quality_report.violations):<58} ║
    ║  Status: {'✓ APROVADO' if quality_report.passed else '✗ REPROVADO':<61} ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                           CUSTOS (FinOps)                                 ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║  Custo estimado (90 dias): ${cost_estimate['total_estimated']:>10,.2f}                         ║
    ║  Tokens consumidos (demo): {total_tokens:>10,}                              ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                           STATUS FINAL                                    ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                                                                          ║
    ║         {'✅  PROJETO APROVADO PARA EXECUÇÃO' if validation_result.is_compliant else '⚠️  PROJETO REQUER AJUSTES':^52}          ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Log final
    observability.logger.log(
        level="INFO",
        component="demo",
        action="complete",
        message="Demonstração do workflow integrado v5.0 concluída com sucesso",
        context={
            "project": client_request["project_name"],
            "governance_approved": validation_result.is_compliant,
            "quality_score": quality_report.overall_score,
            "compliance_score": validation_result.compliance_score,
            "estimated_cost": cost_estimate["total_estimated"]
        }
    )
    
    print_success("Demonstração concluída com sucesso!")
    print_info("Todos os componentes do framework v5.0 foram testados.")

if __name__ == "__main__":
    main()
