# MedCompare

## Medicine Price Comparison Dashboard

MedCompare is a medicine price comparison web application designed to help users compare medicines based on their active ingredients, manufacturers, medicine type, quantity, and cost.

The application allows users to search for a medicine and view other medicines containing the same active ingredient. This makes it easier to compare different brands and identify potentially lower-cost alternatives.

Users can also add medicines to their favourites and manage their saved medicines through a dedicated Favorites page.

---

## Features

### Medicine Search

Users can enter a medicine name into the search bar. MedCompare identifies the active ingredient associated with the searched medicine and displays medicines containing the same active ingredient.

### Price Comparison

Search results display:

* Medicine name
* Manufacturer
* Manufacturer type
* Active ingredient
* Cost
* Medicine type
* Quantity
* Cost per unit

This allows users to compare medicines based on both their total price and quantity.

### Generic and Branded Medicines

Medicines can be classified according to their manufacturer type, allowing users to distinguish between different categories of medicines.

The application uses the following field:

```text
manufacturer_type
```

Example values include:

```text
Branded
Generic
```

### Favourites

Users can add medicines to their favourites using the heart button displayed on medicine cards.

The Favorites page allows users to:

* View saved medicines
* Remove medicines from favourites
* Keep favourite medicines available across searches

### Cost Per Unit

MedCompare calculates the comparable cost of a medicine using:

```text
cost per unit = cost / quantity
```

This provides a more useful comparison when medicines are sold in different quantities.

---

## Technology Stack

| Technology | Purpose                             |
| ---------- | ----------------------------------- |
| Python     | Backend programming                 |
| Flask      | Web framework                       |
| DuckDB     | Data querying and analysis          |
| HTML       | Web page structure                  |
| CSS        | Styling and responsive design       |
| JavaScript | Search and favourite interactions   |
| CSV        | Medicine and favourite data storage |

---

## Project Structure

```text
MedCompare/
│
├── app.py
├── requirements.txt
├── README.md
│
├── database/
│   ├── medicines.csv
│   └── favourites.csv
│
├── templates/
│   ├── index.html
│   └── favorites.html
│
└── static/
    ├── styles1.css
    ├── script.js
    │
    └── assets/
        ├── logo.png
        ├── logo_textless.png
        └── hero-video.mp4
```

---

## Database Structure

MedCompare uses CSV files as its lightweight data storage layer.

All medicine-related tables/files use the same column structure:

| Column              | Description                                          |
| ------------------- | ---------------------------------------------------- |
| `id`                | Unique medicine identifier                           |
| `name`              | Name of the medicine                                 |
| `manufacturer`      | Company/manufacturer producing the medicine          |
| `manufacturer_type` | Type of manufacturer, such as Branded or Generic     |
| `active_ingredient` | Active ingredient(s) contained in the medicine       |
| `cost`              | Cost of the medicine                                 |
| `medicine_type`     | Form of the medicine, such as tablet or syrup        |
| `quantity`          | Number of units or quantity contained in the package |

### Standard Schema

```text
id,name,manufacturer,manufacturer_type,active_ingredient,cost,medicine_type,quantity
```

### Example Records

```csv
id,name,manufacturer,manufacturer_type,active_ingredient,cost,medicine_type,quantity
122898,Lactomide Tablet,S V Biovac Pharmaceuticals Pvt Ltd,Branded,"Furosemide (20mg), Spironolactone (50mg)",10.07,tablet,10
180594,Paradana 250mg Tablet,Dana Pharmaceuticals Pvt Ltd,Branded,Paracetamol (250mg),8.3,tablet,10
136060,METPRIDE 2 MG/500 MG TABLET,Alkem Laboratories Ltd,Branded,"Glimepiride (2mg), Metformin (500mg)",8.12,tablet,10
216843,Thyronex 25 Tablet,Zeelab Pharmacy Pvt Ltd,Branded,Thyroxine (25mcg),25.0,tablet,100
3561,Apcil Tablet,Juggat Pharma,Branded,"Amoxycillin (500mg), Clavulanic Acid (125mg)",6.98,tablet,10
38315,Cyclo P 20mg/500mg Tablet,Laborate Pharmaceuticals India Ltd,Branded,"Dicyclomine (20mg), Paracetamol (500mg)",3.75,tablet,10
202703,Spasmover Tablet,Cachet Pharmaceuticals Pvt Ltd,Branded,"Dicyclomine (10mg), Mefenamic Acid (250mg)",5.0,tablet,10
174369,Pilzine M 5mg/10mg Tablet,Psychotropics India Ltd,Branded,"Levocetirizine (5mg), Montelukast (10mg)",7.7,tablet,10
46149,Cetariv A Syrup,East African (India) Overseas,Branded,"Cetirizine (5mg/5ml), Ambroxol (30mg/5ml)",39.0,syrup,100
```

---

## Favourites Data

The `favourites.csv` file follows the same schema as the main medicine dataset:

