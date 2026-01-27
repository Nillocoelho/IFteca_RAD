# Sistema de Logging JavaScript

## Uso do Logger Condicional

Foi implementado um sistema de logging condicional que suprime logs em produção.

### Como Usar

1. **Incluir o logger.js nos templates HTML:**

```html
<script src="{% static 'reservas/logger.js' %}"></script>
```

2. **Usar o logger em vez de console diretamente:**

```javascript
// ❌ EVITAR (expõe em produção):
console.log('Dados sensíveis:', data);
console.error('Erro:', error);

// ✅ RECOMENDADO (suprimido em produção):
window.logger.log('Dados sensíveis:', data);
window.logger.error('Erro:', error);
```

### API do Logger

- `logger.log(...)` - Suprimido em produção
- `logger.error(...)` - Mostra mensagem genérica em produção
- `logger.warn(...)` - Suprimido em produção
- `logger.info(...)` - Suprimido em produção
- `logger.debug(...)` - Suprimido em produção

### Detecção de Ambiente

Produção é detectada quando o hostname NÃO é:
- `localhost`
- `127.0.0.1`
- Contém `dev`
- Contém `test`

### Fallback

Se `logger.js` não estiver carregado, o código deve ter fallback:

```javascript
if (window.logger) {
  window.logger.error("Erro", error);
} else if (window.location.hostname === 'localhost') {
  console.error("Erro", error);
}
```

## Arquivos JavaScript que Devem Ser Atualizados

Os seguintes arquivos ainda usam `console.log` diretamente e devem ser migrados:

- `salas/static/salas/forms.js`
- `salas/static/salas/detalhar_sala.js`
- `reservas/static/reservas/*.js`

Para migrar, substitua:
- `console.log` → `logger.log`
- `console.error` → `logger.error`
- `console.warn` → `logger.warn`
