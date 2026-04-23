{
    interface ViaCepResponse {
        cep?: string;
        logradouro?: string;
        complemento?: string;
        bairro?: string;
        localidade?: string;
        uf?: string;
        erro?: boolean;
    }

    const inputCepRetirada = document.getElementById('cep-retirada') as HTMLInputElement | null;
    const inputEndereco = document.getElementById('endereco-retirada') as HTMLInputElement | null;
    const inputBairroRetirada = document.getElementById('bairro-retirada') as HTMLInputElement | null;
    const inputCidadeRetirada = document.getElementById('cidade-retirada') as HTMLInputElement | null;
    const inputUfRetirada = document.getElementById('uf-retirada') as HTMLInputElement | null;
    const formAlert = document.getElementById('form-alert') as HTMLDivElement | null;

    function showAlert(message: string): void {
        if (!formAlert) return;
        formAlert.textContent = message;
        formAlert.classList.remove('hidden');
    }

    function hideAlert(): void {
        if (!formAlert) return;
        formAlert.classList.add('hidden');
    }

    function clearAddressFields(): void {
        if (inputEndereco) inputEndereco.value = '';
        if (inputBairroRetirada) inputBairroRetirada.value = '';
        if (inputCidadeRetirada) inputCidadeRetirada.value = '';
        if (inputUfRetirada) inputUfRetirada.value = '';
    }

    async function fetchCep(cepDigits: string): Promise<void> {
        if (inputEndereco && inputBairroRetirada && inputCidadeRetirada && inputUfRetirada) {
            inputEndereco.value = 'Buscando...';
            inputBairroRetirada.value = 'Buscando...';
            inputCidadeRetirada.value = 'Buscando...';
            inputUfRetirada.value = '...';
            
            inputEndereco.disabled = true;
            inputBairroRetirada.disabled = true;
            inputCidadeRetirada.disabled = true;
            inputUfRetirada.disabled = true;
        }

        try {
            const response = await fetch(`https://viacep.com.br/ws/${cepDigits}/json/`);
            if (!response.ok) throw new Error('Falha de comunicação com o ViaCEP.');
            
            const data: ViaCepResponse = await response.json();
            if (data.erro) {
                showAlert('CEP não encontrado. Por favor, verifique o número.');
                clearAddressFields();
                return;
            }

            if (inputEndereco) inputEndereco.value = data.logradouro || '';
            if (inputBairroRetirada) inputBairroRetirada.value = data.bairro || '';
            if (inputCidadeRetirada) inputCidadeRetirada.value = data.localidade || '';
            if (inputUfRetirada) inputUfRetirada.value = (data.uf || '').toUpperCase();

            hideAlert();
        } catch (error) {
            clearAddressFields();
            showAlert('Não foi possível buscar o endereço pelo CEP. Verifique e tente novamente.');
        } finally {
            if (inputEndereco && inputBairroRetirada && inputCidadeRetirada && inputUfRetirada) {
                inputEndereco.disabled = false;
                inputBairroRetirada.disabled = false;
                inputCidadeRetirada.disabled = false;
                inputUfRetirada.disabled = false;
            }
        }
    }

    if (inputCepRetirada) {
        let debounceTimer: ReturnType<typeof setTimeout>;
        inputCepRetirada.addEventListener('input', function (event: Event): void {
            clearTimeout(debounceTimer);
            let cepValue = inputCepRetirada.value.replace(/\D/g, '');
            
            // Aplica mascara visual
            if (cepValue.length > 5) {
                inputCepRetirada.value = cepValue.slice(0, 5) + '-' + cepValue.slice(5, 8);
            } else {
                inputCepRetirada.value = cepValue;
            }

            if (cepValue.length === 0) {
                clearAddressFields();
                inputCepRetirada.setCustomValidity('');
            } else if (cepValue.length === 8) {
                inputCepRetirada.setCustomValidity('');
                debounceTimer = setTimeout(() => {
                    fetchCep(cepValue);
                }, 300);
            } else {
                inputCepRetirada.setCustomValidity('CEP deve conter exatamente 8 dígitos numéricos.');
            }
        });
    }
}
