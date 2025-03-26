#!/usr/bin/env python3

# Add src to PYTHONPATH
from web.components.pdi_flow import PDIFlow
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
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
src_path = str(PROJECT_ROOT / "src")
if src_path not in sys.path:
    sys.path.append(src_path)


def main():
    """Executa o fluxo PDI."""
    flow = PDIFlow(PROJECT_ROOT)
    flow.run()


if __name__ == "__main__":
    main()
