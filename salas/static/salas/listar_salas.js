document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchRoom");
    const filterButtons = Array.from(document.querySelectorAll(".filter-btn"));
    const cards = Array.from(document.querySelectorAll(".room-card"));
    const noResults = document.getElementById("noResults");

    function applyFilters() {
        const term = (searchInput?.value || "").toLowerCase();
        const activeFilter = document.querySelector(".filter-btn.active")?.dataset.filter || "all";
        let visibleCount = 0;

        cards.forEach((card) => {
            const wrapper = card.closest(".room-wrapper") || card;
            const status = card.dataset.status || "";
            const searchBlob = (card.dataset.search || "").toLowerCase();
            const matchesSearch = !term || searchBlob.includes(term);
            const matchesStatus = activeFilter === "all" || (activeFilter === "available" && status === "Disponivel");
            const shouldShow = matchesSearch && matchesStatus;

            wrapper.classList.toggle("d-none", !shouldShow);
            if (shouldShow) visibleCount += 1;
        });

        if (noResults) {
            noResults.classList.toggle("d-none", visibleCount > 0);
        }
    }

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            filterButtons.forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");
            applyFilters();
        });
    });

    searchInput?.addEventListener("input", applyFilters);

    if (window.lucide) {
        window.lucide.createIcons();
    }

    applyFilters();
});
