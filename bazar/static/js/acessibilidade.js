/**
 * Conexão Solidária - Módulo de Acessibilidade
 * Gerencia o Modo de Alto Contraste com persistência em localStorage e acessibilidade via teclado.
 */
(function () {
    const STORAGE_KEY = 'conexao_solidaria_alto_contraste';

    function aplicarAltoContraste(ativo) {
        const root = document.documentElement;
        const body = document.body;

        if (ativo) {
            root.classList.add('alto-contraste', 'high-contrast');
            if (body) body.classList.add('alto-contraste', 'high-contrast');
        } else {
            root.classList.remove('alto-contraste', 'high-contrast');
            if (body) body.classList.remove('alto-contraste', 'high-contrast');
        }

        // Força o reflow imediato do navegador (redesenho do DOM) para atualizar estilos reativamente
        void root.offsetWidth;

        // Atualizar estado de todos os botões de alternância na página
        const botoesContraste = document.querySelectorAll('.toggle-alto-contraste');
        botoesContraste.forEach(function (btn) {
            btn.setAttribute('aria-pressed', String(ativo));
            const spanTexto = btn.querySelector('.texto-contraste');
            if (spanTexto) {
                spanTexto.textContent = ativo ? 'Contraste Normal' : 'Alto Contraste';
            }
            btn.setAttribute('title', ativo ? 'Desativar modo de alto contraste' : 'Ativar modo de alto contraste');
        });

        // Alternância direta das imagens do logotipo (reforço JS para sincronização instantânea)
        const logosNormais = document.querySelectorAll('.logo-normal');
        const logosContraste = document.querySelectorAll('.logo-contraste');

        logosNormais.forEach(function (img) {
            if (ativo) {
                img.classList.add('hidden');
                img.style.setProperty('display', 'none', 'important');
            } else {
                img.classList.remove('hidden');
                img.style.removeProperty('display');
            }
        });

        logosContraste.forEach(function (img) {
            if (ativo) {
                img.classList.remove('hidden');
                img.style.setProperty('display', 'block', 'important');
            } else {
                img.classList.add('hidden');
                img.style.removeProperty('display');
            }
        });
    }

    function toggleAltoContraste() {
        const atual = localStorage.getItem(STORAGE_KEY) === 'true';
        const novo = !atual;
        try {
            localStorage.setItem(STORAGE_KEY, String(novo));
        } catch (e) {
            console.warn('Não foi possível salvar a preferência no localStorage:', e);
        }
        aplicarAltoContraste(novo);
    }

    // Inicialização ao carregar o DOM
    function init() {
        const salvo = localStorage.getItem(STORAGE_KEY) === 'true';
        aplicarAltoContraste(salvo);

        function handleBtnClick(e) {
            toggleAltoContraste();
            this.blur();
        }

        const botoesContraste = document.querySelectorAll('.toggle-alto-contraste');
        botoesContraste.forEach(function (btn) {
            btn.removeEventListener('click', handleBtnClick);
            btn.addEventListener('click', handleBtnClick);
        });

        // Atalho de teclado: Alt + C para alternar Alto Contraste
        window.addEventListener('keydown', function (e) {
            if (e.altKey && (e.key === 'c' || e.key === 'C')) {
                e.preventDefault();
                toggleAltoContraste();
                if (document.activeElement && document.activeElement.classList.contains('toggle-alto-contraste')) {
                    document.activeElement.blur();
                }
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Exporta para escopo global se necessário
    window.toggleAltoContraste = toggleAltoContraste;
})();
