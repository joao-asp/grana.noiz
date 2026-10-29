/* ==========================================================================
   grana.noiz — SPA sem framework
   Hash routing + API JSON + renderização por templates.
   ========================================================================== */
'use strict';

const STORAGE_RA = 'grana_ra';

const MESES = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
];
const MESES_CURTOS = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];

const ICONS = {
  home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/><path d="M9.5 21v-6h5v6"/></svg>',
  users: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="3.2"/><path d="M3.5 20c.4-3.6 2.4-5.5 5.5-5.5s5.1 1.9 5.5 5.5"/><path d="M16 5.2a3 3 0 0 1 0 5.6"/><path d="M17.5 14.6c1.7.7 2.7 2.5 3 5.4"/></svg>',
  wallet: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6.5h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-12a2 2 0 0 1 2-2h12"/><path d="M16 12.5h4"/><circle cx="16.5" cy="14" r=".7" fill="currentColor" stroke="none"/></svg>',
  chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-8 8H5l-2 2V12a8 8 0 0 1 8-8h2a8 8 0 0 1 8 8Z"/><path d="M8 11h.01M12 11h.01M16 11h.01"/></svg>',
  lock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg>',
  unlock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 7.5-2"/></svg>',
  refresh: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 11a8 8 0 1 0-2.3 5.7"/><path d="M20 4v7h-7"/></svg>',
  plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 4.2 4.2L19 6.5"/></svg>',
  x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>',
  alert: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 2.8 20h18.4L12 3Z"/><path d="M12 9v5M12 17.2h.01"/></svg>',
  info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7.8h.01"/></svg>',
  link: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.1.1l1.4-1.4a5 5 0 0 0-7.1-7.1L10 5.9"/><path d="M14 11a5 5 0 0 0-7.1-.1l-1.4 1.4a5 5 0 0 0 7.1 7.1L14 18.1"/></svg>',
  copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/></svg>',
  search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>',
  calendar: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M8 3v4M16 3v4M3 10h18"/></svg>',
  receipt: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3Z"/><path d="M9 8h6M9 12h6"/></svg>',
  trend: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17 9 11l4 4 8-8"/><path d="M15 7h6v6"/></svg>',
  trash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16M9 7V4h6v3M7 7l1 14h8l1-14"/></svg>',
  send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4 20-7Z"/><path d="M22 2 11 13"/></svg>',
  favorite: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21l7.8-7.5 1.1-1.1a5.5 5.5 0 0 0-.1-7.8Z"/></svg>',
  download: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>',
};

const NAV = [
  { route: 'inicio', label: 'Início', icon: 'home' },
  { route: 'transparencia', label: 'Coletivo', icon: 'users' },
  { route: 'caixa', label: 'Caixa', icon: 'wallet' },
  { route: 'assistente', label: 'Assistente', icon: 'chat' },
];

const PAGE_TITLES = {
  inicio: 'Visão geral',
  transparencia: 'Transparência',
  caixa: 'Livro caixa',
  assistente: 'Assistente da caixinha',
  admin: 'Painel da gestão',
};

const state = {
  route: 'inicio',
  loading: true,
  resumo: null,
  membro: null,
  ra: localStorage.getItem(STORAGE_RA) || '',
  adminRoute: false,
  admin: false,
  adminUser: '',
  membros: [],
  auditoria: [],
  caixa: null,
  filters: { tipo: 'todos', q: '', semTelegram: false },
  chat: [],
  chatBusy: false,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data || {};
  }
}

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[char]));
}

function brl(value) {
  return Number(value || 0).toLocaleString('pt-BR', {
    style: 'currency', currency: 'BRL',
  });
}

function mesLabel(mes) {
  const match = /^(\d{4})-(\d{2})$/.exec(String(mes || ''));
  if (!match) return mes || '—';
  return `${MESES[Number(match[2]) - 1] || match[2]}/${match[1]}`;
}

function mesShort(mes) {
  const match = /^(\d{4})-(\d{2})$/.exec(String(mes || ''));
  if (!match) return mes || '—';
  return `${MESES_CURTOS[Number(match[2]) - 1] || match[2]}/${match[1].slice(2)}`;
}

function dateBR(value) {
  if (!value) return '';
  const parsed = new Date(String(value).length <= 10 ? `${value}T12:00:00` : value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return parsed.toLocaleDateString('pt-BR');
}

function hojeISO() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${now.getFullYear()}-${month}-${day}`;
}

function mesAtualISO() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

function initials(name) {
  const parts = String(name || '').trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return '?';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

function firstName(name) {
  return String(name || '').trim().split(/\s+/)[0] || 'coletivo';
}

function statusMeta(status) {
  const map = {
    pago: { label: 'Quitado', cls: 'badge-paid' },
    pendente: { label: 'Pendente', cls: 'badge-pending' },
    aguardando_auditoria: { label: 'Em auditoria', cls: 'badge-audit' },
    sem_cobranca: { label: 'Sem cobrança', cls: 'badge-neutral' },
  };
  return map[status] || { label: status || '—', cls: 'badge-neutral' };
}

function icon(name, cls = '') {
  return `<span class="icon ${cls}" aria-hidden="true">${ICONS[name] || ''}</span>`;
}

function badgeStatus(status) {
  const meta = statusMeta(status);
  return `<span class="badge ${meta.cls}">${esc(meta.label)}</span>`;
}

function badgeTipo(exBolsista) {
  return exBolsista
    ? '<span class="badge badge-ex">Ex-bolsista</span>'
    : '<span class="badge badge-active">Ativo</span>';
}

function pct(part, total) {
  if (!total) return 0;
  return Math.max(0, Math.min(100, Math.round((part / total) * 100)));
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body !== undefined) headers['Content-Type'] = 'application/json';

  const response = await fetch(path, {
    method: options.method || 'GET',
    headers,
    credentials: 'same-origin',
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  let data = {};
  try { data = await response.json(); } catch (_) { data = {}; }
  if (!response.ok) {
    throw new ApiError(data.erro || `Erro ${response.status}`, response.status, data);
  }
  return data;
}

function toast(message, type = 'success') {
  const root = $('#toast-root');
  if (!root) return;
  const el = document.createElement('div');
  el.className = `toast ${type === 'error' ? 'is-error' : type === 'info' ? 'is-info' : ''}`;
  const iconName = type === 'error' ? 'alert' : type === 'info' ? 'info' : 'check';
  el.innerHTML = `${icon(iconName)}<span>${esc(message)}</span>`;
  root.appendChild(el);
  window.setTimeout(() => el.remove(), 3600);
}

function parseRoute() {
  const raw = (window.location.hash || '').replace(/^#\/?/, '').trim();
  if (raw === 'gestao') return 'transparencia';
  return NAV.some((item) => item.route === raw) ? raw : 'inicio';
}

function isAdminPath() {
  return /^\/admin\/?$/.test(window.location.pathname);
}

function goPublic(route = 'inicio') {
  window.location.href = `/#/${route}`;
}

function navigate(route) {
  if (state.adminRoute) {
    goPublic(route);
    return;
  }
  if (!NAV.some((item) => item.route === route)) route = 'inicio';
  if (window.location.hash === `#/${route}`) {
    showRoute(route);
  } else {
    window.location.hash = `#/${route}`;
  }
}

function brandMarkup(link = true) {
  const tag = link ? 'a' : 'div';
  const href = link ? ' href="/#/inicio"' : '';
  return `<${tag} class="brand"${href} aria-label="grana.noiz, início">
    <span class="brand-word">grana.noiz</span>
    <span class="brand-slash">/</span>
    <span class="brand-sub">itcp-unicamp</span>
  </${tag}>`;
}

function renderShell(viewHtml) {
  const route = state.route;
  const mes = state.resumo?.mes || mesAtualISO();

  const sideLinks = NAV.map((item) => `
    <a href="#/${item.route}" data-route="${item.route}"
       class="${route === item.route ? 'is-active' : ''}"
       ${route === item.route ? 'aria-current="page"' : ''}>
      ${icon(item.icon)}<span>${item.label}</span>
    </a>`).join('');

  const bottomLinks = NAV.map((item) => `
    <a href="#/${item.route}" data-route="${item.route}"
       class="${route === item.route ? 'is-active' : ''}"
       aria-label="${item.label}">
      ${icon(item.icon)}<span>${item.label}</span>
    </a>`).join('');

  $('#app-shell').innerHTML = `
    <aside class="sidebar" aria-label="Navegação principal">
      ${brandMarkup(true)}
      <nav class="side-nav">${sideLinks}</nav>
      <div class="sidebar-foot">
        <div class="status-line"><span class="dot"></span> Caixa ativo</div>
      </div>
    </aside>

    <header class="topbar">
      <div class="topbar-left">
        <div>
          <span class="topbar-kicker">grana.noiz / itcp</span>
          <span class="topbar-title">${esc(PAGE_TITLES[route] || 'Caixinha')}</span>
        </div>
      </div>
      <div class="topbar-right">
        <span class="month-chip">${mesShort(mes)}</span>
      </div>
    </header>

    <main id="conteudo" class="main" aria-busy="${state.loading ? 'true' : 'false'}">
      ${viewHtml}
    </main>

    <nav class="bottom-nav" aria-label="Navegação inferior">${bottomLinks}</nav>
  `;
}

