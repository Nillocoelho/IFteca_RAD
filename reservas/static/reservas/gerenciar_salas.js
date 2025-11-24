function getCsrfToken(){const m=document.cookie.match(/csrftoken=([^;]+)/);return m?decodeURIComponent(m[1]):""}

const API_BASE=(document.body.dataset.apiBase||"/reservas/admin/salas/").replace(/\/+$/,"");
const listUrl=`${API_BASE}/`;
const detailUrl=id=>`${API_BASE}/${id}/`;
const deleteUrl=id=>`${API_BASE}/${id}/delete/`;

async function fetchSalas(){
  const res=await fetch(listUrl,{credentials:"same-origin"});
  if(!res.ok) return [];
  return await res.json();
}

function renderSalaRow(s){
  const tr = document.createElement('tr');
  tr.dataset.id = s.id;
  const equipamentos = (s.equipamentos || []);
  const visibleEquip = equipamentos.slice(0, 2).map(e => `<span class="equip-tag">${e}</span>`).join(' ');
  const extra = equipamentos.length > 2 ? `<span class="text-muted">+${equipamentos.length - 2}</span>` : '';
  const statusText = s.status || s.status_text || "Disponivel";
  const statusPillClass =
    statusText === "Disponivel"
      ? "status-pill status-available"
      : statusText === "Ocupada"
      ? "status-pill status-occupied"
      : "status-pill status-maintenance";

  tr.innerHTML = `
    <td class="fw-semibold sala-nome">${s.nome}</td>
    <td class="sala-andar">${s.localizacao || s.andar || ""}</td>
    <td class="sala-capacidade">${s.capacidade} pessoas</td>
    <td class="sala-status"><span class="${statusPillClass}">${statusText}</span></td>
    <td class="sala-equip"><div class="equipments">${visibleEquip} ${extra}</div></td>
    <td class="text-end sala-actions">
      <button class="btn btn-sm btn-edit text-primary me-2" data-id="${s.id}" title="Editar"><i class="bi bi-pencil"></i></button>
      <button class="btn btn-sm btn-delete text-danger" data-id="${s.id}" title="Excluir"><i class="bi bi-trash"></i></button>
    </td>
  `;
  tr._meta = { equipamentos: equipamentos, descricao: s.descricao || "" };
  tr.dataset.nome = s.nome || "";
  tr.dataset.andar = s.localizacao || s.andar || "";
  tr.dataset.tipo = s.tipo || "";
  tr.dataset.equipamentos = (equipamentos || []).join(',');
  tr.dataset.descricao = s.descricao || "";
  return tr;
}

async function loadAndRender(){
  const body=document.getElementById('salasTableBody');
  const arr=await fetchSalas();
  body.innerHTML='';
  if(!arr.length){body.innerHTML='<tr class="js-empty-row"><td colspan="6" class="text-center text-muted py-4">Nenhuma sala cadastrada ainda.</td></tr>';return}
  arr.forEach(s=>body.appendChild(renderSalaRow(s)));
}

function showErrors(list){const box=document.getElementById('modalErrors');const ul=document.getElementById('modalErrorsList');if(!box||!ul) return;ul.innerHTML=list.map(x=>`<li>${x}</li>`).join('');box.classList.remove('d-none')}
function hideErrors(){const box=document.getElementById('modalErrors');if(box)box.classList.add('d-none')}

document.addEventListener('DOMContentLoaded',()=>{
  loadAndRender();
  const search=document.getElementById('searchInput');if(search){search.addEventListener('input',e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('#salasTableBody tr').forEach(tr=>{if(tr.classList.contains('js-empty-row')) return;const name=tr.querySelector('.sala-nome')?.textContent.toLowerCase()||'';const floor=tr.querySelector('.sala-andar')?.textContent.toLowerCase()||'';tr.style.display=(name.includes(q)||floor.includes(q))? '':'none';});});}

  const modalSubmit=document.getElementById('modalSubmit');
  modalSubmit?.addEventListener('click',async()=>{
    hideErrors();
    const id=document.getElementById('modalSalaId').value;
    const payload={nome:document.getElementById('modalNome').value,capacidade:document.getElementById('modalCapacidade').value,tipo:document.getElementById('modalTipo').value,localizacao:document.getElementById('modalAndar').value};
    const csrf=getCsrfToken();
    try{
      let res;
      if(id){res=await fetch(detailUrl(id),{method:'PUT',headers:{'Content-Type':'application/json','X-CSRFToken':csrf},body:JSON.stringify(payload)});}else{res=await fetch(listUrl,{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrf},body:JSON.stringify(payload)});}
      if(!res.ok){const data=await res.json();showErrors([data.detail||'Erro']);return}
      // success
      const bsModal=bootstrap.Modal.getInstance(document.getElementById('modalSala'));
      bsModal?.hide();
      loadAndRender();
    }catch(err){showErrors(['Erro de rede'])}
  });

  document.getElementById('salasTableBody')?.addEventListener('click',async(e)=>{
    const edit=e.target.closest('.btn-edit');
    const del=e.target.closest('.btn-delete');
    if(edit){const id=edit.dataset.id;const tr=document.querySelector(`tr[data-id="${id}"]`);document.getElementById('modalTitle').textContent='Editar Sala';document.getElementById('modalNome').value=tr.querySelector('.sala-nome').textContent;document.getElementById('modalCapacidade').value=tr.querySelector('.sala-capacidade').textContent.replace(/\D/g,'');document.getElementById('modalAndar').value=tr.querySelector('.sala-andar').textContent;document.getElementById('modalSalaId').value=id;new bootstrap.Modal(document.getElementById('modalSala')).show();return}
    if(del){if(!confirm('Tem certeza que deseja excluir esta sala?')) return;const id=del.dataset.id;const csrf=getCsrfToken();const res=await fetch(deleteUrl(id),{method:'DELETE',headers:{'X-CSRFToken':csrf}});if(!res.ok){alert('Erro ao excluir');return}loadAndRender();}
  });
});
