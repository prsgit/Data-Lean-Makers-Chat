// Función para obtener el valor de una cookie por su nombre
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Comprueba si esta cookie comienza con el nombre que buscamos
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Configuración del WebSocket para el sala.html
const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";

// Verificar si es un chat grupal o privado
const isGroupChat =
  typeof groupName !== "undefined" && groupName !== null && groupName !== "";

// ruta de conexión
let chatSocket;
if (isGroupChat) {
  chatSocket = new WebSocket(
    protocol + window.location.host + `/ws/group/${groupName}/`
  );
} else if (
  typeof roomName !== "undefined" &&
  roomName !== null &&
  roomName !== ""
) {
  chatSocket = new WebSocket(
    protocol + window.location.host + `/ws/chat/${roomName}/`
  );
} else {
  console.error(
    "No se puede establecer la conexión WebSocket: los datos no son válidos."
  );
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
      <div class="message ${
        isMyMessage ? "my-message" : "other-message float-right"
      }">
        <strong>${isMyMessage ? "Yo" : sender}:</strong> ${message}
      </div>
    `;

  chatLog.appendChild(newMessage);
  chatLog.scrollTop = chatLog.scrollHeight;
}

// Función para agregar archivos adjuntos al chat
function appendFile(sender, fileUrl, isMyMessage) {
  const chatLog = document.querySelector("#chat-log");
  const newMessage = document.createElement("li");
  const currentTime = new Date();
  const hours = currentTime.getHours().toString().padStart(2, "0");
  const minutes = currentTime.getMinutes().toString().padStart(2, "0");
  const timeString = `${hours}:${minutes}`;

  // Detectar si el archivo es una imagen o un video
  const isImage = /\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(fileUrl);
  const isVideo = /\.(mp4|avi|mov|mkv)$/i.test(fileUrl);

  let fileContent;
  if (isImage) {
    // Mostrar imagen como vista previa
    fileContent = `
       <a href="${fileUrl}" target="_blank">
        <img src="${fileUrl}" alt="Imagen adjunta" style="max-width: 100px; max-height: 100px; border-radius: 5px;" />
      </a>
    `;
  } else if (isVideo) {
    // Mostrar video como vista previa
    fileContent = `
       <a href="${fileUrl}" target="_blank">
        <video controls style="max-width: 200px; max-height: 150px; border-radius: 5px;">
          <source src="${fileUrl}" type="video/mp4">
          Tu navegador no soporta la etiqueta de video.
        </video>
      </a>
    `;
  } else {
    // enlace de descarga para otros archivos
    fileContent = `<a href="${fileUrl}" download target="_blank" class="file-link">Descargar</a>`;
  }

  newMessage.innerHTML = `
      <div class="message-data ${isMyMessage ? "text-right" : ""}">
        <span class="message-data-time">${timeString}</span>
      </div>
      <div class="message ${
        isMyMessage ? "my-message" : "other-message float-right"
      }">
        <strong>${isMyMessage ? "Yo" : sender}:</strong>
        ${fileContent}
      </div>
    `;

  chatLog.appendChild(newMessage);
  chatLog.scrollTop = chatLog.scrollHeight;
}

// Recibir mensajes del servidor
chatSocket.onmessage = function (e) {
  const data = JSON.parse(e.data);
  console.log("Datos recibidos:", data); //datos recibidos

  if (data.message && data.sender) {
    appendMessage(data.sender, data.message, data.sender === username);
  }
  if (data.file_url && data.sender) {
    console.log("URL del archivo:", data.file_url); //  URL del archivo recibido
    appendFile(data.sender, data.file_url, data.sender === username);
  }
};

chatSocket.onclose = function (e) {
  console.error("Chat socket cerrado inesperadamente");
};

// Manejo del envio
document.addEventListener("DOMContentLoaded", function () {
  const messageSubmit = document.querySelector("#chat-message-submit");
  const messageInput = document.querySelector("#chat-message-input");
  const fileInput = document.querySelector("#chat-file-input");
  const fileButton = document.querySelector("#chat-file-button");

  // para abrir el selector de archivos
  fileButton.onclick = function (e) {
    e.preventDefault();
    fileInput.click();
  };

  // Manejo del envío del mensaje o archivo
  messageSubmit.onclick = function (e) {
    e.preventDefault();

    const message = messageInput.value.trim();
    const file = fileInput && fileInput.files[0]; // Verifica si hay un archivo seleccionado

    if (message === "" && !file) {
      // Si no hay ni mensaje ni archivo, no hace nada
      return;
    }

    const data = {
      message: message || "", // Enviar el mensaje, aunque sea vacío si hay archivo
    };

    if (file) {
      const reader = new FileReader();
      reader.onload = function (event) {
        console.log("Archivo cargado en Base64:", event.target.result); // Verifica el contenido del archivo
        data.file_url = event.target.result; // Agregar contenido del archivo
        chatSocket.send(JSON.stringify(data)); // Enviar el mensaje con el archivo
      };
      reader.readAsDataURL(file); // Leer archivo como Base64
    } else {
      chatSocket.send(JSON.stringify(data)); // Enviar solo el mensaje si no hay archivo
    }

    messageInput.value = ""; // Limpiar campo de texto
    if (fileInput) fileInput.value = ""; // Limpiar campo de archivo
  };

  // Enviar mensaje al presionar Enter
  messageInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
      // Detectar Enter sin Shift
      e.preventDefault();
      messageSubmit.click();
    }
  });
});

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
        hasResults = hasResults || userName.includes(filter); // se actualiza hasResults a True si hay un usuario que coincida
      }
    }

    // Filtrar grupos
    for (let i = 0; i < groups.length; i++) {
      const groupNameElement = groups[i].querySelector(".name");
      if (groupNameElement) {
        const groupName = groupNameElement.textContent.toLowerCase();
        groups[i].style.display = groupName.includes(filter) ? "" : "none"; // Mostrar u ocultar según coincidencia
        hasResults = hasResults || groupName.includes(filter); // Actualizar hasResults
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

// Función para los desplegables de grupos y chats individuales
document.addEventListener("DOMContentLoaded", function () {
  const sections = ["group-list", "user-list"];

  sections.forEach((sectionId) => {
    const section = document.getElementById(sectionId);
    const estado = localStorage.getItem(sectionId);
    if (estado === "abierto") {
      section.classList.add("active");
    } else {
      section.classList.remove("active");
    }
  });
});

// Función para abrir y cerrar desplegables
function toggleSection(sectionId, element) {
  const section = document.getElementById(sectionId);
  if (section) {
    section.classList.toggle("active");
    const icon = element.querySelector(".toggle-icon");
    if (icon) {
      icon.classList.toggle("fa-chevron-down");
      icon.classList.toggle("fa-chevron-up");
    }
    // Guardar el estado en localStorage
    const estado = section.classList.contains("active") ? "abierto" : "cerrado";
    localStorage.setItem(sectionId, estado);
  }
}

// Función para vaciar el chat
document.addEventListener("DOMContentLoaded", function () {
  const deleteGroupChatButton = document.getElementById("delete-group-chat");

  if (deleteGroupChatButton) {
    deleteGroupChatButton.onclick = function () {
      fetch(`/delete_group_chat/${groupName}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      })
        .then(response => response.json())
        .then(data => {
          if (data.status === "success") {
            // Limpiar el historial de chat en la interfaz
            const chatLog = document.getElementById("chat-log");
            chatLog.innerHTML = "";
          } else {
            console.error("Error al vaciar el chat grupal");
          }
        });
    };
  }
});

// Función para vaciar el chat individual
document.addEventListener("DOMContentLoaded", function () {
  const deleteChatButton = document.getElementById("delete-chat");
  const roomName = document.getElementById("room-name").value; // Obtener el roomName del input oculto

  if (deleteChatButton) {
    deleteChatButton.onclick = function () {
      fetch(`/delete_chat/${roomName}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      })
        .then(response => response.json())
        .then(data => {
          if (data.status === "success") {
            // Limpiar el historial de chat en la interfaz
            const chatLog = document.getElementById("chat-log");
            chatLog.innerHTML = "";
          } else {
            console.error("Error al vaciar el chat individual");
          }
        });
    };
  }
});

