"use strict";
// Script para popular o select de horário de coleta (09:00 as 17:00)
document.addEventListener('DOMContentLoaded', (event) => {
    const horarioSelect = document.getElementById('horario_coleta');
    if (!horarioSelect)
        return;
    // Configurando horário de início e fim
    const startHour = 9; // 09:00
    const endHour = 17; // 17:00
    const stepMinutes = 60; // 60 minutos de intervalo
    horarioSelect.innerHTML = '';
    const placeholderOption = document.createElement('option');
    placeholderOption.value = '';
    placeholderOption.textContent = 'Selecione um horário';
    horarioSelect.appendChild(placeholderOption);
    // Geração dinâmica de opções
    for (let hour = startHour; hour <= endHour; hour++) {
        for (let minute = 0; minute < 60; minute += stepMinutes) {
            // Não deve ultrapassar as 17:00 com valores inteiros de minutos (ex: 17:30)
            if (hour === endHour && minute > 0)
                continue;
            const hourString = hour.toString().padStart(2, '0');
            const minuteString = minute.toString().padStart(2, '0');
            const timeString = `${hourString}:${minuteString}`;
            const option = document.createElement('option');
            option.value = timeString;
            option.textContent = timeString;
            horarioSelect.appendChild(option);
        }
    }
});
