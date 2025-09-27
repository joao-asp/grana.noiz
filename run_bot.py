#!/usr/bin/env python3
"""
Script para iniciar o Bot da Caixinha
=====================================
"""

import sys
from pathlib import Path

# Adicionar src ao path do Python
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Agora pode importar o bot
if __name__ == "__main__":
    from src.bot import main
    main()