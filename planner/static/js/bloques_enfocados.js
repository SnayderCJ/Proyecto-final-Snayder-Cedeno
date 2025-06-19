// Archivo: static/js/bloques_enfocados.js

let tiempo = 25 * 60;
let enMarcha = false;
let intervalo;

function actualizarTemporizador() {
  const min = Math.floor(tiempo / 60).toString().padStart(2, '0');
  const seg = (tiempo % 60).toString().padStart(2, '0');
  document.getElementById("temporizador").textContent = `${min}:${seg}`;
}

function aplicarConfiguracion() {
  const minutos = parseInt(document.getElementById("inputEnfoque").value) || 25;
  const objetivo = document.getElementById("inputObjetivo").value;

  tiempo = minutos * 60;
  actualizarTemporizador();

  document.getElementById("objetivo-actual").textContent = objetivo === "estudio"
    ? "🎯 Estudio"
    : "🛌 Descanso";
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

function iniciarPomodoro() {
  if (!enMarcha) {
    enMarcha = true;

    intervalo = setInterval(() => {
      if (tiempo > 0) {
        tiempo--;
        actualizarTemporizador();
      } else {
        clearInterval(intervalo);
        enMarcha = false;

        mostrarToast();

        const enfoqueMin = parseInt(document.getElementById("inputEnfoque").value) || 25;
        const tipoBloque = document.getElementById("inputObjetivo").value || "estudio";

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
        })
        .catch(error => {
          console.error("Error al registrar bloque:", error);
        });
      }
    }, 1000);
  }
}

function pausarPomodoro() {
  clearInterval(intervalo);
  enMarcha = false;
}

function reiniciarPomodoro() {
  clearInterval(intervalo);
  tiempo = 25 * 60;
  actualizarTemporizador();
  enMarcha = false;
  document.getElementById("objetivo-actual").textContent = "";
}

function actualizarResumenProductividad() {
  fetch("/planner/api/productividad/")
    .then(response => response.json())
    .then(data => {
      const resumen = document.getElementById("resumen-productividad");
      const tiempoTexto = data.minutos_totales >= 60
        ? `${Math.floor(data.minutos_totales / 60)}h ${data.minutos_totales % 60}m`
        : `${data.minutos_totales}m`;

      resumen.innerHTML = `
        <li class="flex items-center gap-2 text-gray-300">
          <span class="text-green-500">✅</span>
          ${data.bloques_estudio} bloques de estudio completados hoy
        </li>
        <li class="flex items-center gap-2 text-gray-300">
          <span class="text-purple-500">⏱️</span>
          Tiempo Acumulado: ${tiempoTexto}
        </li>
      `;
    })
    .catch(error => {
      console.error("Error al cargar productividad:", error);
    });
}

function mostrarToast() {
  const toast = document.getElementById("toast");
  toast.classList.remove("opacity-0", "-translate-y-4");
  toast.classList.add("opacity-100", "translate-y-0");
  setTimeout(() => {
    toast.classList.remove("opacity-100", "translate-y-0");
    toast.classList.add("opacity-0", "-translate-y-4");
  }, 3000);
}

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
  actualizarTemporizador();
  actualizarResumenProductividad();
});
