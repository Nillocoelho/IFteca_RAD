let reservaParaCancelar = null;

document.addEventListener('click', function(e){
  if(e.target.closest('.btn-cancel')){
    const btn = e.target.closest('.btn-cancel');
    reservaParaCancelar = btn.getAttribute('data-id');
    
    // Atualiza o texto do modal com informações da linha
    const row = btn.closest('tr');
    const usuario = row.cells[0].querySelector('.fw-semibold').textContent;
    const sala = row.cells[1].textContent.trim();
    const data = row.cells[2].textContent.trim();
    const horario = row.cells[3].textContent;
    
    const modalTexto = document.getElementById('modalTexto');
    modalTexto.innerHTML = `Você está prestes a cancelar a reserva de <strong>${usuario}</strong> para a <strong>${sala}</strong> no dia <strong>${data}</strong> das <strong>${horario}</strong>. Esta ação não pode ser desfeita.`;
    
    // Abre o modal
    const modal = new bootstrap.Modal(document.getElementById('modalCancelar'));
    modal.show();
  }
});

document.getElementById('btnConfirmarCancelar').addEventListener('click', function(){
  if(!reservaParaCancelar) return;
  
  fetch(`/reservas/admin/reservas/${reservaParaCancelar}/cancelar/`, {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'X-Requested-With': 'XMLHttpRequest'
    },
    credentials: 'same-origin'
  }).then(r=>r.json()).then(j=>{
    if(j.success){
      // Fecha o modal
      const modal = bootstrap.Modal.getInstance(document.getElementById('modalCancelar'));
      modal.hide();
      
      // Atualiza a linha da tabela
      const btn = document.querySelector(`.btn-cancel[data-id="${reservaParaCancelar}"]`);
      if(btn){
        const row = btn.closest('tr');
        row.cells[4].innerHTML = '<span class="badge bg-danger">Cancelada</span>';
        btn.remove();
      }
      
      reservaParaCancelar = null;
    } else {
      alert(j.error || j.message || 'Erro ao cancelar');
    }
  }).catch(err=>{
    console.error(err);
    alert('Erro ao comunicar com o servidor.');
  });
});

