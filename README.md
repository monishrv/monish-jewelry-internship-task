# Monish Jewelry Internship Task - Product Catalog API

A REST API for managing a jewelry product catalog with CRUD operations, search and filtering functionality, stock management, and admin authentication.

## Tech Stack

* **Backend:** Python, Flask
* **Database:** SQLite
* **ORM:** SQLAlchemy
* **API:** REST API with JSON
* **Authentication:** Bearer Token

## Features

* Create, read, update, and delete products
* Search products by name or category
* Filter products by category
* Filter products by price range
* Filter products by stock availability
* Automatic `in_stock` status
* Admin authentication for product modifications
* Input validation
* Proper HTTP status codes and error handling
* Case-insensitive partial search
* Pagination for product listing and search results

## Design Decisions

* **SQLite over PostgreSQL:** Chosen for zero-config setup and quick deployment, since this project doesn't need concurrent write-heavy traffic. Easy to swap to PostgreSQL later if scale demands it.
* **Simple Bearer token over JWT:** Kept authentication lightweight since this is a single-admin system with no user roles or session expiry needs. A full JWT setup would add complexity without real benefit here.
* **Images stored as comma-separated text:** SQLite doesn't support native array columns, so image URLs are joined into a single text field and split back into a list in the API response, avoiding the need for a separate images table.
* **Pagination on list/search endpoints:** Added to keep response sizes manageable and reflect real-world API design, where returning an entire table at once doesn't scale.
* **Case-insensitive search with partial matching:** Used case-insensitive pattern matching so search feels intuitive (e.g. `"ring"` matches `"Gold Ring"`) rather than requiring exact matches.

## Project Structure

```text
monish-jewelry-internship-task/

│
├── app.py
├── models.py
├── requirements.txt
├── README.md
└── .gitignore
```

> `catalog.db` is created automatically when the application runs and is ignored by Git.

## Setup and Run Locally

### 1. Clone the repository

```bash
git clone <your-repo-url>

cd monish-jewelry-internship-task
```

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

**Mac/Linux:**

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

The API will be available at:

```text
http://127.0.0.1:5000/
```

## API Endpoints

### Public Endpoints

These endpoints do not require authentication.

| Method | Endpoint         | Description                |
| ------ | ---------------- | -------------------------- |
| GET    | `/`              | API health check           |
| GET    | `/products`      | Get all products           |
| GET    | `/products/<id>` | Get a product by ID        |
| GET    | `/search`        | Search and filter products |

### Admin Endpoints

These endpoints require authentication.

| Method | Endpoint         | Description                |
| ------ | ---------------- | -------------------------- |
| POST   | `/products`      | Create a new product       |
| PUT    | `/products/<id>` | Update an existing product |
| DELETE | `/products/<id>` | Delete a product           |

## Search and Filtering

The `/search` endpoint supports the following query parameters:

| Parameter   | Description                             |
| ----------- | --------------------------------------- |
| `q`         | Search by product name or category      |
| `category`  | Filter by category                      |
| `min_price` | Minimum product price                   |
| `max_price` | Maximum product price                   |
| `in_stock`  | Return only products currently in stock |
| `page`      | Page number                             |
| `per_page`  | Number of products per page             |

### Search by Product Name

```text
GET /search?q=ring
```

### Filter by Category

```text
GET /search?category=Rings
```

### Filter by Maximum Price

```text
GET /search?max_price=50
```

### Filter by Minimum Price

```text
GET /search?min_price=20
```

### Show Only In-Stock Products

```text
GET /search?in_stock=true
```

### Pagination

```text
GET /products?page=1&per_page=10
```

or:

```text
GET /search?q=ring&page=2&per_page=5
```

### Combine Multiple Filters

```text
GET /search?q=ring&category=Rings&max_price=100&in_stock=true
```

Search is **case-insensitive** and supports **partial matches**.

## Authentication

Product creation, updating, and deletion require administrator authentication.

The API currently uses a Bearer Token.

Example:

```text
Authorization: Bearer admin-secret-key-12345
```

The authentication header must be included with POST, PUT, and DELETE requests.

GET requests are publicly accessible.

