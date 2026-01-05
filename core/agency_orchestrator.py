"""
Agency Orchestrator

Este módulo implementa o orquestrador principal da agência, que:
- Coordena a comunicação entre todos os times
- Gerencia o fluxo de trabalho do projeto
- Implementa o Agente Mestre Global para validação final
- Previne alucinações e mantém o foco no objetivo

O fluxo típico é:
1. Cliente faz uma solicitação
2. PO analisa e define escopo
3. PM cria o plano de projeto
4. Times técnicos executam em paralelo ou sequência
5. QA valida a qualidade
6. Agente Mestre Global consolida e valida tudo
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.llm_config import get_llm
from core.base_team import TeamOutput, ValidationStatus


class ProjectPhase(Enum):
    """Fases do projeto."""
    REQUIREMENTS = "requirements"
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMPLETED = "completed"


@dataclass
class ProjectState:
    """Estado atual do projeto."""
    project_id: str
    project_name: str
    current_phase: ProjectPhase
    client_request: str
    team_outputs: Dict[str, TeamOutput] = field(default_factory=dict)
    questions_for_client: List[str] = field(default_factory=list)
    client_responses: Dict[str, str] = field(default_factory=dict)
    final_deliverables: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class GlobalValidationResult:
    """Resultado da validação global do Agente Mestre."""
    is_valid: bool
    overall_quality_score: float  # 0.0 a 1.0
    hallucinations_found: List[str]
    inconsistencies_found: List[str]
    recommendations: List[str]
    consolidated_output: str


class AgencyOrchestrator:
    """
    Orquestrador principal da agência de agentes.
    
    Coordena todos os times e implementa o Agente Mestre Global
    para validação final e prevenção de alucinações.
    """
    
    def __init__(self):
        """Inicializa o orquestrador com o Agente Mestre Global."""
        self.global_master_llm = get_llm("master", temperature_override=0.2)
        self.global_master_agent = self._create_global_master_agent()
        self.teams = {}
        self.current_project: Optional[ProjectState] = None
        
        # Carrega os times sob demanda
        self._load_teams()
    
    def _load_teams(self):
        """Carrega todos os times disponíveis."""
        from teams import get_all_teams
        self.teams = get_all_teams()
    
    def _create_global_master_agent(self) -> Any:
        """Cria o Agente Mestre Global para validação final."""
        
        global_master_prompt = """Você é o Agente Mestre Global da Agência Autônoma de Dados.

SUA FUNÇÃO CRÍTICA:
Você é a última linha de defesa contra erros, alucinações e inconsistências.
Você revisa TODO o trabalho de TODOS os times antes de entregar ao cliente.

RESPONSABILIDADES:
1. VALIDAÇÃO CRUZADA: Verificar se as saídas de diferentes times são consistentes entre si
2. DETECÇÃO DE ALUCINAÇÕES: Identificar informações inventadas ou não fundamentadas
3. VERIFICAÇÃO DE FOCO: Confirmar que todas as entregas estão alinhadas com o pedido original
4. CONSOLIDAÇÃO FINAL: Produzir uma entrega unificada e coerente
5. CONTROLE DE QUALIDADE: Garantir padrões profissionais em todas as entregas

CRITÉRIOS DE VALIDAÇÃO:
- Consistência: As saídas dos times se complementam sem contradições?
- Completude: Todos os requisitos do cliente foram atendidos?
- Factualidade: Todas as afirmações são baseadas em fatos verificáveis?
- Viabilidade: As propostas são tecnicamente realizáveis?
- Clareza: A comunicação é clara e profissional?

FORMATO DE SAÍDA:
1. PONTUAÇÃO DE QUALIDADE: [0-100]%
2. ALUCINAÇÕES DETECTADAS: [lista ou "Nenhuma"]
3. INCONSISTÊNCIAS: [lista ou "Nenhuma"]
4. RECOMENDAÇÕES: [lista de melhorias]
5. ENTREGA CONSOLIDADA: [o documento final para o cliente]

