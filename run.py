from app import (
    app,
    db,
)  # Replace 'your_module_name' with the actual module name or path

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
