#!/usr/bin/env python3
"""
Interface web do grana.noiz
===========================

Servidor HTTP baseado apenas na biblioteca padrão (http.server) + SQLite.
Serve o painel mobile-first em ``web/`` e uma API JSON consumida por ele.

Rotas principais:
    GET  /                      painel SPA
    GET  /api/resumo            visão geral pública
    GET  /api/membros           lista de membros (campos sensíveis só p/ admin)
    GET  /api/membros/por-ra/RA  área do membro
    GET  /api/caixa             livro caixa e série mensal
    POST /api/solicitar-pagamento
    POST /api/assistente
    *    /api/admin/*          exigem X-Admin-Token

Execução:
    python -m src.web
"""

from __future__ import annotations

import csv
import hashlib
import hmac
import io
import json
import logging
import mimetypes
import re
import secrets
import sqlite3
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from http.cookies import CookieError, SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:  # python -m src.web
    from . import config
    from .utils import db
except ImportError:  # python web.py (com src/ no sys.path)
    import config  # type: ignore
    from utils import db  # type: ignore

logger = logging.getLogger("grana.web")

WEB_DIR = Path(config.BASE_DIR) / "web"
MESES_PT = (
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
)
MAX_BODY = 1_000_000


# ---------------------------------------------------------------------------
# Helpers de domínio
# ---------------------------------------------------------------------------


def _brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _mes_label(mes: str) -> str:
    try:
        data = datetime.strptime(mes, "%Y-%m")
        return f"{MESES_PT[data.month - 1]}/{data.year}"
    except (TypeError, ValueError):
        return mes


