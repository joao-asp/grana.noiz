#!/usr/bin/env python3
"""
Bot do Telegram para Caixinha Coletiva
======================================

Funcionalidades:
    * cadastro/vínculo do membro (inclusive legado, via RA);
    * registro de pagamentos com auditoria assíncrona;
    * consulta de dívidas e status;
    * cobrança automática mensal apenas para bolsistas ativos.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, List, Optional, Sequence

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.helpers import escape_markdown
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from . import config
from .utils import db

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

MESES_PT = (
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
)


# ---------------------------------------------------------------------------
# Helpers de apresentação
# ---------------------------------------------------------------------------


def _md(texto: Any) -> str:
    """Escapa texto dinâmico para Markdown v1 do Telegram."""
    return escape_markdown(str(texto), version=1)


def _mes_formatado(mes: str) -> str:
    try:
        data = datetime.strptime(mes, "%Y-%m")
        return f"{MESES_PT[data.month - 1]}/{data.year}"
    except (TypeError, ValueError):
        return mes


def _brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _nome_membro(membro: Any) -> str:
    if membro is None:
        return "membro"
    return _md(membro["nome"])


def _limitar_linhas(linhas: Sequence[str], limite: int = 15) -> str:
    if not linhas:
        return ""
    exibidas = list(linhas[:limite])
    if len(linhas) > limite:
        exibidas.append(f"… e mais {len(linhas) - limite}")
    return "\n".join(exibidas)


async def _responder(
    update: Update,
    texto: str,
    parse_mode: Optional[str] = "Markdown",
) -> None:
    if update.message is None:
        return
    await update.message.reply_text(texto, parse_mode=parse_mode)


async def _notificar_admins(
    context: ContextTypes.DEFAULT_TYPE, texto: str
) -> None:
    """Avisa todos os admins; falhas individuais não derrubam o fluxo."""
    for admin_id in config.ADMINS:
        try:
            await context.bot.send_message(
                chat_id=admin_id, text=texto, parse_mode="Markdown"
            )
        except Exception as exc:  # rede/Telegram: apenas registra
            logger.warning("Não foi possível notificar admin %s: %s", admin_id, exc)


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start - boas-vindas, cadastro e instrução de vínculo legado."""
    user = update.effective_user
    if user is None or update.message is None:
        return

    membro = db.buscar_perfil_membro(user.id)

    if membro is None:
        nome = " ".join(
            parte for parte in (user.first_name, user.last_name) if parte
        ) or user.username or "Sem nome"
        if db.adicionar_membro(nome, user.id):
            mensagem_cadastro = (
                f"✅ Oi {_md(nome)}! Te cadastrei automaticamente na caixinha.\n"
                f"Se você já era bolsista da ITCP, use /vincular <RA> para "
                f"trazer seu histórico.\n\n"
            )
        else:
            mensagem_cadastro = (
                "❌ Não consegui te cadastrar. Fale com um admin.\n\n"
            )
    else:
        mensagem_cadastro = f"✅ Oi {_nome_membro(membro)}! Você já está cadastrado(a).\n"
        if membro["ra"]:
            mensagem_cadastro += f"🔗 RA vinculado: {_md(membro['ra'])}\n"
        else:
            mensagem_cadastro += (
                "🔗 Seu cadastro ainda não está vinculado ao histórico legado. "
                "Use /vincular <RA>.\n"
            )
        mensagem_cadastro += "\n"

    comandos_admin = ""
    if user.id in config.ADMINS:
        comandos_admin = (
            "\n🔧 *Comandos de administrador:*\n\n"
            "/status - Balanço de ativos, ex-bolsistas e auditoria\n"
            "/divida_manual <telegram_id> <mes> <valor> - Adicionar dívida manual\n"
        )

    mensagem = f"""{mensagem_cadastro}🎯 *Bot da Caixinha Coletiva*

Este bot te ajuda a acompanhar suas contribuições mensais para a caixinha do coletivo.

📋 *Comandos disponíveis:*

/pagar - Solicitar baixa da cota do mês atual (passa por auditoria)
/divida - Ver suas pendências
/paguei <mes> - Solicitar baixa de um mês específico (ex: /paguei 2025-01)
/vincular <RA> - Vincular seu Telegram ao cadastro legado da ITCP
{comandos_admin}
💰 *Valor mensal:* {_brl(config.VALOR_CONTRIBUICAO)}

🌐 *Painel web:* {_md(config.WEB_PUBLIC_URL)}

❓ *Dúvidas?* Fale com algum admin do coletivo!

---
💚 Este bot foi feito com amor para fortalecer nossa organização coletiva."""

    await _responder(update, mensagem)


