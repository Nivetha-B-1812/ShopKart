from flask import Flask, render_template, session, redirect, url_for, jsonify, request
import os
from config import Config
from models import db
from models.category import Category
from models.product import Product
from models.order import Order
from models.order_item import OrderItem
from models.user import User
from models.review import Review
from werkzeug.security import generate_password_hash, check_password_hash
from models.encryption import encrypt_email, email_lookup
from models.email_service import (
    send_order_confirmation_email,
    send_order_status_email
)
from models.wishlist import Wishlist
from models.feedback import Feedback
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
# =========================================================
# SHOPKART APPLICATION
# =========================================================

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

def is_admin():
    if not session.get("logged_in"):
        return False

    admin_email = os.getenv("SHOPKART_ADMIN_EMAIL", "").strip().lower()
    user_email = session.get("user_email", "").strip().lower()

    return bool(admin_email and user_email == admin_email)
    
# =========================================================
# PRODUCT DISPLAY RATING
# =========================================================

def get_product_rating(product):

    review_average = db.session.query(
        db.func.avg(Review.rating)
    ).filter(
        Review.product_id == product.id
    ).scalar()

    if review_average is not None:
        return round(float(review_average), 1)

    return product.rating
# =========================================================
# HOME PAGE + SEARCH
# =========================================================

@app.route("/")
def home():

    search_query = request.args.get("q", "").strip()

    if search_query:

        search_text = f"%{search_query}%"

        products = Product.query.filter(
            db.or_(
                Product.name.ilike(search_text),
                Product.description.ilike(search_text),
                Product.category.has(
                    Category.name.ilike(search_text)
                )
            )
        ).all()

        categories = Category.query.filter(
            Category.name.ilike(search_text)
        ).all()

        return render_template(
            "index.html",
            products=products,
            search_query=search_query,
            search_categories=categories
        )

    featured_products = Product.query.limit(4).all()

    return render_template(
        "index.html",
        featured_products=featured_products
    )
    
    
# =========================================================
# LOGIN PAGE
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    # Required fields
    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Please enter your email and password."
        }), 400

    # Find user
    email_hash = email_lookup(email)

    user = User.query.filter_by(
    email_lookup=email_hash
    ).first()

    # Invalid email/password
    if not user or not check_password_hash(
        user.password,
        password
    ):
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    # Create login session
    session["user_id"] = user.id
    session["user_name"] = user.full_name
    session["user_email"] = email
    session["logged_in"] = True

    session.permanent = bool(
        data.get("remember", False)
    )

    if is_admin():
        return jsonify({
            "success": True,
            "message": "Admin login successful.",
            "redirect": url_for("admin_dashboard")
        })

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "redirect": url_for("home")
    })
    
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "GET":
        return render_template("signup.html")

    data = request.get_json(silent=True) or {}

    full_name = data.get("fullName", "").strip()
    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip()
    password = data.get("password", "")
    confirm_password = data.get("confirmPassword", "")

    # Required fields
    if not all([full_name, email, password, confirm_password]):
        return jsonify({
            "success": False,
            "message": "Please fill in all required fields."
        }), 400

    # Password match
    if password != confirm_password:
        return jsonify({
            "success": False,
            "message": "Passwords do not match."
        }), 400

    # Password requirements
    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 8 characters."
        }), 400

    if not any(char.isupper() for char in password):
        return jsonify({
            "success": False,
            "message": "Password must contain at least one uppercase letter."
        }), 400

    if not any(char.islower() for char in password):
        return jsonify({
            "success": False,
            "message": "Password must contain at least one lowercase letter."
        }), 400

    if not any(char.isdigit() for char in password):
        return jsonify({
            "success": False,
            "message": "Password must contain at least one number."
        }), 400

    if not any(not char.isalnum() for char in password):
        return jsonify({
            "success": False,
            "message": "Password must contain at least one special character."
        }), 400

    # Check existing email using secure lookup
    email_hash = email_lookup(email)

    existing_user = User.query.filter_by(
        email_lookup=email_hash
    ).first()

    if existing_user:
        return jsonify({
            "success": False,
            "message": "An account with this email already exists."
        }), 400

    # Secure password hashing
    hashed_password = generate_password_hash(
        password,
        method="scrypt"
    )

    user = User(
        full_name=full_name,
        email=email,
        email_encrypted=encrypt_email(email),
        email_lookup=email_hash,
        password=hashed_password,
        phone=phone
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Account created successfully."
    })

    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
    
@app.route("/account")
def account():

    if is_admin():
        return render_template("admin_account.html")

    return render_template("account.html")
    
@app.route("/profile")
def profile():

    # Check whether user is logged in
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    # Get logged-in user's ID from session
    user_id = session.get("user_id")

    # Find user in database
    user = User.query.get(user_id)

    if not user:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        user=user
    )
    
@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if not user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template(
            "edit_profile.html",
            user=user
        )

    data = request.get_json(silent=True) or {}

    full_name = data.get("fullName", "").strip()
    phone = data.get("phone", "").strip()

    if not full_name:
        return jsonify({
            "success": False,
            "message": "Full name is required."
        }), 400

    if phone and (not phone.isdigit() or len(phone) != 10):
        return jsonify({
            "success": False,
            "message": "Phone number must contain exactly 10 digits."
        }), 400

    user.full_name = full_name
    user.phone = phone

    db.session.commit()

    session["user_name"] = user.full_name

    return jsonify({
        "success": True,
        "message": "Profile updated successfully."
    })
    
@app.route("/edit-address", methods=["GET", "POST"])
def edit_address():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if not user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template(
            "edit_address.html",
            user=user
        )

    data = request.get_json(silent=True) or {}

    address = data.get("address", "").strip()
    city = data.get("city", "").strip()
    state = data.get("state", "").strip()
    pincode = data.get("pincode", "").strip()

    if not address:
        return jsonify({
            "success": False,
            "message": "Address is required."
        }), 400

    if not city:
        return jsonify({
            "success": False,
            "message": "City is required."
        }), 400

    if not state:
        return jsonify({
            "success": False,
            "message": "State is required."
        }), 400

    if not pincode or not pincode.isdigit() or len(pincode) != 6:
        return jsonify({
            "success": False,
            "message": "Pincode must contain exactly 6 digits."
        }), 400

    user.address = address
    user.city = city
    user.state = state
    user.pincode = pincode

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Delivery address updated successfully."
    })
    
@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    user = User.query.get(user_id)

    if not user:
        session.clear()
        return redirect(url_for("login"))

    # Open Change Password page
    if request.method == "GET":
        return render_template(
            "change_password.html"
        )

    # Receive password data
    data = request.get_json(silent=True) or {}

    current_password = data.get(
        "currentPassword",
        ""
    )

    new_password = data.get(
        "newPassword",
        ""
    )

    confirm_password = data.get(
        "confirmPassword",
        ""
    )


    # Check empty fields
    if not current_password or not new_password or not confirm_password:

        return jsonify({
            "success": False,
            "message": "Please fill in all password fields."
        }), 400


    # Check current password
    if not check_password_hash(
        user.password,
        current_password
    ):

        return jsonify({
            "success": False,
            "message": "Current password is incorrect."
        }), 400


    # Check new password confirmation
    if new_password != confirm_password:

        return jsonify({
            "success": False,
            "message": "New passwords do not match."
        }), 400


    # Password length
    if len(new_password) < 8:

        return jsonify({
            "success": False,
            "message": "Password must contain at least 8 characters."
        }), 400


    # Uppercase
    if not any(
        char.isupper()
        for char in new_password
    ):

        return jsonify({
            "success": False,
            "message": "Password must contain at least one uppercase letter."
        }), 400


    # Lowercase
    if not any(
        char.islower()
        for char in new_password
    ):

        return jsonify({
            "success": False,
            "message": "Password must contain at least one lowercase letter."
        }), 400


    # Number
    if not any(
        char.isdigit()
        for char in new_password
    ):

        return jsonify({
            "success": False,
            "message": "Password must contain at least one number."
        }), 400


    # Special character
    if not any(
        not char.isalnum()
        for char in new_password
    ):

        return jsonify({
            "success": False,
            "message": "Password must contain at least one special character."
        }), 400


    # New password must be different
    if check_password_hash(
        user.password,
        new_password
    ):

        return jsonify({
            "success": False,
            "message": "New password must be different from your current password."
        }), 400


    # Hash new password using scrypt
    user.password = generate_password_hash(
        new_password,
        method="scrypt"
    )

    db.session.commit()


    return jsonify({
        "success": True,
        "message": "Password changed successfully."
    })
    
    
