import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from models.encryption import decrypt_email

load_dotenv()


def send_order_confirmation_email(
    encrypted_email,
    customer_name,
    order_id,
    total,
    payment_method
):
    try:
        sender_email = os.getenv("SHOPKART_MAIL_USERNAME")
        sender_password = os.getenv("SHOPKART_MAIL_PASSWORD")

        if not sender_email or not sender_password:
            print("Mail credentials are missing in .env")
            return False

        customer_email = decrypt_email(encrypted_email)

        message = EmailMessage()

        message["Subject"] = f"ShopKart Order Confirmed - {order_id}"
        message["From"] = sender_email
        message["To"] = customer_email

        message.set_content(
            f"""ShopKart
Shop More, Worry Less.

Order Confirmed

Hello {customer_name},

Thank you for shopping with ShopKart.

Your order has been successfully placed.

Order ID: {order_id}
Payment Method: {payment_method}
Total Amount: ₹{total:.2f}
Status: Confirmed

We will keep you updated about your order.

Thank you for choosing ShopKart.

ShopKart Team
"""
        )

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)

        print(f"Order confirmation email sent to {customer_email}")
        return True

    except Exception as error:
        print("Email sending failed:", error)
        return False


def send_order_status_email(
    encrypted_email,
    customer_name,
    order_id,
    status
):
    try:
        sender_email = os.getenv("SHOPKART_MAIL_USERNAME")
        sender_password = os.getenv("SHOPKART_MAIL_PASSWORD")

        if not sender_email or not sender_password:
            print("Mail credentials are missing in .env")
            return False

        customer_email = decrypt_email(encrypted_email)

        message = EmailMessage()

        message["Subject"] = (
            f"ShopKart Order Update - {order_id}"
        )

        message["From"] = sender_email
        message["To"] = customer_email

        message.set_content(
            f"""ShopKart
Shop More, Worry Less.

Order Status Update

Hello {customer_name},

Your ShopKart order has been updated.

Order ID: {order_id}
Current Status: {status}

We will keep you updated about your order.

Thank you for choosing ShopKart.

ShopKart Team
"""
        )

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)

        print(
            f"Order status email sent to {customer_email}"
        )

        return True

    except Exception as error:
        print("Order status email failed:", error)
        return False