async def vincular(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /vincular <RA> - liga o Telegram ao cadastro legado pelo RA."""
    user = update.effective_user
    if user is None or update.message is None:
        return

    if not context.args:
        await _responder(
            update,
            "❌ *Informe seu RA.*\n\n"
            "Use: /vincular <RA>\n"
            "Exemplo: /vincular 248340",
        )
        return

    ra = context.args[0]
    ok, motivo, id_membro = db.vincular_por_ra(ra, user.id)

    if not ok:
        mensagens = {
            "ra_nao_encontrado": (
                "❌ *RA não encontrado no cadastro legado.*\n\n"
                "Confira se digitou corretamente ou fale com um admin."
            ),
            "ra_ja_vinculado": (
                "❌ *Este RA já está vinculado a outra conta do Telegram.*\n\n"
                "Fale com um admin para resolver."
            ),
            "telegram_em_outro_cadastro": (
                "❌ *Seu Telegram já está ligado a outro cadastro da caixinha.*\n\n"
                "Fale com um admin para unificar os registros."
            ),
            "erro_banco": (
                "❌ Erro temporário ao vincular. Tente novamente em instantes."
            ),
        }
        await _responder(update, mensagens.get(motivo, "❌ Não foi possível vincular."))
        return

    membro = db.buscar_membro_por_id(id_membro) if id_membro else None
    if membro is None:
        await _responder(update, "✅ Vínculo realizado.")
        return

    dividas = db.buscar_dividas_por_membro_id(int(membro["id"]))
    total = sum(valor for _, valor in dividas)
    tipo = "ex-bolsista (histórico)" if membro["ex_bolsista"] else "bolsista ativo"

    if motivo == "ja_vinculado":
        titulo = "ℹ️ *Este Telegram já estava vinculado.*"
    else:
        titulo = "✅ *Vínculo realizado com sucesso!*"

    mensagem = (
        f"{titulo}\n\n"
        f"👤 {_nome_membro(membro)}\n"
        f"🎓 RA: {_md(membro['ra'])}\n"
        f"🏷️ Vínculo: {_md(tipo)}\n"
        f"📚 Status: {_md(membro['status_vinculo'] or 'ATIVO')}\n"
    )
    if dividas:
        mensagem += (
            f"\n⏳ Pendências em aberto: {len(dividas)} "
            f"({_brl(total)})\nUse /divida para ver os meses."
        )
    else:
        mensagem += "\n🎉 Você não tem pendências em aberto."

    await _responder(update, mensagem)


async def pagar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /pagar - solicita baixa do mês atual para auditoria."""
    user = update.effective_user
    if user is None or update.message is None:
        return

    membro = db.buscar_perfil_membro(user.id)
    if membro is None:
        await _responder(update, "❌ Você não está cadastrado(a). Use /start primeiro!")
        return

    if membro["ex_bolsista"]:
        await _responder(
            update,
            "🎓 Você consta como *ex-bolsista* e não recebe novas cobranças.\n\n"
            "Se quiser acertar alguma pendência histórica, use /divida e "
            "/paguei <mes>.",
        )
        return

    mes_atual = db.buscar_mes_atual()
    ok, motivo = db.registrar_solicitacao_pagamento(user.id, mes_atual)

    if ok:
        mes_fmt = _mes_formatado(mes_atual)
        await _responder(
            update,
            f"🕵️ *Solicitação registrada!*\n\n"
            f"📅 Mês: {mes_fmt}\n"
            f"💰 Valor: {_brl(config.VALOR_CONTRIBUICAO)}\n\n"
            f"Seu pagamento ficou com status *aguardando auditoria*. "
            f"Um admin vai conferir o extrato e confirmar. 💚",
        )
        await _notificar_admins(
            context,
            f"🔔 *Nova solicitação de auditoria*\n\n"
            f"👤 {_nome_membro(membro)}"
            f"{' (RA ' + _md(membro['ra']) + ')' if membro['ra'] else ''}\n"
            f"📅 {mes_fmt}\n"
            f"💰 {_brl(config.VALOR_CONTRIBUICAO)}\n\n"
            f"Confirme no painel admin (`make admin`) após conferir o extrato.",
        )
        return

    mensagens = {
        "ja_pago": "✅ Este mês já está confirmado como pago. Obrigado(a)! 💚",
        "ja_aguardando": (
            "⏳ Sua solicitação para este mês já está *aguardando auditoria*. "
            "Aguarde a conferência de um admin."
        ),
        "mes_invalido": "❌ Mês inválido.",
        "erro_banco": "❌ Erro temporário ao registrar. Tente novamente.",
        "nao_cadastrado": "❌ Você não está cadastrado(a). Use /start primeiro!",
    }
    await _responder(update, mensagens.get(motivo, "❌ Não foi possível registrar."))


async def divida(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /divida - mostra pendências e solicitações em auditoria."""
    user = update.effective_user
    if user is None or update.message is None:
        return

    membro = db.buscar_perfil_membro(user.id)
    if membro is None:
        await _responder(update, "❌ Você não está cadastrado(a). Use /start primeiro!")
        return

    dividas = db.buscar_dividas(user.id)
    em_auditoria = db.buscar_dividas_em_auditoria(user.id)

    if not dividas and not em_auditoria:
        await _responder(
            update,
            "🎉 *Parabéns!* Você está em dia com a caixinha!\n\n"
            "💚 Obrigado(a) por manter nossa organização forte!",
        )
        return

    mensagem = "📋 *Suas pendências:*\n"
    if membro["ex_bolsista"]:
        mensagem += (
            "\n🎓 Você consta como *ex-bolsista*. As pendências abaixo são "
            "históricas e não geram novas cobranças automáticas.\n"
        )
    mensagem += "\n"

    if dividas:
        total = sum(valor for _, valor in dividas)
        linhas = [
            f"• {_mes_formatado(mes)}: {_brl(valor)}" for mes, valor in dividas
        ]
        mensagem += "⏳ *Em aberto:*\n" + _limitar_linhas(linhas, 20)
        mensagem += f"\n\n💰 *Total em aberto:* {_brl(total)}\n"

    if em_auditoria:
        linhas = [
            f"• {_mes_formatado(mes)}: {_brl(valor)}"
            for mes, valor in em_auditoria
        ]
        mensagem += (
            "\n🔎 *Aguardando auditoria:*\n"
            + _limitar_linhas(linhas, 20)
            + "\n"
        )

    mensagem += (
        "\n💡 Use /paguei <mes> para solicitar baixa de um mês específico "
        "ou /pagar para o mês atual."
    )
    await _responder(update, mensagem)


async def paguei_mes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /paguei <mes> - solicita baixa de um mês específico."""
    user = update.effective_user
    if user is None or update.message is None:
        return

    if not context.args:
        await _responder(
            update,
            "❌ *Formato incorreto!*\n\nUse: /paguei YYYY-MM\nExemplo: /paguei 2025-01",
        )
        return

    mes = context.args[0]
    try:
        datetime.strptime(mes, "%Y-%m")
    except ValueError:
        await _responder(
            update,
            "❌ *Formato de mês inválido!*\n\n"
            "Use o formato: YYYY-MM\nExemplo: /paguei 2025-01",
        )
        return

    membro = db.buscar_perfil_membro(user.id)
    if membro is None:
        await _responder(update, "❌ Você não está cadastrado(a). Use /start primeiro!")
        return

    ok, motivo = db.registrar_solicitacao_pagamento(user.id, mes)
    if ok:
        await _responder(
            update,
            f"🕵️ *Solicitação registrada!*\n\n"
            f"📅 Mês: {_mes_formatado(mes)}\n"
            f"💰 Valor: {_brl(config.VALOR_CONTRIBUICAO)}\n\n"
            f"Status: *aguardando auditoria*. Um admin vai conferir e confirmar. 💚",
        )
        await _notificar_admins(
            context,
            f"🔔 *Nova solicitação de auditoria*\n\n"
            f"👤 {_nome_membro(membro)}"
            f"{' (RA ' + _md(membro['ra']) + ')' if membro['ra'] else ''}\n"
            f"📅 {_mes_formatado(mes)}\n"
            f"💰 {_brl(config.VALOR_CONTRIBUICAO)}\n\n"
            f"Confirme no painel admin (`make admin`) após conferir o extrato.",
        )
        return

    mensagens = {
        "ja_pago": "✅ Este mês já está confirmado como pago. Obrigado(a)! 💚",
        "ja_aguardando": (
            "⏳ Sua solicitação para este mês já está *aguardando auditoria*."
        ),
        "mes_invalido": "❌ Mês inválido.",
        "erro_banco": "❌ Erro temporário ao registrar. Tente novamente.",
        "nao_cadastrado": "❌ Você não está cadastrado(a). Use /start primeiro!",
    }
    await _responder(update, mensagens.get(motivo, "❌ Não foi possível registrar."))


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /status - balanço separado de ativos, ex-bolsistas e auditoria."""
    user = update.effective_user
    if user is None or update.message is None:
        return

    if user.id not in config.ADMINS:
        await _responder(update, "❌ Este comando é só para administradores.")
        return

    mes_atual = db.buscar_mes_atual()
    resumo = db.obter_resumo_financeiro()
    resumo_mes = db.obter_resumo_mes(mes_atual)
    aguardando = db.listar_pagamentos_aguardando_auditoria()
    status_mes = db.buscar_status_mes(mes_atual)

    ativos = resumo["ativos"]
    ex = resumo["ex_bolsistas"]
    ativos_mes = resumo_mes["ativos"]
    ex_mes = resumo_mes["ex_bolsistas"]

    mensagem = f"📊 *Status da Caixinha — {_mes_formatado(mes_atual)}*\n\n"

    mensagem += (
        f"👥 *Bolsistas ativos:* {int(ativos['membros'])}\n"
        f"✅ Pagos no mês: {int(ativos_mes['pagos'])}\n"
        f"⏳ Pendentes no mês: {int(ativos_mes['pendentes'])}\n"
        f"🔎 Em auditoria no mês: {int(ativos_mes['em_auditoria'])}\n"
        f"💰 Arrecadado no mês: {_brl(ativos_mes['valor_pago'])}\n"
        f"📉 Saldo devedor histórico: {_brl(ativos['saldo_devedor'])}\n\n"
    )

    mensagem += (
        f"🎓 *Ex-bolsistas:* {int(ex['membros'])}\n"
        f"✅ Cotas pagas (histórico): {int(ex['pagos'])} "
        f"({_brl(ex['valor_pago'])})\n"
        f"⚠️ Pendências históricas: {int(ex['pendentes'])} "
        f"({_brl(ex['saldo_devedor'])})\n\n"
    )

    if aguardando:
        linhas = [
            f"• {_md(row['nome'])} — {_mes_formatado(row['mes'])} — "
            f"{_brl(float(row['valor_pago']))}"
            for row in aguardando
        ]
        mensagem += (
            f"🕵️ *Aguardando auditoria ({len(aguardando)}):*\n"
            + _limitar_linhas(linhas, 15)
            + "\n\n"
        )
    else:
        mensagem += "🕵️ Nenhum pagamento aguardando auditoria.\n\n"

    # Detalhe do mês (ativos e ex-bolsistas que têm lançamento no mês)
    if status_mes:
        pagos = [
            _md(r["nome"]) for r in status_mes
            if r["status_pagamento"] == db.STATUS_PAGO
        ]
        pendentes = [
            _md(r["nome"]) for r in status_mes
            if r["status_pagamento"] == db.STATUS_PENDENTE
        ]
        if pagos:
            mensagem += (
                f"✅ *Pagaram em {_mes_formatado(mes_atual)}:*\n"
                + _limitar_linhas(pagos, 12)
                + "\n\n"
            )
        if pendentes:
            mensagem += (
                f"⏳ *Pendentes em {_mes_formatado(mes_atual)}:*\n"
                + _limitar_linhas(pendentes, 12)
                + "\n"
            )
    else:
        mensagem += (
            f"ℹ️ Ainda não há cobranças criadas para {_mes_formatado(mes_atual)}.\n"
            f"As cobranças são criadas automaticamente todo dia "
            f"{config.COBRANCA_DIA}."
        )

    await _responder(update, mensagem)


async def cobranca_automatica(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Job mensal: cria cobranças apenas para ativos e envia lembretes.

    Ex-bolsistas (``ex_bolsista = 1``) nunca recebem novas cobranças.
    """
    mes_atual = db.buscar_mes_atual()

    cobrancas_criadas = db.criar_cobranca_mensal(mes_atual)
    logger.info("Criadas %s cobranças para %s", cobrancas_criadas, mes_atual)

    membros = db.buscar_membros_para_cobranca()
    for membro in membros:
        telegram_id = membro["telegram_id"]
        if telegram_id is None:
            continue
        try:
            # buscar_dividas ignora solicitações em auditoria (não cobra de novo)
            dividas = db.buscar_dividas(telegram_id)
            if not dividas:
                continue

            divida_atual = 0.0
            anteriores: List[Any] = []
            for mes, valor in dividas:
                if mes == mes_atual:
                    divida_atual = valor
                else:
                    anteriores.append((mes, valor))

            mensagem = (
                f"💰 *Lembrete da Caixinha - {_mes_formatado(mes_atual)}*\n\n"
                f"Oi {_md(membro['nome'])}! 👋\n\n"
            )
            if divida_atual > 0:
                mensagem += (
                    f"📅 *Contribuição deste mês:* {_brl(divida_atual)}\n\n"
                )
            if anteriores:
                total_anterior = sum(valor for _, valor in anteriores)
                mensagem += (
                    f"⚠️ *Meses em atraso:* {_brl(total_anterior)}\n"
                )
                for mes, valor in anteriores:
                    mensagem += f"• {_mes_formatado(mes)}: {_brl(valor)}\n"
                mensagem += "\n"

            total_devido = sum(valor for _, valor in dividas)
            mensagem += (
                f"💳 *Total pendente:* {_brl(total_devido)}\n\n"
                f"Use /pagar para solicitar a baixa do mês atual ou /divida "
                f"para ver detalhes.\n\n"
                f"💚 Sua contribuição fortalece nosso coletivo!"
            )

            await context.bot.send_message(
                chat_id=telegram_id,
                text=mensagem,
                parse_mode="Markdown",
            )
        except Exception as exc:
            logger.error(
                "Erro ao enviar cobrança para %s (%s): %s",
                membro["nome"], telegram_id, exc,
            )


async def divida_manual(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /divida_manual <telegram_id> <mes> <valor> - dívida manual (admin)."""
    user = update.effective_user
    if user is None or update.message is None:
        return

    if user.id not in config.ADMINS:
        await _responder(update, "❌ Este comando é só para administradores.")
        return

    if len(context.args) != 3:
        await _responder(
            update,
            "❌ *Formato incorreto!*\n\n"
            "Use: /divida_manual <telegram_id> <mes> <valor>\n"
            "Exemplo: /divida_manual 123456789 2024-12 5.0",
        )
        return

    try:
        telegram_id = int(context.args[0])
        mes = context.args[1]
        valor = float(context.args[2])
    except ValueError:
        await _responder(
            update,
            "❌ *Formato inválido!*\n\n"
            "- telegram_id deve ser um número\n"
            "- mes deve estar no formato YYYY-MM\n"
            "- valor deve ser um número (use . para decimais)",
        )
        return

    try:
        datetime.strptime(mes, "%Y-%m")
    except ValueError:
        await _responder(
            update,
            "❌ *Formato de mês inválido!*\n\n"
            "Use o formato: YYYY-MM\nExemplo: 2024-12",
        )
        return

    membro = db.buscar_membro_por_telegram_id(telegram_id)
    if membro is None:
        await _responder(
            update,
            f"❌ *Membro não encontrado!*\n\n"
            f"ID {telegram_id} não está cadastrado.\n"
            f"Use /vincular ou cadastre pelo painel administrativo.",
        )
        return

    if db.adicionar_divida_manual(telegram_id, mes, valor):
        await _responder(
            update,
            f"✅ *Dívida adicionada!*\n\n"
            f"👤 Membro: {_nome_membro(membro)}\n"
            f"📅 Mês: {_mes_formatado(mes)}\n"
            f"💰 Valor: {_brl(valor)}\n\n"
            f"A dívida foi registrada como pendente.",
        )
    else:
        await _responder(
            update,
            f"❌ *Erro ao adicionar dívida!*\n\n"
            f"Pode ser que já exista uma cobrança para {_nome_membro(membro)} "
            f"em {_mes_formatado(mes)}.",
        )


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------


def main() -> None:
    """Inicializa banco, handlers e agendador."""
    if (
        config.TELEGRAM_BOT_TOKEN == "SEU_TOKEN_AQUI"
        or not config.TELEGRAM_BOT_TOKEN
        or config.TELEGRAM_BOT_TOKEN.strip() == ""
    ):
        print("❌ ERRO: Configure o token do bot no arquivo .env!")
        print("   1. Converse com @BotFather no Telegram")
        print("   2. Crie um novo bot com /newbot")
        print("   3. Copie o token para TELEGRAM_BOT_TOKEN no .env")
        return

    db.init_db()
    print("✅ Banco de dados inicializado")

    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pagar", pagar))
    application.add_handler(CommandHandler("divida", divida))
    application.add_handler(CommandHandler("paguei", paguei_mes))
    application.add_handler(CommandHandler("vincular", vincular))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("divida_manual", divida_manual))

    scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)
    scheduler.add_job(
        cobranca_automatica,
        trigger=CronTrigger(
            day=config.COBRANCA_DIA,
            hour=config.COBRANCA_HORA,
            minute=config.COBRANCA_MINUTO,
            timezone=config.TIMEZONE,
        ),
        args=[application],
        id="cobranca_mensal",
        replace_existing=True,
    )

    print("🤖 Bot da Caixinha iniciado!")
    print("   Pressione Ctrl+C para parar")

    async def run_bot() -> None:
        try:
            await application.initialize()
            await application.start()
            scheduler.start()
            print("✅ Agendador de cobrança automática ativado")
            await application.updater.start_polling()
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print("\n👋 Bot parado pelo usuário")
        finally:
            try:
                if scheduler.running:
                    scheduler.shutdown(wait=False)
            except Exception:
                pass
            if application.updater is not None:
                await application.updater.stop()
            await application.stop()
            await application.shutdown()

    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n👋 Bot finalizado")


if __name__ == "__main__":
    main()
