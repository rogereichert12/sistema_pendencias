$(document).ready(function () {
  let pendenciasData = [];
  let produtosSelecionados = [];
  let produtos = [];
  let currentPage = 1;
  const recordsPerPage = 10;

  // ============================
  // Inicializar Sidebar
  // ============================
  $(".ui.sidebar").sidebar({ transition: "overlay" });
  $("#toggle-sidebar").on("click", function () {
    $(".ui.sidebar").sidebar("toggle");
  });

  // ============================
  // Carregar Clientes
  // ============================
  function carregarClientes() {
    fetch("/clientes/list")
      .then((res) => res.json())
      .then((data) => {
        const clienteDropdown = $("#cliente-id");
        clienteDropdown.empty();
        data.clients.forEach((cliente) => {
          clienteDropdown.append(
            `<option value="${cliente.id}">${cliente.aluno}</option>`
          );
        });
        clienteDropdown.dropdown();
      })
      .catch(() => {
        Swal.fire({
          icon: "error",
          title: "Erro!",
          text: "Erro ao carregar clientes. Verifique sua conexão.",
          confirmButtonColor: "#d33",
        });
      });
  }

  // ============================
  // Carregar Produtos
  // ============================
  function carregarProdutos() {
    fetch("/produtos/list")
      .then((response) => response.json())
      .then((data) => {
        produtos = data.produtos.map((produto) => ({
          ...produto,
          preco: parseFloat(produto.preco) || 0, // Converte preço para número
        }));
      })
      .catch(() => {
        Swal.fire({
          icon: "error",
          title: "Erro!",
          text: "Erro ao carregar os produtos. Verifique sua conexão.",
          confirmButtonColor: "#d33",
        });
      });
  }

  // ============================
  // Atualizar Lista de Produtos Selecionados
  // ============================
  function atualizarListaProdutos() {
    const container = $("#produtos-list-container");
    container.empty(); // Limpa o contêiner antes de renderizar

    let total = 0;

    produtosSelecionados.forEach((item, index) => {
      const produto = produtos.find((p) => p.id == item.produtoId);
      if (!produto) {
        console.error(`Produto com ID ${item.produtoId} não encontrado.`);
        return;
      }

      const preco = parseFloat(produto.preco) || 0; // Garante que 'preco' seja numérico
      const subtotal = item.quantidade * preco;
      total += subtotal;

      // Adiciona o produto à lista
      container.append(`
          <div class="ui segment produto-item">
            <div class="ui grid">
              <div class="twelve wide column">
                <strong>${produto.descricao}</strong><br />
                Quantidade: ${
                  item.quantidade
                } - Subtotal: R$ ${subtotal.toFixed(2)}
              </div>
              <div class="four wide column right aligned">
                <button class="ui red button remove-produto-btn" data-index="${index}">
                  <i class="trash icon"></i> Remover
                </button>
              </div>
            </div>
          </div>
        `);
    });

    $("#total-valor").val(`R$ ${total.toFixed(2)}`);
  }

  // ============================
  // Adicionar Produto
  // ============================
  $("#add-produto-btn").on("click", function () {
    Swal.fire({
      title: "Adicionar Produto",
      html: `
          <select id="produto-dropdown" class="ui dropdown" style="width: 100%; margin-bottom: 10px;">
            ${produtos
              .map((produto) => {
                const preco = parseFloat(produto.preco) || 0;
                return `<option value="${produto.id}">${
                  produto.descricao
                } - R$ ${preco.toFixed(2)}</option>`;
              })
              .join("")}
          </select>
          <input type="number" id="produto-quantidade" placeholder="Quantidade" min="1" style="width: 100%; padding: 8px;" />
        `,
      showCancelButton: true,
      confirmButtonText: "Adicionar",
      cancelButtonText: "Cancelar",
      preConfirm: () => {
        const produtoId = $("#produto-dropdown").val();
        const quantidade = parseInt($("#produto-quantidade").val());

        if (!produtoId || !quantidade || quantidade <= 0) {
          Swal.showValidationMessage(
            "Selecione um produto e insira uma quantidade válida."
          );
          return false;
        }

        if (produtosSelecionados.some((item) => item.produtoId == produtoId)) {
          Swal.showValidationMessage("Este produto já foi adicionado à lista.");
          return false;
        }

        return { produtoId, quantidade };
      },
    }).then((result) => {
      if (result.isConfirmed) {
        const { produtoId, quantidade } = result.value;
        const produto = produtos.find((p) => p.id == produtoId);
        const subtotal = quantidade * produto.preco; // Calcula o subtotal

        produtosSelecionados.push({ produtoId, quantidade, subtotal });
        atualizarListaProdutos();
      }
    });
  });

  // ============================
  // Remover Produto
  // ============================
  $(document).on("click", ".remove-produto-btn", function () {
    const index = $(this).data("index");
    produtosSelecionados.splice(index, 1);
    atualizarListaProdutos();
  });

  // ============================
  // Submeter Formulário de Pendência
  // ============================
  $("#pendencia-form").on("submit", function (e) {
    e.preventDefault();

    const clienteId = $("#cliente-id").val();
    const data = $("#data").val();
    if (!clienteId || !data || produtosSelecionados.length === 0) {
      Swal.fire({
        icon: "error",
        title: "Erro!",
        text: "Preencha todos os campos obrigatórios.",
      });
      return;
    }

    fetch("/pendencias/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        cliente_id: clienteId,
        data: data,
        produtos: produtosSelecionados, // Envia os produtos com subtotais
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          Swal.fire({
            icon: "success",
            title: "Pendência salva!",
            text: "Os dados foram salvos com sucesso.",
          });
          $("#pendencia-modal").modal("hide");
          carregarPendencias();
        } else {
          Swal.fire({
            icon: "error",
            title: "Erro!",
            text: "Erro ao salvar a pendência.",
          });
        }
      });
  });

  // ============================
  // Inicialização
  // ============================
  $("#add-pendencia-btn").on("click", function () {
    $("#pendencia-form")[0].reset();
    produtosSelecionados = [];
    atualizarListaProdutos();
    $("#pendencia-modal").modal("show");
  });

  carregarClientes();
  carregarProdutos();
  carregarPendencias();
});