# =========================================================
# CATEGORY PAGES
# =========================================================

@app.route("/electronics")
def electronics():
    category = Category.query.filter_by(name="Electronics").first()
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template(
        "category.html",
        category=category,
        products=products
    )


@app.route("/fashion")
def fashion():
    category = Category.query.filter_by(name="Fashion").first()
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template(
        "category.html",
        category=category,
        products=products
    )


@app.route("/home-kitchen")
def home_kitchen():
    category = Category.query.filter_by(name="Home & Kitchen").first()
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template(
        "category.html",
        category=category,
        products=products
    )


@app.route("/books")
def books():
    category = Category.query.filter_by(name="Books").first()
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template(
        "category.html",
        category=category,
        products=products
    )


@app.route("/gaming")
def gaming():
    category = Category.query.filter_by(name="Gaming").first()
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template(
        "category.html",
        category=category,
        products=products
    )


@app.route("/fruits")
def fruits():
    category = Category.query.filter_by(name="Fruits").first()
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template(
        "category.html",
        category=category,
        products=products
    )


@app.route("/vegetables")
def vegetables():
    category = Category.query.filter_by(name="Vegetables").first()
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template(
        "category.html",
        category=category,
        products=products
    )


@app.route("/grocery")
def grocery():
    category = Category.query.filter_by(name="Grocery").first()
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template(
        "category.html",
        category=category,
        products=products
    )

# =========================================================
# PRODUCT DETAILS
# =========================================================
@app.route("/product/<int:product_id>")
def product_details(product_id):

    product = Product.query.get_or_404(product_id)

    reviews = Review.query.filter_by(
        product_id=product.id
    ).order_by(
        Review.created_at.desc()
    ).all()

    # =========================================================
    # CUSTOMER REVIEW RATING
    # =========================================================

    if reviews:

        review_average = round(
            sum(review.rating for review in reviews)
            / len(reviews),
            1
        )

    else:

        review_average = 0

    # =========================================================
    # PRODUCT RATING = CUSTOMER REVIEW AVERAGE
    # =========================================================

    if reviews:

        product_rating = review_average

    else:

        product_rating = product.rating

    return render_template(
        "product.html",
        product=product,
        reviews=reviews,
        review_average=review_average,
        product_rating=product_rating
    )
    
@app.route("/product/<int:product_id>/review", methods=["POST"])
def submit_review(product_id):

    # User must be logged in
    if not session.get("logged_in"):
        return jsonify({
            "success": False,
            "message": "Please login to submit a review."
        }), 401

    product = Product.query.get(product_id)

    if not product:
        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    data = request.get_json(silent=True) or {}

    rating = data.get("rating")
    comment = data.get("comment", "").strip()

    # Validate rating
    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Please select a valid rating."
        }), 400

    if rating < 1 or rating > 5:
        return jsonify({
            "success": False,
            "message": "Rating must be between 1 and 5."
        }), 400

    # Validate comment
    if not comment:
        return jsonify({
            "success": False,
            "message": "Please write your ."
        }), 400

    if len(comment) < 5:
        return jsonify({
            "success": False,
            "message": " must contain at least 5 characters."
        }), 400

    if len(comment) > 1000:
        return jsonify({
            "success": False,
            "message": " cannot exceed 1000 characters."
        }), 400

    user_id = session.get("user_id")

    # One review per customer for each product
    existing_review = Review.query.filter_by(
        product_id=product.id,
        user_id=user_id
    ).first()

    if existing_review:
        return jsonify({
            "success": False,
            "message": "You have already reviewed this product."
        }), 400

    review = Review(
        product_id=product.id,
        user_id=user_id,
        rating=rating,
        comment=comment
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Your review has been submitted successfully."
    })

@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    product = Product.query.get_or_404(product_id)

    data = request.get_json(silent=True) or {}

    quantity = int(data.get("quantity", 1))

    if quantity < 1:
        quantity = 1

    if quantity > 10:
        quantity = 10

    cart = session.get("cart", {})

    product_id_str = str(product_id)

    if product_id_str in cart:
        new_quantity = cart[product_id_str] + quantity

        if new_quantity > 10:
            new_quantity = 10

        cart[product_id_str] = new_quantity
    else:
        cart[product_id_str] = quantity

    session["cart"] = cart
    session.modified = True

    return jsonify({
        "success": True,
        "message": f"{product.name} added to cart",
        "cart_count": sum(cart.values())
    })

# =========================================================
# CART PAGE
# =========================================================

@app.route("/cart")
def cart():

    cart = session.get("cart", {})

    cart_items = []

    for product_id, quantity in cart.items():

        product = Product.query.get(int(product_id))

        if product:
            cart_items.append({
                "product": product,
                "quantity": quantity
            })

    cart_count = sum(cart.values())

    return render_template(
        "cart.html",
        cart_items=cart_items,
        cart_count=cart_count
    )

@app.route("/clear-cart")
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("cart"))

@app.route("/checkout")
def checkout():

    cart = session.get("cart", {})

    cart_items = []

    for product_id, quantity in cart.items():

        product = Product.query.get(int(product_id))

        if product:
            cart_items.append({
                "product": product,
                "quantity": quantity
            })

    subtotal = sum(
        item["product"].price * item["quantity"]
        for item in cart_items
    )

    delivery_charge = 0

    total = subtotal + delivery_charge

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        subtotal=subtotal,
        delivery_charge=delivery_charge,
        total=total
    )
    
@app.route("/buy-now", methods=["POST"])
def buy_now():

    data = request.get_json(silent=True) or {}

    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid product or quantity."
        }), 400

    if quantity < 1 or quantity > 10:
        return jsonify({
            "success": False,
            "message": "Invalid quantity."
        }), 400

    product = Product.query.get(product_id)

    if not product:
        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    if product.stock < quantity:
        return jsonify({
            "success": False,
            "message": "Insufficient stock."
        }), 400

    session["cart"] = {
        str(product.id): quantity
    }

    return jsonify({
        "success": True,
        "message": "Product ready for checkout."
    })

# =========================================================
# PLACE ORDER
# =========================================================

@app.route("/place-order", methods=["POST"])
def place_order():

    if not session.get("logged_in"):
        return jsonify({
            "success": False,
            "message": "Please login before placing an order."
        }), 401


    data = request.get_json(silent=True) or {}

    full_name = data.get("fullName", "").strip()
    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip()
    address = data.get("address", "").strip()
    city = data.get("city", "").strip()
    state = data.get("state", "").strip()
    pincode = data.get("pincode", "").strip()
    payment_method = data.get("payment", "cod")


    if not all([
        full_name,
        email,
        phone,
        address,
        city,
        state,
        pincode
    ]):
        return jsonify({
            "success": False,
            "message": "Please fill in all required fields."
        }), 400


    cart = session.get("cart", {})


    if not cart:
        return jsonify({
            "success": False,
            "message": "Your cart is empty."
        }), 400


    cart_items = []


    for product_id, quantity in cart.items():

        product = Product.query.get(
            int(product_id)
        )

        if product:

            quantity = int(quantity)

            if quantity < 1:
                quantity = 1

            cart_items.append({
                "product": product,
                "quantity": quantity
            })


    if not cart_items:
        return jsonify({
            "success": False,
            "message": "No valid products found in cart."
        }), 400
        # Check stock before placing the order
    for item in cart_items:
        product = item["product"]
        quantity = item["quantity"]

        if product.stock <= 0:
            return jsonify({
                "success": False,
                "message": f"{product.name} is currently out of stock."
            }), 400

        if quantity > product.stock:
            return jsonify({
                "success": False,
                "message": f"Only {product.stock} unit(s) of {product.name} are available."
            }), 400

    # =====================================================
    # SUBTOTAL + 10% DISCOUNT + FINAL TOTAL
    # =====================================================

    subtotal = sum(
        item["product"].price * item["quantity"]
        for item in cart_items
    )

    discount = subtotal * 0.10

    total = subtotal - discount


    # =====================================================
    # CREATE ORDER ID
    # =====================================================

    import uuid

    order_id = (
        "SK"
        + uuid.uuid4().hex[:10].upper()
    )


    # =====================================================
    # CREATE ORDER
    # =====================================================

    order = Order(
        order_id=order_id,
        full_name=full_name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        payment_method=payment_method,
        total=total,
        status="Confirmed"
    )


    db.session.add(order)

    db.session.flush()


    # =====================================================
    # CREATE ORDER ITEMS
    # =====================================================

    for item in cart_items:

        product = item["product"]
        quantity = item["quantity"]

        item_subtotal = (
            product.price * quantity
        )


        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_price=product.price,
            quantity=quantity,
            subtotal=item_subtotal
        )


        db.session.add(order_item)


    db.session.commit()

    # =====================================================
    # SEND ORDER CONFIRMATION EMAIL
    # =====================================================

    # Get logged-in user
    user = User.query.get(session.get("user_id"))

    # Send order confirmation email
    if user and user.email_encrypted:
        send_order_confirmation_email(
            encrypted_email=user.email_encrypted,
            customer_name=user.full_name,
            order_id=order.order_id,
            total=order.total,
            payment_method=order.payment_method
        )


    # =====================================================
    # CLEAR CART
    # =====================================================

    session["cart"] = {}
    session.modified = True


    return jsonify({
        "success": True,
        "message": "Order placed successfully.",
        "order_id": order.order_id,
        "total": order.total
    })

    