def _serializar_detalhe_publico(detalhe: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimiza o retorno da área do membro: sem Telegram e sem observações
    internas da gestão.
    """
    saida = dict(detalhe)
    saida.pop("telegram_id", None)
    saida["telegram_vinculado"] = bool(detalhe.get("telegram_id"))
    saida["pagamentos"] = [
        {k: v for k, v in pagamento.items() if k != "observacoes"}
        for pagamento in detalhe.get("pagamentos", [])
    ]
    return saida


def _notificar_admins(texto: str) -> None:
    """
    Envia aviso ao Telegram em background (sem bloquear a request HTTP).

    Funciona apenas se TELEGRAM_BOT_TOKEN e ADMINS estiverem configurados.
    """
    token = (config.TELEGRAM_BOT_TOKEN or "").strip()
    if not token or token == "SEU_TOKEN_AQUI" or not config.ADMINS:
        return

    def worker() -> None:
        for admin_id in config.ADMINS:
            try:
                dados = urllib.parse.urlencode(
                    {"chat_id": admin_id, "text": texto}
                ).encode("utf-8")
                req = urllib.request.Request(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    data=dados,
                )
                urllib.request.urlopen(req, timeout=5).close()
            except Exception as exc:  # rede/Telegram: não derruba o request
                logger.warning("Falha ao notificar admin %s: %s", admin_id, exc)

    threading.Thread(target=worker, daemon=True).start()


def responder_assistente(mensagem: str, ra: Optional[str] = None) -> Dict[str, Any]:
    """
    Assistente determinístico: responde perguntas frequentes consultando o banco.

    Não usa LLM nem serviço externo — apenas regras e os dados reais da caixinha.
    """
    texto = db.normalizar_nome(mensagem)
    mes = db.buscar_mes_atual()
    possui_pessoal = any(
        chave in texto
        for chave in (
            "quanto eu devo", "quanto devo", "quanto estou devendo",
            "estou devendo", "minha divida", "minhas pendencia", "meu status",
            "minha situacao", "meus pagamentos",
        )
    )

    if possui_pessoal:
        if not ra:
            return {
                "resposta": (
                    "Para eu consultar suas pendências, informe seu RA no campo "
                    "\"Meu espaço\" (ou digite: RA 248340)."
                )
            }
        detalhe = db.obter_detalhe_membro_por_ra(ra)
        if not detalhe:
            return {"resposta": f"Não encontrei o RA {ra} no cadastro da caixinha."}
        pendentes = [
            p for p in detalhe["pagamentos"]
            if p["status_pagamento"] == db.STATUS_PENDENTE
        ]
        em_auditoria = [
            p for p in detalhe["pagamentos"]
            if p["status_pagamento"] == db.STATUS_AGUARDANDO_AUDITORIA
        ]
        if not pendentes and not em_auditoria:
            resposta = f"{detalhe['nome']}, você está em dia. 🎉"
        else:
            linhas = [
                f"• {_mes_label(p['mes'])}: {_brl(float(p['valor_pago']))}"
                for p in pendentes[:12]
            ]
            resposta = (
                f"{detalhe['nome']}, você tem {len(pendentes)} cota(s) em aberto "
                f"({_brl(detalhe.get('saldo_devedor', 0))})."
            )
            if linhas:
                resposta += "\n" + "\n".join(linhas)
            if em_auditoria:
                resposta += (
                    f"\n\nHá também {len(em_auditoria)} solicitação(ões) "
                    "aguardando auditoria."
                )
        return {"resposta": resposta}

    if any(
        k in texto
        for k in ("quem nao pagou", "pendentes", "atrasad", "inadimpl", "adesao")
    ):
        status_mes = db.buscar_status_mes(mes)
        ativos = [r for r in status_mes if not int(r["ex_bolsista"])]
        confirmadas = sum(
            1 for r in ativos if r["status_pagamento"] == db.STATUS_PAGO
        )
        em_auditoria = sum(
            1 for r in ativos
            if r["status_pagamento"] == db.STATUS_AGUARDANDO_AUDITORIA
        )
        em_acompanhamento = max(0, len(ativos) - confirmadas - em_auditoria)
        return {
            "resposta": (
                f"Em {_mes_label(mes)}, {confirmadas} de {len(ativos)} cotas "
                f"ativas já foram confirmadas.\n"
                f"{em_auditoria} estão em auditoria e {em_acompanhamento} "
                "seguem em acompanhamento pela gestão.\n\n"
                "A gestão conversa individualmente com cada pessoa; não "
                "expomos nomes ou dívidas aqui. 💚"
            )
        }

    if any(k in texto for k in ("saldo", "caixa", "arrecad", "quanto tem")):
        caixa = db.obter_resumo_caixa(mes)
        return {
            "resposta": (
                f"Arrecadação histórica de cotas: {_brl(caixa['total_pago'])}.\n"
                f"Despesas registradas: {_brl(caixa['total_despesas'])}.\n"
                f"Saldo do livro caixa: {_brl(caixa['saldo'])}.\n"
                f"No mês de {_mes_label(mes)}: {_brl(caixa['pago_mes'])} arrecadados."
            )
        }

    if any(k in texto for k in ("ex-bolsista", "ex bolsista", "historico")):
        resumo = db.obter_resumo_financeiro()["ex_bolsistas"]
        return {
            "resposta": (
                f"Ex-bolsistas: {int(resumo['membros'])} cadastro(s), "
                f"{int(resumo['pagos'])} cota(s) paga(s) "
                f"({_brl(resumo['valor_pago'])}) e "
                f"{int(resumo['pendentes'])} pendência(s) histórica(s) "
                f"({_brl(resumo['saldo_devedor'])})."
            )
        }

    if any(k in texto for k in ("pix", "como pagar", "pagar")):
        chave = config.PIX_CHAVE or "chave Pix ainda não configurada"
        return {
            "resposta": (
                f"Chave Pix oficial: {chave}.\n"
                f"A cota mensal é {_brl(config.VALOR_CONTRIBUICAO)}. "
                "Depois de pagar, use \"Avisar pagamento\" no seu espaço para "
                "entrar na fila de auditoria."
            )
        }

    if any(k in texto for k in ("proxima", "cobranca", "vencimento", "dia")):
        return {
            "resposta": (
                f"As cobranças automáticas são criadas todo dia "
                f"{config.COBRANCA_DIA} do mês. O valor da cota é "
                f"{_brl(config.VALOR_CONTRIBUICAO)}."
            )
        }

    if any(k in texto for k in ("ajuda", "oi", "ola", "bom dia", "boa tarde")):
        return {
            "resposta": (
                "Posso responder sobre:\n"
                "• quanto você deve (informe seu RA)\n"
                "• quantas cotas estão confirmadas no mês\n"
                "• saldo e arrecadação do caixa\n"
                "• pendências de ex-bolsistas\n"
                "• Pix e próxima cobrança"
            )
        }

    resumo = db.obter_resumo_financeiro()
    caixa = db.obter_resumo_caixa(mes)
    return {
        "resposta": (
            f"Resumo de {_mes_label(mes)}: {int(resumo['ativos']['membros'])} "
            f"ativos, {int(resumo['ativos']['pendentes'])} cota(s) pendente(s) "
            f"no histórico ativo e saldo de {_brl(caixa['saldo'])} no livro caixa.\n\n"
            "Pergunte sobre dívida, pendentes, saldo, Pix ou ex-bolsistas."
        )
    }


# ---------------------------------------------------------------------------
# Autenticação do painel /admin
# ---------------------------------------------------------------------------

SESSION_COOKIE = "grana_admin_session"
PBKDF2_ITERACOES = 260_000
MAX_TENTATIVAS_LOGIN = 5
JANELA_TENTATIVAS_SEGUNDOS = 300

_SESSOES: Dict[str, Dict[str, Any]] = {}
_SESSOES_LOCK = threading.Lock()
_TENTATIVAS: Dict[str, List[float]] = {}
_TENTATIVAS_LOCK = threading.Lock()


def gerar_hash_senha(senha: str, iteracoes: int = PBKDF2_ITERACOES) -> str:
    """Gera hash PBKDF2-SHA256 para WEB_ADMIN_PASSWORD_HASH."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt, iteracoes
    )
    return f"pbkdf2_sha256${iteracoes}${salt.hex()}${digest.hex()}"


def _verificar_hash_senha(senha: str, armazenado: str) -> bool:
    try:
        algoritmo, iteracoes_txt, salt_hex, digest_hex = armazenado.split("$", 3)
        if algoritmo != "pbkdf2_sha256":
            return False
        iteracoes = int(iteracoes_txt)
        salt = bytes.fromhex(salt_hex)
        esperado = bytes.fromhex(digest_hex)
    except (ValueError, TypeError):
        return False

    calculado = hashlib.pbkdf2_hmac(
        "sha256", senha.encode("utf-8"), salt, iteracoes
    )
    return hmac.compare_digest(calculado, esperado)


