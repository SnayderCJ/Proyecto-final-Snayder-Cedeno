// Archivo: static/js/bloques_enfocados_mejorado.js

let tiempo = 25 * 60;
let tiempoOriginal = 25 * 60;
let enMarcha = false;
let intervalo;
let tipoActual = 'estudio';
let cicloPomodoro = 1;
let bloquesCompletados = 0;

// Configuraciones predefinidas
const configuraciones = {
  pomodoro: { enfoque: 25, descansoCorto: 5, descansoLargo: 15 },
  bloqueCorto: { enfoque: 15, descanso: 3 },
  bloqueLargo: { enfoque: 50, descanso: 10 },
  personalizado: { enfoque: 25, descanso: 5 }
};

function actualizarTemporizador() {
  const min = Math.floor(tiempo / 60).toString().padStart(2, '0');
  const seg = (tiempo % 60).toString().padStart(2, '0');
  document.getElementById("temporizador").textContent = `${min}:${seg}`;
  
  // Actualizar título de la página
  document.title = `${min}:${seg} - ${tipoActual === 'estudio' ? '🎯 Estudiando' : '☕ Descansando'}`;
  
  // Cambiar color según el progreso
  const progreso = 1 - (tiempo / tiempoOriginal);
  const temporizadorEl = document.getElementById("temporizador");
  
  if (progreso > 0.8) {
    temporizadorEl.className = "text-4xl font-bold text-red-500 mb-4";
  } else if (progreso > 0.5) {
    temporizadorEl.className = "text-4xl font-bold text-yellow-500 mb-4";
  } else {
    temporizadorEl.className = "text-4xl font-bold text-purple-500 mb-4";
  }
}

function aplicarConfiguracion() {
  const minutos = parseInt(document.getElementById("inputEnfoque").value) || 25;
  const objetivo = document.getElementById("inputObjetivo").value;

  tiempo = minutos * 60;
  tiempoOriginal = minutos * 60;
  tipoActual = objetivo;
  actualizarTemporizador();

  document.getElementById("objetivo-actual").textContent = objetivo === "estudio"
    ? "🎯 Tiempo de Estudio"
    : "☕ Tiempo de Descanso";
    
  // Mostrar información del ciclo
  actualizarInfoCiclo();
}

function aplicarConfiguracionPredefinida(tipo) {
  const config = configuraciones[tipo];
  if (!config) return;
  
  document.getElementById("inputEnfoque").value = config.enfoque;
  tiempo = config.enfoque * 60;
  tiempoOriginal = config.enfoque * 60;
  tipoActual = 'estudio';
  
  actualizarTemporizador();
  document.getElementById("objetivo-actual").textContent = "🎯 Tiempo de Estudio";
  actualizarInfoCiclo();
}

function actualizarInfoCiclo() {
  const infoEl = document.getElementById("info-ciclo");
  if (infoEl) {
    infoEl.textContent = `Ciclo ${cicloPomodoro} - Bloques completados: ${bloquesCompletados}`;
  }
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function reproducirSonido(tipo = 'completado') {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    if (tipo === 'completado') {
      oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
      oscillator.frequency.setValueAtTime(1000, audioContext.currentTime + 0.1);
      oscillator.frequency.setValueAtTime(1200, audioContext.currentTime + 0.2);
    } else if (tipo === 'advertencia') {
      oscillator.frequency.setValueAtTime(600, audioContext.currentTime);
    }
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.3);
  } catch (error) {
    console.log('Audio no disponible');
  }
}

function mostrarNotificacion(mensaje, tipo = 'success') {
  if (Notification.permission === 'granted') {
    new Notification('Tiempo Enfocado', {
      body: mensaje,
      icon: '/static/favicon.ico'
    });
  }
  
  mostrarToast(mensaje, tipo);
}

function iniciarPomodoro() {
  if (!enMarcha) {
    enMarcha = true;
    
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }

    intervalo = setInterval(() => {
      if (tiempo > 0) {
        tiempo--;
        actualizarTemporizador();
        
        if (tiempo === 5) {
          reproducirSonido('advertencia');
        }
      } else {
        clearInterval(intervalo);
        enMarcha = false;
        bloquesCompletados++;
        
        reproducirSonido('completado');
        
        const mensaje = tipoActual === 'estudio' 
          ? '¡Bloque de estudio completado! 🎉' 
          : '¡Tiempo de descanso terminado! 💪';
        mostrarNotificacion(mensaje);

        const enfoqueMin = Math.floor(tiempoOriginal / 60);
        const tipoBloque = tipoActual;

        fetch("/planner/registrar-bloque-temporizador/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")
          },
          body: JSON.stringify({
            tipo: tipoBloque,
            duracion: enfoqueMin
          })
        })
        .then(response => response.json())
        .then(data => {
          console.log("Bloque registrado:", data);
          actualizarResumenProductividad();
          
          if (tipoActual === 'estudio') {
            sugerirDescanso();
          } else {
            sugerirEstudio();
          }
        })
        .catch(error => {
          console.error("Error al registrar bloque:", error);
        });
        
        document.title = "Tiempo Enfocado - Planificador";
      }
    }, 1000);
  }
}

function sugerirDescanso() {
  const esDescansoLargo = bloquesCompletados % 4 === 0;
  const tiempoDescanso = esDescansoLargo ? 15 : 5;
  
  if (confirm(`¡Excelente trabajo! ¿Quieres tomar un ${esDescansoLargo ? 'descanso largo' : 'descanso corto'} de ${tiempoDescanso} minutos?`)) {
    document.getElementById("inputEnfoque").value = tiempoDescanso;
    document.getElementById("inputObjetivo").value = "descanso";
    aplicarConfiguracion();
  }
}

