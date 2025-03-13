from app import app, db
from app.models import Product


def insert_sample_data():
    with app.app_context():
        # Create the database tables
        db.create_all()

        # Insert sample data
        products = [
            Product(name="Laptop", description="A high-end laptop", price=1200.00),
            Product(name="Phone", description="Latest smartphone", price=800.00),
        ]
        db.session.bulk_save_objects(products)
        db.session.commit()
        print("Sample data inserted successfully!")


if __name__ == "__main__":
    insert_sample_data()
