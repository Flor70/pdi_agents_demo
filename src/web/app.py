#!/usr/bin/env python3

# Add src to PYTHONPATH
from web.components.config import DEFAULT_PAGE_CONFIG
from web.components.flow_buttons import render_flow_grid
from web.components.styles import load_css
import streamlit as st
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


def main():
    # Configuração da página
    st.set_page_config(**DEFAULT_PAGE_CONFIG)

    # Carregar estilos CSS
    load_css()

    # Cabeçalho da página
    st.title("🧠 Templo - Agentes Inteligentes")
    st.markdown("### Escolha um fluxo para iniciar")

    # Definir os fluxos disponíveis
    flows = [
        {
            "title": "Plano de Desenvolvimento Individual",
            "icon": "📊",
            "description": "Crie um PDI personalizado baseado na sua entrevista",
            "url": "pdi_app"
        },
        {
            "title": "Feedback 360°",
            "icon": "📝",
            "description": "Em breve! Receba feedback de múltiplas perspectivas",
            "is_placeholder": True,
            "url": None
        },
        {
            "title": "Plano de Aula BOT",
            "icon": "📝",
            "description": "Fluxos e Notas de Aula",
            "url": "plano_aula"
        },
        {
            "title": "Avaliação de Competências",
            "icon": "🔍",
            "description": "Em breve! Identifique e avalie suas competências",
            "is_placeholder": True,
            "url": None
        }
    ]

    # Renderizar a grade de botões
    render_flow_grid(flows)

    # Rodapé
    st.markdown("---")
    st.markdown("Desenvolvido pelo Templo © 2024", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
