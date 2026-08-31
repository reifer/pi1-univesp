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
            root.classList.add('alto-contraste');
            if (body) body.classList.add('alto-contraste');
        } else {
            root.classList.remove('alto-contraste');
            if (body) body.classList.remove('alto-contraste');
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

        const botoesContraste = document.querySelectorAll('.toggle-alto-contraste');
        botoesContraste.forEach(function (btn) {
            btn.removeEventListener('click', toggleAltoContraste);
            btn.addEventListener('click', toggleAltoContraste);
        });

        // Atalho de teclado: Alt + C para alternar Alto Contraste
        window.addEventListener('keydown', function (e) {
            if (e.altKey && (e.key === 'c' || e.key === 'C')) {
                e.preventDefault();
                toggleAltoContraste();
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
