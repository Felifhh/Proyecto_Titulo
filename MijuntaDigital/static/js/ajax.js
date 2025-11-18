document.addEventListener("DOMContentLoaded", () => {
    const contador = document.querySelector(".contador");
    if (!contador) return;

    const proyectoId = contador.dataset.id;

    setInterval(() => {
        fetch(`/proyectos/api/estado/${proyectoId}/`)
            .then(r => r.json())
            .then(data => {
                console.log("Estado proyecto:", data);

                // Si está finalizado → recargar automáticamente
                if (data.cerrado === true) {
                    location.reload();
                }
            })
            .catch(err => console.error("AJAX error:", err));
    }, 5000); // cada 5 segundos
});