def _login_configurado() -> bool:
    return bool(
        (config.WEB_ADMIN_PASSWORD or "").strip()
        or (config.WEB_ADMIN_PASSWORD_HASH or "").strip()
    )


def _admin_habilitado() -> bool:
    return bool(_login_configurado() or (config.WEB_ADMIN_TOKEN or "").strip())


def _credenciais_validas(usuario: str, senha: str) -> bool:
    if not _login_configurado():
        return False
    if not hmac.compare_digest(usuario, config.WEB_ADMIN_USER):
        return False

    hash_armazenado = (config.WEB_ADMIN_PASSWORD_HASH or "").strip()
    if hash_armazenado:
        return _verificar_hash_senha(senha, hash_armazenado)
    return hmac.compare_digest(senha, config.WEB_ADMIN_PASSWORD)


def _limpar_sessoes_expiradas() -> None:
    agora = time.time()
    expiradas = [token for token, dados in _SESSOES.items() if dados["expira"] <= agora]
    for token in expiradas:
        _SESSOES.pop(token, None)


def _criar_sessao(usuario: str) -> str:
    token = secrets.token_urlsafe(32)
    expira = time.time() + (config.WEB_SESSION_TTL_HOURS * 3600)
    with _SESSOES_LOCK:
        _limpar_sessoes_expiradas()
        _SESSOES[token] = {"usuario": usuario, "expira": expira}
    return token


def _obter_sessao(token: str) -> Optional[str]:
    if not token:
        return None
    with _SESSOES_LOCK:
        _limpar_sessoes_expiradas()
        dados = _SESSOES.get(token)
        if not dados:
            return None
        return str(dados["usuario"])


def _remover_sessao(token: str) -> None:
    with _SESSOES_LOCK:
        _SESSOES.pop(token, None)


def _cookie_sessao(token: str) -> str:
    max_age = int(config.WEB_SESSION_TTL_HOURS * 3600)
    partes = [
        f"{SESSION_COOKIE}={token}",
        "HttpOnly",
        "SameSite=Strict",
        "Path=/",
        f"Max-Age={max_age}",
    ]
    if config.WEB_COOKIE_SECURE:
        partes.append("Secure")
    return "; ".join(partes)


def _cookie_expirado() -> str:
    partes = [
        f"{SESSION_COOKIE}=",
        "HttpOnly",
        "SameSite=Strict",
        "Path=/",
        "Max-Age=0",
    ]
    if config.WEB_COOKIE_SECURE:
        partes.append("Secure")
    return "; ".join(partes)


def _login_bloqueado(ip: str) -> bool:
    agora = time.time()
    with _TENTATIVAS_LOCK:
        tentativas = [
            t for t in _TENTATIVAS.get(ip, [])
            if agora - t < JANELA_TENTATIVAS_SEGUNDOS
        ]
        _TENTATIVAS[ip] = tentativas
        return len(tentativas) >= MAX_TENTATIVAS_LOGIN


def _registrar_falha_login(ip: str) -> None:
    agora = time.time()
    with _TENTATIVAS_LOCK:
        tentativas = [
            t for t in _TENTATIVAS.get(ip, [])
            if agora - t < JANELA_TENTATIVAS_SEGUNDOS
        ]
        tentativas.append(agora)
        _TENTATIVAS[ip] = tentativas


def _limpar_falhas_login(ip: str) -> None:
    with _TENTATIVAS_LOCK:
        _TENTATIVAS.pop(ip, None)


def montar_mensagem_cobranca(
    nome: str, mes: str, dividas: List[Tuple[str, float]]
) -> str:
    """Mensagem humana de lembrete usada no disparo manual pelo painel."""
    atual = 0.0
    anteriores: List[Tuple[str, float]] = []
    for mes_divida, valor in dividas:
        if mes_divida == mes:
            atual = float(valor)
        else:
            anteriores.append((mes_divida, float(valor)))

    if atual > 0:
        mensagem = (
            f"Oi {nome}! 👋\n\n"
            f"Passando para lembrar da caixinha de {_mes_label(mes)}.\n"
            f"Cota deste mês: {_brl(atual)}\n"
        )
    else:
        mensagem = (
            f"Oi {nome}! 👋\n\n"
            "Passando para lembrar das cotas em aberto com a caixinha.\n"
        )
    if anteriores:
        total_anterior = sum(valor for _, valor in anteriores)
        mensagem += f"Pendências anteriores: {_brl(total_anterior)}\n"
        for mes_divida, valor in anteriores[:6]:
            mensagem += f"• {_mes_label(mes_divida)}: {_brl(valor)}\n"
    total = sum(float(valor) for _, valor in dividas)
    mensagem += (
        f"\nTotal em acompanhamento: {_brl(total)}\n\n"
        f"Se já pagou, use /paguei {mes} no bot ou avise a gestão. "
        "Se estiver atravessando um aperto, fale com a gente na roda. 💚"
    )
    return mensagem


