import re

# Тест форматирования цены
price_text = '3001 р.'.replace(' р.', '').replace('р', '')
formatted_price = re.sub(r'\B(?=(\d{3})+(?!\d))', ' ', price_text) + ' ₽'

print('Исходная цена:', '3001 р.')
print('После replace:', price_text)
print('Форматированная:', formatted_price)

# Тест с разными вариантами
test_prices = ['3000 р.', '3001 р.', '3500 р.', '10000 р.']
for price in test_prices:
    clean = price.replace(' р.', '').replace('р', '')
    formatted = re.sub(r'\B(?=(\d{3})+(?!\d))', ' ', clean) + ' ₽'
    print(f'{price} -> {formatted}')
