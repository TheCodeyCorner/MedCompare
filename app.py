from flask import Flask, render_template, request
import duckdb
import csv
import re

app = Flask(__name__)


# =========================================================
# FILE PATHS
# =========================================================

MEDICINES = "database/medicines.csv"
FAVOURITES = "database/favourites.csv"
RESULTS = "database/results.csv"


# =========================================================
# CALCULATE COMPARABLE COST
# =========================================================

def calculate_cost(cost, medicine_type, quantity):

    try:
        cost = float(cost)

        match = re.search(
            r"\d+(?:\.\d+)?",
            str(quantity)
        )

        if not match:
            return None

        quantity_value = float(match.group())

    except (ValueError, AttributeError):
        return None

    if quantity_value <= 0:
        return None

    medicine_type = str(
        medicine_type
    ).strip().lower()


    # -----------------------------------------------------
    # COUNT-BASED
    # -----------------------------------------------------

    if medicine_type in [
        "tablet",
        "capsule",
        "lozenge",
        "sachet",
        "patch",
        "suppository"
    ]:

        return (
            cost / quantity_value,
            medicine_type
        )


    # -----------------------------------------------------
    # WEIGHT-BASED
    # -----------------------------------------------------

    if medicine_type in [
        "cream",
        "gel",
        "granules",
        "ointment",
        "powder"
    ]:

        return (
            (cost / quantity_value) * 100,
            "100 g"
        )


    # -----------------------------------------------------
    # VOLUME-BASED
    # -----------------------------------------------------

    if medicine_type in [
        "drops",
        "injection",
        "lotion",
        "solution",
        "suspension",
        "syrup"
    ]:

        return (
            (cost / quantity_value) * 100,
            "100 ml"
        )


    # -----------------------------------------------------
    # UNIT-BASED
    # -----------------------------------------------------

    if medicine_type in [
        "bottle",
        "inhaler",
        "tube",
        "vial"
    ]:

        return (
            cost / quantity_value,
            medicine_type
        )


    return None


# =========================================================
# MEDICINE CARD
# =========================================================

def card(row, favourite=False):

    (
        medicine_id,
        name,
        manufacturer,
        manufacturer_type,
        ingredient,
        cost,
        medicine_type,
        quantity
    ) = row


    manufacturer_type = str(
        manufacturer_type
    ).strip().lower()

    medicine_type = str(
        medicine_type
    ).strip().lower()


    # -----------------------------------------------------
    # FAVORITE
    # -----------------------------------------------------

    heart = "♥" if favourite else "♡"

    favourite_class = (
        "active"
        if favourite
        else ""
    )


    # -----------------------------------------------------
    # CALCULATED COST
    # -----------------------------------------------------

    calculated = calculate_cost(
        cost,
        medicine_type,
        quantity
    )


    if calculated:

        unit_cost, unit = calculated

        cost_html = f"""
        <div class="medicine {manufacturer_type}">

          <div class="medicine-cost-per-tablet">
            ₹{unit_cost:.2f} /
            <span class="medicine">{unit}</span>
          </div>

          <div class="medicine-tablets">
            pack of {quantity}:
            <span class="medicine-cost">
              ₹{float(cost):.2f}
            </span>
          </div>

        </div>
        """

    else:

        cost_html = f"""
        <div class="medicine {manufacturer_type}">

          <div class="medicine-cost">
            ₹{float(cost):.2f}
          </div>

        </div>
        """


    # =====================================================
    # CARD HTML
    # =====================================================

    return f"""
    <div class="medicine-card">

        <div class="medicine-type {manufacturer_type}">
          {manufacturer_type.capitalize()}
        </div>

        <button
          class="favorite-button {favourite_class}"
          data-id="{medicine_id}"
          aria-label="{
              'Remove from favorites'
              if favourite
              else 'Add to favorites'
          }">

          <span class="favorite-heart">
            {heart}
          </span>

        </button>

        <div class="medicine-name">
          {name}
        </div>

        <div class="medicine-type">
          {medicine_type}
        </div>

        <hr>

        <div class="medicine-manufacturer">
          Manufacturer:
          <br>
          <div class="manufacturer">
            {manufacturer}
          </div>
        </div>

        <div class="medicine-active-ing">
          Active Ingredient:
          <br>
          <div class="active-ingredient">
            {ingredient}
          </div>
        </div>

        {cost_html}

    </div>
    """


# =========================================================
# SAVE SEARCH RESULTS
# =========================================================