function renderAdminLogin() {
  return `
    <div class="admin-page">
      <div class="admin-login-wrap">
        ${brandMarkup(true)}
        <section class="card admin-login-card">
          <div class="lock-icon">${icon('lock')}</div>
          <span class="eyebrow" style="margin-top:16px">Acesso restrito</span>
          <h1 style="margin-top:6px">Painel da gestão</h1>
          <p class="subtitle">Entre com usuário e senha para cuidar das cotas, da conciliação e das cobranças.</p>
          ${state.resumo?.admin_login_configurado === false ? `
            <div class="empty" style="margin-top:16px">
              ${icon('alert')}
              <div>Login ainda não configurado. Defina <code>WEB_ADMIN_PASSWORD</code> no <code>.env</code> e reinicie a web.</div>
            </div>` : `
            <form data-form="admin-login" class="form-grid" style="margin-top:18px">
              <div class="field">
                <label for="admin-user">Usuário</label>
                <input id="admin-user" name="usuario" autocomplete="username" required>
              </div>
              <div class="field">
                <label for="admin-pass">Senha</label>
                <input id="admin-pass" name="senha" type="password"
                       autocomplete="current-password" required>
              </div>
              <button class="btn btn-primary btn-block" type="submit">
                ${icon('unlock')} Entrar no painel
              </button>
            </form>`}
          <a class="card-link" href="/#/inicio" style="margin-top:12px">← Voltar ao site</a>
        </section>
        <p class="admin-foot">Área não indexada. Sessão protegida por cookie HttpOnly.</p>
      </div>
    </div>`;
}

function renderAdminShell() {
  if (state.loading) {
    $('#app-shell').innerHTML = `
      <div class="admin-page">
        <div class="admin-login-wrap">
          ${brandMarkup(false)}
          <div class="loading-row">${renderLoading()}</div>
        </div>
      </div>`;
    return;
  }

  if (!state.admin) {
    $('#app-shell').innerHTML = renderAdminLogin();
    return;
  }

  $('#app-shell').innerHTML = `
    <div class="admin-shell">
      <header class="admin-topbar">
        ${brandMarkup(true)}
        <div class="admin-topbar-actions">
          <span class="badge badge-active" title="${esc(state.adminUser || 'gestão')}">Sessão ativa</span>
          <a class="btn btn-ghost btn-sm" href="/#/inicio">
            ${icon('home')} Ver site
          </a>
          <button class="btn btn-ghost btn-sm" type="button" data-action="admin-logout">
            ${icon('unlock')} Sair
          </button>
        </div>
      </header>
      <main id="conteudo" class="main admin-main" aria-busy="false">
        ${renderAdminDashboard()}
      </main>
    </div>`;
}

function renderLoading() {
  return `
    <div class="loading-row" aria-label="Carregando">
      <div class="skeleton" style="height:34px;width:52%"></div>
      <div class="skeleton" style="height:16px;width:72%"></div>
      <div class="skeleton skeleton-card"></div>
      <div class="skeleton skeleton-card"></div>
      <div class="skeleton skeleton-card"></div>
    </div>`;
}

function renderError(message) {
  return `
    <section class="card" style="max-width:560px;margin:8vh auto 0">
      <div class="card-header">
        <div>
          <div class="lock-icon">${icon('alert')}</div>
          <h2 class="card-title" style="margin-top:12px">Não foi possível carregar</h2>
          <p class="card-sub">${esc(message)}</p>
        </div>
      </div>
      <button class="btn btn-primary btn-block" type="button" data-action="refresh">
        ${icon('refresh')} Tentar novamente
      </button>
    </section>`;
}

function renderInicio() {
  const r = state.resumo;
  if (!r) return renderError('A API da caixinha não respondeu.');
  const m = state.membro;
  const ativosMes = r.mes_atual?.ativos || {};
  const cotasMes = (ativosMes.pagos || 0) + (ativosMes.pendentes || 0) + (ativosMes.em_auditoria || 0);
  const adesao = pct(ativosMes.pagos || 0, cotasMes);
  const totalAtivos = r.membros?.ativos || 0;

  const memberCard = m ? renderMemberCard(m, r) : `
    <section class="card member-entry-card">
      <div class="card-header">
        <div>
          <span class="eyebrow">${icon('users')} Minha caixinha</span>
          <h2 class="card-title" style="margin-top:7px">Entre com seu RA</h2>
          <p class="card-sub">Veja o que você deve à caixinha, suas pendências e seu histórico.</p>
        </div>
      </div>
      <form data-form="buscar-ra" class="form-grid">
        <div class="field">
          <label for="ra-input">Seu RA na ITCP/Unicamp</label>
          <input id="ra-input" name="ra" inputmode="numeric" autocomplete="off"
                 placeholder="Ex.: 248340" required>
          <span class="field-hint">
            O RA é usado só para localizar seu cadastro. Não pedimos senha nem
            dados bancários. Se não souber seu RA, fale com a gestão.
          </span>
        </div>
        <button class="btn btn-primary btn-block" type="submit">
          ${icon('search')} Ver o que eu devo
        </button>
      </form>
      <div class="member-entry-note">
        <span class="dot"></span>
        <span>A lista pública não mostra seus valores individuais.</span>
      </div>
    </section>`;

  const healthCard = `
    <section class="card">
      <div class="card-header">
        <div>
          <span class="eyebrow">${icon('wallet')} Saúde da caixinha</span>
          <h2 class="card-title" style="margin-top:7px">Saldo do livro caixa</h2>
        </div>
        <span class="badge badge-active">Coletivo ativo</span>
      </div>
      <div class="money-lg">${brl(r.caixa?.saldo || 0)}</div>
      <p class="card-sub" style="margin-top:5px">
        ${brl(r.caixa?.total_pago || 0)} arrecadados ·
        ${brl(r.caixa?.total_despesas || 0)} em despesas
      </p>
      <div class="progress-block">
        <div class="progress-label">
          <span>${icon('users')} Cotas de ${mesLabel(r.mes)}</span>
          <span class="mono text-secondary">${ativosMes.pagos || 0} de ${cotasMes} (${adesao}%)</span>
        </div>
        <div class="progress-track" role="progressbar" aria-valuenow="${adesao}"
             aria-valuemin="0" aria-valuemax="100">
          <div class="progress-fill" style="width:${adesao}%"></div>
        </div>
      </div>
    </section>`;

  const movimentacoes = m ? `
    <section class="card">
      <div class="card-header">
        <div>
          <h2 class="card-title">Minhas movimentações</h2>
          <p class="card-sub">Últimos lançamentos do seu cadastro.</p>
        </div>
      </div>
      ${renderPagamentosMembro(m)}
    </section>` : '';

  return `
    <section class="page-head">
      <div class="page-head-row">
        <div>
          <span class="eyebrow"><span class="dot"></span> Coletivo ativo</span>
          <h1>Olá, ${m ? esc(firstName(m.nome)) : 'coletivo'}</h1>
          <p class="subtitle">${m
            ? 'Seu espaço individual de acompanhamento da caixinha.'
            : 'Identifique-se pelo RA para ver sua situação. Os dados coletivos ficam logo abaixo.'}</p>
        </div>
        <span class="month-chip">${mesLabel(r.mes)}</span>
      </div>
    </section>

    <div class="grid-2" style="align-items:start">
      ${memberCard}
      ${healthCard}
    </div>

    <div class="stat-grid" style="margin-top:14px">
      <div class="stat">
        <span class="stat-label">Bolsistas ativos</span>
        <span class="stat-value">${totalAtivos}</span>
        <span class="stat-hint">pessoas contribuindo com o coletivo</span>
      </div>
      <div class="stat">
        <span class="stat-label">Pago no mês</span>
        <span class="stat-value is-secondary">${brl(ativosMes.valor_pago || 0)}</span>
        <span class="stat-hint">${ativosMes.pagos || 0} cota(s) confirmada(s)</span>
      </div>
      <div class="stat">
        <span class="stat-label">Em acompanhamento</span>
        <span class="stat-value is-tertiary">${r.ativos?.pendentes || 0}</span>
        <span class="stat-hint">cotas em conversa com a gestão</span>
      </div>
      <div class="stat">
        <span class="stat-label">Em auditoria</span>
        <span class="stat-value ${r.auditoria?.total ? 'is-primary' : ''}">${r.auditoria?.total || 0}</span>
        <span class="stat-hint">solicitações aguardando conferência</span>
      </div>
    </div>

    ${movimentacoes}

    <section class="card card-low" style="margin-top:14px">
      <div class="headerless-note">
        <div class="list-icon is-paid">${icon('trend')}</div>
        <div>
          <h3>Gestão horizontal e transparente</h3>
          <p class="card-sub" style="margin-top:3px">
            As cotas sustentam o espaço, o café e os materiais das oficinas.
            Imprevistos? Fale com a gestão na roda — a conversa vem antes da cobrança.
          </p>
        </div>
      </div>
    </section>`;
}

