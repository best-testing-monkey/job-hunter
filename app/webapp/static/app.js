function initThresholdSlider(sliderEl, readoutEl, onChange) {
  const storageKey = "confidenceThreshold";
  const defaultValue = "65";

  // Read initial value from localStorage
  const initialValue = localStorage.getItem(storageKey) || defaultValue;
  sliderEl.value = initialValue;
  readoutEl.textContent = `${initialValue}%`;

  // Call onChange immediately with initial value
  onChange(initialValue);

  // On input event: write to localStorage, update readout, call onChange
  sliderEl.addEventListener("input", (event) => {
    const value = event.target.value;
    localStorage.setItem(storageKey, value);
    readoutEl.textContent = `${value}%`;
    onChange(value);
  });
}

function makeSortable(tableEl) {
  const headers = tableEl.querySelectorAll("th[data-sort-key]");
  let originalOrder = null;
  let currentSortColumn = null;
  let currentDirection = null; // "asc", "desc", or null

  headers.forEach((header) => {
    header.style.cursor = "pointer";
    header.style.userSelect = "none";

    header.addEventListener("click", () => {
      // Get the body rows
      const tbody = tableEl.querySelector("tbody");
      const rows = Array.from(tbody.querySelectorAll("tr"));

      // Cache the original order on first sort
      if (originalOrder === null) {
        originalOrder = rows.slice();
      }

      const sortKey = header.getAttribute("data-sort-key");

      // If clicking the same column, cycle the direction
      if (currentSortColumn === sortKey) {
        if (currentDirection === null) {
          currentDirection = "asc";
        } else if (currentDirection === "asc") {
          currentDirection = "desc";
        } else {
          currentDirection = null;
        }
      } else {
        // Clicking a different column: reset to ascending
        currentSortColumn = sortKey;
        currentDirection = "asc";
      }

      // Clear arrows from all headers
      headers.forEach((h) => {
        h.textContent = h.textContent.replace(/\s*[▼▲]$/, "");
      });

      // If unsorted, restore original order
      if (currentDirection === null) {
        rows.forEach((row, index) => {
          tbody.appendChild(originalOrder[index]);
        });
        currentSortColumn = null;
      } else {
        // Sort the rows
        const sortedRows = rows.slice();
        sortedRows.sort((rowA, rowB) => {
          const cellA = rowA.querySelector(`td[data-sort-value]`);
          const cellB = rowB.querySelector(`td[data-sort-value]`);

          if (!cellA || !cellB) return 0;

          const valueA = cellA.getAttribute("data-sort-value");
          const valueB = cellB.getAttribute("data-sort-value");

          // Try to parse as numbers
          const numA = parseFloat(valueA);
          const numB = parseFloat(valueB);
          const isNumA = !isNaN(numA) && isFinite(numA);
          const isNumB = !isNaN(numB) && isFinite(numB);

          let comparison;
          if (isNumA && isNumB) {
            comparison = numA - numB;
          } else {
            comparison = valueA.localeCompare(valueB);
          }

          return currentDirection === "asc" ? comparison : -comparison;
        });

        // Re-append rows in sorted order
        sortedRows.forEach((row) => {
          tbody.appendChild(row);
        });

        // Add arrow to the current header
        const arrow = currentDirection === "asc" ? "▼" : "▲";
        header.textContent += ` ${arrow}`;
      }
    });
  });
}

function pollRematchStatus(resumeId, iconEl, intervalMs = 2000) {
  iconEl.classList.add("spinning");

  const pollInterval = setInterval(async () => {
    try {
      const response = await fetch(`/resumes/${resumeId}/rematch-status`);
      const data = await response.json();

      if (!data.running) {
        iconEl.classList.remove("spinning");
        clearInterval(pollInterval);
      }
    } catch (error) {
      console.error("Error polling rematch status:", error);
      iconEl.classList.remove("spinning");
      clearInterval(pollInterval);
    }
  }, intervalMs);
}
