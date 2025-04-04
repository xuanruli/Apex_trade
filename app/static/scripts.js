let stockChart;

function fetchStockData(symbol, timeframe = "daily") {
    fetch(`/api/stock-data/${timeframe}?symbol=${symbol}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("No stock data available.", data.error);
                document.getElementById("stockChart").innerHTML = "<p style='color: red;'>No data available.</p>";
                return;
            }

            if (stockChart) {
                stockChart.destroy();
            }

            const ctx = document.getElementById("stockChart").getContext("2d");
            stockChart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: `Stock Price (${timeframe})`,
                        data: data.prices,
                        borderColor: "blue",
                        borderWidth: 2,
                        pointRadius: 3,
                        fill: true,
                        backgroundColor: "rgba(0, 0, 255, 0.1)",
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { title: { display: true, text: "Date" } },
                        y: { title: { display: true, text: "Closing Price ($)" } }
                    }
                }
            });
        })
        .catch(error => {
            console.error("Error fetching stock data:", error);
            document.getElementById("stockChart").innerHTML = "<p style='color: red;'>Error loading stock data.</p>";
        });
}

function fetchStockNews(symbol) {
    fetch(`/api/news?symbol=${symbol}`)
        .then(response => response.json())
        .then(data => {
            const newsList = document.getElementById("news-list");
            newsList.innerHTML = "";
            if (!data || data.length === 0) {
                newsList.innerHTML = "<p style='color: red;'>No news available.</p>";
                return;
            }

            data.forEach(news => {
                const li = document.createElement("li");
                li.className = "list-group-item";
                li.innerHTML = `
                    <h5>${news.title}</h5>
                    <p>${news.summary}</p>
                    <small class="text-muted">${news.date}</small>
                `;
                newsList.appendChild(li);
            });
        })
        .catch(error => {
            console.error("Error fetching news:", error);
            document.getElementById("news-list").innerHTML = "<p style='color: red;'>Error loading news.</p>";
        });
}

function updateChart(timeframe) {
    const stockSymbol = document.getElementById("stockSymbol").dataset.symbol;
    fetchStockData(stockSymbol, timeframe);
}

document.addEventListener("DOMContentLoaded", function () {
    const stockSymbol = document.getElementById("stockSymbol").dataset.symbol;
    fetchStockData(stockSymbol, "daily");
    fetchStockNews(stockSymbol);
});