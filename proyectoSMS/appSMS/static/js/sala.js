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
     <div id="message-${messageId}" class="flex justify-end mb-2 items-center space-x-2">
        <!-- Contenedor del mensaje -->
        <div class="rounded-xl py-2 px-3 bg-indigo-200 max-w-xs">
            <p class="text-sm mt-1">${message}</p>
            <p class="text-right text-xs text-gray-500 mt-1">${timeString}</p>
        </div>

        <!-- Opciones de mensaje -->
        <div class="message-options relative">
            <button onclick="toggleDropdown('dropdownDots-${messageId}', this)" 
                class="inline-flex items-center p-2 text-sm font-medium text-gray-500 bg-transparent rounded-full hover:opacity-80 focus:outline-none">
                <i class="fa-solid fa-ellipsis-vertical cursor-pointer text-lg text-gray-500 hover:text-gray-700"></i>
            </button>

            <!-- Menú desplegable -->
            <div id="dropdownDots-${messageId}" 
                class="z-50 hidden fixed bg-white divide-y divide-gray-100 rounded-lg shadow-md w-44 p-2">
                <ul class="py-2 text-sm text-gray-700">
                    <li>
                        <button onclick="openMessageDeleteModal('${messageId}', 'forMe')"
                            class="block px-4 py-2 w-full text-left hover:bg-gray-200 whitespace-nowrap">
                            Eliminar para mí
                        </button>
                    </li>
                    <li>
                        <button onclick="openMessageDeleteModal('${messageId}', 'forAll')"
                            class="block px-4 py-2 w-full text-left hover:bg-gray-200 whitespace-nowrap">
                            Eliminar para todos
                        </button>
                    </li>
                </ul>
            </div>
        </div>
    </div>
    `;
    chatLog.insertAdjacentHTML("beforeend", messageHTML);
  } else {
    // Mensaje del receptor
    const messageHTML = `
      <div id="message-${messageId}" class="flex mb-2">
        <div class="rounded-xl py-2 px-3 bg-white max-w-xs">
          <p class="text-sm font-bold text-gray-500">
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
        <img src="${fileUrl}" alt="Imagen adjunta" class="max-w-[50px] max-h-[50px] rounded-lg object-cover" />
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
      <div id="message-${messageId}" class="flex justify-end mb-2 items-center space-x-2">
                <!-- Contenedor del mensaje -->
                <div class="rounded py-2 px-3 bg-indigo-200 max-w-xs">
                    <div class="mt-1">${fileContent}</div>
                    <p class="text-right text-xs text-gray-500 mt-1">${timeString}</p>
                </div>

                <!-- Opciones de mensaje -->
                <div class="message-options relative">
                    <button onclick="toggleDropdown('dropdownDots-${messageId}', this)" 
                        class="inline-flex items-center p-2 text-sm font-medium text-gray-500 bg-transparent rounded-full hover:opacity-80 focus:outline-none">
                        <i class="fa-solid fa-ellipsis-vertical cursor-pointer text-lg text-gray-500 hover:text-gray-700"></i>
                    </button>

                    <!-- Menú desplegable -->
                    <div id="dropdownDots-${messageId}" 
                        class="z-50 hidden fixed bg-white divide-y divide-gray-100 rounded-lg shadow-md w-44 p-2">
                        <ul class="py-2 text-sm text-gray-700">
                            <li>
                                <button onclick="openMessageDeleteModal('${messageId}', 'forMe')"
                                    class="block px-4 py-2 w-full text-left hover:bg-gray-100 whitespace-nowrap">
                                    Eliminar para mí
                                </button>
                            </li>
                            <li>
                                <button onclick="openMessageDeleteModal('${messageId}', 'forAll')"
                                    class="block px-4 py-2 w-full text-left hover:bg-gray-100 whitespace-nowrap">
                                    Eliminar para todos
                                </button>
                            </li>
                        </ul>
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

// Función para mostrar/ocultar el menú "Vaciar Chat"
function toggleChatMenu(event) {
  console.log("toggleChatMenu() se ha ejecutado");

  event.stopPropagation();
  const chatMenu = document.getElementById("chat-menu-options");
  const openModalBtn = document.getElementById("open-modal");
  const openGroupModalBtn = document.getElementById("open-group-modal");

  if (!chatMenu) {
    console.error(
      "Error: No se encontró el elemento chat-menu-options en el DOM."
    );
    return;
  }

  if (chatMenu.classList.contains("hidden")) {
    chatMenu.classList.remove("hidden");
    console.log("Menú de opciones mostrado.");

    // Asegurar que el botón "Vaciar Chat" reaparezca al abrir el menú
    if (openModalBtn) openModalBtn.classList.remove("hidden");
    if (openGroupModalBtn) openGroupModalBtn.classList.remove("hidden");
  } else {
    chatMenu.classList.add("hidden");
    console.log("Menú de opciones ocultado.");
  }

  function closeChatMenu(event) {
    if (!chatMenu.contains(event.target)) {
      chatMenu.classList.add("hidden");
      document.removeEventListener("click", closeChatMenu);
    }
  }

  setTimeout(() => {
    document.addEventListener("click", closeChatMenu);
  }, 100);
}

