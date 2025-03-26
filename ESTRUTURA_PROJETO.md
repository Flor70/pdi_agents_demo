# Estrutura do Projeto Templo Agents

## Visão Geral

O projeto Templo Agents é uma plataforma modular para agregação de diversos fluxos de AI Agents. A arquitetura do projeto foi desenhada para facilitar a adição de novos fluxos de trabalho sem a necessidade de duplicar código, permitindo reutilização de componentes comuns. 

Este documento explica a estrutura organizacional do projeto e como desenvolver novos fluxos de trabalho aproveitando os componentes existentes.

## Estrutura de Diretórios

```
src/
├── assistants/       # Classes dos assistentes AI (interview, pdi, etc)
│   ├── base_assistant.py  # Classe base para novos assistentes
│   ├── docs/         # Documentação e guias dos fluxos
│   └── ...
├── core/             # Funcionalidades essenciais
│   ├── utils.py      # Utilitários para criação de crews
│   └── ...
├── models/           # Modelos de dados Pydantic
│   └── pdi_models.py # Modelos para o fluxo PDI
├── tools/            # Ferramentas utilizadas pelos agentes
├── web/              # Interface web com Streamlit
│   ├── app.py        # Página principal da aplicação
│   ├── components/   # Componentes reutilizáveis
│   │   ├── assistant_manager.py  # Gerenciamento de assistentes
│   │   ├── auth.py               # Autenticação e gestão de sessão
│   │   ├── config.py             # Configurações centralizadas
│   │   ├── file_viewer.py        # Componentes de visualização de arquivos
│   │   ├── flow_base.py          # Classe base para fluxos de trabalho
│   │   ├── flow_buttons.py       # Componentes de botões de navegação
│   │   ├── interview_flow.py     # Lógica de entrevista e execução de crew
│   │   ├── sidebar.py            # Componente de barra lateral
│   │   └── styles.py             # Estilos CSS
│   └── pages/         # Páginas da aplicação
│       ├── pdi_app.py            # Página de PDI
│       ├── plano_aula.py         # Página de Plano de Aula
│       └── ...
└── ...
```

## Componentes Principais

### Classe BaseFlow (flow_base.py)

A classe `BaseFlow` é fundamental para a arquitetura modular do projeto. Ela define a estrutura base de um fluxo de trabalho e inclui métodos comuns que são compartilhados entre diferentes fluxos.

Principais métodos:
- `setup_page()`: Configura a página com estilos e configurações
- `initialize_state()`: Inicializa o estado da sessão
- `setup_authentication()`: Gerencia autenticação com a API OpenAI
- `show_sidebar()`: Exibe a barra lateral de navegação
- `show_main_interface()`: Orquestra a exibição da interface principal

Os seguintes métodos são projetados para serem sobrescritos nas classes derivadas:
- `initialize_assistants()`: Inicializa os assistentes específicos do fluxo
- `show_interview_interface()`: Exibe a interface de entrevista
- `show_chat_interface()`: Exibe a interface de chat
- `show_custom_interface()`: Exibe interfaces personalizadas

### Configurações Centralizadas (config.py)

Este módulo centraliza constantes, mapeamentos e configurações para diferentes fluxos. A estrutura `FLOW_CONFIGS` define configurações específicas para cada tipo de fluxo.

### Gerenciamento de Assistentes

O arquivo `assistant_manager.py` fornece funções para:
- Inicializar assistentes
- Exibir interfaces de chat genéricas
- Fazer upload de documentos para assistentes

### Autenticação e Estado da Sessão

O arquivo `auth.py` contém funções para:
- Verificar a validade da chave API da OpenAI
- Configurar autenticação
- Inicializar o estado da sessão com valores padrão

### Componentes Visuais

- `styles.py`: Carrega estilos CSS comuns
- `sidebar.py`: Gerencia a barra lateral de navegação
- `file_viewer.py`: Visualiza conteúdo de arquivos markdown
- `flow_buttons.py`: Renderiza botões e grids para seleção de fluxos

### Fluxo de Entrevista e Crew

O arquivo `interview_flow.py` contém funções para:
- Inicializar assistentes de entrevista
- Processar respostas de entrevistas
- Mostrar interfaces de entrevista
- Executar processamento de crew

## Fluxos Existentes

### PDI (Plano de Desenvolvimento Individual)

Implementado na classe `PDIFlow`, este fluxo:
1. Conduz uma entrevista com o usuário usando o `InterviewAssistant`
2. Processa os dados da entrevista usando uma crew para gerar um PDI
3. Oferece uma interface para visualizar documentos gerados
4. Disponibiliza assistentes para consulta e criação de posts para LinkedIn

### Plano de Aula

Implementado na classe `PlanoAulaFlow`, este fluxo segue uma estrutura similar ao PDI, mas com adaptações específicas para a criação de planos de aula.

