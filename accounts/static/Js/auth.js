document.addEventListener("DOMContentLoaded", function () {
    const toasts = document.querySelectorAll(".custom-toast");

    toasts.forEach(toast => {
      setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transition = "opacity 0.5s ease";
        setTimeout(() => toast.remove(), 500); // Se elimina del DOM
      }, 5000); // Tiempo en milisegundos antes de desaparecer (5 segundos)
    });
  });