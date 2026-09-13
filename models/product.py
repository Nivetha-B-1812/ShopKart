from . import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    name = db.Column(db.String(150), nullable=False)

    description = db.Column(db.Text, nullable=False)

    price = db.Column(db.Float, nullable=False)

    image = db.Column(db.String(255), nullable=True)

    rating = db.Column(db.Float, default=4.5)

    stock = db.Column(db.Integer, default=50)