function sugerirEstudio() {
  cicloPomodoro++;
  if (confirm('¡Descanso completado! ¿Listo para otro bloque de estudio?')) {
    document.getElementById("inputEnfoque").value = 25;
    document.getElementById("inputObjetivo").value = "estudio";
    aplicarConfiguracion();
  }
}

function pausarPomodoro() {
  clearInterval(intervalo);
  enMarcha = false;
  document.title = "⏸️ Pausado - Tiempo Enfocado";
}

function reiniciarPomodoro() {
  clearInterval(intervalo);
  tiempo = tiempoOriginal;
  actualizarTemporizador();
  enMarcha = false;
  document.getElementById("objetivo-actual").textContent = "";
  document.title = "Tiempo Enfocado - Planificador";
}

function actualizarResumenProductividad() {
  // Intentar primero con la API más completa, luego con la alternativa
  fetch("/planner/api/productividad/")
    .then(response => response.json())
    .then(data => {
      const resumen = document.getElementById("resumen-productividad");
      const bloquesEstudio = data.bloques_estudio || 0;
      const minutosTotales = data.minutos_totales || 0;
      
      const tiempoTexto = minutosTotales >= 60
        ? `${Math.floor(minutosTotales / 60)}h ${minutosTotales % 60}m`
        : `${minutosTotales}m`;

      resumen.innerHTML = `
        <li class="flex items-center gap-2 text-gray-300">
          <span class="text-green-500">✅</span>
          ${bloquesEstudio} bloques de estudio completados hoy
        </li>
        <li class="flex items-center gap-2 text-gray-300">
          <span class="text-purple-500">⏱️</span>
          Tiempo Acumulado: ${tiempoTexto}
        </li>
        <li class="flex items-center gap-2 text-gray-300">
          <span class="text-blue-500">🔄</span>
          Ciclo actual: ${cicloPomodoro}
        </li>
      `;
    })
    .catch(error => {
      console.error("Error al cargar productividad con API principal, intentando alternativa:", error);
      // Intentar con la API alternativa
      fetch("/planner/obtener-estadisticas-productividad/")
        .then(response => response.json())
        .then(data => {
          const resumen = document.getElementById("resumen-productividad");
          const bloquesEstudio = data.bloques_estudio || 0;
          const minutosTotales = data.minutos_totales || 0;
          
          const tiempoTexto = minutosTotales >= 60
            ? `${Math.floor(minutosTotales / 60)}h ${minutosTotales % 60}m`
            : `${minutosTotales}m`;

          resumen.innerHTML = `
            <li class="flex items-center gap-2 text-gray-300">
              <span class="text-green-500">✅</span>
              ${bloquesEstudio} bloques de estudio completados hoy
            </li>
            <li class="flex items-center gap-2 text-gray-300">
              <span class="text-purple-500">⏱️</span>
              Tiempo Acumulado: ${tiempoTexto}
            </li>
            <li class="flex items-center gap-2 text-gray-300">
              <span class="text-blue-500">🔄</span>
              Ciclo actual: ${cicloPomodoro}
            </li>
          `;
        })
        .catch(fallbackError => {
          console.error("Error al cargar productividad con ambas APIs:", fallbackError);
          // Mostrar valores por defecto en caso de error
          const resumen = document.getElementById("resumen-productividad");
          resumen.innerHTML = `
            <li class="flex items-center gap-2 text-gray-300">
              <span class="text-green-500">✅</span>
              0 bloques de estudio completados hoy
            </li>
            <li class="flex items-center gap-2 text-gray-300">
              <span class="text-purple-500">⏱️</span>
              Tiempo Acumulado: 0m
            </li>
            <li class="flex items-center gap-2 text-gray-300">
              <span class="text-blue-500">🔄</span>
              Ciclo actual: ${cicloPomodoro}
            </li>
          `;
        });
    });
}

function mostrarToast(mensaje = "¡Bloque guardado exitosamente!", tipo = 'success') {
  const toast = document.getElementById("toast");
  
  toast.className = `fixed bottom-8 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-lg opacity-100 pointer-events-none transition-all duration-300 ${
    tipo === 'success' ? 'bg-green-500' : 
    tipo === 'warning' ? 'bg-yellow-500' : 
    tipo === 'info' ? 'bg-blue-500' : 'bg-red-500'
  } text-white`;
  
  toast.textContent = mensaje;
  
  setTimeout(() => {
    toast.classList.remove("opacity-100", "translate-y-0");
    toast.classList.add("opacity-0", "-translate-y-4");
  }, 3000);
}

// Atajos de teclado
document.addEventListener('keydown', function(e) {
  if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'SELECT') {
    switch(e.key) {
      case ' ':
        e.preventDefault();
        if (enMarcha) {
          pausarPomodoro();
        } else {
          iniciarPomodoro();
        }
        break;
      case 'r':
        reiniciarPomodoro();
        break;
      case '1':
        aplicarConfiguracionPredefinida('pomodoro');
        break;
      case '2':
        aplicarConfiguracionPredefinida('bloqueCorto');
        break;
      case '3':
        aplicarConfiguracionPredefinida('bloqueLargo');
        break;
    }
  }
});

document.addEventListener('DOMContentLoaded', function() {
  actualizarTemporizador();
  actualizarResumenProductividad();
  setInterval(actualizarResumenProductividad, 30000);
});
