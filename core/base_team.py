"""
Base Team Module

Este módulo define a classe base abstrata para todos os times de agentes.
Cada time segue a arquitetura:
- 1 Agente Mestre (validador/consolidador)
- 2+ Agentes Operacionais (cada um com LLM diferente)

O fluxo de trabalho padrão é:
1. Tarefa chega ao time
2. Cada agente operacional propõe sua solução
3. Agente Mestre avalia, detecta alucinações, consolida
4. Resultado validado é retornado
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.llm_config import get_llm, get_diverse_llms


class AgentRole(Enum):
    """Papéis possíveis de um agente."""
    MASTER = "master"
    OPERATIONAL = "operational"


class ValidationStatus(Enum):
    """Status de validação de uma resposta."""
    VALID = "valid"
    HALLUCINATION_DETECTED = "hallucination_detected"
    OFF_TOPIC = "off_topic"
    INCOMPLETE = "incomplete"
    NEEDS_REVISION = "needs_revision"


@dataclass
class AgentResponse:
    """Resposta de um agente operacional."""
    agent_id: str
    agent_name: str
    model_used: str
    response: str
    confidence: float = 0.0
    reasoning: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ValidationResult:
    """Resultado da validação do Agente Mestre."""
    status: ValidationStatus
    consolidated_response: str
    issues_found: List[str] = field(default_factory=list)
    best_ideas_from: List[str] = field(default_factory=list)
    hallucinations_detected: List[str] = field(default_factory=list)
    recommendations: str = ""


@dataclass
class TeamOutput:
    """Saída final de um time de agentes."""
    team_name: str
    task: str
    operational_responses: List[AgentResponse]
    validation_result: ValidationResult
    final_output: str
    execution_time_seconds: float = 0.0


class BaseTeam(ABC):
    """
    Classe base abstrata para todos os times de agentes.
    
    Cada time herda desta classe e implementa:
    - Definição dos agentes operacionais
    - Lógica específica do domínio
    - Critérios de validação específicos
    """
    
    def __init__(
        self,
        team_name: str,
        team_description: str,
        num_operational_agents: int = 2
    ):
        """
        Inicializa o time de agentes.
        
        Args:
            team_name: Nome do time (ex: "Data Engineering")
            team_description: Descrição do propósito do time
            num_operational_agents: Número de agentes operacionais (2-3)
        """
        self.team_name = team_name
        self.team_description = team_description
        self.num_operational_agents = min(max(num_operational_agents, 2), 3)
        
        # Inicializa os LLMs
        self.master_llm = get_llm("master")
        self.operational_llms = get_diverse_llms(self.num_operational_agents)
        
        # Inicializa os agentes
        self.master_agent = self._create_master_agent()
        self.operational_agents = self._create_operational_agents()
    
    @abstractmethod
    def _get_operational_prompts(self) -> List[str]:
        """
        Retorna os prompts de sistema para os agentes operacionais.
        Cada time deve implementar seus próprios prompts especializados.
        
        Returns:
            Lista de prompts de sistema (um para cada agente operacional)
        """
        pass
    
    @abstractmethod
    def _get_master_prompt(self) -> str:
        """
        Retorna o prompt de sistema para o agente mestre.
        
        Returns:
            Prompt de sistema do agente mestre
        """
        pass
    
    def _create_master_agent(self) -> Any:
        """Cria o agente mestre do time."""
        master_prompt = self._get_master_prompt()
        
        # Adiciona instruções de validação anti-alucinação ao prompt
        enhanced_prompt = f"""{master_prompt}

INSTRUÇÕES CRÍTICAS DE VALIDAÇÃO:
1. DETECÇÃO DE ALUCINAÇÕES: Verifique se as respostas contêm informações inventadas,
   dados fictícios apresentados como reais, ou afirmações sem base factual.
   
2. VERIFICAÇÃO DE FOCO: Confirme se cada resposta está alinhada com a tarefa original.
   Identifique desvios do tema ou interpretações incorretas.
   
3. CONSOLIDAÇÃO: Extraia as melhores ideias de cada resposta operacional.
   Combine-as de forma coerente, eliminando redundâncias e contradições.
   
4. FORMATO DE SAÍDA: Sempre estruture sua validação no seguinte formato:
   - STATUS: [VÁLIDO/ALUCINAÇÃO/FORA_DO_TEMA/INCOMPLETO/REVISÃO_NECESSÁRIA]
   - PROBLEMAS ENCONTRADOS: [lista de problemas, se houver]
   - MELHORES IDEIAS DE: [quais agentes contribuíram com as melhores ideias]
   - RESPOSTA CONSOLIDADA: [a resposta final validada e consolidada]
"""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", enhanced_prompt),
            ("human", "{input}")
        ])
        
        return prompt_template | self.master_llm
    
    def _create_operational_agents(self) -> List[Tuple[str, Any]]:
        """Cria os agentes operacionais do time."""
        operational_prompts = self._get_operational_prompts()
        agents = []
        
        for i, (llm, prompt) in enumerate(zip(self.operational_llms, operational_prompts)):
            agent_id = f"{self.team_name.lower().replace(' ', '_')}_op_{i+1}"
            agent_name = f"Operacional {i+1}"
            
            # Adiciona instruções de qualidade ao prompt
            enhanced_prompt = f"""{prompt}

