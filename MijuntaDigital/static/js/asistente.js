function toggleChatbot() {
  const windowEl = document.getElementById("chatbot-window");
  const isVisible = windowEl.style.display === "flex";
  windowEl.style.display = isVisible ? "none" : "flex";

  if (!isVisible) {
    cargarConversacion(); // 👈 restaura historial al abrir
  }
}

async function sendMessage() {
  const input = document.getElementById("user-input");
  const messagesDiv = document.getElementById("chatbot-messages");
  const mensaje = input.value.trim();
  if (!mensaje) return;

  // Crear mensaje del usuario
  const userMsg = document.createElement("div");
  userMsg.classList.add("user-message");
  userMsg.textContent = mensaje;
  messagesDiv.appendChild(userMsg);
  input.value = "";

  guardarMensaje("user", mensaje);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;

  // Mostrar "pensando..."
  const botMsg = document.createElement("div");
  botMsg.classList.add("bot-message");
  botMsg.textContent = "Pensando...";
  messagesDiv.appendChild(botMsg);

  try {
    const res = await fetch(`/chatbot/api/?mensaje=${encodeURIComponent(mensaje)}`);
    const data = await res.json();

    botMsg.innerHTML = data.respuesta || "Lo siento, no entendí tu pregunta.";
    guardarMensaje("bot", data.respuesta);

    // Si el backend pide acción (ej. pago)
    if (data.accion === "redirigir_pago") {
      window.location.href = "/pagos/iniciar/";
    }

  } catch (err) {
    botMsg.textContent = "Error al conectar con el asistente.";
  }

  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

/* ==============================
   🧠 NUEVAS FUNCIONES DE HISTORIAL LOCAL
   ============================== */

function guardarMensaje(role, content) {
  let historial = JSON.parse(localStorage.getItem("chat_historial")) || [];
  historial.push({ role, content });
  localStorage.setItem("chat_historial", JSON.stringify(historial));
}

function cargarConversacion() {
  const messagesDiv = document.getElementById("chatbot-messages");
  messagesDiv.innerHTML = "";
  const historial = JSON.parse(localStorage.getItem("chat_historial")) || [];

  historial.forEach(msg => {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add(msg.role === "user" ? "user-message" : "bot-message");
    msgDiv.innerHTML = msg.content;
    messagesDiv.appendChild(msgDiv);
  });

  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function limpiarConversacion() {
  localStorage.removeItem("chat_historial");
  document.getElementById("chatbot-messages").innerHTML = "";
}

/* ==============================
   🚀 RECUPERAR CHAT AL CARGAR PÁGINA
   ============================== */
document.addEventListener("DOMContentLoaded", () => {
  // Crea el contenedor si no existe (por si el HTML no lo ha renderizado todavía)
  const messagesDiv = document.getElementById("chatbot-messages");
  if (messagesDiv) {
    cargarConversacion();
  }
});

function toggleChatbot() {
  const windowEl = document.getElementById("chatbot-window");
  const isVisible = windowEl.style.display === "flex";
  windowEl.style.display = isVisible ? "none" : "flex";
  localStorage.setItem("chat_abierto", !isVisible);
  if (!isVisible) cargarConversacion();
}

// Restaurar estado al cargar
document.addEventListener("DOMContentLoaded", () => {
  if (localStorage.getItem("chat_abierto") === "true") {
    document.getElementById("chatbot-window").style.display = "flex";
    cargarConversacion();
  }
});
