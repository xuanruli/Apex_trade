document.addEventListener('DOMContentLoaded', function() {
    const tradeSidebar = document.getElementById('tradeSidebar');
    const closeTradeSidebarBtn = document.querySelector('.close-sidebar-btn');
    const pageOverlay = document.querySelector('.page-overlay');

    // Close sidebar when clicking the close button
    closeTradeSidebarBtn.addEventListener('click', function() {
        tradeSidebar.classList.remove('active');
        pageOverlay.classList.remove('active');
    });

    // Close sidebar when clicking outside
    pageOverlay.addEventListener('click', function() {
        tradeSidebar.classList.remove('active');
        pageOverlay.classList.remove('active');
    });

    // Handle order type selection (buy/sell)
    document.querySelectorAll('.order-type-btn').forEach(button => {
        button.addEventListener('click', function() {
            const orderType = this.dataset.type;
            setOrderType(orderType);
            updateTradeTotalPrice();
        });
    });

    // Handle order type changes (market/limit)
    document.getElementById('tradeOrderType').addEventListener('change', function() {
        const selectedType = this.value;
        const priceInput = document.getElementById('tradePriceInput');

        // Show price input for limit and stop orders, hide for market orders
        if (selectedType === 'market') {
            priceInput.style.display = 'none';
        } else {
            priceInput.style.display = 'block';
        }

        updateTradeTotalPrice();
    });

    // Update the total price whenever quantity or price changes
    document.getElementById('tradeQuantity').addEventListener('input', updateTradeTotalPrice);
    document.getElementById('tradePrice').addEventListener('input', updateTradeTotalPrice);

    // Restful API
    document.getElementById('tradeForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const quantity = parseInt(document.getElementById('tradeQuantity').value) || 0;
        const actionType = document.getElementById('actionType').value;
        const currentShares = parseInt(document.getElementById('tradeCurrentHoldings').textContent) || 0;

        // Basic Check
        if (quantity <= 0) {
            const alertEl = document.getElementById('tradeSidebarAlert');
            alertEl.textContent = 'Short selling is not allowed';
            alertEl.classList.remove('d-none');
            setTimeout(() => {
              alertEl.classList.add('d-none');
            }, 3000);
            return;
        }

        if (actionType === 'sell' && quantity > currentShares) {
            const alertEl = document.getElementById('tradeSidebarAlert');
            alertEl.textContent = 'Selling shares must be less than holding';
            alertEl.classList.remove('d-none');
            setTimeout(() => {
              alertEl.classList.add('d-none');
            }, 3000);
            return;
        }

        // API
        const jsonData = {
            symbol: document.getElementById('tradeSymbolInput').value,
            actionType: document.getElementById('actionType').value,
            quantity: document.getElementById('tradeQuantity').value,
            orderType: document.getElementById('tradeOrderType').value
        };

        if (jsonData.orderType === 'limit') {
            jsonData.price = document.getElementById('tradePrice').value;
        } else {
            jsonData.price = document.getElementById('tradeCurrentPrice').textContent;
        }

        fetch('/trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                 window.location.reload();
            } else {
                const alertEl = document.getElementById('tradeSidebarAlert');
                alertEl.textContent = data.message || 'Trade failed';
                alertEl.classList.remove('d-none');
            }
        })
        .catch(error => {
            const alertEl = document.getElementById('tradeSidebarAlert');
            alertEl.textContent = 'Trade error';
            alertEl.classList.remove('d-none');
        });
    });


    // Initialize price display for market orders on page load
    const orderTypeSelect = document.getElementById('tradeOrderType');
    if (orderTypeSelect.value === 'market') {
        document.getElementById('tradePriceInput').style.display = 'none';
    }
});

// Function to open the trade sidebar with pre-filled data
function openTradeSidebar(symbol, currentShares, currentPrice) {
    const tradeSidebar = document.getElementById('tradeSidebar');
    const pageOverlay = document.querySelector('.page-overlay');

    document.getElementById('tradeSymbolInput').value = symbol;

    // Set the current price
    document.getElementById('tradeCurrentPrice').textContent = currentPrice.toFixed(2);
    document.getElementById('tradePrice').value = currentPrice.toFixed(2);

    // Set current holdings
    document.getElementById('tradeCurrentHoldings').textContent = currentShares;

    // Default to "buy" action
    setOrderType('buy');

    // Set default quantity to 1
    document.getElementById('tradeQuantity').value = 1;

    // Calculate and display the estimated total
    updateTradeTotalPrice();

    // Display the sidebar and overlay
    tradeSidebar.classList.add('active');
    pageOverlay.classList.add('active');
}

// Set the active order type button
function setOrderType(type) {
    // Update the hidden input value
    document.getElementById('actionType').value = type;
    const placeOrderBtn = document.getElementById('place-order-btn');
    // Update the active class on buttons
    document.querySelectorAll('.order-type-btn').forEach(btn => {
        if (btn.dataset.type === type) {
            btn.classList.add('active');
            placeOrderBtn.classList.add('sell');
        } else {
            btn.classList.remove('active');
            placeOrderBtn.classList.remove('sell');
        }
    });
}

// Calculate and update the estimated total
function updateTradeTotalPrice() {
    const quantity = parseInt(document.getElementById('tradeQuantity').value) || 0;
    let price = parseFloat(document.getElementById('tradePrice').value) || 0;
    const orderType = document.getElementById('tradeOrderType').value;

    // For market orders, use the current price
    if (orderType === 'market') {
        price = parseFloat(document.getElementById('tradeCurrentPrice').textContent);
    }

    const total = quantity * price;
    document.getElementById('tradeTotalPrice').textContent = total.toFixed(2);
}