def save_results(results):

    fields = [
        "id",
        "name",
        "manufacturer",
        "manufacturer_type",
        "active_ingredient",
        "cost",
        "medicine_type",
        "quantity"
    ]


    with open(
        RESULTS,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow(fields)

        writer.writerows(results)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# FAVORITES PAGE
# =========================================================

@app.route("/favorites")
def favorites():

    return render_template(
        "favorites.html"
    )


# =========================================================
# SEARCH MEDICINES
# =========================================================

@app.route(
    "/api/medicines",
    methods=["POST"]
)
def search():

    data = request.get_json()

    name = data.get(
        "name",
        ""
    ).strip()


    if not name:

        return """
        <p>Please enter a medicine name.</p>
        """


    # -----------------------------------------------------
    # Find active ingredient
    # -----------------------------------------------------

    ingredient = duckdb.sql("""
        SELECT active_ingredient

        FROM read_csv_auto(?)

        WHERE LOWER(name)
        LIKE LOWER(?)

        LIMIT 1

    """, params=[

        MEDICINES,
        f"%{name}%"

    ]).fetchone()


    if not ingredient:

        save_results([])

        return """
        <p>Medicine not found.</p>
        """


    # -----------------------------------------------------
    # Find all medicines with same ingredient
    # -----------------------------------------------------

    results = duckdb.sql("""
        SELECT

            id,
            name,
            manufacturer,
            manufacturer_type,
            active_ingredient,
            cost,
            medicine_type,
            quantity

        FROM read_csv_auto(?)

        WHERE LOWER(active_ingredient)
        = LOWER(?)

    """, params=[

        MEDICINES,
        ingredient[0]

    ]).fetchall()


    # -----------------------------------------------------
    # Sort by calculated comparable cost
    # -----------------------------------------------------

    def sort_cost(row):
        calculated = calculate_cost(
            row[5],  # cost
            row[6],  # medicine_type
            row[7]   # quantity
        )

        if calculated:
            return calculated[0]

        return float("inf")


    results = sorted(
        results,
        key=sort_cost
    )


    # -----------------------------------------------------
    # Save results.csv
    # -----------------------------------------------------

    save_results(results)


    # -----------------------------------------------------
    # Get favourite IDs
    # -----------------------------------------------------

    favourite_ids = set()


    try:

        with open(
            FAVOURITES,
            newline="",
            encoding="utf-8"
        ) as file:

            favourite_ids = {
                row["id"]
                for row in csv.DictReader(file)
            }

    except FileNotFoundError:

        pass


    # -----------------------------------------------------
    # Generate cards
    # -----------------------------------------------------

    return "".join(

        card(
            row,
            str(row[0]) in favourite_ids
        )

        for row in results
    )


# =========================================================
# LOAD FAVORITES
# =========================================================

@app.route("/api/favorites")
def get_favorites():

    try:

        results = duckdb.sql("""
            SELECT

                id,
                name,
                manufacturer,
                manufacturer_type,
                active_ingredient,
                cost,
                medicine_type,
                quantity

            FROM read_csv_auto(?)

        """, params=[

            FAVOURITES

        ]).fetchall()


    except Exception:

        results = []


    if not results:

        return """
        <p class="no-favorites">
            No favorite medicines yet.
        </p>
        """


    return "".join(

        card(
            row,
            True
        )

        for row in results
    )


# =========================================================
# ADD / REMOVE FAVORITE
# =========================================================

@app.route(
    "/api/favorite",
    methods=["POST"]
)
def update_favorite():

    data = request.get_json()

    medicine_id = str(
        data["id"]
    )

    favourite = data["favorite"]


    # -----------------------------------------------------
    # Read existing favorites
    # -----------------------------------------------------

    try:

        with open(
            FAVOURITES,
            newline="",
            encoding="utf-8"
        ) as file:

            favourites = list(
                csv.DictReader(file)
            )

    except FileNotFoundError:

        favourites = []


    # -----------------------------------------------------
    # Remove existing copy
    # -----------------------------------------------------

    favourites = [

        row

        for row in favourites

        if row["id"] != medicine_id

    ]


    # -----------------------------------------------------
    # Add medicine
    # -----------------------------------------------------

    if favourite:

        medicine = duckdb.sql("""
            SELECT

                id,
                name,
                manufacturer,
                manufacturer_type,
                active_ingredient,
                cost,
                medicine_type,
                quantity

            FROM read_csv_auto(?)

            WHERE id = ?

        """, params=[

            MEDICINES,
            int(medicine_id)

        ]).fetchone()


        if medicine:

            fields = [

                "id",
                "name",
                "manufacturer",
                "manufacturer_type",
                "active_ingredient",
                "cost",
                "medicine_type",
                "quantity"

            ]


            favourites.append(
                dict(
                    zip(
                        fields,
                        medicine
                    )
                )
            )


    # -----------------------------------------------------
    # Rewrite favorites.csv
    # -----------------------------------------------------

    fields = [

        "id",
        "name",
        "manufacturer",
        "manufacturer_type",
        "active_ingredient",
        "cost",
        "medicine_type",
        "quantity"

    ]


    with open(
        FAVOURITES,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        writer.writerows(
            favourites
        )


    return {
        "success": True,
        "favorite": favourite
    }


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )