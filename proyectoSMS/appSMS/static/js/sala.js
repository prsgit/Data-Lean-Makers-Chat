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
        <div class="message-options relative ml-1">
            <button onclick="toggleDropdown('dropdownDots-${messageId}', this)" 
                class="inline-flex items-center p-1 text-sm font-medium bg-transparent rounded-full hover:opacity-80 focus:outline-none">
                <i class="fa-solid fa-ellipsis-vertical cursor-pointer text-lg text-gray-400 hover:text-gray-700"></i>
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
