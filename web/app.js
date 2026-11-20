/* ==========================================================================
   grana.noiz — SPA sem framework
   Hash routing + API JSON + renderização por templates.
   ========================================================================== */
'use strict';

const STORAGE_RA = 'grana_ra';
const STORAGE_THEME = 'grana_theme';

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
  sun: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>',
  moon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A8.5 8.5 0 1 1 11.2 3a6.6 6.6 0 0 0 9.8 9.8Z"/></svg>',
  download: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M5 21h14"/></svg>',
};

const NAV = [
  { route: 'inicio', label: 'Início', icon: 'home' },
  { route: 'transparencia', label: 'ITCP', icon: 'users' },
  { route: 'caixa', label: 'Caixa', icon: 'wallet' },
  { route: 'assistente', label: 'Assistente', icon: 'chat' },
  { route: 'sobre', label: 'Sobre', icon: 'info' },
];

const PAGE_TITLES = {
  inicio: 'Início',
  transparencia: 'ITCP',
  caixa: 'Livro caixa',
  assistente: 'Assistente',
  sobre: 'Sobre',
  admin: 'Painel da gestão',
};

const FRENTES_EQUIPES = ['Tainã', 'Agricultura', 'Loucura', 'Gênero', 'Rede'];
const FRENTES_GEPAS = ['GEPA 1', 'GEPA 2', 'GEPA 3', 'GEPA 4'];

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
  conferencia: [],
  reembolsos: [],
  caixa: null,
  filters: { tipo: 'todos', q: '', semTelegram: false, equipe: '', gepa: '' },
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

function mesCurtoAno(mes) {
  const match = /^(\d{4})-(\d{2})$/.exec(String(mes || ''));
  if (!match) return mes || '—';
  return `${MESES_CURTOS[Number(match[2]) - 1] || match[2]}/${match[1]}`;
}

/** Aceita "10", "10,5" ou "1.234,50" e devolve número (ou NaN). */
function parseValor(texto) {
  let t = String(texto || '').trim().replace(/[^\d.,]/g, '');
  if (t.includes(',')) t = t.replace(/\./g, '').replace(',', '.');
  return Number.parseFloat(t);
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
  return String(name || '').trim().split(/\s+/)[0] || 'ITCP';
}

/* --------------------------------------------------------------------------
   Tema claro / escuro (persistente)
   -------------------------------------------------------------------------- */

function currentTheme() {
  return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
}

function applyTheme(theme) {
  const root = document.documentElement;
  root.setAttribute('data-theme', theme);
  root.style.colorScheme = theme;
  const meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute('content', theme === 'dark' ? '#13171A' : '#F4F5F2');
}

function toggleTheme() {
  const next = currentTheme() === 'dark' ? 'light' : 'dark';
  try { localStorage.setItem(STORAGE_THEME, next); } catch (_) { /* modo privado */ }
  applyTheme(next);
  $$('[data-action="toggle-theme"]').forEach((btn) => {
    btn.innerHTML = themeIcon();
    btn.setAttribute('aria-label', themeLabel());
    btn.setAttribute('title', themeLabel());
  });
}

function themeIcon() {
  return icon(currentTheme() === 'dark' ? 'sun' : 'moon');
}

function themeLabel() {
  return currentTheme() === 'dark' ? 'Mudar para modo claro' : 'Mudar para modo escuro';
}

function themeToggleMarkup() {
  return `<button class="icon-btn" type="button" data-action="toggle-theme"
            aria-label="${themeLabel()}" title="${themeLabel()}">${themeIcon()}</button>`;
}

