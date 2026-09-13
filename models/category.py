from . import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), unique=True, nullable=False)

    description = db.Column(db.String(255), nullable=False)

    image = db.Column(db.String(255), nullable=True)

    products = db.relationship(
        "Product",
        backref="category",
        lazy=True,
        cascade="all, delete-orphan"
    )