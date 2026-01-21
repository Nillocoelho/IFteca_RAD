function getCsrfToken(){const m=document.cookie.match(/csrftoken=([^;]+)/);return m?decodeURIComponent(m[1]):""}

// ========== SNACKBAR ==========
function showSnackbar(message, type = 'info') {
  const snackbar = document.getElementById('snackbar');
  if (!snackbar) return;
  
  snackbar.className = 'snackbar';
  snackbar.classList.add(type);
  
  let icon = '';
  switch(type) {
    case 'success': icon = '<i class="bi bi-check-circle"></i>'; break;
    case 'error': icon = '<i class="bi bi-x-circle"></i>'; break;
    case 'warning': icon = '<i class="bi bi-exclamation-triangle"></i>'; break;
    case 'info': icon = '<i class="bi bi-info-circle"></i>'; break;
  }
  
  snackbar.innerHTML = icon + '<span>' + message + '</span>';
  snackbar.classList.add('show');
  setTimeout(() => { snackbar.classList.remove('show'); }, 4000);
}

const API_BASE = (document.body.dataset.apiBase || "/reservas/admin/salas/").replace(/\/+$/, "");
const IS_ADMIN = document.body.dataset.isAdmin === 'true';
const listUrl = `${API_BASE}/`;
const detailUrl = id => `${API_BASE}/${id}/`;
const deleteUrl = id => `${API_BASE}/${id}/delete/`;

let currentPage = 1;
let paginationData = null;

console.info("[salas-ui] API_BASE detectado", { API_BASE, listUrl, IS_ADMIN });

// ========== FETCH SALAS COM PAGINAÇÃO ==========
async function fetchSalas(page = 1) {
  const url = `${listUrl}?page=${page}`;
  console.info("[salas-ui] requisitando lista de salas", { url });
  const res = await fetch(url, { credentials: "same-origin" });
  console.info("[salas-ui] resposta lista de salas", { status: res.status });
  if (!res.ok) {
    console.warn("[salas-ui] falha ao listar salas", { status: res.status });
    return { salas: [], pagination: null };
  }
  const data = await res.json();
  console.info("[salas-ui] lista carregada", { total: data.salas?.length || 0, pagination: data.pagination });
  return data;
}

// ========== RENDER SALA ROW ==========
function renderSalaRow(s) {
  const tr = document.createElement('tr');
  tr.dataset.id = s.id;
  
  // Garantir que equipamentos seja sempre um array
  let equipamentos = s.equipamentos || [];
  if (typeof equipamentos === 'string') {
    equipamentos = equipamentos.split(',').map(e => e.trim()).filter(Boolean);
  }
  
  const visibleEquip = equipamentos.slice(0, 2).map(e => `<span class="equip-tag">${e}</span>`).join(' ');
  const extra = equipamentos.length > 2 ? `<span class="text-muted">+${equipamentos.length - 2}</span>` : '';
  const statusText = s.status || s.status_text || "Disponivel";
  const statusPillClass =
    statusText === "Disponivel" ? "status-pill status-available" :
    statusText === "Em Manutenção" ? "status-pill status-maintenance" : "status-pill status-available";
  
  const andar = s.tipo || s.localizacao || "";

  // Botões de ação
  let actionsHtml = '';
  if (IS_ADMIN) {
    actionsHtml = `
      <button class="btn btn-sm btn-edit text-primary me-2" data-id="${s.id}" title="Editar"><i class="bi bi-pencil"></i></button>
      <button class="btn btn-sm btn-delete text-danger" data-id="${s.id}" title="Excluir"><i class="bi bi-trash"></i></button>
    `;
  } else {
    actionsHtml = `
      <button class="btn btn-sm btn-action-disabled" disabled title="Apenas administradores podem editar"><i class="bi bi-pencil"></i></button>
      <button class="btn btn-sm btn-action-disabled" disabled title="Apenas administradores podem excluir"><i class="bi bi-trash"></i></button>
    `;
  }

  tr.innerHTML = `
    <td class="sala-nome">${s.nome}</td>
    <td class="sala-tipo">${andar}</td>
    <td class="sala-capacidade">${s.capacidade} pessoas</td>
    <td class="sala-status"><span class="${statusPillClass}">${statusText}</span></td>
    <td class="sala-equip"><div class="equipments">${visibleEquip} ${extra}</div></td>
    <td class="text-center sala-actions">${actionsHtml}</td>
  `;
  
  tr._meta = { equipamentos: equipamentos, descricao: s.descricao || "" };
  tr.dataset.nome = s.nome || "";
  tr.dataset.tipo = s.tipo || "";
  tr.dataset.equipamentos = (equipamentos || []).join(',');
  tr.dataset.descricao = s.descricao || "";
  return tr;
}

