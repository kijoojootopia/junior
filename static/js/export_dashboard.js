const status = document.getElementById("trade-status");
const title = document.getElementById("country-title");
const amount = document.getElementById("latest-export");
const growth = document.getElementById("growth-rate");
const series = document.getElementById("export-series");
let activeRequest;

document.querySelectorAll("[data-country]").forEach(button => {
  button.addEventListener("click", async () => {
    const country = button.dataset.country;
    activeRequest?.abort();
    activeRequest = new AbortController();
    document.querySelectorAll("[data-country]").forEach(item => {
      item.setAttribute("aria-pressed", String(item.dataset.country === country));
    });
    title.textContent = button.textContent;
    status.textContent = "자료를 불러오는 중입니다.";
    amount.textContent = growth.textContent = "—";
    series.replaceChildren();
    try {
      const response = await fetch(`/api/export/trade?country=${encodeURIComponent(country)}`, { signal: activeRequest.signal });
      if (!response.ok) throw new Error("자료를 불러오지 못했습니다.");
      const data = await response.json();
      if (!data.series.length) {
        status.textContent = "등록된 수출 통계가 없습니다.";
        return;
      }
      status.textContent = "";
      amount.textContent = new Intl.NumberFormat("ko-KR").format(data.latest.export_usd);
      growth.textContent = data.growth_pct === null ? "산정 불가" : `${data.growth_pct}%`;
      const chart = document.createElement("div");
      chart.className = "trade-chart";
      const maximum = Math.max(...data.series.map(row => row.export_usd), 1);
      data.series.forEach(row => {
        const item = document.createElement("div");
        item.className = "trade-chart-row";
        const label = document.createElement("span");
        label.textContent = row.year;
        const bar = document.createElement("meter");
        bar.min = 0;
        bar.max = maximum;
        bar.value = row.export_usd;
        bar.setAttribute("aria-label", `${row.year}년 수출액`);
        const value = document.createElement("span");
        value.textContent = `${new Intl.NumberFormat("ko-KR").format(row.export_usd)} USD`;
        item.append(label, bar, value);
        chart.append(item);
      });
      series.append(chart);
    } catch (error) {
      if (error.name !== "AbortError") status.textContent = error.message;
    }
  });
});
