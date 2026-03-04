from database.database import add_item, delete_item


def on_add_item(item_name, category, unit_cost, selling_price, current_stock):
    try:
        add_item(
            item_name,
            category,
            float(unit_cost) if unit_cost else 0,
            float(selling_price) if selling_price else 0,
            int(current_stock) if current_stock else 0
        )
        print("Item added successfully!")
    except Exception as e:
        print(f"Error adding item: {e}")

def on_delete_item(barcode):
    delete_item(barcode)
    print(f"Item {barcode} deleted!")