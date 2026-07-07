(function() {
    function calcFinalPrice() {
        var price = parseFloat(document.getElementById('id_price')?.value) || 0;
        var discount = parseFloat(document.getElementById('id_discount')?.value) || 0;
        var final = discount > 0 ? (price * (1 - discount / 100)).toFixed(2) : price.toFixed(2);
        var el = document.getElementById('final-price-preview');
        if (el) {
            el.textContent = '$' + final;
            el.style.color = discount > 0 ? 'green' : '#333';
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        // اضافه کردن preview بعد از فیلد discount
        var discountField = document.getElementById('id_discount');
        if (discountField) {
            var preview = document.createElement('span');
            preview.id = 'final-price-preview';
            preview.style.cssText = 'margin-left:10px; font-weight:bold; font-size:14px;';
            discountField.parentNode.appendChild(preview);

            discountField.addEventListener('input', calcFinalPrice);
            var priceField = document.getElementById('id_price');
            if (priceField) priceField.addEventListener('input', calcFinalPrice);

            calcFinalPrice();
        }
    });
})();
