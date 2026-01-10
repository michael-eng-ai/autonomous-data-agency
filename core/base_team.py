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

ATUALIZAÇÃO v2.0:
- Integração com sistema de conhecimento em 3 camadas
- Knowledge Base (YAML) para best practices
- RAG Engine para conhecimento dinâmico
- Project Memory para contexto persistente
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
    knowledge_used: Dict[str, bool] = field(default_factory=dict)


class BaseTeam(ABC):
    """
    Classe base abstrata para todos os times de agentes.
    
    Cada time herda desta classe e implementa:
    - Definição dos agentes operacionais
    - Lógica específica do domínio
    - Critérios de validação específicos
    
    RECURSOS DE CONHECIMENTO:
    - Acesso automático à Knowledge Base do domínio
    - Busca semântica via RAG para conhecimento dinâmico
    - Memória de projeto para contexto persistente
    """
    
    def __init__(
        self,
        team_name: str,
        team_description: str,
        domain: str,
        num_operational_agents: int = 2
    ):
        """
        Inicializa o time de agentes.
        
        Args:
            team_name: Nome do time (ex: "Data Engineering")
            team_description: Descrição do propósito do time
            domain: Domínio do conhecimento (ex: "data_engineering")
            num_operational_agents: Número de agentes operacionais (2-3)
        """
        self.team_name = team_name
        self.team_description = team_description
        self.domain = domain
        self.num_operational_agents = min(max(num_operational_agents, 2), 3)
        
        # Inicializa os LLMs
        self.master_llm = get_llm("master")
        self.operational_llms = get_diverse_llms(self.num_operational_agents)
        
        # Inicializa o sistema de conhecimento
        self._init_knowledge_system()
        
        # Inicializa os agentes
        self.master_agent = self._create_master_agent()
        self.operational_agents = self._create_operational_agents()
        
        # Projeto atual (pode ser definido via set_project)
        self.current_project_id: Optional[str] = None
    
    def _init_knowledge_system(self) -> None:
        """Inicializa o sistema de conhecimento em 3 camadas."""
        try:
            from core.knowledge import (
                get_knowledge_base,
                get_rag_engine,
                get_project_memory,
                get_knowledge_manager
            )
            
            self.knowledge_base = get_knowledge_base()
            self.rag_engine = get_rag_engine()
            self.project_memory = get_project_memory()
            self.knowledge_manager = get_knowledge_manager()
            
            self._knowledge_available = True
            print(f"[{self.team_name}] Sistema de conhecimento inicializado")
            
        except ImportError as e:
            print(f"[{self.team_name}] Sistema de conhecimento não disponível: {e}")
            self.knowledge_base = None
            self.rag_engine = None
            self.project_memory = None
            self.knowledge_manager = None
            self._knowledge_available = False
    
    def set_project(self, project_id: str) -> None:
        """
        Define o projeto atual para contexto.
        
        Args:
            project_id: ID do projeto
        """
        self.current_project_id = project_id
        print(f"[{self.team_name}] Projeto definido: {project_id}")
    
    def _get_knowledge_context(self, task: str) -> str:
        """
        Obtém contexto de conhecimento relevante para a tarefa.
        
        Combina conhecimento das 3 camadas:
        1. Knowledge Base (YAML) - Best practices do domínio
        2. RAG Engine - Conhecimento dinâmico relevante
        3. Project Memory - Contexto do projeto atual
        
        Args:
            task: Descrição da tarefa
            
        Returns:
            String formatada com conhecimento relevante
        """
        if not self._knowledge_available:
            return ""
        
        parts = []
        
        # Camada 1: Knowledge Base
        try:
            kb_context = self.knowledge_base.format_for_prompt(
                self.domain,
                sections=['principles', 'checklists', 'anti_patterns']
            )
            if kb_context:
                parts.append("=" * 50)
                parts.append("CONHECIMENTO BASE (Best Practices)")
                parts.append("=" * 50)
                parts.append(kb_context)
        except Exception as e:
            print(f"[{self.team_name}] Erro ao carregar Knowledge Base: {e}")
        
        # Camada 2: RAG Engine
        try:
            if self.rag_engine and self.rag_engine.is_available():
                rag_context = self.rag_engine.search_for_prompt(
                    query=task,
                    n_results=3,
                    domain_filter=self.domain
                )
                if rag_context:
                    parts.append("\n" + "=" * 50)
                    parts.append("CONHECIMENTO DINÂMICO (RAG)")
                    parts.append("=" * 50)
                    parts.append(rag_context)
        except Exception as e:
            print(f"[{self.team_name}] Erro ao consultar RAG: {e}")
        
        # Camada 3: Project Memory
        try:
            if self.current_project_id and self.project_memory:
                project_context = self.project_memory.format_context_for_prompt(
                    self.current_project_id
                )
                if project_context:
                    parts.append("\n" + "=" * 50)
                    parts.append("CONTEXTO DO PROJETO")
                    parts.append("=" * 50)
                    parts.append(project_context)
        except Exception as e:
            print(f"[{self.team_name}] Erro ao carregar contexto do projeto: {e}")
        
        return "\n".join(parts) if parts else ""
    
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
   
4. VALIDAÇÃO COM CONHECIMENTO BASE: Compare as respostas com as best practices
   e anti-patterns fornecidos no contexto de conhecimento. Rejeite sugestões
   que violem princípios estabelecidos.
   
