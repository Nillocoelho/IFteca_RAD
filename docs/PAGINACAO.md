# Implementação de Paginação com Django Paginator

## 📋 Visão Geral

Este documento descreve a implementação de paginação usando o `Paginator` do Django conforme requisito obrigatório do projeto final.

## 🎯 Views com Paginação Implementada

### 1. **Listagem de Salas** (`listar_salas`)
- **Arquivo**: [salas/views.py](salas/views.py)
- **URL**: `/salas/`
- **Itens por página**: 6 salas
- **Usuários**: Todos (pública)

**Código:**
```python
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

paginator = Paginator(salas, 6)  # 6 salas por página
page_number = request.GET.get('page', 1)
try:
    page_obj = paginator.get_page(page_number)
except (EmptyPage, PageNotAnInteger):
    page_obj = paginator.get_page(1)
```

### 2. **Minhas Reservas** (`minhas_reservas`)
- **Arquivo**: [reservas/views.py](reservas/views.py)
- **URL**: `/reservas/minhas-reservas/`
- **Itens por página**: 10 reservas anteriores
- **Usuários**: Estudantes autenticados
- **Observação**: Reservas ativas não são paginadas (sempre visíveis)

**Código:**
```python
paginator = Paginator(reservas_anteriores_qs, 10)  # 10 reservas por página
page_number = request.GET.get('page', 1)
try:
    page_obj = paginator.get_page(page_number)
except (EmptyPage, PageNotAnInteger):
    page_obj = paginator.get_page(1)
```

### 3. **Gerenciar Reservas Admin** (`admin_reservas`)
- **Arquivo**: [reservas/views.py](reservas/views.py)
- **URL**: `/reservas/admin/reserva/`
- **Itens por página**: 15 reservas
- **Usuários**: Administradores
- **Observação**: Preserva filtros de sala e data na paginação

**Código:**
```python
paginator = Paginator(reservas_enriched, 15)  # 15 reservas por página
page_number = request.GET.get('page', 1)
try:
    page_obj = paginator.get_page(page_number)
except (EmptyPage, PageNotAnInteger):
    page_obj = paginator.get_page(1)
```

## 🎨 Implementação nos Templates

### Estrutura do Controle de Paginação

Todos os templates usam o mesmo padrão de paginação Bootstrap 5:

```django
{% if page_obj.has_other_pages %}
<div class="d-flex justify-content-center align-items-center mt-4">
    <nav aria-label="Navegação de páginas">
        <ul class="pagination">
            <!-- Botão Anterior -->
            {% if page_obj.has_previous %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page_obj.previous_page_number }}">
                        <span>&laquo;</span>
                    </a>
                </li>
            {% else %}
                <li class="page-item disabled">
                    <span class="page-link">&laquo;</span>
                </li>
            {% endif %}

            <!-- Números das Páginas -->
            {% for num in page_obj.paginator.page_range %}
                {% if page_obj.number == num %}
                    <li class="page-item active">
                        <span class="page-link">{{ num }}</span>
                    </li>
                {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
                    <li class="page-item">
                        <a class="page-link" href="?page={{ num }}">{{ num }}</a>
                    </li>
                {% endif %}
            {% endfor %}

            <!-- Botão Próximo -->
            {% if page_obj.has_next %}
                <li class="page-item">
                    <a class="page-link" href="?page={{ page_obj.next_page_number }}">
                        <span>&raquo;</span>
                    </a>
                </li>
            {% else %}
                <li class="page-item disabled">
                    <span class="page-link">&raquo;</span>
                </li>
            {% endif %}
        </ul>
    </nav>
</div>
{% endif %}
```

### Templates Modificados

1. **[salas/templates/salas/listar_salas.html](salas/templates/salas/listar_salas.html)**
   - Paginação adicionada após a grid de salas
   - Mantém paginação JavaScript para compatibilidade com filtros

2. **[reservas/templates/reservas/minhas_reservas.html](reservas/templates/reservas/minhas_reservas.html)**
   - Paginação apenas para reservas anteriores
   - Integrada na seção de histórico

