"""
Componentes reutilizáveis para interfaces do Templo Agents.
Este módulo facilita a importação de todos os componentes.
"""

from .styles import load_css
from .sidebar import show_sidebar, get_generated_files
from .assistant_manager import initialize_assistant, show_chat_interface, upload_documents_to_assistant
from .auth import verify_api_key, setup_authentication, initialize_session_state
from .file_viewer import show_file_content, show_pdi_tracker
from .interview_flow import (
    initialize_interview_assistant,
    process_interview_completion,
    start_crew,
    show_interview_interface,
    run_crew_processing
)
from .config import (
    PDI_FILE_ORDER,
    PDI_FILE_TITLES,
    DEFAULT_PAGE_CONFIG,
    FLOW_CONFIGS
)
from .flow_buttons import render_flow_button, render_flow_grid
from .flow_base import BaseFlow
