// Mostrar vista previa de la imagen de perfil elegida para cambiarla en el usuario
function previewAvatar(input) {
    const preview = document.getElementById("preview-avatar");
    const file = input.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        preview.src = e.target.result;
        preview.classList.remove("d-none"); // Mostrar la vista previa
      };
      reader.readAsDataURL(file);
    }
  }
  
  // Mostrar vista previa de la imagen de perfil elegida para cambiarla en el grupo
  function previewAvatar(input) {
    const file = input.files[0];
    const preview = document.getElementById("current-avatar");
  
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        preview.src = e.target.result; // Mostrar vista previa
      };
      reader.readAsDataURL(file); // Leer archivo como URL
    }
  }
  