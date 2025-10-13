// ===============================
// mostrar_monto_catalogo.js
// Cálculo de monto por hora completa (redondeo hacia arriba)
// ===============================

document.addEventListener("DOMContentLoaded", function () {
  const horaInicioInput = document.getElementById("id_hora_inicio");
  const horaFinInput = document.getElementById("id_hora_fin");
  const montoLabel = document.getElementById("monto-total");
  const montoHora = parseFloat(document.getElementById("monto-hora-data").textContent.trim()) || 0;

  // Campo oculto para enviar el monto total
  const montoOculto = document.createElement("input");
  montoOculto.type = "hidden";
  montoOculto.name = "monto_calculado";
  document.querySelector("form").appendChild(montoOculto);

  function calcularMonto() {
    const horaInicio = horaInicioInput.value;
    const horaFin = horaFinInput.value;

    if (!horaInicio || !horaFin) {
      montoLabel.textContent = "—";
      return;
    }

    const inicio = new Date(`1970-01-01T${horaInicio}:00`);
    const fin = new Date(`1970-01-01T${horaFin}:00`);
    const diffHoras = (fin - inicio) / (1000 * 60 * 60);

    if (diffHoras <= 0) {
      montoLabel.textContent = "Horario inválido";
      montoLabel.style.color = "red";
      return;
    }

    // 🔹 Redondeo hacia arriba para cobrar horas completas
    const horasCobradas = Math.ceil(diffHoras);
    const total = horasCobradas * montoHora;

    montoLabel.textContent = `$${total.toLocaleString("es-CL")} (${horasCobradas} hora${horasCobradas > 1 ? 's' : ''})`;
    montoLabel.style.color = "var(--color-text)";
    montoOculto.value = total;
  }

  [horaInicioInput, horaFinInput].forEach(el =>
    el.addEventListener("change", calcularMonto)
  );
});
