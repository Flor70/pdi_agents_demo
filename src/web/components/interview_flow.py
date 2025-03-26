import streamlit as st
import asyncio
import os
from pathlib import Path


def initialize_interview_assistant(assistant_class, openai_api_key, session_state_key):
    """
    Inicializa o assistente de entrevista.

    Args:
        assistant_class (class): Classe do assistente de entrevista
        openai_api_key (str): Chave da API OpenAI
        session_state_key (str): Chave para armazenar o assistente no st.session_state
    """
    if session_state_key not in st.session_state or st.session_state[session_state_key] is None:
        assistant = assistant_class(openai_api_key)
        assistant.initialize_assistant()
        st.session_state[session_state_key] = assistant
        # Inicializa messages com a primeira mensagem do assistente
        if hasattr(assistant, 'messages') and assistant.messages:
            st.session_state.messages = assistant.messages
        else:
            st.session_state.messages = []


def process_interview_completion(response, interview_data_key="interview_data", completion_marker="[INTERVIEW_COMPLETE]"):
    """
    Processa a resposta do assistente para verificar se a entrevista foi concluída.

    Args:
        response (str): Resposta do assistente
        interview_data_key (str): Chave para armazenar os dados da entrevista no st.session_state
        completion_marker (str): Marcador de conclusão da entrevista

    Returns:
        bool: True se a entrevista foi concluída, False caso contrário
    """
    if isinstance(response, str) and completion_marker in response:
        st.session_state.interview_complete = True
        st.session_state[interview_data_key] = response.split(completion_marker)[
            1].strip()
        return True
    return False


async def start_crew(crew_creator, agents_config, tasks_config, interview_data, openai_api_key):
    """
    Inicia a crew para processar os dados da entrevista.

    Args:
        crew_creator (callable): Função para criar a crew
        agents_config (dict): Configuração dos agentes
        tasks_config (dict): Configuração das tarefas
        interview_data (str): Dados da entrevista
        openai_api_key (str): Chave da API OpenAI

    Returns:
        object: Resultado da execução da crew
    """
    crew = await crew_creator(agents_config, tasks_config, interview_data, openai_api_key=openai_api_key)
    return crew.kickoff()


def show_interview_interface(assistant, process_interview_completion_fn=None, messages_key="messages"):
    """
    Mostra a interface de entrevista.

    Args:
        assistant (object): Assistente de entrevista
        process_interview_completion_fn (callable, optional): Função para processar a conclusão da entrevista
        messages_key (str): Chave para armazenar mensagens no st.session_state
    """
    st.title("🎤 Entrevista")
    st.markdown("""
    A seguir vamos começar uma entrevista para conhecer melhor o seu perfil.
    Por favor, responda as perguntas do nosso assistente para que possamos construir um plano personalizado para você.
    """)

    # Inicializa mensagens se necessário
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    # Display chat messages
    for message in st.session_state[messages_key]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Digite sua resposta"):
        # Add user message to chat history
        st.session_state[messages_key].append(
            {"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = asyncio.run(assistant.get_response(prompt))

            # Processa a resposta se houver função para isso
            if process_interview_completion_fn:
                if process_interview_completion_fn(response):
                    st.rerun()

            st.session_state[messages_key].append(
                {"role": "assistant", "content": response})
            st.write(response)


def run_crew_processing(session_state, crew_creator, load_config_fn, project_root, spinner_message="Processando dados..."):
    """
    Executa o processamento da crew após a conclusão da entrevista.

    Args:
        session_state (SessionState): Estado da sessão Streamlit
        crew_creator (callable): Função para criar a crew
        load_config_fn (callable): Função para carregar configurações
        project_root (Path): Caminho raiz do projeto
        spinner_message (str): Mensagem a ser exibida durante o processamento
    """
    with st.spinner(spinner_message):
        agents_config = str(project_root / 'config' / 'agents.yaml')
        tasks_config = str(project_root / 'config' / 'tasks.yaml')
        agents_config, tasks_config = load_config_fn(
            agents_config, tasks_config)
        result = asyncio.run(
            start_crew(
                crew_creator,
                agents_config,
                tasks_config,
                session_state.interview_data,
                openai_api_key=session_state.openai_api_key
            )
        )

    # Atualiza a página atual e arquivo atual após concluir o processamento
    session_state.current_page = 'main'
    session_state.current_file = str(
        project_root / 'src' / 'assistants' / 'docs' / 'pdi_guide.md')
