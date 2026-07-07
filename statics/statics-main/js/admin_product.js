(function() {
    document.addEventListener('DOMContentLoaded', function() {

        function updateFinalFromDiscount(row) {
            var priceInput = row.querySelector('input[id*="price"]');
            var discountInput = row.querySelector('input[id*="discount"]');
            var finalInput = row.querySelector('input.final-price-input');
            if (!priceInput || !discountInput || !finalInput) return;

            var price = parseFloat(priceInput.value) || 0;
            var discount = parseFloat(discountInput.value) || 0;

            // محدود کردن درصد به 0-100
            if (discount > 100) { discount = 100; discountInput.value = 100; }
            if (discount < 0) { discount = 0; discountInput.value = 0; }

            var final = discount > 0 ? (price * (1 - discount / 100)).toFixed(2) : price.toFixed(2);
            finalInput.value = final;
            finalInput.style.color = discount > 0 ? 'green' : '#333';
            finalInput.style.fontWeight = discount > 0 ? 'bold' : 'normal';
        }

        function updateDiscountFromFinal(row) {
            var priceInput = row.querySelector('input[id*="price"]');
            var discountInput = row.querySelector('input[id*="discount"]');
            var finalInput = row.querySelector('input.final-price-input');
            if (!priceInput || !discountInput || !finalInput) return;

            var price = parseFloat(priceInput.value) || 0;
            var final = parseFloat(finalInput.value) || 0;

            // قیمت نهایی نمیتونه بیشتر از قیمت اصلی یا منفی باشه
            if (final > price) { final = price; finalInput.value = price; }
            if (final < 0) { final = 0; finalInput.value = 0; }

            if (price > 0) {
                var discount = Math.round((1 - final / price) * 100);
                discountInput.value = discount;
            }
        }

        function initRows() {
            var rows = document.querySelectorAll('#result_list tbody tr');
            rows.forEach(function(row) {
                var priceInput = row.querySelector('input[id*="price"]');
                var discountInput = row.querySelector('input[id*="discount"]');
                var finalCell = row.querySelector('.field-final_price');
                if (!priceInput || !discountInput || !finalCell) return;

                var currentFinal = finalCell.textContent.trim().replace('$', '');
                var finalInput = document.createElement('input');
                finalInput.type = 'number';
                finalInput.step = '0.01';
                finalInput.min = '0';
                finalInput.value = currentFinal;
                finalInput.className = 'final-price-input';
                finalInput.style.cssText = 'width:70px; padding:2px 4px; color:green; font-weight:bold;';
                finalCell.innerHTML = '';
                finalCell.appendChild(finalInput);

                discountInput.addEventListener('input', function() { updateFinalFromDiscount(row); });
                priceInput.addEventListener('input', function() { updateFinalFromDiscount(row); });
                finalInput.addEventListener('input', function() { updateDiscountFromFinal(row); });
            });
        }

        initRows();
    });
})();