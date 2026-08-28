\# 📚 Book Scraper API



A production-style Python web scraping and REST API project built with

Requests, BeautifulSoup, SQLite, Pandas, FastAPI and Pytest.



The project scrapes book data from Books to Scrape, stores the data in

SQLite, exports it into multiple formats and exposes the dataset through

a RESTful API.



\## 🚀 Features



\- Web scraping with Requests + BeautifulSoup

\- Concurrent scraping with ThreadPoolExecutor

\- Retry mechanism for failed HTTP requests

\- Request timeout handling

\- Structured logging

\- 50 catalogue pages scraped concurrently

\- 1000 books collected

\- SQLite database

\- Pandas DataFrame processing

\- CSV export

\- JSON export

\- Excel export

\- FastAPI REST API

\- Pagination

\- Book search

\- Price filtering

\- Price sorting

\- Book lookup by ID

\- Statistics endpoint

\- Pydantic response validation

\- Automated API tests with Pytest



\## 🏗️ Architecture



`text

Books to Scrape

&#x20;      │

&#x20;      ▼

&#x20;   scraper.py

&#x20;      │

&#x20;      ▼

&#x20;    Pandas

&#x20;      │

&#x20;      ▼

&#x20;   SQLite

&#x20;  books.db

&#x20;      │

&#x20;      ▼

&#x20;  database.py

&#x20;      │

&#x20;      ▼

&#x20;    FastAPI

&#x20;     api.py

&#x20;      │

&#x20;      ├── GET /books

&#x20;      ├── GET /books/search

&#x20;      ├── GET /books/{id}

&#x20;      └── GET /stats

&#x20;      │

&#x20;      ▼

&#x20;   REST API

&#x20;      │

&#x20;      ▼

&#x20;   Pytest

