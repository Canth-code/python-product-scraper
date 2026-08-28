from fastapi.testclient import TestClient

from api import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Book Scraper API is running"


def test_get_books():
    response = client.get("/books")

    assert response.status_code == 200

    data = response.json()

    assert "page" in data
    assert "limit" in data
    assert "total" in data
    assert "pages" in data
    assert "books" in data

    assert data["total"] == 1000
    assert len(data["books"]) <= data["limit"]


def test_pagination():
    response = client.get(
        "/books?page=2&limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["limit"] == 10
    assert len(data["books"]) == 10


def test_search():
    response = client.get(
        "/books/search?q=sapiens"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] >= 1

    for book in data["books"]:
        assert "sapiens" in book["name"].lower()


def test_price_filter():
    response = client.get(
        "/books/search?min_price=20&max_price=30"
    )

    assert response.status_code == 200

    data = response.json()

    for book in data["books"]:
        assert 20 <= book["price"] <= 30


def test_price_sort_ascending():
    response = client.get(
        "/books/search?sort=price_asc&limit=20"
    )

    assert response.status_code == 200

    data = response.json()

    prices = [
        book["price"]
        for book in data["books"]
    ]

    assert prices == sorted(prices)


def test_price_sort_descending():
    response = client.get(
        "/books/search?sort=price_desc&limit=20"
    )

    assert response.status_code == 200

    data = response.json()

    prices = [
        book["price"]
        for book in data["books"]
    ]

    assert prices == sorted(
        prices,
        reverse=True
    )


def test_stats():
    response = client.get("/stats")

    assert response.status_code == 200

    data = response.json()

    assert data["total_products"] == 1000
    assert data["average_price"] == 35.07
    assert data["cheapest_price"] == 10.00
    assert data["most_expensive_price"] == 59.99


def test_get_existing_book():
    response = client.get("/books/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert "name" in data
    assert "price" in data
    assert "url" in data
    assert "availability" in data


def test_book_not_found():
    response = client.get("/books/9999")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Book not found"


def test_invalid_price_range():
    response = client.get(
        "/books/search?min_price=50&max_price=20"
    )

    assert response.status_code == 400


def test_invalid_page():
    response = client.get(
        "/books?page=0"
    )

    assert response.status_code == 422


def test_invalid_limit():
    response = client.get(
        "/books?limit=101"
    )

    assert response.status_code == 422