5. FORMATO DE SAÍDA: Sempre estruture sua validação no seguinte formato:
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
6. UTILIZE O CONHECIMENTO BASE fornecido no contexto para fundamentar suas respostas.
7. SIGA os checklists e EVITE os anti-patterns listados no conhecimento base.
"""
            
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", enhanced_prompt),
                ("human", "{input}")
            ])
            

            # Helper to get model name safely (handles OpenAI and Gemini)
            model_name = getattr(llm, "model_name", getattr(llm, "model", "unknown_model"))
            
            agent = prompt_template | llm
            agents.append((agent_id, agent_name, model_name, agent))
        
        return agents
    
    def _collect_operational_responses(
        self,
        task: str,
        knowledge_context: str
    ) -> List[AgentResponse]:
        """
        Coleta respostas de todos os agentes operacionais.
        
        Args:
            task: A tarefa a ser executada
            knowledge_context: Contexto de conhecimento a ser incluído
            
        Returns:
            Lista de respostas dos agentes operacionais
        """
        responses = []
        
        # Prepara o input com contexto de conhecimento
        if knowledge_context:
            full_input = f"""CONTEXTO DE CONHECIMENTO:
{knowledge_context}

TAREFA:
{task}"""
        else:
            full_input = task
        
        for agent_id, agent_name, model_name, agent in self.operational_agents:
            try:
                result = agent.invoke({"input": full_input})
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
        operational_responses: List[AgentResponse],
        knowledge_context: str
    ) -> ValidationResult:
        """
        Usa o agente mestre para validar e consolidar as respostas.
        
        Args:
            task: A tarefa original
            operational_responses: Respostas dos agentes operacionais
            knowledge_context: Contexto de conhecimento para validação
            
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

CONTEXTO DE CONHECIMENTO (use para validar as respostas):
{knowledge_context if knowledge_context else "Nenhum contexto adicional disponível."}

RESPOSTAS DOS AGENTES OPERACIONAIS:
{responses_text}

Por favor, analise as respostas acima e:
1. Identifique possíveis alucinações ou informações incorretas
2. Verifique se as respostas estão alinhadas com a tarefa E com o conhecimento base
3. Identifique violações de best practices ou uso de anti-patterns
4. Extraia e consolide as melhores ideias de cada resposta
5. Produza uma resposta final validada e otimizada
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
    
    def _store_execution_in_memory(
        self,
        task: str,
        output: 'TeamOutput'
    ) -> None:
        """
        Armazena a execução na memória do projeto.
        
        Args:
            task: Tarefa executada
            output: Resultado da execução
        """
        if not self._knowledge_available or not self.current_project_id:
            return
        
        try:
            from core.knowledge import MemoryType
            
            # Armazena a interação
            self.project_memory.store_interaction(
                project_id=self.current_project_id,
                interaction_type=f"team_execution_{self.domain}",
                content=f"Tarefa: {task[:200]}...\nStatus: {output.validation_result.status.value}",
                participants=[self.team_name]
            )
            
            # Se houver decisões importantes, armazena
            if output.validation_result.status == ValidationStatus.VALID:
                self.project_memory.store(
                    project_id=self.current_project_id,
                    memory_type=MemoryType.ARTIFACT,
                    key=f"{self.domain}_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    value=output.final_output[:1000],
                    metadata={"team": self.team_name, "task": task[:200]}
                )
                
        except Exception as e:
            print(f"[{self.team_name}] Erro ao armazenar na memória: {e}")
    
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
        
        # Obtém contexto de conhecimento
        print(f"\n[0/3] Carregando conhecimento do domínio '{self.domain}'...")
        knowledge_context = self._get_knowledge_context(task)
        knowledge_used = {
            "knowledge_base": bool(knowledge_context and "CONHECIMENTO BASE" in knowledge_context),
            "rag_engine": bool(knowledge_context and "CONHECIMENTO DINÂMICO" in knowledge_context),
            "project_memory": bool(knowledge_context and "CONTEXTO DO PROJETO" in knowledge_context)
        }
        
        if knowledge_context:
            print(f"  ✓ Conhecimento carregado: KB={knowledge_used['knowledge_base']}, RAG={knowledge_used['rag_engine']}, Memory={knowledge_used['project_memory']}")
        else:
            print(f"  ⚠ Nenhum conhecimento adicional disponível")
        
        print(f"\n[1/3] Coletando respostas dos {len(self.operational_agents)} agentes operacionais...")
        
        # Coleta respostas operacionais
        operational_responses = self._collect_operational_responses(task, knowledge_context)
        
        for resp in operational_responses:
            print(f"  ✓ {resp.agent_name} ({resp.model_used}) respondeu")
        
        print(f"\n[2/3] Agente Mestre validando e consolidando...")
        
        # Valida e consolida
        validation_result = self._validate_and_consolidate(
            task,
            operational_responses,
            knowledge_context
        )
        
        print(f"  ✓ Status: {validation_result.status.value}")
        
        execution_time = time.time() - start_time
        
        output = TeamOutput(
            team_name=self.team_name,
            task=task,
            operational_responses=operational_responses,
            validation_result=validation_result,
            final_output=validation_result.consolidated_response,
            execution_time_seconds=execution_time,
            knowledge_used=knowledge_used
        )
        
        # Armazena na memória do projeto
        print(f"\n[3/3] Armazenando execução na memória do projeto...")
        self._store_execution_in_memory(task, output)
        print(f"  ✓ Execução armazenada")
        
        return output
    
    def ask_clarification(self, question: str) -> str:
        """
        Método para solicitar esclarecimento ao cliente.
        Deve ser sobrescrito ou usado com interface de usuário.
        
        Args:
            question: Pergunta a ser feita
            
        Returns:
            Resposta do cliente
        """
        print(f"\n[{self.team_name}] PERGUNTA PARA O CLIENTE:")
        print(f"  {question}")
        # Em produção, isso seria integrado com uma interface
        return input("  Resposta: ")
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.team_name}' ({self.num_operational_agents} operacionais, domain='{self.domain}')>"
