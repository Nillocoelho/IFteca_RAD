/* ==================================
   ADMIN DASHBOARD - IFTECA
   JavaScript: Charts & PDF Report
   ================================== */

// Cores do tema IFTECA
const COLORS = {
    primary: '#008B45',
    primaryLight: '#00a854',
    primaryDark: '#006d36',
    blue: '#2563eb',
    purple: '#9333ea',
    orange: '#ea580c',
    gray: '#6b7280',
    lightGray: '#e5e7eb',
};

// ==================================
// GRÁFICOS COM CHART.JS
// ==================================

document.addEventListener('DOMContentLoaded', function() {
    initMonthlyChart();
    initRoomUsageChart();
});

/**
 * Inicializa o gráfico de Reservas por Mês (Line Chart)
 */
function initMonthlyChart() {
    const ctx = document.getElementById('monthlyChart');
    if (!ctx) return;

    const labels = monthlyData.map(item => item.month);
    const data = monthlyData.map(item => item.total);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Reservas',
                data: data,
                borderColor: COLORS.primary,
                backgroundColor: 'rgba(0, 139, 69, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: COLORS.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1f2937',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y} reservas`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: COLORS.gray,
                        font: {
                            size: 12,
                            weight: 500
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: COLORS.lightGray
                    },
                    ticks: {
                        color: COLORS.gray,
                        font: {
                            size: 12
                        },
                        stepSize: 10
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

/**
 * Inicializa o gráfico de Taxa de Uso por Sala (Bar Chart)
 */
function initRoomUsageChart() {
    const ctx = document.getElementById('roomUsageChart');
    if (!ctx) return;

    const labels = roomData.map(item => item.name);
    const data = roomData.map(item => item.usage);

    // Gerar cores em gradiente de verde
    const backgroundColors = data.map((_, index) => {
        const opacity = 0.6 + (index * 0.08);
        return `rgba(0, 139, 69, ${Math.min(opacity, 1)})`;
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Taxa de Uso',
                data: data,
                backgroundColor: backgroundColors,
                borderColor: COLORS.primary,
                borderWidth: 1,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1f2937',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y}% de ocupação`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: COLORS.gray,
                        font: {
                            size: 11,
                            weight: 500
                        },
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: COLORS.lightGray
                    },
                    ticks: {
                        color: COLORS.gray,
                        font: {
                            size: 12
                        },
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// ==================================
// GERAÇÃO DE RELATÓRIO PDF
// ==================================

/**
 * Gera o relatório PDF do dashboard
 */
function generateReport() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 20;
    let yPos = 0;
    const footerMargin = 20;

    const ensureSpace = (needed = 0) => {
        if (yPos + needed > pageHeight - footerMargin) {
            doc.addPage();
            yPos = 30; // margem superior ao quebrar página
        }
    };

    // ==================================
    // CABEÇALHO
    // ==================================
    
    // "Logo" simples desenhado no PDF (ícone prédio)
    const logoX = margin;
    const logoY = 10;
    doc.setFillColor(233, 246, 255); // fundo claro
    doc.roundedRect(logoX, logoY, 18, 18, 4, 4, 'F');
    doc.setFillColor(0, 139, 69); // corpo do prédio
    doc.rect(logoX + 4, logoY + 4, 10, 10, 'F');
    doc.setFillColor(255, 255, 255); // janelas
    doc.rect(logoX + 5, logoY + 5, 3, 3, 'F');
    doc.rect(logoX + 10, logoY + 5, 3, 3, 'F');
    doc.rect(logoX + 5, logoY + 10, 3, 3, 'F');
    doc.rect(logoX + 10, logoY + 10, 3, 3, 'F');

    // Fundo verde do cabeçalho
    doc.setFillColor(0, 139, 69); // #008B45
    doc.rect(0, 0, pageWidth, 45, 'F');
    
    // Título principal
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(22);
    doc.setFont('helvetica', 'bold');
    doc.text('IFTECA - Sistema de Reservas', pageWidth / 2, 18, { align: 'center' });
    
    // Subtítulo
    doc.setFontSize(12);
    doc.setFont('helvetica', 'normal');
    doc.text('Instituto Federal da Paraíba - Campus João Pessoa', pageWidth / 2, 28, { align: 'center' });
    
    // Data do relatório
    const dataAtual = new Date().toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    doc.setFontSize(10);
    doc.text(`Relatório gerado em: ${dataAtual}`, pageWidth / 2, 38, { align: 'center' });
    
    yPos = 60;

    // ==================================
    // TÍTULO DA SEÇÃO: KPIs
    // ==================================
    
    doc.setTextColor(0, 139, 69);
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.text('Indicadores Principais (KPIs)', margin, yPos);
    
    yPos += 5;
    doc.setDrawColor(0, 139, 69);
    doc.setLineWidth(0.5);
    doc.line(margin, yPos, pageWidth - margin, yPos);
    
    yPos += 15;

    // ==================================
    // CARDS DE KPIs
    // ==================================
    
    const cardWidth = (pageWidth - margin * 2 - 15) / 2;
    const cardHeight = 35;
    
    // Card 1: Total de Reservas
    drawKPICard(doc, margin, yPos, cardWidth, cardHeight, 
        'Total de Reservas', kpis.totalReservas.toString(), '#2563eb');
    
    // Card 2: Salas Cadastradas
    drawKPICard(doc, margin + cardWidth + 15, yPos, cardWidth, cardHeight, 
        'Salas Cadastradas', kpis.totalSalas.toString(), '#008B45');
    
    yPos += cardHeight + 10;
    
    // Card 3: Usuários Ativos
    drawKPICard(doc, margin, yPos, cardWidth, cardHeight, 
        'Usuários Ativos', kpis.totalUsuarios.toString(), '#9333ea');
    
    // Card 4: Taxa de Ocupação
    drawKPICard(doc, margin + cardWidth + 15, yPos, cardWidth, cardHeight, 
        'Taxa de Ocupação', kpis.taxaOcupacao + '%', '#ea580c');
    
    yPos += cardHeight + 25;

    // ==================================
    // TÍTULO DA SEÇÃO: RESERVAS POR MÊS
    // ==================================
    
    ensureSpace(60);
    doc.setTextColor(0, 139, 69);
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.text('Reservas por Mês', margin, yPos);
    
    yPos += 5;
    doc.line(margin, yPos, pageWidth - margin, yPos);
    
    yPos += 10;

    // Tabela de reservas por mês
    doc.setFontSize(10);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(60, 60, 60);
    
    const colWidth = (pageWidth - margin * 2) / monthlyData.length;
    
    // Cabeçalho da tabela
    doc.setFillColor(240, 240, 240);
    doc.rect(margin, yPos, pageWidth - margin * 2, 10, 'F');
    
    monthlyData.forEach((item, index) => {
        const x = margin + (index * colWidth) + (colWidth / 2);
        doc.text(item.month, x, yPos + 7, { align: 'center' });
    });
    
    yPos += 12;
    
    // Valores
    doc.setFont('helvetica', 'normal');
    monthlyData.forEach((item, index) => {
        const x = margin + (index * colWidth) + (colWidth / 2);
        doc.text(item.total.toString(), x, yPos + 5, { align: 'center' });
    });
    
    yPos += 25;

    // ==================================
    // TÍTULO DA SEÇÃO: TAXA DE USO POR SALA
    // ==================================
    
    // Se a lista não couber na página atual, quebra antes de imprimir
    ensureSpace(roomData.length * 12 + 40);
    doc.setTextColor(0, 139, 69);
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.text('Taxa de Uso por Sala', margin, yPos);
    
    yPos += 5;
    doc.line(margin, yPos, pageWidth - margin, yPos);
    
    yPos += 10;

    // Lista de salas com barras de progresso
    doc.setFontSize(10);
    
    roomData.forEach((sala, index) => {
        ensureSpace(15); // quebra antes de cada item se faltar espaço
        // Nome da sala
        doc.setTextColor(60, 60, 60);
        doc.setFont('helvetica', 'normal');
        doc.text(sala.name, margin, yPos + 4);
        
        // Barra de fundo
        const barX = margin + 45;
        const barWidth = 100;
        const barHeight = 6;
        
        doc.setFillColor(230, 230, 230);
        doc.roundedRect(barX, yPos, barWidth, barHeight, 2, 2, 'F');
        
        // Barra de progresso
        doc.setFillColor(0, 139, 69);
        doc.roundedRect(barX, yPos, (barWidth * sala.usage) / 100, barHeight, 2, 2, 'F');
        
        // Porcentagem
        doc.setFont('helvetica', 'bold');
        doc.text(`${sala.usage}%`, barX + barWidth + 8, yPos + 5);
        
        yPos += 12;
    });
    
    yPos += 15;

    // ==================================
    // ALERTAS
    // ==================================
    
    ensureSpace(40);
    doc.setTextColor(0, 139, 69);
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.text('Alertas do Sistema', margin, yPos);
    
    yPos += 5;
    doc.line(margin, yPos, pageWidth - margin, yPos);
    
    yPos += 10;
    
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(60, 60, 60);
    
    if (kpis.salasManutencao > 0) {
        const blocoAltura = 12 + (salasManutencao?.length || 0) * 6 + 4;
        ensureSpace(blocoAltura);
        doc.setFillColor(254, 243, 199); // Amarelo claro
        doc.roundedRect(margin, yPos, pageWidth - margin * 2, blocoAltura, 3, 3, 'F');
        doc.text(`Alerta: ${kpis.salasManutencao} sala(s) em manutenção`, margin + 5, yPos + 8);
        yPos += 14;

        if (Array.isArray(salasManutencao) && salasManutencao.length) {
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(90, 90, 90);
            salasManutencao.forEach((nome) => {
                doc.text(`• ${nome}`, margin + 8, yPos + 4);
                yPos += 6;
            });
        }
    }
    
    if (kpis.reservasHoje > 0) {
        doc.setFillColor(219, 234, 254); // Azul claro
        doc.roundedRect(margin, yPos, pageWidth - margin * 2, 12, 3, 3, 'F');
        doc.text(`ℹ ${kpis.reservasHoje} reserva(s) finalizaram hoje`, margin + 5, yPos + 8);
        yPos += 16;
    }
    
    if (kpis.salasManutencao === 0 && kpis.reservasHoje === 0) {
        doc.setFillColor(220, 252, 231); // Verde claro
        doc.roundedRect(margin, yPos, pageWidth - margin * 2, 12, 3, 3, 'F');
        doc.text('✓ Nenhum alerta no momento', margin + 5, yPos + 8);
    }

    // ==================================
    // RODAPÉ (todas as páginas)
    // ==================================
    const totalPages = doc.getNumberOfPages();
    for (let i = 1; i <= totalPages; i++) {
        doc.setPage(i);
        const footerY = pageHeight - 20;
        
        doc.setDrawColor(200, 200, 200);
        doc.setLineWidth(0.3);
        doc.line(margin, footerY - 5, pageWidth - margin, footerY - 5);
        
        doc.setFontSize(8);
        doc.setTextColor(128, 128, 128);
        doc.setFont('helvetica', 'normal');
        
        doc.text('IFTECA - Sistema de Gerenciamento de Salas', margin, footerY);
        doc.text('Instituto Federal da Paraíba', pageWidth / 2, footerY, { align: 'center' });
        doc.text(`Página ${i} de ${totalPages}`, pageWidth - margin, footerY, { align: 'right' });
    }

    // ==================================
    // SALVAR PDF
    // ==================================
    
    const nomeArquivo = `IFTECA_Relatorio_${new Date().toISOString().split('T')[0]}.pdf`;
    doc.save(nomeArquivo);
    
    // Notificação de sucesso
    showNotification('Relatório PDF gerado com sucesso!', 'success');
}

