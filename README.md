ShopKart

Shop More, Worry Less.

ShopKart is a full-stack e-commerce web application developed as an academic project. It provides a professional online shopping experience with product browsing, category-based shopping, search, cart management, checkout, user authentication, order tracking, and admin management.

Live Application

Live Demo:
https://shopkart-5q9a.onrender.com

Project Overview

ShopKart is designed as a modern e-commerce platform inspired by real-world online shopping applications while maintaining its own brand identity and implementation.

The application includes both customer-side and administrator-side functionality.

Key Features

Customer Features

- Professional responsive home page
- Product categories
- 48 products across 8 categories
- Product details page
- Product search
- Add to Cart
- Update cart quantity
- Remove products from cart
- Dynamic cart count
- Buy Now
- Checkout
- Order placement
- Order confirmation page
- My Account
- My Profile
- Edit profile information
- Change password
- My Orders
- Order status tracking
- Login
- Sign Up
- Logout

Product Categories

ShopKart contains 8 categories:

1. Electronics
2. Fashion
3. Home & Kitchen
4. Books
5. Gaming
6. Fruits
7. Vegetables
8. Grocery

Each category contains 6 products, giving a total of 48 products.

Security Features

ShopKart includes security-related features such as:

- Password hashing using Werkzeug
- User session management
- Encrypted email storage
- Key-based email lookup
- Authenticated encryption using PyNaCl SecretBox
- Environment variables for sensitive configuration
- Separate admin access control

Sensitive credentials and encryption keys are stored using environment variables and are not included in the GitHub repository.

Admin Features

The administrator can:

- Access the Admin Dashboard
- View order statistics
- View total sales
- Manage customer orders
- View order details
- Update order status
- Send order status notifications
- View all products
- Edit product information
- Update price, stock and rating
- View product details

Order Status

Orders can have the following statuses:

- Confirmed
- Packed
- Shipped
- Delivered
- Cancelled

Technology Stack

Frontend

- HTML5
- CSS3
- JavaScript
- Responsive Web Design
- SVG Icons

Backend

- Python
- Flask
- Flask-SQLAlchemy

Database

- SQLite
- SQLAlchemy ORM

Security

- Werkzeug Password Hashing
- PyNaCl
- SecretBox authenticated encryption
- HMAC-based email lookup

Deployment

- GitHub
- Render

Project Structure

ShopKart/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── database/
│   └── shopkart.db
│
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── product.py
│   ├── category.py
│   ├── cart.py
│   ├── order.py
│   ├── order_item.py
│   ├── encryption.py
│   └── email_service.py
│
├── routes/
│   ├── auth.py
│   ├── main.py
│   ├── products.py
│   ├── cart.py
│   ├── checkout.py
│   └── account.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── categories.html
│   ├── product.html
│   ├── cart.html
│   ├── checkout.html
│   ├── order_success.html
│   ├── account.html
│   ├── orders.html
│   └── admin pages
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

Installation and Setup

1. Clone the Repository

git clone https://github.com/Nivetha-B-1812/ShopKart.git
cd ShopKart

2. Create a Virtual Environment

python -m venv venv

Activate the environment:

source venv/bin/activate

3. Install Dependencies

pip install -r requirements.txt

4. Configure Environment Variables

Create a ".env" file and add the required configuration:

SECRET_KEY=your_secret_key

SHOPKART_ENCRYPTION_KEY=your_encryption_key

SHOPKART_MAIL_USERNAME=your_email
SHOPKART_MAIL_PASSWORD=your_app_password

SHOPKART_ADMIN_EMAIL=your_admin_email

SHOPKART_CONTACT_EMAIL=your_contact_email
SHOPKART_HELP_EMAIL=your_help_email

Do not commit the ".env" file to GitHub.

5. Run the Application

python app.py

Open:

http://127.0.0.1:5000/

Email Notification

ShopKart includes an email notification system for order-related communication.

When running locally, the application can send:

- Order confirmation emails
- Order status update emails

The email recipient address is obtained from the encrypted user email data and decrypted only when required for authorized email delivery.

Deployment

The project is connected to GitHub and deployed as a Flask web service.

Start Command

gunicorn app:app

Environment variables required for deployment must be configured in the deployment platform.

Future Improvements

Possible future enhancements include:

- Online payment gateway integration
- Persistent production database
- HTTPS-based transactional email API
- Product reviews and ratings
- Wishlist
- Coupon and discount system
- Advanced product filtering
- Recommendation system
- Image upload management
- Improved admin analytics
- Persistent cloud storage

Academic Project

Project Name: ShopKart
Type: Full Stack Web Development Project
Application: E-Commerce Web Application
Tagline: Shop More, Worry Less.

Author

Nivetha Baskar

B.Tech Information Technology

License

This project is developed for academic and educational purposes.