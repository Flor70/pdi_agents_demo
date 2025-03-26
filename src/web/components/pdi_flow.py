import streamlit as st
import asyncio
from pathlib import Path

from assistants.interview_assistant import InterviewAssistant
from assistants.pdi_assistant import PDIAssistant
from assistants.linkedin_assistant import LinkedInAssistant
from assistants.mestre_dos_magos_assistant import MestreDosMagosAssistant
from core.utils import create_crew, load_config

from .flow_base import BaseFlow
from . import (
    initialize_assistant,
    show_chat_interface,
    upload_documents_to_assistant,
    initialize_interview_assistant,
    process_interview_completion,
    show_interview_interface,
    run_crew_processing,
    show_pdi_tracker
)


class PDIFlow(BaseFlow):
    """Fluxo de PDI específico."""

    def __init__(self, project_root=None):
        """Inicializa o fluxo de PDI."""
        super().__init__("pdi", project_root)

    def initialize_assistants(self):
        """Inicializa os assistentes necessários para o fluxo de PDI."""
        # Assistente de entrevista
        if 'interview_assistant' not in st.session_state or st.session_state.interview_assistant is None:
            initialize_interview_assistant(
                InterviewAssistant,
                st.session_state.openai_api_key,
                'interview_assistant'
            )

        # PDI Assistant (para chat)
        if st.session_state.interview_complete and (
            'pdi_assistant' not in st.session_state or
            st.session_state.pdi_assistant is None
        ):
            # Inicializa o assistente PDI
            st.session_state.pdi_assistant = PDIAssistant(
                st.session_state.openai_api_key)
            st.session_state.pdi_assistant.initialize_assistant()

            # Faz upload dos documentos
            try:
                st.session_state.pdi_assistant.upload_pdi_documents(
                    self.output_dir)
                st.session_state.pdi_assistant.create_thread()
            except ValueError as e:
                st.error(f"Erro ao carregar documentos PDI: {str(e)}")

        # LinkedIn Assistant
        if st.session_state.interview_complete and (
            'linkedin_assistant' not in st.session_state or
            st.session_state.linkedin_assistant is None
        ) and st.session_state.current_page == 'linkedin':
            st.session_state.linkedin_assistant = LinkedInAssistant(
                st.session_state.openai_api_key)
            st.session_state.linkedin_assistant.initialize_assistant()

        # Mestre dos Magos Assistant
        if st.session_state.interview_complete and (
            'mestre_dos_magos_assistant' not in st.session_state or
            st.session_state.mestre_dos_magos_assistant is None
        ) and st.session_state.current_page == 'mestre_dos_magos':
            st.session_state.mestre_dos_magos_assistant = MestreDosMagosAssistant(
                st.session_state.openai_api_key)
            st.session_state.mestre_dos_magos_assistant.initialize_assistant()
            st.session_state.mestre_dos_magos_assistant.create_thread()
            st.session_state.mestre_dos_magos_messages = []

    def show_interview_interface(self):
        """Mostra a interface de entrevista do PDI."""
        # Garante que o assistente está inicializado
        if 'interview_assistant' not in st.session_state or st.session_state.interview_assistant is None:
            initialize_interview_assistant(
                InterviewAssistant,
                st.session_state.openai_api_key,
                'interview_assistant'
            )

        # Função para processar a resposta da entrevista
        def process_completion(response):
            if process_interview_completion(response):
                # Se a entrevista foi concluída, inicia o processamento da crew
                spinner_message = "🚀 Iniciando a criação do seu PDI personalizado... \n\n" + \
                    "Este processo envolve várias etapas de análise e pode levar alguns minutos. " + \
                    "Estamos trabalhando para criar um plano detalhado e sob medida para você! 😊"

                run_crew_processing(
                    st.session_state,
                    create_crew,
                    load_config,
                    self.project_root,
                    spinner_message
                )
                return True
            return False

        # Mostra a interface de entrevista
        show_interview_interface(
            st.session_state.interview_assistant,
            process_completion,
            "messages"
        )

    def show_chat_interface(self):
        """Mostra a interface de chat com o consultor PDI."""
        show_chat_interface(
            title="💬 Consultor PDI Bot",
            description="""
            Olá! Sou seu consultor especializado no Plano de Desenvolvimento Individual.
            Posso responder perguntas sobre o perfil do colaborador, recomendações e plano de desenvolvimento.
            Como posso ajudar?
            """,
            assistant=st.session_state.pdi_assistant,
            messages_key="chat_messages"
        )

    def show_linkedin_interface(self):
        """Mostra a interface para criação de posts do LinkedIn."""
        # Inicializa o assistente de LinkedIn se necessário
        if st.session_state.linkedin_assistant is None:
            st.session_state.linkedin_assistant = LinkedInAssistant(
                st.session_state.openai_api_key)
            st.session_state.linkedin_assistant.initialize_assistant()

            # Tenta gerar o post inicial
            try:
                # Gera o post inicial automaticamente
                initial_post = st.session_state.linkedin_assistant.upload_pdi_documents(
                    self.output_dir)
                if initial_post:
                    st.session_state.linkedin_messages = [
                        {"role": "assistant", "content": initial_post}
                    ]
            except ValueError as e:
                st.error(str(e))
                return

        # Mostra a interface
        show_chat_interface(
            title="📱 LinkedIn Post Creator",
            description="Este assistente criou um post do LinkedIn celebrando o início do seu PDI. Você pode pedir ajustes conforme necessário.",
            assistant=st.session_state.linkedin_assistant,
            messages_key="linkedin_messages"
        )

    def show_mestre_dos_magos_interface(self):
        """Mostra a interface do Mestre dos Magos."""
        show_chat_interface(
            title="🧙‍♂️ Mestre dos Magos",
            description="Este assistente é um mestre dos magos e pode te ajudar a cumprir sua jornada de PDI com sabedoria.",
            assistant=st.session_state.mestre_dos_magos_assistant,
            messages_key="mestre_dos_magos_messages"
        )

    def show_pdi_tracker_interface(self):
        """Mostra a interface de visualização do PDI."""
        show_pdi_tracker(self.output_dir)

    def show_custom_interface(self):
        """Mostra interfaces personalizadas específicas do PDI."""
        if st.session_state.current_page == 'pdi_tracker':
            self.show_pdi_tracker_interface()
        elif st.session_state.current_page == 'linkedin':
            self.show_linkedin_interface()
        elif st.session_state.current_page == 'mestre_dos_magos':
            self.show_mestre_dos_magos_interface()
        else:
            super().show_custom_interface()