// Función para vaciar el chat grupal
document.addEventListener("DOMContentLoaded", function () {
  const openGroupModalBtn = document.getElementById("open-group-modal");
  const closeGroupModalBtn = document.getElementById("close-group-modal");
  const confirmDeleteGroupBtn = document.getElementById("confirm-delete-group");
  const modalGroupBackdrop = document.getElementById("modal-group-backdrop");

  // Función para obtener el CSRF Token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Abrir modal y ocultar el botón "Vaciar Chat" en el chat grupal
  if (openGroupModalBtn) {
    openGroupModalBtn.addEventListener("click", function () {
      modalGroupBackdrop.classList.remove("hidden");
      openGroupModalBtn.classList.add("hidden"); // Oculta el botón al abrir el modal
    });
  }

  // Cerrar modal sin mostrar el botón de nuevo
  if (closeGroupModalBtn) {
    closeGroupModalBtn.addEventListener("click", function () {
      modalGroupBackdrop.classList.add("hidden");

      if (
        document
          .getElementById("chat-menu-options")
          .classList.contains("hidden")
      ) {
        openGroupModalBtn.classList.add("hidden");
      }
    });
  }

  // Confirmar eliminación del chat grupal
  if (confirmDeleteGroupBtn) {
    confirmDeleteGroupBtn.addEventListener("click", function () {
      console.log("Nombre del grupo enviado al backend:", groupName);
      fetch(`/delete_group_chat/${groupName}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            document.getElementById("chat-log").innerHTML = ""; // Vaciar el chat
            modalGroupBackdrop.classList.add("hidden"); // Ocultar modal
            openGroupModalBtn.classList.add("hidden");
          } else {
            console.error("Error al vaciar el chat grupal.");
          }
        })
        .catch((error) => console.error("Error:", error));
    });
  }
});

// Función para vaciar el chat individual completo
document.addEventListener("DOMContentLoaded", function () {
  const openModalBtn = document.getElementById("open-modal");
  const closeModalBtn = document.getElementById("close-modal");
  const confirmDeleteBtn = document.getElementById("confirm-delete");
  const modalBackdrop = document.getElementById("modal-backdrop");

  // Función para obtener el CSRF Token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Abrir modal y ocultar botón "Vaciar Chat"
  if (openModalBtn) {
    openModalBtn.addEventListener("click", function () {
      modalBackdrop.classList.remove("hidden");
      openModalBtn.classList.add("hidden"); // Ocultar el botón al abrir el modal
    });
  }

  // Cerrar modal sin mostrar el botón de nuevo
  if (closeModalBtn) {
    closeModalBtn.addEventListener("click", function () {
      modalBackdrop.classList.add("hidden");

      if (
        document
          .getElementById("chat-menu-options")
          .classList.contains("hidden")
      ) {
        openModalBtn.classList.add("hidden");
      }
    });
  }

  // Confirmar eliminación del chat
  if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener("click", function () {
      fetch(`/delete_chat/${roomName}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "success") {
            document.getElementById("chat-log").innerHTML = ""; // Vaciar el chat
            modalBackdrop.classList.add("hidden"); // Ocultar modal
            openModalBtn.classList.add("hidden");
          } else {
            console.error("Error al vaciar el chat.");
          }
        })
        .catch((error) => console.error("Error:", error));
    });
  }
});

// Función para mostrar/ocultar el menú "Cerrar sesión"
function toggleMenuOptions(event) {
  event.stopPropagation(); // Asegura que el evento no cierre el menú inmediatamente

  const menu = document.getElementById("menu-options");
  const chatMenu = document.getElementById("chat-menu-options");

  chatMenu.classList.add("hidden"); // Cierra el otro menú si está abierto
  menu.classList.toggle("hidden"); // Alternar la visibilidad del menú

  // Cierra el menú si se hace clic fuera de él
  document.addEventListener("click", function closeMenu(e) {
    if (!menu.contains(e.target) && e.target.id !== "menu-logout-btn") {
      menu.classList.add("hidden");
      document.removeEventListener("click", closeMenu);
    }
  });
}

// Funcion para el desplegable de eliminar sms para mi/para todos
function toggleDropdown(menuId, button) {
  let dropdown = document.getElementById(menuId);

  if (!dropdown || !button) return;

  // Cierra todos los dropdowns antes de abrir el seleccionado
  document.querySelectorAll("[id^='dropdownDots-']").forEach((menu) => {
    if (menu.id !== menuId) {
      menu.classList.add("hidden");
    }
  });

  // Alternar visibilidad del dropdown
  dropdown.classList.toggle("hidden");

  // Obtener la posición del botón de los tres puntos
  let buttonRect = button.getBoundingClientRect();
  let dropdownWidth = dropdown.offsetWidth;
  let dropdownHeight = dropdown.offsetHeight;
  let viewportWidth = window.innerWidth;
  let viewportHeight = window.innerHeight;

  // Calcular posición del menú
  let posX = buttonRect.right + 10; // Mueve el menú a la derecha del botón
  let posY = buttonRect.top;

  // Ajustar si el menú se sale de la pantalla por la derecha
  if (posX + dropdownWidth > viewportWidth) {
    posX = buttonRect.left - dropdownWidth - 10;
  }

  // Ajustar si el menú se sale de la pantalla por abajo
  if (posY + dropdownHeight > viewportHeight) {
    posY = viewportHeight - dropdownHeight - 10;
  }

  // Aplicar posición al menú
  dropdown.style.left = `${posX}px`;
  dropdown.style.top = `${posY}px`;
}