@app.route("/order-success/<order_id>")
def order_success(order_id):

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    order = Order.query.filter_by(
        order_id=order_id
    ).first_or_404()

    return render_template(
        "order_success.html",
        order=order
    )
    
@app.route("/orders")
def orders():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_email = session.get("user_email")

    orders = Order.query.filter_by(
        email=user_email
    ).order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "orders.html",
        orders=orders
    )
    
@app.route("/admin")
def admin_dashboard():

    if not is_admin():
        return redirect(url_for("home"))

    total_orders = Order.query.count()

    confirmed_orders = Order.query.filter_by(
        status="Confirmed"
    ).count()

    packed_orders = Order.query.filter_by(
        status="Packed"
    ).count()

    shipped_orders = Order.query.filter_by(
        status="Shipped"
    ).count()

    delivered_orders = Order.query.filter_by(
        status="Delivered"
    ).count()

    cancelled_orders = Order.query.filter_by(
        status="Cancelled"
    ).count()

    total_sales = db.session.query(
        db.func.sum(Order.total)
    ).scalar() or 0

    recent_orders = Order.query.order_by(
        Order.created_at.desc()
    ).limit(5).all()

    return render_template(
        "admin_dashboard.html",
        total_orders=total_orders,
        confirmed_orders=confirmed_orders,
        packed_orders=packed_orders,
        shipped_orders=shipped_orders,
        delivered_orders=delivered_orders,
        cancelled_orders=cancelled_orders,
        total_sales=total_sales,
        recent_orders=recent_orders
    )
    
@app.route("/admin/products")
def admin_products():

    if not is_admin():
        return redirect(url_for("home"))

    products = Product.query.order_by(
        Product.id.asc()
    ).all()

    return render_template(
        "admin_products.html",
        products=products
    )
    
@app.route("/admin/product/<int:product_id>/edit")
def admin_edit_product(product_id):

    if not is_admin():
        return redirect(url_for("home"))

    product = Product.query.get(product_id)

    if not product:
        return redirect(url_for("admin_products"))

    categories = Category.query.order_by(
        Category.name.asc()
    ).all()

    return render_template(
        "admin_edit_product.html",
        product=product,
        categories=categories
    )

@app.route("/admin/product/<int:product_id>/edit", methods=["POST"])
def update_admin_product(product_id):

    if not is_admin():
        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    product = Product.query.get(product_id)

    if not product:
        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    description = data.get("description", "").strip()
    category_id = data.get("category_id")
    price = data.get("price")
    stock = data.get("stock")
    rating = data.get("rating")

    if not all([
        name,
        description,
        category_id is not None,
        price is not None,
        stock is not None,
        rating is not None
    ]):
        return jsonify({
            "success": False,
            "message": "Please fill in all fields."
        }), 400

    try:
        category_id = int(category_id)
        price = float(price)
        stock = int(stock)
        rating = float(rating)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid product information."
        }), 400

    if price < 0:
        return jsonify({
            "success": False,
            "message": "Price cannot be negative."
        }), 400

    if stock < 0:
        return jsonify({
            "success": False,
            "message": "Stock cannot be negative."
        }), 400

    if rating < 0 or rating > 5:
        return jsonify({
            "success": False,
            "message": "Rating must be between 0 and 5."
        }), 400

    category = Category.query.get(category_id)

    if not category:
        return jsonify({
            "success": False,
            "message": "Category not found."
        }), 404

    product.name = name
    product.description = description
    product.category_id = category_id
    product.price = price
    product.stock = stock
    product.rating = rating

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Product updated successfully."
    })
# =========================================================
# ADMIN ORDERS
# =========================================================

@app.route("/admin/orders")
def admin_orders():

    if not is_admin():
        return redirect(url_for("home"))

    orders = Order.query.order_by(
        Order.created_at.desc()
    ).all()

    return render_template(
        "admin_orders.html",
        orders=orders
    )
  
@app.context_processor
def inject_template_functions():
    return {
        "is_admin": is_admin,
        "get_product_rating": get_product_rating,
        "to_ist": to_ist
    }

def to_ist(dt):
    if dt is None:
        return None

    return dt.replace(
        tzinfo=timezone.utc
    ).astimezone(
        ZoneInfo("Asia/Kolkata")
    )

@app.route("/admin/order/<int:order_id>")
def admin_order_details(order_id):

    if not is_admin():
        return redirect(url_for("home"))

    order = Order.query.get(order_id)

    if not order:
        return redirect(url_for("admin_orders"))

    return render_template(
        "admin_order_details.html",
        order=order
    )
    
@app.route("/toggle-wishlist/<int:product_id>", methods=["POST"])
def toggle_wishlist(product_id):

    if not session.get("logged_in"):
        return jsonify({
            "success": False,
            "login_required": True,
            "message": "Please login to use Wishlist."
        }), 401

    user_id = session.get("user_id")

    product = Product.query.get(product_id)

    if not product:
        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    existing = Wishlist.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()

        return jsonify({
            "success": True,
            "added": False,
            "message": "Removed from Wishlist."
        })

    wishlist_item = Wishlist(
        user_id=user_id,
        product_id=product_id
    )

    db.session.add(wishlist_item)
    db.session.commit()

    return jsonify({
        "success": True,
        "added": True,
        "message": "Added to Wishlist."
    })
# =========================================================
# UPDATE ORDER STATUS
# ========================================================#
@app.route("/admin/update-order-status/<int:order_id>", methods=["POST"])
def update_order_status(order_id):

    if not is_admin():
        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    data = request.get_json(silent=True) or {}
    new_status = data.get("status", "").strip()

    allowed_statuses = [
        "Confirmed",
        "Packed",
        "Shipped",
        "Delivered",
        "Cancelled"
    ]

    if new_status not in allowed_statuses:
        return jsonify({
            "success": False,
            "message": "Invalid order status."
        }), 400

    order = Order.query.get(order_id)

    if not order:
        return jsonify({
            "success": False,
            "message": "Order not found."
        }), 404

    # Update order status
    order.status = new_status

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Unable to update order status."
        }), 500

    # Send customer notification separately
    email_sent = False

    try:
        user = User.query.filter_by(
            email_lookup=email_lookup(order.email)
        ).first()

        if user and user.email_encrypted:

            send_order_status_email(
                encrypted_email=user.email_encrypted,
                customer_name=user.full_name,
                order_id=order.order_id,
                status=order.status
            )

            email_sent = True

    except Exception as e:
        # Email failure should NOT undo the status update
        print("Order status email error:", e)

    if email_sent:
        message = "Order status updated and customer notified."
    else:
        message = "Order status updated successfully."

    return jsonify({
        "success": True,
        "message": message,
        "status": order.status
    })
    
