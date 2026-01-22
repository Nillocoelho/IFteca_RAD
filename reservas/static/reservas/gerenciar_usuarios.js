/**
 * Gerenciar Usuários - JavaScript
 */
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('searchInput');
  const filterTipo = document.getElementById('filterTipo');
  const filterStatus = document.getElementById('filterStatus');
  const tableBody = document.getElementById('usersTableBody');
  const rows = tableBody.querySelectorAll('tr[data-id]');
  const feedback = document.getElementById('feedback');
  
  // Modal elements
  const modalEl = document.getElementById('modalConfirm');
  const modal = modalEl ? new bootstrap.Modal(modalEl) : null;
  const modalTitle = document.getElementById('modalTitle');
  const modalMessage = document.getElementById('modalMessage');
  const btnConfirm = document.getElementById('btnConfirm');
  
  let pendingAction = null;

  // ========================
  // Filtros de busca
  // ========================
  function applyFilters() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    const tipoFilter = filterTipo.value.toLowerCase();
    const statusFilter = filterStatus.value.toLowerCase();
    
    let visibleCount = 0;
    
    rows.forEach(row => {
      const nome = (row.dataset.nome || '').toLowerCase();
      const email = (row.dataset.email || '').toLowerCase();
      const tipo = (row.dataset.tipo || '').toLowerCase();
      const status = (row.dataset.status || '').toLowerCase();
      
      const matchesSearch = !searchTerm || 
        nome.includes(searchTerm) || 
        email.includes(searchTerm);
      
      const matchesTipo = !tipoFilter || tipo === tipoFilter;
      const matchesStatus = !statusFilter || status === statusFilter;
      
      if (matchesSearch && matchesTipo && matchesStatus) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });
    
    // Mostrar mensagem se não houver resultados
    const emptyRow = tableBody.querySelector('.empty-row');
    if (emptyRow) {
      emptyRow.style.display = visibleCount === 0 && rows.length > 0 ? '' : 'none';
    }
  }
  
  // Event listeners para filtros
  if (searchInput) {
    searchInput.addEventListener('input', applyFilters);
  }
  
  if (filterTipo) {
    filterTipo.addEventListener('change', applyFilters);
  }
  
  if (filterStatus) {
    filterStatus.addEventListener('change', applyFilters);
  }

  // ========================
  // Toggle Ativar/Desativar
  // ========================
  function showFeedback(message, type = 'success') {
    feedback.textContent = message;
    feedback.className = `alert alert-${type}`;
    feedback.classList.remove('d-none');
    
    setTimeout(() => {
      feedback.classList.add('d-none');
    }, 4000);
  }

  function toggleUserStatus(userId, currentActive) {
    const action = currentActive ? 'desativar' : 'ativar';
    const actionPast = currentActive ? 'desativado' : 'ativado';
    
    // Encontra a linha do usuário
    const row = tableBody.querySelector(`tr[data-id="${userId}"]`);
    if (!row) return;
    
    const userName = row.dataset.nome;
    
    // Configura o modal
    modalTitle.textContent = `${currentActive ? 'Desativar' : 'Ativar'} Usuário`;
    modalMessage.textContent = `Tem certeza que deseja ${action} o usuário "${userName}"?`;
    btnConfirm.className = currentActive ? 'btn btn-danger' : 'btn btn-success';
    btnConfirm.textContent = currentActive ? 'Desativar' : 'Ativar';
    
    pendingAction = { userId, currentActive, row };
    modal.show();
  }

  // Handler para confirmar ação
  if (btnConfirm) {
    btnConfirm.addEventListener('click', async () => {
      if (!pendingAction) return;
      
      const { userId, currentActive, row } = pendingAction;
      
      try {
        const response = await fetch(`/reservas/admin/usuarios/${userId}/toggle/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
          },
        });
        
        const data = await response.json();
        
        if (response.ok) {
          // Atualiza a linha da tabela
          const newActive = !currentActive;
          const statusBadge = row.querySelector('.badge-status');
          const toggleBtn = row.querySelector('.btn-toggle');
          
          // Atualiza status badge
          statusBadge.textContent = newActive ? 'Ativo' : 'Inativo';
          statusBadge.className = `badge-status badge-${newActive ? 'ativo' : 'inativo'}`;
          
          // Atualiza botão toggle
          toggleBtn.dataset.active = newActive.toString();
          toggleBtn.className = `btn-action btn-toggle ${newActive ? 'btn-deactivate' : 'btn-activate'}`;
          toggleBtn.title = newActive ? 'Desativar usuário' : 'Ativar usuário';
          toggleBtn.querySelector('i').className = `bi ${newActive ? 'bi-toggle-on' : 'bi-toggle-off'}`;
          
          // Atualiza data attribute
          row.dataset.status = newActive ? 'ativo' : 'inativo';
          
          showFeedback(data.message || `Usuário ${newActive ? 'ativado' : 'desativado'} com sucesso!`, 'success');
        } else {
          showFeedback(data.error || 'Erro ao atualizar usuário.', 'danger');
        }
      } catch (error) {
        console.error('Erro:', error);
        showFeedback('Erro de conexão. Tente novamente.', 'danger');
      }
      
      modal.hide();
      pendingAction = null;
    });
  }

  // Event delegation para botões de toggle
  tableBody.addEventListener('click', (e) => {
    const toggleBtn = e.target.closest('.btn-toggle');
    if (toggleBtn) {
      const userId = parseInt(toggleBtn.dataset.id);
      const currentActive = toggleBtn.dataset.active === 'true';
      toggleUserStatus(userId, currentActive);
    }
  });

  // ========================
  // CRIAR USUÁRIO
  // ========================
  const formCriarUsuario = document.getElementById('formCriarUsuario');
  const criarUsuarioFeedback = document.getElementById('criarUsuarioFeedback');
  
  if (formCriarUsuario) {
    formCriarUsuario.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const btnSubmit = document.getElementById('btnCriarUsuario');
      const originalText = btnSubmit.innerHTML;
      
      // Coletar dados do formulário
      const data = {
        first_name: document.getElementById('novoNome').value.trim(),
        last_name: document.getElementById('novoSobrenome').value.trim(),
        email: document.getElementById('novoEmail').value.trim(),
        password: document.getElementById('novoSenha').value,
        tipo: document.getElementById('novoTipo').value,
      };
      
      // Validação básica
      if (!data.first_name || !data.last_name || !data.email || !data.password || !data.tipo) {
        showModalFeedback('Preencha todos os campos obrigatórios.', 'danger');
        return;
      }
      
      if (data.password.length < 6) {
        showModalFeedback('A senha deve ter no mínimo 6 caracteres.', 'danger');
        return;
      }
      
      // Desabilitar botão
      btnSubmit.disabled = true;
      btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Criando...';
      
      try {
        const response = await fetch('/reservas/admin/usuarios/criar/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
          },
          body: JSON.stringify(data),
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
          showModalFeedback(result.message, 'success');
          
          // Limpar formulário
          formCriarUsuario.reset();
          
          // Recarregar página após 1.5s para mostrar novo usuário
          setTimeout(() => {
            window.location.reload();
          }, 1500);
        } else {
          showModalFeedback(result.error || 'Erro ao criar usuário.', 'danger');
        }
      } catch (error) {
        console.error('Erro:', error);
        showModalFeedback('Erro de conexão. Tente novamente.', 'danger');
      } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = originalText;
      }
    });
    
    // Limpar feedback ao abrir modal
    const modalCriarUsuario = document.getElementById('modalCriarUsuario');
    if (modalCriarUsuario) {
      modalCriarUsuario.addEventListener('show.bs.modal', () => {
        formCriarUsuario.reset();
        criarUsuarioFeedback.classList.add('d-none');
      });
    }
  }
  
  function showModalFeedback(message, type) {
    if (criarUsuarioFeedback) {
      criarUsuarioFeedback.textContent = message;
      criarUsuarioFeedback.className = `alert alert-${type}`;
      criarUsuarioFeedback.classList.remove('d-none');
    }
  }

  // ========================
  // CSRF Token
  // ========================
  function getCSRFToken() {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
    return cookieValue || '';
  }
});
