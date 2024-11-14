document.addEventListener('DOMContentLoaded', function() {
    const sections = ['ordersSection', 'userSection', 'settingsSection', 'editProfileSection', 'addMediaSection', 'ourDishSection'];
    const icons = ['ordersIcon', 'userIcon', 'ourDishIcon']; // Add other icon IDs as needed

    function hideAllSections() {
        sections.forEach(section => {
            const sectionElement = document.getElementById(section);
            if (sectionElement) {
                sectionElement.style.display = 'none';
            }
        });
    }

    function showSection(sectionId) {
        hideAllSections();
        const sectionElement = document.getElementById(sectionId);
        if (sectionElement) {
            sectionElement.style.display = 'block';
        }
    }

    function resetIconColors() {
        icons.forEach(icon => {
            const iconElement = document.getElementById(icon);
            if (iconElement) {
                iconElement.classList.remove('btn-warning');
                const labelElement = iconElement.querySelector('.icon-label');
                if (labelElement) {
                    labelElement.classList.remove('btn-warning');
                }
            }
        });
    }

    // Show ourDishSection by default on page load
    showSection('ourDishSection');
    const ourDishIcon = document.getElementById('ourDishIcon');
    ourDishIcon.classList.add('btn-warning'); // Set default color for ourDishIcon
    const ourDishLabel = ourDishIcon.querySelector('.icon-label');
    if (ourDishLabel) {
        ourDishLabel.classList.add('btn-warning');
    }

    // Add event listeners for each icon
    document.getElementById('ordersIcon').addEventListener('click', function() {
        showSection('ordersSection');
        resetIconColors();
        this.classList.add('btn-warning');
        const labelElement = this.querySelector('.icon-label');
        if (labelElement) {
            labelElement.classList.add('btn-warning');
        }
    });

    document.getElementById('userIcon').addEventListener('click', function() {
        showSection('userSection');
        resetIconColors();
        this.classList.add('btn-warning');
        const labelElement = this.querySelector('.icon-label');
        if (labelElement) {
            labelElement.classList.add('btn-warning');
        }
    });

    document.getElementById('ourDishIcon').addEventListener('click', function() {
        const ourDishSection = document.getElementById('ourDishSection');
        if (ourDishSection.style.display !== 'block') {
            showSection('ourDishSection');
        }
        resetIconColors();
        this.classList.add('btn-warning');
        const labelElement = this.querySelector('.icon-label');
        if (labelElement) {
            labelElement.classList.add('btn-warning');
        }
    });

    // Add similar event listeners for other icons as needed
});