function renderMemberCard(m, r) {
  const status = m.status_mes_atual || 'sem_cobranca';
  const meta = statusMeta(status);
  const isEx = Boolean(m.ex_bolsista);
  const pix = r.pix_chave || '';
  const pagamentos = m.pagamentos || [];
  const pendentes = pagamentos.filter((p) => p.status_pagamento === 'pendente');
  const emAuditoria = pagamentos.filter((p) => p.status_pagamento === 'aguardando_auditoria');
  const cotaMes = pagamentos.find((p) => p.mes === r.mes);
  const valorMes = cotaMes ? Number(cotaMes.valor_pago) : Number(r.valor_contribuicao || 0);

  const opcoes = pendentes.map((p) => ({ mes: p.mes, valor: Number(p.valor_pago) }));
  if (
    !isEx
    && !opcoes.some((o) => o.mes === r.mes)
    && status !== 'pago'
    && status !== 'aguardando_auditoria'
  ) {
    opcoes.push({ mes: r.mes, valor: Number(r.valor_contribuicao || 0) });
  }

  const pendentesVisiveis = pendentes.slice(0, 8);
  const pendenciasHtml = pendentes.length ? `
    <div class="pending-block">
      <div class="pending-head">
        <span>Pendências em aberto</span>
        <span class="mono">${pendentes.length} cota(s)</span>
      </div>
      <div class="list">
        ${pendentesVisiveis.map((p) => `
          <div class="list-row">
            <div class="list-main">
              <div class="list-icon is-audit">${icon('receipt')}</div>
              <div>
                <div class="list-title">${mesLabel(p.mes)}</div>
                <span class="list-sub">em aberto</span>
              </div>
            </div>
            <span class="list-value">${brl(p.valor_pago)}</span>
          </div>`).join('')}
      </div>
      ${pendentes.length > pendentesVisiveis.length
        ? `<p class="field-hint">… e mais ${pendentes.length - pendentesVisiveis.length} mês(es). Fale com a gestão para combinar.</p>`
        : ''}
    </div>` : `
    <div class="empty" style="padding:14px;margin-top:12px">
      ${icon('check')}
      <div>${isEx ? 'Sem pendências históricas em aberto.' : 'Nenhuma pendência em aberto. 🎉'}</div>
    </div>`;

  const solicitacaoHtml = opcoes.length ? `
    <form data-form="solicitar-mes" class="solicitar-form">
      <div class="field">
        <label for="mes-solicitar">Avisar pagamento</label>
        <select id="mes-solicitar" name="mes">
          ${opcoes.map((o) => `
            <option value="${o.mes}">
              ${mesLabel(o.mes)} — ${brl(o.valor)}
            </option>`).join('')}
        </select>
      </div>
      <button class="btn btn-primary btn-block" type="submit">
        ${icon('receipt')} Avisar pagamento
      </button>
      <span class="field-hint">
        A gestão confere o extrato antes de confirmar. Se você já pagou,
        selecione o mês correspondente.
      </span>
    </form>` : status === 'aguardando_auditoria' ? `
    <div class="pending-note is-audit">
      ${icon('refresh')} Sua solicitação está em auditoria. A gestão confere e confirma.
    </div>` : `
    <div class="pending-note is-ok">
      ${icon('check')} ${isEx ? 'Sem novas cobranças para ex-bolsistas.' : 'Você está em dia com a caixinha.'}
    </div>`;

  return `
    <section class="card">
      <div class="card-header">
        <div class="member-main">
          <div class="avatar ${isEx ? 'is-ex' : ''}">${esc(initials(m.nome))}</div>
          <div class="member-info">
            <h2 class="card-title" style="font-size:1rem">${esc(m.nome)}</h2>
            <p class="card-sub">RA ${esc(m.ra || '—')} · ${esc(m.status_vinculo || 'ATIVO')}</p>
          </div>
        </div>
        <button class="card-link" type="button" data-action="clear-member">Trocar</button>
      </div>

      <div class="btn-row" style="margin-bottom:12px">
        ${badgeTipo(isEx)}
        ${badgeStatus(status)}
      </div>

      <div class="stat-grid" style="grid-template-columns:repeat(2,minmax(0,1fr))">
        <div class="stat">
          <span class="stat-label">Cota de ${mesLabel(r.mes)}</span>
          <span class="stat-value ${status === 'pago' ? 'is-secondary' : 'is-tertiary'}">
            ${brl(valorMes)}
          </span>
          <span class="stat-hint">${esc(meta.label)}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Total em aberto</span>
          <span class="stat-value ${Number(m.saldo_devedor || 0) > 0 ? 'is-tertiary' : 'is-secondary'}">
            ${brl(m.saldo_devedor || 0)}
          </span>
          <span class="stat-hint">${m.cotas_pendentes || 0} cota(s)</span>
        </div>
      </div>

      ${isEx ? `
        <p class="field-hint" style="margin-top:10px">
          Você consta como ex-bolsista. As pendências são históricas e não geram novas cobranças.
        </p>` : ''}

      ${pix ? `
        <div class="pix-box" style="margin-top:12px">
          <div class="pix-box-main">
            ${icon('copy')}
            <div style="min-width:0">
              <span class="pix-label">Chave Pix oficial</span>
              <span class="pix-value" title="${esc(pix)}">${esc(pix)}</span>
            </div>
          </div>
          <button class="btn btn-secondary btn-sm" type="button" data-action="copy-pix">
            ${icon('copy')} Copiar
          </button>
        </div>` : ''}

      ${solicitacaoHtml}

      ${pendenciasHtml}

      ${emAuditoria.length ? `
        <p class="field-hint" style="margin-top:10px">
          ${emAuditoria.length} solicitação(ões) em auditoria:
          ${emAuditoria.slice(0, 4).map((p) => mesLabel(p.mes)).join(', ')}.
        </p>` : ''}
    </section>`;
}

function renderPagamentosMembro(m) {
  const pagamentos = (m.pagamentos || []).slice(0, 6);
  if (!pagamentos.length) {
    return `<div class="empty">${icon('receipt')}<div>Nenhum lançamento encontrado.</div></div>`;
  }
  return `
    <div class="list">
      ${pagamentos.map((p) => {
        const meta = statusMeta(p.status_pagamento);
        const iconClass = p.status_pagamento === 'pago' ? 'is-paid'
          : p.status_pagamento === 'aguardando_auditoria' ? 'is-audit' : '';
        return `
          <div class="list-row">
            <div class="list-main">
              <div class="list-icon ${iconClass}">
                ${icon(p.status_pagamento === 'pago' ? 'check' : 'receipt')}
              </div>
              <div>
                <div class="list-title">Cota de ${mesLabel(p.mes)}</div>
                <span class="list-sub">${p.data_pagamento
                  ? `Confirmado em ${dateBR(p.data_pagamento)}`
                  : 'Importado do histórico'}</span>
              </div>
            </div>
            <div class="list-right">
              <span class="list-value">${brl(p.valor_pago)}</span>
              <span class="badge ${meta.cls}" style="margin-top:4px">${meta.label}</span>
            </div>
          </div>`;
      }).join('')}
    </div>`;
}

