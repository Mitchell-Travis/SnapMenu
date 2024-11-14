document.addEventListener('DOMContentLoaded', function() {
    const tableInfoModal = new bootstrap.Modal(document.getElementById('tableInfoModal'), {
        backdrop: 'static',
        keyboard: false
    });
    const dinerCountGrid = document.getElementById('dinerCountGrid');
    const tableInfoForm = document.getElementById('tableInfoForm');
    let selectedCount = 0;

    // Create number buttons
    for (let i = 1; i <= 12; i++) {
        const col = document.createElement('div');
        col.className = 'col';
        col.innerHTML = `
            <input type="radio" class="btn-check" name="dinerCount" id="diner${i}" value="${i}" autocomplete="off">
            <label class="btn btn-outline-primary w-100" for="diner${i}">${i}</label>
        `;
        dinerCountGrid.appendChild(col);
    }

    // Handle button selection
    dinerCountGrid.addEventListener('change', function(e) {
        if (e.target.type === 'radio') {
            selectedCount = parseInt(e.target.value);
        }
    });

    // Handle form submission
    tableInfoForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (selectedCount > 0) {
            console.log(`Number of diners selected: ${selectedCount}`);
            // Here you can add code to proceed to the ordering system
            tableInfoModal.hide();
            // You might want to store this value or pass it to another function
            // For example: initializeOrderingSystem(selectedCount);
        } else {
            alert('Please select the number of diners.');
        }
    });

    // Show the modal automatically when the page loads
    tableInfoModal.show();
});
