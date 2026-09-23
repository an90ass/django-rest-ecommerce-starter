# Enterprise Django REST E-Commerce Starter Template

A production-ready, enterprise-grade Django REST Framework (DRF) E-Commerce API Starter built with clean architecture, strict role-based access control (RBAC), atomic transactional processing, rate limiting, and OpenAPI 3.0 documentation.

---

## System Architecture

```mermaid
graph TD
    Client[Web / Mobile Clients] -->|HTTPS Requests| Throttle[Rate Limiting & Throttling]
    Throttle -->|Bearer JWT Token| JWT[SimpleJWT Authentication]
    JWT -->|RBAC Roles| Permissions[Permissions & Security Layer]
    Permissions --> Router[DRF Router & API Views]
    
    subgraph Core Modules
        Router --> AuthModule[Auth & User Management]
        Router --> CatalogModule[Product Catalog & Reviews]
        Router --> CartModule[Cart & Wishlist Engine]
        Router --> OrderModule[Atomic Checkout & Orders]
    end
    
    OrderModule -->|@transaction.atomic| Checkout[Checkout Service]
    Checkout -->|Stock Check & Deduction| Stock[Product Inventory]
    Checkout -->|Payment Gateway Abstraction| Payment[Payment Service]
    
    AuthModule --> DB[(SQLite / PostgreSQL)]
    CatalogModule --> DB
    CartModule --> DB
    OrderModule --> DB
```

---

## Key Enterprise Features

- **Custom User & JWT Authentication**:
  - `CustomUser` model using Email as primary identifier.
  - Role-Based Access Control (`ADMIN`, `SELLER`, `CUSTOMER`).
  - JWT Tokens with custom claims (`role`, `full_name`, `email`) and automatic refresh rotation.
- **Advanced Product Catalog & Review Engine**:
  - Hierarchical (Parent-Child) Category Tree.
  - Product gallery with multi-file upload endpoint (`/upload_images/`).
  - Automatic product rating & review count recalculation.
- **Shopping Cart & Wishlist**:
  - Session-based guest carts & authenticated user carts.
  - Subtotal, estimated tax (5%), and grand total calculations.
  - Stock validation upon adding or updating cart quantities.
- **Atomic Checkout Engine & Order Lifecycle**:
  - Transactional order creation (`@transaction.atomic`): Stock check -> Order creation -> Inventory deduction -> Cart clearance.
  - Order cancellation with automatic inventory restoration & refund processing.
  - Payment Abstraction Layer (Stripe, PayPal, Cash on Delivery support).
- **Security & Rate Limiting**:
  - DRF Throttling (`AnonRateThrottle`, `UserRateThrottle`, `ScopedRateThrottle` for Auth endpoints).
  - Security hardening headers (`SECURE_BROWSER_XSS_FILTER`, `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS`).
  - Global standardized exception handler (`utils/exceptions.py`).
- **Interactive API Documentation**:
  - Swagger UI (`/api/docs/`), Redoc (`/api/redoc/`), and OpenAPI 3.0 Schema (`/api/schema/`) via `drf-spectacular`.

---

## Quickstart Guide

### Prerequisites
- Python 3.10+
- Virtual Environment (`venv`)

### Local Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd django-rest-ecommerce-starter-
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to `ecommerce/.env`:
   ```bash
   cp .env.example ecommerce/.env
   ```

5. **Run Database Migrations**:
   ```bash
   cd ecommerce
   python manage.py migrate
   ```

6. **Create Admin Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```
   Access Swagger documentation at: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

---

## Running Automated Tests

Run the full unit test suite (Auth, Catalog, Cart, Orders, Checkout):
```bash
python manage.py test
```

---

## Docker Deployment

Run the entire application stack (PostgreSQL + Web API) using Docker Compose:

```bash
docker-compose up --build -d
```

---

## REST API Endpoints Reference Matrix

| Category | HTTP Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/v1/auth/register/` | Register new user account | AllowAny (Throttled) |
| **Auth** | `POST` | `/api/v1/auth/login/` | Obtain JWT Token Pair | AllowAny (Throttled) |
| **Auth** | `POST` | `/api/v1/auth/token/refresh/` | Refresh JWT Token | AllowAny |
| **Auth** | `GET / PATCH` | `/api/v1/auth/me/` | Profile details & update | IsAuthenticated |
| **Auth** | `POST` | `/api/v1/auth/change-password/` | Change account password | IsAuthenticated |
| **Categories**| `GET` | `/api/v1/categories/` | List root categories with children | AllowAny |
| **Categories**| `POST / DELETE` | `/api/v1/categories/` | Create / Delete category | Admin / Seller |
| **Products** | `GET` | `/api/v1/products/` | List products with search/filters | AllowAny |
| **Products** | `GET` | `/api/v1/products/{id}/` | Get product details & reviews | AllowAny |
| **Products** | `POST` | `/api/v1/products/` | Create product | Admin / Seller |
| **Products** | `POST` | `/api/v1/products/{id}/upload_images/` | Upload gallery images | Admin / Seller |
| **Reviews** | `GET / POST` | `/api/v1/reviews/` | List or submit product review | IsAuthenticated |
| **Cart** | `GET` | `/api/v1/cart/` | View current shopping cart | AllowAny |
| **Cart** | `POST` | `/api/v1/cart/` | Add item to cart | AllowAny |
| **Cart** | `PATCH / DELETE`| `/api/v1/cart/items/{id}/` | Update or remove cart item | AllowAny |
| **Wishlist** | `GET` | `/api/v1/wishlist/` | Get user saved wishlist | IsAuthenticated |
| **Wishlist** | `POST` | `/api/v1/wishlist/toggle/` | Toggle product in wishlist | IsAuthenticated |
| **Address** | `GET / POST` | `/api/v1/addresses/` | List & add shipping addresses | IsAuthenticated |
| **Checkout** | `POST` | `/api/v1/checkout/` | Atomic Checkout process | IsAuthenticated |
| **Orders** | `GET` | `/api/v1/orders/` | List user order history | IsAuthenticated |
| **Orders** | `POST` | `/api/v1/orders/{id}/cancel/` | Cancel order & restore stock | IsAuthenticated |
| **Docs** | `GET` | `/api/docs/` | Interactive Swagger UI | AllowAny |

---

## License

This project is licensed under the MIT License.