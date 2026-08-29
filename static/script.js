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
// Initialize
// --------------------------------

setupFavoriteButtons();
loadFavorites();