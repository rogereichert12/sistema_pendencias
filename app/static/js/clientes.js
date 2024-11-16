$(document).ready(function () {
  // ============================
  // Variáveis Globais
  // ============================
  let clientsData = []; // Dados completos de clientes
  let filteredData = []; // Dados filtrados para pesquisa e ordenação
  let currentPage = 1; // Página atual na tabela
  const recordsPerPage = 10; // Registros por página

  // ============================
  // Inicializar Sidebar
  // ============================
  $(".ui.sidebar").sidebar({ transition: "overlay" });
  $("#toggle-sidebar").on("click", function () {
    $(".ui.sidebar").sidebar("toggle");
  });

  // ============================
  // Função Principal: Carregar Clientes
  // ============================
  function loadClients() {
    fetch("/clientes/list")
      .then((response) => response.json())
      .then((data) => {
        clientsData = data.clients || [];
        filteredData = [...clientsData]; // Inicializa os dados filtrados
        renderTable(); // Atualiza a tabela
        renderPagination(); // Atualiza a paginação
      })
      .catch(() => {
        Swal.fire({
          icon: "error",
          title: "Erro!",
          text: "Erro ao carregar os clientes. Verifique sua conexão.",
          confirmButtonColor: "#d33",
        });
      });
  }

  window.loadClients = loadClients;

  // ============================
  // Renderizar Tabela
  // ============================
  function renderTable() {
    const tableBody = $("#clients-table-body");
    const noClientsMessage = $("#no-clients-message");

    tableBody.empty();

    if (filteredData.length === 0) {
      noClientsMessage.removeClass("hidden"); // Mostra mensagem de "nenhum cliente encontrado"
    } else {
      noClientsMessage.addClass("hidden");
      const start = (currentPage - 1) * recordsPerPage;
      const end = start + recordsPerPage;
      const visibleClients = filteredData.slice(start, end);

      visibleClients.forEach((client) => {
        const row = `
          <tr>
            <td>${client.id}</td>
            <td>${client.aluno}</td>
            <td>${client.responsavel}</td>
            <td>${client.telefone}</td>
            <td>${client.cpf}</td>
            <td>
              <button class="ui yellow button edit-btn" data-id="${client.id}">
                <i class="edit icon"></i> Editar
              </button>
              <button class="ui red button delete-btn" data-id="${client.id}">
                <i class="trash icon"></i> Excluir
              </button>
            </td>
          </tr>`;
        tableBody.append(row);
      });
    }
  }

  function renderPagination() {
    const paginationControls = $("#pagination-controls");
    paginationControls.empty();

    const totalPages = Math.ceil(filteredData.length / recordsPerPage);
    for (let i = 1; i <= totalPages; i++) {
      const button = `
        <button class="ui button ${
          i === currentPage ? "active" : ""
        }" data-page="${i}">
            ${i}
        </button>`;
      paginationControls.append(button);
    }

    $(".pagination .ui.button").on("click", function () {
      currentPage = parseInt($(this).data("page"));
      renderTable();
      renderPagination();
    });
  }

  // ============================
  // Função de Pesquisa Instantânea
  // ============================
  /**
   * Atualiza `filteredData` com base no texto digitado na barra de pesquisa.
   */
  $("#search-client").on("input", function () {
    const query = $(this).val().toLowerCase(); // Converte o texto da pesquisa para minúsculas

    // Filtra os dados com base na pesquisa
    filteredData = clientsData.filter(
      (client) =>
        client.aluno.toLowerCase().includes(query) ||
        client.responsavel.toLowerCase().includes(query) ||
        client.cpf.includes(query) ||
        client.telefone.includes(query)
    );

    currentPage = 1; // Reseta para a primeira página
    renderTable(); // Atualiza a tabela
    renderPagination(); // Atualiza a paginação
  });

  // ============================
  // Modal de Adicionar Cliente
  // ============================
  $("#add-client-btn").on("click", function () {
    $("#client-form")[0].reset(); // Reseta o formulário
    $("#client-id").val(""); // Limpa o campo de ID
    $("#modal-title").text("Adicionar Cliente");
    $("#client-modal").modal("show"); // Mostra o modal
  });

  // ============================
  // Modal de Editar Cliente
  // ============================
  $(document).on("click", ".edit-btn", function () {
    const clientId = $(this).data("id");

    fetch(`/clientes/get/${clientId}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.client) {
          $("#client-id").val(data.client.id);
          $("#aluno").val(data.client.aluno);
          $("#responsavel").val(data.client.responsavel);
          $("#telefone").val(data.client.telefone);
          $("#cpf").val(data.client.cpf);

          $("#modal-title").text("Editar Cliente");
          $("#client-modal").modal("show"); // Mostra o modal
        } else {
          Swal.fire({
            icon: "error",
            title: "Erro!",
            text: "Cliente não encontrado.",
            confirmButtonColor: "#d33",
          });
        }
      })
      .catch(() => {
        Swal.fire({
          icon: "error",
          title: "Erro!",
          text: "Erro ao carregar os dados do cliente.",
          confirmButtonColor: "#d33",
        });
      });
  });

  $(document).on("click", ".delete-btn", function () {
    const clientId = $(this).data("id");

    // Alerta de confirmação para exclusão
    Swal.fire({
      title: "Você tem certeza?",
      text: "Esta ação não pode ser desfeita!",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#d33",
      cancelButtonColor: "#6c757d",
      confirmButtonText: "Sim, excluir!",
      cancelButtonText: "Cancelar",
    }).then((result) => {
      if (result.isConfirmed) {
        // Requisição para deletar o cliente
        fetch(`/clientes/delete/${clientId}`, {
          method: "DELETE",
        })
          .then((response) => {
            if (response.ok) {
              // Cliente excluído com sucesso
              Swal.fire({
                icon: "success",
                title: "Excluído!",
                text: "O cliente foi excluído com sucesso.",
                confirmButtonColor: "#00b5ad",
                timer: 2000,
              });
              loadClients(); // Recarrega a lista de clientes
            } else {
              // Erro ao excluir cliente
              return response.json().then((data) => {
                throw new Error(data.message || "Erro ao excluir cliente.");
              });
            }
          })
          .catch((err) => {
            // Exibe erro usando o SweetAlert2
            Swal.fire({
              icon: "error",
              title: "Erro!",
              text: `Erro ao excluir cliente: ${err.message}`,
              confirmButtonColor: "#d33",
            });
          });
      }
    });
  });

  // ============================
  // Submeter Formulário de Cliente
  // ============================
  $("#client-form").on("submit", function (e) {
    e.preventDefault();

    const id = $("#client-id").val();
    const aluno = $("#aluno").val();
    const responsavel = $("#responsavel").val();
    const telefone = $("#telefone").val();
    const cpf = $("#cpf").val();

    const url = id ? `/clientes/edit/${id}` : "/clientes/add";
    const method = id ? "PUT" : "POST";

    fetch(url, {
      method: method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ aluno, responsavel, telefone, cpf }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          loadClients();
          $("#client-modal").modal("hide");
          Swal.fire({
            icon: "success",
            title: "Cliente salvo!",
            text: "Os dados foram salvos com sucesso.",
            confirmButtonColor: "#00b5ad",
          });
        } else {
          Swal.fire({
            icon: "error",
            title: "Erro!",
            text: data.message || "Erro ao salvar cliente.",
            confirmButtonColor: "#d33",
          });
        }
      })
      .catch(() => {
        Swal.fire({
          icon: "error",
          title: "Erro!",
          text: "CPF já cadastrado no sistema",
          confirmButtonColor: "#d33",
        });
      });
  });

  // ============================
  // Inicializar
  // ============================
  loadClients();
});
