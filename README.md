# Inventory & Order Management System

A full-stack inventory and order management system built with **FastAPI** and **SQLAlchemy**, featuring **JWT-based authentication**, **role-based access control**, and a **transactional order workflow**. The system supports public browsing, secure order placement, inventory management, and a foundational **ML-based demand forecasting pipeline**.  
, and admin-controlled order lifecycle operations. A lightweight **Streamlit frontend** demonstrates end-to-end functionality.

This project demonstrates backend engineering, database design, data engineering, and applied machine learning in a single cohesive system.

---

## Key Capabilities

- Secure authentication with JWT (OAuth2)
- Role-based access control (admin / user)
- Public book browsing with pagination, filtering, and sorting
- Atomic order placement with inventory updates
- Deterministic order lifecycle management
- PostgreSQL + Alembic migrations
- AI-powered natural language search (Gemini + LangChain)
- Sales fact table and historical bootstrap dataset
- ETL pipeline for ML training data
- Weekly demand forecasting baseline model

## Features

## Features

### Public
- Browse all books
- Pagination, filtering, and sorting
- AI-powered natural language search

### User
- User registration and login
- View profile details
- Place orders
- View personal order history

### Admin
- Add new books
- Update book details and stock
- Delete books
- View all orders
- Update order status  
  (PLACED → CONFIRMED → SHIPPED → DELIVERED / CANCELLED)

---

## Order Lifecycle & Inventory Rules

- Stock decreases when an order is **PLACED**
- Stock is restored when an order is **CANCELLED**
- A **sales record** is created only when an order is **DELIVERED**
- Delivered and cancelled orders are terminal states

This ensures clean transactional integrity and ML-safe historical data.

---

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- JWT Authentication (OAuth2)

### Frontend
- Streamlit
- Requests

### Machine Learning / Data
- Pandas
- Scikit-learn

### Tools
- Git & GitHub

---


## Project Structure
![Project Stucture](screenshots/project-structure.png)



## Screenshots

### Home Page & Public Book Browsing
![Home Page](screenshots/Home-page.png)

### Filter Books (Domain / Budget)
![Filter Books](screenshots/filter-books.png)

### Create User
![Create User](screenshots/create-user.png)

### User Login
![Login](screenshots/client/client-place-order.png)

### Place Order
![Place Order](screenshots/client/client-place-order.png)

### My Orders
![My Orders](screenshots/client/client-my-orders.png)

### Admin – Add Book
![Admin Add Book](screenshots/server/admin-add-book.png)

### Admin – Update Book Stock
![Admin Update Stock](screenshots/server/admin-book-stock.png)

### Admin – Delete Book
![Admin Delete Book](screenshots/server/admin-delete-book.png)

### Admin – View All Orders
![Admin View All Orders](screenshots/server/admin-view-all-orders.png)


---

## API Endpoints

### Authentication
- POST `/create-user`
- POST `/login`
- GET `/get-details`

### Public Books
- GET `/public/`
- GET `/public/{book_id}`
- GET `/public/search/?query=...`
- GET `/public/domain/{domain}?max_price=`

### Orders
- POST `/orders/`
- GET `/orders/get-my-orders`

### Admin
- POST `/admin/`
- PATCH `/admin/{book_id}`
- DELETE `/admin/{book_id}`
- GET `/admin/get-all-orders`
- PATCH `/admin/orders/{order_id}/status`

---

## Machine Learning Overview

- Kaggle retail dataset used for bootstrapping historical demand
- Data cleaned and loaded into `historical_sales` table
- Real bookstore transactions stored in `sales` table
- Weekly aggregation by domain
- Lag-based features:
  - lag_1, lag_2, lag_4, lag_8
- Global RandomForestRegressor baseline
- Predicts next 7-day demand per domain

This design mirrors real-world forecasting pipelines used in retail systems.

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone <repo-url>
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 2. Install Dependencies and create .env file
```bash
pip install -r requirements.txt
cp .env.example .env
```

---

### 3. Inside .env File
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/BooksManagementDatabase
SECRET_KEY=your_secret_key
GEMINI_API_KEY=your_api_key
```


---

### 4. Run Database Migrations
```bash
alembic upgrade head
```

---

### 5. Start Backend Server
```bash
uvicorn main:app --reload
```

Backend will be available at:  
http://localhost:8000  

Swagger Docs:  
http://localhost:8000/docs  

---

## Frontend Setup (Streamlit)

### 1. Create Virtual Environment

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 3. Start Frontend
```bash
streamlit run app.py
```

Frontend will be available at:  
http://localhost:8501  

---
## How to Use the Application

1. Start the backend server  
2. Start the Streamlit frontend  
3. Browse books publicly  
4. Create an account and log in  
5. Place orders as a user  
6. Manage inventory and orders as admin  
7. (Optional) Use natural language search for books  
8. (Optional) Run historical data loader and train forecasting model