function renderAdminDashboard() {
  const r = state.resumo || {};
  const auditoria = state.auditoria || [];
  const caixa = state.caixa || {};
  const ativosMes = r.mes_atual?.ativos || {};
  const telegramOk = Boolean(r.telegram_habilitado);
  const comTelegram = state.membros.filter((m) => m.telegram_id && !m.ex_bolsista).length;

  const adminActions = `
    <div class="admin-actions">
      <button class="btn btn-primary" type="button" data-action="generate">
        ${icon('calendar')} Gerar cobranças de ${mesLabel(r.mes)}
      </button>
      <button class="btn btn-ghost" type="button" data-action="open-new-member">
        ${icon('plus')} Nova pessoa
      </button>
      <button class="btn btn-ghost" type="button" data-action="refresh">
        ${icon('refresh')} Atualizar
      </button>
    </div>`;

  return `
    <section class="page-head">
      <div class="page-head-row">
        <div>
          <span class="eyebrow">${icon('lock')} Painel da gestão</span>
          <h1>Membros & cobranças</h1>
          <p class="subtitle">Cotas, vínculos, conciliação e comunicação com o coletivo.</p>
        </div>
        <span class="badge badge-active">Caixa ativo</span>
      </div>
      ${adminActions}
    </section>

    <div class="stat-grid">
      <div class="stat">
        <span class="stat-label">Ativos</span>
        <span class="stat-value">${r.membros?.ativos || 0}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Ex-bolsistas</span>
        <span class="stat-value">${r.membros?.ex_bolsistas || 0}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Pago no mês</span>
        <span class="stat-value is-secondary">${brl(ativosMes.valor_pago || 0)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Aguardando auditoria</span>
        <span class="stat-value ${auditoria.length ? 'is-primary' : ''}">${auditoria.length}</span>
      </div>
    </div>

    <div class="grid-2" style="margin-top:14px">
      <section class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Cobrança no Telegram</h2>
            <p class="card-sub">Lembrete humano para ativos com pendência e Telegram vinculado.</p>
          </div>
          <button class="btn ${telegramOk ? 'btn-primary' : 'btn-ghost'} btn-sm"
                  type="button" data-action="disparar-telegram" ${telegramOk ? '' : 'disabled'}>
            ${icon('send')} Disparar
          </button>
        </div>
        <p class="field-hint">
          ${telegramOk
            ? `${comTelegram} membro(s) com Telegram vinculado. Se ainda não gerou as cotas do mês, use "Gerar cobranças" primeiro. A mensagem inclui a cota, pendências anteriores e um convite para conversar com a gestão. Nada é marcado como pago automaticamente.`
            : 'Configure TELEGRAM_BOT_TOKEN no .env para habilitar o disparo.'}
        </p>
      </section>

      <section class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Livro caixa</h2>
            <p class="card-sub">Saldo ${brl(caixa.saldo || 0)} · ${brl(caixa.total_despesas || 0)} em despesas.</p>
          </div>
          <button class="btn btn-ghost btn-sm" type="button" data-action="open-expense">
            ${icon('plus')} Despesa
          </button>
        </div>
        ${renderDespesas((caixa.despesas_recentes || []).slice(0, 3))}
      </section>
    </div>

    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Conciliação de pagamentos</h2>
          <p class="card-sub">Solicitações feitas pelo bot ou pela web.</p>
        </div>
        <button class="card-link" type="button" data-action="refresh">${icon('refresh')} Atualizar</button>
      </div>
      ${renderAuditoria(auditoria)}
    </section>

    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Membros do coletivo</h2>
          <p class="card-sub" id="member-count">${state.membros.length} cadastro(s)</p>
        </div>
        <a class="btn btn-ghost btn-sm" href="/api/admin/membros/ex-bolsistas.csv">
          ${icon('download')} Exportar ex-bolsistas
        </a>
      </div>
      <p class="field-hint" style="margin-top:-4px;margin-bottom:10px">
        Ex-bolsistas ficam guardados no histórico interno e não aparecem na
        transparência pública. Use o filtro “Ex-bolsistas” para vê-los aqui.
      </p>
      ${renderToolbar(true)}
      <div id="member-list">${renderMemberRows()}</div>
    </section>`;
}

function renderTransparencia() {
  const r = state.resumo || {};
  const ativosMes = r.mes_atual?.ativos || {};
  const totalMes = (ativosMes.pagos || 0) + (ativosMes.pendentes || 0) + (ativosMes.em_auditoria || 0);
  const confirmadas = ativosMes.pagos || 0;
  const acompanhamento = ativosMes.pendentes || 0;
  const adesao = pct(confirmadas, totalMes);

  return `
    <section class="page-head">
      <div class="page-head-row">
        <div>
          <span class="eyebrow"><span class="dot"></span> Transparência ativa</span>
          <h1>O coletivo</h1>
          <p class="subtitle">Quem faz parte e como a caixinha caminha, com cuidado e sem expor dívidas nominalmente.</p>
        </div>
      </div>
    </section>

    <div class="stat-grid">
      <div class="stat">
        <span class="stat-label">Bolsistas ativos</span>
        <span class="stat-value">${r.membros?.ativos || 0}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Cotas confirmadas no mês</span>
        <span class="stat-value is-secondary">${confirmadas} de ${totalMes}</span>
        <span class="stat-hint">${adesao}% do mês</span>
      </div>
      <div class="stat">
        <span class="stat-label">Em acompanhamento</span>
        <span class="stat-value is-tertiary">${acompanhamento}</span>
        <span class="stat-hint">conversas individuais da gestão</span>
      </div>
      <div class="stat">
        <span class="stat-label">Saldo do livro caixa</span>
        <span class="stat-value is-secondary">${brl(r.caixa?.saldo || 0)}</span>
        <span class="stat-hint">caixa aberto e transparente</span>
      </div>
    </div>

    <div class="progress-block" style="margin-top:14px">
      <div class="progress-label">
        <span>${icon('users')} Cotas de ${mesLabel(r.mes)}</span>
        <span class="mono text-secondary">${confirmadas} de ${totalMes} confirmadas</span>
      </div>
      <div class="progress-track" role="progressbar" aria-valuenow="${adesao}"
           aria-valuemin="0" aria-valuemax="100">
        <div class="progress-fill" style="width:${adesao}%"></div>
      </div>
    </div>

    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Quem está ativo no coletivo</h2>
          <p class="card-sub" id="member-count">${state.membros.length} pessoa(s) ativa(s) · ex-bolsistas ficam no histórico interno</p>
        </div>
      </div>
      ${renderToolbar(false)}
      <div id="member-list">${renderMembrosNeutros()}</div>
    </section>

    <section class="card card-low" style="margin-top:14px">
      <div class="headerless-note">
        <div class="list-icon is-paid">${icon('favorite')}</div>
        <div>
          <h3>Cuidado e conversa, não exposição</h3>
          <p class="card-sub" style="margin-top:3px">
            Não publicamos quem está devendo nem valores individuais. A gestão
            acompanha cada situação em conversa, considerando imprevistos e a
            realidade de cada pessoa. Ex-bolsistas continuam guardados no
            histórico interno e não aparecem nesta lista. O que é público é o
            caixa e a saúde geral do coletivo.
          </p>
        </div>
      </div>
    </section>`;
}

function renderAuditoria(itens) {
  if (!itens.length) {
    return `<div class="empty">${icon('check')}<div>Nenhum pagamento aguardando auditoria.</div></div>`;
  }
  return `
    <div class="list">
      ${itens.map((item) => `
        <div class="audit-row">
          <div class="list-main">
            <div class="list-icon is-audit">${icon('refresh')}</div>
            <div>
              <div class="list-title">${esc(item.nome)}</div>
              <span class="list-sub">
                RA ${esc(item.ra || '—')} · ${mesLabel(item.mes)} ·
                ${esc(item.data_pagamento ? dateBR(item.data_pagamento) : 'sem data')}
              </span>
            </div>
          </div>
          <div class="member-amount">
            <span class="value">${brl(item.valor_pago)}</span>
            <span class="label">Aguardando</span>
          </div>
          <div class="audit-actions">
            <button class="btn btn-secondary btn-sm" type="button"
                    data-action="audit" data-id="${item.id}" data-decision="1">
              ${icon('check')} Aprovar
            </button>
            <button class="btn btn-danger btn-sm" type="button"
                    data-action="audit" data-id="${item.id}" data-decision="0">
              ${icon('x')} Rejeitar
            </button>
          </div>
        </div>`).join('')}
    </div>`;
}

function renderToolbar(admin) {
  const f = state.filters;
  const chips = admin
    ? [
        ['todos', 'Todos'],
        ['ativos', 'Ativos'],
        ['ex_bolsistas', 'Ex-bolsistas'],
      ]
    : [];
  return `
    <div class="toolbar">
      <div class="form-inline">
        <div class="field">
          <label for="member-search">Buscar</label>
          <input id="member-search" data-search="membros" value="${esc(f.q)}"
                 placeholder="${admin ? 'Nome ou RA' : 'Nome'}" autocomplete="off">
        </div>
      </div>
      ${chips.length ? `
        <div class="filter-chips" role="group" aria-label="Filtrar membros">
          ${chips.map(([tipo, label]) => `
            <button class="chip ${f.tipo === tipo ? 'is-active' : ''}" type="button"
                    data-action="filter" data-tipo="${tipo}">${label}</button>`).join('')}
          ${admin ? `
            <button class="chip ${f.semTelegram ? 'is-active' : ''}" type="button"
                    data-action="filter-tg">Sem Telegram</button>` : ''}
        </div>` : ''}
    </div>`;
}

