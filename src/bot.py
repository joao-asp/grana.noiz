#!/usr/bin/env python3
"""
Bot do Telegram para Caixinha Coletiva
======================================

Este bot ajuda coletivos a gerenciar contribuições mensais de forma organizada.
Funcionalidades: registrar pagamentos, consultar dívidas, cobrança automática.
"""

import logging
from datetime import datetime
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from . import config
from .utils import db

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /start - Dá boas-vindas e explica como usar o bot.
    """
    user = update.effective_user
    
    # Verificar se o usuário já é membro
    membro = db.buscar_membro_por_telegram_id(user.id)
    
    if not membro:
        # Adicionar novo membro automaticamente
        nome = user.first_name or user.username or "Sem nome"
        if db.adicionar_membro(nome, user.id):
            mensagem_cadastro = f"✅ Oi {nome}! Te cadastrei automaticamente na caixinha.\n\n"
        else:
            mensagem_cadastro = "❌ Houve um problema ao te cadastrar. Fale com um admin.\n\n"
    else:
        mensagem_cadastro = f"✅ Oi {membro[1]}! Você já está cadastrado(a).\n\n"
    
    # Verificar se é admin para mostrar comandos extras
    comandos_admin = ""
    if user.id in config.ADMINS:
        comandos_admin = f"""
🔧 **Comandos de administrador:**

/status - Ver quem pagou no mês atual
/divida_manual <id> <mes> <valor> - Adicionar dívida manual"""
    
    mensagem = f"""{mensagem_cadastro}🎯 **Bot da Caixinha Coletiva**

Este bot te ajuda a acompanhar suas contribuições mensais para a caixinha do coletivo.

📋 **Comandos disponíveis:**

/pagar - Marcar que você pagou a caixinha do mês atual
/divida - Ver quanto você deve (meses não pagos)
/paguei <mes> - Marcar pagamento de um mês específico (ex: /paguei 2025-01){comandos_admin}

💰 **Valor mensal:** R$ {config.VALOR_CONTRIBUICAO:.2f}

❓ **Dúvidas?** Fale com algum admin do coletivo!

---
💚 Este bot foi feito com amor para fortalecer nossa organização coletiva."""

    await update.message.reply_text(mensagem)

async def pagar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /pagar - Marca pagamento do mês atual.
    """
    user = update.effective_user
    mes_atual = db.buscar_mes_atual()
    
    # Verificar se o usuário é membro
    membro = db.buscar_membro_por_telegram_id(user.id)
    if not membro:
        await update.message.reply_text(
            "❌ Você não está cadastrado(a). Use /start primeiro!"
        )
        return
    
    # Tentar marcar o pagamento
    if db.marcar_pagamento(user.id, mes_atual):
        mes_formatado = datetime.strptime(mes_atual, "%Y-%m").strftime("%B/%Y")
        await update.message.reply_text(
            f"✅ **Pagamento confirmado!**\n\n"
            f"📅 Mês: {mes_formatado}\n"
            f"💰 Valor: R$ {config.VALOR_CONTRIBUICAO:.2f}\n\n"
            f"Obrigado(a) por contribuir com nosso coletivo! 💚"
        )
    else:
        await update.message.reply_text(
            f"❌ Não foi possível registrar seu pagamento.\n\n"
            f"Pode ser que:\n"
            f"• Você já marcou como pago este mês\n"
            f"• Ainda não foi criada a cobrança para {mes_atual}\n\n"
            f"Fale com um admin se o problema persistir."
        )

