from fastapi import FastAPI, HTTPException, Query
from enum import Enum
from pydantic import BaseModel
import math

from database import (
    get_product_count,
    get_products_paginated,
    get_product_by_id,
    search_products,
    get_search_count,
    get_stats as get_database_stats
)


class SortOption(str, Enum):
    name = "name"
    price_asc = "price_asc"
    price_desc = "price_desc"


class Book(BaseModel):
    id: int
    name: str
    price: float
    url: str
    availability: str


class BooksResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int
    books: list[Book]


class SearchResponse(BaseModel):
    query: str
    min_price: float | None
    max_price: float | None
    sort: SortOption
    count: int
    books: list[Book]


app = FastAPI(
    title="Book Scraper API",
    description="Books To Scrape REST API",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Book Scraper API is running"
    }


@app.get("/books", response_model=BooksResponse)
def get_books(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100)
):
    offset = (page - 1) * limit

    total = get_product_count()

    rows = get_products_paginated(
        limit,
        offset
    )

    books = [
        {
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "url": row[3],
            "availability": row[4]
        }
        for row in rows
    ]

    pages = math.ceil(total / limit) if total > 0 else 0

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
        "books": books
    }


@app.get("/books/search", response_model=BooksResponse)
def search_books(
        q: str = "",
        min_price: float | None = None,
        max_price: float | None = None,
        sort: SortOption = SortOption.name,
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=100)
):
    if min_price is not None and max_price is not None:
        if min_price > max_price:
            raise HTTPException(
                status_code=400,
                detail="min_price cannot be greater than max_price"
            )

    offset = (page - 1) * limit

    total = get_search_count(
        query_text=q,
        min_price=min_price,
        max_price=max_price
    )

    rows = search_products(
        query_text=q,
        min_price=min_price,
        max_price=max_price,
        sort=sort.value,
        limit=limit,
        offset=offset
    )

    books = [
        {
            "id": row[0],
            "name": row[1],
            "price": row[2],
            "url": row[3],
            "availability": row[4]
        }
        for row in rows
    ]

    pages = math.ceil(total / limit) if total > 0 else 0

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
        "books": books
    }

@app.get("/stats")
def get_stats():
    row = get_database_stats()

    return {
        "total_products": row[0],
        "average_price": round(row[1], 2),
        "cheapest_price": round(row[2], 2),
        "most_expensive_price": round(row[3], 2),
        "total_catalog_value": round(row[4], 2)
    }


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    row = get_product_by_id(book_id)

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return {
        "id": row[0],
        "name": row[1],
        "price": row[2],
        "url": row[3],
        "availability": row[4]
    }
