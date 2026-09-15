'''text

🛒 ShopKart

🛍️ Shop More, Worry Less.

ShopKart is a professional full-stack e-commerce web application designed to provide a modern, secure, and user-friendly online shopping experience.

The application is inspired by modern e-commerce platforms while maintaining its own unique branding, design, features, and functionality.

---

🔗 Project Links

📂 GitHub Repository

https://github.com/Nivetha-B-1812/ShopKart

🌐 Live Website

https://shopkart-5q9a.onrender.com

---

📌 About ShopKart

ShopKart is a complete e-commerce web application developed as part of a Full Stack Web Development academic project.

It provides users with a complete online shopping experience including product browsing, category navigation, search, authentication, cart management, checkout, order tracking, wishlist, and account management.

The application also includes a dedicated Admin Dashboard for managing products, orders, stock, pricing, ratings, and order status.

---

✨ Key Features

👤 Customer Features

Feature| Description
🏠 Home Page| Professional e-commerce landing page
🔍 Product Search| Search for products quickly
🗂️ Categories| Browse products by category
🖼️ Product Details| View product information and images
🛒 Add to Cart| Add products to the shopping cart
➕➖ Quantity Control| Increase or decrease product quantity
❌ Remove Product| Remove products from the cart
💰 Dynamic Total| Automatically calculate cart total
⚡ Buy Now| Direct purchase option
💳 Checkout| Complete the checkout process
📦 Order Management| View current and previous orders
🚚 Order Tracking| Track order status
❤️ Wishlist| Save favorite products
👤 Profile| Manage customer profile
🔑 Password Management| Change account password
🚪 Logout| Securely logout from the account

---

🛍️ Product Categories

ShopKart provides 8 major product categories with a collection of products for a realistic shopping experience.

Category| Products
📱 Electronics| 6
👕 Fashion| 6
🏠 Home & Kitchen| 6
📚 Books| 6
🎮 Gaming| 6
🍎 Fruits| 6
🥕 Vegetables| 6
🛒 Grocery| 6
Total| 48

---

🛠️ Admin Dashboard

ShopKart includes a dedicated administration system for managing the e-commerce platform.

📊 Dashboard

Administrators can monitor:

- 📦 Total Orders
- 💰 Total Sales
- ✅ Confirmed Orders
- 📦 Packed Orders
- 🚚 Shipped Orders
- 🏠 Delivered Orders
- ❌ Cancelled Orders
- 🕒 Recent Orders

📋 Order Management

Admins can:

- 👀 View customer orders
- 📄 View complete order details
- 🔄 Update order status
- 📦 Manage order workflow
- 📧 Send order status notifications

🛍️ Product Management

Admins can:

- 👀 View products
- ✏️ Edit product information
- 💰 Update product prices
- 📦 Update stock
- ⭐ Update product ratings
- 🗂️ Change product categories
- 📄 View product details

---

🚚 Order Workflow

ShopKart provides a structured order management process:

🟢 Confirmed
      ↓
📦 Packed
      ↓
🚚 Shipped
      ↓
🏠 Delivered

Orders can also be cancelled when applicable.

---

🔐 Security

Security is an important component of the ShopKart application.

The project implements:

- 🔒 Secure password hashing
- 🔐 Encrypted email storage
- 🛡️ Authenticated encryption using PyNaCl
- 🔑 HMAC-based email lookup
- 👤 Session-based authentication
- ⚙️ Environment variables for sensitive credentials
- 🚫 ".gitignore" protection for confidential configuration

Sensitive credentials and encryption keys are kept outside the public source code.

---

💻 Technology Stack

Layer| Technologies
🎨 Frontend| HTML5, CSS3, JavaScript
⚙️ Backend| Python, Flask
🗄️ ORM| Flask-SQLAlchemy, SQLAlchemy
💾 Database| SQLite
🔐 Authentication| Flask Sessions, Werkzeug
🛡️ Security| PyNaCl, HMAC
📧 Email| SMTP / Email Service
📂 Version Control| Git, GitHub
☁️ Deployment| Render
🚀 Production Server| Gunicorn

---

📁 Project Structure

ShopKart/
│
├── 📄 app.py
├── 📄 config.py
├── 📄 requirements.txt
├── 🔐 .env
├── 📄 .gitignore
│
├── 📂 database/
│   └── shopkart.db
│
├── 📂 models/
│   ├── __init__.py
│   ├── user.py
│   ├── category.py
│   ├── product.py
│   ├── cart.py
│   ├── order.py
│   ├── order_item.py
│   ├── encryption.py
│   └── email_service.py
│
├── 📂 templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── product.html
│   ├── cart.html
│   ├── checkout.html
│   ├── orders.html
│   ├── account.html
│   ├── profile.html
│   ├── admin_dashboard.html
│   ├── admin_orders.html
│   ├── admin_order_details.html
│   ├── admin_products.html
│   └── admin_edit_product.html
│
└── 📂 static/
    ├── 📂 css/
    │   └── style.css
    │
    ├── 📂 js/
    │   └── script.js
    │
    └── 📂 images/
        ├── logo/
        ├── categories/
        └── products/

---

⚙️ Installation

1️⃣ Clone the Repository

git clone https://github.com/Nivetha-B-1812/ShopKart.git
cd ShopKart

2️⃣ Create Virtual Environment

python -m venv venv

Windows

venv\Scripts\activate

Linux / macOS

source venv/bin/activate

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Configure Environment Variables

Create a ".env" file in the project root:

SECRET_KEY=your-secret-key
SHOPKART_ENCRYPTION_KEY=your-encryption-key
SHOPKART_MAIL_USERNAME=your-email
SHOPKART_MAIL_PASSWORD=your-app-password
SHOPKART_ADMIN_EMAIL=your-admin-email
SHOPKART_CONTACT_EMAIL=your-contact-email
SHOPKART_HELP_EMAIL=your-help-email

«⚠️ Never upload real passwords, API keys, or encryption keys to GitHub.»

5️⃣ Run the Application

python app.py

Open the application in your browser:

http://127.0.0.1:5000/

---

☁️ Deployment

ShopKart is deployed using Render with Gunicorn as the production server.

Deployment Flow

📂 GitHub
    ↓
☁️ Render
    ↓
🚀 Gunicorn
    ↓
⚙️ Flask Application

🌐 Live Website

https://shopkart-5q9a.onrender.com

---

📧 Email Notifications

ShopKart supports email notification functionality for:

- 📩 Order confirmation
- 🔄 Order status updates
- 📦 Order-related notifications

Customer email information is protected using encryption and secure lookup mechanisms.

---

🚀 Future Enhancements

Future versions of ShopKart can include:

- 💳 Real payment gateway integration
- 🐘 PostgreSQL production database
- 📧 Advanced email API integration
- 📱 Progressive Web App support
- 🔔 Real-time notifications
- 🎟️ Coupon and discount system
- ⭐ Customer review system
- 📊 Advanced admin analytics
- 🚚 Improved delivery management
- ❤️ Enhanced wishlist functionality

---

🎓 Academic Project

ShopKart was developed as a Full Stack Web Development academic project.

The project demonstrates practical implementation of:

- 🎨 Frontend Development
- ⚙️ Backend Development
- 💾 Database Management
- 👤 User Authentication
- 🔐 Data Security
- 🛒 E-Commerce Functionality
- ☁️ Cloud Deployment

---

👩‍💻 Developer

Nivetha Baskar

B.Tech Information Technology

Full Stack Web Development Project

---

🔗 Important Links

📂 GitHub

https://github.com/Nivetha-B-1812/ShopKart

🌐 ShopKart

https://shopkart-5q9a.onrender.com

---

📜 License

This project is developed for academic and educational purposes.

Copyright © 2026 ShopKart.

---

<p align="center">🛒 ShopKart

Shop More, Worry Less.

Built with HTML, CSS, JavaScript, Python, Flask & SQLAlchemy.

</p>

'''