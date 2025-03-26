import streamlit as st


def render_flow_button(title, icon, description, url, is_placeholder=False):
    """
    Renderiza um botão para um fluxo específico.

    Args:
        title (str): Título do fluxo
        icon (str): Emoji para o ícone do fluxo
        description (str): Descrição curta do fluxo
        url (str): URL para o fluxo (ou None se for placeholder)
        is_placeholder (bool): Se é um botão de placeholder
    """
    if not is_placeholder and url:
        html = f"""
        <a href="{url}" target="_self" style="text-decoration:none">
            <div class="big-button">
                <div class="big-button-content">
                    <div class="big-button-icon">{icon}</div>
                    <div>{title}</div>
                    <div style="font-size: 14px; margin-top: 10px;">{description}</div>
                </div>
            </div>
        </a>
        """
    else:
        html = f"""
        <div class="big-button">
            <div class="big-button-content">
                <div class="big-button-icon">{icon}</div>
                <div>{title}</div>
                <div class="placeholder-text">{description}</div>
            </div>
        </div>
        """

    st.markdown(html, unsafe_allow_html=True)


def render_flow_grid(flows):
    """
    Renderiza uma grade de botões para os fluxos disponíveis.

    Args:
        flows (list): Lista de dicionários com configurações dos fluxos
    """
    # Organizar os fluxos em linhas de 2 botões
    rows = [flows[i:i+2] for i in range(0, len(flows), 2)]

    for row in rows:
        cols = st.columns(2)
        for i, flow in enumerate(row):
            with cols[i]:
                render_flow_button(
                    title=flow.get("title", "Fluxo"),
                    icon=flow.get("icon", "📋"),
                    description=flow.get("description", ""),
                    url=flow.get("url"),
                    is_placeholder=flow.get("is_placeholder", False)
                )
