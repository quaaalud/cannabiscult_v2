let terpeneChartInstance = null;
function generateColors(count) {
  const colors = [
    'rgba(63, 81, 181, 0.5)', 'rgba(77, 182, 172, 0.5)', 'rgba(66, 133, 244, 0.5)',
    'rgba(156, 39, 176, 0.5)', 'rgba(233, 30, 99, 0.5)', 'rgba(66, 73, 244, 0.4)',
    'rgba(66, 133, 244, 0.2)'
  ];
  return colors.slice(0, count);
}
function attachResizeListener(canvas) {
  let resizeTimeout;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      if (terpeneChartInstance) {
        initTerpeneChart(terpeneChartInstance.data.labels, terpeneChartInstance.data.datasets[0].data);
      }
    }, 300);
  });
}
export default function initTerpeneChart(labels, dataValues) {
    const canvasContainer = document.getElementById('terpene_text');
    const existingCanvas = document.getElementById('terpeneChart');
    if (existingCanvas) {
        existingCanvas.remove();
    }
    const newCanvas = document.createElement('canvas');
    newCanvas.id = 'terpeneChart';
    canvasContainer.appendChild(newCanvas);

    const ctx = newCanvas.getContext('2d');
    if (terpeneChartInstance) {
        terpeneChartInstance.destroy();
    }
    terpeneChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Terpenes',
                data: dataValues,
                backgroundColor: generateColors(labels.length),
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 500,
            },
        }
    });
    attachResizeListener(newCanvas);
}

