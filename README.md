```text

🛒 ShopKart

🛍️ Shop More, Worry Less.

A professional full-stack e-commerce web application inspired by modern online shopping platforms, developed as an academic Full Stack Web Development project.

🌐 Live Application: https://shopkart-5q9a.onrender.com

---

✨ About ShopKart

ShopKart is a full-stack e-commerce application designed to provide a smooth, modern, and user-friendly online shopping experience.

The application includes product browsing, category-based shopping, search, cart management, secure authentication, checkout, order tracking, customer account management, and an admin dashboard.

---

🚀 Key Features

🏠 Customer Features

- 🛍️ Professional home page
- 📦 Browse products by category
- 🔎 Product search
- 🖼️ Product images and details
- ⭐ Product ratings
- 🛒 Add products to cart
- ➕➖ Update product quantity
- ❌ Remove products from cart
- 💰 Dynamic cart total
- ⚡ Buy Now option
- 💳 Checkout and simulated payment
- 📋 Order summary
- 📦 Order tracking
- 👤 Customer account
- 📝 Edit profile
- 🔐 Change password
- 🚪 Secure logout

---

🗂️ Product Categories

ShopKart currently contains 8 categories with 48 products.

Category| Products
💻 Electronics| 6
👗 Fashion| 6
🏠 Home & Kitchen| 6
📚 Books| 6
🎮 Gaming| 6
🍎 Fruits| 6
🥕 Vegetables| 6
🛒 Grocery| 6

Total: 48 Products

---

🔐 Security Features

ShopKart includes security-focused features for user accounts and sensitive information.

- 🔒 Secure password hashing
- 🔐 Encrypted email storage
- 🛡️ Authenticated encryption using PyNaCl
- 🔑 HMAC-based email lookup
- 🍪 Session-based authentication
- 🔒 Environment variables for sensitive credentials
- 🚫 Sensitive configuration excluded from GitHub using ".gitignore"

---

👨‍💼 Admin Features

ShopKart includes a dedicated admin dashboard for managing the application.

📊 Admin Dashboard

- 📦 Total orders
- 💰 Total sales
- 🟡 Confirmed orders
- 📦 Packed orders
- 🚚 Shipped orders
- ✅ Delivered orders
- ❌ Cancelled orders
- 🕒 Recent orders

📋 Order Management

- 👀 View all customer orders
- 📄 View order details
- 🔄 Update order status
- 📧 Send order status notifications

🛍️ Product Management

- 📦 View all products
- ✏️ Edit product information
- 💰 Update price
- 📊 Update stock
- ⭐ Update rating
- 🗂️ Change product category
- 👀 View product details

---

📦 Order Status

Orders can move through the following stages:

🟡 Confirmed
      ↓
📦 Packed
      ↓
🚚 Shipped
      ↓
✅ Delivered

Orders can also be marked as:

❌ Cancelled

---

🛠️ Technology Stack

🎨 Frontend

- HTML5
- CSS3
- JavaScript

⚙️ Backend

- Python
- Flask
- Flask-SQLAlchemy

🗄️ Database

- SQLite
- SQLAlchemy ORM

🔐 Security

- Werkzeug Password Hashing
- PyNaCl
- HMAC
- Environment Variables

☁️ Deployment

- GitHub
- Render
- Gunicorn

---


📁 Project Structure

ShopKart/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
│
├── database/
│   └── shopkart.db
│
├── models/
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
├── templates/
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
└── static/
    ├── css/
    │   └── style.css
    │
    ├── js/
    │   └── script.js
    │
    └── images/
        ├── logo/
        ├── categories/
        └── products/


---

⚙️ Installation & Setup

1️⃣ Clone the Repository

git clone https://github.com/Nivetha-B-1812/ShopKart.git
cd ShopKart

2️⃣ Install Dependencies

pip install -r requirements.txt

3️⃣ Configure Environment Variables

Create a ".env" file and configure the required application secrets.

SECRET_KEY=your-secret-key

SHOPKART_ENCRYPTION_KEY=your-encryption-key

SHOPKART_MAIL_USERNAME=your-email
SHOPKART_MAIL_PASSWORD=your-app-password

SHOPKART_ADMIN_EMAIL=your-admin-email

SHOPKART_CONTACT_EMAIL=your-contact-email
SHOPKART_HELP_EMAIL=your-help-email

«⚠️ Never upload the ".env" file or real passwords/keys to GitHub.»

---

▶️ Run the Application

Start the Flask application using:

python app.py

Then open:

http://127.0.0.1:5000/

---

📧 Email Notification

ShopKart includes email notification functionality for:

- 📩 Order confirmation
- 🔄 Order status updates

The application uses the customer's encrypted email information and decrypts it only when authorized email delivery is required.

☁️ Deployment Note

The local application successfully supports email notifications.

However, the current Render Free Web Service environment restricts outbound SMTP traffic, so Gmail SMTP email delivery may not work after deployment.

The application itself remains functional for:

- 🔐 Login
- 🛒 Cart
- 💳 Checkout
- 📦 Order placement
- 👨‍💼 Admin management
- 📋 Order tracking

---

🌐 Deployment

ShopKart is deployed using:

- 🐙 GitHub for source code
- ☁️ Render for hosting
- 🚀 Gunicorn as the production WSGI server

🔗 Live Website

https://shopkart-5q9a.onrender.com

---

🔮 Future Improvements

Planned improvements for future versions include:

- 💳 Real payment gateway integration
- 📧 HTTPS-based email API integration
- 🗄️ PostgreSQL production database
- 📱 Progressive Web App support
- ❤️ Wishlist functionality
- 🔔 Real-time notifications
- 🎟️ Coupon and discount system
- ⭐ Customer reviews
- 📊 Advanced admin analytics
- 🚚 Improved delivery management

---

🎓 Academic Project

This project was developed as part of a Full Stack Web Development academic project.

The main objective is to demonstrate practical implementation of:

Frontend
   ↓
Backend
   ↓
Database
   ↓
Authentication
   ↓
Security
   ↓
E-Commerce
   ↓
Deployment

---

👩‍💻 Developer

Nivetha Baskar

🎓 B.Tech Information Technology
💻 Full Stack Web Development Project

---

📜 License

This project is developed for academic and educational purposes.

© 2026 ShopKart. All rights reserved.

---

🛒 ShopKart

Shop More, Worry Less.

Built with HTML, CSS, JavaScript, Python, Flask & SQLAlchemy.

```