document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");

    // If search input not present, stop safely
    if (!searchInput) return;

    searchInput.addEventListener("input", () => {
        const query = searchInput.value.trim().toLowerCase();
        const movieCards = document.querySelectorAll(".movie-card");

        movieCards.forEach(card => {
            const title = card.getAttribute("data-title") || "";
            
            // Show / hide without breaking flex layout
            if (title.includes(query)) {
                card.style.display = "";
            } else {
                card.style.display = "none";
            }
        });
    });
});