3. **[reservas/templates/reservas/admin_reservas.html](reservas/templates/reservas/admin_reservas.html)**
   - Paginação preserva filtros de busca (sala e data)
   - URLs incluem parâmetros: `?page=2&sala=1&data=2026-01-20`

## 🧪 Testes Automatizados

### Arquivo de Testes
**[salas/tests/test_pagination.py](salas/tests/test_pagination.py)** - 6 testes

### Casos de Teste

1. **`test_listar_salas_primeira_pagina`**
   - Verifica que a primeira página mostra 6 salas
   - Confirma que `has_next()` é True
   - Confirma que `has_previous()` é False

2. **`test_listar_salas_segunda_pagina`**
   - Testa navegação para segunda página
   - Verifica que tem página anterior e próxima

3. **`test_listar_salas_ultima_pagina`**
   - Verifica que última página mostra salas restantes
   - Confirma que não há próxima página

4. **`test_listar_salas_pagina_invalida`**
   - Testa comportamento com página inexistente
   - Deve redirecionar para última página válida

5. **`test_listar_salas_paginator_info`**
   - Valida propriedades do paginator
   - Conta total, número de páginas, itens por página

6. **`test_pagination_preserva_url_parameters`**
   - Testa que filtros não interferem na paginação
   - Salas inativas não aparecem na contagem

### Executar Testes

```bash
# Testes de paginação apenas
docker-compose exec web python manage.py test salas.tests.test_pagination -v 2

# Todos os testes (150)
docker-compose exec web python manage.py test --parallel
```

## 📊 Resultados

✅ **6 testes de paginação - TODOS PASSARAM**
✅ **150 testes totais do projeto - TODOS PASSARAM**

## 🔑 Recursos do Paginator Django Utilizados

### Propriedades e Métodos

```python
page_obj.number                    # Número da página atual
page_obj.has_previous()            # Tem página anterior?
page_obj.has_next()                # Tem próxima página?
page_obj.previous_page_number      # Número da página anterior
page_obj.next_page_number          # Número da próxima página
page_obj.has_other_pages()         # Tem mais de uma página?
page_obj.paginator.count           # Total de itens
page_obj.paginator.num_pages       # Total de páginas
page_obj.paginator.per_page        # Itens por página
page_obj.paginator.page_range      # Range de números de páginas
```

## 🎯 Atendimento aos Requisitos

### Requisito: "Paginação"

✅ **COMPLETO - Backend com Django Paginator**

- ✅ Usa `django.core.paginator.Paginator`
- ✅ Implementado em 3 views principais
- ✅ Controles de navegação nos templates
- ✅ Preserva filtros e parâmetros de URL
- ✅ Tratamento de erros (páginas inválidas)
- ✅ Testes automatizados validando funcionamento
- ✅ Documentação completa

### Funcionalidades Extras

- Paginação JavaScript mantida para UX (compatibilidade com filtros frontend)
- Controles acessíveis com ARIA labels
- Design responsivo com Bootstrap 5
- Janela de páginas visíveis (mostra ±2 páginas da atual)

## 📝 Notas de Implementação

1. **Tratamento de Erros**: Usa `try/except` para lidar com `EmptyPage` e `PageNotAnInteger`
2. **Fallback Inteligente**: Páginas inválidas redirecionam para página 1
3. **Preservação de Estado**: Filtros são mantidos nos links de paginação
4. **Performance**: QuerySets são avaliados apenas uma vez por página
5. **Acessibilidade**: Elementos semânticos e labels apropriados

## 🚀 Demonstração

Para ver a paginação em ação:

1. Acesse http://localhost:8000/salas/
2. Se houver mais de 6 salas, controles de paginação aparecem
3. Navegue entre páginas usando os botões

---

**Data de Implementação**: 19 de janeiro de 2026  
**Desenvolvedor**: Nillo Coelho  
**Projeto**: IFteca_RAD - Sistema de Reserva de Salas
