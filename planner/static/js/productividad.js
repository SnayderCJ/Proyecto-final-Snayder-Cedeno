// Archivo: static/js/productividad.js
document.addEventListener("DOMContentLoaded", function () {
  // Obtener datos desde elementos del DOM
  const dataElement = document.getElementById('productividad-data');
  const dataProductividad = JSON.parse(dataElement.textContent);
  const porcentaje = parseInt(document.getElementById('porcentaje-data').textContent);
  
  const ctx = document.getElementById('graficoProductividad').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
      datasets: [{
        label: 'Nivel de Productividad',
        data: dataProductividad,
        backgroundColor: ['#6EE7B7', '#3B82F6', '#818CF8', '#A78BFA', '#F472B6', '#FBBF24', '#F87171'],
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: '#ddd',
            font: {
              family: "'Inter', sans-serif"
            }
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            color: '#ddd',
            font: {
              family: "'Inter', sans-serif"
            }
          }
        }
      }
    }
  });

  const restante = 100 - porcentaje;

  // Donut grande dinámico
  new Chart(document.getElementById("donutChart"), {
    type: 'doughnut',
    data: {
      labels: ['Productivo', 'Restante'],
      datasets: [{
        data: [porcentaje, restante],
        backgroundColor: ['#A259FF', '#3f3f46'],
        borderWidth: 0,
        cutout: '75%',
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      animation: {
        animateRotate: true,
        duration: 1000,
        onProgress: function(animation) {
          const progress = animation.currentStep / animation.numSteps;
          document.getElementById("donutPorcentaje").textContent = Math.round(porcentaje * progress) + "%";
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  });
});
