$(document).ready(function () {
    // ============================
    // Inicializar Sidebar
    // ============================
    $(".ui.sidebar").sidebar({ transition: "overlay" });
    $("#toggle-sidebar").on("click", function () {
      $(".ui.sidebar").sidebar("toggle");
    });
  
    // ============================
    // Botão Adicionar Pendência
    // ============================
    $("#add-pendencia-btn").on("click", function () {
      $("#pendencia-form")[0].reset(); // Limpa o formulário
      $("#pendencia-modal").modal("show"); // Abre o modal
    });
  
    // ============================
    // Enviar Formulário de Pendência
    // ============================
    $("#pendencia-form").on("submit", function (e) {
      e.preventDefault(); // Evita o recarregamento da página
  
      const pendenciaData = {
        cliente_id: $("#cliente-id").val(),
        data: $("#data").val(),
        descricao: $("#descricao").val(),
        valor: $("#valor").val(),
      };
  
      // Envia os dados via POST
      fetch("/pendencias/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(pendenciaData),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            Swal.fire({
              icon: "success",
              title: "Pendência adicionada!",
              text: "A pendência foi cadastrada com sucesso.",
              confirmButtonColor: "#00b5ad",
            });
            $("#pendencia-modal").modal("hide");
            loadPendencias(); // Recarrega as pendências (função a ser implementada)
          } else {
            Swal.fire({
              icon: "error",
              title: "Erro!",
              text: data.message || "Erro ao adicionar pendência.",
              confirmButtonColor: "#d33",
            });
          }
        })
        .catch(() => {
          Swal.fire({
            icon: "error",
            title: "Erro!",
            text: "Erro ao enviar os dados. Verifique sua conexão.",
            confirmButtonColor: "#d33",
          });
        });
    });
  });
  