def _enviar_telegram(chat_id: int, texto: str) -> bool:
    token = (config.TELEGRAM_BOT_TOKEN or "").strip()
    if not token or token == "SEU_TOKEN_AQUI":
        return False
    try:
        dados = urllib.parse.urlencode(
            {"chat_id": chat_id, "text": texto}
        ).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=dados,
        )
        urllib.request.urlopen(req, timeout=8).close()
        return True
    except Exception as exc:
        logger.warning("Falha ao enviar Telegram para %s: %s", chat_id, exc)
        return False


def _disparar_cobrancas_telegram(mes: str) -> Dict[str, int]:
    """Envia lembretes para ativos com Telegram e alguma pendência."""
    membros = db.buscar_membros_para_cobranca()
    alvos: List[Tuple[int, str]] = []
    sem_pendencia = 0
    for membro in membros:
        telegram_id = membro["telegram_id"]
        if telegram_id is None:
            continue
        dividas = db.buscar_dividas(int(telegram_id))
        if not dividas:
            sem_pendencia += 1
            continue
        alvos.append(
            (int(telegram_id), montar_mensagem_cobranca(membro["nome"], mes, dividas))
        )

    enviados = 0
    erros = 0
    if alvos:
        with ThreadPoolExecutor(max_workers=8) as executor:
            resultados = list(
                executor.map(lambda alvo: _enviar_telegram(alvo[0], alvo[1]), alvos)
            )
        enviados = sum(1 for ok in resultados if ok)
        erros = len(resultados) - enviados

    return {
        "considerados": len(membros),
        "enviados": enviados,
        "sem_pendencia": sem_pendencia,
        "erros": erros,
    }


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------


