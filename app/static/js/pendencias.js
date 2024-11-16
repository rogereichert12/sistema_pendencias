$(document).ready(function () {
    // ============================
    // Função Principal: Carregar Pendências
    // ============================
    function loadPendencias() {
        fetch("/pendencias/list")
            .then((response) => response.json())
            .then((data) => {
                const tableBody = $("#pendencias-table-body");
                tableBody.empty();

                if (data.pendencias.length === 0) {
                    tableBody.append('<tr><td colspan="6">Nenhuma pendência encontrada.</td></tr>');
                } else {
                    data.pendencias.forEach((pendencia) => {
                        tableBody.append(`
                            <tr>
                                <td>${pendencia.data}</td>
                                <td>${pendencia.descricao}</td>
                                <td>R$ ${pendencia.valor.toFixed(2)}</td>
                                <td>R$ ${pendencia.total_pago.toFixed(2)}</td>
                                <td>${pendencia.status}</td>
                                <td>
                                    <button class="ui yellow button edit-btn" data-id="${pendencia.id}">
                                        <i class="edit icon"></i> Editar
                                    </button>
                                    <button class="ui red button delete-btn" data-id="${pendencia.id}">
                                        <i class="trash icon"></i> Excluir
                                    </button>
                                </td>
                            </tr>
                        `);
                    });
                }
            })
            .catch(() => {
                alert("Erro ao carregar pendências.");
            });
    }

    // ============================
    // Modal: Adicionar Pendência
    // ============================
    $("#add-pendencia-btn").on("click", function () {
        $("#pendencia-form")[0].reset();
        $("#pendencia-id").val("");
        $("#modal-title").text("Adicionar Pendência");
        $("#pendencia-modal").modal("show");
    });

    // ============================
    // Submeter Formulário
    // ============================
    $("#pendencia-form").on("submit", function (e) {
        e.preventDefault();

        const pendencia = {
            id: $("#pendencia-id").val(),
            data: $("#data").val(),
            descricao: $("#descricao").val(),
            valor: parseFloat($("#valor").val()),
        };

        fetch("/pendencias/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(pendencia),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    $("#pendencia-modal").modal("hide");
                    loadPendencias();
                } else {
                    alert("Erro ao salvar pendência.");
                }
            })
            .catch(() => {
                alert("Erro ao salvar pendência.");
            });
    });

    // ============================
    // Inicializar
    // ============================
    loadPendencias();
});