// ========== RENDER PAGINAÇÃO ==========
function renderPagination(pagination) {
  const container = document.getElementById('paginationContainer');
  if (!container || !pagination) return;
  
  const { current_page, total_pages, has_previous, has_next, total_items } = pagination;
  
  if (total_pages <= 1) {
    container.innerHTML = '';
    return;
  }
  
  let html = '<nav aria-label="Paginação de salas"><ul class="pagination justify-content-center mb-0">';
  
  // Botão Anterior
  html += `<li class="page-item ${!has_previous ? 'disabled' : ''}">
    <a class="page-link" href="#" data-page="${current_page - 1}" ${!has_previous ? 'tabindex="-1"' : ''}>
      <i class="bi bi-chevron-left"></i>
    </a>
  </li>`;
  
  // Números das páginas
  const maxVisible = 5;
  let startPage = Math.max(1, current_page - Math.floor(maxVisible / 2));
  let endPage = Math.min(total_pages, startPage + maxVisible - 1);
  
  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1);
  }
  
  if (startPage > 1) {
    html += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
    if (startPage > 2) {
      html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
    }
  }
  
  for (let i = startPage; i <= endPage; i++) {
    html += `<li class="page-item ${i === current_page ? 'active' : ''}">
      <a class="page-link" href="#" data-page="${i}">${i}</a>
    </li>`;
  }
  
  if (endPage < total_pages) {
    if (endPage < total_pages - 1) {
      html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
    }
    html += `<li class="page-item"><a class="page-link" href="#" data-page="${total_pages}">${total_pages}</a></li>`;
  }
  
  // Botão Próximo
  html += `<li class="page-item ${!has_next ? 'disabled' : ''}">
    <a class="page-link" href="#" data-page="${current_page + 1}" ${!has_next ? 'tabindex="-1"' : ''}>
      <i class="bi bi-chevron-right"></i>
    </a>
  </li>`;
  
  html += '</ul></nav>';
  html += `<div class="text-center text-muted small mt-2">Mostrando página ${current_page} de ${total_pages} (${total_items} salas)</div>`;
  
  container.innerHTML = html;
  
  // Event listeners para paginação
  container.querySelectorAll('.page-link[data-page]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const page = parseInt(link.dataset.page);
      if (page && page !== current_page && page >= 1 && page <= total_pages) {
        currentPage = page;
        loadAndRender(page);
      }
    });
  });
}

// ========== LOAD AND RENDER ==========
async function loadAndRender(page = 1) {
  const body = document.getElementById('salasTableBody');
  const data = await fetchSalas(page);
  const arr = data.salas || [];
  paginationData = data.pagination;
  currentPage = page;
  
  console.info("[salas-ui] renderizando tabela", { total: arr.length, page });
  body.innerHTML = '';
  
  if (!arr.length) {
    body.innerHTML = '<tr class="js-empty-row"><td colspan="6" class="text-center text-muted py-4">Nenhuma sala cadastrada ainda.</td></tr>';
    renderPagination(null);
    return;
  }
  
  arr.forEach(s => body.appendChild(renderSalaRow(s)));
  renderPagination(paginationData);
}

function showErrors(list) {
  const box = document.getElementById('modalErrors');
  const ul = document.getElementById('modalErrorsList');
  if (!box || !ul) return;
  ul.innerHTML = list.map(x => `<li>${x}</li>`).join('');
  box.classList.remove('d-none');
}

function hideErrors() {
  const box = document.getElementById('modalErrors');
  if (box) box.classList.add('d-none');
}