@app.before_request
def block_customer_pages_for_admin():
    # Only apply this restriction to logged-in admin users
    if not session.get("logged_in") or not is_admin():
        return

    # Admin is allowed to access these pages
    allowed_endpoints = {
    "admin_dashboard",
    "admin_products",
    "admin_edit_product",
    "update_admin_product",
    "admin_orders",
    "admin_order_details",
    "admin_",
    "update_order_status",
    "account",
    "profile",
    "edit_profile",
    "edit_address",
    "change_password",
    "logout",
    "login",
    "static",
    "admin_feedback",
    "edit_admin_feedback",
    "remove_admin_feedback"

}

    # Allow admin pages and account/security pages
    if request.endpoint in allowed_endpoints:
        return

    # Block every other customer-side route
    return redirect(url_for("admin_dashboard"))
    
# =========================================================
# CONTACT US
# =========================================================

@app.route("/contact")
def contact():
    return render_template("contact.html")
    
@app.route("/help-center")
def help_center():
    return render_template("help_center.html")
    
# =========================================================
# CUSTOMER 
# =========================================================
@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        rating = request.form.get("rating", "").strip()
        message = request.form.get("message", "").strip()
        feedback_category = request.form.get("feedback_category", "").strip()

        if not name or not email or not rating or not message:
            return render_template(
                "feedback.html",
                error="Please fill in all fields."
            )

        try:
            rating = int(rating)
        except ValueError:
            return render_template(
                "feedback.html",
                error="Invalid rating."
            )

        if rating < 1 or rating > 5:
            return render_template(
                "feedback.html",
                error="Rating must be between 1 and 5."
            )

        new_feedback = Feedback(
            name=name,
            email=email,
            rating=rating,
            message=message,
            feedback_category=feedback_category
        )

        db.session.add(new_feedback)
        db.session.commit()

        return render_template(
            "feedback.html",
            success="Thank you for your valuable feedback!"
        )

    return render_template(
        "feedback.html",
        user_name=session.get("user_name", ""),
        user_email=session.get("user_email", "")
    )

    
# =========================================================
# ADMIN - CUSTOMER FEEDBACK
# =========================================================

@app.route("/admin/feedback")
def admin_feedback():

    if not is_admin():
        return redirect(url_for("home"))

    feedbacks = Feedback.query.order_by(
        Feedback.created_at.desc()
    ).all()

    return render_template(
        "admin_feedback.html",
        feedbacks=feedbacks
    )
    
@app.route("/admin/feedback/<int:feedback_id>/edit", methods=["POST"])
def edit_admin_feedback(feedback_id):

    if not is_admin():
        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    feedback = Feedback.query.get(feedback_id)

    if not feedback:
        return jsonify({
            "success": False,
            "message": "Feedback not found."
        }), 404

    data = request.get_json(silent=True) or {}

    rating = data.get("rating")
    message = data.get("message", "").strip()
    feedback_category = data.get("feedback_category", "").strip()

    if rating is None or not message:
        return jsonify({
            "success": False,
            "message": "Please fill in all required fields."
        }), 400

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid rating."
        }), 400

    if rating < 1 or rating > 5:
        return jsonify({
            "success": False,
            "message": "Rating must be between 1 and 5."
        }), 400

    feedback.rating = rating
    feedback.message = message
    feedback.feedback_category = feedback_category

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Feedback updated successfully."
    })


@app.route("/admin/feedback/<int:feedback_id>/remove", methods=["POST"])
def remove_admin_feedback(feedback_id):

    if not is_admin():
        return jsonify({
            "success": False,
            "message": "Admin access required."
        }), 403

    feedback = Feedback.query.get(feedback_id)

    if not feedback:
        return jsonify({
            "success": False,
            "message": "Feedback not found."
        }), 404

    db.session.delete(feedback)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Feedback removed successfully."
    })
# =========================================================
# UPDATE CART QUANTITY
# =========================================================

@app.route("/update-cart/<int:product_id>", methods=["POST"])
def update_cart(product_id):

    data = request.get_json(silent=True) or {}

    quantity = int(data.get("quantity", 1))

    cart = session.get("cart", {})

    product_id_str = str(product_id)

    if product_id_str in cart:

        if quantity <= 0:
            cart.pop(product_id_str)
        else:
            cart[product_id_str] = quantity

    session["cart"] = cart
    session.modified = True

    return jsonify({
        "success": True,
        "cart_count": sum(cart.values())
    })


# =========================================================
# REMOVE FROM CART
# =========================================================

