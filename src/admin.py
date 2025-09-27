#!/usr/bin/env python3
"""
Script auxiliar para gerenciar o banco de dados da caixinha.
Use este script para tarefas administrativas básicas.
"""

import sqlite3
import sys
from datetime import datetime
import config
from utils import db

def mostrar_menu():
    """Mostra o menu de opções."""
    print("\n🗃️  Gerenciador do Banco da Caixinha")
    print("="*40)
    print("1. Ver todos os membros")
    print("2. Adicionar novo membro")
    print("3. Ver dívidas de um membro")
    print("4. Ver status do mês atual")
    print("5. Criar cobrança para o mês atual")
    print("6. Adicionar dívida manual")
    print("7. Backup do banco de dados")
    print("8. Sair")
    print("="*40)

def ver_membros():
    """Lista todos os membros cadastrados."""
    membros = db.buscar_todos_membros()
    
    if not membros:
        print("❌ Nenhum membro cadastrado.")
        return
    
    print(f"\n👥 Membros cadastrados ({len(membros)}):")
    print("-" * 50)
    for id_membro, nome, telegram_id in membros:
        print(f"ID: {id_membro:3d} | {nome:20s} | Telegram: {telegram_id}")

def adicionar_membro():
    """Adiciona um novo membro manualmente."""
    print("\n➕ Adicionar novo membro")
    
    nome = input("Nome do membro: ").strip()
    if not nome:
        print("❌ Nome não pode estar vazio.")
        return
    
    try:
        telegram_id = int(input("ID do Telegram: ").strip())
    except ValueError:
        print("❌ ID do Telegram deve ser um número.")
        return
    
    if db.adicionar_membro(nome, telegram_id):
        print(f"✅ Membro {nome} adicionado com sucesso!")
    else:
        print(f"❌ Erro: Membro com ID {telegram_id} já existe.")

def ver_dividas_membro():
    """Mostra dívidas de um membro específico."""
    try:
        telegram_id = int(input("\nID do Telegram do membro: ").strip())
    except ValueError:
        print("❌ ID deve ser um número.")
        return
    
    membro = db.buscar_membro_por_telegram_id(telegram_id)
    if not membro:
        print("❌ Membro não encontrado.")
        return
    
    dividas = db.buscar_dividas(telegram_id)
    
    print(f"\n💰 Dívidas de {membro[1]}:")
    print("-" * 30)
    
    if not dividas:
        print("✅ Sem dívidas! Está em dia.")
        return
    
    total = 0
    for mes, valor in dividas:
        mes_fmt = datetime.strptime(mes, "%Y-%m").strftime("%b/%Y")
        print(f"{mes_fmt}: R$ {valor:.2f}")
        total += valor
    
    print("-" * 30)
    print(f"Total: R$ {total:.2f}")

def ver_status_mes():
    """Mostra status de pagamentos do mês atual."""
    mes_atual = db.buscar_mes_atual()
    pagamentos = db.buscar_pagamentos_mes_atual(mes_atual)
    
    if not pagamentos:
        print(f"❌ Não há cobranças para {mes_atual}.")
        return
    
    mes_fmt = datetime.strptime(mes_atual, "%Y-%m").strftime("%B/%Y")
    print(f"\n📊 Status - {mes_fmt}")
    print("="*40)
    
    pagos = [(nome, quitado) for nome, quitado in pagamentos if quitado]
    nao_pagos = [(nome, quitado) for nome, quitado in pagamentos if not quitado]
    
    if pagos:
        print(f"\n✅ Já pagaram ({len(pagos)}):")
        for nome, _ in pagos:
            print(f"  • {nome}")
    
    if nao_pagos:
        print(f"\n⏳ Pendentes ({len(nao_pagos)}):")
        for nome, _ in nao_pagos:
            print(f"  • {nome}")
    
    total_arrecadado = len(pagos) * config.VALOR_CONTRIBUICAO
    total_esperado = len(pagamentos) * config.VALOR_CONTRIBUICAO
    
    print(f"\n💰 Arrecadado: R$ {total_arrecadado:.2f} / R$ {total_esperado:.2f}")

