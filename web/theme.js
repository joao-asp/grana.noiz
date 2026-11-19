/* Aplica o tema salvo (ou o do sistema) antes de pintar, sem piscar. */
(function () {
  var tema = null;
  try { tema = localStorage.getItem('grana_theme'); } catch (e) {}
  if (tema !== 'light' && tema !== 'dark') {
    tema = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark' : 'light';
  }
  var raiz = document.documentElement;
  raiz.setAttribute('data-theme', tema);
  raiz.style.colorScheme = tema;
  var meta = document.querySelector('meta[name="theme-color"]');
  if (meta) meta.setAttribute('content', tema === 'dark' ? '#0F172A' : '#F8FAFC');
})();
