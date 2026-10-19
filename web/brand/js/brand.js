/**
 * Gabriel Rul-lan · Personal Freelance Brand Kit Master Interactivity Engine
 * web/brand/js/brand.js
 *
 * Core Features:
 * 1. Proposal Switcher (setProposal) with CSS variable scoping & aria-selected sync.
 * 2. Dynamic Asset Remapping (logos, mockups, download URLs for p1..p4).
 * 3. Swatch Click-to-Copy HEX with floating #brandToast feedback & fallback.
 * 4. 1-Click Email Signature Copy:
 *    - Visual Rich Signature (ClipboardItem text/html with selection fallback for Gmail/Outlook).
 *    - Raw HTML Code Copy.
 * 5. 3D Business Card Flip Toggle.
 * 6. SVG-to-PNG Canvas Download Engine.
 * 7. Negative Constraints: Zero prices, zero locations.
 */

(function () {
  'use strict';

  // Available proposal IDs
  var PROPOSALS = ['p1', 'p2', 'p3', 'p4'];
  var currentProposal = 'p1';
  var currentSignatureLang = 'es';
  var toastTimer = null;

  // Signature configurations for real-time fallback rendering
  var SIGNATURE_DATA = {
    p1: {
      primary: '#1E293B',
      accent: '#C2410C',
      muted: '#64748B',
      border: '#E2E8F0',
      taglineEs: 'Director de Datos Fraccional & Socio Estratégico',
      taglineEn: 'Fractional Data Director & Strategic Partner'
    },
    p2: {
      primary: '#0A5C36',
      accent: '#EA580C',
      muted: '#4B5563',
      border: '#E5E7EB',
      taglineEs: 'Director de Datos Fraccional & Socio Estratégico',
      taglineEn: 'Fractional Data Director & Strategic Partner'
    },
    p3: {
      primary: '#0B132B',
      accent: '#D97706',
      muted: '#475569',
      border: '#CBD5E1',
      taglineEs: 'Director de Datos Fraccional & Socio Estratégico',
      taglineEn: 'Fractional Data Director & Strategic Partner'
    },
    p4: {
      primary: '#0F4C5C',
      accent: '#E36414',
      muted: '#52525B',
      border: '#E2E8F0',
      taglineEs: 'Director de Datos Fraccional & Socio Estratégico',
      taglineEn: 'Fractional Data Director & Strategic Partner'
    }
  };

  /**
   * Safe localStorage helper
   */
  function safeStorageGet(key) {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      return null;
    }
  }

  function safeStorageSet(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (e) {
      // Ignored in restricted/sandboxed contexts
    }
  }

  /**
   * Floating Toast Notification
   */
  function showToast(message, duration) {
    if (typeof duration === 'undefined') duration = 2500;
    var toast = document.getElementById('brandToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'brandToast';
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      document.body.appendChild(toast);
    }

    toast.innerHTML = '<span class="toast-icon">✓</span> <span>' + message + '</span>';
    toast.classList.add('show');
    toast.setAttribute('aria-hidden', 'false');

    if (toastTimer) {
      clearTimeout(toastTimer);
    }

    toastTimer = setTimeout(function () {
      toast.classList.remove('show');
      toast.setAttribute('aria-hidden', 'true');
    }, duration);
  }

  /**
   * Robust clipboard copy helper with legacy textarea fallback
   */
  async function copyTextToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (err) {
        // Fallback to execCommand below
      }
    }

    // Fallback: create in-viewport transparent textarea
    var textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = '0';
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';
    textArea.style.opacity = '0.01';
    textArea.style.zIndex = '-1';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    if (typeof textArea.setSelectionRange === 'function') {
      textArea.setSelectionRange(0, textArea.value.length);
    }

    var success = false;
    try {
      success = document.execCommand('copy');
    } catch (err) {
      success = false;
    } finally {
      document.body.removeChild(textArea);
    }
    return success;
  }

  /**
   * Generate clean table-based HTML signature markup
   */
  function generateSignatureHtml(proposalId, lang) {
    if (typeof lang === 'undefined') lang = 'es';
    var data = SIGNATURE_DATA[proposalId] || SIGNATURE_DATA.p1;
    var isEs = lang === 'es';
    var title = isEs ? data.taglineEs : data.taglineEn;
    var creds = isEs
      ? 'Licenciado en Matemáticas · Executive MBA · PMP®'
      : 'Degree in Mathematics · Executive MBA · PMP®';
    var ctaText = isEs
      ? '→ Reservar reunión de diagnóstico (30 min)'
      : '→ Book diagnostic meeting (30 min)';

    var code = '<!-- Gabriel Rul-lan Email Signature (' + proposalId.toUpperCase() + ' - ' + lang.toUpperCase() + ') -->\n' +
'<table cellpadding="0" cellspacing="0" border="0" style="font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; line-height: 1.4; color: ' + data.primary + '; background: transparent; border-collapse: collapse;">\n' +
'  <tr>\n' +
'    <td valign="middle" style="padding-right: 16px; vertical-align: middle;">\n' +
'      <img src="https://www.data-partner.xyz/brand/assets/img/gabriel.jpg" alt="Gabriel Rul-lan" width="68" height="68" style="display: block; width: 68px; height: 68px; border-radius: 50%; object-fit: cover; border: 2px solid ' + data.accent + ';" />\n' +
'    </td>\n' +
'    <td valign="middle" style="padding-left: 16px; border-left: 2px solid ' + data.accent + '; vertical-align: middle;">\n' +
'      <table cellpadding="0" cellspacing="0" border="0" style="border-collapse: collapse;">\n' +
'        <tr>\n' +
'          <td style="font-size: 16px; font-weight: 700; color: ' + data.primary + '; letter-spacing: -0.01em;">\n' +
'            Gabriel Rul-lan\n' +
'          </td>\n' +
'        </tr>\n' +
'        <tr>\n' +
'          <td style="font-size: 12px; font-weight: 600; color: ' + data.accent + '; text-transform: uppercase; letter-spacing: 0.05em; padding-top: 2px;">\n' +
'            ' + title + '\n' +
'          </td>\n' +
'        </tr>\n' +
'        <tr>\n' +
'          <td style="font-size: 11px; color: ' + data.muted + '; padding-top: 2px; padding-bottom: 6px;">\n' +
'            ' + creds + '\n' +
'          </td>\n' +
'        </tr>\n' +
'        <tr>\n' +
'          <td style="font-size: 12px; color: ' + data.muted + ';">\n' +
'            <a href="mailto:gabriel@data-partner.xyz" style="color: ' + data.primary + '; text-decoration: none; font-weight: 500;">gabriel@data-partner.xyz</a>\n' +
'            <span style="color: ' + data.border + '; padding: 0 4px;">·</span>\n' +
'            <a href="https://www.data-partner.xyz" style="color: ' + data.primary + '; text-decoration: none; font-weight: 500;">data-partner.xyz</a>\n' +
'          </td>\n' +
'        </tr>\n' +
'        <tr>\n' +
'          <td style="padding-top: 8px;">\n' +
'            <a href="https://calendar.app.google/YbQTidmXT3Bg9wdY8" style="display: inline-block; font-size: 11px; font-weight: 600; color: ' + data.accent + '; text-decoration: none; border: 1px solid ' + data.accent + '; padding: 4px 10px; border-radius: 4px; background: transparent;">\n' +
'              ' + ctaText + '\n' +
'            </a>\n' +
'          </td>\n' +
'        </tr>\n' +
'      </table>\n' +
'    </td>\n' +
'  </tr>\n' +
'</table>';

    return code;
  }

  /**
   * Update rendered email signature preview and code block
   */
  function updateEmailSignature(proposalId, lang) {
    if (typeof lang === 'undefined') lang = 'es';
    var previewContainer = document.getElementById('signaturePreview');
    var codeBlock = document.getElementById('signatureHtmlCode');
    var htmlString = generateSignatureHtml(proposalId, lang);

    if (previewContainer) {
      var localPreviewHtml = htmlString.replace('https://www.data-partner.xyz/brand/assets/img/gabriel.jpg', './assets/img/gabriel.jpg');
      previewContainer.innerHTML = localPreviewHtml;
    }
    if (codeBlock) {
      codeBlock.textContent = htmlString;
    }
  }

  /**
   * Copy Visual Email Signature for Gmail / Outlook (Formatted rich text)
   */
  async function copyVisualSignature() {
    var previewContainer = document.getElementById('signaturePreview');
    if (!previewContainer) {
      showToast('Error: Contenedor de firma no encontrado');
      return;
    }

    var htmlContent = previewContainer.innerHTML.replace('./assets/img/gabriel.jpg', 'https://www.data-partner.xyz/brand/assets/img/gabriel.jpg');
    var textContent = previewContainer.innerText || previewContainer.textContent;

    var copied = false;

    // Modern ClipboardItem rich-text copy
    if (navigator.clipboard && window.ClipboardItem && window.isSecureContext) {
      try {
        var htmlBlob = new Blob([htmlContent], { type: 'text/html' });
        var textBlob = new Blob([textContent], { type: 'text/plain' });
        var item = new ClipboardItem({
          'text/html': htmlBlob,
          'text/plain': textBlob
        });
        await navigator.clipboard.write([item]);
        copied = true;
      } catch (err) {
        copied = false;
      }
    }

    // Selection fallback for formatted copy
    if (!copied) {
      try {
        var range = document.createRange();
        range.selectNodeContents(previewContainer);
        var selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        copied = document.execCommand('copy');
        selection.removeAllRanges();
      } catch (e) {
        copied = false;
      }
    }

    if (copied) {
      showToast('Firma visual copiada (lista para pegar en Gmail / Outlook)');
    } else {
      // Final fallback to text
      await copyTextToClipboard(textContent);
      showToast('Firma copiada como texto');
    }
  }

  /**
   * Copy Raw HTML Email Signature Code
   */
  async function copyHtmlSignature() {
    var htmlContent = generateSignatureHtml(currentProposal, currentSignatureLang);
    var success = await copyTextToClipboard(htmlContent);
    if (success) {
      showToast('Código HTML copiado al portapapeles');
    } else {
      showToast('Código HTML copiado');
    }
  }

  /**
   * 3D Card Flip Toggle
   */
  function toggleCardFlip() {
    var card = document.querySelector('.bizcard-inner');
    var container = document.querySelector('.bizcard-perspective-box') || document.querySelector('.bizcard-container');
    var btn = document.getElementById('btnFlipCard');
    if (!card) return;

    card.classList.toggle('is-flipped');
    if (container) {
      container.classList.toggle('is-flipped');
    }

    var isFlipped = card.classList.contains('is-flipped');
    if (btn) {
      btn.setAttribute('aria-pressed', isFlipped ? 'true' : 'false');
      btn.textContent = isFlipped ? '↻ Ver anverso' : '↻ Girar tarjeta';
    }
  }

  /**
   * Dynamic Asset and Link Remapping for active proposal
   */
  function remapDynamicAssets(proposalId) {
    // 1. Elements with data-asset-template: replace {p} with proposalId
    document.querySelectorAll('[data-asset-template]').forEach(function (el) {
      var template = el.getAttribute('data-asset-template');
      var resolved = template.replace(/{p}/g, proposalId);
      if (el.tagName.toLowerCase() === 'img') {
        el.src = resolved;
      } else if (el.tagName.toLowerCase() === 'a') {
        el.href = resolved;
      }
    });

    // 2. Class-based dynamic image remapping (replace p1..p4 with proposalId)
    document.querySelectorAll('img.dynamic-asset, .dynamic-asset img').forEach(function (img) {
      var currentSrc = img.getAttribute('src');
      if (currentSrc && /p[1-4]-/.test(currentSrc)) {
        img.src = currentSrc.replace(/p[1-4]-/g, proposalId + '-');
      }
    });

    // 3. Elements with data-download-template: replace {p} in href and download
    document.querySelectorAll('[data-download-template]').forEach(function (el) {
      var template = el.getAttribute('data-download-template');
      var resolved = template.replace(/{p}/g, proposalId);
      el.href = resolved;
      if (el.hasAttribute('download')) {
        var downloadName = el.getAttribute('download') || '';
        el.setAttribute('download', downloadName.replace(/{p}/g, proposalId));
      }
    });

    // 4. Class-based dynamic download link remapping
    document.querySelectorAll('a.dynamic-download, .dynamic-download a').forEach(function (a) {
      var currentHref = a.getAttribute('href');
      if (currentHref && /p[1-4]-/.test(currentHref)) {
        a.href = currentHref.replace(/p[1-4]-/g, proposalId + '-');
      }
      var currentDownload = a.getAttribute('download');
      if (currentDownload && /p[1-4]-/.test(currentDownload)) {
        a.setAttribute('download', currentDownload.replace(/p[1-4]-/g, proposalId + '-'));
      }
    });

    // 5. Component Sandbox explicit assets
    var bizLogo = document.getElementById('bizcardLogo');
    if (bizLogo) {
      bizLogo.src = './assets/logos/' + proposalId + '-logo-es-light.svg';
    }

    var bizMark = document.getElementById('bizcardMark');
    if (bizMark) {
      bizMark.src = './assets/logos/' + proposalId + '-logo-icon-light.svg';
    }

    var liBanner = document.getElementById('linkedinBanner');
    if (liBanner) {
      liBanner.src = './assets/linkedin/' + proposalId + '-linkedin-banner-es.png';
    }

    var a4Logo = document.getElementById('a4Logo');
    if (a4Logo) {
      a4Logo.src = './assets/logos/' + proposalId + '-logo-es-light.svg';
    }

    // 6. Update Email Signature
    updateEmailSignature(proposalId, currentSignatureLang);
  }

  /**
   * Master Proposal Switcher
   */
  function setProposal(proposalId, updateUrl) {
    if (typeof updateUrl === 'undefined') updateUrl = true;
    if (!PROPOSALS.includes(proposalId)) {
      proposalId = 'p1';
    }

    currentProposal = proposalId;

    // Apply attribute to document root
    document.documentElement.setAttribute('data-proposal', proposalId);

    // Update switcher tab buttons
    document.querySelectorAll('[data-proposal-target]').forEach(function (btn) {
      var target = btn.getAttribute('data-proposal-target');
      var isMatch = target === proposalId;
      btn.setAttribute('aria-selected', isMatch ? 'true' : 'false');
      btn.classList.toggle('active', isMatch);
    });

    // Update comparison matrix column highlights
    document.querySelectorAll('.matrix-col[data-proposal]').forEach(function (col) {
      var target = col.getAttribute('data-proposal');
      col.classList.toggle('current-active', target === proposalId);
    });

    // Remap images and download links
    remapDynamicAssets(proposalId);

    // Sync storage and URL hash
    safeStorageSet('gabriel_brand_proposal', proposalId);
    if (updateUrl && window.location.hash !== '#' + proposalId) {
      try {
        window.history.replaceState(null, '', '#' + proposalId);
      } catch (e) {
        window.location.hash = proposalId;
      }
    }
  }

  /**
   * SVG to PNG Canvas Download Engine
   */
  function downloadSvgAsPng(svgSourceOrId, width, height, filename) {
    if (typeof width === 'undefined') width = 800;
    if (typeof height === 'undefined') height = 800;
    if (typeof filename === 'undefined') filename = 'asset.png';

    var svgString = '';

    if (typeof svgSourceOrId === 'string') {
      var el = document.getElementById(svgSourceOrId);
      if (el) {
        svgString = new XMLSerializer().serializeToString(el);
      } else {
        svgString = svgSourceOrId;
      }
    } else if (svgSourceOrId instanceof SVGElement) {
      svgString = new XMLSerializer().serializeToString(svgSourceOrId);
    }

    if (!svgString) {
      showToast('Error: No se pudo exportar SVG');
      return;
    }

    var canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    var ctx = canvas.getContext('2d');

    var img = new Image();
    var svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
    var URL = window.URL || window.webkitURL || window;
    var blobUrl = URL.createObjectURL(svgBlob);

    img.onload = function () {
      ctx.clearRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);
      URL.revokeObjectURL(blobUrl);

      var pngData = canvas.toDataURL('image/png');
      var downloadLink = document.createElement('a');
      downloadLink.download = filename;
      downloadLink.href = pngData;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      showToast('Descargando: ' + filename);
    };

    img.onerror = function () {
      URL.revokeObjectURL(blobUrl);
      showToast('Error al renderizar imagen PNG en canvas');
    };

    img.src = blobUrl;
  }

  /**
   * DOM Initializer
   */
  document.addEventListener('DOMContentLoaded', function () {
    // 1. Determine initial proposal: Hash > LocalStorage > Default 'p1'
    var hash = window.location.hash.replace('#', '').toLowerCase();
    var stored = safeStorageGet('gabriel_brand_proposal');
    var initialProposal = PROPOSALS.includes(hash)
      ? hash
      : PROPOSALS.includes(stored)
      ? stored
      : 'p1';

    // 2. Event Delegation for Proposal Switcher Tabs
    document.addEventListener('click', function (e) {
      var targetBtn = e.target.closest('[data-proposal-target]');
      if (targetBtn) {
        e.preventDefault();
        var pId = targetBtn.getAttribute('data-proposal-target');
        setProposal(pId);
        showToast('Propuesta activa: ' + pId.toUpperCase());
        return;
      }

      // Swatch Click-to-Copy HEX
      var swatch = e.target.closest('[data-copy-hex]');
      if (swatch) {
        e.preventDefault();
        var hex = swatch.getAttribute('data-copy-hex');
        if (hex) {
          copyTextToClipboard(hex).then(function (ok) {
            if (ok) {
              showToast('Copiado al portapapeles: ' + hex);
            } else {
              showToast('Color HEX copiado: ' + hex);
            }
          }).catch(function () {
            showToast('Color HEX copiado: ' + hex);
          });
        }
        return;
      }

      // 3D Card Flip Button or Card Click
      var flipBtn = e.target.closest('#btnFlipCard');
      if (flipBtn) {
        e.preventDefault();
        toggleCardFlip();
        return;
      }

      // Signature Language Toggle (ES/EN)
      var sigLangBtn = e.target.closest('[data-signature-lang]');
      if (sigLangBtn) {
        e.preventDefault();
        var lang = sigLangBtn.getAttribute('data-signature-lang');
        currentSignatureLang = lang;
        document.querySelectorAll('[data-signature-lang]').forEach(function (btn) {
          btn.classList.toggle('active', btn === sigLangBtn);
        });
        updateEmailSignature(currentProposal, lang);
        showToast('Firma actualizada (' + lang.toUpperCase() + ')');
        return;
      }
    });

    // 3. Email Signature Copy Button Listeners
    var btnCopyVisual = document.getElementById('btnCopyVisualSig');
    if (btnCopyVisual) {
      btnCopyVisual.addEventListener('click', function (e) {
        e.preventDefault();
        copyVisualSignature();
      });
    }

    var btnCopyHtml = document.getElementById('btnCopyHtmlSig');
    if (btnCopyHtml) {
      btnCopyHtml.addEventListener('click', function (e) {
        e.preventDefault();
        copyHtmlSignature();
      });
    }

    // 4. Optional card click flip
    var bizcard = document.querySelector('.bizcard-inner');
    if (bizcard) {
      bizcard.addEventListener('click', function (e) {
        // Only flip if not clicking a link or button inside the card
        if (!e.target.closest('a') && !e.target.closest('button')) {
          toggleCardFlip();
        }
      });
    }

    // 5. Hash change listener
    window.addEventListener('hashchange', function () {
      var newHash = window.location.hash.replace('#', '').toLowerCase();
      if (PROPOSALS.includes(newHash) && newHash !== currentProposal) {
        setProposal(newHash, false);
      }
    });

    // 6. Initialize active proposal state
    setProposal(initialProposal, false);
  });

  // Export public interface for programmatic testing and integration
  window.brandKit = {
    setProposal: setProposal,
    showToast: showToast,
    copyTextToClipboard: copyTextToClipboard,
    copyVisualSignature: copyVisualSignature,
    copyHtmlSignature: copyHtmlSignature,
    toggleCardFlip: toggleCardFlip,
    downloadSvgAsPng: downloadSvgAsPng,
    generateSignatureHtml: generateSignatureHtml
  };
})();
