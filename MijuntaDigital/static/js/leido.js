document.addEventListener("DOMContentLoaded", function() {
  const notiLinks = document.querySelectorAll(".marcar-leida");
  notiLinks.forEach(link => {
    link.addEventListener("click", function(e) {
      e.preventDefault();
      const id = this.dataset.id;

      fetch(`/notificaciones/marcar-leida/${id}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      })
      .then(response => response.json())
      .then(data => {
        if (data.ok) {
          // Oculta el contador o actualiza su número
          const badge = document.querySelector(".badge.bg-danger");
          if (badge) {
            let count = parseInt(badge.textContent.trim());
            count = Math.max(0, count - 1);
            badge.textContent = count;
            if (count === 0) badge.remove();
          }
          // Cambia el color visual del item
          this.classList.add("text-muted");
        }
      });
    });
  });

  // Helper para obtener el token CSRF
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});

