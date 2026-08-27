ShopEase – Full-Stack E-Commerce Web Application

ShopEase is a **full-stack E-Commerce web application** developed to provide a complete online shopping experience. The application allows users to browse and search for products, filter products by category, manage their shopping cart, validate stock availability, place orders, and make online payments using Razorpay.

The project also includes **admin-side product and inventory management**, allowing administrators to add, update, and delete products and manage stock availability.

---

## 🚀 Features

### 👤 User Features

* 🔐 User registration and login
* 🔍 Product search
* 🗂️ Category-based product filtering
* 🛍️ Product browsing and product details
* 🛒 Add products to shopping cart
* ➕ Increase or decrease product quantity
* ❌ Remove products from cart
* 📦 Stock availability validation
* 🧾 Place orders
* 📋 View order information
* 💳 Online payment using Razorpay

### 👨‍💼 Admin Features

* ➕ Add new products
* ✏️ Update product details
* 🗑️ Delete products
* 📦 Manage product inventory
* 📊 Manage stock availability
* 🛍️ Manage the product catalog

---

## 🏗️ Project Architecture

```text
ShopEase
│
├── Frontend
│   └── React.js
│
├── Backend
│   └── Flask
│
├── Database
│   └── MySQL
│
└── Payment Gateway
    └── Razorpay
```

The application follows a **frontend–backend–database architecture**.

```text
User
  │
  ▼
React.js Frontend
  │
  │ REST APIs
  ▼
Flask Backend
  │
  ├── Authentication
  ├── Product Management
  ├── Cart Management
  ├── Order Management
  ├── Inventory Management
  └── Payment Processing
  │
  ▼
MySQL Database
```

---

## 🛠️ Tech Stack

### Frontend

* React.js
* JavaScript
* HTML5
* CSS3

### Backend

* Python
* Flask
* REST APIs

### Database

* MySQL

### Payment Gateway

* Razorpay

### Development Tools

* Git
* GitHub
* VS Code

---

## 🔑 Core Functionalities

### 🔍 Product Search & Filtering

Users can search for products and filter products based on categories, making it easier to find required items.

### 🛒 Shopping Cart

The shopping cart allows users to:

* Add products
* Remove products
* Update quantities
* View cart totals
* Validate product stock before checkout

### 📦 Stock Validation

The application checks product availability before completing an order to help prevent users from purchasing products that are unavailable or exceed the available stock.

### 🔐 Authentication

Users can register and log in to the application. Authentication helps provide user-specific functionality such as order management.

### 📋 Order Management

The application handles the complete order workflow, including:

```text
Product Selection
       ↓
Shopping Cart
       ↓
Stock Validation
       ↓
Order Creation
       ↓
Payment
       ↓
Order Processing
```

### 💳 Razorpay Integration

Razorpay is integrated into the application to support online payments.

The payment workflow connects the frontend, Flask backend, and Razorpay payment service.

### 👨‍💼 Admin Product Management

Administrators can manage the product catalog by:

* Adding products
* Updating products
* Deleting products
* Updating stock
* Managing product availability

---

## 🗄️ Database

MySQL is used as the relational database for storing and managing application data.

The database handles information related to:

* Users
* Products
* Product categories
* Cart items
* Orders
* Inventory
* Payment-related information

The Flask backend communicates with MySQL to perform database operations.

---

## 🔗 REST API

The Flask backend provides RESTful APIs that allow the React frontend to communicate with the server.

The APIs handle operations related to:

* User authentication
* Product management
* Product search and filtering
* Shopping cart
* Orders
* Inventory
* Payments

```text
React.js
   │
   │ HTTP Requests
   ▼
Flask REST API
   │
   │ Database Operations
   ▼
MySQL
```

---

## 📁 Project Structure

```text
ShopEase/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── app.py
│   ├── routes/
│   ├── models/
│   ├── ...
│   └── requirements.txt
│
├── database/
│   └── ...
│
├── README.md
└── .gitignore
```

> Update the folder names above if your actual GitHub repository uses a different structure.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Sreejaramgari/ecommerce.git
```

```bash
cd ecommerce
```

### 2. Backend Setup

Create and activate a Python virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure MySQL

Create a MySQL database for the application.

Update your database configuration with your local MySQL credentials.

Example:

```text
Host: localhost
Database: your_database_name
Username: your_mysql_username
Password: your_mysql_password
```

> Never upload your actual database password or secret credentials to GitHub.

### 4. Configure Razorpay

Add your Razorpay API credentials through environment variables or a configuration file that is excluded from GitHub.

Example:

```text
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
```

**Do not commit real API keys or secrets to the repository.**

### 5. Start the Backend

Run the Flask application:

```bash
python app.py
```

### 6. Start the Frontend

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the React application:

```bash
npm start
```

If your project uses Vite, use:

```bash
npm run dev
```

---

## 🖥️ Application Workflow

```text
User
 │
 ▼
Browse Products
 │
 ▼
Search / Filter Products
 │
 ▼
Add to Cart
 │
 ▼
Update Cart
 │
 ▼
Stock Validation
 │
 ▼
Checkout
 │
 ▼
Razorpay Payment
 │
 ▼
Order Creation
 │
 ▼
Order Management
```

---

## 🎯 Project Objectives

The main objectives of ShopEase were to:

* Build a real-world full-stack web application
* Understand frontend and backend integration
* Develop RESTful APIs
* Work with relational databases
* Implement authentication
* Implement shopping cart and inventory logic
* Integrate an online payment gateway
* Build admin-side CRUD functionality
* Understand end-to-end application development

---

## 📚 Learning Outcomes

Through this project, I gained practical experience in:

* React.js frontend development
* Python Flask backend development
* REST API development
* MySQL database management
* CRUD operations
* Authentication
* Cart and order management
* Inventory and stock validation
* Payment gateway integration
* Frontend-backend communication
* Full-stack application architecture
* Git and GitHub
**GitHub:**
https://github.com/Sreejaramgari

**ShopEase Repository:**
https://github.com/Sreejaramgari/ecommerce
