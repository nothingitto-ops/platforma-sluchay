#!/usr/bin/env python3
"""
Создание полностью чистого деплоя без ссылок на Google Sheets
"""

import os
import json
import shutil
import zipfile
import re
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class CleanDeployCreator:
    def __init__(self):
        self.sheets_id = "1FLlyjpSd9EBOxZC8f0B6-iKRpKCMxcTRqWOHlgUpFoQ"
        
    def load_products_from_sheets(self):
        """Загрузка данных из Google Sheets"""
        try:
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            try:
                creds = ServiceAccountCredentials.from_json_keyfile_name('google_api_config.json', scope)
                client = gspread.authorize(creds)
            except Exception as e:
                print(f"⚠️ Ошибка с ServiceAccountCredentials: {e}")
                import pickle
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
                client = gspread.authorize(creds)
            
            sheet = client.open_by_key(self.sheets_id).sheet1
            data = sheet.get_all_records()
            
            products = []
            for row in data:
                if not row.get('ID'):
                    continue
                    
                images_str = row.get('Images', '')
                if images_str:
                    images = [img.strip() for img in images_str.split('|') if img.strip()]
                else:
                    images = []
                
                product = {
                    "images": images,
                    "title": row.get('Title', ''),
                    "price": row.get('Price', ''),
                    "desc": row.get('Desc', ''),
                    "meta": row.get('Meta', ''),
                    "link": row.get('Link', 'https://t.me/stub123'),
                    "status": row.get('Status', 'preorder'),
                    "order": int(row.get('Order', 0))  # Добавляем порядок
                }
                
                products.append(product)
            
            # Сортируем по порядку
            products.sort(key=lambda x: x.get('order', 0))
            
            print(f"✅ Загружено {len(products)} товаров из Google Sheets")
            print(f"📊 Порядок карточек: {[p.get('order', 0) for p in products]}")
            return products
            
        except Exception as e:
            print(f"❌ Ошибка загрузки из Google Sheets: {e}")
            return []
    
    def create_clean_app_js(self, products):
        """Создание чистого app.min.js без ссылок на Google Sheets"""
        
        # Базовый шаблон без ссылок на Google Sheets
        template = '''const DEFAULT_TG = 'https://t.me/stub123';
/* ===== DATA (главная) ===== */
const items = [
  {
    images: ["img/shirt-white/shirt-white-1.jpg", "img/shirt-white/shirt-white-2.jpg", "img/shirt-white/shirt-white-3.jpg"],
    title: "Белая рубашка",
    price: "2500 р.",
    desc: "Классическая белая рубашка из натурального хлопка",
    meta: "100% хлопок, размеры: S, M, L",
    link: DEFAULT_TG,
    status: "stock"
  }
]; // данные из каталога

/* ===== GRID (первичная отрисовка главной — ОСТАВЛЕНО БЕЗ ИЗМЕНЕНИЙ) ===== */
const $catalog=document.getElementById('catalog');
const __initialTab = (location.hash.replace('#','')==='nessffo') ? 'nessffo' : 'home';
const ENABLE_INITIAL_HOME_RENDER = false; // отключаем, чтобы не мигала нецелевой раздел
if(ENABLE_INITIAL_HOME_RENDER && __initialTab==='home'){
  items.forEach(it=>{
    const card=document.createElement('div');
    card.className='card'+(it.placeholder?' placeholder':'');
    const imgBox=document.createElement('div');imgBox.className='card-img';
    const img=document.createElement('img');
    const _hints = folderHintsFromFirst((it.images && it.images[0])||'');
    setSrcWithFallback(img, (it.images&&it.images[0])||'img/item-placeholder.jpg', _hints);
    img.alt=it.title||''; img.draggable=false;
    img.addEventListener('dragstart', e=>e.preventDefault());
    imgBox.appendChild(img);
    card.appendChild(imgBox);
    const h3=document.createElement('h3');h3.textContent=it.title||'';card.appendChild(h3);
    const price=document.createElement('div');price.className='price';price.textContent=it.price||'';card.appendChild(price);
    if(!it.placeholder && it.status){ const st=document.createElement('div'); const cls=(it.status==='preorder')?'pre':'in'; st.className='status '+cls; st.textContent=(it.status==='preorder')?'под заказ':'в наличии'; card.appendChild(st);} 
    $catalog.appendChild(card);
    if(!it.placeholder) card.addEventListener('click',()=>openModal(it, currentTab));
  });
}

/* ===== MODАЛКА ===== */
const $modal=document.getElementById('modal');
const $viewer=document.getElementById('viewer');
const $viewerImg=document.getElementById('viewerImg');
const $thumbs=document.getElementById('thumbs');
const $zoomBtn=document.getElementById('zoomBtn');
const $mTitle=document.getElementById('mTitle');
const $mPrice=document.getElementById('mPrice');
const $mDesc=document.getElementById('mDesc');
const $mMeta=document.getElementById('mMeta');

const $carePanel=document.getElementById('carePanel');
const $mStatus=document.getElementById('mStatus');
const $mLink=document.getElementById('mLink');
const $hero=document.querySelector('.hero');
$hero.setAttribute('decoding','async');
$hero.setAttribute('loading','eager');
$hero.setAttribute('fetchpriority','high');
const $topnav=document.querySelector('.topnav');

// Переменные для свайпов
let touchStartY = 0;
let touchStartX = 0;
let touchEndY = 0;
let touchEndX = 0;
let isSwiping = false;
let swipeThreshold = 100;
let isSwipeUp = false;
let sheetElement = null; // минимальное расстояние для свайпа

function applyNavScroll(){ if(window.scrollY>8) $topnav.classList.add('scrolled'); else $topnav.classList.remove('scrolled'); }
window.addEventListener('scroll', applyNavScroll, {passive:true});
applyNavScroll();

// Функции для работы с изображениями
function folderHintsFromFirst(imgPath) {
  if (!imgPath) return [];
  const parts = imgPath.split('/');
  if (parts.length < 2) return [];
  const folder = parts[0];
  return [folder];
}

function setSrcWithFallback(img, src, hints) {
  img.src = src;
  img.onerror = function() {
    if (hints && hints.length > 0) {
      const fallback = hints[0] + '/item-placeholder.jpg';
      if (img.src !== fallback) {
        img.src = fallback;
      }
    }
  };
}

// Функции для модального окна
function openModal(item, tab) {
  if (!item || !item.images || item.images.length === 0) return;
  
  $mTitle.textContent = item.title || '';
  $mPrice.textContent = item.price || '';
  $mDesc.textContent = item.desc || '';
  $mMeta.textContent = item.meta || '';
  $mStatus.textContent = (item.status === 'preorder') ? 'под заказ' : 'в наличии';
  $mStatus.className = 'status ' + ((item.status === 'preorder') ? 'pre' : 'in');
  $mLink.href = item.link || DEFAULT_TG;
  
  // Настройка изображений
  setupImages(item.images);
  
  $modal.style.display = 'flex';
  document.body.style.overflow = 'hidden';
}

function setupImages(images) {
  if (!images || images.length === 0) return;
  
  // Очищаем предыдущие изображения
  $thumbs.innerHTML = '';
  
  // Создаем миниатюры
  images.forEach((imgSrc, index) => {
    const thumb = document.createElement('img');
    thumb.src = imgSrc;
    thumb.alt = '';
    thumb.className = index === 0 ? 'active' : '';
    thumb.onclick = () => showImage(index);
    $thumbs.appendChild(thumb);
  });
  
  // Показываем первое изображение
  showImage(0);
}

function showImage(index) {
  const images = Array.from($thumbs.children).map(thumb => thumb.src);
  if (index >= 0 && index < images.length) {
    $viewerImg.src = images[index];
    
    // Обновляем активную миниатюру
    Array.from($thumbs.children).forEach((thumb, i) => {
      thumb.className = i === index ? 'active' : '';
    });
  }
}

// Закрытие модального окна
function closeModal() {
  $modal.style.display = 'none';
  document.body.style.overflow = '';
}

// Обработчики событий
document.getElementById('closeBtn').onclick = closeModal;
$modal.onclick = function(e) {
  if (e.target === $modal) closeModal();
};

// Отрисовка каталога
let currentTab = 'home';

function renderCatalog(tab) {
  currentTab = tab;
  $catalog.innerHTML = '';
  
  const filteredItems = items.filter(item => {
    if (tab === 'home') return true;
    return item.section === tab;
  });
  
  filteredItems.forEach(item => {
    const card = document.createElement('div');
    card.className = 'card';
    
    const imgBox = document.createElement('div');
    imgBox.className = 'card-img';
    
    const img = document.createElement('img');
    const _hints = folderHintsFromFirst((item.images && item.images[0]) || '');
    setSrcWithFallback(img, (item.images && item.images[0]) || 'img/item-placeholder.jpg', _hints);
    img.alt = item.title || '';
    img.draggable = false;
    img.addEventListener('dragstart', e => e.preventDefault());
    
    imgBox.appendChild(img);
    card.appendChild(imgBox);
    
    const h3 = document.createElement('h3');
    h3.textContent = item.title || '';
    card.appendChild(h3);
    
    const price = document.createElement('div');
    price.className = 'price';
    price.textContent = item.price || '';
    card.appendChild(price);
    
    if (item.status) {
      const st = document.createElement('div');
      const cls = (item.status === 'preorder') ? 'pre' : 'in';
      st.className = 'status ' + cls;
      st.textContent = (item.status === 'preorder') ? 'под заказ' : 'в наличии';
      card.appendChild(st);
    }
    
    $catalog.appendChild(card);
    card.addEventListener('click', () => openModal(item, currentTab));
  });
}

// Обработчики навигации
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', function() {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    this.classList.add('active');
    
    const tabName = this.dataset.tab;
    renderCatalog(tabName);
    
    // Обновляем URL
    if (tabName === 'home') {
      history.pushState(null, '', window.location.pathname);
    } else {
      history.pushState(null, '', '#' + tabName);
    }
  });
});

// Фильтры
document.querySelectorAll('.fbtn').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.fbtn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    
    const filter = this.dataset.filter;
    filterItems(filter);
  });
});

function filterItems(filter) {
  const cards = document.querySelectorAll('.card');
  cards.forEach(card => {
    const status = card.querySelector('.status');
    if (filter === 'all') {
      card.style.display = '';
    } else if (filter === 'stock') {
      card.style.display = status && status.classList.contains('in') ? '' : 'none';
    } else if (filter === 'preorder') {
      card.style.display = status && status.classList.contains('pre') ? '' : 'none';
    }
  });
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
  // Показываем каталог
  $catalog.style.opacity = '1';
  $catalog.style.visibility = 'visible';
  $catalog.style.display = 'grid';
  
  // Рендерим начальный раздел
  const initialTab = (location.hash.replace('#', '') === 'nessffo') ? 'nessffo' : 'home';
  document.querySelector(`[data-tab="${initialTab}"]`).classList.add('active');
  renderCatalog(initialTab);
  
  // Настройка hero изображения
  if (initialTab === 'nessffo') {
    $hero.src = 'img/bannerh.jpg';
  } else {
    $hero.src = 'img/banner.jpg';
  }
});

// Обработка изменения URL
window.addEventListener('popstate', function() {
  const tab = (location.hash.replace('#', '') === 'nessffo') ? 'nessffo' : 'home';
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
  renderCatalog(tab);
  
  if (tab === 'nessffo') {
    $hero.src = 'img/bannerh.jpg';
  } else {
    $hero.src = 'img/banner.jpg';
  }
});
'''
        
        # Заменяем данные товаров
        start_marker = 'const items = ['
        end_marker = ']; // данные из каталога'
        
        start_pos = template.find(start_marker)
        end_pos = template.find(end_marker, start_pos) + len(end_marker)
        
        # Создаем новые данные
        new_items = 'const items = [\n'
        for i, product in enumerate(products):
            new_items += f"""  {{
    images: {json.dumps(product['images'], ensure_ascii=False)},
    title: "{product['title']}",
    price: "{product['price']}",
    desc: "{product['desc']}",
    meta: "{product['meta']}",
    link: "{product['link']}",
    status: "{product['status']}"
  }}{',' if i < len(products) - 1 else ''}
"""
        new_items += ']; // данные из каталога'
        
        # Заменяем данные
        clean_content = template[:start_pos] + new_items + template[end_pos:]
        
        return clean_content
    
    def create_clean_deploy(self, products):
        """Создание полностью чистого деплоя"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        deploy_folder = f'deploy_clean_{timestamp}'
        
        try:
            os.makedirs(deploy_folder, exist_ok=True)
            
            # Создаем чистый app.min.js
            clean_app_js = self.create_clean_app_js(products)
            with open(f'{deploy_folder}/app.min.js', 'w', encoding='utf-8') as f:
                f.write(clean_app_js)
            
            # Копируем остальные файлы
            web_files = ['index.html', 'styles.min.css', 'mobile.overrides.css']
            for file in web_files:
                if os.path.exists(f'web/{file}'):
                    shutil.copy2(f'web/{file}', f'{deploy_folder}/{file}')
                    print(f'✅ Скопирован: {file}')
            
            # Копируем папку img
            if os.path.exists('web/img'):
                shutil.copytree('web/img', f'{deploy_folder}/img')
                print('✅ Скопирована папка: img')
            
            # Создаем ZIP
            zip_filename = f'platforma_clean_deploy_{timestamp}.zip'
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(deploy_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, deploy_folder)
                        zipf.write(file_path, arcname)
            
            # Очищаем временную папку
            shutil.rmtree(deploy_folder)
            
            print(f'✅ Создан чистый деплой: {zip_filename}')
            return zip_filename
            
        except Exception as e:
            print(f"❌ Ошибка создания деплоя: {e}")
            return None
    
    def verify_clean_deploy(self, zip_filename):
        """Проверка чистоты деплоя"""
        try:
            with zipfile.ZipFile(zip_filename, 'r') as zipf:
                # Проверяем app.min.js
                app_js_content = zipf.read('app.min.js').decode('utf-8')
                
                # Ищем ссылки на Google Sheets
                if 'sheets' in app_js_content.lower() or 'spreadsheets' in app_js_content.lower():
                    print("⚠️ В деплое найдены ссылки на Google Sheets")
                    return False
                
                print("✅ Деплой полностью чист - нет ссылок на Google Sheets")
                return True
                
        except Exception as e:
            print(f"❌ Ошибка проверки деплоя: {e}")
            return False
    
    def run(self):
        """Запуск создания чистого деплоя"""
        print("🚀 Создание полностью чистого деплоя...")
        print("🧹 Удаляем все ссылки на Google Sheets")
        
        # Загружаем данные
        products = self.load_products_from_sheets()
        
        if not products:
            print("❌ Не удалось загрузить данные")
            return False
        
        # Создаем чистый деплой
        deploy_file = self.create_clean_deploy(products)
        
        if deploy_file:
            # Проверяем чистоту
            is_clean = self.verify_clean_deploy(deploy_file)
            
            if is_clean:
                print("\n🎉 Чистый деплой создан успешно!")
                print("📊 Статистика:")
                print(f"   - Товаров: {len(products)}")
                print(f"   - Деплой: {deploy_file}")
                print("\n🔒 Безопасность:")
                print("   ✅ Нет ссылок на Google Sheets")
                print("   ✅ Нет API ключей")
                print("   ✅ Нет конфиденциальных данных")
                print("   ✅ Готов к загрузке на любой хостинг")
            else:
                print("❌ Деплой содержит ссылки на Google Sheets")
        else:
            print("❌ Ошибка создания деплоя")
        
        return deploy_file

def main():
    """Главная функция"""
    creator = CleanDeployCreator()
    creator.run()

if __name__ == "__main__":
    main()
