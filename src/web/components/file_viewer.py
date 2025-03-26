import streamlit as st
import os
from pathlib import Path


def show_file_content(file_path=None, default_file=None):
    """
    Mostra o conteúdo de um arquivo markdown.

    Args:
        file_path (str, optional): Caminho do arquivo a ser exibido
        default_file (str, optional): Arquivo padrão se file_path não existir
    """
    try:
        # Se não há file_path, use o padrão
        if file_path is None:
            if default_file and os.path.exists(default_file):
                file_path = default_file
            else:
                st.warning("Nenhum arquivo selecionado para visualização.")
                return

        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            st.error(f"Arquivo não encontrado: {file_path}")
            if default_file and os.path.exists(default_file):
                file_path = default_file
                st.info(
                    f"Mostrando arquivo padrão: {os.path.basename(default_file)}")
            else:
                return

        # Ler e exibir o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            st.markdown(content)

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {str(e)}")
        if default_file and os.path.exists(default_file):
            try:
                with open(default_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    st.markdown(content)
            except:
                st.error(f"Também não foi possível ler o arquivo padrão.")


def show_pdi_tracker(output_dir, height=600):
    """
    Mostra a interface de visualização do PDI com o componente React.

    Args:
        output_dir (str): Diretório de saída onde está o arquivo pdi.json
        height (int): Altura do componente em pixels
    """
    st.title("📊 Visualização do PDI")

    # Verifica se o arquivo JSON existe
    pdi_json_path = Path(output_dir) / 'pdi.json'
    if not pdi_json_path.exists():
        # Tenta caminho alternativo
        project_root = Path(output_dir).parent.parent
        alt_json_path = project_root / "output" / 'pdi.json'
        if alt_json_path.exists():
            pdi_json_path = alt_json_path
        else:
            st.info(
                "Nenhum PDI disponível para visualização. Complete a entrevista primeiro.")
            return

    try:
        # Lê o arquivo JSON
        with open(pdi_json_path, 'r', encoding='utf-8') as f:
            pdi_data = f.read()

        # Caminho para o componente React compilado
        project_root = Path(output_dir).parent.parent
        component_path = project_root / "frontend" / "dist" / "pdi-tracker.js"
        if not component_path.exists():
            st.error(
                "Componente de visualização não encontrado. Execute 'npm run build' no diretório frontend.")
            return

        # Lê o conteúdo do arquivo JS
        with open(component_path, 'r', encoding='utf-8') as f:
            js_content = f.read()

        # Renderiza o componente React
        st.components.v1.html(
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
                        {height}
                    );
                </script>
            </body>
            </html>
            """,
            height=height,
            scrolling=True
        )

    except Exception as e:
        st.error(f"Erro ao carregar a visualização do PDI: {str(e)}")
