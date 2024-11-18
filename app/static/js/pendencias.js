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
    // Carregar Pendências
    // ============================
    function carregarPendencias() {
      fetch("/pendencias/list")
        .then((response) => response.json())
        .then((data) => {
          pendenciasData = data.pendencias || [];
          renderTabelaPendencias();
        })
        .catch(() => {
          Swal.fire({
            icon: "error",
            title: "Erro!",
            text: "Erro ao carregar as pendências. Verifique sua conexão.",
            confirmButtonColor: "#d33",
          });
        });
    }
  
    // ============================
    // Renderizar Tabela de Pendências
    // ============================
    function renderTabelaPendencias() {
      const tabelaBody = $("#pendencias-table-body");
      tabelaBody.empty();
  
      pendenciasData.forEach((pendencia) => {
        const valor = parseFloat(pendencia.valor) || 0;
        const dataFormatada = new Date(pendencia.data).toLocaleDateString(
          "pt-BR"
        );
        tabelaBody.append(`
            <tr>
              <td>${pendencia.id}</td>
              <td>${pendencia.cliente}</td>
              <td>${dataFormatada}</td>
              <td>R$ ${valor.toFixed(2)}</td>
              <td>
                <button class="ui blue button visualizar-pendencia-btn" data-id="${
                  pendencia.id
                }">
                  <i class="eye icon"></i> Visualizar
                </button>
                <button class="ui red button excluir-pendencia-btn" data-id="${
                  pendencia.id
                }">
                  <i class="trash icon"></i> Excluir
                </button>
              </td>
            </tr>
          `);
      });
    }
  
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
            preco: parseFloat(produto.preco) || 0,
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
    // Atualizar Lista de Produtos
    // ============================
    function atualizarListaProdutos() {
      const container = $("#produtos-list-container");
      container.empty();
  
      let total = 0;
  
      produtosSelecionados.forEach((item, index) => {
        const produto = produtos.find((p) => p.id == item.produtoId);
        if (!produto) {
          console.error(`Produto com ID ${item.produtoId} não encontrado.`);
          return;
        }
  
        const preco = parseFloat(produto.preco) || 0;
        const subtotal = item.quantidade * preco;
        total += subtotal;
  
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
  
          const produto = produtos.find((p) => p.id == produtoId);
          const subtotal = quantidade * produto.preco;
  
          return { produtoId, quantidade, subtotal };
        },
      }).then((result) => {
        if (result.isConfirmed) {
          const { produtoId, quantidade, subtotal } = result.value;
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
          produtos: produtosSelecionados,
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
            produtosSelecionados = [];
            atualizarListaProdutos(); // Limpa produtos
            carregarPendencias(); // Atualiza tabela
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
    $(document).on("click", "#gerar-relatorio-btn", function () {
        const clienteId = $("#select-cliente").val(); // Obtém o cliente selecionado
      
        if (!clienteId) {
          Swal.fire({
            icon: "warning",
            title: "Atenção",
            text: "Por favor, selecione um cliente para gerar o relatório.",
          });
          return;
        }
      
        // Requisição para obter os dados do relatório
        fetch(`/pendencias/relatorio/${clienteId}`)
          .then((response) => {
            if (!response.ok) {
              throw new Error("Erro ao gerar o relatório.");
            }
            return response.json();
          })
          .then((data) => {
            if (data.success) {
              const pendencias = data.pendencias;
      
              // Construção do conteúdo do relatório
              let conteudoRelatorio = `
                <div style="width: 80mm; font-family: Arial, sans-serif; font-size: 12px; margin: 0 auto; padding: 10px;">
                  <h3 style="text-align: center;">Relatório de Pendências</h3>
                  <p style="text-align: center;">Cliente ID: ${clienteId}</p>
                  <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 12px; margin-top: 10px;">
                    <thead>
                      <tr>
                        <th style="border-bottom: 1px solid #000;">ID</th>
                        <th style="border-bottom: 1px solid #000;">Data</th>
                        <th style="border-bottom: 1px solid #000;">Descrição</th>
                        <th style="border-bottom: 1px solid #000;">Qtd</th>
                        <th style="border-bottom: 1px solid #000;">Subtotal</th>
                      </tr>
                    </thead>
                    <tbody>
              `;
      
              pendencias.forEach((pendencia) => {
                const dataFormatada = new Date(pendencia.data).toLocaleDateString(
                  "pt-BR"
                );
                conteudoRelatorio += `
                  <tr>
                    <td>${pendencia.id}</td>
                    <td>${dataFormatada}</td>
                    <td>${pendencia.descricao}</td>
                    <td>${pendencia.quantidade}</td>
                    <td>R$ ${parseFloat(pendencia.preco).toFixed(2)}</td>
                  </tr>
                `;
              });
      
              conteudoRelatorio += `
                    </tbody>
                  </table>
                </div>
              `;
      
              // Inserir o conteúdo do relatório em uma nova janela de impressão
              const printWindow = window.open("", "_blank");
              printWindow.document.write(`
                <html>
                  <head>
                    <title>ti</title>
                    <style>
                      body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                      table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                      th, td { border: 1px solid #000; padding: 5px; text-align: left; }
                      th { background-color: #f2f2f2; }
                      h3 { margin: 0; padding: 10px 0; text-align: center; }
                    </style>
                  </head>
                  <body onload="window.print(); window.close();">
                    ${conteudoRelatorio}
                  </body>
                </html>
              `);
              printWindow.document.close();
            } else {
              Swal.fire({
                icon: "error",
                title: "Erro!",
                text: "Nenhuma pendência encontrada para este cliente.",
              });
            }
          })
          .catch((error) => {
            console.error(error);
            Swal.fire({
              icon: "error",
              title: "Erro!",
              text: "Erro ao gerar o relatório.",
            });
          });
      });
      
      
  
    // ============================
    // Carregar Clientes no Combobox
    // ============================
    function carregarClientesCombo() {
      fetch("/clientes/list")
        .then((res) => {
          if (!res.ok) throw new Error("Erro na resposta da API de clientes.");
          return res.json();
        })
        .then((data) => {
          if (!data.clients || data.clients.length === 0) {
            throw new Error("Nenhum cliente encontrado na API.");
          }
  
          const clienteDropdown = $("#select-cliente");
          clienteDropdown.empty();
          clienteDropdown.append(
            `<option value="">Selecione um cliente</option>`
          );
  
          data.clients.forEach((cliente) => {
            clienteDropdown.append(
              `<option value="${cliente.id}">${cliente.aluno}</option>`
            );
          });
  
          clienteDropdown.dropdown();
          console.log("Clientes carregados com sucesso:", data.clients); // Log de debug
        })
        .catch((error) => {
          console.error("Erro ao carregar clientes:", error);
          Swal.fire({
            icon: "error",
            title: "Erro!",
            text: "Erro ao carregar clientes. Verifique sua conexão.",
          });
        });
    }
  
    // ============================
    // Gerar Relatório Consolidado
    // ============================
    
      
    
    carregarPendencias();
    carregarClientesCombo();
    carregarClientes();
    carregarProdutos();
    
  });
  