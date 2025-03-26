import streamlit as st
from pathlib import Path
import os
import asyncio

from . import (
    load_css,
    show_sidebar,
    get_generated_files,
    setup_authentication,
    initialize_session_state,
    show_file_content,
    show_chat_interface,
    initialize_interview_assistant,
    process_interview_completion,
    show_interview_interface,
    run_crew_processing
)
from .config import FLOW_CONFIGS


class BaseFlow:
    """Classe base para todos os fluxos de trabalho."""

    def __init__(self, flow_type="default", project_root=None):
        """
        Inicializa o fluxo de trabalho.

        Args:
            flow_type (str): Tipo de fluxo (ex: "pdi", "plano_aula")
            project_root (Path): Caminho raiz do projeto
        """
        self.flow_type = flow_type
        self.config = FLOW_CONFIGS.get(
            flow_type, FLOW_CONFIGS.get("default", {}))

        # Configurar o caminho raiz do projeto
        if project_root is None:
            # Encontra o caminho raiz do projeto automaticamente
            current_file = Path(__file__)
            self.project_root = current_file.parent.parent.parent.parent
        else:
            self.project_root = Path(project_root)

        # Configurar o diretório de saída
        self.output_dir = str(self.project_root / "output")

        # Diretório de documentação
        self.docs_dir = str(self.project_root / "src" / "assistants" / "docs")

        # Inicializar assistentes como None
        self.interview_assistant = None
        self.chat_assistant = None

    def setup_page(self):
        """Configura a página com os estilos e configurações necessárias."""
        # Aplicar configurações da página
        page_config = self.config.get("page_config", {})
        st.set_page_config(**page_config)

        # Carregar estilos CSS
        load_css()

        # Definir o título da página
        st.title(self.config.get("title", "Templo Agents"))

    def initialize_state(self):
        """Inicializa o estado da sessão com valores padrão."""
        # Define o tipo de fluxo
        if 'flow_type' not in st.session_state:
            st.session_state.flow_type = self.flow_type

        # Outros valores padrão
        default_values = {
            'interview_complete': False,
            'interview_data': None,
            'current_page': 'main',
            'current_file': str(Path(self.docs_dir) / self.config.get("guide_path", "guide.md"))
        }

        initialize_session_state(self.flow_type, default_values)

    def setup_authentication(self):
        """Configura a autenticação com a API OpenAI."""
        return setup_authentication()

    def initialize_assistants(self):
        """Inicializa os assistentes necessários para o fluxo."""
        # Este método deve ser implementado nas classes derivadas
        pass

    def get_generated_files(self):
        """Obtém a lista de arquivos gerados no diretório de saída."""
        return get_generated_files(self.output_dir)

    def show_sidebar(self):
        """Mostra a barra lateral de navegação."""
        generated_files = self.get_generated_files()

        show_sidebar(
            generated_files,
            self.config.get("file_order", []),
            self.config.get("file_titles", {}),
            self.project_root,
            self.output_dir,
            st.session_state.current_page,
            st.session_state.current_file
        )

    def show_file_content(self):
        """Mostra o conteúdo do arquivo atual."""
        default_file = str(Path(self.docs_dir) /
                           self.config.get("guide_path", "guide.md"))
        show_file_content(st.session_state.current_file, default_file)

    def show_main_interface(self):
        """Mostra a interface principal com base no estado atual."""
        # Verifica se a entrevista foi concluída
        if st.session_state.interview_complete:
            # Mostrar a sidebar
            self.show_sidebar()

            # Mostrar a interface apropriada com base na página atual
            if st.session_state.current_page == 'main':
                self.show_file_content()
            elif st.session_state.current_page == 'chat' and self.chat_assistant:
                self.show_chat_interface()
            else:
                # Implementações específicas para cada tipo de fluxo
                self.show_custom_interface()
        else:
            # Inicializa o assistente de entrevista e mostra a interface
            self.show_interview_interface()

    def show_chat_interface(self):
        """Mostra a interface de chat com o assistente."""
        # Este método deve ser implementado nas classes derivadas ou estendido com funcionalidades específicas
        pass

    def show_interview_interface(self):
        """Mostra a interface de entrevista."""
        # Este método deve ser implementado nas classes derivadas ou estendido com funcionalidades específicas
        pass

    def show_custom_interface(self):
        """Mostra interfaces personalizadas específicas do fluxo."""
        # Este método deve ser implementado nas classes derivadas
        st.info(
            f"Interface personalizada não implementada para a página: {st.session_state.current_page}")

    def run(self):
        """Executa o fluxo de trabalho."""
        # Configuração inicial
        self.setup_page()
        self.initialize_state()

        # Verifica autenticação
        if not self.setup_authentication():
            return

        # Inicializar assistentes
        self.initialize_assistants()

        # Mostrar interface principal
        self.show_main_interface()
