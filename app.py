from flask import Flask, render_template, request
import duckdb
import csv

app = Flask(__name__)


# ================================
# File paths
# ================================

MEDICINES = "database/medicines.csv"
FAVOURITES = "database/favourites.csv"


# ================================
# Create HTML card
# ================================

def card(row, favourite=False):

    id, name, manufacturer, medicine_type, ingredient, cost, tablets = row

    type_class = "generic" if medicine_type.lower() == "generic" else "branded"

    heart = "♥" if favourite else "♡"
    favourite_class = "active" if favourite else ""

    per_tablet = cost / tablets if tablets else 0

    aria_label = (
        "Remove from favorites"
        if favourite
        else "Add to favorites"
    )

    return f"""
    <div class="medicine-card" data-id="{id}">

        <div class="medicine-type {type_class}">
            {medicine_type}
        </div>

        <button
            class="favorite-button {favourite_class}"
            data-id="{id}"
            aria-label="{aria_label}">

            <span class="favorite-heart">{heart}</span>

        </button>

        <div class="medicine-name">
            {name}
        </div>

        <div class="medicine-manufacturer">
            Manufacturer:<br>{manufacturer}
        </div>

        <div class="medicine-active-ing">
            Active Ingredient:<br>{ingredient}
        </div>

        <div class="medicine-cost">
            Cost: ₹{cost:.2f}
        </div>

        <div class="medicine-tablets">
            Tablets: {tablets}
        </div>

        <div class="medicine-cost-per-tablet">
            Cost per Tablet: ₹{per_tablet:.2f}
        </div>

    </div>
    """


# ================================
# Pages
# ================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/favorites")
def favorites():
    return render_template("favorites.html")


# ================================
# Search
# ================================

@app.route("/api/medicines", methods=["POST"])
def search():

    data = request.get_json()
    name = data.get("name", "").strip()

    if not name:
        return "<p>Please enter a medicine name.</p>"


    # Find active ingredient

    ingredient = duckdb.sql("""
        SELECT active_ingredient
        FROM read_csv_auto(?)
        WHERE LOWER(name) LIKE LOWER(?)
        LIMIT 1
    """, params=[
        MEDICINES,
        f"%{name}%"
    ]).fetchone()


    if not ingredient:
        return "<p>Medicine not found.</p>"


    # Find all medicines with that ingredient

    results = duckdb.sql("""
        SELECT
            id,
            name,
            manufacturer,
            type,
            active_ingredient,
            cost,
            tablet_count

        FROM read_csv_auto(?)

        WHERE LOWER(active_ingredient) = LOWER(?)

        ORDER BY
            cost / NULLIF(tablet_count, 0)

    """, params=[
        MEDICINES,
        ingredient[0]
    ]).fetchall()


    # IDs already favourited

    with open(FAVOURITES, newline="") as f:

        favourite_ids = {
            row["id"]
            for row in csv.DictReader(f)
        }


    return "".join(
        card(
            row,
            str(row[0]) in favourite_ids
        )
        for row in results
    )


# ================================
# Load favourites
# ================================

@app.route("/api/favorites")
def get_favorites():

    results = duckdb.sql("""
        SELECT
            id,
            name,
            manufacturer,
            type,
            active_ingredient,
            cost,
            tablet_count

        FROM read_csv_auto(?)

    """, params=[FAVOURITES]).fetchall()


    if not results:

        return """
        <p class="no-favorites">
            No favorite medicines yet.
        </p>
        """


    return "".join(
        card(row, True)
        for row in results
    )


# ================================
# Add / remove favourite
# ================================

@app.route("/api/favorite", methods=["POST"])
def update_favorite():

    data = request.get_json()

    medicine_id = str(data["id"])
    favourite = data["favorite"]


    # Read current favourites

    with open(FAVOURITES, newline="") as f:

        favourites = list(
            csv.DictReader(f)
        )


    # Remove this medicine if it exists

    favourites = [
        row
        for row in favourites
        if row["id"] != medicine_id
    ]


    # Add it if it should be favourited

    if favourite:

        medicine = duckdb.sql("""
            SELECT
                id,
                name,
                manufacturer,
                type,
                active_ingredient,
                cost,
                tablet_count

            FROM read_csv_auto(?)

            WHERE id = ?

        """, params=[
            MEDICINES,
            int(medicine_id)
        ]).fetchone()


        if medicine:

            favourites.append(
                dict(zip(
                    [
                        "id",
                        "name",
                        "manufacturer",
                        "type",
                        "active_ingredient",
                        "cost",
                        "tablet_count"
                    ],
                    medicine
                ))
            )


    # Save favourites

    with open(
        FAVOURITES,
        "w",
        newline=""
    ) as f:

        fieldnames = [
            "id",
            "name",
            "manufacturer",
            "type",
            "active_ingredient",
            "cost",
            "tablet_count"
        ]

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(favourites)


    return {
        "success": True,
        "favorite": favourite
    }


# ================================
# Start server
# ================================

if __name__ == "__main__":
    app.run(debug=True)