function membrosFiltrados() {
  const f = state.filters;
  const termo = f.q.trim().toLowerCase();
  return state.membros.filter((m) => {
    if (f.tipo === 'ativos' && m.ex_bolsista) return false;
    if (f.tipo === 'ex_bolsistas' && !m.ex_bolsista) return false;
    if (f.semTelegram && m.telegram_id) return false;
    if (!termo) return true;
    const alvo = `${m.nome || ''} ${m.ra || ''}`.toLowerCase();
    return alvo.includes(termo);
  });
}

function renderMemberRows() {
  const lista = membrosFiltrados();
  if (!lista.length) {
    return `<div class="empty">${icon('users')}<div>Nenhum membro encontrado com esse filtro.</div></div>`;
  }
  return `<div class="member-list">
    ${lista.map((m) => {
      const status = statusMeta(m.status_mes_atual);
      const isEx = Boolean(m.ex_bolsista);
      return `
        <div class="member-row">
          <div class="member-main">
            <div class="avatar ${isEx ? 'is-ex' : ''}">${esc(initials(m.nome))}</div>
            <div class="member-info">
              <div class="member-name">${esc(m.nome)}</div>
              <div class="member-meta">
                ${state.admin ? (m.ra ? `<span>RA ${esc(m.ra)}</span>` : '<span>sem RA</span>') : ''}
                <span>${esc(m.status_vinculo || (isEx ? 'EX-BOLSISTA' : 'ATIVO'))}</span>
                ${state.admin ? `<span>TG ${esc(m.telegram_id || '—')}</span>` : ''}
              </div>
            </div>
          </div>
          <div class="member-side">
            <div class="member-amount">
              <span class="value">${brl(m.saldo_devedor || 0)}</span>
              <span class="label">${m.cotas_pendentes || 0} pendente(s)</span>
            </div>
            <span class="badge ${status.cls}">${status.label}</span>
          </div>
          ${state.admin ? `
            <div class="member-actions">
              ${!m.telegram_id ? `
                <button class="btn btn-ghost btn-sm" type="button"
                        data-action="open-link" data-id="${m.id}">
                  ${icon('link')} Vincular Telegram
                </button>` : `
                <span class="badge badge-active">${icon('check')} Telegram</span>`}
              <button class="btn btn-ghost btn-sm" type="button"
                      data-action="member-detail" data-id="${m.id}">
                ${icon('info')} Detalhes
              </button>
            </div>` : ''}
        </div>`;
    }).join('')}
  </div>`;
}

function renderMembrosNeutros() {
  const lista = membrosFiltrados();
  if (!lista.length) {
    return `<div class="empty">${icon('users')}<div>Nenhum membro encontrado com esse filtro.</div></div>`;
  }
  return `<div class="member-list">
    ${lista.map((m) => `
      <div class="member-row neutral">
        <div class="member-main">
          <div class="avatar">${esc(initials(m.nome))}</div>
          <div class="member-info">
            <div class="member-name">${esc(m.nome)}</div>
            <div class="member-meta">
              <span>${esc(m.status_vinculo || 'ATIVO')}</span>
            </div>
          </div>
        </div>
        <div class="member-side">
          <span class="badge badge-active">Ativo</span>
        </div>
      </div>`).join('')}
  </div>`;
}

function updateMemberList() {
  const container = $('#member-list');
  if (container) {
    container.innerHTML = state.adminRoute ? renderMemberRows() : renderMembrosNeutros();
  }
  const count = $('#member-count');
  if (count) count.textContent = `${membrosFiltrados().length} cadastro(s)`;
  $$('.filter-chips .chip').forEach((chip) => {
    const tipo = chip.getAttribute('data-tipo');
    if (tipo) chip.classList.toggle('is-active', state.filters.tipo === tipo);
    if (chip.getAttribute('data-action') === 'filter-tg') {
      chip.classList.toggle('is-active', state.filters.semTelegram);
    }
  });
}

function renderCaixa() {
  const c = state.caixa;
  if (!c) return renderError('Não foi possível carregar o livro caixa.');
  const max = Math.max(...c.serie.map((s) => Number(s.arrecadado || 0)), 1);
  const barras = c.serie.map((s) => {
    const altura = s.arrecadado > 0 ? Math.max(4, Math.round((s.arrecadado / max) * 110)) : 2;
    return `
      <div class="chart-col" title="${mesShort(s.mes)}: ${brl(s.arrecadado)}">
        <div class="chart-bar"><i style="height:${altura}px"></i></div>
        <span class="chart-label">${mesShort(s.mes)}</span>
      </div>`;
  }).join('');

  return `
    <section class="page-head">
      <div class="page-head-row">
        <div>
          <span class="eyebrow">${icon('wallet')} Transparência ativa</span>
          <h1>Livro caixa</h1>
          <p class="subtitle">Cotas arrecadadas, despesas e série dos últimos 12 meses.</p>
        </div>
        <button class="icon-btn" type="button" data-action="refresh" aria-label="Atualizar">
          ${icon('refresh')}
        </button>
      </div>
    </section>

    <section class="card">
      <div class="card-header">
        <div>
          <span class="stat-label">Saldo do livro caixa</span>
          <div class="money-lg ${c.saldo >= 0 ? 'text-secondary' : 'text-error'}">${brl(c.saldo)}</div>
          <p class="card-sub" style="margin-top:4px">
            ${brl(c.total_pago)} em cotas · ${brl(c.total_despesas)} em despesas
          </p>
        </div>
        <span class="badge ${c.saldo >= 0 ? 'badge-active' : 'badge-ex'}">
          ${c.saldo >= 0 ? 'Positivo' : 'Negativo'}
        </span>
      </div>
      <div class="grid-2">
        <div class="stat">
          <span class="stat-label">Entradas em ${mesLabel(c.mes)}</span>
          <span class="stat-value is-secondary">+ ${brl(c.pago_mes)}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Saídas em ${mesLabel(c.mes)}</span>
          <span class="stat-value is-tertiary">- ${brl(c.despesas_mes)}</span>
        </div>
      </div>
    </section>

    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Arrecadação por mês</h2>
          <p class="card-sub">Cotas confirmadas nos últimos 12 meses.</p>
        </div>
        <div class="chart-legend"><span><i class="legend-dot"></i>Arrecadado</span></div>
      </div>
      <div class="chart" role="img" aria-label="Gráfico de arrecadação mensal">${barras}</div>
    </section>

    <div class="grid-2" style="margin-top:14px">
      <section class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Cotas recebidas</h2>
            <p class="card-sub">Lançamentos confirmados recentemente.</p>
          </div>
        </div>
        ${renderPagamentosRecentes(c.pagamentos_recentes)}
      </section>

      <section class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Despesas</h2>
            <p class="card-sub">Saídas registradas pela gestão.</p>
          </div>
        </div>
        ${renderDespesas(c.despesas_recentes)}
      </section>
    </div>`;
}

function renderPagamentosRecentes(itens) {
  if (!itens?.length) {
    return `<div class="empty">${icon('receipt')}<div>Nenhuma cota recebida ainda.</div></div>`;
  }
  return `<div class="list">
    ${itens.map((p) => `
      <div class="list-row">
        <div class="list-main">
          <div class="list-icon is-paid">${icon('check')}</div>
          <div>
            <div class="list-title">Cota recebida</div>
            <span class="list-sub">
              ${mesLabel(p.mes)} · ${p.data_pagamento ? dateBR(p.data_pagamento) : 'histórico'}
            </span>
          </div>
        </div>
        <div class="list-right">
          <span class="list-value">${brl(p.valor_pago)}</span>
        </div>
      </div>`).join('')}
  </div>`;
}

function renderDespesas(itens) {
  if (!itens?.length) {
    return `<div class="empty">${icon('wallet')}<div>Nenhuma despesa lançada.</div></div>`;
  }
  return `<div class="list">
    ${itens.map((d) => `
      <div class="list-row">
        <div class="list-main">
          <div class="list-icon is-expense">${icon('receipt')}</div>
          <div>
            <div class="list-title">${esc(d.descricao)}</div>
            <span class="list-sub">${dateBR(d.data)}${d.categoria ? ` · ${esc(d.categoria)}` : ''}</span>
          </div>
        </div>
        <div class="list-right">
          <span class="list-value text-error">- ${brl(d.valor)}</span>
          ${state.admin ? `
            <button class="btn btn-danger btn-sm" type="button" style="margin-top:4px"
                    data-action="delete-expense" data-id="${d.id}" aria-label="Remover despesa">
              ${icon('trash')}
            </button>` : ''}
        </div>
      </div>`).join('')}
  </div>`;
}

