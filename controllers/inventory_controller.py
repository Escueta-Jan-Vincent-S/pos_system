from database.database import add_item, delete_item, update_item, get_item_by_barcode

def on_add_item(item_name, category, unit_cost, selling_price, current_stock, product_barcode=""):
    try:
        add_item(
            item_name,
            category,
            float(unit_cost) if unit_cost else 0,
            float(selling_price) if selling_price else 0,
            int(current_stock) if current_stock else 0,
            product_barcode
        )
        print("Item added successfully!")
    except Exception as e:
        print(f"Error adding item: {e}")

def on_delete_item(barcode):
    delete_item(barcode)
    print(f"Item {barcode} deleted!")

def on_edit_item(barcode, item_name, category, unit_cost, selling_price, current_stock, product_barcode=None):
    try:
        update_item(barcode, item_name, category,
            float(unit_cost) if unit_cost else 0,
            float(selling_price) if selling_price else 0,
            int(current_stock) if current_stock else 0,
            product_barcode)
        print(f"Item {barcode} updated!")
    except Exception as e:
        print(f"Error updating item: {e}")