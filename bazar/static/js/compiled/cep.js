"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
{
    const inputCepRetirada = document.getElementById('cep-retirada');
    const inputEndereco = document.getElementById('endereco-retirada');
    const inputBairroRetirada = document.getElementById('bairro-retirada');
    const inputCidadeRetirada = document.getElementById('cidade-retirada');
    const inputUfRetirada = document.getElementById('uf-retirada');
    const formAlert = document.getElementById('form-alert');
    const cepError = document.getElementById('cep-error');
    function showAlert(message) {
        if (!formAlert)
            return;
        formAlert.textContent = message;
        formAlert.classList.remove('hidden');
    }
    function hideAlert() {
        if (!formAlert)
            return;
        formAlert.classList.add('hidden');
    }
    function showCepError() {
        if (cepError)
            cepError.classList.remove('hidden');
        if (inputCepRetirada) {
            inputCepRetirada.classList.add('border-red-500', 'ring-red-500');
            inputCepRetirada.classList.remove('border-slate-100');
        }
    }
    function hideCepError() {
        if (cepError)
            cepError.classList.add('hidden');
        if (inputCepRetirada) {
            inputCepRetirada.classList.remove('border-red-500', 'ring-red-500');
            inputCepRetirada.classList.add('border-slate-100');
        }
    }
    function clearAddressFields() {
        if (inputEndereco)
            inputEndereco.value = '';
        if (inputBairroRetirada)
            inputBairroRetirada.value = '';
        if (inputCidadeRetirada)
            inputCidadeRetirada.value = '';
        if (inputUfRetirada)
            inputUfRetirada.value = '';
    }
    function fetchCep(cepDigits) {
        return __awaiter(this, void 0, void 0, function* () {
            hideCepError();
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
                const response = yield fetch('https://viacep.com.br/ws/' + cepDigits + '/json/');
                if (!response.ok)
                    throw new Error('Falha de comunicacao com o ViaCEP.');
                const data = yield response.json();
                if (data.erro) {
                    showCepError();
                    clearAddressFields();
                    return;
                }
                if (inputEndereco)
                    inputEndereco.value = data.logradouro || '';
                if (inputBairroRetirada)
                    inputBairroRetirada.value = data.bairro || '';
                if (inputCidadeRetirada)
                    inputCidadeRetirada.value = data.localidade || '';
                if (inputUfRetirada)
                    inputUfRetirada.value = (data.uf || '').toUpperCase();
            }
            catch (error) {
                clearAddressFields();
                showCepError();
            }
            finally {
                if (inputEndereco && inputBairroRetirada && inputCidadeRetirada && inputUfRetirada) {
                    inputEndereco.disabled = false;
                    inputBairroRetirada.disabled = false;
                    inputCidadeRetirada.disabled = false;
                    inputUfRetirada.disabled = false;
                }
            }
        });
    }
    if (inputCepRetirada) {
        let debounceTimer;
        inputCepRetirada.addEventListener('input', function (event) {
            clearTimeout(debounceTimer);
            let cepValue = inputCepRetirada.value.replace(/\D/g, '');
            // Aplica mascara visual
            if (cepValue.length > 5) {
                inputCepRetirada.value = cepValue.slice(0, 5) + '-' + cepValue.slice(5, 8);
            }
            else {
                inputCepRetirada.value = cepValue;
            }
            if (cepValue.length === 0) {
                clearAddressFields();
                inputCepRetirada.setCustomValidity('');
                hideCepError();
            }
            else if (cepValue.length === 8) {
                inputCepRetirada.setCustomValidity('');
                debounceTimer = setTimeout(() => {
                    fetchCep(cepValue);
                }, 300);
            }
            else {
                inputCepRetirada.setCustomValidity('CEP deve conter exatamente 8 dÃgitos numÃ©ricos.');
                if (cepValue.length < 8 && cepValue.length > 0)
                    hideCepError();
            }
        });
    }
}
