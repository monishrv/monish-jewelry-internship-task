import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

ADMIN_HEADER = {"Authorization": "Bearer admin-secret-key-12345"}

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200

def test_create_product(client):
    response = client.post('/products', json={
        "name": "Test Ring", "price": 25, "category": "Rings", "stock": 5
    }, headers=ADMIN_HEADER)
    assert response.status_code == 201
    assert response.get_json()['name'] == "Test Ring"

def test_create_product_without_auth_fails(client):
    response = client.post('/products', json={
        "name": "Test Ring", "price": 25, "category": "Rings", "stock": 5
    })
    assert response.status_code == 401

def test_create_product_negative_price_fails(client):
    response = client.post('/products', json={
        "name": "Bad Ring", "price": -10, "category": "Rings", "stock": 5
    }, headers=ADMIN_HEADER)
    assert response.status_code == 400

def test_get_nonexistent_product_returns_404(client):
    response = client.get('/products/999')
    assert response.status_code == 404

def test_search_finds_product(client):
    client.post('/products', json={
        "name": "Gold Necklace", "price": 50, "category": "Necklaces", "stock": 3
    }, headers=ADMIN_HEADER)
    response = client.get('/search?q=Gold')
    data = response.get_json()
    assert data['total'] == 1
    assert data['products'][0]['name'] == "Gold Necklace"

def test_delete_product(client):
    create_response = client.post('/products', json={
        "name": "To Delete", "price": 10, "category": "Test", "stock": 1
    }, headers=ADMIN_HEADER)
    product_id = create_response.get_json()['id']

    delete_response = client.delete(f'/products/{product_id}', headers=ADMIN_HEADER)
    assert delete_response.status_code == 200

    get_response = client.get(f'/products/{product_id}')
    assert get_response.status_code == 404