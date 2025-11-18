document.addEventListener("DOMContentLoaded", () => {
    const elementos = document.querySelectorAll(".contador");

    elementos.forEach(el => {
        let segundos = parseInt(el.dataset.segundos);

        function actualizar() {
            if (segundos <= 0) {
                el.innerHTML = "Finalizado";
                return;
            }

            let d = Math.floor(segundos / 86400);
            let h = Math.floor((segundos % 86400) / 3600);
            let m = Math.floor((segundos % 3600) / 60);
            let s = segundos % 60;

            el.innerHTML =
                `${d}d ${h}h ${m}m ${s}s`;

            segundos--;
            setTimeout(actualizar, 1000);
        }

        actualizar();
    });
});
