function getCsrfToken(form) {
  // Prefer the hidden input token from the current form; fallback to cookie.
  const input = form?.querySelector('input[name="csrfmiddlewaretoken"]');
  if (input && input.value) return input.value;
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

function bindSalaForm(formSelector, options = {}) {
  const form = document.querySelector(formSelector);
  if (!form) return;

  const successBox = document.querySelector(options.successSelector || "");
  const errorBox = document.querySelector(options.errorSelector || "");

  const showErrors = (messages) => {
    if (!errorBox) return;
    errorBox.innerHTML = messages.map((message) => `<li>${message}</li>`).join("");
    errorBox.parentElement?.classList.remove("d-none");
  };

  const showSuccess = (message) => {
    if (!successBox) return;
    successBox.textContent = message;
    successBox.classList.remove("d-none");
  };

  const clearFeedback = () => {
    successBox?.classList.add("d-none");
    if (errorBox) {
      errorBox.innerHTML = "";
      errorBox.parentElement?.classList.add("d-none");
    }
  };

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearFeedback();

    const formData = new FormData(form);
    const nome = (formData.get("nome") || "").toString().trim();
    const capacidadeValue = formData.get("capacidade");
    const tipo = (formData.get("tipo") || "").toString().trim();

    const clientErrors = [];
    if (!nome) clientErrors.push("Preencha o nome da sala.");

    const capacidade = parseInt(capacidadeValue, 10);
    if (Number.isNaN(capacidade) || capacidade <= 0) {
      clientErrors.push("Informe uma capacidade numérica maior que zero.");
    }

    if (!tipo) clientErrors.push("Selecione o tipo da sala.");

    if (clientErrors.length) {
      showErrors(clientErrors);
      return;
    }

    try {
      const response = await fetch("/api/salas/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(form),
        },
        credentials: "same-origin",
        body: JSON.stringify({ nome, capacidade, tipo }),
      });

      const data = await response.json();

      if (!response.ok) {
        showErrors(data.errors || ["Erro ao salvar a sala."]);
        return;
      }

      form.reset();
      showSuccess(data.message || "Sala cadastrada com sucesso.");

      if (typeof options.onSuccess === "function") {
        options.onSuccess(data.sala);
      }
    } catch (error) {
      showErrors(["Não foi possível enviar os dados. Tente novamente."]);
    }
  });
}

