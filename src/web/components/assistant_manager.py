import streamlit as st
import asyncio
from pathlib import Path


def initialize_assistant(assistant_class, api_key, session_state_key, initialize_method=None, **kwargs):
    """
    Inicializa um assistente se ele ainda não estiver inicializado.

    Args:
        assistant_class (class): Classe do assistente a ser inicializado
        api_key (str): Chave da API OpenAI
        session_state_key (str): Chave para armazenar o assistente no st.session_state
        initialize_method (callable, optional): Método opcional a ser chamado após inicialização
        **kwargs: Argumentos adicionais para passar ao inicializar o assistente

    Returns:
        objeto: O assistente inicializado
    """
    if session_state_key not in st.session_state or st.session_state[session_state_key] is None:
        assistant = assistant_class(api_key, **kwargs)
        assistant.initialize_assistant()

        # Se há um método adicional para inicializar, chame-o
        if initialize_method:
            initialize_method(assistant)

        st.session_state[session_state_key] = assistant

    return st.session_state[session_state_key]


def show_chat_interface(title, description, assistant, messages_key="chat_messages", process_response=None):
    """
    Interface genérica de chat que pode ser usada com diferentes assistentes.

    Args:
        title (str): Título da interface de chat
        description (str): Descrição da interface de chat
        assistant (object): Objeto do assistente inicializado
        messages_key (str): Chave para armazenar mensagens no st.session_state
        process_response (callable, optional): Função para processar a resposta do assistente
    """
    # Verifica se o assistente está inicializado
    if assistant is None:
        st.error("Erro: Assistente não inicializado corretamente")
        return

    st.title(title)
    st.markdown(description)

    # Inicializa mensagens se necessário
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []

    # Display chat messages
    for message in st.session_state[messages_key]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Digite sua mensagem"):
        # Add user message to chat history
        st.session_state[messages_key].append(
            {"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Get assistant response
        with st.chat_message("assistant"):
            # Verifica se não está em processo especial
            if not (process_response and "[INTERVIEW_COMPLETE]" in prompt):
                with st.spinner("Pensando..."):
                    response = asyncio.run(assistant.get_response(prompt))
            else:
                response = asyncio.run(assistant.get_response(prompt))

            # Verifica se precisamos processar a resposta de maneira especial
            if process_response:
                if process_response(response, st.session_state):
                    st.rerun()

            st.session_state[messages_key].append(
                {"role": "assistant", "content": response})
            st.write(response)


def upload_documents_to_assistant(assistant, output_dir, method_name="upload_pdi_documents"):
    """
    Faz upload de documentos para o assistente usando o método especificado.

    Args:
        assistant (object): Objeto do assistente inicializado
        output_dir (str): Diretório onde estão os documentos
        method_name (str): Nome do método a ser chamado para fazer upload dos documentos

    Returns:
        bool: True se o upload foi bem-sucedido, False caso contrário
    """
    try:
        if hasattr(assistant, method_name):
            method = getattr(assistant, method_name)
            result = method(output_dir)
            return True, result
        else:
            return False, f"Método {method_name} não encontrado no assistente"
    except Exception as e:
        return False, str(e)
