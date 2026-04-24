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
    console.log('Script de CEP carregado');
    const inputCep = document.getElementById('cep-retirada');
    const inputEndereco = document.getElementById('endereco-retirada');
    const inputBairroRetirada = document.getElementById('bairro-retirada');
    const inputCidadeRetirada = document.getElementById('cidade-retirada');
    const inputUfRetirada = document.getElementById('uf-retirada');
    const cepError = document.getElementById('cep-error');
    let currentFetchToken = 0;
    function showCepError() {
        if (cepError) {
            cepError.classList.remove('hidden');
            cepError.classList.add('block');
            cepError.style.setProperty('display', 'block', 'important');
            cepError.style.setProperty('visibility', 'visible', 'important');
            cepError.style.opacity = '1';
        }
        if (inputCep) {
            inputCep.classList.add('border-red-500', 'ring-red-500');
            inputCep.classList.remove('border-slate-100');
        }
    }
    function hideCepError() {
        if (cepError) {
            cepError.classList.add('hidden');
            cepError.classList.remove('block');
            cepError.style.removeProperty('display');
            cepError.style.removeProperty('visibility');
            cepError.style.opacity = '1';
        }
        if (inputCep) {
            inputCep.classList.remove('border-red-500', 'ring-red-500');
            inputCep.classList.add('border-slate-100');
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
    function fetchCep(cepDigits, fetchToken) {
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
                const response = yield fetch(`https://viacep.com.br/ws/${cepDigits}/json/`);
                if (!response.ok)
                    throw new Error('Falha de comunicacao com o ViaCEP.');
                // Evita preencher campos com resposta antiga quando o CEP ja mudou.
                const currentCepDigits = inputCep ? inputCep.value.replace(/\D/g, '') : '';
                if (fetchToken !== currentFetchToken || currentCepDigits !== cepDigits) {
                    return;
                }
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
                hideCepError();
            }
            catch (error) {
                const currentCepDigits = inputCep ? inputCep.value.replace(/\D/g, '') : '';
                if (fetchToken !== currentFetchToken || currentCepDigits !== cepDigits) {
                    return;
                }
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
    if (inputCep) {
        inputCep.addEventListener('input', function (event) {
            hideCepError();
            let cepValue = inputCep.value.replace(/\D/g, '');
            // Aplica mascara visual
            if (cepValue.length > 5) {
                inputCep.value = cepValue.slice(0, 5) + '-' + cepValue.slice(5, 8);
            }
            else {
                inputCep.value = cepValue;
            }
            if (cepValue.length !== 8) {
                currentFetchToken += 1;
                clearAddressFields();
                inputCep.setCustomValidity('CEP deve conter exatamente 8 dígitos numéricos.');
            }
            else {
                inputCep.setCustomValidity('');
                const fetchToken = currentFetchToken + 1;
                currentFetchToken = fetchToken;
                fetchCep(cepValue, fetchToken);
            }
            if (cepValue.length === 0) {
                inputCep.setCustomValidity('');
            }
        });
    }
}