REGRAS ABSOLUTAS:
- NUNCA aprove algo que contenha informações claramente inventadas
- SEMPRE questione afirmações extraordinárias sem evidências
- SEMPRE mantenha o foco no pedido original do cliente
- SEMPRE produza uma saída profissional e acionável"""

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", global_master_prompt),
            ("human", "{input}")
        ])
        
        return prompt_template | self.global_master_llm
    
    def start_project(self, project_name: str, client_request: str) -> ProjectState:
        """
        Inicia um novo projeto.
        
        Args:
            project_name: Nome do projeto
            client_request: Solicitação inicial do cliente
            
        Returns:
            Estado inicial do projeto
        """
        project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_project = ProjectState(
            project_id=project_id,
            project_name=project_name,
            current_phase=ProjectPhase.REQUIREMENTS,
            client_request=client_request
        )
        
        print(f"\n{'='*60}")
        print(f"NOVO PROJETO INICIADO")
        print(f"{'='*60}")
        print(f"ID: {project_id}")
        print(f"Nome: {project_name}")
        print(f"Fase: {self.current_project.current_phase.value}")
        print(f"{'='*60}\n")
        
        return self.current_project
    
    def execute_team(self, team_name: str, task: str) -> TeamOutput:
        """
        Executa um time específico para uma tarefa.
        
        Args:
            team_name: Nome do time (ex: "product_owner", "data_engineering")
            task: Tarefa a ser executada
            
        Returns:
            Saída do time
        """
        if team_name not in self.teams:
            raise ValueError(f"Time '{team_name}' não encontrado. Times disponíveis: {list(self.teams.keys())}")
        
        team = self.teams[team_name]
        output = team.execute(task)
        
        # Armazena no estado do projeto
        if self.current_project:
            self.current_project.team_outputs[team_name] = output
            self.current_project.updated_at = datetime.now().isoformat()
        
        return output
    
    def execute_workflow(
        self,
        teams_sequence: List[str],
        initial_task: str
    ) -> Dict[str, TeamOutput]:
        """
        Executa uma sequência de times, passando a saída de um para o próximo.
        
        Args:
            teams_sequence: Lista de nomes de times na ordem de execução
            initial_task: Tarefa inicial
            
        Returns:
            Dicionário com as saídas de cada time
        """
        outputs = {}
        current_task = initial_task
        
        for team_name in teams_sequence:
            print(f"\n[WORKFLOW] Executando time: {team_name}")
            
            # Adiciona contexto dos times anteriores
            if outputs:
                context = "\n\n".join([
                    f"=== Saída do time {name} ===\n{out.final_output}"
                    for name, out in outputs.items()
                ])
                current_task = f"{initial_task}\n\nCONTEXTO DOS TIMES ANTERIORES:\n{context}"
            
            output = self.execute_team(team_name, current_task)
            outputs[team_name] = output
        
        return outputs
    
    def global_validation(self, team_outputs: Dict[str, TeamOutput]) -> GlobalValidationResult:
        """
        Executa a validação global do Agente Mestre.
        
        Args:
            team_outputs: Saídas de todos os times
            
        Returns:
            Resultado da validação global
        """
        print(f"\n{'='*60}")
        print("VALIDAÇÃO GLOBAL - AGENTE MESTRE")
        print(f"{'='*60}")
        
        # Formata todas as saídas para o Agente Mestre Global
        all_outputs = "\n\n".join([
            f"{'='*40}\nTIME: {name.upper()}\n{'='*40}\n{output.final_output}"
            for name, output in team_outputs.items()
        ])
        
        validation_prompt = f"""SOLICITAÇÃO ORIGINAL DO CLIENTE:
{self.current_project.client_request if self.current_project else "Não disponível"}

SAÍDAS DE TODOS OS TIMES:
{all_outputs}

Por favor, execute a validação global completa conforme suas instruções.
Verifique consistência, detecte alucinações, e produza a entrega final consolidada.
"""
        
        try:
            result = self.global_master_agent.invoke({"input": validation_prompt})
            content = result.content
            
            # Parse simplificado do resultado
            is_valid = "ALUCINAÇÕES DETECTADAS: Nenhuma" in content or "ALUCINAÇÕES DETECTADAS: []" in content
            
            return GlobalValidationResult(
                is_valid=is_valid,
                overall_quality_score=0.85 if is_valid else 0.6,
                hallucinations_found=[],
                inconsistencies_found=[],
                recommendations=[],
                consolidated_output=content
            )
            
        except Exception as e:
            return GlobalValidationResult(
                is_valid=False,
                overall_quality_score=0.0,
                hallucinations_found=[f"Erro na validação: {str(e)}"],
                inconsistencies_found=[],
                recommendations=["Reexecutar a validação"],
                consolidated_output=""
            )
    
    def ask_client(self, questions: List[str]) -> None:
        """
        Registra perguntas para o cliente.
        
        Args:
            questions: Lista de perguntas
        """
        if self.current_project:
            self.current_project.questions_for_client.extend(questions)
        
        print(f"\n{'='*60}")
        print("PERGUNTAS PARA O CLIENTE")
        print(f"{'='*60}")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}")
        print(f"{'='*60}\n")
    
    def receive_client_response(self, question_index: int, response: str) -> None:
        """
        Registra a resposta do cliente a uma pergunta.
        
        Args:
            question_index: Índice da pergunta (1-based)
            response: Resposta do cliente
        """
        if self.current_project and question_index <= len(self.current_project.questions_for_client):
            question = self.current_project.questions_for_client[question_index - 1]
            self.current_project.client_responses[question] = response
            self.current_project.updated_at = datetime.now().isoformat()
    
    def get_project_summary(self) -> str:
        """Retorna um resumo do estado atual do projeto."""
        if not self.current_project:
            return "Nenhum projeto ativo."
        
        p = self.current_project
        summary = f"""
{'='*60}
RESUMO DO PROJETO
{'='*60}
ID: {p.project_id}
Nome: {p.project_name}
Fase Atual: {p.current_phase.value}
Criado em: {p.created_at}
Atualizado em: {p.updated_at}

Times Executados: {len(p.team_outputs)}
- {', '.join(p.team_outputs.keys()) if p.team_outputs else 'Nenhum'}

Perguntas Pendentes: {len(p.questions_for_client) - len(p.client_responses)}
Respostas Recebidas: {len(p.client_responses)}
{'='*60}
"""
        return summary


def get_agency_orchestrator() -> AgencyOrchestrator:
    """Factory function para criar o orquestrador da agência."""
    return AgencyOrchestrator()


if __name__ == "__main__":
    # Teste do orquestrador
    print("Iniciando teste do Agency Orchestrator...")
    
    orchestrator = get_agency_orchestrator()
    print(f"Times disponíveis: {list(orchestrator.teams.keys())}")