function renderAssistente() {
  if (!state.chat.length) {
    state.chat.push({
      role: 'bot',
      text: 'Oi! Sou o assistente da caixinha. Posso consultar suas pendências, a adesão do mês, o saldo do caixa, Pix e a próxima cobrança.',
      time: new Date(),
    });
  }
  return `
    <section class="page-head">
      <div class="page-head-row">
        <div>
          <span class="eyebrow">${icon('chat')} Apoio à organização</span>
          <h1>Assistente da caixinha</h1>
          <p class="subtitle">Respostas determinísticas com os dados reais do coletivo.</p>
        </div>
      </div>
    </section>

    <section class="card chat-card">
      <div class="chat-log" id="chat-log" aria-live="polite">
        ${state.chat.map(renderMensagem).join('')}
      </div>
      <div class="suggestions" id="chat-suggestions">
        ${['Quanto eu devo?', 'Como está a adesão do mês?', 'Qual o saldo?', 'Como pagar?', 'Próxima cobrança']
          .map((texto) => `<button class="suggestion" type="button" data-action="suggestion"
            data-text="${esc(texto)}">${esc(texto)}</button>`).join('')}
      </div>
      <form class="chat-form" data-form="chat">
        <div class="field" style="flex:1 1 auto">
          <label for="chat-input" class="hidden">Mensagem</label>
          <input id="chat-input" name="mensagem" placeholder="Pergunte sobre a caixinha…"
                 autocomplete="off" required ${state.chatBusy ? 'disabled' : ''}>
        </div>
        <button class="btn btn-primary" type="submit" ${state.chatBusy ? 'disabled' : ''}
                aria-label="Enviar mensagem">
          ${icon('send')}
        </button>
      </form>
    </section>`;
}

function renderMensagem(msg) {
  const hora = msg.time instanceof Date
    ? msg.time.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    : '';
  return `
    <div class="msg ${msg.role === 'user' ? 'msg-user' : 'msg-bot'}">
      ${esc(msg.text)}
      ${hora ? `<span class="msg-time">${hora}</span>` : ''}
    </div>`;
}

function renderView() {
  if (state.loading) return renderLoading();
  switch (state.route) {
    case 'transparencia': return renderTransparencia();
    case 'caixa': return renderCaixa();
    case 'assistente': return renderAssistente();
    case 'inicio':
    default: return renderInicio();
  }
}

function render() {
  if (state.adminRoute) {
    renderAdminShell();
  } else {
    renderShell(renderView());
  }
}

async function fetchResumo() {
  state.resumo = await api('/api/resumo');
}

async function loadMembro(silencioso = false) {
  if (!state.ra) return;
  try {
    const data = await api(`/api/membros/por-ra/${encodeURIComponent(state.ra)}`);
    state.membro = data.membro;
  } catch (error) {
    state.membro = null;
    localStorage.removeItem(STORAGE_RA);
    state.ra = '';
    if (!silencioso) toast(error.message, 'error');
  }
}

async function loadMembros() {
  if (state.adminRoute) {
    const data = await api('/api/admin/membros');
    state.membros = data.membros || [];
  } else {
    const data = await api('/api/membros?tipo=ativos');
    state.membros = data.membros || [];
  }
}

async function loadAuditoria() {
  const data = await api('/api/admin/auditoria');
  state.auditoria = data.auditoria || [];
}

async function loadCaixa() {
  state.caixa = await api('/api/caixa');
}

async function loadAdminData() {
  await Promise.all([fetchResumo(), loadMembros(), loadAuditoria(), loadCaixa()]);
}

async function showRoute(route, opcoes = {}) {
  state.route = NAV.some((item) => item.route === route) ? route : 'inicio';
  state.loading = true;
  render();

  try {
    if (!opcoes.skipResumo && !state.resumo) await fetchResumo();
    if (state.route === 'transparencia') {
      if (!state.membros.length) await loadMembros();
    }
    if (state.route === 'caixa' && !state.caixa) await loadCaixa();
    if (state.route === 'inicio' && state.ra && !state.membro) {
      await loadMembro(true);
    }
  } catch (error) {
    toast(error.message || 'Erro ao carregar dados', 'error');
  }

  state.loading = false;
  render();
}

async function refreshData() {
  state.resumo = null;
  state.caixa = null;
  try {
    if (state.adminRoute) {
      if (state.admin) {
        await loadAdminData();
      } else {
        await fetchResumo();
      }
    } else {
      await fetchResumo();
      if (state.route === 'transparencia') await loadMembros();
      if (state.route === 'caixa') await loadCaixa();
      if (state.ra) await loadMembro(true);
    }
  } catch (error) {
    toast(error.message || 'Erro ao atualizar', 'error');
  }
  state.loading = false;
  render();
}

async function refreshRoute() {
  if (state.adminRoute) {
    await refreshData();
    return;
  }
  if (state.route === 'caixa') state.caixa = null;
  if (state.route === 'transparencia') state.membros = [];
  await refreshData();
}

async function loginAdmin(usuario, senha) {
  await api('/api/admin/login', {
    method: 'POST',
    body: { usuario, senha },
  });
  state.admin = true;
  state.adminUser = usuario;
  state.loading = true;
  render();
  try {
    await loadAdminData();
  } catch (error) {
    toast(error.message || 'Erro ao carregar o painel.', 'error');
  }
  state.loading = false;
  render();
  toast(`Bem-vindo(a), ${usuario}.`, 'success');
}

async function logoutAdmin() {
  try {
    await api('/api/admin/logout', { method: 'POST', body: {} });
  } catch (_) {
    // mesmo se a rede falhar, o cookie expira no servidor na próxima sessão
  }
  state.admin = false;
  state.adminUser = '';
  state.membros = [];
  state.auditoria = [];
  state.caixa = null;
  state.resumo = null;
  state.filters = { tipo: 'todos', q: '', semTelegram: false };
  toast('Sessão encerrada.', 'info');
  render();
}

function openModal({ title, subtitle = '', body, submitLabel = 'Confirmar', danger = false, onSubmit }) {
  const root = $('#modal-root');
  root.innerHTML = `
    <div class="modal-backdrop" role="presentation">
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div class="modal-header">
          <div>
            <h2 class="modal-title" id="modal-title">${esc(title)}</h2>
            ${subtitle ? `<p class="modal-sub">${esc(subtitle)}</p>` : ''}
          </div>
          <button class="icon-btn" type="button" data-action="close-modal" aria-label="Fechar">
            ${icon('x')}
          </button>
        </div>
        <form id="modal-form">
          <div class="modal-body">${body}</div>
          <div class="modal-actions">
            <button class="btn btn-ghost" type="button" data-action="close-modal">Cancelar</button>
            <button class="btn ${danger ? 'btn-danger' : 'btn-primary'}" type="submit">${esc(submitLabel)}</button>
          </div>
        </form>
      </div>
    </div>`;

  document.body.classList.add('modal-open');
  const backdrop = $('.modal-backdrop', root);
  backdrop.addEventListener('click', (event) => {
    if (event.target === backdrop) closeModal();
  });

  const form = $('#modal-form', root);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const botao = form.querySelector('button[type="submit"]');
    const rotulo = botao.textContent;
    botao.disabled = true;
    botao.textContent = 'Salvando…';
    try {
      const dados = Object.fromEntries(new FormData(form).entries());
      const resultado = await onSubmit(dados, form);
      if (resultado !== false) closeModal();
    } catch (error) {
      toast(error.message || 'Não foi possível salvar.', 'error');
      botao.disabled = false;
      botao.textContent = rotulo;
    }
  });

  window.setTimeout(() => {
    const primeiro = root.querySelector('input, textarea, select');
    if (primeiro) primeiro.focus();
  }, 30);
}

function closeModal() {
  const root = $('#modal-root');
  if (root) root.innerHTML = '';
  document.body.classList.remove('modal-open');
}