def criar_cobranca_mes():
    """Cria cobranças para o mês atual."""
    mes_atual = db.buscar_mes_atual()
    
    confirmacao = input(f"\nCriar cobranças para {mes_atual}? (s/N): ").strip().lower()
    if confirmacao != 's':
        print("❌ Operação cancelada.")
        return
    
    cobranças = db.criar_cobranca_mensal(mes_atual)
    print(f"✅ Criadas {cobranças} cobranças para {mes_atual}.")

def fazer_backup():
    """Faz backup do banco de dados."""
    from shutil import copy2
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_nome = f"caixinha_backup_{timestamp}.db"
    
    try:
        copy2(config.DB_PATH, backup_nome)
        print(f"✅ Backup criado: {backup_nome}")
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")

def adicionar_divida_manual():
    """Adiciona uma dívida manual para um membro."""
    print("\n💰 Adicionar dívida manual")
    
    # Mostrar lista de membros
    membros = db.listar_membros_simples()
    if not membros:
        print("❌ Nenhum membro cadastrado.")
        return
    
    print("\n👥 Membros disponíveis:")
    print("-" * 50)
    for i, (nome, telegram_id) in enumerate(membros, 1):
        print(f"{i:2d}. {nome:20s} (ID: {telegram_id})")
    
    print("\n📝 Você pode escolher pelo número ou digitar o ID do Telegram")
    escolha = input("Escolha o membro (número ou ID): ").strip()
    
    # Determinar o telegram_id
    try:
        if escolha.isdigit() and int(escolha) <= len(membros):
            # Escolheu pelo número
            nome_escolhido, telegram_id = membros[int(escolha) - 1]
        else:
            # Tentou digitar o ID diretamente
            telegram_id = int(escolha)
            # Verificar se o ID existe
            membro = db.buscar_membro_por_telegram_id(telegram_id)
            if not membro:
                print(f"❌ Membro com ID {telegram_id} não encontrado.")
                return
            nome_escolhido = membro[1]
    except ValueError:
        print("❌ Opção inválida.")
        return
    
    # Solicitar mês
    mes = input("\nMês da dívida (YYYY-MM, ex: 2024-12): ").strip()
    try:
        datetime.strptime(mes, "%Y-%m")
    except ValueError:
        print("❌ Formato de mês inválido. Use YYYY-MM")
        return
    
    # Solicitar valor
    try:
        valor = float(input(f"Valor da dívida (R$, ex: 50.0): R$ ").strip())
        if valor <= 0:
            print("❌ Valor deve ser positivo.")
            return
    except ValueError:
        print("❌ Valor inválido.")
        return
    
    # Confirmar
    mes_fmt = datetime.strptime(mes, "%Y-%m").strftime("%B/%Y")
    print(f"\n📋 Confirmar dados:")
    print(f"👤 Membro: {nome_escolhido}")
    print(f"📅 Mês: {mes_fmt}")
    print(f"💰 Valor: R$ {valor:.2f}")
    
    confirmacao = input("\nConfirmar adição? (s/N): ").strip().lower()
    if confirmacao != 's':
        print("❌ Operação cancelada.")
        return
    
    # Adicionar a dívida
    if db.adicionar_divida_manual(telegram_id, mes, valor):
        print(f"✅ Dívida adicionada para {nome_escolhido}!")
    else:
        print(f"❌ Erro: Já existe uma cobrança para {nome_escolhido} em {mes}.")

def main():
    """Função principal do script."""
    # Inicializar banco
    db.init_db()
    
    while True:
        mostrar_menu()
        
        try:
            opcao = input("\nEscolha uma opção (1-8): ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Saindo...")
            break
        
        if opcao == "1":
            ver_membros()
        elif opcao == "2":
            adicionar_membro()
        elif opcao == "3":
            ver_dividas_membro()
        elif opcao == "4":
            ver_status_mes()
        elif opcao == "5":
            criar_cobranca_mes()
        elif opcao == "6":
            adicionar_divida_manual()
        elif opcao == "7":
            fazer_backup()
        elif opcao == "8":
            print("👋 Até mais!")
            break
        else:
            print("❌ Opção inválida. Escolha entre 1 e 8.")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
