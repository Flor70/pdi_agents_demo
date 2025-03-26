import streamlit as st
from pathlib import Path
import os


def show_sidebar(generated_files, file_order, file_titles, project_root, output_dir, current_page, current_file):
    """
    Mostra a sidebar com os arquivos gerados e opções de navegação.

    Args:
        generated_files (list): Lista de objetos Path representando os arquivos gerados
        file_order (list): Lista com a ordem de exibição dos arquivos
        file_titles (dict): Dicionário mapeando nomes de arquivos para títulos de exibição
        project_root (Path): Caminho raiz do projeto
        output_dir (str): Diretório de saída
        current_page (str): Página atual
        current_file (str): Arquivo atual
    """
    with st.sidebar:
        st.title("🗂️ Navegação")

        # Botão para voltar à página inicial
        if st.button("🏠 Página Inicial"):
            st.switch_page("app.py")

        # Botões de navegação podem ser personalizados por fluxo
        navigation_buttons = {
            "pdi": [
                ("📚 Guia", "main", str(project_root / 'src' /
                 'assistants' / 'docs' / 'pdi_guide.md')),
                ("💬 Consultor Bot", "chat", None),
                ("🧙‍♂️ Mestre dos Magos", "mestre_dos_magos", None),
                ("📊 Visualização", "pdi_tracker", None),
                ("📱 LinkedIn Post", "linkedin", None)
            ],
            # Outros fluxos podem ter botões diferentes
            "default": [
                ("📚 Guia", "main", str(project_root /
                 'src' / 'assistants' / 'docs' / 'guide.md')),
                ("💬 Consultor Bot", "chat", None)
            ]
        }

        # Determina qual conjunto de botões mostrar, com fallback para default
        flow_type = st.session_state.get('flow_type', 'default')
        buttons = navigation_buttons.get(
            flow_type, navigation_buttons['default'])

        for label, page, file in buttons:
            if st.button(label):
                st.session_state.current_page = page
                if file:
                    st.session_state.current_file = file
                st.rerun()

        st.divider()

        # Lista de documentos
        st.subheader("📑 Documentos Gerados")
        if generated_files:
            generated_files_dict = {f.name: f for f in generated_files}
            for filename in file_order:
                if filename in generated_files_dict:
                    file = generated_files_dict[filename]
                    display_name = file_titles.get(filename, filename)

                    if st.button(f"{display_name}"):
                        st.session_state.current_file = str(file)
                        st.session_state.current_page = 'main'
                        st.rerun()
        else:
            st.info("Nenhum documento gerado ainda.")


def get_generated_files(output_dir):
    """
    Obtém a lista de arquivos gerados no diretório de saída.

    Args:
        output_dir (str): Diretório de saída

    Returns:
        list: Lista de objetos Path representando os arquivos gerados
    """
    output_path = Path(output_dir)
    if not output_path.exists():
        # Tenta encontrar um caminho alternativo
        project_root = Path(output_dir).parent.parent
        alt_output_dir = project_root / "output"
        if alt_output_dir.exists():
            output_path = alt_output_dir
        else:
            return []

    return list(output_path.glob("*.md"))
