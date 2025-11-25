document.addEventListener("DOMContentLoaded", () => {
    const PAGE_SIZE = 6;
    const searchInput = document.getElementById("searchRoom");
    const filterButtons = Array.from(document.querySelectorAll(".filter-btn"));
    const cards = Array.from(document.querySelectorAll(".room-card"));
    const wrappers = cards.map((card) => card.closest(".room-wrapper") || card);
    const noResults = document.getElementById("noResults");
    const paginationRow = document.getElementById("paginationRow");
    const prevPageBtn = document.getElementById("prevPage");
    const nextPageBtn = document.getElementById("nextPage");
    const pageIndicator = document.getElementById("pageIndicator");

    let filteredWrappers = [...wrappers];
    let currentPage = 1;

    function applyFilters() {
        const term = (searchInput?.value || "").toLowerCase();
        const activeFilter = document.querySelector(".filter-btn.active")?.dataset.filter || "all";
        let visibleCount = 0;
        const matched = [];

        cards.forEach((card, idx) => {
            const wrapper = wrappers[idx];
            const status = card.dataset.status || "";
            const searchBlob = (card.dataset.search || "").toLowerCase();
            const matchesSearch = !term || searchBlob.includes(term);
            const matchesStatus = activeFilter === "all" || (activeFilter === "available" && status === "Disponivel");
            const shouldShow = matchesSearch && matchesStatus;

            wrapper.classList.add("d-none");
            if (shouldShow) {
                matched.push(wrapper);
                visibleCount += 1;
            }
        });

        filteredWrappers = matched;
        const totalPages = Math.max(1, Math.ceil(filteredWrappers.length / PAGE_SIZE));
        if (currentPage > totalPages) currentPage = totalPages;
        applyPagination();
        updatePaginationUI(totalPages);

        if (noResults) noResults.classList.toggle("d-none", visibleCount > 0);
    }

    function applyPagination() {
        filteredWrappers.forEach((wrapper, idx) => {
            const pageIndex = Math.floor(idx / PAGE_SIZE) + 1;
            const onPage = pageIndex === currentPage;
            wrapper.classList.toggle("d-none", !onPage);
        });
    }

    function updatePaginationUI(totalPages) {
        if (!paginationRow || !pageIndicator || !prevPageBtn || !nextPageBtn) return;
        const hasPagination = totalPages > 1;
        paginationRow.classList.toggle("d-none", !hasPagination);
        pageIndicator.textContent = `${currentPage}/${totalPages}`;
        prevPageBtn.disabled = currentPage <= 1;
        nextPageBtn.disabled = currentPage >= totalPages;
    }

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            filterButtons.forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");
            applyFilters();
        });
    });

    searchInput?.addEventListener("input", applyFilters);

    prevPageBtn?.addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage -= 1;
            applyPagination();
            const totalPages = Math.max(1, Math.ceil(filteredWrappers.length / PAGE_SIZE));
            updatePaginationUI(totalPages);
        }
    });

    nextPageBtn?.addEventListener("click", () => {
        const totalPages = Math.max(1, Math.ceil(filteredWrappers.length / PAGE_SIZE));
        if (currentPage < totalPages) {
            currentPage += 1;
            applyPagination();
            updatePaginationUI(totalPages);
        }
    });

    if (window.lucide) {
        window.lucide.createIcons();
    }

    applyFilters();
});