function openNovoMembro() {
  openModal({
    title: 'Nova pessoa no coletivo',
    subtitle: 'Cadastro manual de membro ativo ou ex-bolsista.',
    submitLabel: 'Cadastrar',
    body: `
      <div class="form-grid two">
        <div class="field">
          <label for="novo-nome">Nome</label>
          <input id="novo-nome" name="nome" required maxlength="120">
        </div>
        <div class="field">
          <label for="novo-ra">RA (opcional)</label>
          <input id="novo-ra" name="ra" inputmode="numeric" autocomplete="off">
        </div>
        <div class="field">
          <label for="novo-telegram">Telegram ID (opcional)</label>
          <input id="novo-telegram" name="telegram_id" inputmode="numeric" autocomplete="off">
        </div>
        <div class="field">
          <label for="novo-status">Status</label>
          <input id="novo-status" name="status_vinculo" value="ATIVO" maxlength="80">
        </div>
      </div>
      <label class="checkbox">
        <input type="checkbox" name="ex_bolsista"> Ex-bolsista (mantém histórico, sem novas cobranças)
      </label>`,
    onSubmit: async (dados) => {
      await api('/api/admin/membros', {
        method: 'POST',
        body: {
          nome: dados.nome,
          ra: dados.ra || null,
          telegram_id: dados.telegram_id || null,
          status_vinculo: dados.status_vinculo || 'ATIVO',
          ex_bolsista: dados.ex_bolsista === 'on',
        },
      });
      toast('Pessoa cadastrada com sucesso.');
      await refreshData();
    },
  });
}

function openVincular(membroId) {
  const membro = state.membros.find((m) => Number(m.id) === Number(membroId));
  if (!membro) return;
  openModal({
    title: 'Vincular Telegram',
    subtitle: membro.nome,
    submitLabel: 'Vincular',
    body: `
      <div class="field">
        <label for="vincular-telegram">ID numérico do Telegram</label>
        <input id="vincular-telegram" name="telegram_id" inputmode="numeric"
               autocomplete="off" required>
        <span class="field-hint">Se o Telegram já pertencer a outro cadastro, será pedida confirmação para mesclar.</span>
      </div>`,
    onSubmit: async (dados) => {
      try {
        await api(`/api/admin/membros/${membroId}/vincular`, {
          method: 'POST',
          body: { telegram_id: Number(dados.telegram_id) },
        });
      } catch (error) {
        if (error.status === 409 && error.data?.requer_confirmacao) {
          openConfirmarMesclagem(membroId, dados.telegram_id, error.data.dono);
          return false;
        }
        throw error;
      }
      toast('Telegram vinculado com sucesso.');
      await refreshData();
    },
  });
}

function openConfirmarMesclagem(membroId, telegramId, dono) {
  openModal({
    title: 'Mesclar cadastros?',
    subtitle: 'Essa ação move os lançamentos e remove o cadastro antigo.',
    submitLabel: 'Mesclar e vincular',
    danger: true,
    body: `
      <p class="small">
        O Telegram <strong>${esc(telegramId)}</strong> já pertence a
        <strong>${esc(dono?.nome || 'outro cadastro')}</strong>
        ${dono?.ra ? `(RA ${esc(dono.ra)})` : ''}.
      </p>
      <p class="field-hint">
        Os pagamentos do cadastro antigo serão preservados no membro selecionado.
      </p>`,
    onSubmit: async () => {
      await api(`/api/admin/membros/${membroId}/vincular`, {
        method: 'POST',
        body: { telegram_id: Number(telegramId), confirmar: true },
      });
      toast('Cadastros mesclados e Telegram vinculado.');
      await refreshData();
    },
  });
}

function openGerarCobrancas() {
  const mes = state.resumo?.mes || mesAtualISO();
  openModal({
    title: `Gerar cobranças de ${mesLabel(mes)}`,
    subtitle: 'Somente bolsistas ativos recebem novas cobranças.',
    submitLabel: 'Gerar cobranças',
    body: `<p class="small">As cotas pendentes de ${mesLabel(mes)} serão criadas para todos os membros ativos. Ex-bolsistas ficam de fora.</p>`,
    onSubmit: async () => {
      const resultado = await api('/api/admin/cobrancas', {
        method: 'POST',
        body: { mes },
      });
      toast(`${resultado.criadas} cobrança(s) criada(s) para ${mesLabel(mes)}.`);
      await refreshData();
    },
  });
}

function openDispararTelegram() {
  const mes = state.resumo?.mes || mesAtualISO();
  if (!state.resumo?.telegram_habilitado) {
    toast('Configure TELEGRAM_BOT_TOKEN no .env para disparar.', 'info');
    return;
  }
  openModal({
    title: 'Disparar cobranças no Telegram',
    subtitle: mesLabel(mes),
    submitLabel: 'Disparar agora',
    body: `
      <p class="small">
        O lembrete será enviado individualmente para bolsistas ativos com
        pendência e Telegram vinculado.
      </p>
      <p class="field-hint">
        Quem está em dia não recebe. A mensagem é humana, inclui a cota do mês
        e convida a conversar com a gestão. Nada é marcado como pago
        automaticamente.
      </p>`,
    onSubmit: async () => {
      const resultado = await api('/api/admin/telegram/cobrancas', {
        method: 'POST',
        body: { mes },
      });
      const resumo = [
        `${resultado.enviados} enviada(s)`,
        `${resultado.sem_pendencia} em dia`,
        `${resultado.erros} erro(s)`,
      ].join(' · ');
      toast(resumo, resultado.erros ? 'info' : 'success');
    },
  });
}

function openAuditoria(item, aprovado) {
  openModal({
    title: aprovado ? 'Aprovar pagamento' : 'Rejeitar solicitação',
    subtitle: `${item.nome} · ${mesLabel(item.mes)} · ${brl(item.valor_pago)}`,
    submitLabel: aprovado ? 'Aprovar' : 'Rejeitar',
    danger: !aprovado,
    body: `
      <div class="field">
        <label for="audit-obs">Observação (opcional)</label>
        <textarea id="audit-obs" name="observacao"
          placeholder="${aprovado ? 'Ex.: conferido no extrato de 05/10' : 'Ex.: valor não localizado no extrato'}"></textarea>
      </div>`,
    onSubmit: async (dados) => {
      await api(`/api/admin/auditoria/${item.id}`, {
        method: 'POST',
        body: { aprovar: aprovado, observacao: dados.observacao || null },
      });
      toast(aprovado ? 'Pagamento aprovado.' : 'Solicitação rejeitada.', aprovado ? 'success' : 'info');
      await refreshData();
    },
  });
}

function openNovaDespesa() {
  openModal({
    title: 'Nova despesa',
    subtitle: 'Lançamento no livro caixa do coletivo.',
    submitLabel: 'Lançar despesa',
    body: `
      <div class="form-grid two">
        <div class="field" style="grid-column:1/-1">
          <label for="despesa-desc">Descrição</label>
          <input id="despesa-desc" name="descricao" required maxlength="140"
                 placeholder="Ex.: Café e filtros para oficina">
        </div>
        <div class="field">
          <label for="despesa-valor">Valor (R$)</label>
          <input id="despesa-valor" name="valor" type="number" min="0.01" step="0.01" required>
        </div>
        <div class="field">
          <label for="despesa-data">Data</label>
          <input id="despesa-data" name="data" type="date" value="${hojeISO()}" required>
        </div>
        <div class="field">
          <label for="despesa-categoria">Categoria</label>
          <input id="despesa-categoria" name="categoria" maxlength="60"
                 placeholder="alimentação, materiais…">
        </div>
        <div class="field">
          <label for="despesa-comprovante">Comprovante (opcional)</label>
          <input id="despesa-comprovante" name="comprovante" maxlength="255"
                 placeholder="Link ou referência">
        </div>
      </div>`,
    onSubmit: async (dados) => {
      await api('/api/admin/despesas', {
        method: 'POST',
        body: {
          descricao: dados.descricao,
          valor: Number(dados.valor),
          data: dados.data,
          categoria: dados.categoria || null,
          comprovante: dados.comprovante || null,
        },
      });
      toast('Despesa lançada no livro caixa.');
      await refreshData();
    },
  });
}

function openExcluirDespesa(id) {
  openModal({
    title: 'Remover despesa?',
    subtitle: 'Essa ação não pode ser desfeita.',
    submitLabel: 'Remover',
    danger: true,
    body: '<p class="small">O lançamento será apagado do livro caixa e o saldo será recalculado.</p>',
    onSubmit: async () => {
      await api(`/api/admin/despesas/${id}`, { method: 'DELETE' });
      toast('Despesa removida.');
      await refreshData();
    },
  });
}

