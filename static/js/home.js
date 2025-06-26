// Configuración del temporizador Pomodoro
document.addEventListener('DOMContentLoaded', function() {
    // Obtener datos de productividad del JSON
    const productivityDataElement = document.getElementById('productivity-data');
    let productivityData = [];
    
    if (productivityDataElement) {
        try {
            productivityData = JSON.parse(productivityDataElement.textContent);
            console.log('🔍 Datos de productividad cargados:', productivityData);
        } catch (error) {
            console.error('Error al parsear datos de productividad:', error);
        }
    }

    // Animar las barras de productividad
    const productivityBars = document.querySelectorAll('[class*="bg-gradient-to-t"]');
    
    // Configurar estado inicial y animar
    productivityBars.forEach((bar, index) => {
        // Estado inicial
        bar.style.transform = 'scaleY(0)';
        bar.style.transformOrigin = 'bottom';
        bar.style.transition = 'transform 0.6s ease-out';
        
        // Animar con retraso escalonado
        setTimeout(() => {
            bar.style.transform = 'scaleY(1)';
        }, index * 150 + 300); // Retraso inicial de 300ms + 150ms por barra
    });

    // Agregar efecto de pulso a las barras con datos
    setTimeout(() => {
        productivityBars.forEach((bar, index) => {
            if (productivityData[index] && productivityData[index].percentage > 5) {
                bar.classList.add('animate-pulse');
                setTimeout(() => {
                    bar.classList.remove('animate-pulse');
                }, 1000);
            }
        });
    }, 2000);

    // Configuración del temporizador Pomodoro
    let pomodoroTime = 25 * 60;
    let timerInterval = null;
    let isRunning = false;

    const timerDisplay = document.getElementById('pomodoro-timer');
    const startButton = document.getElementById('pomodoro-start');
    const resetButton = document.getElementById('pomodoro-reset');

    function updateTimerDisplay(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    function startTimer() {
        if (!isRunning) {
            isRunning = true;
            startButton.textContent = 'Pausar';
            startButton.classList.remove('bg-purple-600', 'hover:bg-purple-500');
            startButton.classList.add('bg-red-600', 'hover:bg-red-500');
            
            timerInterval = setInterval(() => {
                if (pomodoroTime > 0) {
                    pomodoroTime--;
                    updateTimerDisplay(pomodoroTime);
                } else {
                    clearInterval(timerInterval);
                    isRunning = false;
                    new Audio('/static/sounds/timer-end.mp3').play().catch(() => {});
                    if (Notification.permission === 'granted') {
                        new Notification('¡Tiempo completado!', {
                            body: 'Tu sesión Pomodoro ha terminado. ¡Toma un descanso!',
                            icon: '/static/img/Logo2.png'
                        });
                    }
                }
            }, 1000);
        } else {
            clearInterval(timerInterval);
            isRunning = false;
            startButton.textContent = 'Iniciar';
            startButton.classList.remove('bg-red-600', 'hover:bg-red-500');
            startButton.classList.add('bg-purple-600', 'hover:bg-purple-500');
        }
    }

    function resetTimer() {
        clearInterval(timerInterval);
        isRunning = false;
        pomodoroTime = 25 * 60;
        updateTimerDisplay(pomodoroTime);
        startButton.textContent = 'Iniciar';
        startButton.classList.remove('bg-red-600', 'hover:bg-red-500');
        startButton.classList.add('bg-purple-600', 'hover:bg-purple-500');
    }

    if (startButton) startButton.addEventListener('click', startTimer);
    if (resetButton) resetButton.addEventListener('click', resetTimer);

    // Función para optimizar horario
    window.optimizarHorario = function() {
        window.location.href = "/planner/horarios/?optimize=true";
    };

    // Consejo del día automático
    const tips = [
        "La técnica Pomodoro puede aumentar tu productividad hasta un 75%. Tus patrones de estudio muestran que eres más productivo en sesiones de 25 minutos.",
        "Estudiar en múltiples sesiones cortas es más efectivo que una sola sesión larga. Intenta dividir tu tiempo de estudio en bloques de 25-30 minutos.",
        "Tomar notas a mano puede mejorar la retención de información en un 29% comparado con tomar notas en dispositivos electrónicos.",
        "Explicar conceptos a otros puede mejorar tu comprensión en un 90%. Considera formar un grupo de estudio.",
        "Dormir bien antes de un examen es más efectivo que estudiar toda la noche. El cerebro necesita descanso para consolidar la información.",
        "Alternar entre diferentes materias durante el estudio puede mejorar el aprendizaje en un 20% comparado con estudiar un solo tema por largo tiempo.",
        "Hacer ejercicio regular puede mejorar tu capacidad de concentración y memoria en hasta un 20%.",
        "Establecer metas específicas y alcanzables puede aumentar tu motivación y productividad en un 25%.",
        "Mantener un espacio de trabajo ordenado puede reducir la distracción y aumentar la concentración en un 15%.",
        "Tomar descansos regulares puede prevenir la fatiga mental y mantener altos niveles de productividad durante todo el día."
    ];

    function updateTip() {
        const tipElement = document.getElementById('daily-tip');
        if (tipElement) {
            const randomTip = tips[Math.floor(Math.random() * tips.length)];
            tipElement.textContent = randomTip;
        }
    }

    const lastUpdate = localStorage.getItem('lastTipUpdate');
    const now = new Date().getTime();

    if (!lastUpdate || (now - lastUpdate) > 24 * 60 * 60 * 1000) {
        updateTip();
        localStorage.setItem('lastTipUpdate', now);
    }
});

// Función para actualizar datos de productividad dinámicamente
function updateProductivityData(data) {
    const bars = document.querySelectorAll('[class*="bg-gradient-to-t"]');
    
    if (data && data.length === 7) {
        bars.forEach((bar, index) => {
            if (data[index] !== undefined) {
                const percentage = Math.max(5, data[index].percentage || 0);
                bar.style.height = `${percentage}%`;
                
                // Actualizar tooltip si existe
                const tooltip = bar.querySelector('[class*="opacity-0"]');
                if (tooltip) {
                    tooltip.textContent = `${data[index].percentage || 0}%`;
                }
            }
        });
    }
}

// Función para mostrar estado de carga
function showProductivityLoading() {
    const container = document.querySelector('.h-32.px-4');
    if (container) {
        container.innerHTML = `
            <div class="flex items-center justify-center h-full">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                <span class="ml-2 text-sm text-muted-foreground">Cargando datos...</span>
            </div>
        `;
    }
}

// Exportar funciones para uso global
window.updateProductivityData = updateProductivityData;
window.showProductivityLoading = showProductivityLoading;
