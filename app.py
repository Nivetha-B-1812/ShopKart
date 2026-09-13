from flask import Flask, render_template, session, redirect, url_for, jsonify, request
import os
from config import Config
from models import db
from models.category import Category
from models.product import Product
from models.order import Order
from models.order_item import OrderItem
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from models.encryption import encrypt_email, email_lookup
from models.email_service import (
    send_order_confirmation_email,
    send_order_status_email
)

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

    return jsonify({
        "success": True,
        "message": "Login successful."
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

    return render_template(
        "product.html",
        product=product
    )

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


    total = sum(
        item["product"].price * item["quantity"]
        for item in cart_items
    )


    import uuid

    order_id = (
        "SK"
        + uuid.uuid4().hex[:10].upper()
    )


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


    for item in cart_items:

        product = item["product"]
        quantity = item["quantity"]

        subtotal = (
            product.price * quantity
        )


        order_item = OrderItem(

            order_id=order.id,

            product_id=product.id,

            product_name=product.name,

            product_price=product.price,

            quantity=quantity,

            subtotal=subtotal
        )


        db.session.add(order_item)
    db.session.commit()

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

    session["cart"] = {}
    session.modified = True

    return jsonify({
        "success": True,
        "message": "Order placed successfully.",
        "order_id": order_id
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
def inject_admin_status():
    return {
        "is_admin": is_admin
    }

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

    # Save the new status
    order.status = new_status

    db.session.commit()

    # Find the customer account
    user = User.query.filter_by(
        email_lookup=email_lookup(order.email)
    ).first()

    # Send status notification email
    if user and user.email_encrypted:

        send_order_status_email(
            encrypted_email=user.email_encrypted,
            customer_name=user.full_name,
            order_id=order.order_id,
            status=order.status
        )

    return jsonify({
        "success": True,
        "message": "Order status updated and customer notified.",
        "status": order.status
    })
    
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

# =========================================================
# DATABASE SEED
# =========================================================

def seed_database():

    # CATEGORIES
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # ADD CATEGORIES
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # PRODUCTS
    # EXACTLY 6 PRODUCTS PER CATEGORY
    # TOTAL = 48 PRODUCTS
    # -----------------------------------------------------

    products = {

        "Electronics": [
            ("Wireless Headphone", 1500),
            ("Smartwatch", 2500),
            ("Smartphone", 15000),
            ("Laptop", 54999),
            ("Bluetooth Speaker", 1499),
            ("Tablet", 15999)
        ],

        "Fashion": [
            ("Sneakers", 2000),
            ("T-Shirt", 500),
            ("Hand Bag", 850),
            ("Jeans", 800),
            ("Hoodie", 499),
            ("Sunglasses", 199)
        ],

        "Home & Kitchen": [
            ("Mixer Grinder", 3299),
            ("Nonstick Cookware Set", 1999),
            ("Table Lamp", 999),
            ("Electric Kettle", 1299),
            ("Dinner Set", 1499),
            ("Air Fryer", 2999)
        ],

        "Books": [
            ("Fiction", 299),
            ("Programming", 399),
            ("Self Help", 149),
            ("Science", 249),
            ("Biography", 349),
            ("History", 249)
        ],

        "Gaming": [
            ("Gaming Keyboard", 1999),
            ("Game Controller", 2499),
            ("Gaming Headset", 1799),
            ("Gaming Mouse", 1299),
            ("Gaming Chair", 8999),
            ("Gaming Monitor", 12999)
        ],

        "Fruits": [
            ("Apple", 80),
            ("Banana", 70),
            ("Mango", 150),
            ("Orange", 120),
            ("Grapes", 110),
            ("Pomegranate", 180)
        ],

        "Vegetables": [
            ("Tomato", 60),
            ("Potato", 50),
            ("Carrot", 80),
            ("Onion", 55),
            ("Cucumber", 45),
            ("Capsicum", 90)
        ],

        "Grocery": [
            ("Rice", 650),
            ("Coconut Oil", 220),
            ("Biscuit", 50),
            ("Wheat Flour", 70),
            ("Sugar", 55),
            ("Tea Powder", 180)
        ]
    }


    # -----------------------------------------------------
    # REMOVE OLD PRODUCT NAME
    # -----------------------------------------------------

    old_product = Product.query.filter_by(
        name="Wireless Headphones"
    ).first()

    if old_product:
        db.session.delete(old_product)
        db.session.commit()


    # -----------------------------------------------------
    # ADD / UPDATE PRODUCTS
    # -----------------------------------------------------

    for category_name, product_list in products.items():

        category = Category.query.filter_by(
            name=category_name
        ).first()

        if not category:
            continue

        for product_name, price in product_list:

            existing_product = Product.query.filter_by(
                name=product_name
            ).first()

            if existing_product:

                existing_product.name = product_name

                existing_product.image = (
                    product_name.lower().replace(" ", "-") + ".jpg"
                )

            else:

                product = Product(
                    category_id=category.id,
                    name=product_name,
                    description=(
                        f"High-quality {product_name} "
                        "available at ShopKart."
                    ),
                    price=price,
                    image=product_name.lower().replace(" ", "-") + ".jpg",
                    rating=4.5,
                    stock=50
                )

                db.session.add(product)

    db.session.commit()


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

with app.app_context():

    db.create_all()

    seed_database()

# =========================================================
# RUN APPLICATION
# =========================================================
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )