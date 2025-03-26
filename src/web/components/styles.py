import streamlit as st


def load_css():
    """Carrega os estilos CSS comuns para todas as páginas."""
    st.markdown("""
    <style>
        .big-button {
            display: inline-block;
            padding: 20px;
            background-color: #4CAF50;
            color: white;
            text-align: center;
            text-decoration: none;
            font-size: 20px;
            margin: 10px;
            border-radius: 12px;
            width: 100%;
            height: 200px;
            transition: all 0.3s;
            cursor: pointer;
            box-shadow: 0 9px #999;
        }
        
        .big-button:hover {
            background-color: #3e8e41;
            box-shadow: 0 5px #666;
            transform: translateY(4px);
        }
        
        .big-button:active {
            background-color: #3e8e41;
            box-shadow: 0 2px #666;
            transform: translateY(8px);
        }
        
        .big-button-icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        
        .big-button-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
        }
        
        .placeholder-text {
            font-style: italic;
            margin-top: 10px;
        }
        
        h1, h3 {
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