class WebHandler(BaseHTTPRequestHandler):
    server_version = "grana.noiz/1.0"
    protocol_version = "HTTP/1.1"

    # -- logging ---------------------------------------------------------
    def log_message(self, fmt: str, *args: Any) -> None:
        logger.info("%s - %s", self.address_string(), fmt % args)

    # -- entrypoints -----------------------------------------------------
    def do_GET(self) -> None:
        self._responded = False
        self._dispatch("GET")

    def do_POST(self) -> None:
        self._responded = False
        self._dispatch("POST")

    def do_DELETE(self) -> None:
        self._responded = False
        self._dispatch("DELETE")

    def do_OPTIONS(self) -> None:
        self._responded = True
        self.send_response(204)
        self._security_headers()
        self.send_header("Allow", "GET, POST, DELETE, OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()

    # -- dispatch --------------------------------------------------------
    def _dispatch(self, method: str) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        query = urllib.parse.parse_qs(parsed.query)

        try:
            if method in ("POST", "DELETE") and not self._check_origin():
                return
            if path.startswith("/api/"):
                self._handle_api(method, path.rstrip("/") or "/", query)
            else:
                if method != "GET":
                    self._send_json(405, {"erro": "Método não permitido"})
                else:
                    self._serve_static(path)
        except sqlite3.Error as exc:
            logger.exception("Erro de banco na web: %s", exc)
            self._send_json(500, {"erro": "Erro de banco de dados"})
        except Exception as exc:  # nunca derrubar o servidor por uma request
            logger.exception("Erro inesperado na web: %s", exc)
            self._send_json(500, {"erro": "Erro interno"})

    # -- respostas -------------------------------------------------------
    def _security_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; script-src 'self'; "
            "font-src 'self'; connect-src 'self'; base-uri 'none'; "
            "form-action 'self'",
        )

    def _send_json(
        self,
        status: int,
        dados: Dict[str, Any],
        cabecalhos: Optional[Dict[str, str]] = None,
    ) -> None:
        if self._responded:
            return
        self._responded = True
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(corpo)))
        for chave, valor in (cabecalhos or {}).items():
            self.send_header(chave, valor)
        self._security_headers()
        self.end_headers()
        self.wfile.write(corpo)

    def _send_csv(self, nome_arquivo: str, conteudo: str) -> None:
        if self._responded:
            return
        self._responded = True
        corpo = conteudo.encode("utf-8-sig")
        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header(
            "Content-Disposition", f'attachment; filename="{nome_arquivo}"'
        )
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(corpo)))
        self._security_headers()
        self.end_headers()
        self.wfile.write(corpo)

    def _serve_static(self, path: str) -> None:
        if self._responded:
            return
        admin_path = path.rstrip("/") == "/admin"
        if path in ("", "/"):
            path = "/index.html"
        if path == "/favicon.ico":
            self._responded = True
            self.send_response(204)
            self._security_headers()
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        relativo = path.lstrip("/")
        alvo = (WEB_DIR / relativo).resolve()
        try:
            alvo.relative_to(WEB_DIR.resolve())
        except ValueError:
            self._send_json(403, {"erro": "Acesso negado"})
            return

        if not alvo.is_file():
            # SPA: rotas sem extensão caem no index (hash routing não exige,
            # mas mantém links diretos funcionando).
            if "." not in Path(relativo).name:
                alvo = WEB_DIR / "index.html"
            else:
                self._send_json(404, {"erro": "Arquivo não encontrado"})
                return

        if not alvo.is_file():
            self._send_json(404, {"erro": "Arquivo não encontrado"})
            return

        mime = mimetypes.guess_type(str(alvo))[0] or "application/octet-stream"
        if mime.startswith("text/") or mime in ("application/javascript",):
            mime += "; charset=utf-8"

        corpo = alvo.read_bytes()
        self._responded = True
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Content-Length", str(len(corpo)))
        if admin_path:
            self.send_header("X-Robots-Tag", "noindex, nofollow")
        self._security_headers()
        self.end_headers()
        self.wfile.write(corpo)

    # -- auth ------------------------------------------------------------
    def _token_cookie(self) -> str:
        cabecalho = self.headers.get("Cookie", "")
        if not cabecalho:
            return ""
        cookie = SimpleCookie()
        try:
            cookie.load(cabecalho)
        except CookieError:
            return ""
        morsel = cookie.get(SESSION_COOKIE)
        return morsel.value if morsel else ""

    def _admin_atual(self) -> Optional[str]:
        usuario = _obter_sessao(self._token_cookie())
        if usuario:
            return usuario
        # Token opcional para scripts/curl, sem uso no navegador.
        token = (config.WEB_ADMIN_TOKEN or "").strip()
        if token:
            enviado = self.headers.get("X-Admin-Token", "")
            if hmac.compare_digest(enviado, token):
                return config.WEB_ADMIN_USER or "api"
        return None

    def _is_admin(self) -> bool:
        return self._admin_atual() is not None

    def _require_admin(self) -> bool:
        if not _admin_habilitado():
            self._send_json(
                503,
                {
                    "erro": (
                        "Painel admin desabilitado. Configure "
                        "WEB_ADMIN_PASSWORD ou WEB_ADMIN_PASSWORD_HASH."
                    )
                },
            )
            return False
        if not self._is_admin():
            self._send_json(401, {"erro": "Faça login para continuar."})
            return False
        return True

    def _check_origin(self) -> bool:
        origem = self.headers.get("Origin")
        if not origem:
            return True
        host = self.headers.get("Host", "")
        try:
            netloc = urllib.parse.urlparse(origem).netloc
        except ValueError:
            netloc = ""
        if netloc != host:
            self._send_json(403, {"erro": "Origem não permitida."})
            return False
        return True

    # -- body ------------------------------------------------------------
    def _read_json(self) -> Optional[Dict[str, Any]]:
        # Exige JSON: evita CSRF via formulário cross-origin (text/plain).
        content_type = (
            self.headers.get("Content-Type", "").split(";")[0].strip().lower()
        )
        if content_type != "application/json":
            self._send_json(
                415, {"erro": "Content-Type deve ser application/json"}
            )
            return None
        try:
            tamanho = int(self.headers.get("Content-Length", "0") or 0)
        except ValueError:
            self._send_json(400, {"erro": "Content-Length inválido"})
            return None
        if tamanho > MAX_BODY:
            self._send_json(413, {"erro": "Corpo da requisição muito grande"})
            return None
        if tamanho <= 0:
            return {}
        bruto = self.rfile.read(tamanho)
        try:
            dados = json.loads(bruto.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"erro": "JSON inválido"})
            return None
        if not isinstance(dados, dict):
            self._send_json(400, {"erro": "JSON deve ser um objeto"})
            return None
        return dados

    # -- API -------------------------------------------------------------
    def _handle_api(
        self, method: str, path: str, query: Dict[str, List[str]]
    ) -> None:
        if path == "/api/health" and method == "GET":
            self._send_json(200, {"ok": True, "db": config.DB_PATH})
            return

        if path == "/api/resumo" and method == "GET":
            self._api_resumo()
            return

        if path == "/api/membros" and method == "GET":
            self._api_membros(query)
            return

        match = re.fullmatch(r"/api/membros/por-ra/(.+)", path)
        if match and method == "GET":
            self._api_membro_por_ra(match.group(1))
            return

        if path == "/api/caixa" and method == "GET":
            mes = (query.get("mes") or [db.buscar_mes_atual()])[0]
            caixa = db.obter_resumo_caixa(mes)
            # Transparência sem exposição nominal de quem pagou.
            for pagamento in caixa.get("pagamentos_recentes", []):
                pagamento.pop("nome", None)
            self._send_json(200, caixa)
            return

        if path == "/api/solicitar-pagamento" and method == "POST":
            self._api_solicitar_pagamento()
            return

        if path == "/api/assistente" and method == "POST":
            dados = self._read_json()
            if dados is None:
                return
            mensagem = str(dados.get("mensagem") or "").strip()
            if not mensagem:
                self._send_json(400, {"erro": "Mensagem vazia"})
                return
            ra = str(dados.get("ra") or "").strip() or None
            self._send_json(200, responder_assistente(mensagem, ra))
            return

        if path == "/api/admin/login" and method == "POST":
            self._api_admin_login()
            return

        if path == "/api/admin/logout" and method == "POST":
            self._api_admin_logout()
            return

        if path == "/api/admin/session" and method == "GET":
            usuario = self._admin_atual()
            if usuario:
                self._send_json(200, {"ok": True, "usuario": usuario})
            elif not _admin_habilitado():
                self._send_json(
                    503,
                    {"erro": "Painel admin desabilitado.", "habilitado": False},
                )
            else:
                self._send_json(
                    401, {"erro": "Sessão expirada.", "habilitado": True}
                )
            return

        if path == "/api/admin/membros" and method == "GET":
            if not self._require_admin():
                return
            membros = db.listar_membros_web(tipo="todos")
            self._send_json(
                200, {"total": len(membros), "membros": membros}
            )
            return

        if path == "/api/admin/membros/ex-bolsistas.csv" and method == "GET":
            if not self._require_admin():
                return
            membros = db.listar_membros_web(tipo="ex_bolsistas")
            buffer = io.StringIO()
            escritor = csv.writer(buffer, delimiter=";")
            escritor.writerow([
                "id", "nome", "ra", "status_vinculo", "modalidade_bolsa",
                "data_inicio", "data_desligamento", "telegram_id",
                "cotas_pagas", "total_pago", "cotas_pendentes", "saldo_devedor",
            ])
            for m in membros:
                escritor.writerow([
                    m.get("id"), m.get("nome"), m.get("ra") or "",
                    m.get("status_vinculo") or "", m.get("modalidade_bolsa") or "",
                    m.get("data_inicio") or "", m.get("data_desligamento") or "",
                    m.get("telegram_id") or "", m.get("cotas_pagas") or 0,
                    f"{float(m.get('total_pago') or 0):.2f}",
                    m.get("cotas_pendentes") or 0,
                    f"{float(m.get('saldo_devedor') or 0):.2f}",
                ])
            nome = f"ex-bolsistas-itcp-{datetime.now():%Y%m%d}.csv"
            self._send_csv(nome, buffer.getvalue())
            return

        if path == "/api/admin/telegram/cobrancas" and method == "POST":
            if not self._require_admin():
                return
            self._api_admin_disparar_telegram()
            return

        if path == "/api/admin/auditoria" and method == "GET":
            if not self._require_admin():
                return
            self._send_json(
                200,
                {
                    "auditoria": [
                        dict(row)
                        for row in db.listar_pagamentos_aguardando_auditoria()
                    ]
                },
            )
            return

        if path == "/api/admin/cobrancas" and method == "POST":
            if not self._require_admin():
                return
            dados = self._read_json()
            if dados is None:
                return
            mes = str(dados.get("mes") or db.buscar_mes_atual())
            try:
                criadas = db.criar_cobranca_mensal(mes)
            except ValueError as exc:
                self._send_json(400, {"erro": str(exc)})
                return
            self._send_json(200, {"ok": True, "mes": mes, "criadas": criadas})
            return

        if path == "/api/admin/membros" and method == "POST":
            if not self._require_admin():
                return
            self._api_admin_novo_membro()
            return

        match = re.fullmatch(r"/api/admin/membros/(\d+)", path)
        if match and method == "GET":
            if not self._require_admin():
                return
            detalhe = db.obter_detalhe_membro_web(int(match.group(1)))
            if detalhe is None:
                self._send_json(404, {"erro": "Membro não encontrado"})
                return
            self._send_json(200, {"membro": detalhe})
            return

        match = re.fullmatch(r"/api/admin/membros/(\d+)/vincular", path)
        if match and method == "POST":
            if not self._require_admin():
                return
            self._api_admin_vincular(int(match.group(1)))
            return

        match = re.fullmatch(r"/api/admin/auditoria/(\d+)", path)
        if match and method == "POST":
            if not self._require_admin():
                return
            self._api_admin_auditoria_item(int(match.group(1)))
            return

        if path == "/api/admin/despesas" and method == "POST":
            if not self._require_admin():
                return
            self._api_admin_nova_despesa()
            return

        match = re.fullmatch(r"/api/admin/despesas/(\d+)", path)
        if match and method == "DELETE":
            if not self._require_admin():
                return
            removida = db.remover_despesa(int(match.group(1)))
            if not removida:
                self._send_json(404, {"erro": "Despesa não encontrada"})
                return
            self._send_json(200, {"ok": True})
            return

        self._send_json(404, {"erro": "Rota não encontrada"})

    # -- endpoints -------------------------------------------------------
    def _api_resumo(self) -> None:
        mes = db.buscar_mes_atual()
        resumo = db.obter_resumo_financeiro()
        resumo_mes = db.obter_resumo_mes(mes)
        caixa = db.obter_resumo_caixa(mes)
        auditoria = db.listar_pagamentos_aguardando_auditoria()
        contagens = db.contar_membros_por_tipo()
        admin = self._is_admin()

        resposta: Dict[str, Any] = {
            "mes": mes,
            "valor_contribuicao": config.VALOR_CONTRIBUICAO,
            "pix_chave": config.PIX_CHAVE,
            "cobranca_dia": config.COBRANCA_DIA,
            "admin_habilitado": _admin_habilitado(),
            "admin_login_configurado": _login_configurado(),
            "telegram_habilitado": bool(
                (config.TELEGRAM_BOT_TOKEN or "").strip()
                and config.TELEGRAM_BOT_TOKEN != "SEU_TOKEN_AQUI"
            ),
            # Ex-bolsistas ficam arquivados no histórico: não vão para o
            # payload público, apenas para a sessão administrativa.
            "membros": {"ativos": contagens["ativos"]},
            "ativos": resumo["ativos"],
            "mes_atual": {"ativos": resumo_mes["ativos"]},
            "caixa": {
                "total_pago": caixa["total_pago"],
                "total_despesas": caixa["total_despesas"],
                "saldo": caixa["saldo"],
                "pago_mes": caixa["pago_mes"],
                "despesas_mes": caixa["despesas_mes"],
            },
            "auditoria": {"total": len(auditoria)},
        }
        if admin:
            resposta["membros"]["ex_bolsistas"] = contagens["ex_bolsistas"]
            resposta["ex_bolsistas"] = resumo["ex_bolsistas"]
            resposta["mes_atual"]["ex_bolsistas"] = resumo_mes["ex_bolsistas"]

        self._send_json(200, resposta)

    def _api_membros(self, query: Dict[str, List[str]]) -> None:
        tipo = (query.get("tipo") or ["ativos"])[0]
        if tipo not in ("todos", "ativos"):
            # Ex-bolsistas são arquivados e não aparecem no site público.
            self._send_json(200, {"total": 0, "membros": []})
            return
        busca = (query.get("q") or [""])[0]
        membros = db.listar_membros_web(tipo="ativos", busca=busca)
        # Retorno público minimalista: sem valores, dívidas, RA ou Telegram.
        neutros = [
            {
                "id": m["id"],
                "nome": m["nome"],
                "ex_bolsista": False,
                "status_vinculo": m.get("status_vinculo") or "ATIVO",
            }
            for m in membros
        ]
        self._send_json(200, {"total": len(neutros), "membros": neutros})

    def _api_membro_por_ra(self, ra: str) -> None:
        detalhe = db.obter_detalhe_membro_por_ra(ra)
        if detalhe is None:
            self._send_json(404, {"erro": "RA não encontrado"})
            return
        self._send_json(200, {"membro": _serializar_detalhe_publico(detalhe)})

    def _api_solicitar_pagamento(self) -> None:
        dados = self._read_json()
        if dados is None:
            return
        ra = str(dados.get("ra") or "").strip()
        mes = str(dados.get("mes") or db.buscar_mes_atual())
        if not ra:
            self._send_json(400, {"erro": "Informe o RA"})
            return
        detalhe = db.obter_detalhe_membro_por_ra(ra)
        if detalhe is None:
            self._send_json(404, {"erro": "RA não encontrado"})
            return
        if detalhe.get("ex_bolsista") and mes == db.buscar_mes_atual():
            self._send_json(
                409,
                {
                    "erro": (
                        "Você consta como ex-bolsista e não recebe novas "
                        "cobranças. Para pendências históricas, fale com a gestão."
                    ),
                    "motivo": "ex_bolsista",
                },
            )
            return

        ok, motivo = db.registrar_solicitacao_pagamento_membro(
            int(detalhe["id"]), mes, origem="web"
        )
        if not ok:
            mensagens = {
                "ja_pago": "Essa cota já está confirmada como paga.",
                "ja_aguardando": "Essa cota já está aguardando auditoria.",
                "mes_invalido": "Mês inválido.",
                "erro_banco": "Erro temporário ao registrar.",
            }
            self._send_json(
                409,
                {"erro": mensagens.get(motivo, "Não foi possível registrar."),
                 "motivo": motivo},
            )
            return

        _notificar_admins(
            "Nova solicitação de auditoria (web)\n"
            f"Membro: {detalhe['nome']}\n"
            f"RA: {detalhe.get('ra') or '—'}\n"
            f"Mês: {mes}\n"
            f"Valor: {_brl(config.VALOR_CONTRIBUICAO)}\n"
            "Confira no painel web ou no painel admin."
        )
        atualizado = db.obter_detalhe_membro_por_ra(ra)
        self._send_json(
            200,
            {
                "ok": True,
                "mensagem": "Solicitação registrada e enviada para auditoria.",
                "membro": _serializar_detalhe_publico(atualizado or detalhe),
            },
        )

    def _api_admin_login(self) -> None:
        if not _login_configurado():
            self._send_json(
                503,
                {
                    "erro": (
                        "Login administrativo não configurado. Defina "
                        "WEB_ADMIN_PASSWORD no .env."
                    )
                },
            )
            return

        ip = self.client_address[0]
        if _login_bloqueado(ip):
            self._send_json(
                429,
                {"erro": "Muitas tentativas. Tente novamente em alguns minutos."},
                {"Retry-After": str(JANELA_TENTATIVAS_SEGUNDOS)},
            )
            return

        dados = self._read_json()
        if dados is None:
            return
        usuario = str(dados.get("usuario") or "").strip()
        senha = str(dados.get("senha") or "")
        if not usuario or not senha:
            self._send_json(400, {"erro": "Informe usuário e senha."})
            return

        if not _credenciais_validas(usuario, senha):
            _registrar_falha_login(ip)
            # Mensagem genérica para não revelar qual campo errou.
            self._send_json(401, {"erro": "Usuário ou senha inválidos."})
            return

        _limpar_falhas_login(ip)
        token = _criar_sessao(usuario)
        self._send_json(
            200,
            {"ok": True, "usuario": usuario},
            {"Set-Cookie": _cookie_sessao(token)},
        )

    def _api_admin_logout(self) -> None:
        token = self._token_cookie()
        if token:
            _remover_sessao(token)
        self._send_json(
            200,
            {"ok": True},
            {"Set-Cookie": _cookie_expirado()},
        )

    def _api_admin_disparar_telegram(self) -> None:
        token_bot = (config.TELEGRAM_BOT_TOKEN or "").strip()
        if not token_bot or token_bot == "SEU_TOKEN_AQUI":
            self._send_json(
                503, {"erro": "TELEGRAM_BOT_TOKEN não configurado."}
            )
            return
        dados = self._read_json()
        if dados is None:
            return
        mes = str(dados.get("mes") or db.buscar_mes_atual())
        try:
            datetime.strptime(mes, "%Y-%m")
        except (TypeError, ValueError):
            self._send_json(400, {"erro": "Mês inválido"})
            return

        resultado = _disparar_cobrancas_telegram(mes)
        self._send_json(
            200,
            {
                "ok": True,
                "mes": mes,
                **resultado,
                "mensagem": (
                    f"{resultado['enviados']} cobrança(s) enviada(s) no Telegram."
                ),
            },
        )

    def _api_admin_novo_membro(self) -> None:
        dados = self._read_json()
        if dados is None:
            return
        nome = str(dados.get("nome") or "").strip()
        if not nome:
            self._send_json(400, {"erro": "Nome é obrigatório"})
            return
        telegram_id = dados.get("telegram_id")
        if telegram_id in ("", None):
            telegram_id = None
        else:
            try:
                telegram_id = int(telegram_id)
            except (TypeError, ValueError):
                self._send_json(400, {"erro": "telegram_id deve ser numérico"})
                return
        ok = db.adicionar_membro(
            nome=nome,
            telegram_id=telegram_id,
            ra=dados.get("ra"),
            status_vinculo=str(dados.get("status_vinculo") or "ATIVO"),
            ex_bolsista=bool(dados.get("ex_bolsista")),
        )
        if not ok:
            self._send_json(
                409, {"erro": "Já existe membro com esse RA ou Telegram."}
            )
            return
        membro = db.buscar_membro_por_ra(dados.get("ra")) if dados.get("ra") else None
        self._send_json(
            200,
            {
                "ok": True,
                "id": int(membro["id"]) if membro is not None else None,
            },
        )

    def _api_admin_vincular(self, membro_id: int) -> None:
        dados = self._read_json()
        if dados is None:
            return
        try:
            telegram_id = int(dados.get("telegram_id"))
        except (TypeError, ValueError):
            self._send_json(400, {"erro": "telegram_id deve ser numérico"})
            return

        dono = db.buscar_membro_por_telegram_id(telegram_id)
        if (
            dono is not None
            and int(dono["id"]) != int(membro_id)
            and not bool(dados.get("confirmar"))
        ):
            self._send_json(
                409,
                {
                    "erro": (
                        "Esse Telegram já pertence a outro cadastro. "
                        "Confirme para mesclar os registros."
                    ),
                    "requer_confirmacao": True,
                    "dono": {
                        "id": int(dono["id"]),
                        "nome": dono["nome"],
                        "ra": dono["ra"],
                    },
                },
            )
            return

        if not db.vincular_telegram_id(membro_id, telegram_id):
            self._send_json(404, {"erro": "Membro não encontrado"})
            return
        self._send_json(200, {"ok": True})

    def _api_admin_auditoria_item(self, pagamento_id: int) -> None:
        dados = self._read_json()
        if dados is None:
            return
        aprovado = bool(dados.get("aprovar", True))
        observacao = str(dados.get("observacao") or "").strip() or None
        if not db.aprovar_pagamento(pagamento_id, aprovado, observacao):
            self._send_json(404, {"erro": "Pagamento não encontrado"})
            return
        self._send_json(200, {"ok": True, "aprovado": aprovado})

    def _api_admin_nova_despesa(self) -> None:
        dados = self._read_json()
        if dados is None:
            return
        try:
            valor = float(dados.get("valor"))
            despesa_id = db.adicionar_despesa(
                descricao=str(dados.get("descricao") or ""),
                valor=valor,
                data=str(dados.get("data") or "") or None,
                categoria=str(dados.get("categoria") or "") or None,
                comprovante=str(dados.get("comprovante") or "") or None,
            )
        except (TypeError, ValueError) as exc:
            self._send_json(400, {"erro": str(exc)})
            return
        self._send_json(200, {"ok": True, "id": despesa_id})


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    db.init_db()

    host = config.WEB_HOST
    porta = config.WEB_PORT
    servidor = ThreadingHTTPServer((host, porta), WebHandler)
    servidor.daemon_threads = True

    logger.info("Interface web em http://%s:%s", host, porta)
    if not (config.WEB_ADMIN_TOKEN or "").strip():
        logger.warning(
            "WEB_ADMIN_TOKEN vazio: o painel admin ficará somente leitura."
        )
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        logger.info("Encerrando interface web...")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
