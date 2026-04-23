// Script para manipulação e tipagem do select de horário (09:00 as 17:00)
document.addEventListener('DOMContentLoaded', (event: Event): void => {
    const dataList = document.getElementById('opcoes-horario') as HTMLDataListElement | null;
    
    if (!dataList) return;

    // Configurando horário de início e fim
    const startHour = 9; // 09:00
    const endHour = 17;  // 17:00
    const stepMinutes = 30; // 30 minutos de intervalo

    dataList.innerHTML = '';

    // Geração dinâmica de opções
    for (let hour = startHour; hour <= endHour; hour++) {
        for (let minute = 0; minute < 60; minute += stepMinutes) {
            // Não deve ultrapassar as 17:00 com valores inteiros de minutos (ex: 17:30)
            if (hour === endHour && minute > 0) continue;

            const hourString = hour.toString().padStart(2, '0');
            const minuteString = minute.toString().padStart(2, '0');
            const timeString = `${hourString}:${minuteString}`;

            const option = document.createElement('option');
            option.value = timeString;
            dataList.appendChild(option);
        }
    }
});