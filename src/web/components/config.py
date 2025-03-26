"""
Arquivo de configuração para componentes reutilizáveis.
Centraliza constantes e mapeamentos usados em diferentes fluxos.
"""

# Ordem e títulos para arquivos PDI
PDI_FILE_ORDER = [
    "final_summary.md",
    "pdi.md",
    "analise_perfil.md",
    "aggregated_research.md",
    "technical_skills.md",
    "behavioral_skills.md",
    "industry_trends.md",
    "recomendacoes.md"
]

PDI_FILE_TITLES = {
    "final_summary.md": "📝 Resumo Final",
    "pdi.md": "📋 PDI Completo",
    "analise_perfil.md": "👤 Análise de Perfil",
    "aggregated_research.md": "📊 Conteúdos Online Selecionados",
    "technical_skills.md": "💡 Competências Técnicas",
    "behavioral_skills.md": "🤝 Competências Comportamentais",
    "industry_trends.md": "🌟 Tendências da Indústria",
    "recomendacoes.md": "📚 Recomendações de Conteúdo Interno"
}

# Configurações padrão para UI
DEFAULT_PAGE_CONFIG = {
    "page_title": "Templo - Agentes Inteligentes",
    "page_icon": "🧠",
    "layout": "wide"
}

# Mapeamento de fluxos para configurações específicas
FLOW_CONFIGS = {
    "pdi": {
        "title": "✨ Templo PDI Bot",
        "description": "Crie um Plano de Desenvolvimento Individual personalizado.",
        "page_config": {
            "page_title": "Templo PDI Bot",
            "page_icon": "📚",
            "layout": "centered"
        },
        "file_order": PDI_FILE_ORDER,
        "file_titles": PDI_FILE_TITLES,
        "guide_path": "pdi_guide.md"
    },
    "plano_aula": {
        "title": "✨ Templo Plano de Aula",
        "description": "Crie um plano de aula personalizado.",
        "page_config": {
            "page_title": "Templo Plano de Aula",
            "page_icon": "📝",
            "layout": "centered"
        },
        "file_order": [
            "plano_aula.md",
            "atividades.md",
            "recursos.md"
        ],
        "file_titles": {
            "plano_aula.md": "📝 Plano de Aula",
            "atividades.md": "📋 Atividades",
            "recursos.md": "📚 Recursos"
        },
        "guide_path": "plano_aula_guide.md"
    },
    # Adicione outros fluxos aqui conforme necessário
}
