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
  const logPrefix = options.logPrefix || `[SalaForm ${form.id || formSelector}]`;
  console.debug(`${logPrefix}: vinculado e pronto para envio.`);

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
    const localizacao = (formData.get("localizacao") || formData.get("andar") || "").toString().trim();
    const status = (formData.get("status") || "").toString().trim();
    const equipamentosRaw = (formData.get("equipamentos") || "").toString().trim();
    const descricao = (formData.get("descricao") || formData.get("descrição") || "").toString().trim();

    const clientErrors = [];
    if (!nome) clientErrors.push("Preencha o nome da sala.");

    const capacidade = parseInt(capacidadeValue, 10);
    if (Number.isNaN(capacidade) || capacidade <= 0) {
      clientErrors.push("Informe uma capacidade numerica maior que zero.");
    }

    if (!tipo) clientErrors.push("Selecione o tipo da sala.");
    if (!status) clientErrors.push("Selecione o status da sala.");
    console.debug(`${logPrefix}: submissao iniciada`, { nome, capacidade, tipo, localizacao, status });

    if (clientErrors.length) {
      console.warn(`${logPrefix}: bloqueado por validacao do cliente`, clientErrors);
      showErrors(clientErrors);
      return;
    }

    const payloadBody = { nome, capacidade, tipo };
    if (localizacao) payloadBody.localizacao = localizacao;
    if (equipamentosRaw) {
      payloadBody.equipamentos = equipamentosRaw.split(",").map((s) => s.trim()).filter(Boolean);
    }
    if (status) payloadBody.status = status;
    if (descricao) payloadBody.descricao = descricao;
    console.debug(`${logPrefix}: enviando payload para API`, payloadBody);
    try {
      // Determine mode: prefer explicit data-mode on form (set when opening modal),
      // fallback to hidden input `#modalSalaId` value if present.
      const formMode = form.dataset.mode || (form.querySelector("#modalSalaId")?.value ? "edit" : "create");
      const id = form.querySelector("#modalSalaId")?.value;
      let url = "/api/salas/";
      let method = "POST";
      if (formMode === "edit" && id) {
        url = `/api/salas/${id}/`;
        method = "PUT";
      }

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(form),
        },
        credentials: "same-origin",
        body: JSON.stringify(payloadBody),
      });

      let data = null;
      try {
        // Nem sempre o servidor retorna JSON (ex: 405 vazia); proteger parsing
        data = await response.json();
      } catch (err) {
        console.debug(`${logPrefix}: resposta sem JSON`, err);
        data = null;
      }

      if (!response.ok) {
        console.warn(`${logPrefix}: erro da API ao salvar sala`, { status: response.status, data });
        const errors = data && data.errors ? data.errors : [data && data.message ? data.message : "Erro ao salvar a sala."];
        showErrors(errors);
        return;
      }

      // Reseta UI do form, mas usa dados retornados para atualizar a tabela
      form.reset();
      delete form.dataset.mode;
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.textContent = options.createButtonText || "Adicionar Sala";

      const defaultMessage = method === "PUT" ? "Sala atualizada com sucesso." : "Sala cadastrada com sucesso.";
      showSuccess(data.message || defaultMessage);
      console.info(`${logPrefix}: sala salva com sucesso`, data.sala);

      if (typeof options.onSuccess === "function") {
        const serverSala = data?.sala || {};
        options.onSuccess(serverSala, payloadBody);
      }
    } catch (error) {
      console.error(`${logPrefix}: falha inesperada ao enviar`, error);
      showErrors(["Nao foi possivel enviar os dados. Tente novamente."]);
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
    const statusText = sala.status || "Disponivel";
    const statusPillClass =
      statusText === "Disponivel"
        ? "status-pill status-available"
        : statusText === "Ocupada"
        ? "status-pill status-occupied"
        : "status-pill status-maintenance";

    tr.innerHTML = `
      <td class="fw-semibold sala-nome">${sala.nome}</td>
      <td class="sala-andar">${sala.andar || ""}</td>
      <td class="sala-capacidade">${sala.capacidade} pessoas</td>
      <td class="sala-status"><span class="${statusPillClass}">${statusText}</span></td>
      <td class="sala-equip">
        <div class="equipments">${visibleEquip} ${extra}</div>
      </td>
      <td class="text-end sala-actions">
        <button class="btn btn-sm btn-edit text-primary me-2" data-id="${sala.id}" title="Editar"><i class="bi bi-pencil"></i></button>
        <button class="btn btn-sm btn-delete text-danger" data-id="${sala.id}" title="Excluir"><i class="bi bi-trash"></i></button>
      </td>
    `;

    tr._meta = { equipamentos: equipments, descricao: sala.descricao || "" };
    tr.dataset.nome = sala.nome || "";
    tr.dataset.andar = sala.andar || "";
    tr.dataset.tipo = sala.tipo || "";
    tr.dataset.equipamentos = equipments.join(",");
    tr.dataset.descricao = sala.descricao || "";
    return tr;
  }

  bindSalaForm("#modalSalaForm", {
    successSelector: "#modalSuccess",
    errorSelector: "#modalErrors",
    logPrefix: "[SalaForm Modal]",
    onSuccess: (sala, submitted) => {
      const tableBody = document.getElementById("salasTableBody");
      if (!tableBody) return;
      const salaObj = {
        id: sala.id,
        nome: sala.nome,
        capacidade: sala.capacidade,
        tipo: sala.tipo,
        andar: sala.andar || sala.localizacao || submitted?.localizacao || "",
        status: sala.status || submitted?.status || "Disponivel",
        equipamentos: sala.equipamentos || submitted?.equipamentos || [],
        descricao: sala.descricao || submitted?.descricao || "",
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
      const modalForm = document.querySelector("#modalSalaForm");
      if (modalForm) delete modalForm.dataset.mode;
    },
  });

  // Formulario de pagina simples (criar_sala)
  bindSalaForm("#pageSalaForm", {
    successSelector: "#pageSuccess",
    errorSelector: "#pageErrors",
    logPrefix: "[SalaForm Pagina]",
    onSuccess: () => {
      // Apenas feedback; nao ha tabela para atualizar aqui.
    },
  });

  document.getElementById("salasTableBody")?.addEventListener("click", async (e) => {
    const editBtn = e.target.closest(".btn-edit, .action-btn.edit, .action-btn");
    const delBtn = e.target.closest(".btn-delete, .action-btn.delete");
    if (editBtn) {
      let row = editBtn.closest("tr");
      if (!row) return;
      let id = editBtn.dataset.id || row.dataset.id;
      if (!id) {
        const nome = row.dataset.nome || row.querySelector(".sala-nome")?.textContent || "";
        if (nome) {
          try {
            const resp = await fetch(`/api/salas/lookup/?nome=${encodeURIComponent(nome)}`, { credentials: "same-origin" });
            if (resp.ok) {
              const json = await resp.json();
              id = json.id;
              row.dataset.id = id;
            } else {
              alert("Nao foi possivel identificar o registro para edicao.");
              return;
            }
          } catch (err) {
            alert("Erro ao consultar servidor para identificar a sala.");
            return;
          }
        } else {
          return;
        }
      }
      const modalLabel = document.getElementById("modalSalaLabel");
      if (modalLabel) modalLabel.textContent = "Editar Sala";
      document.getElementById("modalNome").value = row.querySelector(".sala-nome")?.textContent || "";
      document.getElementById("modalCapacidade").value =
        (row.querySelector(".sala-capacidade")?.textContent || "").replace(/\D/g, "") || "";
      document.getElementById("modalTipo").value = row.dataset.tipo || "";
      document.getElementById("modalAndar").value = row.querySelector(".sala-andar")?.textContent || "";
      const statusText = row.querySelector(".sala-status")?.textContent.trim() || "Disponivel";
      document.getElementById("modalStatus").value = statusText;
      const equipamentosFromMeta = row._meta?.equipamentos;
      if (Array.isArray(equipamentosFromMeta)) {
        document.getElementById("modalEquip").value = equipamentosFromMeta.join(", ");
      } else {
        const ds = row.dataset.equipamentos || "";
        document.getElementById("modalEquip").value = ds
          ? ds.split(",").map((s) => s.trim()).filter(Boolean).join(", ")
          : "";
      }
      document.getElementById("modalDesc").value = row._meta?.descricao || row.dataset.descricao || "";
      document.getElementById("modalSalaId").value = id;
      const modalForm = document.querySelector("#modalSalaForm");
      if (modalForm) {
        modalForm.dataset.mode = "edit";
        const submitBtn = modalForm.querySelector('button[type="submit"]');
        if (submitBtn) submitBtn.textContent = "Salvar alteracoes";
      }
      const modal = new bootstrap.Modal(document.getElementById("modalSala"));
      modal.show();
      return;
    }

    if (delBtn) {
      let row = delBtn.closest("tr");
      if (!row) return;
      let id = delBtn.dataset.id || row.dataset.id;
      if (!id) {
        const nome = row.dataset.nome || row.querySelector(".sala-nome")?.textContent || "";
        if (nome) {
          try {
            const resp = await fetch(`/api/salas/lookup/?nome=${encodeURIComponent(nome)}`, { credentials: "same-origin" });
            if (resp.ok) {
              const json = await resp.json();
              id = json.id;
              row.dataset.id = id;
            } else {
              alert("Nao foi possivel identificar o registro para exclusao.");
              return;
            }
          } catch (err) {
            alert("Erro ao consultar servidor para identificar a sala.");
            return;
          }
        } else {
          return;
        }
      }

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
        row.remove();
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

  const params = new URLSearchParams(window.location.search);
  if (params.get("openModal") === "1") {
    const modalEl = document.getElementById("modalSala");
    if (modalEl && window.bootstrap) {
      const modal = new bootstrap.Modal(modalEl);
      modal.show();
    }
  }

  const modalEl = document.getElementById("modalSala");
  if (modalEl) {
    modalEl.addEventListener("hidden.bs.modal", () => {
      const form = document.getElementById("modalSalaForm");
      form?.reset();
      const errors = document.getElementById("modalErrors");
      const success = document.getElementById("modalSuccess");
      errors?.parentElement?.classList.add("d-none");
      if (errors) errors.innerHTML = "";
      success?.classList.add("d-none");
      const label = document.getElementById("modalSalaLabel");
      if (label) label.textContent = "Adicionar Nova Sala";
      const idField = document.getElementById("modalSalaId");
      if (idField) idField.value = "";
    });
  }
});
