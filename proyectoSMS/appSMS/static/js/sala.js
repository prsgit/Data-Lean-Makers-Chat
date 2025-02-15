// Función para obtener el valor de una cookie por su nombre
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Comprueba si esta cookie comienza con el nombre que buscamos
      if (cookie.substring(0, name.length + 1) === name + "=") {
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

//Función de agregar mensajes al chat
function appendMessage(sender, message, isMyMessage, messageId) {
  const chatLog = document.querySelector("#chat-log");
  const currentTime = new Date();
  const timeString = currentTime.toLocaleTimeString("es-ES", {
    hour: "2-digit",
    minute: "2-digit",
    hour24: true,
  });

  if (isMyMessage) {
    // Mensaje del emisor
    const messageHTML = `
      <div id="message-${messageId}" class="flex justify-end mb-2">
        <div class="rounded py-2 px-3 bg-[#E2F7CB] max-w-xs">
          <p class="text-sm mt-1">
            ${message}
          </p>
          <p class="text-right text-xs text-gray-500 mt-1">
            ${timeString}
          </p>
          <div class="message-options relative mt-1">
            <span class="options-icon text-gray-400 cursor-pointer text-sm"
                  onclick="toggleMenu('${messageId}')">
              &#x2026;
            </span>
            <div class="options-menu absolute right-0 bg-white shadow-md rounded-md p-2 hidden"
                 id="menu-${messageId}">
              <button class="block text-sm text-gray-700 hover:bg-gray-200 px-2 py-1 rounded-md w-full"
                      onclick="deleteMessage('${messageId}')">
                Eliminar para mí
              </button>
              <button class="block text-sm text-red-600 hover:bg-red-100 px-2 py-1 rounded-md w-full"
                      onclick="deleteMessageForAll('${messageId}')">
                Eliminar para todos
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
    chatLog.insertAdjacentHTML("beforeend", messageHTML);
  } else {
    // Mensaje del receptor
    const messageHTML = `
      <div id="message-${messageId}" class="flex mb-2">
        <div class="rounded py-2 px-3 bg-[#F2F2F2] max-w-xs">
          <p class="text-sm font-bold text-teal-700">
            ${sender}
          </p>
          <p class="text-sm mt-1">
            ${message}
          </p>
          <p class="text-right text-xs text-gray-500 mt-1">
            ${timeString}
          </p>
        </div>
      </div>
    `;
    chatLog.insertAdjacentHTML("beforeend", messageHTML);
  }

  chatLog.scrollTop = chatLog.scrollHeight;
}

// Funcion para agregar archivos al chat
function appendFile(sender, fileUrl, isMyMessage, messageId) {
  const chatLog = document.querySelector("#chat-log");
  const currentTime = new Date();
  const timeString = currentTime.toLocaleTimeString("es-ES", {
    hour: "2-digit",
    minute: "2-digit",
    hour24: true,
  });

  // Detectar tipo de archivo
  const isImage = /\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(fileUrl);
  const isVideo = /\.(mp4|avi|mov|mkv)$/i.test(fileUrl);

  // Preparar el contenido del archivo según su tipo
  let fileContent;
  if (isImage) {
    fileContent = `
      <a href="${fileUrl}" target="_blank" class="inline-block">
        <img src="${fileUrl}" alt="Imagen adjunta" class="max-w-[100px] max-h-[100px] rounded-lg object-cover" />
      </a>
    `;
  } else if (isVideo) {
    fileContent = `
      <a href="${fileUrl}" target="_blank" class="inline-block">
        <video controls class="max-w-[130px] max-h-[130px] rounded-lg">
          <source src="${fileUrl}" type="video/mp4">
          Tu navegador no soporta la etiqueta de video.
        </video>
      </a>
    `;
  } else {
    fileContent = `
      <a href="${fileUrl}" download target="_blank" 
         class="inline-flex items-center px-3 py-2 text-sm font-medium text-blue-600 bg-blue-100 rounded-lg hover:bg-blue-200">
        <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
          <path d="M13 8V2H7v6H2l8 8 8-8h-5zM0 18h20v2H0v-2z"/>
        </svg>
        Descargar archivo
      </a>
    `;
  }

  if (isMyMessage) {
    // Mensaje del emisor
    const messageHTML = `
      <div id="message-${messageId}" class="flex justify-end mb-2">
        <div class="rounded py-2 px-3 bg-[#E2F7CB] max-w-xs">
          <div class="mt-1">
            ${fileContent}
          </div>
          <p class="text-right text-xs text-gray-500 mt-1">
            ${timeString}
          </p>
          <div class="message-options relative mt-1">
            <span class="options-icon text-gray-400 cursor-pointer text-sm"
                  onclick="toggleMenu('${messageId}')">
              &#x2026;
            </span>
            <div class="options-menu absolute right-0 bg-white shadow-md rounded-md p-2 hidden"
                 id="menu-${messageId}">
              <button class="block text-sm text-gray-700 hover:bg-gray-200 px-2 py-1 rounded-md w-full"
                      onclick="deleteMessage('${messageId}')">
                Eliminar para mí
              </button>
              <button class="block text-sm text-red-600 hover:bg-red-100 px-2 py-1 rounded-md w-full"
                      onclick="deleteMessageForAll('${messageId}')">
                Eliminar para todos
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
    chatLog.insertAdjacentHTML("beforeend", messageHTML);
  } else {
    // Mensaje del receptor
    const messageHTML = `
      <div id="message-${messageId}" class="flex mb-2">
        <div class="rounded py-2 px-3 bg-[#F2F2F2] max-w-xs">
          <p class="text-sm font-bold text-teal-700">
            ${sender}
          </p>
          <div class="mt-1">
            ${fileContent}
          </div>
          <p class="text-right text-xs text-gray-500 mt-1">
            ${timeString}
          </p>
        </div>
      </div>
    `;
    chatLog.insertAdjacentHTML("beforeend", messageHTML);
  }

  chatLog.scrollTop = chatLog.scrollHeight;
}

// Recibir mensajes del servidor
chatSocket.onmessage = function (e) {
  const data = JSON.parse(e.data);
  console.log("Datos recibidos:", data); //datos recibidos

  const messageId = data.message_id; // Captura el ID del mensaje del objeto recibido

  if (data.type === "delete_for_all" && messageId) {
    // Manejar la eliminación para todos
    const messageElement = document.getElementById(`message-${messageId}`);
    if (messageElement) {
      messageElement.remove();
    }
    // Si hay un archivo relacionado, eliminar su vista
    if (data.file_url) {
      console.log(`Archivo eliminado de la vista: ${data.file_url}`);
    }
    return;
  }

  // Manejar la eliminación solo para el emisor no afecta al receptor
  if (data.type === "delete_for_me" && messageId) {
    const messageElement = document.getElementById(`message-${messageId}`);
    if (messageElement) {
      messageElement.remove();
    }
    return;
  }

  if (data.message && data.sender) {
    appendMessage(
      data.sender,
      data.message,
      data.sender === username,
      messageId
    );
  }
  if (data.file_url && data.sender) {
    console.log("URL del archivo:", data.file_url); //  URL del archivo recibido
    const fileMessageId = data.message_id; // Captura el ID del mensaje relacionado con el archivo

    appendFile(
      data.sender,
      data.file_url,
      data.sender === username,
      fileMessageId
    );
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
    if (hasResults) {
      noResultsMessage.classList.add("hidden");
    } else {
      noResultsMessage.classList.remove("hidden");
    }
  }

  // Busca al escribir en el input
  if (searchInput) {
    searchInput.addEventListener("input", filterItems);
  }
});

