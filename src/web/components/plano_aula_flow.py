import streamlit as st
import asyncio
from pathlib import Path

from .flow_base import BaseFlow
from . import (
    initialize_assistant,
    initialize_interview_assistant,
    process_interview_completion,
    show_interview_interface,
    run_crew_processing,
    show_chat_interface
)

# Importações condicionais para um futuro assistente de plano de aula
try:
    from assistants.plano_aula_assistant import PlanoAulaAssistant
    from assistants.plano_aula_interview_assistant import PlanoAulaInterviewAssistant
    ASSISTANTS_AVAILABLE = True
except ImportError:
    # Se os assistentes ainda não foram implementados
    from assistants.interview_assistant import InterviewAssistant
    ASSISTANTS_AVAILABLE = False


class PlanoAulaFlow(BaseFlow):
    """Fluxo de Plano de Aula."""

    def __init__(self, project_root=None):
        """Inicializa o fluxo de Plano de Aula."""
        super().__init__("plano_aula", project_root)

    def initialize_assistants(self):
        """Inicializa os assistentes necessários para o fluxo de Plano de Aula."""
        # Assistente de entrevista
        if 'interview_assistant' not in st.session_state or st.session_state.interview_assistant is None:
            if ASSISTANTS_AVAILABLE:
                initialize_interview_assistant(
                    PlanoAulaInterviewAssistant,
                    st.session_state.openai_api_key,
                    'interview_assistant'
                )
            else:
                # Fallback para o assistente de entrevista padrão
                initialize_interview_assistant(
                    InterviewAssistant,
                    st.session_state.openai_api_key,
                    'interview_assistant'
                )

        # Assistente de Plano de Aula (para chat)
        if st.session_state.interview_complete and (
            'plano_aula_assistant' not in st.session_state or
            st.session_state.plano_aula_assistant is None
        ):
            if ASSISTANTS_AVAILABLE:
                # Inicializa o assistente de Plano de Aula
                st.session_state.plano_aula_assistant = PlanoAulaAssistant(
                    st.session_state.openai_api_key)
                st.session_state.plano_aula_assistant.initialize_assistant()

                # Faz upload dos documentos
                try:
                    st.session_state.plano_aula_assistant.upload_documents(
                        self.output_dir)
                    st.session_state.plano_aula_assistant.create_thread()
                except ValueError as e:
                    st.error(
                        f"Erro ao carregar documentos do Plano de Aula: {str(e)}")
            else:
                # Mensagem de aviso que o assistente ainda não está disponível
                st.info(
                    "Os assistentes específicos para o Plano de Aula ainda estão em desenvolvimento.")

    def show_interview_interface(self):
        """Mostra a interface de entrevista do Plano de Aula."""
        # Garante que o assistente está inicializado
        if 'interview_assistant' not in st.session_state or st.session_state.interview_assistant is None:
            if ASSISTANTS_AVAILABLE:
                initialize_interview_assistant(
                    PlanoAulaInterviewAssistant,
                    st.session_state.openai_api_key,
                    'interview_assistant'
                )
            else:
                initialize_interview_assistant(
                    InterviewAssistant,
                    st.session_state.openai_api_key,
                    'interview_assistant'
                )

        # Função para processar a resposta da entrevista
        def process_completion(response):
            if process_interview_completion(response):
                # Aqui você pode adicionar um processamento específico para plano de aula
                # Por enquanto, vamos apenas marcar como concluído
                st.session_state.current_page = 'main'
                st.session_state.current_file = str(
                    Path(self.docs_dir) / self.config.get("guide_path", "guide.md"))
                return True
            return False

        # Mostra a interface de entrevista
        show_interview_interface(
            st.session_state.interview_assistant,
            process_completion,
            "messages"
        )

    def show_chat_interface(self):
        """Mostra a interface de chat com o consultor de Plano de Aula."""
        if ASSISTANTS_AVAILABLE and hasattr(st.session_state, 'plano_aula_assistant'):
            show_chat_interface(
                title="💬 Consultor de Plano de Aula",
                description="""
                Olá! Sou seu consultor especializado em Planos de Aula.
                Posso responder perguntas sobre o plano, atividades e recursos.
                Como posso ajudar?
                """,
                assistant=st.session_state.plano_aula_assistant,
                messages_key="chat_messages"
            )
        else:
            st.info(
                "O assistente de chat para Plano de Aula ainda está em desenvolvimento.")

    def show_custom_interface(self):
        """Mostra interfaces personalizadas específicas do Plano de Aula."""
        # Por enquanto, mostra apenas a interface padrão
        super().show_custom_interface()
