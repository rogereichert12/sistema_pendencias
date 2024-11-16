$(document).ready(function () {
  let clientsData = [];
  let filteredData = [];
  let currentPage = 1;
  const recordsPerPage = 10;

  // Inicializar Sidebar
  $(".ui.sidebar").sidebar({ transition: "overlay" });
  $("#toggle-sidebar").on("click", function () {
    $(".ui.sidebar").sidebar("toggle");
  });

  // Função para carregar clientes
  function loadClients() {
    fetch("/clientes/list")
      .then((response) => response.json())
      .then((data) => {
        clientsData = data.clients || [];
        filteredData = [...clientsData];
        renderTable();
        renderPagination();
      })
      .catch(() => {
        alert("Erro ao carregar os clientes.");
      });
  }

  // Função para renderizar a tabela
  function renderTable() {
    const tableBody = $("#clients-table-body");
    const noClientsMessage = $("#no-clients-message");

    tableBody.empty();

    if (filteredData.length === 0) {
      noClientsMessage.removeClass("hidden");
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

  // Função para renderizar paginação
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

  // Adicionar Cliente - Mostrar Modal
  $("#add-client-btn").on("click", function () {
    $("#client-form")[0].reset(); // Reseta o formulário
    $("#client-id").val(""); // Limpa o campo de ID
    $("#modal-title").text("Adicionar Cliente");
    $("#client-modal").modal("show"); // Abre a modal
  });

  // Editar Cliente - Mostrar Modal
  $(document).on("click", ".edit-btn", function () {
    const clientId = $(this).data("id");
    fetch(`/clientes/get/${clientId}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.client) {
          // Preenche os campos do formulário
          $("#client-id").val(data.client.id);
          $("#aluno").val(data.client.aluno);
          $("#responsavel").val(data.client.responsavel);
          $("#telefone").val(data.client.telefone);
          $("#cpf").val(data.client.cpf);

          $("#modal-title").text("Editar Cliente");
          $("#client-modal").modal("show"); // Abre a modal
        } else {
          alert("Erro ao carregar os dados do cliente.");
        }
      })
      .catch(() => {
        alert("Erro ao carregar os dados do cliente.");
      });
  });

  // Submeter Formulário de Cliente
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
          alert("Cliente salvo com sucesso!");
        } else {
          alert("Erro ao salvar cliente: " + data.message);
        }
      })
      .catch(() => {
        alert("Erro ao salvar cliente.");
      });
  });

  // Pesquisa de clientes
  $("#search-client").on("input", function () {
    const query = $(this).val().toLowerCase();
    filteredData = clientsData.filter(
      (client) =>
        client.aluno.toLowerCase().includes(query) ||
        client.responsavel.toLowerCase().includes(query) ||
        client.cpf.includes(query)
    );

    currentPage = 1;
    renderTable();
    renderPagination();
  });

  // Inicializa carregamento de clientes
  loadClients();
});
