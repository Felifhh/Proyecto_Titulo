
(function () {
    const sel = document.getElementById('id_vincular_reserva');
    const fecha = document.getElementById('id_fecha');
    const inicio = document.getElementById('id_hora_inicio');
    const fin = document.getElementById('id_hora_fin');
    const ubicacion = document.getElementById('id_ubicacion');

    if (!sel || !fecha || !inicio || !fin || !ubicacion) return;

    sel.addEventListener('change', function () {
        const opt = this.selectedOptions[0];

        if (opt && opt.value) {
            fecha.value = opt.dataset.fecha;
            inicio.value = opt.dataset.inicio;
            fin.value = opt.dataset.fin;

            // Tomar el nombre del espacio desde el texto del option
            ubicacion.value = opt.textContent.split(' — ')[0];
            ubicacion.setAttribute('readonly', true);

            fecha.setAttribute('readonly', true);
            inicio.setAttribute('disabled', true);
            fin.setAttribute('disabled', true);
        } else {
            fecha.removeAttribute('readonly');
            inicio.removeAttribute('disabled');
            fin.removeAttribute('disabled');
            ubicacion.removeAttribute('readonly');

            fecha.value = "";
            inicio.value = "";
            fin.value = "";
            ubicacion.value = "";
        }
    });
})();



