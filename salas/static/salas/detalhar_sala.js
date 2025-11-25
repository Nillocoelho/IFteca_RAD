document.addEventListener("DOMContentLoaded", () => {
    const calendarGrid = document.getElementById("calendarGrid");
    const monthLabel = document.getElementById("monthLabel");
    const slotDateLabel = document.getElementById("slotDateLabel");
    const prevBtn = document.getElementById("prevMonth");
    const nextBtn = document.getElementById("nextMonth");

    const today = new Date();
    let currentMonth = today.getMonth();
    let currentYear = today.getFullYear();
    let selectedDate = new Date(today);

    function renderCalendar() {
        if (!calendarGrid) return;
        calendarGrid.innerHTML = "";
        const firstDay = new Date(currentYear, currentMonth, 1);
        const startDay = firstDay.getDay(); // 0=Sun
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

        const monthName = firstDay.toLocaleString("default", { month: "long" });
        if (monthLabel) {
            monthLabel.textContent = `${monthName.charAt(0).toUpperCase() + monthName.slice(1)} ${currentYear}`;
        }

        // leading blanks
        for (let i = 0; i < startDay; i++) {
            const div = document.createElement("div");
            div.className = "day muted";
            div.textContent = "";
            calendarGrid.appendChild(div);
        }

        for (let d = 1; d <= daysInMonth; d++) {
            const dateCell = document.createElement("div");
            dateCell.className = "day";
            dateCell.textContent = d;
            const thisDate = new Date(currentYear, currentMonth, d);
            if (isSameDate(thisDate, selectedDate)) {
                dateCell.classList.add("selected");
            }
            dateCell.addEventListener("click", () => {
                selectedDate = thisDate;
                updateSelectedDate();
            });
            calendarGrid.appendChild(dateCell);
        }
    }

    function updateSelectedDate() {
        renderCalendar();
        if (slotDateLabel) {
            const options = { day: "2-digit", month: "2-digit", year: "numeric" };
            slotDateLabel.textContent = `Horários disponíveis para ${selectedDate.toLocaleDateString("pt-BR", options)}:`;
        }
    }

    function isSameDate(a, b) {
        return a.getDate() === b.getDate() && a.getMonth() === b.getMonth() && a.getFullYear() === b.getFullYear();
    }

    prevBtn?.addEventListener("click", () => {
        currentMonth -= 1;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear -= 1;
        }
        renderCalendar();
    });

    nextBtn?.addEventListener("click", () => {
        currentMonth += 1;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear += 1;
        }
        renderCalendar();
    });

    if (window.lucide) {
        window.lucide.createIcons();
    }

    updateSelectedDate();
});
