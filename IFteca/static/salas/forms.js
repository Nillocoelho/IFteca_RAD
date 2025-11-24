function getCsrfToken() {
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
    errorBox.innerHTML = messages
      .map((message) => `<li>${message}</li>`)
      .join("");
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
          "X-CSRFToken": getCsrfToken(),
        },
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
  bindSalaForm("#modalSalaForm", {
    successSelector: "#modalSuccess",
    errorSelector: "#modalErrors",
    onSuccess: (sala) => {
      const tableBody = document.getElementById("salasTableBody");
      if (tableBody) {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${sala.nome}</td><td>${sala.capacidade} pessoas</td><td>${sala.tipo}</td><td>--</td>`;
        const emptyRow = tableBody.querySelector(".js-empty-row");
        if (emptyRow) emptyRow.remove();
        tableBody.appendChild(row);
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
    },
  });

  bindSalaForm("#pageSalaForm", {
    successSelector: "#pageSuccess", 
    errorSelector: "#pageErrors",
  });
});
