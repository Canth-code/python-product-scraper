from database import (
    get_product_count,
    get_average_price,
    get_all_products
)


count = get_product_count()
average = get_average_price()

df = get_all_products()

print(f"Total products: {count}")
print(f"Average price: {average:.2f}")
print(f"Cheapest price: {df['price'].min():.2f}")
print(f"Most expensive price: {df['price'].max():.2f}")
print(f"Total value: {df['price'].sum():.2f}")