async def divida(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /divida - Mostra dívidas pendentes do usuário.
    """
    user = update.effective_user
    
    # Verificar se o usuário é membro
    membro = db.buscar_membro_por_telegram_id(user.id)
    if not membro:
        await update.message.reply_text(
            "❌ Você não está cadastrado(a). Use /start primeiro!"
        )
        return
    
    # Buscar dívidas
    dividas = db.buscar_dividas(user.id)
    
    if not dividas:
        await update.message.reply_text(
            "🎉 **Parabéns!** Você está em dia com a caixinha!\n\n"
            "💚 Obrigado(a) por manter nossa organização forte!"
        )
        return
    
    # Formatar lista de dívidas
    total = sum(valor for _, valor in dividas)
    lista_dividas = []
    
    for mes, valor in dividas:
        mes_formatado = datetime.strptime(mes, "%Y-%m").strftime("%b/%Y")
        lista_dividas.append(f"• {mes_formatado}: R$ {valor:.2f}")
    
    mensagem = f"📋 **Suas pendências:**\n\n"
    mensagem += "\n".join(lista_dividas)
    mensagem += f"\n\n💰 **Total devido:** R$ {total:.2f}"
    mensagem += f"\n\n💡 Use /pagar para marcar o mês atual ou /paguei <mes> para meses específicos."
    
    await update.message.reply_text(mensagem)

async def paguei_mes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /paguei <mes> - Marca pagamento de um mês específico.
    """
    user = update.effective_user
    
    # Verificar se foi fornecido o mês
    if not context.args:
        await update.message.reply_text(
            "❌ **Formato incorreto!**\n\n"
            "Use: /paguei YYYY-MM\n"
            "Exemplo: /paguei 2025-01"
        )
        return
    
    mes = context.args[0]
    
    # Validar formato do mês
    try:
        datetime.strptime(mes, "%Y-%m")
    except ValueError:
        await update.message.reply_text(
            "❌ **Formato de mês inválido!**\n\n"
            "Use o formato: YYYY-MM\n"
            "Exemplo: /paguei 2025-01"
        )
        return
    
    # Verificar se o usuário é membro
    membro = db.buscar_membro_por_telegram_id(user.id)
    if not membro:
        await update.message.reply_text(
            "❌ Você não está cadastrado(a). Use /start primeiro!"
        )
        return
    
    # Tentar marcar o pagamento
    if db.marcar_pagamento(user.id, mes):
        mes_formatado = datetime.strptime(mes, "%Y-%m").strftime("%B/%Y")
        await update.message.reply_text(
            f"✅ **Pagamento confirmado!**\n\n"
            f"📅 Mês: {mes_formatado}\n"
            f"💰 Valor: R$ {config.VALOR_CONTRIBUICAO:.2f}\n\n"
            f"Obrigado(a) por contribuir! 💚"
        )
    else:
        await update.message.reply_text(
            f"❌ Não foi possível registrar o pagamento para {mes}.\n\n"
            f"Pode ser que:\n"
            f"• Você já marcou como pago este mês\n"
            f"• Este mês não existe na cobrança\n\n"
            f"Fale com um admin se precisar de ajuda."
        )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /status - Mostra status de pagamentos do mês (só admins).
    """
    user = update.effective_user
    
    # Verificar se é admin
    if user.id not in config.ADMINS:
        await update.message.reply_text(
            "❌ Este comando é só para administradores."
        )
        return
    
    mes_atual = db.buscar_mes_atual()
    pagamentos = db.buscar_pagamentos_mes_atual(mes_atual)
    
    if not pagamentos:
        await update.message.reply_text(
            f"📋 Ainda não há cobranças criadas para {mes_atual}.\n\n"
            f"As cobranças são criadas automaticamente todo dia 1º."
        )
        return
    
    # Separar quem pagou e quem não pagou
    pagos = [nome for nome, quitado in pagamentos if quitado]
    nao_pagos = [nome for nome, quitado in pagamentos if not quitado]
    
    mes_formatado = datetime.strptime(mes_atual, "%Y-%m").strftime("%B/%Y")
    
    mensagem = f"📊 **Status - {mes_formatado}**\n\n"
    
    if pagos:
        mensagem += f"✅ **Já pagaram ({len(pagos)}):**\n"
        for nome in pagos:
            mensagem += f"• {nome}\n"
        mensagem += "\n"
    
    if nao_pagos:
        mensagem += f"⏳ **Pendentes ({len(nao_pagos)}):**\n"
        for nome in nao_pagos:
            mensagem += f"• {nome}\n"
        mensagem += "\n"
    
    total_arrecadado = len(pagos) * config.VALOR_CONTRIBUICAO
    total_esperado = len(pagamentos) * config.VALOR_CONTRIBUICAO
    
    mensagem += f"💰 **Arrecadado:** R$ {total_arrecadado:.2f} / R$ {total_esperado:.2f}"
    
    await update.message.reply_text(mensagem)

async def cobranca_automatica(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Função executada automaticamente todo dia 1º para criar cobranças
    e enviar lembretes aos membros.
    """
    mes_atual = db.buscar_mes_atual()
    
    # Criar cobranças para o mês
    cobranças_criadas = db.criar_cobranca_mensal(mes_atual)
    logger.info(f"Criadas {cobranças_criadas} cobranças para {mes_atual}")
    
    # Enviar mensagens para todos os membros
    membros = db.buscar_todos_membros()
    
    for membro_id, nome, telegram_id in membros:
        try:
            # Buscar dívidas do membro
            dividas = db.buscar_dividas(telegram_id)
            
            if not dividas:
                continue  # Membro está em dia
            
            # Separar dívida do mês atual e meses anteriores
            divida_atual = 0
            dividas_anteriores = []
            
            for mes, valor in dividas:
                if mes == mes_atual:
                    divida_atual = valor
                else:
                    dividas_anteriores.append((mes, valor))
            
            # Montar mensagem
            mes_formatado = datetime.strptime(mes_atual, "%Y-%m").strftime("%B/%Y")
            
            mensagem = f"💰 **Lembrete da Caixinha - {mes_formatado}**\n\n"
            mensagem += f"Oi {nome}! 👋\n\n"
            
            if divida_atual > 0:
                mensagem += f"📅 **Contribuição deste mês:** R$ {divida_atual:.2f}\n\n"
            
            if dividas_anteriores:
                total_anterior = sum(valor for _, valor in dividas_anteriores)
                mensagem += f"⚠️ **Meses em atraso:** R$ {total_anterior:.2f}\n"
                
                for mes, valor in dividas_anteriores:
                    mes_fmt = datetime.strptime(mes, "%Y-%m").strftime("%b/%Y")
                    mensagem += f"• {mes_fmt}: R$ {valor:.2f}\n"
                mensagem += "\n"
            
            total_devido = sum(valor for _, valor in dividas)
            mensagem += f"💳 **Total pendente:** R$ {total_devido:.2f}\n\n"
            mensagem += f"Use /pagar para marcar o pagamento atual ou /divida para ver detalhes.\n\n"
            mensagem += f"💚 Sua contribuição fortalece nosso coletivo!"
            
            # Enviar mensagem
            await context.bot.send_message(
                chat_id=telegram_id,
                text=mensagem
            )
            
        except Exception as e:
            logger.error(f"Erro ao enviar cobrança para {nome} ({telegram_id}): {e}")

async def divida_manual(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Comando /divida_manual <telegram_id> <mes> <valor> - Adiciona dívida manual (só admins).
    """
    user = update.effective_user
    
    # Verificar se é admin
    if user.id not in config.ADMINS:
        await update.message.reply_text(
            "❌ Este comando é só para administradores."
        )
        return
    
    # Verificar argumentos
    if len(context.args) != 3:
        await update.message.reply_text(
            "❌ **Formato incorreto!**\n\n"
            "Use: /divida_manual <telegram_id> <mes> <valor>\n"
            "Exemplo: /divida_manual 123456789 2024-12 50.0"
        )
        return
    
    try:
        telegram_id = int(context.args[0])
        mes = context.args[1]
        valor = float(context.args[2])
    except ValueError:
        await update.message.reply_text(
            "❌ **Formato inválido!**\n\n"
            "- telegram_id deve ser um número\n"
            "- mes deve estar no formato YYYY-MM\n"
            "- valor deve ser um número (use . para decimais)"
        )
        return
    
    # Validar formato do mês
    try:
        datetime.strptime(mes, "%Y-%m")
    except ValueError:
        await update.message.reply_text(
            "❌ **Formato de mês inválido!**\n\n"
            "Use o formato: YYYY-MM\n"
            "Exemplo: 2024-12"
        )
        return
    
    # Verificar se o membro existe
    membro = db.buscar_membro_por_telegram_id(telegram_id)
    if not membro:
        await update.message.reply_text(
            f"❌ **Membro não encontrado!**\n\n"
            f"ID {telegram_id} não está cadastrado.\n"
            f"Use /start primeiro ou cadastre manualmente."
        )
        return
    
    # Adicionar a dívida
    if db.adicionar_divida_manual(telegram_id, mes, valor):
        mes_formatado = datetime.strptime(mes, "%Y-%m").strftime("%B/%Y")
        await update.message.reply_text(
            f"✅ **Dívida adicionada!**\n\n"
            f"👤 Membro: {membro[1]}\n"
            f"📅 Mês: {mes_formatado}\n"
            f"💰 Valor: R$ {valor:.2f}\n\n"
            f"A dívida foi registrada como pendente."
        )
    else:
        await update.message.reply_text(
            f"❌ **Erro ao adicionar dívida!**\n\n"
            f"Pode ser que já existe uma cobrança para {membro[1]} em {mes}.\n"
            f"Use o painel administrativo para verificar."
        )

def main():
    """
    Função principal que inicializa o bot.
    """
    # Verificar se o token foi configurado
    if (config.TELEGRAM_BOT_TOKEN == "SEU_TOKEN_AQUI" or 
        not config.TELEGRAM_BOT_TOKEN or 
        config.TELEGRAM_BOT_TOKEN.strip() == ""):
        print("❌ ERRO: Configure o token do bot no arquivo config.py!")
        print("   1. Converse com @BotFather no Telegram")
        print("   2. Crie um novo bot com /newbot")
        print("   3. Copie o token e cole em config.py")
        return
    
    # Inicializar banco de dados
    db.init_db()
    print("✅ Banco de dados inicializado")
    
    # Criar aplicação do bot
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # Registrar comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pagar", pagar))
    application.add_handler(CommandHandler("divida", divida))
    application.add_handler(CommandHandler("paguei", paguei_mes))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("divida_manual", divida_manual))
    
    # Configurar agendador para cobrança automática
    scheduler = AsyncIOScheduler()
    
    # Todo dia 10 às 9h da manhã
    scheduler.add_job(
        cobranca_automatica,
        trigger=CronTrigger(day=config.COBRANCA_DIA, hour=config.COBRANCA_HORA, minute=config.COBRANCA_MINUTO),
        args=[application],
        id='cobranca_mensal',
        replace_existing=True
    )
    
    # Iniciar bot
    print("🤖 Bot da Caixinha iniciado!")
    print("   Pressione Ctrl+C para parar")
    
    async def run_bot():
        """Função async para executar o bot com agendador."""
        try:
            # Inicializar aplicação
            await application.initialize()
            await application.start()
            
            # Iniciar agendador
            scheduler.start()
            print("✅ Agendador de cobrança automática ativado")
            
            # Iniciar polling
            await application.updater.start_polling()
            
            # Manter rodando
            await asyncio.Event().wait()
            
        except KeyboardInterrupt:
            print("\n👋 Bot parado pelo usuário")
        finally:
            # Cleanup
            scheduler.shutdown(wait=False)
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
    
    # Executar o bot
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n👋 Bot finalizado")

if __name__ == '__main__':
    main()