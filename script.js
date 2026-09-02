const dates = [
  { label: '09 Oct 2020', rates: [-0.545, -0.523, -0.329, 0.155, 0.854] },
  { label: '09 Sep 2020', rates: [-0.504, -0.499, -0.179, 0.359, 1.069] },
  { label: '07 Aug 2020', rates: [-0.502, -0.476, -0.209, 0.293, 1.011] },
  { label: '09 Jul 2020', rates: [-0.462, -0.447, -0.114, 0.412, 1.161] },
  { label: '09 Jun 2020', rates: [-0.455, -0.421, 0.058, 0.590, 1.427] }
];
const chart = document.querySelector('#detail-chart');
const selectedDate = document.querySelector('#selected-date');
const longRate = document.querySelector('#long-rate');
const curveMove = document.querySelector('#curve-move');

function smoothRates(rates) {
  return rates.map((rate, index) => {
    const previous = rates[Math.max(0, index - 1)];
    const next = rates[Math.min(rates.length - 1, index + 1)];
    return rate * 0.7 + ((previous + next) / 2) * 0.3;
  });
}

function renderChart(index) {
  const snapshot = dates[index];
  const fit = smoothRates(snapshot.rates);
  const plot = { left: 44, right: 728, top: 24, bottom: 330 };
  const minRate = -0.7;
  const maxRate = 1.6;
  const x = (position) => plot.left + (position / 4) * (plot.right - plot.left);
  const y = (value) => plot.bottom - ((value - minRate) / (maxRate - minRate)) * (plot.bottom - plot.top);
  const gridValues = [-0.5, 0, 0.5, 1, 1.5];
  const grid = gridValues.map((value) => `<line class="detail-grid" x1="${plot.left}" x2="${plot.right}" y1="${y(value)}" y2="${y(value)}" /><text x="4" y="${y(value) + 4}" fill="#486581" font-size="10" font-family="DM Mono, monospace">${value.toFixed(1)}%</text>`).join('');
  const points = snapshot.rates.map((rate, pointIndex) => `${x(pointIndex)},${y(rate)}`).join(' ');
  const fitPoints = fit.map((rate, pointIndex) => `${x(pointIndex)},${y(rate)}`).join(' ');
  const dots = snapshot.rates.map((rate, pointIndex) => `<circle class="detail-observed" cx="${x(pointIndex)}" cy="${y(rate)}" r="6" />`).join('');
  chart.innerHTML = `${grid}<polyline class="detail-fit" points="${fitPoints}" /><polyline points="${points}" fill="none" stroke="#ec6a58" stroke-width="1" stroke-dasharray="3 5" opacity=".55" />${dots}`;
  selectedDate.textContent = snapshot.label;
  longRate.textContent = `${snapshot.rates[4].toFixed(3)}%`;
  const change = index === dates.length - 1 ? snapshot.rates[4] - dates[index - 1].rates[4] : snapshot.rates[4] - dates[index + 1].rates[4];
  const direction = change >= 0 ? '+' : '';
  curveMove.textContent = `${direction}${change.toFixed(2)} pts vs ${index === dates.length - 1 ? 'prior' : 'next'} snapshot`;
}

document.querySelectorAll('.date-button').forEach((button) => {
  button.addEventListener('click', () => {
    const activeButton = document.querySelector('.date-button.active');
    activeButton.classList.remove('active');
    activeButton.setAttribute('aria-selected', 'false');
    button.classList.add('active');
    button.setAttribute('aria-selected', 'true');
    renderChart(Number(button.dataset.index));
  });
});

renderChart(0);