DIRETRIZES DE QUALIDADE:
1. Baseie suas respostas apenas em conhecimento verificável e práticas estabelecidas.
2. Se não tiver certeza sobre algo, indique claramente.
3. Evite inventar dados, estatísticas ou exemplos fictícios.
4. Mantenha o foco estritamente na tarefa solicitada.
5. Seja específico e acionável em suas recomendações.
"""
            
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", enhanced_prompt),
                ("human", "{input}")
            ])
            
            agent = prompt_template | llm
            agents.append((agent_id, agent_name, llm.model_name, agent))
        
        return agents
    
    def _collect_operational_responses(self, task: str) -> List[AgentResponse]:
        """
        Coleta respostas de todos os agentes operacionais.
        
        Args:
            task: A tarefa a ser executada
            
        Returns:
            Lista de respostas dos agentes operacionais
        """
        responses = []
        
        for agent_id, agent_name, model_name, agent in self.operational_agents:
            try:
                result = agent.invoke({"input": task})
                response = AgentResponse(
                    agent_id=agent_id,
                    agent_name=agent_name,
                    model_used=model_name,
                    response=result.content,
                    confidence=0.8  # Pode ser ajustado com base em métricas
                )
                responses.append(response)
            except Exception as e:
                responses.append(AgentResponse(
                    agent_id=agent_id,
                    agent_name=agent_name,
                    model_used=model_name,
                    response=f"ERRO: {str(e)}",
                    confidence=0.0
                ))
        
        return responses
    
    def _validate_and_consolidate(
        self,
        task: str,
        operational_responses: List[AgentResponse]
    ) -> ValidationResult:
        """
        Usa o agente mestre para validar e consolidar as respostas.
        
        Args:
            task: A tarefa original
            operational_responses: Respostas dos agentes operacionais
            
        Returns:
            Resultado da validação e consolidação
        """
        # Formata as respostas para o agente mestre
        responses_text = "\n\n".join([
            f"=== RESPOSTA DO {r.agent_name.upper()} (Modelo: {r.model_used}) ===\n{r.response}"
            for r in operational_responses
        ])
        
        validation_prompt = f"""TAREFA ORIGINAL:
{task}

RESPOSTAS DOS AGENTES OPERACIONAIS:
{responses_text}

Por favor, analise as respostas acima e:
1. Identifique possíveis alucinações ou informações incorretas
2. Verifique se as respostas estão alinhadas com a tarefa
3. Extraia e consolide as melhores ideias de cada resposta
4. Produza uma resposta final validada e otimizada
"""
        
        try:
            result = self.master_agent.invoke({"input": validation_prompt})
            
            # Parse da resposta do mestre (simplificado)
            content = result.content
            
            # Detecta status baseado no conteúdo
            status = ValidationStatus.VALID
            if "ALUCINAÇÃO" in content.upper() or "HALLUCINATION" in content.upper():
                status = ValidationStatus.HALLUCINATION_DETECTED
            elif "FORA DO TEMA" in content.upper() or "OFF TOPIC" in content.upper():
                status = ValidationStatus.OFF_TOPIC
            elif "INCOMPLETO" in content.upper() or "INCOMPLETE" in content.upper():
                status = ValidationStatus.INCOMPLETE
            
            return ValidationResult(
                status=status,
                consolidated_response=content,
                best_ideas_from=[r.agent_name for r in operational_responses if r.confidence > 0.5],
                hallucinations_detected=[],
                recommendations=""
            )
            
        except Exception as e:
            return ValidationResult(
                status=ValidationStatus.NEEDS_REVISION,
                consolidated_response=f"Erro na validação: {str(e)}",
                issues_found=[str(e)]
            )
    
    def execute(self, task: str) -> TeamOutput:
        """
        Executa o fluxo completo do time para uma tarefa.
        
        Args:
            task: A tarefa a ser executada
            
        Returns:
            Saída completa do time com todas as respostas e validação
        """
        import time
        start_time = time.time()
        
        print(f"\n{'='*60}")
        print(f"TIME: {self.team_name}")
        print(f"{'='*60}")
        print(f"Tarefa: {task[:100]}...")
        print(f"\n[1/2] Coletando respostas dos {len(self.operational_agents)} agentes operacionais...")
        
        # Coleta respostas operacionais
        operational_responses = self._collect_operational_responses(task)
        
        for resp in operational_responses:
            print(f"  ✓ {resp.agent_name} ({resp.model_used}) respondeu")
        
        print(f"\n[2/2] Agente Mestre validando e consolidando...")
        
        # Valida e consolida
        validation_result = self._validate_and_consolidate(task, operational_responses)
        
        print(f"  ✓ Status: {validation_result.status.value}")
        
        execution_time = time.time() - start_time
        
        return TeamOutput(
            team_name=self.team_name,
            task=task,
            operational_responses=operational_responses,
            validation_result=validation_result,
            final_output=validation_result.consolidated_response,
            execution_time_seconds=execution_time
        )
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.team_name}' ({self.num_operational_agents} operacionais)>"
