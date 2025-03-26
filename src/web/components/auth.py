import streamlit as st
import os
from openai import OpenAI


def verify_api_key(api_key):
    """
    Verifica se a chave da API OpenAI é válida.

    Args:
        api_key (str): Chave da API OpenAI

    Returns:
        bool: True se a chave é válida, False caso contrário
    """
    try:
        client = OpenAI(api_key=api_key)
        # Faz uma chamada simples para testar a API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Olá"}]
        )
        return True
    except Exception as e:
        return False


def setup_authentication():
    """
    Configura a autenticação com a API OpenAI.

    Returns:
        bool: True se autenticado com sucesso, False caso contrário
    """
    # Inicializar session_state para API key se ainda não existe
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = None

    # Se já tem uma chave válida, retorna True
    if st.session_state.openai_api_key:
        return True

    # Solicita a chave da API
    st.info("Para utilizar este fluxo, é necessário fornecer uma chave da API OpenAI.")
    api_key = st.text_input("🔑 OpenAI API Key", type="password")

    if api_key:
        # Verifica se a chave é válida antes de prosseguir
        if verify_api_key(api_key):
            st.session_state.openai_api_key = api_key
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("✅ API Key válida!")
            return True
        else:
            st.error("❌ API Key inválida!")

    return False


def initialize_session_state(flow_type="default", default_values=None):
    """
    Inicializa o estado da sessão com valores padrão.

    Args:
        flow_type (str): Tipo de fluxo (ex: "pdi", "plano_aula")
        default_values (dict): Valores padrão para o estado da sessão
    """
    # Configura valores comuns a todos os fluxos
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'main'

    if 'current_file' not in st.session_state:
        st.session_state.current_file = None

    if 'flow_type' not in st.session_state:
        st.session_state.flow_type = flow_type

    # Se valores padrão foram fornecidos, inicialize-os
    if default_values:
        for key, value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = value
