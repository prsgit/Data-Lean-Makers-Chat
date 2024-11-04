// Configuración del WebSocket para el sala.html
const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";

// Verificar si es un chat grupal o privado
const isGroupChat = typeof groupName !== 'undefined' && groupName !== null && groupName !== "";

// ruta de conexión 
let chatSocket;
if (isGroupChat) {
  chatSocket = new WebSocket(protocol + window.location.host + `/ws/group/${groupName}/`);
} else if (typeof roomName !== 'undefined' && roomName !== null && roomName !== "") {
  chatSocket = new WebSocket(protocol + window.location.host + `/ws/chat/${roomName}/`);
} else {
  console.error("No se puede establecer la conexión WebSocket: los datos no son válidos.");
}

// Conexión WebSocket abierta
chatSocket.onopen = function (e) {
  console.log("Conexión WebSocket abierta");
};

chatSocket.onerror = function (e) {
  console.error("Error en la conexión WebSocket: ", e);
};

// Función para agregar mensajes al chat
function appendMessage(sender, message, isMyMessage) {
  const chatLog = document.querySelector("#chat-log");
  const newMessage = document.createElement("li");
  const currentTime = new Date();
  const hours = currentTime.getHours().toString().padStart(2, "0");
  const minutes = currentTime.getMinutes().toString().padStart(2, "0");
  const timeString = `${hours}:${minutes}`;

  newMessage.innerHTML = `
      <div class="message-data ${isMyMessage ? "text-right" : ""}">
        <span class="message-data-time">${timeString}</span>
      </div>
      <div class="message ${isMyMessage ? "my-message" : "other-message float-right"}">
        <strong>${isMyMessage ? "Yo" : sender}:</strong> ${message}
      </div>
    `;
  
  chatLog.appendChild(newMessage);
  chatLog.scrollTop = chatLog.scrollHeight;
}

// Recibir mensajes del servidor
chatSocket.onmessage = function (e) {
  const data = JSON.parse(e.data);
  if (data.message && data.sender) {
    appendMessage(data.sender, data.message, data.sender === username);
  }
};

chatSocket.onclose = function (e) {
  console.error("Chat socket cerrado inesperadamente");
};

// Manejo del enfoque en el campo de entrada
const messageInput = document.querySelector("#chat-message-input");
const messageSubmit = document.querySelector("#chat-message-submit");

if (messageInput) {
  messageInput.focus();
  messageInput.onkeyup = function (e) {
    if (e.keyCode === 13) {
      messageSubmit.click();
    }
  };

  messageSubmit.onclick = function (e) {
    const message = messageInput.value.trim();
    if (message !== "") {
      chatSocket.send(
        JSON.stringify({
          message: message,
        })
      );
      messageInput.value = "";
    }
  };
}


// ###########################################################################################

// Búsqueda de usuarios y grupos en el input de búsqueda
document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("search-input");
  const userList = document.getElementById("user-list");
  const groupList = document.getElementById("group-list");
  const noResultsMessage = document.getElementById("no-results");

  if (!userList) {
    console.error("No se encontró la lista de usuarios");
    return;
  }

  const users = userList.getElementsByTagName("li");
  const groups = groupList ? groupList.getElementsByTagName("li") : [];

  function filterItems() {
    const filter = searchInput.value.toLowerCase();
    let hasResults = false; // Variable para comprobar si hay resultados

    // Filtrar usuarios
    for (let i = 0; i < users.length; i++) {
      const userNameElement = users[i].querySelector(".name");
      if (userNameElement) {
        const userName = userNameElement.textContent.toLowerCase();
        users[i].style.display = userName.includes(filter) ? "" : "none"; // Mostrar u ocultar según coincidencia
        hasResults = hasResults || (userName.includes(filter)); // Actualizar hasResults
      }
    }

    // Filtrar grupos
    for (let i = 0; i < groups.length; i++) {
      const groupNameElement = groups[i].querySelector(".name");
      if (groupNameElement) {
        const groupName = groupNameElement.textContent.toLowerCase();
        groups[i].style.display = groupName.includes(filter) ? "" : "none"; // Mostrar u ocultar según coincidencia
        hasResults = hasResults || (groupName.includes(filter)); // Actualizar hasResults
      }
    }

    // Muestra u oculta el mensaje "Sin resultados"
    noResultsMessage.style.display = hasResults ? "none" : "block";
  }

  // Busca al escribir en el input
  if (searchInput) {
    searchInput.addEventListener("input", filterItems);
  }
});




// ESTE CÓDIGO FALLA , NO GUARDA LOS SMS ENVAIDOS POR UN GRUPO.
// const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";

// // Verificar si es un chat grupal o privado (se espera que `groupName` o `roomName` estén definidos)
// const isGroupChat = typeof groupName !== 'undefined' && groupName !== null;
// const chatSocket = new WebSocket(
//   protocol + window.location.host + (isGroupChat ? `/ws/group/${groupName}/` : `/ws/chat/${roomName}/`)
// );

// chatSocket.onopen = function (e) {
//   console.log("Conexión WebSocket abierta");
// };

// chatSocket.onerror = function (e) {
//   console.error("Error en la conexión WebSocket: ", e);
// };

// // Función para agregar mensajes al chat
// function appendMessage(sender, message, isMyMessage) {
//   const chatLog = document.querySelector("#chat-log");
//   const newMessage = document.createElement("li");
//   const currentTime = new Date();
//   const hours = currentTime.getHours().toString().padStart(2, "0");
//   const minutes = currentTime.getMinutes().toString().padStart(2, "0");
//   const timeString = `${hours}:${minutes}`;

//   newMessage.innerHTML = `
//       <div class="message-data ${isMyMessage ? "text-right" : ""}">
//         <span class="message-data-time">${timeString}</span>
//       </div>
//       <div class="message ${isMyMessage ? "my-message" : "other-message float-right"}">
//         <strong>${isMyMessage ? "Yo" : sender}:</strong> ${message}
//       </div>
//     `;
  
//   chatLog.appendChild(newMessage);
//   chatLog.scrollTop = chatLog.scrollHeight;
// }

// // Recibir mensajes del servidor
// chatSocket.onmessage = function (e) {
//   const data = JSON.parse(e.data);
//   if (data.message && data.sender) {
//     appendMessage(data.sender, data.message, data.sender === username);
//   }
// };

// chatSocket.onclose = function (e) {
//   console.error("Chat socket cerrado inesperadamente");
// };

// // Manejo del enfoque en el campo de entrada
// const messageInput = document.querySelector("#chat-message-input");
// const messageSubmit = document.querySelector("#chat-message-submit");

// if (messageInput) {
//   messageInput.focus();
//   messageInput.onkeyup = function (e) {
//     if (e.keyCode === 13) {
//       messageSubmit.click();
//     }
//   };

//   messageSubmit.onclick = function (e) {
//     const message = messageInput.value.trim();
//     if (message !== "") {
//       chatSocket.send(
//         JSON.stringify({
//           message: message,
//         })
//       );
//       messageInput.value = "";
//     }
//   };
// }