#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
from datetime import datetime

def clean_filename(name):
    """Очистка имени файла"""
    return re.sub(r'[^a-zA-Z0-9а-яА-Я]', '-', name.lower()).strip('-')

def update_from_sheets():
    """Обновление данных сайта из Google Sheets"""
    
    print("🔄 Запуск обновления данных из Google Sheets...")
    
    # Загружаем данные из Google Sheets
    try:
        with open('sheets_data.json', 'r', encoding='utf-8') as f:
            sheets_data = json.load(f)
        print(f"✅ Загружено {len(sheets_data)} товаров из Google Sheets")
    except Exception as e:
        print(f"❌ Ошибка загрузки данных Google Sheets: {e}")
        return False
    
    # Создаем правильную структуру данных для сайта
    updated_items = []
    
    for sheet_product in sheets_data:
        # Извлекаем правильные данные из Google Sheets
        product_id = sheet_product.get('id', '')
        section = sheet_product.get('section', '')
        title = sheet_product.get('title', '')
        price = sheet_product.get('price', '')
        desc = sheet_product.get('desc', '')
        meta = sheet_product.get('meta', '')
        status = sheet_product.get('status', '')
        images = sheet_product.get('images', '')
        link = sheet_product.get('link', '')
        
        # Определяем порядок на основе ID
        try:
            order = int(product_id) if product_id.isdigit() else 999
        except:
            order = 999
        
        # Определяем раздел (home или nessffo)
        section_name = 'home'
        if 'цветочный' in title.lower() or 'сумка' in title.lower():
            section_name = 'nessffo'
        
        # Создаем правильную структуру товара
        item = {
            "images": images.split(',') if images else [],
            "title": title,
            "price": price,
            "desc": desc,
            "meta": meta,
            "link": link,
            "status": status,
            "order": order
        }
        
        updated_items.append(item)
        print(f"✅ Обработан товар: {title} - {price}")
    
    # Сортируем по порядку
    updated_items.sort(key=lambda x: x.get('order', 999))
    
    # Создаем JavaScript код для app.min.js
    js_content = f"""// Автоматически обновлено из Google Sheets
// Время обновления: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

// Глобальные переменные
let currentTab = (location.hash.replace('#','')==='nessffo') ? 'nessffo' : 'home';
let activeFilter = 'all';
let heroReady = false;

// Данные товаров из Google Sheets
const items = {json.dumps(updated_items, ensure_ascii=False, indent=2)};

// Функции для обработки свайпов
let startX = 0;
let startY = 0;
let currentX = 0;
let currentY = 0;
let isDragging = false;
let sheetElement = null; // минимальное расстояние для свайпа

function applyNavScroll(){{ 
  if($topnav) {{
    if(window.scrollY>8) $topnav.classList.add('scrolled'); 
    else $topnav.classList.remove('scrolled'); 
  }}
}}
window.addEventListener('scroll', applyNavScroll, {passive:true});
applyNavScroll();

// Функции для модального окна
const $modal = document.getElementById('modal');
const $viewer = document.getElementById('viewer');
const $viewerImg = document.getElementById('viewerImg');
const $zoomBtn = document.getElementById('zoomBtn');
const $catalog = document.getElementById('catalog');
const $carePanel = document.getElementById('carePanel');

if($modal) $modal.addEventListener('click',closeModal);
const closeBtn = document.getElementById('closeBtn');
if(closeBtn) closeBtn.addEventListener('click',closeModal);

function renderThumbs(arr){
  if(!$viewer) return;
  const dots = $viewer.querySelector('.dots');
  if (dots) dots.remove();
  const dotsContainer = document.createElement('div');
  dotsContainer.className = 'dots';
  arr.forEach((_, i) => {
    const dot = document.createElement('div');
    dot.className = 'dot';
    if (i === 0) dot.classList.add('active');
    dot.addEventListener('click', () => {
      $viewerImg.src = arr[i];
      $viewer.querySelectorAll('.dot').forEach(d => d.classList.remove('active'));
      dot.classList.add('active');
    });
    dotsContainer.appendChild(dot);
  });
  $viewer.appendChild(dotsContainer);
}

function openModal(item, tab) {
  if(!$modal || !$viewerImg) return;
  $viewerImg.src = item.images[0];
  renderThumbs(item.images);
  $modal.style.display = 'flex';
  document.body.style.overflow = 'hidden';
  
  // Обновляем информацию о товаре
  const titleEl = $modal.querySelector('.modal-title');
  const priceEl = $modal.querySelector('.modal-price');
  const descEl = $modal.querySelector('.modal-desc');
  const metaEl = $modal.querySelector('.modal-meta');
  
  if(titleEl) titleEl.textContent = item.title;
  if(priceEl) priceEl.textContent = item.price;
  if(descEl) descEl.textContent = item.desc;
  if(metaEl) metaEl.textContent = item.meta;
}

function closeModal() {
  if(!$modal) return;
  $modal.style.display = 'none';
  document.body.style.overflow = 'auto';
}

// Функции для зума изображения
const SCALE=2; // коэффициент зума
const DRAG_THRESHOLD = 3; // px — чтобы клик не путался с микродвижениями

let isZoomed = false;
let dragStartX = 0;
let dragStartY = 0;
let dragOffsetX = 0;
let dragOffsetY = 0;

if($viewerImg) {
  $viewerImg.addEventListener('click', function(e) {
    if (!isZoomed) {
      enterZoom();
    } else {
      leaveZoom();
    }
  });
  
  $viewerImg.addEventListener('dblclick', function(e) {
    e.preventDefault();
    if (!isZoomed) {
      enterZoom();
    } else {
      leaveZoom();
    }
  });
}

if($viewer) {
  $viewer.addEventListener('dragstart', function(e) {
    e.preventDefault();
  });
  
  $viewer.addEventListener('pointerdown', function(e) {
    if (!isZoomed) return;
    e.preventDefault();
    dragStartX = e.clientX - dragOffsetX;
    dragStartY = e.clientY - dragOffsetY;
    $viewer.style.cursor = 'grabbing';
  });
  
  $viewer.addEventListener('pointermove', function(e) {
    if (!isZoomed) return;
    e.preventDefault();
    dragOffsetX = e.clientX - dragStartX;
    dragOffsetY = e.clientY - dragStartY;
    updateImagePosition();
  });
  
  $viewer.addEventListener('pointerup', function() {
    if (!isZoomed) return;
    $viewer.style.cursor = 'grab';
  });
}

if($zoomBtn) {
  $zoomBtn.addEventListener('click', function() {
    if (!isZoomed) {
      enterZoom();
    } else {
      leaveZoom();
    }
  });
}

function enterZoom() {
  if(!$viewerImg) return;
  isZoomed = true;
  $viewerImg.style.transform = 'scale(2)';
  $viewer.style.cursor = 'grab';
  if($zoomBtn) $zoomBtn.textContent = '🔍-';
}

function leaveZoom() {
  if(!$viewerImg) return;
  isZoomed = false;
  $viewerImg.style.transform = 'scale(1)';
  $viewer.style.cursor = 'default';
  dragOffsetX = 0;
  dragOffsetY = 0;
  updateImagePosition();
  if($zoomBtn) $zoomBtn.textContent = '🔍+';
}

function updateImagePosition() {
  if(!$viewerImg) return;
  const bounds = getBounds();
  const x = Math.max(bounds.minX, Math.min(bounds.maxX, dragOffsetX));
  const y = Math.max(bounds.minY, Math.min(bounds.maxY, dragOffsetY));
  $viewerImg.style.transform = `scale(2) translate(${x}px, ${y}px)`;
}

function getBounds() {
  if(!$viewerImg || !$viewer) return {{minX:0, maxX:0, minY:0, maxY:0}};
  const imgRect = $viewerImg.getBoundingClientRect();
  const viewerRect = $viewer.getBoundingClientRect();
  const scaledWidth = imgRect.width * SCALE;
  const scaledHeight = imgRect.height * SCALE;
  return {{
    minX: -(scaledWidth - viewerRect.width) / 2,
    maxX: (scaledWidth - viewerRect.width) / 2,
    minY: -(scaledHeight - viewerRect.height) / 2,
    maxY: (scaledHeight - viewerRect.height) / 2
  }};
}

// Кэш для разрешенных URL изображений
const RESOLVED_SRC = {{}};

// Функция для получения подсказок папок из первого изображения
function folderHintsFromFirst(src) {{
  const parts = src.split('/');
  if (parts.length >= 2) {{
    const folder = parts[0];
    const filename = parts[1];
    const nameWithoutExt = filename.split('.')[0];
    const baseName = nameWithoutExt.split('_')[0];
    return [folder, baseName, nameWithoutExt];
  }}
  return [src];
}}

// Функция для генерации кандидатов URL
function candidatesFor(src, hintFolders) {{
  const candidates = [];
  
  // Добавляем оригинальный путь
  candidates.push(src);
  
  // Добавляем варианты с подсказками
  if (hintFolders && hintFolders.length > 0) {{
    for (const hint of hintFolders) {{
      candidates.push(`img/${{hint}}/${{src.split('/').pop()}}`);
    }}
  }}
  
  // Добавляем варианты с img/ префиксом
  if (!src.startsWith('img/')) {{
    candidates.push(`img/${{src}}`);
  }}
  
  return candidates;
}}

// Функция для установки src с fallback
function setSrcWithFallback(img, src, hintFolders) {{
  // Быстрый путь: уже знаем рабочий URL — не дёргаем сеть лишний раз
  if (RESOLVED_SRC[src]) {{
    img.src = RESOLVED_SRC[src];
    return;
  }}
  
  const candidates = candidatesFor(src, hintFolders);
  
  function tryNext(index = 0) {{
    if (index >= candidates.length) {{
      // Все варианты не сработали — ставим placeholder
      img.src = 'img/item-placeholder.jpg';
      return;
    }}
    
    const candidate = candidates[index];
    const testImg = new Image();
    
    testImg.onload = function() {{
      // Успех! Сохраняем в кэш и устанавливаем
      RESOLVED_SRC[src] = candidate;
      img.src = candidate;
    }};
    
    testImg.onerror = function() {{
      // Пробуем следующий кандидат
      tryNext(index + 1);
    }};
    
    testImg.src = candidate;
  }}
  
  tryNext();
}}

// Функция для установки hero баннера
function setHero(tab) {{
  const $hero = document.querySelector('.hero');
  if (!$hero) return;
  
  if (tab === 'nessffo') {{
    $hero.src = 'img/bannerh.jpg';
  }} else {{
    $hero.src = 'img/banner.jpg';
  }}
}}

// Функция для рендера коллекции
function renderCollection(arr, instant=false) {{
  if(!$catalog) return;
  const src = arr.filter(it => !it.placeholder && (activeFilter==='all' ? true : (it.status||'stock')===activeFilter))
    .sort((a, b) => (a.order || 999) - (b.order || 999));
  
  closeModal();
  $catalog.innerHTML = '';
  
  src.forEach(it => {{
    const card = document.createElement('div');
    card.className = 'card';
    const imgBox = document.createElement('div');
    imgBox.className = 'img-box';
    const img = document.createElement('img');
    setSrcWithFallback(img, it.images[0], folderHintsFromFirst(it.images[0])); 
    img.alt = it.title; 
    img.draggable = false;
    img.addEventListener('dragstart', e => e.preventDefault());
    imgBox.appendChild(img);
    card.appendChild(imgBox);
    const h3 = document.createElement('h3');
    h3.textContent = it.title;
    card.appendChild(h3);
    // Форматируем цену для каталога
    const priceText = it.price.replace(' р.', '').replace('р', '');
    const formattedPrice = priceText.toString().replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ' ') + ' ₽';
    const price = document.createElement('div');
    price.className = 'price';
    price.textContent = formattedPrice;
    card.appendChild(price);
    if(!it.placeholder && it.status) {{ 
      const st = document.createElement('div'); 
      const cls = (it.status==='preorder')?'pre':'in'; 
      st.className = 'status '+cls; 
      st.textContent = (it.status==='preorder')?'под заказ':'в наличии'; 
      card.appendChild(st);
    }} 
    $catalog.appendChild(card);

    if(!it.placeholder) {{
      card.addEventListener('click', () => openModal(it, currentTab));
    }}
  }});
}}

// Функция для рендера активной вкладки
function renderActive(instant=false) {{
  if(!$catalog) return;
  const arr = (currentTab === 'home') ? items.filter(item => !item.title.includes('цветочный') && !item.title.includes('Сумка')) : items.filter(item => item.title.includes('цветочный') || item.title.includes('Сумка'));
  
  // Управляем кнопкой и панелью руководства
  const $careBtn = document.getElementById('careBtn');
  const showInNessffo = currentTab === 'nessffo';
  
  // Устанавливаем data-section для правильных стилей фильтров
  document.body.setAttribute('data-section', currentTab);
  
  if($careBtn) {{
    $careBtn.style.display = showInNessffo ? 'flex' : 'none';
  }}
  
  if($carePanel) {{
    // Определяем, мобильное ли устройство
    const isMobile = window.innerWidth <= 768;
    
    if(showInNessffo) {{
      if(isMobile) {{
        // На мобильных показываем памятку автоматически
        $carePanel.style.display = 'block';
      }} else {{
        // На десктопе скрываем, показываем только по клику на кнопку
        $carePanel.style.display = 'none';
      }}
    }} else {{
      // В разделе home скрываем везде
      $carePanel.style.display = 'none';
    }}
    
    // Добавляем обработчик клика для кнопки (только на десктопе)
    if(showInNessffo && !isMobile && $careBtn && !$careBtn.hasAttribute('data-click-added')) {{
      $careBtn.setAttribute('data-click-added', 'true');
      $careBtn.addEventListener('click', function() {{
        $carePanel.style.display = $carePanel.style.display === 'none' ? 'block' : 'none';
        $carePanel.classList.remove('collapsed');
      }});
    }}
    
    // Добавляем обработчик клика для сворачивания памятки
    if(showInNessffo && !$carePanel.hasAttribute('data-click-added')) {{
      $carePanel.setAttribute('data-click-added', 'true');
      $carePanel.addEventListener('click', function(e) {{
        // Сворачиваем/разворачиваем при клике на заголовок или саму панель, но не на элементы списка
        if(e.target.tagName === 'H4' || e.target.closest('h4') || (e.target === this && !e.target.closest('ul')) ) {{
          $carePanel.classList.toggle('collapsed');
        }}
      }});
    }}
  }}
  
  renderCollection(arr, instant);
  // показать сетку (если до этого был скелетон)
  $catalog.style.display = 'grid';
  // Не перезаписываем visibility и opacity, если это не instant рендер
  if(instant) {{
    $catalog.style.visibility = 'visible';
    $catalog.style.opacity = '1';
  }}
  // обновить баннер для вкладки
  setHero(currentTab);
}}

// Инициализация вкладок и фильтров
(function tabs() {{
  const tabs = document.querySelectorAll('.topnav .tab');
  const filterBtns = document.querySelectorAll('#filters .fbtn');
  const filterByTab = {{ home: 'all', nessffo: 'all' }}; // дефолт на вкладку

  function setFilter(f) {{
    activeFilter = f;
    filterByTab[currentTab] = f;
    filterBtns.forEach(b => b.classList.toggle('active', b.dataset.filter === f));
  }}

  function activate(tab) {{
    tabs.forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
  }}

  function switchTab(tab) {{
    currentTab = tab;
    activate(tab);
    setFilter(filterByTab[tab] || 'all');
    renderActive(true);
  }}

  // Обработчики для вкладок
  tabs.forEach(tab => {{
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  }});

  // Обработчики для фильтров
  filterBtns.forEach(btn => {{
    btn.addEventListener('click', () => setFilter(btn.dataset.filter));
  }});

  // Инициализация
  switchTab(currentTab);
  renderActive(true);
}})();

// Инициализация каталога при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {{
  if($catalog) {{
    $catalog.style.display = 'grid';
    $catalog.style.visibility = 'visible';
    $catalog.style.opacity = '1';
  }}
}});
"""
    
    # Сохраняем обновленный app.min.js
    try:
        with open('../web/app.min.js', 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Файл app.min.js обновлен с {len(updated_items)} товарами")
    except Exception as e:
        print(f"❌ Ошибка сохранения app.min.js: {e}")
        return False
    
    # Создаем резервную копию
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'../backups/site_backup_{timestamp}'
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        import shutil
        shutil.copy2('../web/app.min.js', f'{backup_dir}/app.min.js')
        shutil.copy2('../web/index.html', f'{backup_dir}/index.html')
        shutil.copy2('../web/styles.min.css', f'{backup_dir}/styles.min.css')
        print(f"✅ Резервная копия создана: {backup_dir}")
    except Exception as e:
        print(f"⚠️ Ошибка создания резервной копии: {e}")
    
    print(f"\n🎉 Обновление завершено!")
    print(f"📊 Статистика:")
    print(f"   - Товаров обновлено: {len(updated_items)}")
    print(f"   - Время обновления: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

if __name__ == "__main__":
    update_from_sheets()
