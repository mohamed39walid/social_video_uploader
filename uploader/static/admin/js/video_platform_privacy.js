document.addEventListener("DOMContentLoaded", function () {
    const platformCheckboxes = document.querySelectorAll('input[name="platforms"]');
    const privacyFields = document.querySelectorAll('.platform-privacy');

    // Function to toggle privacy visibility
    function togglePrivacy() {
        privacyFields.forEach((privacy) => {
            const platform = privacy.dataset.platform;
            const checkbox = Array.from(platformCheckboxes).find(c => c.value === platform);
            if (checkbox && checkbox.checked) {
                privacy.closest('.form-row').style.display = 'block';
            } else {
                privacy.closest('.form-row').style.display = 'none';
            }
        });
    }

    // Initial toggle on page load
    togglePrivacy();

    // Add change listener on checkboxes
    platformCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', togglePrivacy);
    });
});