/**
 * Desenha um card de KPI no PDF
 */
function drawKPICard(doc, x, y, width, height, label, value, color) {
    // Fundo do card
    doc.setFillColor(248, 249, 250);
    doc.roundedRect(x, y, width, height, 4, 4, 'F');
    
    // Borda colorida à esquerda
    const rgb = hexToRgb(color);
    doc.setFillColor(rgb.r, rgb.g, rgb.b);
    doc.rect(x, y, 4, height, 'F');
    
    // Valor
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(rgb.r, rgb.g, rgb.b);
    doc.text(value, x + 15, y + 18);
    
    // Label
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(100, 100, 100);
    doc.text(label, x + 15, y + 28);
}

/**
 * Converte cor hexadecimal para RGB
 */
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : { r: 0, g: 0, b: 0 };
}

/**
 * Exibe uma notificação toast
 */
function showNotification(message, type = 'info') {
    // Remove notificação existente
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();
    
    // Cria nova notificação
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <i class="bi ${type === 'success' ? 'bi-check-circle' : 'bi-info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Estilos inline
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#008B45' : '#2563eb'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        font-size: 14px;
        font-weight: 500;
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Adiciona animação CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    // Remove após 4 segundos
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ==================================
// ATUALIZAÇÃO AUTOMÁTICA (OPCIONAL)
// ==================================

/**
 * Atualiza os dados do dashboard via API
 */
async function refreshDashboard() {
    try {
        const response = await fetch('/reservas/api/dashboard/');
        const data = await response.json();
        
        // Atualizar KPIs na página
        // (Implementar se necessário atualização em tempo real)
        
        console.log('Dashboard data refreshed:', data);
    } catch (error) {
        console.error('Erro ao atualizar dashboard:', error);
    }
}

// Atualizar a cada 5 minutos (opcional)
// setInterval(refreshDashboard, 300000);