// ========== DOM READY ==========
document.addEventListener('DOMContentLoaded', () => {
  loadAndRender(1);
  
  // Busca local (filtra na página atual)
  const search = document.getElementById('searchInput');
  if (search) {
    search.addEventListener('input', e => {
      const q = e.target.value.toLowerCase();
      document.querySelectorAll('#salasTableBody tr').forEach(tr => {
        if (tr.classList.contains('js-empty-row')) return;
        const name = tr.querySelector('.sala-nome')?.textContent.toLowerCase() || '';
        const tipo = tr.querySelector('.sala-tipo')?.textContent.toLowerCase() || '';
        tr.style.display = (name.includes(q) || tipo.includes(q)) ? '' : 'none';
      });
    });
  }

  // Limpar formulário ao clicar em Adicionar Sala
  const btnAdd = document.getElementById('btnAdd');
  if (btnAdd) {
    btnAdd.addEventListener('click', () => {
      document.getElementById('modalTitle').textContent = 'Adicionar Nova Sala';
      document.getElementById('modalNome').value = '';
      document.getElementById('modalCapacidade').value = '';
      document.getElementById('modalTipo').value = '';
      document.getElementById('modalEquip').value = '';
      document.getElementById('modalDesc').value = '';
      document.getElementById('modalSalaId').value = '';
      const submitBtn = document.getElementById('modalSubmit');
      if (submitBtn) submitBtn.textContent = 'Adicionar Sala';
      hideErrors();
    });
  }

  // Submit do modal
  const modalSubmit = document.getElementById('modalSubmit');
  modalSubmit?.addEventListener('click', async () => {
    hideErrors();
    const id = document.getElementById('modalSalaId').value;
    const equipRaw = document.getElementById('modalEquip').value;
    const equipList = equipRaw ? equipRaw.split(',').map(e => e.trim()).filter(Boolean) : [];
    const payload = {
      nome: document.getElementById('modalNome').value,
      capacidade: document.getElementById('modalCapacidade').value,
      tipo: document.getElementById('modalTipo').value,
      equipamentos: equipList,
      descricao: document.getElementById('modalDesc').value
    };
    const csrf = getCsrfToken();
    console.info("[salas-ui] submit sala", { id, payload });
    
    try {
      let res;
      if (id) {
        res = await fetch(detailUrl(id), {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
          body: JSON.stringify(payload)
        });
      } else {
        res = await fetch(listUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
          body: JSON.stringify(payload)
        });
      }
      
      console.info("[salas-ui] resposta ao salvar sala", { status: res.status });
      
      if (!res.ok) {
        let data = {};
        try { data = await res.json(); } catch (e) { data = {}; }
        const detail = typeof data.detail === "string" ? data.detail : "Erro";
        console.warn("[salas-ui] erro ao salvar sala", { status: res.status, body: data });
        if (detail.toLowerCase().includes('reserva')) {
          showSnackbar(detail, 'warning');
        }
        showErrors([detail]);
        return;
      }
      
      // Success
      const bsModal = bootstrap.Modal.getInstance(document.getElementById('modalSala'));
      bsModal?.hide();
      showSnackbar(id ? 'Sala atualizada com sucesso!' : 'Sala criada com sucesso!', 'success');
      loadAndRender(currentPage);
    } catch (err) {
      console.error("[salas-ui] falha de rede ao salvar sala", err);
      showErrors(['Erro de rede']);
    }
  });

  // Click na tabela (editar/excluir)
  document.getElementById('salasTableBody')?.addEventListener('click', async (e) => {
    const edit = e.target.closest('.btn-edit');
    const del = e.target.closest('.btn-delete');
    
    if (edit) {
      const id = edit.dataset.id;
      console.info("[salas-ui] editar sala acionado", { id });
      const tr = document.querySelector(`tr[data-id="${id}"]`);
      document.getElementById('modalTitle').textContent = 'Editar Sala';
      const submitBtn = document.getElementById('modalSubmit');
      if (submitBtn) submitBtn.textContent = 'Salvar alterações';
      document.getElementById('modalNome').value = tr.querySelector('.sala-nome').textContent;
      document.getElementById('modalCapacidade').value = tr.querySelector('.sala-capacidade').textContent.replace(/\D/g, '');
      document.getElementById('modalTipo').value = tr.dataset.tipo || '';
      
      const equipField = document.getElementById('modalEquip');
      if (equipField) {
        const eq = tr._meta?.equipamentos || ((tr.dataset.equipamentos || '').split(',').filter(Boolean));
        equipField.value = eq.join(', ');
      }
      
      const descField = document.getElementById('modalDesc');
      if (descField) {
        descField.value = tr._meta?.descricao || tr.dataset.descricao || '';
      }
      
      document.getElementById('modalSalaId').value = id;
      new bootstrap.Modal(document.getElementById('modalSala')).show();
      return;
    }
    
    if (del) {
      if (!confirm('Tem certeza que deseja excluir esta sala?')) return;
      const id = del.dataset.id;
      console.info("[salas-ui] solicitando exclusão da sala", { id });
      const csrf = getCsrfToken();
      
      try {
        const res = await fetch(deleteUrl(id), {
          method: 'DELETE',
          headers: { 'X-CSRFToken': csrf }
        });
        
        console.info("[salas-ui] resposta exclusão", { status: res.status });
        
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          const msg = data.detail || 'Erro ao excluir sala';
          if (msg.toLowerCase().includes('reserva')) {
            showSnackbar('Não é possível excluir: existem reservas para esta sala.', 'error');
          } else {
            showSnackbar(msg, 'error');
          }
          return;
        }
        
        showSnackbar('Sala excluída com sucesso!', 'success');
        loadAndRender(currentPage);
      } catch (err) {
        console.error('[salas-ui] erro de rede ao excluir', err);
        showSnackbar('Erro de rede ao excluir sala', 'error');
      }
    }
  });
});
