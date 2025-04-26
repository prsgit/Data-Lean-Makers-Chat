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
        <div class="rounded-xl py-2 px-3 max-w-xs bg-wasabiClaro">
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
  const isDocument = /\.(pdf|docx|doc|pptx|ppt|xlsx|xls|zip)$/i.test(fileUrl);

  // Preparar el contenido del archivo según su tipo
  let fileContent;
  if (isImage) {
    fileContent = `
      <a href="${fileUrl}" target="_blank" class="inline-block">
        <img src="${fileUrl}" alt="Imagen adjunta" class="w-24 h-20 rounded-lg object-cover cursor-pointer text-sm underline"/>
      </a>
    `;
  } else if (isVideo) {
    fileContent = `
       <a href="${fileUrl}" target="_blank" class="inline-block">
      <video controls class="w-28 h-28 rounded-lg object-cover">
        <source src="${fileUrl}" type="video/mp4">
        Tu navegador no soporta la etiqueta de video.
      </video>
    </a>
    `;
  } else if (isDocument) {
    // Para otros archivos (PDF, DOC, etc.)
    fileContent = `
      <a href="${fileUrl}" download target="_blank" 
         class="inline-flex items-center px-1 py-1 text-sm font-medium text-blue-600 bg-blue-100 rounded-lg hover:bg-blue-200">
       <i class="fa-solid fa-circle-down text-sm"></i>
        Descargar archivo
      </a>
    `;
  }

  if (isMyMessage) {
    // Mensaje del emisor
    const messageHTML = `
      <div id="message-${messageId}" class="flex justify-end mb-2 items-center space-x-2">
                <!-- Contenedor del mensaje -->
        <div class="rounded-xl py-2 px-3 max-w-xs bg-wasabiClaro">
                <div class="rounded-xl py-2 px-3 max-w-xs ">
                    <div class="text-sm mt-1">${fileContent}</div>
                    <p class="text-right text-xs text-gray-500 mt-1">${timeString}</p>
                </div>

                <!-- Opciones de mensaje -->
                <div class="message-options relative">
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
      <div id="message-${messageId}" class="flex items-center mb-2 space-x-2">
        <div class="rounded-xl py-2 px-3 bg-white max-w-xs">
          <p class="text-sm font-bold text-gray-500">
            ${sender}
          </p>
          <div class="text-sm mt-1">
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

  if (data.message && data.sender && data.sender_realname) {
    appendMessage(
      data.sender,
      data.message,
      data.sender_realname === username,
      messageId
    );

    //si estoy en el chat correcto, marcar el mensaje como leído
    if (typeof otherUsername !== "undefined" && otherUsername === data.sender_realname &&  data.message_id) {
      marcarMensajeComoLeido(data.message_id, data.sender_realname);
    }

    if (typeof groupName !== "undefined" && groupName !== null && groupName !== "") {
      marcarGrupoComoLeido(groupName);
    }    
  }


  if (data.file_url && data.sender && data.sender_realname) {
    console.log("URL del archivo:", data.file_url); //  URL del archivo recibido
    const fileMessageId = data.message_id; // Captura el ID del mensaje relacionado con el archivo

    appendFile(
      data.sender,
      data.file_url,
      data.sender_realname === username,
      fileMessageId
    );
  }

  if (data.type === "sistema") {
    mostrarMensajeDelSistema(data.message);
  }

  if (data.type === "update_unread_count") {
    actualizarGlobito(data.unread_count, data.sender_username);
  }

  if (data.type === "update_unread_group_count") {
    actualizarGlobito(data.unread_count, data.group_name);
  }

};

chatSocket.onclose = function (e) {
  console.error("Chat socket cerrado inesperadamente");
};

// muestra un sms de advertencia si tienes el permiso "lectura" activado y se ha intentado por consola enviar un sms/archivo
function mostrarMensajeDelSistema(texto) {
  const chatLog = document.getElementById("chat-log");
  const msgSistema = document.createElement("div");

  msgSistema.className = "text-center text-sm text-gray-700 italic my-2";
  msgSistema.textContent = texto;

  chatLog.appendChild(msgSistema);
  chatLog.scrollTop = chatLog.scrollHeight;
}


function actualizarGlobito(unread_count, username) {
  if (!username) {
    console.warn("No se proporcionó el nombre del usuario o grupo.");
    return;
  }

  // Verificar si estoy en el chat individual actual
  if (typeof otherUsername !== "undefined" && otherUsername === username) {
    console.log("Estoy en el chat con", username, "- No se muestra globito.");
    return;
  }

  // Verificar si estoy en el grupo actual
  if (typeof groupName !== "undefined" && groupName === username) {
    console.log("Estoy en el grupo", username, "- No se muestra globito.");
    return;
  }

  // Buscar el globito ya sea de usuario o grupo
  let globito = document.getElementById(`contador-${username}`) 
             || document.getElementById(`contador-grupo-${username}`);

  // Si no existe, lo creamos dependiendo del tipo
  if (!globito) {
    const userLink = document.querySelector(`a[href$="/${username}/"] .about`);
    if (userLink) {
      globito = document.createElement("div");

      // Distinguir entre grupo y usuario por prefijo
      const esGrupo = document.getElementById(`contador-grupo-${username}`) !== null 
                      || (typeof groupName !== "undefined" && groupName === username);
      globito.id = esGrupo ? `contador-grupo-${username}` : `contador-${username}`;

      globito.className = "px-1 py-0.5 bg-red-500 min-w-5 rounded-full font-bold text-center text-white text-xs absolute -top-2 -end-1 translate-x-1/4 text-nowrap";
      userLink.appendChild(globito);
    } else {
      console.warn("No se encontró enlace para colocar el globito de:", username);
      return;
    }
  }

  // Actualiza o elimina el globito según el contador
  if (unread_count > 0) {
    globito.textContent = unread_count;
    globito.style.display = "flex";
  } else {
    globito.textContent = "";
    globito.style.display = "none";
  }
}


function marcarMensajeComoLeido(messageId) {
  fetch(`/marcar-leido/${messageId}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie('csrftoken'),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  }).then(response => {
    if (!response.ok) {
      console.error("Error al marcar mensaje como leído.");
    }
  }).catch(error => {
    console.error("Error de red:", error);
  });
}


function marcarGrupoComoLeido(groupName) {
  fetch(`/marcar-leido-grupo/${groupName}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie('csrftoken'),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  }).then(response => {
    if (!response.ok) {
      console.error("Error al marcar el grupo como leído.");
    }
  }).catch(error => {
    console.error("Error de red:", error);
  });
}


// Función para manejar el estado de primer acceso
// function handlePrimerAcceso(primer_acceso) {
//   // Si es el primer acceso, mostramos la vista completa
//   if (primer_acceso) {
//       // Almacenamos en localStorage que es el primer acceso
//       localStorage.setItem("primer_acceso", "true");
//       document.querySelector(".vista-completa").classList.remove("hidden");
//       document.querySelector("#chat-block").classList.add("hidden");
//   } else {
//       // Si ya no es el primer acceso, mostramos el chat normal
//       localStorage.setItem("primer_acceso", "false");
//       document.querySelector(".vista-completa").classList.add("hidden");
//       document.querySelector("#chat-block").classList.remove("hidden");
//   }
// }

// Función para marcar como no primer acceso cuando se selecciona un grupo o chat
// function marcarComoNoPrimerAcceso() {
//   // Actualizar el estado en localStorage
//   localStorage.setItem("primer_acceso", "false");
//   // Actualizar la vista
//   document.querySelector(".vista-completa").classList.add("hidden");
//   document.querySelector("#chat-block").classList.remove("hidden");
// }
// Manejo del envio
document.addEventListener("DOMContentLoaded", function () {
  // Verificar si hay un valor de primer acceso en localStorage
  // const primer_acceso = localStorage.getItem("primer_acceso");
    
  // // Si no existe en localStorage, usar el valor del servidor
  // if (!primer_acceso) {
  //     const serverPrimerAcceso = document.getElementById('primer-acceso-value');
  //     if (serverPrimerAcceso) {
  //         const valor = serverPrimerAcceso.value === "true";
  //         handlePrimerAcceso(valor);
  //         // Solo almacenamos en localStorage si es el primer acceso
  //         if (valor) {
  //             localStorage.setItem("primer_acceso", "true");
  //         }
  //     }
  // } else {
  //     // Si existe en localStorage, usamos ese valor
  //     handlePrimerAcceso(primer_acceso === "true");
  // }
  
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

  // desplazar scroll hacia abajo al cargar la vista del chat
  const chatLog = document.querySelector("#chat-log");
  if (chatLog) {
    chatLog.scrollTop = chatLog.scrollHeight;
  }

});
