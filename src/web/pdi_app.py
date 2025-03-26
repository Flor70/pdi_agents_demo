#!/usr/bin/env python3

# Add src to PYTHONPATH
from langchain_openai import ChatOpenAI
from core.utils import create_crew, load_config
from assistants.mestre_dos_magos_assistant import MestreDosMagosAssistant
from assistants.linkedin_assistant import LinkedInAssistant
from assistants.interview_assistant import InterviewAssistant
from assistants.pdi_assistant import PDIAssistant
import asyncio
import streamlit.components.v1 as components
import streamlit as st
import pathlib
import os
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
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
src_path = str(PROJECT_ROOT / "src")
if src_path not in sys.path:
    sys.path.append(src_path)


# Configuração da página
st.set_page_config(
    page_title="Templo PDI Agents",
    page_icon="📚",
    layout="centered"
)

# Set up base directory and file paths
CONFIG_DIR = PROJECT_ROOT / "config"
AGENTS_CONFIG = str(CONFIG_DIR / "agents.yaml")
TASKS_CONFIG = str(CONFIG_DIR / "tasks.yaml")
OUTPUT_DIR = str(PROJECT_ROOT / "output")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'interview_complete' not in st.session_state:
    st.session_state.interview_complete = False
if 'interview_data' not in st.session_state:
    st.session_state.interview_data = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = None
if 'pdi_assistant' not in st.session_state:
    st.session_state.pdi_assistant = None
if 'interview_assistant' not in st.session_state:
    st.session_state.interview_assistant = None
if 'linkedin_assistant' not in st.session_state:
    st.session_state.linkedin_assistant = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'linkedin_messages' not in st.session_state:
    st.session_state.linkedin_messages = []
if 'mestre_dos_magos_assistant' not in st.session_state:
    st.session_state.mestre_dos_magos_assistant = None
if 'mestre_dos_magos_messages' not in st.session_state:
    st.session_state.mestre_dos_magos_messages = []

# Mapeamento de nomes de arquivos para títulos em português
FILE_ORDER = [
    "final_summary.md",
    "pdi.md",
    "analise_perfil.md",
    "aggregated_research.md",
    "technical_skills.md",
    "behavioral_skills.md",
    "industry_trends.md",
    "recomendacoes.md"
]

FILE_TITLES = {
    "final_summary.md": "📝 Resumo Final",
    "pdi.md": "📋 PDI Completo",
    "analise_perfil.md": "👤 Análise de Perfil",
    "aggregated_research.md": "📊 Conteúdos Online Selecionados",
    "technical_skills.md": "💡 Competências Técnicas",
    "behavioral_skills.md": "🤝 Competências Comportamentais",
    "industry_trends.md": "🌟 Tendências da Indústria",
    "recomendacoes.md": "📚 Recomendações de Conteúdo Interno"
}


def show_sidebar(generated_files):
    """Mostra a sidebar com os arquivos gerados"""
    with st.sidebar:
        st.title("🗂️ Navegação")

        # Botão para voltar à página inicial
        if st.button("🏠 Página Inicial"):
            st.switch_page("app.py")

        # Botão para voltar ao guia
        if st.button("📚 Guia do PDI"):
            st.session_state.current_page = 'main'
            st.session_state.current_file = str(
                PROJECT_ROOT / 'src' / 'assistants' / 'docs' / 'pdi_guide.md')
            st.rerun()

        # Botão para chat
        if st.button("💬 Consultor PDI Bot"):
            st.session_state.current_page = 'chat'
            st.rerun()

        # Botão para Mestre dos Magos
        if st.button("🧙‍♂️ Mestre dos Magos"):
            st.session_state.current_page = 'mestre_dos_magos'
            st.rerun()

        # Botão para visualização do PDI
        if st.button("📊 Visualização do PDI"):
            st.session_state.current_page = 'pdi_tracker'
            st.rerun()

        # Botão para LinkedIn Post Creator
        if st.button("📱 LinkedIn Post"):
            st.session_state.current_page = 'linkedin'
            st.rerun()

        st.divider()

        # Lista de documentos
        st.subheader("📑 Documentos Gerados")
        generated_files_dict = {f.name: f for f in generated_files}
        for filename in FILE_ORDER:
            if filename in generated_files_dict:
                file = generated_files_dict[filename]
                display_name = FILE_TITLES.get(filename, filename)

                if st.button(f"{display_name}"):
                    st.session_state.current_file = str(file)
                    st.session_state.current_page = 'main'
                    st.rerun()