window.addEventListener("DOMContentLoaded", () => {
  function renderSalaRow(sala) {
    const tr = document.createElement("tr");
    tr.dataset.id = sala.id;
    const equipments = sala.equipamentos || [];
    const visibleEquip = equipments.slice(0, 2).map((e) => `<span class="equip-tag">${e}</span>`).join(" ");
    const extra = equipments.length > 2 ? `<span class="text-muted">+${equipments.length - 2}</span>` : "";
    const statusClass = sala.status === "Disponivel" ? "success" : sala.status === "Ocupada" ? "danger" : "warning";
    tr.innerHTML = `
      <td class="sala-nome">${sala.nome}</td>
      <td class="sala-andar">${sala.andar || ""}</td>
      <td class="sala-capacidade">${sala.capacidade} pessoas</td>
      <td class="sala-status"><span class="badge status-badge bg-${statusClass}">${sala.status || "Disponivel"}</span></td>
      <td class="sala-equip">${visibleEquip} ${extra}</td>
      <td class="sala-actions">
        <button class="btn btn-sm btn-edit text-primary me-2" data-id="${sala.id}" title="Editar"><i class="bi bi-pencil"></i></button>
        <button class="btn btn-sm btn-delete text-danger" data-id="${sala.id}" title="Excluir"><i class="bi bi-trash"></i></button>
      </td>
    `;
    tr._meta = { equipamentos: equipments, descricao: sala.descricao || "" };
    return tr;
  }

  bindSalaForm("#modalSalaForm", {
    successSelector: "#modalSuccess",
    errorSelector: "#modalErrors",
    onSuccess: (sala) => {
      const tableBody = document.getElementById("salasTableBody");
      if (!tableBody) return;
      const salaObj = {
        id: sala.id,
        nome: sala.nome,
        capacidade: sala.capacidade,
        tipo: sala.tipo,
        andar: document.getElementById("modalAndar")?.value || "",
        status: document.getElementById("modalStatus")?.value || "Disponivel",
        equipamentos: (document.getElementById("modalEquip")?.value || "")
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        descricao: document.getElementById("modalDesc")?.value || "",
      };

      const editId = document.getElementById("modalSalaId")?.value;
      if (editId) {
        const existing = tableBody.querySelector(`tr[data-id="${salaObj.id}"]`);
        if (existing) {
          const newRow = renderSalaRow(salaObj);
          tableBody.replaceChild(newRow, existing);
        }
      } else {
        const emptyRow = tableBody.querySelector(".js-empty-row");
        if (emptyRow) emptyRow.remove();
        tableBody.appendChild(renderSalaRow(salaObj));
      }

      const modalEl = document.getElementById("modalSala");
      const modal = bootstrap.Modal.getInstance(modalEl);
      modal?.hide();

      const feedback = document.getElementById("modalSavedFeedback");
      if (feedback) {
        feedback.textContent = `Sala "${sala.nome}" cadastrada.`;
        feedback.classList.remove("d-none");
        setTimeout(() => feedback.classList.add("d-none"), 4000);
      }
      document.getElementById("modalSalaId").value = "";
    },
  });

  // Também vinculamos o formulário da página padrão (criar sala)
  // Isso permite que o formulário em `salas/templates/salas/criar_sala.html`
  // envie via fetch para a `api_criar_sala` e mostre feedback em tela.
  bindSalaForm("#pageSalaForm", {
    successSelector: "#pageSuccess",
    errorSelector: "#pageErrors",
    onSuccess: (sala) => {
      // Por enquanto apenas mostra a mensagem de sucesso; não há tabela
      // para atualizar nesta view simples. Mantemos o comportamento
      // de reset do form e possibilidade de callback futuro.
    },
  });

  document.getElementById("salasTableBody")?.addEventListener("click", async (e) => {
    const editBtn = e.target.closest(".btn-edit");
    const delBtn = e.target.closest(".btn-delete");
    if (editBtn) {
      const id = editBtn.dataset.id;
      const row = document.querySelector(`tr[data-id="${id}"]`);
      if (!row) return;
      document.getElementById("modalSalaLabel").textContent = "Editar Sala";
      document.getElementById("modalNome").value = row.querySelector(".sala-nome")?.textContent || "";
      document.getElementById("modalCapacidade").value = (row.querySelector(".sala-capacidade")?.textContent || "").replace(/\D/g, "") || "";
      document.getElementById("modalTipo").value = row.dataset.tipo || "";
      document.getElementById("modalAndar").value = row.querySelector(".sala-andar")?.textContent || "";
      const statusText = row.querySelector(".sala-status")?.textContent.trim() || "Disponivel";
      document.getElementById("modalStatus").value = statusText;
      document.getElementById("modalEquip").value = (row._meta?.equipamentos || []).join(", ");
      document.getElementById("modalDesc").value = row._meta?.descricao || "";
      document.getElementById("modalSalaId").value = id;
      const modal = new bootstrap.Modal(document.getElementById("modalSala"));
      modal.show();
      return;
    }

    if (delBtn) {
      const id = delBtn.dataset.id;
      if (!confirm("Tem certeza que deseja excluir esta sala?")) return;
      try {
        const csrf = getCsrfToken(document.getElementById("modalSalaForm"));
        const resp = await fetch(`/api/salas/${id}/`, {
          method: "DELETE",
          headers: { "X-CSRFToken": csrf },
          credentials: "same-origin",
        });
        if (!resp.ok) {
          alert("Erro ao excluir a sala.");
          return;
        }
        const row = document.querySelector(`tr[data-id="${id}"]`);
        row?.remove();
      } catch (err) {
        alert("Erro ao excluir a sala.");
      }
      return;
    }
  });

  const searchInput = document.getElementById("searchInput");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const q = e.target.value.trim().toLowerCase();
      document.querySelectorAll("#salasTableBody tr").forEach((tr) => {
        if (tr.classList.contains("js-empty-row")) return;
        const name = tr.querySelector(".sala-nome")?.textContent.toLowerCase() || "";
        const floor = tr.querySelector(".sala-andar")?.textContent.toLowerCase() || "";
        const visible = name.includes(q) || floor.includes(q);
        tr.style.display = visible ? "" : "none";
      });
      const anyVisible = Array.from(document.querySelectorAll("#salasTableBody tr")).some((t) => t.style.display !== "none");
      const tbody = document.getElementById("salasTableBody");
      if (!anyVisible && tbody) {
        const empty = document.createElement("tr");
        empty.className = "js-empty-row";
        empty.innerHTML = '<td colspan="6" class="text-center text-secondary py-4">Nenhuma sala encontrada</td>';
        const existingEmpty = tbody.querySelector(".js-empty-row");
        if (existingEmpty) existingEmpty.remove();
        tbody.appendChild(empty);
      } else if (tbody) {
        const existingEmpty = tbody.querySelector(".js-empty-row");
        if (existingEmpty) existingEmpty.remove();
      }
    });
  }
});
