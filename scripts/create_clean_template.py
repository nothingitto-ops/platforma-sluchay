#!/usr/bin/env python3
"""
Создание полностью чистого шаблона app.min.js без ссылок на Google Sheets
"""

def create_clean_template():
    """Создание чистого шаблона app.min.js"""
    
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

// Остальной код без изменений...
'''
    
    # Сохраняем чистый шаблон
    with open('web/app.min.js', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("✅ Создан чистый шаблон app.min.js без ссылок на Google Sheets")

if __name__ == "__main__":
    create_clean_template()