// Cerrar dropdown si el usuario hace clic fuera
document.addEventListener("click", function (event) {
  let isClickInside = event.target.closest(".message-options");

  if (!isClickInside) {
    document.querySelectorAll("[id^='dropdownDots-']").forEach((menu) => {
      menu.classList.add("hidden");
    });
  }
});

//Función eliminar sms para mi/eliminar sms para todos uno a uno
// Variables globales
let currentMessageId = null;
let deleteType = null;

document.addEventListener("DOMContentLoaded", function () {
  const messageModal = document.getElementById("message-delete-modal");
  const messageModalTitle = document.getElementById("message-modal-title");
  const messageModalText = document.getElementById("message-modal-text");
  const messageCloseModalBtn = document.getElementById("message-close-modal");
  const messageConfirmDeleteBtn = document.getElementById(
    "message-confirm-delete"
  );

  //  Comprueba que el modal está listo para usar
  if (!messageModal || !messageConfirmDeleteBtn || !messageCloseModalBtn) {
    console.error("Error: No se encontraron los elementos del modal.");
    return;
  }

  //  Abre el modal
  window.openMessageDeleteModal = function (messageId, type) {
    console.log(
      "Abriendo modal de eliminación de mensaje para:",
      messageId,
      type
    );

    currentMessageId = messageId; // Guarda el ID del mensaje
    deleteType = type; // Guarda si es "Eliminar para mí" o "Eliminar para todos"

    //  Verifica si el modal existe antes de manipular
    if (!messageModal) {
      console.error("Error: El modal no está en el DOM.");
      return;
    }

    // Mensaje dependiendo de si es para mi o para todos
    if (type === "forMe") {
      messageModalTitle.textContent = "¿Desea eliminar este mensaje para ti?";
      messageModalText.textContent = "Este mensaje se eliminará solo para ti";
    } else if (type === "forAll") {
      messageModalTitle.textContent =
        "¿Desea eliminar este mensaje para todos?";
      messageModalText.textContent = "Este mensaje se eliminará para todos";
    }

    // Mostrar el modal eliminando la clase "hidden"
    messageModal.classList.remove("hidden");

    console.log("Modal mostrado correctamente.");
  };

  // Evento para confirmar eliminación (solo se ejecuta al hacer clic en "Eliminar")
  messageConfirmDeleteBtn.addEventListener("click", function () {
    if (!currentMessageId) {
      console.error("Error: No hay mensaje seleccionado para eliminar.");
      return;
    }

    console.log(
      "Confirmando eliminación del mensaje:",
      currentMessageId,
      deleteType
    );

    if (deleteType === "forMe") {
      window.deleteMessage(currentMessageId);
    } else if (deleteType === "forAll") {
      window.deleteMessageForAll(currentMessageId);
    }

    // Ocultar el modal después de la eliminación
    messageModal.classList.add("hidden");
    currentMessageId = null;
    deleteType = null;
  });

  // Evento para cerrar el modal al hacer clic en "Cancelar"
  messageCloseModalBtn.addEventListener("click", function () {
    console.log("Cancelando eliminación del mensaje");
    messageModal.classList.add("hidden");

    // Reiniciar variables globales
    currentMessageId = null;
    deleteType = null;
  });
});

// Funciones globales para eliminar de eliminar para mi/eliminar para todos sms uno a uno (al final del archivo, fuera del DOMContentLoaded)
window.deleteMessage = function (messageId) {
  console.log("Ejecutando deleteMessage para:", messageId);

  const messageElement = document.getElementById(`message-${messageId}`);
  if (messageElement) {
    const deleteUrl = isGroupChat
      ? `/delete_group_message/${messageId}/`
      : `/delete_private_message/${messageId}/`;

    fetch(deleteUrl, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          messageElement.remove();
          console.log("Mensaje eliminado para mi.");
        } else {
          console.error("Error al eliminar el mensaje.");
        }
      })
      .catch((error) => console.error("Error en la solicitud:", error));
  }
};

window.deleteMessageForAll = function (messageId) {
  console.log("Ejecutando deleteMessageForAll para:", messageId);

  const messageElement = document.getElementById(`message-${messageId}`);
  if (messageElement) {
    const deleteUrl = isGroupChat
      ? `/delete_group_message_for_all/${messageId}/`
      : `/delete_private_message_for_all/${messageId}/`;

    fetch(deleteUrl, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          messageElement.remove();
          console.log("Mensaje eliminado para todos.");
        } else {
          console.error("Error al eliminar el mensaje para todos.");
        }
      })
      .catch((error) => console.error("Error en la solicitud:", error));
  }
};