## Create a Product

### Request

```text
POST /products
```

### Headers

```text
Content-Type: application/json
Authorization: Bearer admin-secret-key-12345
```

### Request Body

```json
{
    "name": "Gold Ring",
    "price": 45.99,
    "category": "Rings",
    "images": [
        "img1.jpg",
        "img2.jpg"
    ],
    "stock": 10
}
```

### Example Response

```json
{
    "id": 1,
    "name": "Gold Ring",
    "price": 45.99,
    "category": "Rings",
    "images": [
        "img1.jpg",
        "img2.jpg"
    ],
    "stock": 10,
    "in_stock": true
}
```

## Get All Products

```text
GET /products
```

Example response:

```json
[
    {
        "id": 1,
        "name": "Gold Ring",
        "price": 45.99,
        "category": "Rings",
        "images": [
            "img1.jpg"
        ],
        "stock": 10,
        "in_stock": true
    }
]
```

With pagination, the response may also include pagination metadata depending on the implementation.

## Get Product by ID

```text
GET /products/1
```

Returns the product with the specified ID.

If the product does not exist, the API returns:

```json
{
    "error": "Product not found"
}
```

## Update a Product

### Request

```text
PUT /products/<id>
```

### Headers

```text
Content-Type: application/json
Authorization: Bearer admin-secret-key-12345
```

### Example Request Body

```json
{
    "price": 50.99,
    "stock": 5
}
```

Only the fields that need to be updated have to be provided.

## Delete a Product

### Request

```text
DELETE /products/<id>
```

### Headers

```text
Authorization: Bearer admin-secret-key-12345
```

Example:

```text
DELETE /products/1
```

## Product Data Format

Each product contains the following fields:

| Field      | Description                         |
| ---------- | ----------------------------------- |
| `id`       | Unique product identifier           |
| `name`     | Product name                        |
| `price`    | Product price                       |
| `category` | Product category                    |
| `images`   | List of product image URLs/names    |
| `stock`    | Available quantity                  |
| `in_stock` | Automatically determined from stock |

The `in_stock` field is automatically calculated based on the stock quantity.

For example:

```text
stock > 0  →  in_stock: true

stock = 0  →  in_stock: false
```

## Validation and Error Handling

The API handles common invalid requests and edge cases, including:

* Missing required fields
* Invalid product data
* Invalid price values
* Invalid price ranges
* Invalid pagination parameters
* Product not found
* Unauthorized requests
* Empty search results
* Out-of-stock products
* Case-insensitive searches
* Partial search matches

### HTTP Status Codes

| Status Code | Meaning                      |
| ----------- | ---------------------------- |
| `200`       | Successful request           |
| `201`       | Product successfully created |
| `400`       | Invalid request              |
| `401`       | Unauthorized                 |
| `404`       | Product not found            |

## Example API Usage

### Get All Products

```text
GET http://127.0.0.1:5000/products
```

### Search for Rings

```text
GET http://127.0.0.1:5000/search?q=ring
```

### Find Rings Under $50

```text
GET http://127.0.0.1:5000/search?q=ring&max_price=50
```

### Find In-Stock Products

```text
GET http://127.0.0.1:5000/search?in_stock=true
```

### Paginated Product List

```text
GET http://127.0.0.1:5000/products?page=1&per_page=10
```

### Create a Product

```text
POST http://127.0.0.1:5000/products
```

Headers:

```text
Content-Type: application/json
Authorization: Bearer admin-secret-key-12345
```

Body:

```json
{
    "name": "Gold Ring",
    "price": 45.99,
    "category": "Rings",
    "images": [
        "img1.jpg",
        "img2.jpg"
    ],
    "stock": 10
}
```

## Future Improvements

Possible future improvements include:

* JWT-based authentication
* Environment-based secret configuration
* User registration and login
* Product sorting
* Image upload support
* PostgreSQL database
* Swagger/OpenAPI documentation
* Frontend product catalog
* Admin dashboard
* Cloud deployment
* Docker containerization
* Automated testing and CI/CD

## Author

**Monish**

B.Tech Computer Science and Engineering

## License

This project was created as part of an internship task.
