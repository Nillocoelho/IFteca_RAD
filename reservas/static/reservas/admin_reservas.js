document.addEventListener('click', function(e){
  if(e.target.closest('.btn-cancel')){
    const btn = e.target.closest('.btn-cancel');
    const reservaId = btn.getAttribute('data-id');
    if(!confirm('Cancelar esta reserva?')) return;
    fetch(`/reservas/admin/reservas/${reservaId}/cancelar/`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'same-origin'
    }).then(r=>r.json()).then(j=>{
      if(j.success){
        btn.closest('tr').querySelectorAll('td')[4].innerHTML = '<span class="badge bg-danger">Cancelada</span>';
        btn.remove();
      } else {
        alert(j.error || j.message || 'Erro ao cancelar');
      }
    }).catch(err=>{
      console.error(err);alert('Erro ao comunicar com o servidor.');
    });
  }
});
