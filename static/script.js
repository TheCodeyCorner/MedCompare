// --------------------------------
// Elements
// --------------------------------

const searchForm =
    document.getElementById(
        "medicine-search-form"
    );


const searchInput =
    document.getElementById(
        "medicine-search"
    );


const container =
    document.querySelector(
        ".medicine-card-grid"
    );


// --------------------------------
// Search Medicines
// --------------------------------

if (searchForm) {

    searchForm.addEventListener(
        "submit",
        async function(event) {

            event.preventDefault();


            const medicineName =
                searchInput.value.trim();


            if (!medicineName) {
                return;
            }


            try {

                const response =
                    await fetch(
                        "/api/medicines",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                name: medicineName
                            })
                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        "Search failed"
                    );

                }


                const html =
                    await response.text();


                container.innerHTML =
                    html;


                setupFavoriteButtons();
                updateAnalytics();


            } catch (error) {

                console.error(
                    "Search error:",
                    error
                );


                container.innerHTML = `
                    <p>
                        Unable to search
                        for medicines.
                    </p>
                `;

            }

        }
    );

}


// --------------------------------
// Setup Favourite Buttons
// --------------------------------

function setupFavoriteButtons() {

    const favoriteButtons =
        document.querySelectorAll(
            ".favorite-button"
        );


    favoriteButtons.forEach(button => {

        button.addEventListener(
            "click",
            async function() {

                const medicineId =
                    this.dataset.id;


                // Determine new state

                const newFavoriteState =
                    !this.classList.contains(
                        "active"
                    );


                try {

                    const response =
                        await fetch(
                            "/api/favorite",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    id: medicineId,

                                    favorite:
                                        newFavoriteState
                                })
                            }
                        );


                    const result =
                        await response.json();


                    if (!result.success) {

                        throw new Error(
                            "Favorite update failed"
                        );

                    }


                    // --------------------------------
                    // Favourites page
                    // Remove card after unfavourite
                    // --------------------------------

                    if (
                        !newFavoriteState &&
                        window.location.pathname
                            === "/favorites"
                    ) {

                        const card =
                            this.closest(
                                ".medicine-card"
                            );


                        if (card) {

                            card.remove();

                        }


                        // No favourites left

                        if (
                            document.querySelectorAll(
                                ".medicine-card"
                            ).length === 0
                        ) {

                            container.innerHTML = `
                                <p class="no-favorites">
                                    No favorite
                                    medicines yet.
                                </p>
                            `;

                        }


                        return;

                    }


                    // --------------------------------
                    // Normal search page
                    // --------------------------------

                    const heart =
                        this.querySelector(
                            ".favorite-heart"
                        );


                    if (newFavoriteState) {

                        this.classList.add(
                            "active"
                        );


                        heart.textContent =
                            "♥";


                        this.setAttribute(
                            "aria-label",
                            "Remove from favorites"
                        );

                    } else {

                        this.classList.remove(
                            "active"
                        );


                        heart.textContent =
                            "♡";


                        this.setAttribute(
                            "aria-label",
                            "Add to favorites"
                        );

                    }


                } catch (error) {

                    console.error(
                        "Favorite error:",
                        error
                    );

                }

            }
        );

    });

}


// --------------------------------
// Load Favourites
// --------------------------------

async function loadFavorites() {

    const favoritesContainer =
        document.getElementById(
            "favorites-grid"
        );


    if (!favoritesContainer) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/favorites"
            );


        if (!response.ok) {

            throw new Error(
                "Failed to load favorites"
            );

        }


        const html =
            await response.text();


        favoritesContainer.innerHTML =
            html;


        setupFavoriteButtons();


    } catch (error) {

        console.error(
            "Favorites error:",
            error
        );


        favoritesContainer.innerHTML = `
            <p>
                Unable to load favorites.
            </p>
        `;

    }

}


// --------------------------------
// Analytics Charts
// (population driven by /api/analytics, which reads
// the server's database/results.csv)
// --------------------------------

let manufacturerChartInstance = null;
let typeChartInstance = null;


function initCharts() {

    const manufacturerCanvas =
        document.getElementById(
            "manufacturerChart"
        );

    const typeCanvas =
        document.getElementById(
            "typeChart"
        );


    // These canvases only exist on index.html, so bail
    // out quietly on pages (e.g. favorites) that don't
    // have them.
    if (!manufacturerCanvas || !typeCanvas) {
        return;
    }


    manufacturerChartInstance = new Chart(

        manufacturerCanvas.getContext("2d"),

        {
            type: "bar",

            data: {
                labels: [],

                datasets: [{
                    label: "Products in Last Search",
                    data: [],
                    backgroundColor: "#2563eb"
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    title: {
                        display: true,
                        text:
                            "Manufacturers in Last Search"
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                }
            }
        }

    );


    typeChartInstance = new Chart(

        typeCanvas.getContext("2d"),

        {
            type: "doughnut",

            data: {
                labels: [],

                datasets: [{
                    data: [],
                    backgroundColor: [
                        "#0284c7",
                        "#f59e0b",
                        "#16a34a",
                        "#dc2626"
                    ]
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    title: {
                        display: true,
                        text:
                            "Branded vs. Generic Split"
                    }
                }
            }
        }

    );

}


async function updateAnalytics() {

    // No charts on this page (e.g. favorites.html) -
    // nothing to update.
    if (!manufacturerChartInstance || !typeChartInstance) {
        return;
    }


    const analyticsSection =
        document.getElementById(
            "analyticsSection"
        );


    try {

        const response =
            await fetch(
                "/api/analytics"
            );


        if (!response.ok) {

            throw new Error(
                "Failed to load analytics"
            );

        }


        const data =
            await response.json();


        // results.csv has no rows yet (fresh start, or a
        // search that returned nothing) - keep the whole
        // section hidden rather than showing empty charts.
        const hasData =
            data.manufacturers.counts.length > 0;


        if (analyticsSection) {

            analyticsSection.style.display =
                hasData ? "block" : "none";

        }


        if (!hasData) {
            return;
        }


        manufacturerChartInstance.data.labels =
            data.manufacturers.labels;

        manufacturerChartInstance.data.datasets[0].data =
            data.manufacturers.counts;

        manufacturerChartInstance.update();


        typeChartInstance.data.labels =
            data.types.labels;

        typeChartInstance.data.datasets[0].data =
            data.types.counts;

        typeChartInstance.update();


    } catch (error) {

        console.error(
            "Analytics error:",
            error
        );


        // On a genuine fetch/parse error, don't leave a
        // stale chart showing - hide the section.
        if (analyticsSection) {

            analyticsSection.style.display =
                "none";

        }

    }

}


// --------------------------------
// Initialize
// --------------------------------

setupFavoriteButtons();
loadFavorites();
initCharts();
updateAnalytics();