// Función para vaciar el chat grupal completo
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
        .then((response) => response.json())
        .then((data) => {
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

// Función para vaciar el chat individual completo
document.addEventListener("DOMContentLoaded", function () {
  const deleteChatButton = document.getElementById("delete-chat");
  // const roomName = document.getElementById("room-name").value; // Obtener el roomName del input oculto

  if (deleteChatButton) {
    deleteChatButton.onclick = function () {
      fetch(`/delete_chat/${roomName}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      })
        .then((response) => response.json())
        .then((data) => {
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

// Función para menu cerrar sesion
function toggleMenuOptions() {
  const menu = document.getElementById("menu-options");
  menu.classList.toggle("hidden"); // Alternar la visibilidad del menú

  // Cerrar el menú si se hace clic fuera
  document.addEventListener("click", function closeMenu(event) {
    if (!menu.contains(event.target) && event.target.closest("i") === null) {
      menu.classList.add("hidden");
      document.removeEventListener("click", closeMenu);
    }
  });
}

// Función para mostrar/ocultar el menú "Vaciar Chat"
function toggleChatMenu() {
  const chatMenu = document.getElementById("chat-menu-options");
  chatMenu.classList.toggle("hidden"); // Alternar la visibilidad del menú

  // Cerrar el menú si se hace clic fuera
  document.addEventListener("click", function closeChatMenu(event) {
    if (
      !chatMenu.contains(event.target) &&
      event.target.closest("i") === null
    ) {
      chatMenu.classList.add("hidden");
      document.removeEventListener("click", closeChatMenu);
    }
  });
}

// Función para mostrar/ocultar el menú de opciones
function toggleMenu(messageId) {
  const menu = document.querySelector(`#menu-${messageId}`);
  const allMenus = document.querySelectorAll(".options-menu");

  // Cerrar todos los otros menús
  allMenus.forEach((m) => {
    if (m.id !== `menu-${messageId}`) {
      m.classList.add("hidden");
    }
  });

  // Toggle del menú actual
  menu.classList.toggle("hidden");
}

// Función "eliminar para mi", tanto para chat individual y grupal
function deleteMessage(messageId) {
  const messageElement = document.getElementById(`message-${messageId}`);
  if (messageElement) {
    // Determinar la URL según el tipo de chat
    const deleteUrl = isGroupChat
      ? `/delete_group_message/${messageId}/` // Ruta para mensajes grupales
      : `/delete_private_message/${messageId}/`; // Ruta para mensajes privados

    // Llamada al servidor para eliminar el mensaje
    fetch(deleteUrl, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          // Elimina el mensaje del DOM si la operación fue exitosa
          messageElement.remove();
        } else {
          console.error("Error al eliminar el mensaje");
        }
      })
      .catch((error) => console.error("Error en la solicitud:", error));
  }
}

// Función "eliminar para todos"
function deleteMessageForAll(messageId) {
  const messageElement = document.getElementById(`message-${messageId}`);
  if (messageElement) {
    // Determinar la URL según el tipo de chat
    const deleteUrl = isGroupChat
      ? `/delete_group_message_for_all/${messageId}/` // Ruta para eliminar mensajes grupales
      : `/delete_private_message_for_all/${messageId}/`; // Ruta para eliminar mensajes privados

    // Llamada al servidor para eliminar el mensaje para todos
    fetch(deleteUrl, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          // Elimina el mensaje del DOM si la operación fue exitosa
          messageElement.remove();
          if (data.file_url) {
            console.log(`Archivo eliminado de la vista: ${data.file_url}`);
          }
        } else {
          console.error("Error al eliminar el mensaje para todos");
        }
      })
      .catch((error) => console.error("Error en la solicitud:", error));
  }
}
