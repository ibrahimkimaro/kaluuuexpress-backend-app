// Static JavaScript for Invoice Auto-Calculation in Django Admin

(function () {
    'use strict';

    // Wait for the DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCalculator);
    } else {
        initCalculator();
    }

    function initCalculator() {
        // Get the form elements
        const weightField = document.getElementById('id_weight_kg');
        const serviceTierField = document.getElementById('id_service_tier');
        const weightHandlingField = document.getElementById('id_weight_handling');
        const payingBillField = document.getElementById('id_paying_bill');

        // Get the readonly display fields
        const totalAmountField = document.querySelector('.field-total_amount .readonly');
        const creditAmountField = document.querySelector('.field-credit_amount .readonly');

        // Check if we're on the add/change form
        if (!weightField || !serviceTierField || !weightHandlingField) {
            return; // Not on the invoice form
        }

        // Attach event listeners
        weightField.addEventListener('input', calculateTotals);
        serviceTierField.addEventListener('change', calculateTotals);
        weightHandlingField.addEventListener('change', calculateTotals);
        if (payingBillField) {
            payingBillField.addEventListener('input', calculateTotals);
        }

        // Initial calculation on page load
        calculateTotals();

        function calculateTotals() {
            const weight = parseFloat(weightField.value) || 0;
            const serviceTierId = serviceTierField.value;
            const weightHandlingId = weightHandlingField.value;
            const payingBill = parseFloat(payingBillField?.value) || 0;

            // If service tier or weight handling not selected, show message
            if (!serviceTierId || !weightHandlingId || weight === 0) {
                if (totalAmountField) {
                    totalAmountField.textContent = 'Select service tier, weight handling, and enter weight';
                }
                if (creditAmountField) {
                    creditAmountField.textContent = '-';
                }
                return;
            }

            // Fetch the prices using the custom admin endpoint
            const url = `/admin/shipping/invoice/get-prices/?service_tier_id=${serviceTierId}&weight_handling_id=${weightHandlingId}`;

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    const servicePrice = data.service_price || 0;
                    const handlingRate = data.handling_rate || 0;

                    // Calculate total amount
                    // Formula: weight_kg * price_per_kg_usd * rate_tsh_per_kg
                    const totalAmount = weight * servicePrice * handlingRate;

                    // Calculate credit amount (balance)
                    // Formula: total_amount - paying_bill
                    const creditAmount = totalAmount - payingBill;

                    // Update the display fields
                    if (totalAmountField) {
                        totalAmountField.textContent = totalAmount.toFixed(2);
                    }
                    if (creditAmountField) {
                        creditAmountField.textContent = creditAmount.toFixed(2);
                    }
                })
                .catch(error => {
                    console.error('Error fetching prices:', error);
                    if (totalAmountField) {
                        totalAmountField.textContent = 'Error calculating total';
                    }
                });
        }
    }
})();
