// configuración del websocket para el sala.html

const protocol = window.location.protocol === "https:" ? "wss://" : "ws://"; // Determinar el protocolo
const chatSocket = new WebSocket(
  protocol + window.location.host + "/ws/chat/" + roomName + "/" // Conectar al WebSocket usando roomName
);

chatSocket.onopen = function (e) {
  console.log("Conexión WebSocket abierta");
};

chatSocket.onerror = function (e) {
  console.error("Error en la conexión WebSocket: ", e);
};

// Función para agregar mensajes al chat
function appendMessage(sender, message, isMyMessage) {
  const chatLog = document.querySelector("#chat-log"); // contenedor de mensajes
  const newMessage = document.createElement("li"); // Crear un nuevo elemento de lista para el mensaje

  // Obtener la hora actual para mostrarla junto al mensaje
  const currentTime = new Date();
  const hours = currentTime.getHours().toString().padStart(2, "0");
  const minutes = currentTime.getMinutes().toString().padStart(2, "0");
  const timeString = `${hours}:${minutes}`;

  // HTML para el nuevo mensaje
  newMessage.innerHTML = `
      <div class="message-data ${isMyMessage ? "text-right" : ""}">
        <span class="message-data-time">${timeString}</span>
      </div>
      <div class="message ${
        isMyMessage ? "my-message" : "other-message float-right"
      }">
        <strong>${isMyMessage ? "Yo" : sender}:</strong> ${message}
      </div>
    `;

  chatLog.appendChild(newMessage); // Añadir el nuevo mensaje al log de chat
  chatLog.scrollTop = chatLog.scrollHeight; // Desplazar hacia abajo para mostrar el nuevo mensaje
}

chatSocket.onmessage = function (e) {
  const data = JSON.parse(e.data); // Parsear el mensaje recibido
  appendMessage(data.sender, data.message, data.sender === username); // Añadir el mensaje al chat
};

chatSocket.onclose = function (e) {
  console.error("Chat socket cerrado inesperadamente");
};

// Manejo del enfoque en el campo de entrada
document.querySelector("#chat-message-input").focus();
document.querySelector("#chat-message-input").onkeyup = function (e) {
  if (e.keyCode === 13) {
    // Si se presiona Enter
    document.querySelector("#chat-message-submit").click(); // Simula clic en enviar
  }
};

document.querySelector("#chat-message-submit").onclick = function (e) {
  const messageInputDom = document.querySelector("#chat-message-input"); // Selector del campo de entrada
  const message = messageInputDom.value; // Obtener el valor del mensaje

  // Validación para evitar enviar mensajes vacíos o solo espacios
  if (message.trim() !== "") {
    chatSocket.send(
      JSON.stringify({
        message: message, // Enviar el mensaje al servidor
      })
    );
    messageInputDom.value = ""; // Limpiar el campo de entrada
  }
};

// ###########################################################################################

// Para buscar usuarios en el search

document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("search-input");
  const searchButton = document.getElementById("search-button");
  const userList = document.getElementById("user-list");
  const users = userList.getElementsByTagName("li");
  const noResultsMessage = document.getElementById("no-results");

  function filterUsers() {
    const filter = searchInput.value.toLowerCase();
    let hasResults = false; // Variable para comprobar si hay resultados

    for (let i = 0; i < users.length; i++) {
      const userName = users[i]
        .querySelector(".name")
        .textContent.toLowerCase();
      if (userName.includes(filter)) {
        users[i].style.display = ""; // Muestra el usuario si coincide
        hasResults = true; // Hay al menos un resultado
      } else {
        users[i].style.display = "none"; // Oculta el usuario si no coincide
      }
    }

    // Muestra u oculta el mensaje "Sin resultados"
    noResultsMessage.style.display = hasResults ? "none" : "block";
  }

  // Busca al escribir en el input
  searchInput.addEventListener("input", filterUsers);

  // Busca al hacer clic en la lupa
  searchButton.addEventListener("click", filterUsers);
});