function statusMeta(status) {
  const map = {
    pago: { label: 'Quitado', cls: 'badge-paid' },
    pendente: { label: 'Pendente', cls: 'badge-pending' },
    aguardando_auditoria: { label: 'Aguardando confirmação', cls: 'badge-wait' },
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

const BASE_PATH = '/caixinhaitcp';

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body !== undefined) headers['Content-Type'] = 'application/json';

  const response = await fetch(`${BASE_PATH}${path}`, {
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
  return new RegExp(`^${BASE_PATH}/admin/?$`).test(window.location.pathname);
}

function goPublic(route = 'inicio') {
  window.location.href = `${BASE_PATH}/#/${route}`;
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
  const href = link ? ` href="${BASE_PATH}/#/inicio"` : '';
  return `<${tag} class="brand"${href} aria-label="grana.noiz, início">
    <span class="itcp-logo-slot" title="Espaço reservado para logo da ITCP">ITCP</span>
    <span class="brand-text">
      <span class="brand-word">grana.noiz</span>
      <span class="brand-slash">/</span>
      <span class="brand-sub">itcp</span>
    </span>
  </${tag}>`;
}

function renderShell(viewHtml) {
  const route = state.route;

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
    </aside>

    <header class="topbar">
      <div class="topbar-left">
        <div>
          <span class="topbar-title">grana.noiz / ITCP</span>
        </div>
      </div>
      <div class="topbar-right">
        ${themeToggleMarkup()}
      </div>
    </header>

    <main id="conteudo" class="main" aria-busy="${state.loading ? 'true' : 'false'}">
      <div class="content-wrap">
        ${viewHtml}
      </div>
    </main>

    <nav class="bottom-nav" aria-label="Navegação inferior">${bottomLinks}</nav>
  `;
}

function renderAdminLogin() {
  return `
    <div class="admin-page">
      <div class="admin-login-wrap">
        <div class="admin-login-top">${brandMarkup(true)}${themeToggleMarkup()}</div>
        <section class="card admin-login-card">
          <div class="lock-icon">${icon('lock')}</div>
          <span class="eyebrow" style="margin-top:16px">Acesso restrito</span>
          <h1 style="margin-top:6px">Painel da gestão</h1>
          <p class="subtitle">Entre com usuário e senha para conferir pagamentos e gerenciar a caixinha da ITCP.</p>
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
          <a class="card-link" href="${BASE_PATH}/#/inicio" style="margin-top:12px">← Voltar ao site</a>
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
          ${themeToggleMarkup()}
          <span class="badge badge-active" title="${esc(state.adminUser || 'gestão')}">Sessão ativa</span>
          <a class="btn btn-ghost btn-sm" href="${BASE_PATH}/#/inicio">
            ${icon('home')} Ver site
          </a>
          <button class="btn btn-ghost btn-sm" type="button" data-action="admin-logout">
            ${icon('unlock')} Sair
          </button>
        </div>
      </header>
      <main id="conteudo" class="admin-main" aria-busy="false">
        <div class="content-wrap">
          ${renderAdminDashboard()}
        </div>
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

function renderFrentePickerMarkup(inputName = 'frente', defaultFrente = 'Tainã') {
  const equipes = state.resumo?.frentes_reembolso?.equipes || FRENTES_EQUIPES;
  const gepas = state.resumo?.frentes_reembolso?.gepas || FRENTES_GEPAS;
  const isGepa = gepas.includes(defaultFrente);
  const initialGroup = isGepa ? 'gepa' : 'equipe';
  const initialFrente = defaultFrente || equipes[0] || 'Tainã';

  return `
    <div class="frente-picker" data-frente-picker>
      <input type="hidden" name="${esc(inputName)}" value="${esc(initialFrente)}" data-frente-input>
      <div class="seg-control" role="tablist" aria-label="Tipo de frente">
        <button type="button" class="seg-btn ${initialGroup === 'equipe' ? 'is-active' : ''}"
                data-action="select-frente-group" data-group="equipe">
          Equipes
        </button>
        <button type="button" class="seg-btn ${initialGroup === 'gepa' ? 'is-active' : ''}"
                data-action="select-frente-group" data-group="gepa">
          GEPAs
        </button>
      </div>
      <div class="frente-options ${initialGroup === 'equipe' ? '' : 'hidden'}" data-frente-list="equipe">
        ${equipes.map((f) => `
          <button type="button" class="frente-chip ${initialFrente === f ? 'is-active' : ''}"
                  data-action="select-frente-item" data-frente="${esc(f)}">${esc(f)}</button>`).join('')}
      </div>
      <div class="frente-options ${initialGroup === 'gepa' ? '' : 'hidden'}" data-frente-list="gepa">
        ${gepas.map((f) => `
          <button type="button" class="frente-chip ${initialFrente === f ? 'is-active' : ''}"
                  data-action="select-frente-item" data-frente="${esc(f)}">${esc(f)}</button>`).join('')}
      </div>
    </div>`;
}

function renderStatusReembolsoPickerMarkup(defaultPago = false) {
  return `
    <div class="status-picker" data-status-picker>
      <input type="hidden" name="ja_pago" value="${defaultPago ? '1' : '0'}" data-status-input>
      <div class="status-toggle-group" role="radiogroup" aria-label="Status do reembolso">
        <button type="button" class="status-opt is-pending ${!defaultPago ? 'is-active' : ''}"
                data-action="select-reembolso-status" data-paid="0">
          <span class="status-dot"></span>
          <span>Ainda não foi feito (pendente)</span>
        </button>
        <button type="button" class="status-opt is-paid ${defaultPago ? 'is-active' : ''}"
                data-action="select-reembolso-status" data-paid="1">
          <span class="status-dot"></span>
          <span>Já foi feito (pago)</span>
        </button>
      </div>
    </div>`;
}

function renderInicio() {
  const r = state.resumo;
  if (!r) return renderError('A API da caixinha não respondeu.');
  const m = state.membro;
  const ativosMes = r.mes_atual?.ativos || {};
  const totalAtivos = r.membros?.ativos || 0;
  const pagamentosMes = ativosMes.pagos || 0;

  const memberCard = m ? renderMemberCard(m, r) : `
    <section class="card member-entry-card">
      <div class="card-header">
        <div>
          <h2 class="card-title">Consultar pelo RA</h2>
          <p class="card-sub">Veja sua situação na caixinha e avise quando pagar.</p>
        </div>
      </div>
      <form data-form="buscar-ra" class="form-grid">
        <div class="field">
          <label for="ra-input">Seu RA</label>
          <input id="ra-input" name="ra" inputmode="numeric" autocomplete="off"
                 placeholder="Ex.: 248340" required>
        </div>
        <button class="btn btn-primary btn-block" type="submit">
          ${icon('search')} Consultar
        </button>
      </form>
    </section>`;

  const reembolsoCard = `
    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Pedir reembolso</h2>
          <p class="card-sub">Para gastos do cotidiano da ITCP (uber/transporte, lanche, materiais de oficina etc.).</p>
        </div>
        <button class="btn btn-primary btn-sm" type="button" data-action="open-reembolso">
          ${icon('plus')} Novo pedido
        </button>
      </div>
      ${m?.reembolsos?.length ? `
        <div class="list">
          ${m.reembolsos.slice(0, 4).map((rb) => {
            const st = rb.status === 'aprovado'
              ? { label: 'Já feito / Pago', cls: 'badge-paid' }
              : rb.status === 'rejeitado'
                ? { label: 'Recusado', cls: 'badge-ex' }
                : { label: 'Pendente (a receber)', cls: 'badge-wait' };
            return `
              <div class="list-row">
                <div class="list-main">
                  <div>
                    <div class="list-title">
                      <span class="frente-tag" style="margin-right:6px">${esc(rb.frente)}</span>
                      ${esc(rb.descricao)}
                    </div>
                    <span class="list-sub">${dateBR(rb.data_gasto)}</span>
                  </div>
                </div>
                <div class="list-right">
                  <span class="list-value">${brl(rb.valor)}</span>
                  <span class="badge ${st.cls}" style="margin-top:4px">${st.label}</span>
                </div>
              </div>`;
          }).join('')}
        </div>` : `
        <p class="field-hint">Escolha Equipe ou GEPA, informe valor, chave Pix e se o reembolso já foi feito ou está pendente.</p>`}
    </section>`;

  const pagosDoMembro = (m?.pagamentos || []).filter(
    (p) => p.status_pagamento === 'pago' || p.status_pagamento === 'aguardando_auditoria',
  );
  const movimentacoes = (m && pagosDoMembro.length) ? `
    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Histórico de pagamentos</h2>
          <p class="card-sub">Pagamentos já confirmados ou em conferência.</p>
        </div>
      </div>
      ${renderPagamentosMembro(m)}
    </section>` : '';

  return `
    <section class="page-head">
      <div class="page-head-row">
        <div>
          <h1>Olá, ${m ? esc(firstName(m.nome)) : 'ITCP'}</h1>
          <p class="subtitle">${m
            ? 'Sua situação na caixinha da ITCP.'
            : 'Caixinha da ITCP.'}</p>
        </div>
      </div>
    </section>

    <div class="home-grid">
      ${memberCard}
    </div>

    ${reembolsoCard}

    <div class="stat-grid stat-grid-2" style="margin-top:14px">
      <div class="stat">
        <span class="stat-label">Pessoas na ITCP</span>
        <span class="stat-value">${totalAtivos}</span>
        <span class="stat-hint">bolsistas ativos</span>
      </div>
      <div class="stat">
        <span class="stat-label">Pagamentos no mês</span>
        <span class="stat-value is-secondary">${pagamentosMes}</span>
        <span class="stat-hint">${pagamentosMes === 1 ? '1 pagamento feito este mês' : `${pagamentosMes} pagamentos feitos este mês`} · ${brl(ativosMes.valor_pago || 0)}</span>
      </div>
    </div>

    ${movimentacoes}`;
}

function renderMemberCard(m, r) {
  const isEx = Boolean(m.ex_bolsista);
  const pix = r.pix_chave || '';
  const pagamentos = m.pagamentos || [];
  const pendentes = pagamentos
    .filter((p) => p.status_pagamento === 'pendente')
    .sort((a, b) => String(a.mes).localeCompare(String(b.mes)));
  const totalAberto = Number(m.saldo_devedor || 0);
  const avisos = m.solicitacoes_aguardando || [];
  const aguardandoMes = pagamentos.filter((p) => p.status_pagamento === 'aguardando_auditoria');

  const reembolsosAReceber = (m.reembolsos || [])
    .filter((rb) => rb.status === 'aguardando')
    .reduce((acc, rb) => acc + Number(rb.valor || 0), 0);

  let periodoAberto = '';
  if (pendentes.length === 1) {
    periodoAberto = `Referente a ${mesCurtoAno(pendentes[0].mes)}`;
  } else if (pendentes.length > 1) {
    periodoAberto = `${pendentes.length} meses em aberto (${mesCurtoAno(pendentes[0].mes)} a ${mesCurtoAno(pendentes[pendentes.length - 1].mes)})`;
  }

  const abertoHtml = pendentes.length ? `
    <div class="debt-summary">
      <div class="debt-total">
        <span class="stat-label">Total em aberto</span>
        <span class="stat-value">${brl(totalAberto)}</span>
        <span class="debt-range">${esc(periodoAberto)}</span>
      </div>
    </div>` : `
    <div class="pending-note is-ok">
      ${icon('check')}
      <span>${isEx ? 'Sem pendências em aberto.' : 'Tudo em dia por aqui.'}</span>
    </div>`;

  let balancoHtml = '';
  if (reembolsosAReceber > 0 && totalAberto > 0) {
    const diff = Number((reembolsosAReceber - totalAberto).toFixed(2));
    let resumoFinal = 'Valores equivalentes (acerto zerado com a caixinha).';
    if (diff > 0) {
      resumoFinal = `Saldo líquido a receber da caixinha: ${brl(diff)}`;
    } else if (diff < 0) {
      resumoFinal = `Restante a pagar após abater seus reembolsos: ${brl(Math.abs(diff))}`;
    }
    balancoHtml = `
      <div class="balance-box">
        <div class="balance-head">
          <span>Balanço com reembolsos pendentes</span>
        </div>
        <div class="balance-grid">
          <span>Reembolsos a receber: <strong class="mono">${brl(reembolsosAReceber)}</strong></span>
          <span>Em aberto na caixinha: <strong class="mono">${brl(totalAberto)}</strong></span>
        </div>
        <div class="balance-result">${resumoFinal}</div>
      </div>`;
  } else if (reembolsosAReceber > 0) {
    balancoHtml = `
      <div class="balance-box">
        <div class="balance-head">
          <span>Reembolsos a receber</span>
          <span class="mono">${brl(reembolsosAReceber)}</span>
        </div>
        <div class="balance-grid">
          <span>Sem meses pendentes na caixinha.</span>
        </div>
      </div>`;
  }

  const avisosHtml = (avisos.length || aguardandoMes.length) ? `
    <div class="pending-note is-wait">
      ${icon('refresh')}
      <span>
        ${avisos.map((a) => `${brl(a.valor)} em ${dateBR(a.data_pagamento)}`).join(' · ')}
        ${aguardandoMes.length ? `${avisos.length ? ' · ' : ''}${aguardandoMes.map((p) => mesCurtoAno(p.mes)).join(', ')}` : ''}
        — aguardando confirmação.
      </span>
    </div>` : '';

  const formHtml = pendentes.length ? `
    <form data-form="solicitar-pagamento" class="solicitar-form" novalidate>
      <h3 class="form-title">Avisar pagamento</h3>
      <div class="form-grid two">
        <div class="field">
          <label for="pg-data">Data do pagamento</label>
          <input id="pg-data" name="data" type="date" value="${hojeISO()}" max="${hojeISO()}" required>
        </div>
        <div class="field">
          <label for="pg-valor">Valor pago (R$)</label>
          <input id="pg-valor" name="valor" inputmode="decimal" autocomplete="off"
                 placeholder="${totalAberto.toFixed(2).replace('.', ',')}" required>
        </div>
      </div>
      <div class="field">
        <label for="pg-obs">Observação ou comprovante (opcional)</label>
        <input id="pg-obs" name="observacao" maxlength="300" autocomplete="off"
               placeholder="Ex.: Pix de 05/11, link do comprovante">
      </div>
      <button class="btn btn-primary btn-block" type="submit">
        ${icon('receipt')} Avisar pagamento
      </button>
      <span class="field-hint">O valor abate primeiro os meses mais antigos.</span>
    </form>` : '';

  return `
    <section class="card member-card">
      <div class="card-header">
        <div class="member-main">
          <div class="avatar ${isEx ? 'is-ex' : ''}">${esc(initials(m.nome))}</div>
          <div class="member-info">
            <h2 class="card-title" style="font-size:1rem">${esc(m.nome)}</h2>
            <p class="card-sub">RA ${esc(m.ra || '—')}</p>
          </div>
        </div>
        <button class="card-link" type="button" data-action="clear-member">Trocar</button>
      </div>

      ${abertoHtml}

      ${balancoHtml}

      ${pix ? `
        <div class="pix-box" style="margin-top:12px">
          <div class="pix-box-main">
            ${icon('copy')}
            <div style="min-width:0">
              <span class="pix-label">Chave Pix</span>
              <span class="pix-value" title="${esc(pix)}">${esc(pix)}</span>
            </div>
          </div>
          <button class="btn btn-secondary btn-sm" type="button" data-action="copy-pix">
            ${icon('copy')} Copiar
          </button>
        </div>` : ''}

      ${avisosHtml}

      ${formHtml}
    </section>`;
}

function renderPagamentosMembro(m) {
  const pagamentos = (m.pagamentos || [])
    .filter((p) => p.status_pagamento === 'pago' || p.status_pagamento === 'aguardando_auditoria')
    .slice(0, 8);
  if (!pagamentos.length) {
    return `<div class="empty">${icon('receipt')}<div>Nenhum pagamento confirmado ainda.</div></div>`;
  }
  return `
    <div class="list">
      ${pagamentos.map((p) => {
        const meta = statusMeta(p.status_pagamento);
        const iconClass = p.status_pagamento === 'pago' ? 'is-paid' : 'is-wait';
        return `
          <div class="list-row">
            <div class="list-main">
              <div class="list-icon ${iconClass}">
                ${icon(p.status_pagamento === 'pago' ? 'check' : 'receipt')}
              </div>
              <div>
                <div class="list-title">${mesLabel(p.mes)}</div>
                <span class="list-sub">${p.data_pagamento
                  ? `Confirmado em ${dateBR(p.data_pagamento)}`
                  : 'Confirmado no histórico'}</span>
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
  const conferencia = state.conferencia || [];
  const reembolsos = state.reembolsos || [];
  const reembolsosPendentes = reembolsos.filter((rb) => rb.status === 'aguardando');
  const caixa = state.caixa || {};
  const ativosMes = r.mes_atual?.ativos || {};
  const pagamentosMes = ativosMes.pagos || 0;
  const telegramOk = Boolean(r.telegram_habilitado);
  const comTelegram = state.membros.filter((m) => m.telegram_id && !m.ex_bolsista).length;
  const totalParaConferir = conferencia.length + reembolsosPendentes.length;

  const adminActions = `
    <div class="admin-actions">
      <button class="btn btn-primary" type="button" data-action="generate">
        ${icon('calendar')} Gerar cobranças do mês
      </button>
      <button class="btn btn-ghost" type="button" data-action="open-reembolso">
        ${icon('plus')} Pedido de reembolso
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
          <h1>Gestão da ITCP</h1>
          <p class="subtitle">Membros, conferência de pagamentos, reembolsos e livro caixa.</p>
        </div>
      </div>
      ${adminActions}
    </section>

    <div class="stat-grid">
      <div class="stat">
        <span class="stat-label">Na ITCP</span>
        <span class="stat-value">${r.membros?.ativos || 0}</span>
        <span class="stat-hint">bolsistas ativos</span>
      </div>
      <div class="stat">
        <span class="stat-label">Ex-bolsistas</span>
        <span class="stat-value">${r.membros?.ex_bolsistas || 0}</span>
        <span class="stat-hint">no histórico</span>
      </div>
      <div class="stat">
        <span class="stat-label">Pagamentos no mês</span>
        <span class="stat-value is-secondary">${pagamentosMes}</span>
        <span class="stat-hint">${pagamentosMes === 1 ? '1 pagamento feito este mês' : `${pagamentosMes} pagamentos feitos este mês`} · ${brl(ativosMes.valor_pago || 0)}</span>
      </div>
      <div class="stat">
        <span class="stat-label">Para conferir</span>
        <span class="stat-value ${totalParaConferir ? 'is-primary' : ''}">${totalParaConferir}</span>
        <span class="stat-hint">${conferencia.length} pagto(s) · ${reembolsosPendentes.length} reembolso(s)</span>
      </div>
    </div>

    <div class="grid-2" style="margin-top:14px">
      <section class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Lembrete no Telegram</h2>
            <p class="card-sub">Envia aviso para quem está com mês em aberto e Telegram vinculado.</p>
          </div>
          <button class="btn ${telegramOk ? 'btn-primary' : 'btn-ghost'} btn-sm"
                  type="button" data-action="disparar-telegram" ${telegramOk ? '' : 'disabled'}>
            ${icon('send')} Disparar
          </button>
        </div>
        <p class="field-hint">
          ${telegramOk
            ? `${comTelegram} pessoa(s) com Telegram vinculado.`
            : 'Configure TELEGRAM_BOT_TOKEN no .env para habilitar o disparo.'}
        </p>
      </section>

      <section class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Livro caixa</h2>
            <p class="card-sub">Saldo ${brl(caixa.saldo || 0)} · ${brl(caixa.total_despesas || 0)} em saídas/reembolsos.</p>
          </div>
          <button class="btn btn-ghost btn-sm" type="button" data-action="open-expense">
            ${icon('plus')} Lançar saída
          </button>
        </div>
        ${renderDespesas((caixa.despesas_recentes || []).slice(0, 3))}
      </section>
    </div>

    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Pedidos de reembolso (Equipes e GEPAs)</h2>
          <p class="card-sub">Gastos do cotidiano da ITCP. Ao aprovar, o valor entra automaticamente nas saídas da caixinha.</p>
        </div>
        <button class="card-link" type="button" data-action="open-reembolso">${icon('plus')} Novo pedido</button>
      </div>
      ${renderReembolsosAdmin(reembolsos)}
    </section>

    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Conferência de pagamentos</h2>
          <p class="card-sub">Avisos enviados pelo bot ou pelo site. Ao confirmar, o valor abate os meses mais antigos primeiro.</p>
        </div>
        <button class="card-link" type="button" data-action="refresh">${icon('refresh')} Atualizar</button>
      </div>
      ${renderConferencia(conferencia)}
    </section>

    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Pessoas cadastradas</h2>
          <p class="card-sub" id="member-count">${state.membros.length} cadastro(s)</p>
        </div>
        <a class="btn btn-ghost btn-sm" href="${BASE_PATH}/api/admin/membros/ex-bolsistas.csv">
          ${icon('download')} Exportar ex-bolsistas
        </a>
      </div>
      ${renderToolbar(true)}
      <div id="member-list">${renderMemberRows()}</div>
    </section>`;
}

function renderTransparencia() {
  const r = state.resumo || {};
  const ativosMes = r.mes_atual?.ativos || {};
  const confirmadas = ativosMes.pagos || 0;

  return `
    <section class="page-head">
      <div class="page-head-row">
        <div>
          <h1>ITCP</h1>
          <p class="subtitle">Quem faz parte da ITCP hoje.</p>
        </div>
      </div>
    </section>

    <div class="stat-grid stat-grid-2">
      <div class="stat">
        <span class="stat-label">Pessoas na ITCP</span>
        <span class="stat-value">${r.membros?.ativos || 0}</span>
        <span class="stat-hint">bolsistas ativos</span>
      </div>
      <div class="stat">
        <span class="stat-label">Pagamentos no mês</span>
        <span class="stat-value is-secondary">${confirmadas}</span>
        <span class="stat-hint">${confirmadas === 1 ? '1 pagamento feito este mês' : `${confirmadas} pagamentos feitos este mês`}</span>
      </div>
    </div>

    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Pessoas ativas na ITCP</h2>
          <p class="card-sub" id="member-count">${state.membros.length} pessoa(s)</p>
        </div>
      </div>
      ${renderToolbar(false)}
      <div id="member-list">${renderMembrosNeutros()}</div>
    </section>`;
}

function renderReembolsosAdmin(itens) {
  if (!itens || !itens.length) {
    return `<div class="empty">${icon('check')}<div>Nenhum pedido de reembolso registrado.</div></div>`;
  }
  return `
    <div class="list">
      ${itens.map((rb) => {
        const isPaid = rb.status === 'aprovado';
        const isRej = rb.status === 'rejeitado';
        const st = isPaid
          ? { label: 'Já feito / Pago', cls: 'badge-paid' }
          : isRej
            ? { label: 'Recusado', cls: 'badge-ex' }
            : { label: 'Pendente (não feito)', cls: 'badge-wait' };
        return `
          <div class="confer-row">
            <div class="list-main">
              <div>
                <div class="list-title">
                  <span class="frente-tag" style="margin-right:6px">${esc(rb.frente)}</span>
                  ${esc(rb.descricao)}
                </div>
                <span class="list-sub">
                  ${esc(rb.data_gasto ? dateBR(rb.data_gasto) : 'sem data')}
                  ${rb.solicitante_nome ? ` · ${esc(rb.solicitante_nome)}` : ''}
                  ${rb.ra ? ` (RA ${esc(rb.ra)})` : ''}
                </span>
                ${rb.pix_chave ? `<span class="list-sub">Chave Pix: ${esc(rb.pix_chave)}</span>` : ''}
                ${rb.comprovante ? `<span class="list-sub">Obs./comprovante: ${esc(rb.comprovante)}</span>` : ''}
                ${rb.nota_gestao ? `<span class="list-sub">Nota da gestão: ${esc(rb.nota_gestao)}</span>` : ''}
              </div>
            </div>
            <div class="member-amount">
              <span class="value">${brl(rb.valor)}</span>
              <span class="badge ${st.cls}" style="margin-top:4px">${st.label}</span>
            </div>
            <div class="confer-actions">
              ${!isPaid ? `
                <button class="btn btn-secondary btn-sm" type="button"
                        data-action="conferir-reembolso" data-id="${rb.id}" data-decision="1">
                  ${icon('check')} Marcar pago
                </button>` : `
                <button class="btn btn-ghost btn-sm" type="button"
                        data-action="toggle-reembolso-pendente" data-id="${rb.id}">
                  Marcar pendente
                </button>`}
              ${!isRej ? `
                <button class="btn btn-danger btn-sm" type="button"
                        data-action="conferir-reembolso" data-id="${rb.id}" data-decision="0">
                  ${icon('x')} Recusar
                </button>` : ''}
            </div>
          </div>`;
      }).join('')}
    </div>`;
}

function renderConferencia(itens) {
  if (!itens.length) {
    return `<div class="empty">${icon('check')}<div>Nada aguardando conferência.</div></div>`;
  }
  return `
    <div class="list">
      ${itens.map((item) => `
        <div class="confer-row">
          <div class="list-main">
            <div class="list-icon is-wait">${icon('refresh')}</div>
            <div>
              <div class="list-title">${esc(item.nome)}</div>
              <span class="list-sub">
                RA ${esc(item.ra || '—')} ·
                ${item.tipo === 'valor' ? 'abate os meses mais antigos' : mesLabel(item.mes)} ·
                ${esc(item.data_pagamento ? dateBR(item.data_pagamento) : 'sem data')}
              </span>
              ${item.observacao ? `<span class="list-sub">${esc(item.observacao)}</span>` : ''}
            </div>
          </div>
          <div class="member-amount">
            <span class="value">${brl(item.valor_pago)}</span>
            <span class="label">Aguardando</span>
          </div>
          <div class="confer-actions">
            <button class="btn btn-secondary btn-sm" type="button"
                    data-action="conferir" data-id="${item.id}" data-tipo="${item.tipo}" data-decision="1">
              ${icon('check')} Confirmar
            </button>
            <button class="btn btn-danger btn-sm" type="button"
                    data-action="conferir" data-id="${item.id}" data-tipo="${item.tipo}" data-decision="0">
              ${icon('x')} Recusar
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
        ['ativos', 'Na ITCP'],
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
      ${admin ? `
        <div class="form-inline member-front-filters">
          <div class="field">
            <label for="member-equipe">Equipe</label>
            <select id="member-equipe" data-filter="equipe">
              <option value="">Todas</option>
              <option value="Sem equipe" ${f.equipe === 'Sem equipe' ? 'selected' : ''}>Sem equipe</option>
              ${['Tainã','Agricultura','Loucura','Gênero','Rede'].map((v) => `<option value="${esc(v)}" ${f.equipe === v ? 'selected' : ''}>${esc(v)}</option>`).join('')}
            </select>
          </div>
          <div class="field">
            <label for="member-gepa">GEPA</label>
            <select id="member-gepa" data-filter="gepa">
              <option value="">Todos</option>
              <option value="Sem GEPA" ${f.gepa === 'Sem GEPA' ? 'selected' : ''}>Sem GEPA</option>
              ${['GEPA 1','GEPA 2','GEPA 3','GEPA 4'].map((v) => `<option value="${esc(v)}" ${f.gepa === v ? 'selected' : ''}>${esc(v)}</option>`).join('')}
            </select>
          </div>
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
    if (f.equipe) {
      const equipe = (m.equipe || '').trim();
      if (f.equipe === 'Sem equipe' ? Boolean(equipe) : equipe !== f.equipe) return false;
    }
    if (f.gepa) {
      const gepa = (m.gepa || '').trim();
      if (f.gepa === 'Sem GEPA' ? Boolean(gepa) : gepa !== f.gepa) return false;
    }
    if (!termo) return true;
    const alvo = `${m.nome || ''} ${m.pronomes || ''} ${m.ra || ''} ${m.modalidade || m.modalidade_bolsa || ''} ${m.equipe || ''} ${m.gepa || ''}`.toLowerCase();
    return alvo.includes(termo);
  });
}

function renderMemberRows() {
  const lista = membrosFiltrados();
  if (!lista.length) {
    return `<div class="empty">${icon('users')}<div>Ninguém encontrado com esse filtro.</div></div>`;
  }
  return `<div class="member-list">
    ${lista.map((m) => {
      const isEx = Boolean(m.ex_bolsista);
      const frente = m.equipe || m.gepa || (m.equipe === '' && m.gepa === '' ? 'Sem equipe / Sem GEPA' : 'Sem equipe / Sem GEPA');
      const modalidade = m.modalidade || m.modalidade_bolsa || 'Sem modalidade';
      const meta = [
        m.ra ? `RA ${m.ra}` : 'Sem RA',
        modalidade,
        frente,
      ].join(' • ');
      return `
        <div class="member-row">
          <div class="member-main">
            <div class="avatar ${isEx ? 'is-ex' : ''}">${esc(initials(m.nome))}</div>
            <div class="member-info">
              <div class="member-name">${esc(m.nome)}${m.pronomes ? ` <span class="name-pronouns">(${esc(m.pronomes)})</span>` : ''}</div>
              <div class="member-meta">${esc(meta)}</div>
            </div>
          </div>
          <div class="member-side">
            <div class="member-amount">
              <span class="value">${brl(m.saldo_devedor || 0)}</span>
              <span class="label">${m.cotas_pendentes || 0} mês(es) em aberto</span>
            </div>
          </div>
          ${state.admin ? `
            <div class="member-actions">
              <button class="btn btn-ghost btn-sm" type="button"
                      data-action="member-detail" data-id="${m.id}">
                ${icon('info')} Abrir ficha
              </button>
            </div>` : ''}
        </div>`;
    }).join('')}
  </div>`;
}

function tagMembro(m) {
  return m.recem_ingresso ? 'Entrou recentemente' : 'Na ITCP';
}

function renderMembrosNeutros() {
  const lista = membrosFiltrados().filter((m) => !m.ex_bolsista);
  if (!lista.length) {
    return `<div class="empty">${icon('users')}<div>Ninguém encontrado com esse nome.</div></div>`;
  }
  return `<div class="member-list">
    ${lista.map((m) => `
      <div class="member-row neutral">
        <div class="member-main">
          <div class="avatar">${esc(initials(m.nome))}</div>
          <div class="member-info">
            <div class="member-name">${esc(m.nome)}</div>
            <span class="member-tag ${m.recem_ingresso ? 'is-new' : ''}">${tagMembro(m)}</span>
          </div>
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
  if (count) count.textContent = state.adminRoute
    ? `${membrosFiltrados().length} cadastro(s)`
    : `${membrosFiltrados().length} pessoa(s)`;
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

  const porCategoria = c.despesas_por_categoria || [];
  const pendentesReembolso = c.reembolsos_pendentes || [];

  return `
    <section class="page-head">
      <div class="page-head-row">
        <div>
          <h1>Livro caixa</h1>
          <p class="subtitle">Reembolsos, despesas e entradas da caixinha da ITCP.</p>
        </div>
        <div class="btn-row">
          <button class="btn btn-primary btn-sm" type="button" data-action="open-reembolso">
            ${icon('plus')} Pedir reembolso
          </button>
          <button class="icon-btn" type="button" data-action="refresh" aria-label="Atualizar">
            ${icon('refresh')}
          </button>
        </div>
      </div>
    </section>

    <section class="card">
      <div class="card-header">
        <div>
          <span class="stat-label">Saldo do livro caixa</span>
          <div class="money-lg ${c.saldo >= 0 ? 'text-secondary' : 'text-error'}">${brl(c.saldo)}</div>
          <p class="card-sub" style="margin-top:4px">
            ${brl(c.total_pago)} recebidos · ${brl(c.total_despesas)} em reembolsos e despesas
          </p>
        </div>
        <span class="badge ${c.saldo >= 0 ? 'badge-active' : 'badge-ex'}">
          ${c.saldo >= 0 ? 'Positivo' : 'Negativo'}
        </span>
      </div>
      <div class="grid-2">
        <div class="stat">
          <span class="stat-label">Saídas em ${mesLabel(c.mes)}</span>
          <span class="stat-value is-tertiary">- ${brl(c.despesas_mes)}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Entradas em ${mesLabel(c.mes)}</span>
          <span class="stat-value is-secondary">+ ${brl(c.pago_mes)}</span>
        </div>
      </div>
    </section>

    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Reembolsos e despesas da caixinha</h2>
          <p class="card-sub">Saídas aprovadas para equipes, GEPAs e atividades da ITCP.</p>
        </div>
        <button class="card-link" type="button" data-action="open-reembolso">
          ${icon('plus')} Pedir reembolso
        </button>
      </div>
      ${porCategoria.length ? `
        <div class="expense-cats" style="margin-bottom:14px">
          ${porCategoria.map((cat) => `
            <div class="expense-cat-item">
              <div class="expense-cat-head">
                <span class="frente-tag">${esc(cat.categoria)}</span>
                <span class="expense-cat-count">${cat.quantidade} saída(s)</span>
              </div>
              <span class="expense-cat-val">- ${brl(cat.total)}</span>
            </div>`).join('')}
        </div>` : ''}
      ${renderDespesas(c.despesas_recentes)}
      ${pendentesReembolso.length ? `
        <div class="pending-block" style="margin-top:12px">
          <div class="pending-head">
            <span class="small">Reembolsos pendentes — ainda não feitos (${pendentesReembolso.length})</span>
          </div>
          <div class="list">
            ${pendentesReembolso.map((rb) => `
              <div class="list-row">
                <div class="list-main">
                  <div>
                    <div class="list-title">
                      <span class="frente-tag" style="margin-right:6px">${esc(rb.frente)}</span>
                      ${esc(rb.descricao)}
                    </div>
                    <span class="list-sub">${dateBR(rb.data_gasto)}${rb.solicitante_nome ? ` · ${esc(rb.solicitante_nome)}` : ''}</span>
                  </div>
                </div>
                <div class="list-right">
                  <span class="list-value">${brl(rb.valor)}</span>
                  <span class="badge badge-wait" style="margin-top:4px">Pendente</span>
                </div>
              </div>`).join('')}
          </div>
        </div>` : ''}
    </section>

    <div class="grid-2" style="margin-top:14px">
      <section class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Arrecadação por mês</h2>
            <p class="card-sub">Valor recebido no mês em que o pagamento foi registrado.</p>
          </div>
          <div class="chart-legend"><span><i class="legend-dot"></i>Recebido</span></div>
        </div>
        <div class="chart" role="img" aria-label="Gráfico de arrecadação mensal">${barras}</div>
      </section>

      <section class="card">
        <div class="card-header">
          <div>
            <h2 class="card-title">Pagamentos recebidos</h2>
            <p class="card-sub">Entradas confirmadas recentemente.</p>
          </div>
        </div>
        ${renderPagamentosRecentes(c.pagamentos_recentes)}
      </section>
    </div>`;
}

function renderPagamentosRecentes(itens) {
  if (!itens?.length) {
    return `<div class="empty">${icon('receipt')}<div>Nenhum pagamento recebido ainda.</div></div>`;
  }
  return `<div class="list">
    ${itens.map((p) => `
      <div class="list-row">
        <div class="list-main">
          <div class="list-icon is-paid">${icon('check')}</div>
          <div>
            <div class="list-title">Pagamento recebido</div>
            <span class="list-sub">
              ${p.data_pagamento ? `Pago em ${dateBR(p.data_pagamento)} (ref. ${mesShort(p.mes)})` : `${mesLabel(p.mes)} · histórico`}
            </span>
          </div>
        </div>
        <div class="list-right">
          <span class="list-value text-secondary">+ ${brl(p.valor_pago)}</span>
        </div>
      </div>`).join('')}
  </div>`;
}

function renderDespesas(itens) {
  if (!itens?.length) {
    return `<div class="empty">${icon('wallet')}<div>Nenhum reembolso ou despesa registrado ainda.</div></div>`;
  }
  return `<div class="list">
    ${itens.map((d) => `
      <div class="list-row">
        <div class="list-main">
          <div class="list-icon is-expense">${icon('receipt')}</div>
          <div>
            <div class="list-title">
              ${d.categoria ? `<span class="frente-tag" style="margin-right:6px">${esc(d.categoria)}</span>` : ''}
              ${esc(d.descricao)}
            </div>
            <span class="list-sub">${dateBR(d.data)}${d.comprovante ? ` · ${esc(d.comprovante)}` : ''}</span>
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
      text: 'Oi! Sou o assistente da caixinha da ITCP. Posso consultar suas pendências, os pagamentos do mês, o saldo do caixa e a chave Pix.',
      time: new Date(),
    });
  }
  return `
    <section class="page-head">
      <div class="page-head-row">
        <div>
          <h1>Assistente</h1>
          <p class="subtitle">Tire dúvidas sobre a caixinha da ITCP.</p>
        </div>
      </div>
    </section>

    <section class="card chat-card">
      <div class="chat-log" id="chat-log" aria-live="polite">
        ${state.chat.map(renderMensagem).join('')}
      </div>
      <div class="suggestions" id="chat-suggestions">
        ${['Quanto eu devo?', 'Pagamentos deste mês', 'Qual o saldo?', 'Como pagar?', 'Próxima cobrança']
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

function renderSobre() {
  return `
    <section class="page-head">
      <div class="page-head-row">
        <div>
          <h1>Sobre o grana.noiz</h1>
          <p class="subtitle">Transparência e autogestão financeira para coletivos, movimentos e organizações populares.</p>
        </div>
      </div>
    </section>

    <section class="card">
      <div class="card-header">
        <div>
          <h2 class="card-title">O que é o projeto</h2>
          <p class="card-sub">Ferramenta aberta construída a partir da experiência da caixinha da ITCP/Unicamp.</p>
        </div>
      </div>
      <div class="about-prose">
        <p>
          O <strong>grana.noiz</strong> é uma plataforma leve de gestão e transparência financeira pensada para o cotidiano de coletivos autônomos, incubadoras populares, cooperativas e movimentos sociais.
        </p>
        <p>
          O objetivo é organizar contribuições mensais, pedidos de reembolso de equipes e frentes de trabalho, conciliação simples e prestação de contas do livro caixa — sem expor dívidas individuais publicamente e sem depender de planilhas confusas ou sistemas empresariais fechados.
        </p>
      </div>
    </section>

    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Software Livre e Licença AGPL-3.0</h2>
          <p class="card-sub">Autonomia tecnológica, código auditável e sem aprisionamento proprietário.</p>
        </div>
        <span class="frente-tag">GNU AGPLv3</span>
      </div>
      <div class="about-prose">
        <p>
          Este projeto é <strong>software livre e de código aberto</strong>, distribuído sob a licença <strong>GNU Affero General Public License v3.0 (AGPL-3.0)</strong>. Na prática, isso garante quatro liberdades fundamentais para qualquer pessoa ou coletivo:
        </p>
        <ul class="about-list">
          <li><strong>Usar livremente:</strong> qualquer coletivo, grupo ou organização popular pode rodar o sistema para sua própria caixinha, sem custos de licença ou restrições.</li>
          <li><strong>Estudar e auditar:</strong> todo o código-fonte é público, permitindo verificar como os cálculos, os abatimentos e os dados são tratados.</li>
          <li><strong>Adaptar à realidade local:</strong> você pode modificar textos, regras, frentes, valores e fluxos para as necessidades da sua organização.</li>
          <li><strong>Compartilhar melhorias:</strong> a licença AGPL-3.0 protege o bem comum — melhorias e versões disponibilizadas em rede permanecem livres para toda a comunidade.</li>
        </ul>
      </div>
    </section>

    <section class="card" style="margin-top:14px">
      <div class="card-header">
        <div>
          <h2 class="card-title">Repositório oficial e como contribuir</h2>
          <p class="card-sub">Código aberto no GitHub para auditar, sugerir melhorias ou enviar código.</p>
        </div>
      </div>
      <div class="about-prose">
        <p>
          Toda pessoa interessada é bem-vinda para inspecionar o código, abrir <em>issues</em> relatando problemas ou ideias, melhorar a documentação e enviar <em>pull requests</em>.
        </p>
        <div class="pix-box" style="margin-top:4px">
          <div class="pix-box-main">
            ${icon('link')}
            <div style="min-width:0">
              <span class="pix-label">Repositório no GitHub</span>
              <span class="pix-value">https://github.com/joao-asp/grana.noiz</span>
            </div>
          </div>
          <a class="btn btn-primary btn-sm" href="https://github.com/joao-asp/grana.noiz"
             target="_blank" rel="noopener noreferrer">
            Acessar GitHub
          </a>
        </div>
      </div>
    </section>`;
}

function renderView() {
  if (state.loading) return renderLoading();
  switch (state.route) {
    case 'transparencia': return renderTransparencia();
    case 'caixa': return renderCaixa();
    case 'assistente': return renderAssistente();
    case 'sobre': return renderSobre();
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

async function loadConferencia() {
  const data = await api('/api/admin/conferencia');
  state.conferencia = data.conferencia || [];
}

async function loadReembolsos() {
  const data = await api('/api/admin/reembolsos');
  state.reembolsos = data.reembolsos || [];
}

async function loadCaixa() {
  state.caixa = await api('/api/caixa');
}

async function loadAdminData() {
  await Promise.all([fetchResumo(), loadMembros(), loadConferencia(), loadReembolsos(), loadCaixa()]);
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
  state.conferencia = [];
  state.reembolsos = [];
  state.caixa = null;
  state.resumo = null;
  state.filters = { tipo: 'todos', q: '', semTelegram: false, equipe: '', gepa: '' };
  toast('Sessão encerrada.', 'info');
  render();
}

function openModal({ title, subtitle = '', body, submitLabel = 'Confirmar', danger = false, hideCancel = false, onSubmit }) {
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
            ${hideCancel ? '' : '<button class="btn btn-ghost" type="button" data-action="close-modal">Cancelar</button>'}
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
    title: 'Nova pessoa na ITCP',
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
    subtitle: 'Somente bolsistas ativos na ITCP recebem novas cobranças.',
    submitLabel: 'Gerar cobranças',
    body: `<p class="small">Os lançamentos pendentes de ${mesLabel(mes)} serão criados para todas as pessoas ativas. Ex-bolsistas ficam de fora.</p>`,
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
        Quem está em dia não recebe. Nada é marcado como pago automaticamente.
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

function openConferencia(item, aprovado) {
  const detalhe = item.tipo === 'valor'
    ? `${brl(item.valor_pago)} · ${item.data_pagamento ? dateBR(item.data_pagamento) : 'sem data'}`
    : `${mesLabel(item.mes)} · ${brl(item.valor_pago)}`;
  openModal({
    title: aprovado ? 'Confirmar pagamento' : 'Recusar aviso',
    subtitle: `${item.nome} · ${detalhe}`,
    submitLabel: aprovado ? 'Confirmar' : 'Recusar',
    danger: !aprovado,
    body: `
      ${aprovado && item.tipo === 'valor' ? `
        <p class="small">O valor será abatido do saldo em aberto, começando pelos meses mais antigos.</p>` : ''}
      <div class="field">
        <label for="confer-obs">Observação (opcional)</label>
        <textarea id="confer-obs" name="observacao"
          placeholder="${aprovado ? 'Ex.: conferido no extrato de 05/10' : 'Ex.: valor não localizado no extrato'}"></textarea>
      </div>`,
    onSubmit: async (dados) => {
      const resultado = await api(`/api/admin/conferencia/${item.id}`, {
        method: 'POST',
        body: { aprovar: aprovado, observacao: dados.observacao || null, tipo: item.tipo },
      });
      if (!aprovado) {
        toast('Aviso recusado.', 'info');
      } else if (item.tipo === 'valor') {
        const quitadas = (resultado.meses_quitados || []).map(mesCurtoAno);
        const partes = [`${brl(resultado.aplicado)} abatidos`];
        if (quitadas.length) partes.push(`quitou ${quitadas.join(', ')}`);
        if (resultado.parcial) {
          partes.push(`${mesCurtoAno(resultado.parcial.mes)} ainda deve ${brl(resultado.parcial.restante)}`);
        }
        toast(partes.join(' · '));
      } else {
        toast('Pagamento confirmado.');
      }
      await refreshData();
    },
  });
}

function openPedidoReembolso() {
  const nomeMembro = state.membro?.nome || '';
  openModal({
    title: 'Pedir reembolso',
    subtitle: 'Gastos do cotidiano da ITCP (uber/transporte, lanche, materiais de oficina etc.).',
    submitLabel: 'Salvar reembolso',
    body: `
      <div class="field">
        <label>Frente (Equipe ou GEPA)</label>
        ${renderFrentePickerMarkup('frente', 'Tainã')}
      </div>

      <div class="form-grid two">
        <div class="field">
          <label for="rb-solicitante">Seu nome</label>
          <input id="rb-solicitante" name="solicitante" maxlength="100" autocomplete="name"
                 value="${esc(nomeMembro)}" placeholder="Quem está pedindo" required>
        </div>
        <div class="field">
          <label for="rb-pix">Chave Pix para receber</label>
          <input id="rb-pix" name="pix_chave" maxlength="140" autocomplete="off"
                 placeholder="CPF, e-mail, celular ou aleatória" required>
        </div>
      </div>

      <div class="form-grid two">
        <div class="field">
          <label for="rb-valor">Valor (R$)</label>
          <input id="rb-valor" name="valor" inputmode="decimal" autocomplete="off"
                 placeholder="Ex.: 28,50" required>
        </div>
        <div class="field">
          <label for="rb-data">Data do gasto</label>
          <input id="rb-data" name="data" type="date" value="${hojeISO()}" max="${hojeISO()}" required>
        </div>
      </div>

      <div class="field">
        <label for="rb-desc">Descrição curta</label>
        <input id="rb-desc" name="descricao" required maxlength="140" autocomplete="off"
               placeholder="Ex.: uber para atividade, lanche da reunião">
      </div>

      <div class="field">
        <label>Status do reembolso</label>
        ${renderStatusReembolsoPickerMarkup(false)}
      </div>

      <div class="field">
        <label for="rb-comp">Observação ou comprovante (opcional)</label>
        <input id="rb-comp" name="comprovante" maxlength="300" autocomplete="off"
               placeholder="Link do comprovante ou observação complementar">
      </div>`,
    onSubmit: async (dados) => {
      const solicitante = String(dados.solicitante || '').trim();
      if (!solicitante) {
        throw new Error('Informe seu nome.');
      }
      const pixChave = String(dados.pix_chave || '').trim();
      if (!pixChave) {
        throw new Error('Informe a chave Pix para o reembolso.');
      }
      const valor = parseValor(dados.valor);
      if (!Number.isFinite(valor) || valor <= 0) {
        throw new Error('Informe um valor válido maior que zero.');
      }
      const jaPago = dados.ja_pago === '1';
      const resultado = await api('/api/reembolsos', {
        method: 'POST',
        body: {
          ra: state.ra || null,
          solicitante,
          pix_chave: pixChave,
          frente: dados.frente,
          valor,
          data: dados.data || hojeISO(),
          descricao: dados.descricao,
          comprovante: dados.comprovante || null,
          ja_pago: jaPago,
        },
      });
      if (resultado.membro) state.membro = resultado.membro;
      toast(resultado.mensagem || 'Reembolso registrado.');
      await refreshData();
    },
  });
}

function openConferenciaReembolso(item, aprovado) {
  openModal({
    title: aprovado ? 'Confirmar pagamento de reembolso' : 'Recusar pedido de reembolso',
    subtitle: `${item.frente} · ${brl(item.valor)} · ${item.descricao}`,
    submitLabel: aprovado ? 'Marcar como pago' : 'Recusar',
    danger: !aprovado,
    body: `
      ${item.pix_chave ? `
        <div class="pix-box">
          <div class="pix-box-main">
            ${icon('copy')}
            <div style="min-width:0">
              <span class="pix-label">Chave Pix de ${esc(item.solicitante_nome || 'solicitante')}</span>
              <span class="pix-value">${esc(item.pix_chave)}</span>
            </div>
          </div>
        </div>` : ''}
      ${aprovado ? `
        <p class="small">O reembolso será marcado como feito/pago e entrará nas saídas e despesas do livro caixa (${esc(item.frente)}).</p>` : ''}
      <div class="field">
        <label for="rb-nota">Observação da gestão (opcional)</label>
        <textarea id="rb-nota" name="observacao"
          placeholder="${aprovado ? 'Ex.: pago via Pix em 18/11' : 'Ex.: comprovante ausente'}"></textarea>
      </div>`,
    onSubmit: async (dados) => {
      await api(`/api/admin/reembolsos/${item.id}`, {
        method: 'POST',
        body: { aprovar: aprovado, observacao: dados.observacao || null },
      });
      toast(
        aprovado
          ? `Reembolso de ${brl(item.valor)} (${item.frente}) marcado como pago.`
          : 'Pedido de reembolso recusado.',
        aprovado ? 'success' : 'info',
      );
      await refreshData();
    },
  });
}

async function marcarReembolsoPendente(reembolsoId) {
  try {
    await api(`/api/admin/reembolsos/${reembolsoId}`, {
      method: 'POST',
      body: { status: 'aguardando' },
    });
    toast('Reembolso marcado como pendente (ainda não feito).', 'info');
    await refreshData();
  } catch (error) {
    toast(error.message || 'Não foi possível alterar o status.', 'error');
  }
}

function openNovaDespesa() {
  openModal({
    title: 'Nova saída / despesa',
    subtitle: 'Lançamento direto no livro caixa da ITCP.',
    submitLabel: 'Lançar saída',
    body: `
      <div class="field">
        <label>Equipe ou GEPA</label>
        ${renderFrentePickerMarkup('categoria', 'Tainã')}
      </div>
      <div class="form-grid two">
        <div class="field">
          <label for="despesa-valor">Valor (R$)</label>
          <input id="despesa-valor" name="valor" type="number" min="0.01" step="0.01" required>
        </div>
        <div class="field">
          <label for="despesa-data">Data</label>
          <input id="despesa-data" name="data" type="date" value="${hojeISO()}" required>
        </div>
        <div class="field" style="grid-column:1/-1">
          <label for="despesa-desc">Descrição curta</label>
          <input id="despesa-desc" name="descricao" required maxlength="140"
                 placeholder="Ex.: uber para atividade, lanche da reunião">
        </div>
        <div class="field" style="grid-column:1/-1">
          <label for="despesa-comprovante">Observação ou comprovante (opcional)</label>
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
      toast('Saída lançada no livro caixa.');
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

async function saveMembroFicha(id) {
  const form = $('#member-edit-form');
  if (!form) return;
  const dados = Object.fromEntries(new FormData(form).entries());
  await api(`/api/admin/membros/${id}`, {
    method: 'PATCH',
    body: dados,
  });
  toast('Alterações da ficha salvas.');
  await refreshData();
  await openDetalheMembro(id);
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
  const pagamentosMap = new Map((m.pagamentos || []).map((p) => [p.mes, p]));
  const anos = Array.from(new Set([
    ...Object.keys(Object.fromEntries((m.pagamentos || []).map((p) => [p.mes.slice(0, 4), true]))),
    String(new Date().getFullYear()),
  ])).sort((a, b) => Number(b) - Number(a));
  const mesesNomes = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
  const pagamentoGrids = anos.map((ano) => `
    <div class="payment-year">
      <div class="payment-year-title">${ano}</div>
      <div class="payment-grid">
        ${mesesNomes.map((nome, indice) => {
          const mes = `${ano}-${String(indice + 1).padStart(2, '0')}`;
          const pagamento = pagamentosMap.get(mes);
          const status = pagamento ? pagamento.status_pagamento : 'sem_cobranca';
          const cls = status === 'pago' ? 'is-paid' : status === 'aguardando_auditoria' ? 'is-wait' : status === 'pendente' ? 'is-pending' : '';
          const label = status === 'pago' ? 'Pago' : status === 'aguardando_auditoria' ? 'Aguardando' : status === 'pendente' ? 'Pendente' : '—';
          return `<button type="button" class="payment-chip ${cls}" data-action="toggle-payment-month" data-member-id="${m.id}" data-mes="${mes}" title="${label}">
            <span>${nome}</span><small>${label}</small>
          </button>`;
        }).join('')}
      </div>
    </div>`).join('');

  const equipeAtual = m.equipe || '';
  const gepaAtual = m.gepa || '';
  const modalidadeAtual = m.modalidade || m.modalidade_bolsa || '';
  openModal({
    title: m.nome,
    subtitle: 'Ficha cadastral e pagamentos',
    submitLabel: 'Fechar',
    hideCancel: true,
    body: `
      <div class="member-tabs" role="tablist" aria-label="Abas da ficha">
        <button type="button" class="member-tab is-active" data-action="member-tab" data-tab="ficha">Ficha</button>
        <button type="button" class="member-tab" data-action="member-tab" data-tab="pagamentos">Pagamentos</button>
      </div>

      <div class="member-tab-panel" data-member-panel="ficha">
        <form id="member-edit-form" class="member-edit-form">
          <div class="form-grid two">
            <div class="field"><label for="member-nome">Nome</label><input id="member-nome" name="nome" value="${esc(m.nome || '')}" maxlength="120" required></div>
            <div class="field"><label for="member-pronomes">Pronomes</label><input id="member-pronomes" name="pronomes" value="${esc(m.pronomes || '')}" placeholder="Ex.: ela/dela"></div>
            <div class="field"><label for="member-ra">RA</label><input id="member-ra" name="ra" value="${esc(m.ra || '')}" inputmode="numeric"></div>
            <div class="field"><label for="member-curso">Curso</label><input id="member-curso" name="curso" value="${esc(m.curso || '')}"></div>
            <div class="field"><label for="member-entrada">Quando entrou</label><input id="member-entrada" name="data_entrada" value="${esc(m.data_entrada || '')}" placeholder="AAAA-MM ou semestre"></div>
            <div class="field"><label for="member-modalidade">Modalidade</label>
              <select id="member-modalidade" name="modalidade">
                ${['','Bolsista BAS','Estagiário','Extensão','Extensão Pós-Graduação','BAEF','Outro'].map((v) => `<option value="${esc(v)}" ${modalidadeAtual === v ? 'selected' : ''}>${v || 'Não informada'}</option>`).join('')}
              </select>
            </div>
            <div class="field"><label for="member-equipe">Equipe</label>
              <select id="member-equipe-edit" name="equipe">
                ${['','Sem equipe','Tainã','Agricultura','Loucura','Gênero','Rede'].map((v) => `<option value="${esc(v)}" ${equipeAtual === v || (!equipeAtual && v === 'Sem equipe') ? 'selected' : ''}>${v || 'Não informada'}</option>`).join('')}
              </select>
            </div>
            <div class="field"><label for="member-gepa">GEPA</label>
              <select id="member-gepa-edit" name="gepa">
                ${['','Sem GEPA','GEPA 1','GEPA 2','GEPA 3','GEPA 4'].map((v) => `<option value="${esc(v)}" ${gepaAtual === v || (!gepaAtual && v === 'Sem GEPA') ? 'selected' : ''}>${v || 'Não informada'}</option>`).join('')}
              </select>
            </div>
            <div class="field"><label for="member-contato">Contato</label><input id="member-contato" name="contato" value="${esc(m.contato || '')}" placeholder="Telefone, e-mail ou outro"></div>
            <div class="field"><label>Telegram</label>
              <div class="telegram-field">${m.telegram_id ? `<span class="badge badge-active">${icon('check')} Vinculado · ${esc(m.telegram_id)}</span>` : '<span class="badge badge-neutral">Não vinculado</span>'}
                ${m.telegram_id ? '' : `<button type="button" class="btn btn-ghost btn-sm" data-action="open-link" data-id="${m.id}">${icon('link')} Vincular</button>`}
              </div>
            </div>
          </div>
          <div class="field"><label for="member-observacoes">Observações</label><textarea id="member-observacoes" name="observacoes" rows="3" placeholder="Informações adicionais">${esc(m.observacoes || '')}</textarea></div>
          <button type="button" class="btn btn-primary" data-action="save-member" data-id="${m.id}">${icon('check')} Salvar alterações</button>
        </form>
      </div>

      <div class="member-tab-panel" data-member-panel="pagamentos" hidden>
        <div class="payment-summary">
          <div><span>Pendente</span><strong>${brl(m.saldo_devedor || 0)}</strong></div>
          <div><span>Pago</span><strong>${brl(m.total_pago || 0)}</strong></div>
        </div>
        ${pagamentoGrids}
        <button type="button" class="btn btn-primary payment-register" data-action="register-member-payments" data-id="${m.id}">
          ${icon('check')} Registrar meses selecionados
        </button>
      </div>
    `,
    onSubmit: async () => {},
  });
}

async function solicitarPagamento(dados) {
  if (!state.ra) return;
  const valor = parseValor(dados.valor);
  if (!Number.isFinite(valor) || valor <= 0) {
    toast('Informe o valor pago.', 'error');
    return;
  }
  const aberto = Number(state.membro?.saldo_devedor || 0);
  if (aberto && valor - aberto > 0.001) {
    toast(`O valor é maior que o total em aberto (${brl(aberto)}).`, 'error');
    return;
  }
  try {
    const resultado = await api('/api/solicitar-pagamento', {
      method: 'POST',
      body: {
        ra: state.ra,
        valor,
        data: dados.data || hojeISO(),
        observacao: dados.observacao || null,
      },
    });
    state.membro = resultado.membro;
    toast(resultado.mensagem || 'Aviso enviado.');
    await refreshData();
  } catch (error) {
    toast(error.message || 'Não foi possível enviar o aviso.', 'error');
  }
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
    case 'toggle-theme':
      toggleTheme();
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
    case 'member-tab':
      $$('.member-tab').forEach((tab) => tab.classList.toggle('is-active', tab === element));
      $$('[data-member-panel]').forEach((panel) => {
        panel.hidden = panel.dataset.memberPanel !== element.dataset.tab;
      });
      break;
    case 'save-member':
      await saveMembroFicha(Number(element.dataset.id));
      break;
    case 'toggle-payment-month':
      element.classList.toggle('is-selected');
      break;
    case 'register-member-payments':
      {
        const meses = $$('.payment-chip.is-selected')
          .map((chip) => chip.dataset.mes);
        if (!meses.length) {
          toast('Selecione pelo menos um mês.', 'error');
          break;
        }
        await api(`/api/admin/membros/${Number(element.dataset.id)}/pagamentos`, {
          method: 'POST',
          body: { meses },
        });
        toast(`${meses.length} mês(es) registrado(s) como pago.`);
        await refreshData();
        await openDetalheMembro(Number(element.dataset.id));
      }
      break;
    case 'conferir':
      {
        const item = state.conferencia.find((a) => (
          Number(a.id) === Number(element.dataset.id) && a.tipo === element.dataset.tipo
        ));
        if (item) openConferencia(item, element.dataset.decision === '1');
      }
      break;
    case 'conferir-reembolso':
      {
        const item = state.reembolsos.find((rb) => Number(rb.id) === Number(element.dataset.id));
        if (item) openConferenciaReembolso(item, element.dataset.decision === '1');
      }
      break;
    case 'toggle-reembolso-pendente':
      await marcarReembolsoPendente(Number(element.dataset.id));
      break;
    case 'select-frente-group':
      {
        const picker = element.closest('[data-frente-picker]');
        if (!picker) break;
        const group = element.dataset.group;
        $$('[data-action="select-frente-group"]', picker).forEach((btn) => {
          btn.classList.toggle('is-active', btn.dataset.group === group);
        });
        $$('[data-frente-list]', picker).forEach((list) => {
          const ativo = list.dataset.frenteList === group;
          list.classList.toggle('hidden', !ativo);
          if (ativo) {
            const selectedChip = $('.frente-chip.is-active', list) || $('.frente-chip', list);
            if (selectedChip) {
              $$('.frente-chip', picker).forEach((c) => c.classList.remove('is-active'));
              selectedChip.classList.add('is-active');
              const input = $('[data-frente-input]', picker);
              if (input) input.value = selectedChip.dataset.frente;
            }
          }
        });
      }
      break;
    case 'select-frente-item':
      {
        const picker = element.closest('[data-frente-picker]');
        if (!picker) break;
        $$('.frente-chip', picker).forEach((c) => c.classList.toggle('is-active', c === element));
        const input = $('[data-frente-input]', picker);
        if (input) input.value = element.dataset.frente || '';
      }
      break;
    case 'select-reembolso-status':
      {
        const picker = element.closest('[data-status-picker]');
        if (!picker) break;
        const paid = element.dataset.paid === '1' ? '1' : '0';
        $$('[data-action="select-reembolso-status"]', picker).forEach((btn) => {
          btn.classList.toggle('is-active', btn.dataset.paid === paid);
        });
        const input = $('[data-status-input]', picker);
        if (input) input.value = paid;
      }
      break;
    case 'open-reembolso':
      openPedidoReembolso();
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
  if (tipo === 'solicitar-pagamento') {
    const dados = Object.fromEntries(new FormData(form).entries());
    await solicitarPagamento(dados);
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

document.addEventListener('change', (event) => {
  if (event.target.matches('[data-filter="equipe"]')) {
    state.filters.equipe = event.target.value;
    updateMemberList();
  }
  if (event.target.matches('[data-filter="gepa"]')) {
    state.filters.gepa = event.target.value;
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

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register(`${BASE_PATH}/service-worker.js`, {
      scope: `${BASE_PATH}/`,
    }).catch(() => {});
  });
}
