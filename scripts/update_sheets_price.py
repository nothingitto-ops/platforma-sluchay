#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import csv
import io
import json
from datetime import datetime

def update_sheets_price():
    """Обновление цены сумки через плечо в Google Sheets"""
    
    print("🔄 Обновление цены сумки через плечо...")
    
    # URL для получения данных из Google Sheets
    sheets_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRGdW7QcHV6BgZHJnSMzXKkmsXDYZulMojN312tgvI6PK86H8dRjReYUOHI2l_aVYzLg2NIjAcir89g/pub?output=tsv"
    
    try:
        print("📊 Получаем данные из Google Sheets...")
        response = requests.get(sheets_url, allow_redirects=True)
        response.raise_for_status()
        
        # Парсим TSV данные
        tsv_data = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(tsv_data), delimiter='\t')
        
        products = []
        headers = next(reader)  # Пропускаем заголовки
        
        for row in reader:
            if len(row) >= 9:
                product_id = row[0] if len(row) > 0 else ""
                section = row[1] if len(row) > 1 else ""
                title = row[2] if len(row) > 2 else ""
                price = row[3] if len(row) > 3 else ""
                desc = row[4] if len(row) > 4 else ""
                meta = row[5] if len(row) > 5 else ""
                status = row[6] if len(row) > 6 else ""
                images = row[7] if len(row) > 7 else ""
                link = row[8] if len(row) > 8 else ""
                
                # Пропускаем пустые строки
                if not title.strip():
                    continue
                
                # Обновляем цену для сумки через плечо
                if "Сумка через плечо" in price:
                    print(f"💰 Обновляем цену сумки через плечо: {price} → 4500 р.")
                    price = "4500 р."
                
                products.append({
                    "id": product_id,
                    "section": section,
                    "title": title,
                    "price": price,
                    "desc": desc,
                    "meta": meta,
                    "status": status,
                    "images": images,
                    "link": link
                })
        
        print(f"✅ Получено {len(products)} товаров из Google Sheets")
        
        # Сохраняем обновленные данные
        with open('sheets_data_updated.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        print("📁 Обновленные данные сохранены в sheets_data_updated.json")
        return products
        
    except Exception as e:
        print(f"❌ Ошибка получения данных: {e}")
        return []

if __name__ == "__main__":
    update_sheets_price()