```text
id,name,manufacturer,manufacturer_type,active_ingredient,cost,medicine_type,quantity
```

This keeps the data structure consistent between the main medicine database and saved medicines.

When a user favourites a medicine, the complete medicine record is stored in the favourites dataset.

When a user removes a favourite, the corresponding record is removed from `favourites.csv`.

---

## Application Workflow

```text
User enters medicine name
          │
          ▼
   Flask receives request
          │
          ▼
   DuckDB searches medicines.csv
          │
          ▼
 Identify active ingredient
          │
          ▼
Find medicines with same ingredient
          │
          ▼
 Sort by cost per unit
          │
          ▼
Generate medicine cards
          │
          ▼
 Display results in browser
```

---

## Favourite Workflow

```text
User clicks heart
       │
       ▼
JavaScript detects medicine ID
       │
       ▼
POST request to /api/favorite
       │
       ▼
Flask receives favourite state
       │
       ├───────────────┐
       │               │
       ▼               ▼
 Favourite         Unfavourite
       │               │
       ▼               ▼
Add record         Remove record
       │               │
       └───────┬───────┘
               ▼
       Update favourites.csv
               │
               ▼
        Update interface
```

---

## Flask Routes

| Route            | Method | Purpose                           |
| ---------------- | ------ | --------------------------------- |
| `/`              | GET    | Displays the main MedCompare page |
| `/favorites`     | GET    | Displays the Favorites page       |
| `/api/medicines` | POST   | Searches for medicines            |
| `/api/favorites` | GET    | Retrieves saved favourites        |
| `/api/favorite`  | POST   | Adds or removes a favourite       |

---

## API Overview

### Search Medicines

```text
POST /api/medicines
```

Request:

```json
{
    "name": "Paracetamol"
}
```

The server searches for the medicine, determines its active ingredient, and returns matching medicine cards.

---

### Get Favourites

```text
GET /api/favorites
```

Returns the medicines currently stored in `favourites.csv`.

---

### Update Favourite

```text
POST /api/favorite
```

Request:

```json
{
    "id": "12345",
    "favorite": true
}
```

To remove a medicine:

```json
{
    "id": "12345",
    "favorite": false
}
```

---

## Frontend

The frontend consists of two primary pages:

### Home Page

The home page contains:

* Fixed navigation bar
* MedCompare branding
* Hero section
* Medicine search form
* Medicine comparison cards
* Footer
* Favorites navigation

### Favorites Page

The Favorites page contains:

* Navigation bar
* Saved medicine cards
* Favourite removal buttons
* Empty favourites message
* Footer

---

## Static Assets

The project uses the following visual assets:

| Asset               | Purpose                                      |
| ------------------- | -------------------------------------------- |
| `logo.png`          | Main MedCompare logo containing the branding |
| `logo_textless.png` | Logo symbol without text                     |
| `hero-video.mp4`    | Background video used in the hero section    |

`logo_textless.png` can be used where only the MedCompare symbol is required, such as compact/mobile layouts or visual elements where the text-based logo would be redundant.

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd MedCompare
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

The required Python packages are listed in:

```text
requirements.txt
```

Install them with:

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

The Flask development server will start locally.

Open the address displayed by Flask in a web browser.

---

## Requirements

The project's Python dependencies are maintained in:

```text
requirements.txt
```

The file should contain the packages required by the Flask application, including Flask and DuckDB.

Example:

```text
Flask
duckdb
```

Additional packages should be added to `requirements.txt` whenever they are introduced as project dependencies.

---

## Data Processing

DuckDB is used to query the CSV medicine dataset without requiring a traditional database server.

For example, the application can query the CSV file directly to find a medicine:

```sql
SELECT active_ingredient
FROM read_csv_auto(?)
WHERE LOWER(name) LIKE LOWER(?)
LIMIT 1
```

After identifying the active ingredient, the application searches for all medicines containing the same ingredient.

Results can then be ordered according to their comparable cost:

```sql
ORDER BY cost / NULLIF(quantity, 0)
```

This prevents division-by-zero errors when calculating the cost per unit.

---

## Design Goals

The project focuses on:

1. **Simple medicine comparison**
2. **Clear price information**
3. **Active-ingredient-based searching**
4. **Lightweight data storage**
5. **Responsive web design**
6. **Persistent favourites**
7. **Comparable pricing based on quantity**

---

## Future Improvements

Possible future improvements include:

* Medicine category filtering
* Manufacturer filtering
* Generic-versus-branded price analysis
* Regional medicine pricing
* Price history
* Medicine availability information
* Advanced analytics dashboards
* Interactive price comparison charts
* Medicine recommendations based on active ingredients
* Cloud-hosted database storage
* User accounts and personalized favourites

---

## Disclaimer

MedCompare is an educational software project intended for medicine price comparison and data analysis.

The application does not provide medical advice, diagnosis, prescriptions, or recommendations regarding which medicine a person should take. Users should consult a qualified healthcare professional before making medical decisions.