def show_file_content():
    """Mostra o conteúdo do arquivo atual"""
    try:
        if 'current_file' not in st.session_state or st.session_state.current_file is None:
            st.session_state.current_file = str(
                PROJECT_ROOT / 'src' / 'assistants' / 'docs' / 'pdi_guide.md')

        file_path = st.session_state.current_file
        if not os.path.exists(file_path):
            st.error(f"Arquivo não encontrado: {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            st.markdown(content)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {str(e)}")
        st.session_state.current_file = str(
            PROJECT_ROOT / 'src' / 'assistants' / 'docs' / 'pdi_guide.md')
        st.rerun()


def verify_api_key(api_key):
    """Verifica se a chave da API OpenAI é válida"""
    try:
        client = ChatOpenAI(
            api_key=api_key,
            model="gpt-4o-mini"
        )
        # Faz uma chamada simples para testar a API
        response = client.invoke("Olá")
        return True
    except Exception as e:
        st.error(f"Chave da API inválida!")
        return False


def initialize_llm():
    return ChatOpenAI(
        model="gpt-4o-2024-08-06"
    )


def initialize_session_state():
    """Inicializa o estado da sessão para a entrevista"""
    if 'interview_assistant' not in st.session_state or st.session_state.interview_assistant is None:
        st.session_state.interview_assistant = InterviewAssistant(
            st.session_state.openai_api_key)
        st.session_state.interview_assistant.initialize_assistant()
        st.session_state.messages = st.session_state.interview_assistant.messages


def show_generic_chat_interface(title, description, assistant, messages_key="chat_messages"):
    """Interface genérica de chat que pode ser usada com diferentes assistentes"""
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
            # Verifica se não está em processo de criação do PDI
            if not (hasattr(assistant, 'process_interview_completion') and "[INTERVIEW_COMPLETE]" in prompt):
                with st.spinner("Pensando..."):
                    response = asyncio.run(assistant.get_response(prompt))
            else:
                response = asyncio.run(assistant.get_response(prompt))

            # Verifica se é uma resposta de conclusão de entrevista
            if hasattr(assistant, 'process_interview_completion'):
                if assistant.process_interview_completion(response, st.session_state):
                    st.rerun()

            st.session_state[messages_key].append(
                {"role": "assistant", "content": response})
            st.write(response)


def show_interview_interface():
    """Interface do chat para entrevista"""
    show_generic_chat_interface(
        title="🎤 Entrevista PDI",
        description="""
        A seguir vamos começar uma entrevista para conhecer melhor o seu perfil.
        Por favor, responda as perguntas do nosso assistente para que possamos construir um PDI personalizado para você.
        """,
        assistant=st.session_state.interview_assistant,
        messages_key="messages"
    )


def show_chat_interface():
    """Interface do chat para consulta do PDI"""
    show_generic_chat_interface(
        title="💬 Consultor PDI Bot",
        description="""
        Olá! Sou seu consultor especializado no Plano de Desenvolvimento Individual.
        Posso responder perguntas sobre o perfil do colaborador, recomendações e plano de desenvolvimento.
        Como posso ajudar?
        """,
        assistant=st.session_state.pdi_assistant,
        messages_key="chat_messages"
    )


def show_linkedin_interface():
    """Interface do chat para criação de posts do LinkedIn"""
    if st.session_state.linkedin_assistant is None:
        st.session_state.linkedin_assistant = LinkedInAssistant(
            st.session_state.openai_api_key)
        st.session_state.linkedin_assistant.initialize_assistant()
        try:
            # Gera o post inicial automaticamente
            initial_post = st.session_state.linkedin_assistant.upload_pdi_documents(
                OUTPUT_DIR)
            if initial_post:
                st.session_state.linkedin_messages = [
                    {"role": "assistant", "content": initial_post}
                ]
        except ValueError as e:
            st.error(str(e))
            return

    st.title("📱 LinkedIn Post Creator")
    st.markdown("Este assistente criou um post do LinkedIn celebrando o início do seu PDI. Você pode pedir ajustes conforme necessário.")

    # Display chat messages
    for message in st.session_state.linkedin_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Digite sua mensagem para ajustar o post"):
        st.session_state.linkedin_messages.append(
            {"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response = asyncio.run(
                    st.session_state.linkedin_assistant.get_response(prompt))
            st.session_state.linkedin_messages.append(
                {"role": "assistant", "content": response})
            st.write(response)


def show_pdi_tracker():
    """Mostra a interface de visualização do PDI"""
    st.title("📊 Visualização do PDI")

    # Verifica se o arquivo JSON existe
    pdi_json_path = Path(OUTPUT_DIR) / 'pdi.json'
    if not pdi_json_path.exists():
        st.info(
            "Nenhum PDI disponível para visualização. Complete a entrevista primeiro.")
        return

    try:
        # Lê o arquivo JSON
        with open(pdi_json_path, 'r', encoding='utf-8') as f:
            pdi_data = f.read()

        # Caminho para o componente React compilado
        component_path = Path(PROJECT_ROOT) / "frontend" / \
            "dist" / "pdi-tracker.js"
        if not component_path.exists():
            st.error(
                "Componente de visualização não encontrado. Execute 'npm run build' no diretório frontend.")
            return

        # Lê o conteúdo do arquivo JS
        with open(component_path, 'r', encoding='utf-8') as f:
            js_content = f.read()

        # Renderiza o componente React
        components.html(
            f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>PDI Tracker</title>
                <style>
                    body {{
                        margin: 0;
                        padding: 16px;
                        font-family: system-ui, -apple-system, sans-serif;
                    }}
                </style>
            </head>
            <body>
                <div id="pdi-tracker-root"></div>
                <script>{js_content}</script>
                <script>
                    const pdiConfig = {pdi_data};
                    window.renderPDITracker(
                        document.getElementById('pdi-tracker-root'),
                        pdiConfig,
                        600
                    );
                </script>
            </body>
            </html>
            """,
            height=600,
            scrolling=True
        )

    except Exception as e:
        st.error(f"Erro ao carregar a visualização do PDI: {str(e)}")


def show_main_page():
    """Página principal do aplicativo"""
    st.title("✨ Templo PDI Bot")
    st.divider()

    # API Key input if not already set
    if not st.session_state.openai_api_key:
        st.info(
            "Para utilizar o PDI Bot, é necessário fornecer uma chave da API OpenAI.")
        api_key = st.text_input("🔑 OpenAI API Key", type="password")
        if api_key:
            # Verifica se a chave é válida antes de prosseguir
            if verify_api_key(api_key):
                st.session_state.openai_api_key = api_key
                os.environ["OPENAI_API_KEY"] = api_key
                initialize_session_state()
                st.success("✅ API Key válida!")
                st.rerun()
        st.stop()

    # Garante que o assistente está inicializado
    if 'interview_assistant' not in st.session_state or st.session_state.interview_assistant is None:
        initialize_session_state()
        st.rerun()

    if st.session_state.interview_complete:
        output_dir = Path(OUTPUT_DIR)
        # Lista todos os arquivos .md no diretório
        generated_files = list(output_dir.glob("*.md"))

        # Mostrar a sidebar
        show_sidebar(generated_files)

        # Inicializa o PDI Assistant se necessário
        if st.session_state.current_page == 'chat' and (
            'pdi_assistant' not in st.session_state or
            st.session_state.pdi_assistant is None
        ):
            st.session_state.pdi_assistant = PDIAssistant(
                st.session_state.openai_api_key)
            st.session_state.pdi_assistant.initialize_assistant()
            st.session_state.pdi_assistant.upload_pdi_documents(output_dir)
            st.session_state.pdi_assistant.create_thread()

        # Mostrar a interface apropriada
        if st.session_state.current_page == 'chat':
            show_chat_interface()
        elif st.session_state.current_page == 'pdi_tracker':
            show_pdi_tracker()
        elif st.session_state.current_page == 'linkedin':
            show_linkedin_interface()
        elif st.session_state.current_page == 'mestre_dos_magos':
            show_mestre_dos_magos_interface()
        else:
            # Se é a primeira vez após completar a entrevista, mostrar o guia
            if 'current_file' not in st.session_state:
                st.session_state.current_file = str(
                    PROJECT_ROOT / 'src' / 'assistants' / 'docs' / 'pdi_guide.md')

            # Mostrar o conteúdo do arquivo atual
            show_file_content()
    else:
        # Initialize LLM and messages if not exists
        initialize_session_state()

        # Show interview interface
        show_interview_interface()


def show_mestre_dos_magos_interface():
    """Interface do chat para o Mestre dos Magos"""
    if st.session_state.mestre_dos_magos_assistant is None:
        st.session_state.mestre_dos_magos_assistant = MestreDosMagosAssistant(
            st.session_state.openai_api_key)
        st.session_state.mestre_dos_magos_assistant.initialize_assistant()
        st.session_state.mestre_dos_magos_assistant.create_thread()
        st.session_state.mestre_dos_magos_messages = []

    show_generic_chat_interface(
        title="🧙‍♂️ Mestre dos Magos",
        description="Este assistente é um mestre dos magos e pode te ajudar a cumprir sua jornada de PDI com sabedoria.",
        assistant=st.session_state.mestre_dos_magos_assistant,
        messages_key="mestre_dos_magos_messages"
    )


def main():
    show_main_page()


if __name__ == "__main__":
    main()
