Monish Jewelry Product Catalog API

A simple REST API for managing a jewelry product catalog. The API supports product CRUD operations, search and filtering, stock management, pagination, sorting, and basic admin authentication.

Live Demo

https://monish-jewelry-internship-task.onrender.com

Features

The API provides complete CRUD operations for products. Each product contains a name, price, category, images, and stock quantity.

Products can be searched by name or category and filtered by category, price range, and stock availability.

The API also supports pagination and sorting by price, name, or stock.

Admin-only operations such as creating, updating, and deleting products are protected using Bearer token authentication.

Input validation is included for required fields, negative prices, and negative stock values.

The project also includes automated tests using pytest and a Postman collection for API testing.

Tech Stack

Python, Flask, Flask-SQLAlchemy, SQLite, Flask-CORS, python-dotenv, Gunicorn, Render, Postman, and pytest.

Design Decisions

SQLite

SQLite was selected because the project is a small product catalog API and does not require a separate database server for local development. The database can be migrated to PostgreSQL or another production database in the future.

SQLAlchemy

SQLAlchemy provides a clean database abstraction and makes it easier to work with the Product model and database queries.

Bearer Token Authentication

Admin operations require an Authorization header using the Bearer token format. This provides a simple authentication mechanism suitable for the scope of this internship task.

Pagination

Pagination is supported using the page and limit query parameters so that the API does not need to return every product at once.

Stock Management

Stock is stored as an integer. The API automatically returns an in_stock field based on whether the stock quantity is greater than zero.

Project Structure

monish-jewelry-internship-task/
│
├── app.py
├── models.py
├── test_app.py
├── requirements.txt
├── postman_collection.json
├── README.md
├── .gitignore

The .env file is used locally for the admin secret and is excluded from Git using .gitignore.

Running Locally

Clone the repository:

git clone https://github.com/monishrv/monish-jewelry-internship-task.git
cd monish-jewelry-internship-task

Create a virtual environment:

python -m venv venv

Activate the virtual environment on Windows:

venv\Scripts\activate

Install the dependencies:

pip install -r requirements.txt

Create a .env file in the project root:

ADMIN_KEY=your-secret-key

Start the application:

python app.py

The API will be available at:

http://127.0.0.1:5000

The database is created automatically when the application starts.

API Endpoints

Health Check

GET /

Returns the current API status.

Create Product

POST /products

Requires admin authentication.

Example request body:

{
  "name": "Gold Ring",
  "price": 2500,
  "category": "Rings",
  "images": [
    "https://example.com/ring.jpg"
  ],
  "stock": 10
}

Get All Products

GET /products

Optional pagination parameters:

?page=1&limit=10

Get Product by ID

GET /products/<id>

Returns a single product.

Update Product

PUT /products/<id>

Requires admin authentication.

Only the fields that need to be changed have to be included in the request.

Example:

{
  "price": 2800,
  "stock": 8
}

Delete Product

DELETE /products/<id>

Requires admin authentication.

Search and Filtering

The search endpoint is:

GET /search

Search by product name or category:

/search?q=ring

Filter by category:

/search?category=Rings

Filter by minimum price:

/search?min_price=1000

Filter by maximum price:

/search?max_price=5000

Filter by price range:

/search?min_price=1000&max_price=5000

Filter by stock availability:

/search?in_stock=true

or:

/search?in_stock=false

Search, filtering, pagination, and sorting can also be combined.

Sorting

Products can be sorted by price, name, or stock.

Sort by price:

/search?sort_by=price

Descending order:

/search?sort_by=price&order=desc

Other supported sorting fields are:

sort_by=name
sort_by=stock

Authentication

Admin-only endpoints require a Bearer token in the Authorization header.

Example:

Authorization: Bearer your-secret-key

The protected endpoints are:

POST /products
PUT /products/<id>
DELETE /products/<id>

Requests without valid authentication return:

{
  "error": "Unauthorized"
}

Creating a Product

A product requires:

name
price
category

The following fields are optional:

images
stock

If stock is not provided, it defaults to 0.

Stock Management

The API automatically determines whether a product is in stock.

For example, when:

"stock": 5

the response contains:

"in_stock": true

When:

"stock": 0

the response contains:

"in_stock": false

This allows out-of-stock products to be identified and filtered easily.

Validation and Error Handling

The API validates required product fields and prevents negative prices and negative stock values.

For example, a negative price returns:

{
  "error": "Price cannot be negative"
}

A negative stock value returns:

{
  "error": "Stock cannot be negative"
}

Requests for products that do not exist return HTTP 404.

Unauthorized admin requests return HTTP 401.

Invalid or missing request data returns HTTP 400.

Testing

The project includes automated tests using pytest.

Run the test suite with:

pytest test_app.py -v

The test suite covers the health endpoint, product creation, authentication, validation, product lookup, search, and deletion.

Postman Collection

A Postman collection is included in the repository:

postman_collection.json

It can be imported into Postman to test the API endpoints.

For local testing, the collection uses:

base_url = http://127.0.0.1:5000

The admin authentication token should be configured using the Postman environment rather than hardcoded into individual requests.

Deployment

The API is deployed on Render using Gunicorn.

Live API:

https://monish-jewelry-internship-task.onrender.com

The application uses environment variables for the admin secret in the deployed environment.

Future Improvements

The project can be extended with PostgreSQL for a production database, stronger authentication such as JWT, image upload and storage, product categories as separate database entities, rate limiting, API documentation using OpenAPI or Swagger, and a frontend product catalog.

Author

Monish R V

GitHub:

https://github.com/monishrv/monish-jewelry-internship-task