async function openDetalheMembro(id) {
  let m;
  try {
    const data = await api(`/api/admin/membros/${id}`);
    m = data.membro;
  } catch (error) {
    toast(error.message || 'Não foi possível carregar o membro.', 'error');
    return;
  }
  const pagamentos = (m.pagamentos || []).slice(0, 8);
  openModal({
    title: m.nome,
    subtitle: `RA ${m.ra || '—'} · ${m.status_vinculo || 'ATIVO'}`,
    submitLabel: 'Fechar',
    body: `
      <div class="stat-grid">
        <div class="stat">
          <span class="stat-label">Pendente</span>
          <span class="stat-value is-tertiary">${brl(m.saldo_devedor || 0)}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Pago</span>
          <span class="stat-value is-secondary">${brl(m.total_pago || 0)}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Cotas pagas</span>
          <span class="stat-value">${m.cotas_pagas || 0}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Auditoria</span>
          <span class="stat-value">${m.em_auditoria || 0}</span>
        </div>
      </div>
      ${pagamentos.length ? `
        <div class="list" style="margin-top:12px">
          ${pagamentos.map((p) => `
            <div class="list-row">
              <div class="list-main">
                <div class="list-icon ${p.status_pagamento === 'pago' ? 'is-paid' : p.status_pagamento === 'aguardando_auditoria' ? 'is-audit' : ''}">
                  ${icon(p.status_pagamento === 'pago' ? 'check' : 'receipt')}
                </div>
                <div>
                  <div class="list-title">${mesLabel(p.mes)}</div>
                  <span class="list-sub">${statusMeta(p.status_pagamento).label}</span>
                </div>
              </div>
              <span class="list-value">${brl(p.valor_pago)}</span>
            </div>`).join('')}
        </div>` : '<div class="empty" style="margin-top:12px">Sem lançamentos.</div>'}
    `,
    onSubmit: async () => {},
  });
}

async function solicitarPagamentoMes(mes) {
  if (!state.ra) return;
  const mesEscolhido = mes || state.resumo?.mes || mesAtualISO();
  try {
    const resultado = await api('/api/solicitar-pagamento', {
      method: 'POST',
      body: { ra: state.ra, mes: mesEscolhido },
    });
    state.membro = resultado.membro;
    toast(resultado.mensagem || 'Solicitação registrada.');
    await refreshData();
  } catch (error) {
    toast(error.message || 'Não foi possível solicitar.', 'error');
  }
}

async function solicitarPagamento() {
  return solicitarPagamentoMes(state.resumo?.mes || mesAtualISO());
}

async function copiarPix() {
  const pix = state.resumo?.pix_chave;
  if (!pix) {
    toast('Chave Pix não configurada.', 'info');
    return;
  }
  try {
    await navigator.clipboard.writeText(pix);
    toast('Chave Pix copiada.');
  } catch (_) {
    toast('Não foi possível copiar automaticamente.', 'error');
  }
}

function appendChat(role, text) {
  state.chat.push({ role, text, time: new Date() });
  const log = $('#chat-log');
  if (log) {
    log.insertAdjacentHTML('beforeend', renderMensagem(state.chat[state.chat.length - 1]));
    log.scrollTop = log.scrollHeight;
  }
}

async function sendChat(texto) {
  const mensagem = String(texto || '').trim();
  if (!mensagem || state.chatBusy) return;
  appendChat('user', mensagem);
  state.chatBusy = true;
  const input = $('#chat-input');
  if (input) { input.value = ''; input.disabled = true; }
  const form = $('form[data-form="chat"]');
  if (form) form.querySelector('button[type="submit"]').disabled = true;

  try {
    const resposta = await api('/api/assistente', {
      method: 'POST',
      body: { mensagem, ra: state.ra || null },
    });
    appendChat('bot', resposta.resposta || 'Não consegui responder.');
  } catch (error) {
    appendChat('bot', error.message || 'Erro ao consultar o assistente.');
  } finally {
    state.chatBusy = false;
    if (input) { input.disabled = false; input.focus(); }
    if (form) form.querySelector('button[type="submit"]').disabled = false;
  }
}

function buscarRA(ra) {
  const valor = String(ra || '').trim();
  if (!valor) {
    toast('Informe seu RA.', 'error');
    return;
  }
  state.ra = valor;
  localStorage.setItem(STORAGE_RA, valor);
  state.membro = null;
  showRoute('inicio');
}

async function handleAction(element) {
  const action = element.dataset.action;
  switch (action) {
    case 'admin-logout':
      await logoutAdmin();
      break;
    case 'disparar-telegram':
      openDispararTelegram();
      break;
    case 'refresh':
      await refreshRoute();
      break;
    case 'clear-member':
      state.membro = null;
      state.ra = '';
      localStorage.removeItem(STORAGE_RA);
      render();
      break;
    case 'copy-pix':
      await copiarPix();
      break;
    case 'solicitar':
      await solicitarPagamento();
      break;
    case 'generate':
      openGerarCobrancas();
      break;
    case 'open-new-member':
      openNovoMembro();
      break;
    case 'open-link':
      openVincular(Number(element.dataset.id));
      break;
    case 'member-detail':
      await openDetalheMembro(Number(element.dataset.id));
      break;
    case 'audit':
      {
        const item = state.auditoria.find((a) => Number(a.id) === Number(element.dataset.id));
        if (item) openAuditoria(item, element.dataset.decision === '1');
      }
      break;
    case 'open-expense':
      openNovaDespesa();
      break;
    case 'delete-expense':
      openExcluirDespesa(Number(element.dataset.id));
      break;
    case 'filter':
      state.filters.tipo = element.dataset.tipo || 'todos';
      updateMemberList();
      break;
    case 'filter-tg':
      state.filters.semTelegram = !state.filters.semTelegram;
      updateMemberList();
      break;
    case 'suggestion':
      sendChat(element.dataset.text);
      break;
    case 'close-modal':
      closeModal();
      break;
    case 'retry':
      await refreshRoute();
      break;
    default:
      break;
  }
}

async function handleSubmit(form) {
  const tipo = form.dataset.form;
  if (tipo === 'buscar-ra') {
    const dados = Object.fromEntries(new FormData(form).entries());
    buscarRA(dados.ra);
    return;
  }
  if (tipo === 'admin-login') {
    const dados = Object.fromEntries(new FormData(form).entries());
    const usuario = String(dados.usuario || '').trim();
    const senha = String(dados.senha || '');
    if (!usuario || !senha) {
      toast('Informe usuário e senha.', 'error');
      return;
    }
    try {
      await loginAdmin(usuario, senha);
    } catch (error) {
      const campoSenha = form.querySelector('[name="senha"]');
      if (campoSenha) campoSenha.value = '';
      toast(error.message || 'Não foi possível entrar.', 'error');
    }
    return;
  }
  if (tipo === 'solicitar-mes') {
    const dados = Object.fromEntries(new FormData(form).entries());
    await solicitarPagamentoMes(dados.mes);
    return;
  }
  if (tipo === 'chat') {
    const dados = Object.fromEntries(new FormData(form).entries());
    await sendChat(dados.mensagem);
  }
}

document.addEventListener('click', (event) => {
  const routeEl = event.target.closest('[data-route]');
  if (routeEl) {
    event.preventDefault();
    navigate(routeEl.dataset.route);
    return;
  }
  const actionEl = event.target.closest('[data-action]');
  if (actionEl) {
    event.preventDefault();
    handleAction(actionEl);
  }
});

document.addEventListener('submit', (event) => {
  const form = event.target.closest('form[data-form]');
  if (!form) return;
  event.preventDefault();
  handleSubmit(form);
});

document.addEventListener('input', (event) => {
  if (event.target.matches('[data-search="membros"]')) {
    state.filters.q = event.target.value;
    updateMemberList();
  }
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeModal();
});

window.addEventListener('hashchange', () => {
  if (state.adminRoute) {
    render();
    return;
  }
  showRoute(parseRoute());
});

async function boot() {
  state.adminRoute = isAdminPath();

  if (state.adminRoute) {
    state.route = 'admin';
    state.loading = true;
    render();

    try {
      await fetchResumo();
    } catch (_) {
      // o login ainda pode funcionar; a sessão dirá
    }

    try {
      const sessao = await api('/api/admin/session');
      state.admin = true;
      state.adminUser = sessao.usuario || '';
    } catch (error) {
      state.admin = false;
      if (error.status && ![401, 503].includes(error.status)) {
        toast(error.message || 'Não foi possível validar a sessão.', 'error');
      }
    }

    if (state.admin) {
      try {
        await loadAdminData();
      } catch (error) {
        toast(error.message || 'Não foi possível carregar o painel.', 'error');
      }
    }

    state.loading = false;
    render();
    return;
  }

  state.route = parseRoute();
  state.loading = true;
  render();

  try {
    await fetchResumo();
  } catch (error) {
    toast(error.message || 'API indisponível.', 'error');
  }

  if (state.ra) await loadMembro(true);
  await showRoute(state.route, { skipResumo: true });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}