@app.route("/remove-from-cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):

    cart = session.get("cart", {})

    product_id_str = str(product_id)

    if product_id_str in cart:
        cart.pop(product_id_str)

    session["cart"] = cart
    session.modified = True

    return jsonify({
        "success": True,
        "cart_count": sum(cart.values())
    })
    
@app.route("/wishlist")
def wishlist():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session.get("user_id")

    wishlist_items = Wishlist.query.filter_by(
        user_id=user_id
    ).order_by(Wishlist.created_at.desc()).all()

    return render_template(
        "wishlist.html",
        wishlist_items=wishlist_items
    )

@app.route("/add-to-wishlist/<int:product_id>", methods=["POST"])
def add_to_wishlist(product_id):

    if not session.get("logged_in"):
        return jsonify({
            "success": False,
            "login_required": True,
            "message": "Please login to use Wishlist."
        }), 401

    user_id = session.get("user_id")

    product = Product.query.get(product_id)

    if not product:
        return jsonify({
            "success": False,
            "message": "Product not found."
        }), 404

    existing = Wishlist.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()

    if existing:
        return jsonify({
            "success": True,
            "already_exists": True,
            "message": "Product is already in your Wishlist."
        })

    wishlist_item = Wishlist(
        user_id=user_id,
        product_id=product_id
    )

    db.session.add(wishlist_item)
    db.session.commit()

    return jsonify({
        "success": True,
        "already_exists": False,
        "message": "Product added to Wishlist."
    })
# =========================================================
# DATABASE SEED
# =========================================================

def seed_database():

    # =====================================================
    # CATEGORIES
    # =====================================================

    categories = [
        {
            "name": "Electronics",
            "description": "Latest electronic products",
            "image": "electronics.jpg"
        },
        {
            "name": "Fashion",
            "description": "Trendy fashion products",
            "image": "fashion.jpg"
        },
        {
            "name": "Home & Kitchen",
            "description": "Useful products for your home",
            "image": "home-kitchen.jpg"
        },
        {
            "name": "Books",
            "description": "Books for knowledge and entertainment",
            "image": "books.jpg"
        },
        {
            "name": "Gaming",
            "description": "Gaming products and accessories",
            "image": "gaming.jpg"
        },
        {
            "name": "Fruits",
            "description": "Fresh and healthy fruits",
            "image": "fruits.jpg"
        },
        {
            "name": "Vegetables",
            "description": "Fresh vegetables for your kitchen",
            "image": "vegetables.jpg"
        },
        {
            "name": "Grocery",
            "description": "Everyday grocery essentials",
            "image": "grocery.jpg"
        }
    ]

    # =====================================================
    # ADD CATEGORIES
    # =====================================================

    for category_data in categories:

        existing_category = Category.query.filter_by(
            name=category_data["name"]
        ).first()

        if not existing_category:

            category = Category(
                name=category_data["name"],
                description=category_data["description"],
                image=category_data["image"]
            )

            db.session.add(category)

    db.session.commit()

    # =====================================================
    # PRODUCTS
    # EXACTLY 6 PRODUCTS PER CATEGORY
    # TOTAL = 48 PRODUCTS
    # =====================================================

    products = {

        "Electronics": [
            {
                "name": "Wireless Headphone",
                "price": 1500,
                "rating": 4.7,
                "description": "Comfortable wireless headphones with Bluetooth connectivity, clear stereo sound, deep bass, built-in microphone, adjustable headband and soft ear cushions. Suitable for music, online classes, calls and everyday entertainment."
            },
            {
                "name": "Smartwatch",
                "price": 2500,
                "rating": 4.6,
                "description": "Feature-rich smartwatch with a 1.83-inch display, heart-rate monitoring, SpO2 tracking, step counter, sleep monitoring, multiple sports modes and Bluetooth calling. Designed for everyday fitness tracking with a battery life of up to 7 days depending on usage."
            },
            {
                "name": "Smartphone",
                "price": 15000,
                "rating": 4.6,
                "description": "Modern smartphone featuring 8 GB RAM, 128 GB internal storage, a 6.5-inch Full HD+ display, 5000 mAh battery, 50 MP primary camera, front camera, octa-core processor, dual SIM support, 5G connectivity and USB Type-C charging."
            },
            {
                "name": "Laptop",
                "price": 54999,
                "rating": 4.7,
                "description": "Powerful laptop with 16 GB RAM, 512 GB SSD storage, 15.6-inch Full HD display and an Intel Core i5 processor. Includes integrated graphics, Wi-Fi 6, Bluetooth, USB connectivity and a comfortable full-size keyboard. Suitable for programming, office work, studying and everyday multitasking."
            },
            {
                "name": "Bluetooth Speaker",
                "price": 1499,
                "rating": 4.7,
                "description": "Portable Bluetooth speaker with powerful stereo audio, enhanced bass, wireless connectivity and a compact design. Includes rechargeable battery, hands-free calling support and easy controls, making it suitable for home use, travel and outdoor entertainment."
            },
            {
                "name": "Tablet",
                "price": 15999,
                "rating": 4.5,
                "description": "Versatile tablet with a large high-resolution display, 6 GB RAM, 128 GB internal storage and an efficient octa-core processor. Supports Wi-Fi, Bluetooth, USB Type-C connectivity and long-lasting battery performance for studying, browsing, video streaming and entertainment."
            }
        ],

        "Fashion": [
            {
                "name": "Sneakers",
                "price": 2000,
                "rating": 4.4,
                "description": "Comfortable casual sneakers designed for everyday walking and active use. Features a lightweight upper, cushioned footbed, flexible rubber outsole and breathable construction for improved comfort during long hours of wear."
            },
            {
                "name": "T-Shirt",
                "price": 500,
                "rating": 4.2,
                "description": "Soft everyday T-shirt made from comfortable cotton-blend fabric. Features a regular fit, round neckline, short sleeves and durable stitching. Easy to pair with jeans, trousers or shorts for casual everyday outfits."
            },
            {
                "name": "Hand Bag",
                "price": 850,
                "rating": 4.5,
                "description": "Stylish everyday handbag with a spacious main compartment and additional storage pockets for organizing personal belongings. Designed with durable material, comfortable handles and a versatile appearance suitable for college, work and casual outings."
            },
            {
                "name": "Jeans",
                "price": 800,
                "rating": 4.3,
                "description": "Classic denim jeans with a comfortable regular fit and durable stitching. Made from a soft yet strong denim blend with practical front and back pockets. Suitable for casual wear and easy to combine with shirts, T-shirts and jackets."
            },
            {
                "name": "Hoodie",
                "price": 499,
                "rating": 4.6,
                "description": "Comfortable casual hoodie made with soft fabric for warmth and everyday comfort. Features a hood, long sleeves, ribbed cuffs and a relaxed fit. Ideal for cool weather, travel, college wear and casual outdoor activities."
            },
            {
                "name": "Sunglasses",
                "price": 199,
                "rating": 4.1,
                "description": "Lightweight everyday sunglasses with UV-protection lenses and a comfortable frame. Designed to reduce bright sunlight and provide a stylish appearance for outdoor activities, travel and casual wear."
            }
        ],

        "Home & Kitchen": [
            {
                "name": "Mixer Grinder",
                "price": 3299,
                "rating": 4.5,
                "description": "Powerful mixer grinder designed for everyday kitchen preparation. Includes multiple stainless-steel jars for grinding, blending and mixing, along with durable blades and easy-to-use speed controls. Suitable for chutneys, spices, smoothies and everyday cooking needs."
            },
            {
                "name": "Nonstick Cookware Set",
                "price": 1999,
                "rating": 4.4,
                "description": "Practical nonstick cookware set designed for everyday cooking with less oil. Features durable nonstick interiors, comfortable handles and easy-to-clean surfaces. Suitable for preparing vegetables, curries, eggs, snacks and other daily meals."
            },
            {
                "name": "Table Lamp",
                "price": 999,
                "rating": 4.3,
                "description": "Modern table lamp designed for study, reading and bedside use. Provides comfortable illumination with a compact design and easy controls. Suitable for bedrooms, study tables, office desks and workspaces."
            },
            {
                "name": "Electric Kettle",
                "price": 1299,
                "rating": 4.6,
                "description": "Fast electric kettle designed for boiling water quickly and conveniently. Features a stainless-steel heating interior, automatic shut-off, boil-dry protection and an easy-pour handle. Suitable for tea, coffee, instant noodles and hot beverages."
            },
            {
                "name": "Dinner Set",
                "price": 1499,
                "rating": 4.2,
                "description": "Elegant everyday dinner set designed for family meals and entertaining guests. Includes essential plates, bowls and serving pieces with a durable finish. Easy to clean and suitable for regular dining and special occasions."
            },
            {
                "name": "Air Fryer",
                "price": 2999,
                "rating": 4.5,
                "description": "Convenient air fryer designed to prepare crispy food using significantly less oil than traditional frying. Features adjustable temperature and timer controls, a removable cooking basket and easy-clean surfaces. Suitable for fries, snacks, vegetables and baked foods."
            }
        ],

        "Books": [
            {
                "name": "Fiction",
                "price": 299,
                "rating": 4.4,
                "description": "Engaging fiction book collection featuring imaginative storytelling, memorable characters and interesting plots. Suitable for readers who enjoy novels, mystery, adventure, romance and entertaining stories during leisure time."
            },
            {
                "name": "Programming",
                "price": 399,
                "rating": 4.7,
                "description": "Programming reference book covering fundamental programming concepts, problem solving, algorithms, data structures and practical coding techniques. Suitable for students, beginners and developers who want to strengthen their programming skills."
            },
            {
                "name": "Self Help",
                "price": 149,
                "rating": 4.3,
                "description": "Self-help reading material focused on personal development, positive habits, productivity, confidence and goal setting. Designed to provide practical ideas that readers can apply to their everyday personal and professional life."
            },
            {
                "name": "Science",
                "price": 249,
                "rating": 4.5,
                "description": "Informative science book introducing important scientific concepts in an easy-to-understand format. Covers interesting topics from the natural world, technology and scientific discoveries, making it suitable for students and curious readers."
            },
            {
                "name": "Biography",
                "price": 349,
                "rating": 4.6,
                "description": "Inspirational biography featuring the life journey, achievements, challenges and experiences of a notable personality. Provides readers with valuable lessons about determination, success, leadership and overcoming obstacles."
            },
            {
                "name": "History",
                "price": 249,
                "rating": 4.2,
                "description": "Historical reading material covering important events, people, civilizations and developments from the past. Written to help readers understand historical timelines, major changes and their influence on modern society."
            }
        ],

        "Gaming": [
            {
                "name": "Gaming Keyboard",
                "price": 1999,
                "rating": 4.5,
                "description": "Responsive gaming keyboard featuring tactile keys, dedicated gaming controls, anti-ghosting support and durable construction. Designed for fast and accurate gameplay as well as comfortable everyday typing."
            },
            {
                "name": "Game Controller",
                "price": 2499,
                "rating": 4.4,
                "description": "Ergonomic game controller with responsive analog sticks, precision buttons, directional controls and comfortable grips. Suitable for PC and compatible gaming systems, providing improved control for racing, sports, action and adventure games."
            },
            {
                "name": "Gaming Headset",
                "price": 1799,
                "rating": 4.6,
                "description": "Immersive gaming headset with stereo audio, deep bass, adjustable headband, cushioned ear cups and a built-in microphone. Designed for gaming, voice communication, movies and music with comfortable long-session use."
            },
            {
                "name": "Gaming Mouse",
                "price": 1299,
                "rating": 4.3,
                "description": "Precision gaming mouse with adjustable sensitivity, responsive buttons and ergonomic grip. Features smooth tracking and programmable controls for faster gameplay. Suitable for FPS, strategy, racing and everyday computer use."
            },
            {
                "name": "Gaming Chair",
                "price": 8999,
                "rating": 4.5,
                "description": "Ergonomic gaming chair with high-back support, cushioned seat, adjustable armrests and reclining backrest. Designed to provide comfortable seating during extended gaming, studying and computer work sessions."
            },
            {
                "name": "Gaming Monitor",
                "price": 12999,
                "rating": 4.7,
                "description": "Gaming monitor featuring a Full HD display, high refresh rate, fast response time and smooth image performance. Includes HDMI connectivity and adjustable display settings, making it suitable for competitive gaming, entertainment and everyday computing."
            }
        ],

        "Fruits": [
            {
                "name": "Apple",
                "price": 80,
                "rating": 4.5,
                "description": "Fresh and crisp apples selected for everyday consumption. Naturally sweet with a refreshing texture and suitable for snacks, fruit salads, lunch boxes and healthy everyday meals."
            },
            {
                "name": "Banana",
                "price": 70,
                "rating": 4.4,
                "description": "Fresh ripe bananas with a naturally sweet taste and soft texture. Convenient as a quick snack and suitable for breakfast, smoothies, desserts and everyday healthy meals."
            },
            {
                "name": "Mango",
                "price": 150,
                "rating": 4.8,
                "description": "Juicy and naturally sweet mangoes selected for their rich flavour and pleasant texture. Suitable for eating fresh, preparing smoothies, juices, desserts and refreshing summer dishes."
            },
            {
                "name": "Orange",
                "price": 120,
                "rating": 4.3,
                "description": "Fresh juicy oranges with a refreshing citrus flavour. Suitable for direct consumption, fresh juice, fruit salads and everyday snacks."
            },
            {
                "name": "Grapes",
                "price": 110,
                "rating": 4.2,
                "description": "Fresh table grapes with a naturally sweet flavour and juicy texture. Ideal for snacks, fruit bowls, lunch boxes and refreshing everyday consumption."
            },
            {
                "name": "Pomegranate",
                "price": 180,
                "rating": 4.6,
                "description": "Fresh pomegranates containing juicy ruby-red seeds with a naturally sweet and slightly tangy flavour. Suitable for direct consumption, salads, juices and healthy snack preparation."
            }
        ],

        "Vegetables": [
            {
                "name": "Tomato",
                "price": 60,
                "rating": 4.4,
                "description": "Fresh tomatoes with a juicy texture and balanced flavour. Suitable for curries, gravies, salads, sauces, soups and everyday Indian cooking."
            },
            {
                "name": "Potato",
                "price": 50,
                "rating": 4.5,
                "description": "Fresh versatile potatoes suitable for boiling, frying, baking and traditional cooking. Ideal for curries, snacks, fries, mashed dishes and everyday family meals."
            },
            {
                "name": "Carrot",
                "price": 80,
                "rating": 4.3,
                "description": "Fresh crunchy carrots with a naturally sweet flavour. Suitable for salads, soups, curries, stir-fries, juices and healthy snacks."
            },
            {
                "name": "Onion",
                "price": 55,
                "rating": 4.2,
                "description": "Fresh onions with a crisp texture and strong natural flavour. An everyday kitchen essential suitable for curries, gravies, salads, frying and a wide variety of dishes."
            },
            {
                "name": "Cucumber",
                "price": 45,
                "rating": 4.4,
                "description": "Fresh crisp cucumbers with a cool and refreshing taste. Suitable for salads, sandwiches, raita, juices and healthy snacks."
            },
            {
                "name": "Capsicum",
                "price": 90,
                "rating": 4.5,
                "description": "Fresh green capsicum with a crunchy texture and mild flavour. Suitable for stir-fries, pizzas, noodles, curries, salads and a variety of everyday recipes."
            }
        ],

        "Grocery": [
            {
                "name": "Rice",
                "price": 650,
                "rating": 4.6,
                "description": "Quality everyday rice suitable for regular family meals. Produces soft and flavourful cooked rice and can be used for steamed rice, biryani, fried rice, pulao and other traditional dishes."
            },
            {
                "name": "Coconut Oil",
                "price": 220,
                "rating": 4.4,
                "description": "Pure coconut oil suitable for everyday cooking and food preparation. Offers a naturally pleasant coconut aroma and can be used for frying, seasoning, traditional recipes and household cooking needs."
            },
            {
                "name": "Biscuit",
                "price": 50,
                "rating": 4.2,
                "description": "Crunchy everyday biscuits with a pleasant sweet flavour. Suitable for tea-time snacks, lunch boxes and quick refreshments for children and adults."
            },
            {
                "name": "Wheat Flour",
                "price": 70,
                "rating": 4.5,
                "description": "Fine-quality wheat flour suitable for preparing soft chapatis, rotis, parathas, pooris and other everyday Indian breads. Easy to mix and suitable for regular household cooking."
            },
            {
                "name": "Sugar",
                "price": 55,
                "rating": 4.3,
                "description": "Fine-grain everyday sugar suitable for tea, coffee, desserts, sweets, baking and general cooking. Dissolves easily and is convenient for regular household use."
            },
            {
                "name": "Tea Powder",
                "price": 180,
                "rating": 4.6,
                "description": "Aromatic tea powder selected for a rich flavour and refreshing everyday cup of tea. Suitable for preparing traditional milk tea, black tea and other hot tea beverages."
            }
        ]
    }

    # =====================================================
    # REMOVE OLD PRODUCT NAME
    # =====================================================

    old_product = Product.query.filter_by(
        name="Wireless Headphones"
    ).first()

    if old_product:
        db.session.delete(old_product)
        db.session.commit()

    # =====================================================
    # ADD / UPDATE PRODUCTS
    # =====================================================

    for category_name, product_list in products.items():

        category = Category.query.filter_by(
            name=category_name
        ).first()

        if not category:
            continue

        for product_data in product_list:

            product_name = product_data["name"]
            price = product_data["price"]
            rating = product_data["rating"]
            description = product_data["description"]

            existing_product = Product.query.filter_by(
                name=product_name
            ).first()

            if existing_product:

                existing_product.category_id = category.id
                existing_product.name = product_name
                existing_product.description = description
                existing_product.price = price
                existing_product.rating = rating
                existing_product.image = (
                    product_name.lower().replace(" ", "-") + ".jpg"
                )

            else:

                product = Product(
                    category_id=category.id,
                    name=product_name,
                    description=description,
                    price=price,
                    image=product_name.lower().replace(" ", "-") + ".jpg",
                    rating=rating,
                    stock=50
                )

                db.session.add(product)

    db.session.commit()


# =========================================================
# DEMO CUSTOMER REVIEWS
# =========================================================

def seed_demo_reviews():

    from datetime import datetime, timedelta

    # =========================================================
    # DEMO CUSTOMERS
    # =========================================================

    demo_customers = [
        {"name": "Arun Kumar", "email": "arun.demo@shopkart.com"},
        {"name": "Priya Sharma", "email": "priya.demo@shopkart.com"},
        {"name": "Rahul Raj", "email": "rahul.demo@shopkart.com"},
        {"name": "Sneha R", "email": "sneha.demo@shopkart.com"},
        {"name": "Karthik S", "email": "karthik.demo@shopkart.com"},
        {"name": "Divya M", "email": "divya.demo@shopkart.com"},
        {"name": "Vijay Kumar", "email": "vijay.demo@shopkart.com"},
        {"name": "Meena K", "email": "meena.demo@shopkart.com"},
        {"name": "Naveen P", "email": "naveen.demo@shopkart.com"},
        {"name": "Anjali S", "email": "anjali.demo@shopkart.com"}
    ]

    demo_users = []

    for customer in demo_customers:

        email = customer["email"].strip().lower()
        email_hash = email_lookup(email)

        user = User.query.filter_by(
            email_lookup=email_hash
        ).first()

        if not user:

            user = User(
                full_name=customer["name"],
                email=email,
                email_encrypted=encrypt_email(email),
                email_lookup=email_hash,
                password=generate_password_hash(
                    "ShopKart@123",
                    method="scrypt"
                ),
                phone=""
            )

            db.session.add(user)
            db.session.flush()

        demo_users.append(user)

    db.session.commit()

    # =========================================================
    # REMOVE ONLY OLD DEMO REVIEWS
    # REAL CUSTOMER REVIEWS ARE NOT DELETED
    # =========================================================

    demo_user_ids = [
        user.id for user in demo_users
    ]

    old_demo_reviews = Review.query.filter(
        Review.user_id.in_(demo_user_ids)
    ).all()

    for old_review in old_demo_reviews:
        db.session.delete(old_review)

    db.session.commit()

    # =========================================================
    # GENERAL REVIEWS
    # =========================================================

    general_reviews = {

        "Electronics": [
            ("The product quality is really good and the performance is better than I expected. 😊"),
            ("I am very happy with this purchase. The product works smoothly and feels reliable. 😍"),
            ("Good quality product for the price. The packaging was neat and secure. 👍"),
            ("The product looks premium and works exactly as described. Highly satisfied! ✨"),
            ("Very impressed with the quality and overall shopping experience. Thank you, ShopKart! 🌟"),
            ("Really useful product for everyday use. Everything arrived safely and in good condition. 👌"),
            ("The product is exactly as shown in the description. Good value for money. 💯"),
            ("Excellent quality and a smooth shopping experience. I would recommend this product. 🤩"),
            ("The product arrived on time and was packed properly. Very satisfied with my purchase. 🙌"),
            ("Good product and a pleasant shopping experience with ShopKart. Thank you, ShopKart! 🛍️")
        ],

        "Fashion": [
            ("The quality is very good and the product looks stylish. I really liked it. 🥰"),
            ("Really happy with the purchase. The product looks exactly as shown. ❤️"),
            ("Good material and comfortable to use. Worth the price. 👌"),
            ("The design looks premium and the quality is better than expected. ✨"),
            ("Very satisfied with the product. Thank you, ShopKart! 🌸"),
            ("The product arrived safely and the overall experience was excellent. 😊"),
            ("Nice quality and attractive design. I am happy with this purchase. 😍"),
            ("The product looks great and feels comfortable. Definitely worth the money. 💯"),
            ("Good product quality and neat packaging. Very satisfied! 🙌"),
            ("Loved the product and the smooth shopping experience. Thank you, ShopKart! 🛍️")
        ],

        "Home & Kitchen": [
            ("The product quality is excellent and it is very useful at home. 😊"),
            ("Really satisfied with the quality and performance of this product. 🥰"),
            ("Good product for everyday household use. The packaging was secure. 👍"),
            ("The product looks neat and works as expected. Worth the price. ✨"),
            ("Very happy with this purchase. Thank you, ShopKart! 🌟"),
            ("The quality is better than I expected and the product arrived safely. 👌"),
            ("Good value for money and useful for regular home use. 💯"),
            ("The product is exactly as described. Overall, a very good purchase. 😍"),
            ("Nice quality product with proper packaging. Highly satisfied! 🙌"),
            ("Excellent shopping experience and good product quality. Thank you, ShopKart! 🛍️")
        ],

        "Books": [
            ("The book quality is good and the pages are printed clearly. 📖"),
            ("Really enjoyed this book. The content is useful and easy to read. 😊"),
            ("Good quality book with neat printing and proper packaging. 👍"),
            ("The content is interesting and the book arrived in good condition. ✨"),
            ("Very happy with this purchase. Thank you, ShopKart! 🌟"),
            ("The book is exactly what I expected and the overall quality is good. 👌"),
            ("Good value for money. The book was packed safely and arrived on time. 💯"),
            ("The content is informative and the reading experience is very good. 🥰"),
            ("Nice book with good print quality. Highly satisfied with the purchase. 😍"),
            ("Excellent book and smooth shopping experience. Thank you, ShopKart! 📚")
        ],

        "Gaming": [
            ("The gaming product quality is excellent and the performance is smooth. 🎮"),
            ("Really happy with this gaming product. It works very well. 😎"),
            ("Good build quality and excellent performance for the price. 👍"),
            ("The product feels durable and works exactly as described. 🔥"),
            ("Very satisfied with the gaming experience. Thank you, ShopKart! 🤩"),
            ("The product arrived safely and the quality is better than expected. 👌"),
            ("Good value for money and suitable for regular gaming use. 💯"),
            ("The design looks great and the performance is really good. ⚡"),
            ("Excellent quality and a smooth overall gaming experience. 😊"),
            ("Loved the product and the overall experience. Thank you, ShopKart! 🕹️")
        ],

        "Grocery": [
            ("The grocery product quality is very good and the packaging was neat. 😊"),
            ("Good quality grocery product and the quantity was as expected. 👌"),
            ("The product was packed properly and arrived in good condition. 👍"),
            ("Really satisfied with the quality of this grocery item. 🥰"),
            ("Very happy with this grocery purchase. Thank you, ShopKart! 🌟"),
            ("Good value for money and suitable for regular household use. 💯"),
            ("The product quality is good and the packaging was secure. ✨"),
            ("The grocery item was exactly as described. Highly satisfied! 😍"),
            ("Nice quality product and a smooth delivery experience. 🙌"),
            ("Good grocery product and shopping experience. Thank you, ShopKart! 🛍️")
        ]
    }

    # =========================================================
    # FRUIT REVIEWS
    # EXACT FRUIT NAME IS INCLUDED IN EVERY REVIEW
    # =========================================================

    fruit_reviews = {

        "Apple": [
            ("The apple quality was excellent and the apples were fresh and crisp. 🍎"),
            ("These apples were fresh, juicy and good for everyday eating. 😊"),
            ("I really liked the apple quality. The apples arrived in good condition. 🥰"),
            ("The apples were fresh and nicely packed. Very satisfied! ❤️"),
            ("The apple taste was good and the quality was better than expected. Thank you, ShopKart! ✨"),
            ("Fresh apples with good quality. Really happy with this fruit purchase. 👌"),
            ("The apples looked fresh and tasted good. Worth the price. 🌟"),
            ("Good apple quality and proper packaging. Highly satisfied! 😍"),
            ("The apples were fresh and suitable for regular consumption. 👍"),
            ("Very happy with these apples. Thank you, ShopKart! 🍏")
        ],

        "Banana": [
            ("The banana quality was very good and the bananas arrived fresh. 🍌"),
            ("These bananas were fresh and had a good taste. 😊"),
            ("I liked the banana quality. The bananas were packed carefully. 🥰"),
            ("The bananas were fresh and good for everyday consumption. ❤️"),
            ("Very good banana quality and the freshness was impressive. Thank you, ShopKart! ✨"),
            ("The bananas arrived in good condition and tasted fresh. 👌"),
            ("Fresh bananas at a reasonable price. Really satisfied! 🌟"),
            ("The banana quality was better than expected. Good fruit purchase. 😍"),
            ("The bananas were fresh and suitable for regular use. 👍"),
            ("Loved the fresh bananas. Thank you, ShopKart! 🍌")
        ],

        "Mango": [
            ("The mangoes were fresh, juicy and had a really good taste. 🥭"),
            ("Very happy with the mango quality. The mangoes arrived in good condition. 😊"),
            ("The mangoes were tasty and fresh. Good quality fruit. 🥰"),
            ("I really liked these mangoes. They were fresh and delicious. ❤️"),
            ("Excellent mango quality and very good taste. Thank you, ShopKart! ✨"),
            ("The mangoes were packed properly and arrived fresh. 👌"),
            ("Good mangoes with nice taste and freshness. Worth the price. 🌟"),
            ("The mango quality was better than expected. Very satisfied! 😍"),
            ("Fresh and tasty mangoes. A very good fruit purchase. 👍"),
            ("Really enjoyed these mangoes. Thank you, ShopKart! 🥭")
        ],

        "Orange": [
            ("The oranges were fresh, juicy and had a good taste. 🍊"),
            ("Very good orange quality. The oranges arrived fresh and clean. 😊"),
            ("I liked the freshness of these oranges. Good fruit quality. 🥰"),
            ("The oranges were juicy and suitable for everyday consumption. ❤️"),
            ("Excellent orange quality and freshness. Thank you, ShopKart! ✨"),
            ("The oranges were packed carefully and arrived in good condition. 👌"),
            ("Fresh oranges with good taste. Really happy with the purchase. 🌟"),
            ("The orange quality was better than expected. Highly satisfied! 😍"),
            ("Good fresh oranges and proper packaging. 👍"),
            ("Loved the fresh oranges. Thank you, ShopKart! 🍊")
        ],

        "Grapes": [
            ("The grapes were fresh, sweet and good quality. 🍇"),
            ("Really liked the freshness of these grapes. They tasted good. 😊"),
            ("The grapes arrived in good condition and were nicely packed. 🥰"),
            ("Fresh grapes with good taste. Very satisfied with the purchase. ❤️"),
            ("Excellent grape quality and freshness. Thank you, ShopKart! ✨"),
            ("The grapes were sweet and suitable for regular consumption. 👌"),
            ("Good quality grapes at a reasonable price. 🌟"),
            ("The grape freshness was better than expected. Highly satisfied! 😍"),
            ("Fresh and tasty grapes. A very good fruit purchase. 👍"),
            ("Really happy with these grapes. Thank you, ShopKart! 🍇")
        ],

        "Pomegranate": [
            ("The pomegranate was fresh and the quality was really good. ❤️"),
            ("These pomegranates were fresh and the seeds tasted good. 😊"),
            ("I liked the pomegranate quality and freshness. Nicely packed. 🥰"),
            ("The pomegranate arrived in good condition and tasted fresh. 👌"),
            ("Excellent pomegranate quality. Thank you, ShopKart! ✨"),
            ("The pomegranate was fresh and suitable for regular consumption. 🌟"),
            ("Good quality pomegranate with fresh seeds. Very satisfied! 😍"),
            ("The pomegranate freshness was better than expected. 👍"),
            ("Fresh pomegranate with good quality and proper packaging. ❤️"),
            ("Really happy with the pomegranate purchase. Thank you, ShopKart!")
        ]
    }

    # =========================================================
    # VEGETABLE REVIEWS
    # EXACT VEGETABLE NAME IS INCLUDED IN EVERY REVIEW
    # =========================================================

    vegetable_reviews = {

        "Tomato": [
            ("The tomatoes were fresh, red and good quality. 🍅"),
            ("Very happy with the tomato freshness. The tomatoes arrived in good condition. 😊"),
            ("The tomatoes were fresh and suitable for everyday cooking. 🥰"),
            ("Good tomato quality and proper packaging. 👌"),
            ("The tomatoes were fresh and better than expected. Thank you, ShopKart! ✨"),
            ("Really satisfied with the freshness of these tomatoes. 🌟"),
            ("Fresh tomatoes at a good price. Very useful for regular cooking. 👍"),
            ("The tomato quality was excellent and the packing was neat. ❤️"),
            ("The tomatoes arrived fresh and in good condition. 😍"),
            ("Very happy with these fresh tomatoes. Thank you, ShopKart! 🍅")
        ],

        "Potato": [
            ("The potatoes were fresh and good quality. 🥔"),
            ("Very satisfied with the potato quality and freshness. 😊"),
            ("The potatoes were clean and suitable for everyday cooking. 🥰"),
            ("Good quality potatoes with proper packaging. 👌"),
            ("The potatoes were fresh and arrived in good condition. Thank you, ShopKart! ✨"),
            ("Really happy with the freshness of these potatoes. 🌟"),
            ("Fresh potatoes at a reasonable price. Good purchase. 👍"),
            ("The potato quality was better than expected. Very satisfied! ❤️"),
            ("The potatoes were good quality and useful for regular cooking. 😍"),
            ("Very happy with these potatoes. Thank you, ShopKart! 🥔")
        ],

        "Carrot": [
            ("The carrots were fresh, crunchy and good quality. 🥕"),
            ("Really happy with the freshness of these carrots. 😊"),
            ("The carrots arrived fresh and were suitable for everyday cooking. 🥰"),
            ("Good carrot quality and neat packaging. 👌"),
            ("The carrots were fresh and better than expected. Thank you, ShopKart! ✨"),
            ("Very satisfied with the quality and freshness of the carrots. 🌟"),
            ("Fresh carrots at a good price. Good purchase. 👍"),
            ("The carrot quality was excellent and the packing was proper. ❤️"),
            ("The carrots arrived in good condition and looked fresh. 😍"),
            ("Really happy with these fresh carrots. Thank you, ShopKart! 🥕")
        ],

        "Onion": [
            ("The onions were fresh and good quality. 🧅"),
            ("Very satisfied with the onion quality and freshness. 😊"),
            ("The onions arrived in good condition and were suitable for cooking. 🥰"),
            ("Good onion quality and proper packaging. 👌"),
            ("The onions were fresh and better than expected. Thank you, ShopKart! ✨"),
            ("Really happy with the freshness of these onions. 🌟"),
            ("Fresh onions at a reasonable price. Good purchase. 👍"),
            ("The onion quality was excellent and the packing was neat. ❤️"),
            ("The onions were good quality and useful for regular cooking. 😍"),
            ("Very happy with these fresh onions. Thank you, ShopKart! 🧅")
        ],

        "Cucumber": [
            ("The cucumbers were fresh, crisp and good quality. 🥒"),
            ("Really liked the freshness of these cucumbers. 😊"),
            ("The cucumbers arrived fresh and in good condition. 🥰"),
            ("Good cucumber quality and proper packaging. 👌"),
            ("The cucumbers were fresh and better than expected. Thank you, ShopKart! ✨"),
            ("Very satisfied with the quality and freshness of the cucumbers. 🌟"),
            ("Fresh cucumbers at a good price. Very happy with the purchase. 👍"),
            ("The cucumber quality was excellent and the packing was neat. ❤️"),
            ("The cucumbers looked fresh and were suitable for everyday use. 😍"),
            ("Really happy with these fresh cucumbers. Thank you, ShopKart! 🥒")
        ],

        "Capsicum": [
            ("The capsicums were fresh, crisp and good quality. 🫑"),
            ("Very happy with the freshness of these capsicums. 😊"),
            ("The capsicums arrived fresh and in good condition. 🥰"),
            ("Good capsicum quality and neat packaging. 👌"),
            ("The capsicums were fresh and better than expected. Thank you, ShopKart! ✨"),
            ("Really satisfied with the quality and freshness of the capsicums. 🌟"),
            ("Fresh capsicums at a reasonable price. Good purchase. 👍"),
            ("The capsicum quality was excellent and the packing was proper. ❤️"),
            ("The capsicums looked fresh and were suitable for regular cooking. 😍"),
            ("Very happy with these fresh capsicums. Thank you, ShopKart! 🫑")
        ]
    }

    # =========================================================
    # DATE RANGE
    # JANUARY 2, 2026 TO SEPTEMBER 12, 2026
    # =========================================================

    start_date = datetime(2026, 1, 2)
    end_date = datetime(2026, 9, 12)

    total_days = (
        end_date - start_date
    ).days

    # =========================================================
    # ALL PRODUCTS
    # =========================================================

    all_products = Product.query.order_by(
        Product.id.asc()
    ).all()

    # =========================================================
    # CREATE REVIEWS
    # =========================================================

    for product in all_products:

        # 6 to 10 reviews per product
        review_count = 6 + ((product.id - 1) % 5)

        category_name = product.category.name

        # -----------------------------------------------------
        # Correct review set based on category
        # -----------------------------------------------------

        if category_name == "Fruits":

            comments = fruit_reviews.get(
                product.name,
                []
            )

        elif category_name == "Vegetables":

            comments = vegetable_reviews.get(
                product.name,
                []
            )

        else:

            comments = general_reviews.get(
                category_name,
                general_reviews["Electronics"]
            )

        # -----------------------------------------------------
        # Create reviews
        # -----------------------------------------------------

        for index in range(review_count):

            user = demo_users[index]

            # 4 / 5 star ratings
            rating_pattern = [
                5, 4, 5, 5, 4,
                5, 5, 4, 5, 5
            ]

            rating = rating_pattern[index]

            # Different comment for each review
            comment = comments[
                (product.id + index) % len(comments)
            ]

            # -------------------------------------------------
            # Different past date
            # -------------------------------------------------

            day_offset = (
                (product.id * 17)
                + (index * 23)
                + (product.id * index * 3)
            ) % (total_days + 1)

            review_date = start_date + timedelta(
                days=day_offset
            )

            # Different time
            hour = 9 + (
                (product.id + index * 2) % 10
            )

            minute = (
                product.id * 7
                + index * 19
            ) % 60

            review_date = review_date.replace(
                hour=hour,
                minute=minute
            )

            review = Review(
                product_id=product.id,
                user_id=user.id,
                rating=rating,
                comment=comment,
                created_at=review_date
            )

            db.session.add(review)

    db.session.commit()

    print(
        "Demo customer reviews seeded successfully."
    )

# =========================================================
# DATABASE INITIALIZATION
# =========================================================

with app.app_context():

    db.create_all()

    seed_database()

    seed_demo_reviews()

# =========================================================
# RUN APPLICATION
# =========================================================
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )