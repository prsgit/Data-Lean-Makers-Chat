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
      messageModalText.textContent = "Esta acción no podrá deshacerse";
    } else if (type === "forAll") {
      messageModalTitle.textContent =
        "¿Desea eliminar este mensaje para todos?";
      messageModalText.textContent = "Esta acción no podrá deshacerse";
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

// Función solo para mobile, se ve la listade usuarios y al elegir uno cambia al chat y viceversa.
document.addEventListener("DOMContentLoaded", function () {
  // Obtener los bloques
  const contactsBlock = document.getElementById("contacts-block");
  const chatBlock = document.getElementById("chat-block");

  // Función para ajustar la vista basada en el ancho de la ventana
  function adjustViewBasedOnWidth() {
    if (window.innerWidth >= 768) {
      // En pantallas medianas o grandes, siempre mostrar ambos bloques con sus clases originales
      contactsBlock.classList.remove("hidden");
      chatBlock.classList.remove("hidden");
      chatBlock.classList.add("md:flex");

      // Asegurar que la vista no esté afectada por el estado anterior
      if (!chatBlock.classList.contains("md:w-2/3")) {
        chatBlock.classList.add("md:w-2/3");
      }
      if (!contactsBlock.classList.contains("md:w-1/3")) {
        contactsBlock.classList.add("md:w-1/3");
      }
    } else {
      // En móvil, verifica si hay un chat activo
      const isUserOrGroupSelected = document.querySelector(".active") !== null;
      const isChatViewActive =
        localStorage.getItem("chatViewActive") === "true";

      if (isUserOrGroupSelected && isChatViewActive) {
        // Mostrar solo el chat
        contactsBlock.classList.add("hidden");
        chatBlock.classList.remove("hidden");
        chatBlock.classList.add("flex");
      } else {
        // Mostrar solo la lista de contactos
        contactsBlock.classList.remove("hidden");
        chatBlock.classList.add("hidden");
        localStorage.removeItem("chatViewActive");
      }
    }
  }

  // Ajustar la vista cuando se carga la página
  adjustViewBasedOnWidth();

  // Ajusta la vista cuando cambia el tamaño de la ventana
  window.addEventListener("resize", adjustViewBasedOnWidth);

  // Obtener todos los enlaces de usuario y grupo existentes
  const userLinks = document.querySelectorAll("#user-list a, #group-list a");

  // Agregar evento de clic a cada enlace
  userLinks.forEach((link) => {
    link.addEventListener("click", function () {
      // Solo aplicar en móviles
      if (window.innerWidth < 768) {
        // Guardar estado en localStorage
        localStorage.setItem("chatViewActive", "true");
      }
    });
  });

  // Manejar el evento de clic en el botón de regreso
  const backButton = document.getElementById("back-to-contacts");
  if (backButton) {
    backButton.addEventListener("click", function () {
      // Solo aplicar en móviles
      if (window.innerWidth < 768) {
        // Mostrar bloque de contactos y ocultar bloque de chat
        contactsBlock.classList.remove("hidden");
        chatBlock.classList.add("hidden");

        // Limpiar localStorage
        localStorage.removeItem("chatViewActive");
      }
    });
  }
});

