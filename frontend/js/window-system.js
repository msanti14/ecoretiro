/**
 * EcoRetiro OS — Window System
 * Lógica de botones de ventana (_, □, ×) y animación slideIn
 * Sin dependencias externas
 */
(function () {
  'use strict';

  /* -------- Window Controls -------- */

  function initWindowControls() {
    document.querySelectorAll('.window-controls').forEach(function (controlBar) {
      var win = controlBar.closest('.window');

      controlBar.querySelectorAll('.window-btn').forEach(function (btn) {
        var action = btn.textContent.trim();

        if (action === '_') {
          btn.addEventListener('click', function () { minimizeWindow(win); });
        } else if (action === '\u25A1') {
          btn.addEventListener('click', function () { maximizeWindow(win); });
        } else if (action === '\u00D7') {
          btn.addEventListener('click', function () { closeWindow(win); });
        }
      });
    });
  }

  function minimizeWindow(win) {
    var target = win.closest('.container') || win;
    target.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
    target.style.transform = 'scale(0.5)';
    target.style.opacity = '0.5';

    setTimeout(function () {
      target.style.transform = '';
      target.style.opacity = '';
      setTimeout(function () { target.style.transition = ''; }, 300);
    }, 500);
  }

  function maximizeWindow(win) {
    var target = win.closest('.container') || win;
    target.classList.toggle('maximized');
  }

  function closeWindow(win) {
    var target = win.closest('.container') || win;
    target.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
    target.style.transform = 'scale(0.8)';
    target.style.opacity = '0';

    setTimeout(function () {
      target.style.display = 'none';

      var inPages = window.location.pathname.indexOf('/pages/') !== -1;
      var prefix = inPages ? '' : 'pages/';
      var isLoggedIn = localStorage.getItem('ecoretiro-token') !== null;

      var screen = document.createElement('div');
      screen.className = 'desktop-screen';

      var grid = document.createElement('div');
      grid.className = 'desktop-grid';

      if (!isLoggedIn) {
        grid.appendChild(createDesktopIcon('\uD83D\uDD11', 'Iniciar Sesi\u00F3n', prefix + 'login.html'));
      } else {
        var items = [
          { emoji: '\uD83C\uDFE0', label: 'Inicio', href: prefix + 'home.html' },
          { emoji: '\u2795', label: 'Nueva Solicitud', href: prefix + 'nueva-solicitud.html' },
          { emoji: '\uD83D\uDCE6', label: 'Seguimiento', href: prefix + 'tracking.html' },
          { emoji: '\uD83D\uDC64', label: 'Perfil', href: prefix + 'perfil.html' },
          { emoji: '\uD83D\uDD12', label: 'Cerrar Sesi\u00F3n', href: null }
        ];

        items.forEach(function (item) {
          if (item.href) {
            grid.appendChild(createDesktopIcon(item.emoji, item.label, item.href));
          } else {
            var icon = createDesktopIcon(item.emoji, item.label);
            icon.addEventListener('click', function () {
              localStorage.removeItem('ecoretiro-token');
              window.location.href = prefix + 'login.html';
            });
            grid.appendChild(icon);
          }
        });
      }

      screen.appendChild(grid);
      document.body.appendChild(screen);
    }, 300);
  }

  function createDesktopIcon(emoji, label, href) {
    var icon = document.createElement('div');
    icon.className = 'desktop-icon';
    icon.innerHTML = '<div class="desktop-icon-emoji">' + emoji + '</div><div class="desktop-icon-label">' + label + '</div>';
    if (href) {
      icon.addEventListener('click', function () {
        window.location.href = href;
      });
    }
    return icon;
  }

  /* -------- SlideIn al cargar -------- */

  function initSlideIn() {
    document.querySelectorAll('.container').forEach(function (el) {
      // Re-trigger: resetea y relanza la animación CSS
      el.style.animation = 'none';
      void el.offsetWidth; // force reflow
      el.style.animation = '';
    });
  }

  /* -------- Theme Toggle -------- */

  function initThemeToggle() {
    var saved = localStorage.getItem('ecoretiro-theme');
    if (saved === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
    }

    document.querySelectorAll('.window-titlebar').forEach(function (titlebar) {
      var controls = titlebar.querySelector('.window-controls');
      if (!controls) return;

      var btn = document.createElement('div');
      btn.className = 'theme-toggle';
      btn.title = 'Toggle dark mode';
      btn.textContent = getCurrentIcon();
      titlebar.insertBefore(btn, controls);

      btn.addEventListener('click', function () {
        toggleTheme();
        document.querySelectorAll('.theme-toggle').forEach(function (b) {
          b.textContent = getCurrentIcon();
        });
      });
    });
  }

  function toggleTheme() {
    var html = document.documentElement;
    var isDark = html.getAttribute('data-theme') === 'dark';
    if (isDark) {
      html.removeAttribute('data-theme');
      localStorage.setItem('ecoretiro-theme', 'light');
    } else {
      html.setAttribute('data-theme', 'dark');
      localStorage.setItem('ecoretiro-theme', 'dark');
    }
  }

  function getCurrentIcon() {
    return document.documentElement.getAttribute('data-theme') === 'dark' ? '☀' : '☾';
  }

  /* -------- Init -------- */

  function init() {
    initSlideIn();
    initWindowControls();
    initThemeToggle();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
