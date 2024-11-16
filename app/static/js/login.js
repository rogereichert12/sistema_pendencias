// Exibir o modal ao clicar no link "Registrar-se"
$("#open-register-modal").on("click", function (e) {
  e.preventDefault();
  $("#register-modal").modal("show");
});

// Lidar com o formulário de login
$("#login-form").on("submit", function (e) {
  e.preventDefault();
  const formData = $(this).serialize();

  $.post("/login", formData)
    .done(function (response) {
      if (response.success) {
        Swal.fire({
          icon: "success",
          title: "Bem-vindo!",
          text: response.message,
          timer: 2000,
          showConfirmButton: false,
        }).then(() => {
          window.location.href = "/dashboard";
        });
      } else {
        Swal.fire({
          icon: "error",
          title: "Erro!",
          text: response.message,
        });
      }
    })
    .fail(function () {
      Swal.fire({
        icon: "error",
        title: "Erro!",
        text: "Erro no servidor. Tente novamente mais tarde.",
      });
    });
});

// Lidar com o formulário de registro
$("#register-form").on("submit", function (e) {
  e.preventDefault();
  const formData = $(this).serialize();

  $.post("/register", formData)
    .done(function (response) {
      if (response.success) {
        Swal.fire({
          icon: "success",
          title: "Sucesso!",
          text: response.message,
          timer: 2000,
          showConfirmButton: false,
        }).then(() => {
          $("#register-modal").modal("hide");
        });
      } else {
        Swal.fire({
          icon: "error",
          title: "Erro!",
          text: response.message,
        });
      }
    })
    .fail(function () {
      Swal.fire({
        icon: "error",
        title: "Erro!",
        text: "Erro no servidor. Tente novamente mais tarde.",
      });
    });
});