## Como Desenvolver Novos Fluxos

### 1. Criar uma Nova Classe de Fluxo

Para criar um novo fluxo, crie uma nova classe que herda de `BaseFlow`:

```python
# src/web/components/novo_fluxo.py
import streamlit as st
from .flow_base import BaseFlow

class NovoFluxo(BaseFlow):
    def __init__(self, project_root=None):
        super().__init__("novo_fluxo", project_root)
        
    def initialize_assistants(self):
        # Inicializar assistentes específicos
        pass
        
    def show_interview_interface(self):
        # Implementar interface de entrevista
        pass
        
    def show_chat_interface(self):
        # Implementar interface de chat
        pass
        
    def show_custom_interface(self):
        # Implementar interfaces personalizadas
        pass
```

### 2. Adicionar Configuração ao config.py

Defina configurações específicas para seu fluxo:

```python
# Adicionar ao dicionário FLOW_CONFIGS em src/web/components/config.py
"novo_fluxo": {
    "title": "✨ Templo Novo Fluxo",
    "description": "Descrição do novo fluxo.",
    "page_config": {
        "page_title": "Templo Novo Fluxo",
        "page_icon": "🔮",
        "layout": "centered"
    },
    "file_order": [
        "arquivo1.md",
        "arquivo2.md"
    ],
    "file_titles": {
        "arquivo1.md": "📝 Título Amigável 1",
        "arquivo2.md": "📋 Título Amigável 2"
    },
    "guide_path": "novo_fluxo_guide.md"
}
```

### 3. Criar a Página Streamlit

Crie um arquivo para a página do novo fluxo:

```python
# src/web/pages/novo_fluxo.py
#!/usr/bin/env python3

import sys
from pathlib import Path
import sqlite3

# SQLite3 version fix for Streamlit Cloud
try:
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass

# Configurar caminhos
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
src_path = str(PROJECT_ROOT / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from web.components.novo_fluxo import NovoFluxo

def main():
    """Executa o novo fluxo."""
    flow = NovoFluxo(PROJECT_ROOT)
    flow.run()

if __name__ == "__main__":
    main()
```

### 4. Adicionar o Botão na Página Principal

Adicione seu fluxo à lista de fluxos disponíveis:

```python
# Adicionar ao array flows em src/web/app.py
{
    "title": "Seu Novo Fluxo",
    "icon": "🔮",
    "description": "Descrição curta do seu fluxo",
    "url": "novo_fluxo"
}
```

### 5. Criar Assistentes Necessários

Se o seu fluxo requer assistentes personalizados:

1. Criar um assistente que herde da classe `BaseAssistant` (opcional):

```python
# src/assistants/novo_assistant.py
from .base_assistant import BaseAssistant

class NovoAssistant(BaseAssistant):
    def __init__(self, openai_api_key):
        super().__init__(openai_api_key)
        
    def initialize_assistant(self):
        instructions = """Instruções personalizadas para o seu assistente."""
        super().initialize_assistant("Nome do Assistente", instructions)
        
    # Métodos adicionais específicos
```

2. Ou usar os assistentes existentes conforme necessário.

## Boas Práticas

1. **Modularização**: Mantenha cada fluxo em seu próprio arquivo.
2. **Reutilização**: Utilize os componentes existentes sempre que possível.
3. **Configuração Centralizada**: Defina constantes e configurações em `config.py`.
4. **Processamento Assíncrono**: Use `asyncio` para operações demoradas.
5. **Tratamento de Erros**: Sempre inclua tratamento de exceções.
6. **Documentação**: Documente claramente o propósito de cada método e classe.

## Componentes Reutilizáveis Importantes

### Interfaces de Navegação
```python
from web.components import show_sidebar, get_generated_files
```

### Gestão de Arquivos
```python
from web.components import show_file_content, show_pdi_tracker
```

### Gerenciamento de Assistentes
```python
from web.components import initialize_assistant, show_chat_interface, upload_documents_to_assistant
```

### Fluxo de Entrevista
```python
from web.components import initialize_interview_assistant, process_interview_completion, show_interview_interface
```

### Autenticação
```python
from web.components import setup_authentication, initialize_session_state
```

### Estilos e Configuração
```python
from web.components import load_css
from web.components import PDI_FILE_ORDER, PDI_FILE_TITLES, DEFAULT_PAGE_CONFIG, FLOW_CONFIGS
```

## Conclusão

A arquitetura modular do projeto Templo Agents oferece uma estrutura robusta para desenvolvimento e expansão de diferentes fluxos de AI Agents. Ao seguir as diretrizes e padrões estabelecidos neste documento, você pode facilmente criar e integrar novos fluxos de trabalho mantendo a consistência e reutilizando componentes existentes. 