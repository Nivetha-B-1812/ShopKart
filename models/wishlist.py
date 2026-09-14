from . import db


class Wishlist(db.Model):

    __tablename__ = "wishlists"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=db.func.now()
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "wishlist_items",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    product = db.relationship(
        "Product",
        backref=db.backref(
            "wishlist_items",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "product_id",
            name="unique_user_product_wishlist"
        ),
    )