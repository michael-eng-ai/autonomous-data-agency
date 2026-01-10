# 🔧 Instruções para Corrigir o CI da Branch Main

## 📋 Problema
O teste `test_project_lifecycle` em `tests/test_core.py` falha porque tenta inicializar equipes que precisam de `OPENAI_API_KEY`, mas a chave não está configurada no ambiente CI.

## ✅ Solução: Opção B - Usar Mock/Fake API Key

### Passo 1: Checkout da branch main
```bash
cd /home/seu/projeto/autonomous-data-agency
git checkout main
git pull origin main
```

### Passo 2: Editar o arquivo tests/conftest.py

Substitua o conteúdo de `tests/conftest.py` por:

```python
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CORREÇÃO: Configurar fake API key antes de qualquer import que precise dela
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-fake-key-for-testing-only"

@pytest.fixture
def mock_llm():
    """Mock for LLM responses."""
    mock = MagicMock()
    mock.invoke.return_value.content = "Mocked LLM Response"
    return mock

@pytest.fixture
def orchestrator(mock_llm):
    from core.agency_orchestrator import AgencyOrchestrator
    
    # CORREÇÃO: Usar patch.object para mockar get_llm de forma mais robusta
    with patch('core.agency_orchestrator.get_llm', return_value=mock_llm):
        with patch('teams.product_owner.team.get_llm', return_value=mock_llm):
            with patch('teams.architecture.team.get_llm', return_value=mock_llm):
                with patch('teams.data_engineering.team.get_llm', return_value=mock_llm):
                    orchestrator = AgencyOrchestrator()
                    orchestrator.global_master_agent = mock_llm
                    return orchestrator
```

### Passo 3: Verificar localmente (opcional mas recomendado)
```bash
# Instalar dependências se necessário
pip install -r requirements.txt

# Rodar os testes
pytest tests/test_core.py -v
```

### Passo 4: Commit e push
```bash
git add tests/conftest.py
git commit -m "fix: Add fake OPENAI_API_KEY for CI testing environment"
git push origin main
```

### Passo 5: Verificar o CI
```bash
# Acompanhe em: https://github.com/michael-eng-ai/autonomous-data-agency/actions
# O workflow "CI" deve passar com sucesso ✅
```

## 🎯 O que foi mudado?

1. **Linha 10-11**: Adiciona uma fake API key (`sk-fake-key-for-testing-only`) quando `OPENAI_API_KEY` não está definida no ambiente (como no CI)

2. **Linhas 22-27**: Usa `patch` do unittest.mock para mockar todas as chamadas a `get_llm()` em diferentes módulos, garantindo que nenhum código tente realmente se conectar à OpenAI

## 📊 Resultado Esperado

Depois de aplicar essa correção:
- ✅ Os testes na main devem passar
- ✅ O CI do GitHub Actions deve ficar verde
- ✅ Não é mais necessário configurar OPENAI_API_KEY como secret

## ⚠️ Notas

- Esta solução usa uma fake API key apenas para testes
- Em produção, você ainda deve usar uma chave real da OpenAI
- O mock garante que nenhuma chamada real à API da OpenAI seja feita durante os testes
