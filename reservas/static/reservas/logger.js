/**
 * Sistema de logging condicional para JavaScript
 * Em produção (detectado por hostname ou configuração), suprime logs
 */

const IS_PRODUCTION = 
  window.location.hostname !== 'localhost' && 
  window.location.hostname !== '127.0.0.1' &&
  !window.location.hostname.includes('dev') &&
  !window.location.hostname.includes('test');

const logger = {
  log: (...args) => {
    if (!IS_PRODUCTION) {
      console.log(...args);
    }
  },
  
  error: (...args) => {
    // Erros sempre são logados, mas apenas em formato genérico em produção
    if (IS_PRODUCTION) {
      console.error('Ocorreu um erro. Entre em contato com o suporte.');
    } else {
      console.error(...args);
    }
  },
  
  warn: (...args) => {
    if (!IS_PRODUCTION) {
      console.warn(...args);
    }
  },
  
  info: (...args) => {
    if (!IS_PRODUCTION) {
      console.info(...args);
    }
  },
  
  debug: (...args) => {
    if (!IS_PRODUCTION) {
      console.debug(...args);
    }
  }
};

// Exporta para uso global
window.logger = logger;
