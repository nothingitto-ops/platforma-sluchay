// Упрощенная версия для тестирования
const items = [
  {
    "images": ["product_2/product_2_1.jpg"],
    "title": "Пояс-юбка",
    "price": "3000 р.",
    "desc": "Пояс, который имеет функцию мешка",
    "meta": "Состав: 50% хлопок 50% лён",
    "link": "https://t.me/stub123",
    "status": "stock",
    "order": 2,
    "section": "home"
  },
  {
    "images": ["product_3/product_3_1.jpg"],
    "title": "Пояс P1",
    "price": "3500 р.",
    "desc": "Пояс, который имеет функцию мешка",
    "meta": "Состав: 100% хлопок (цвет на выбор)",
    "link": "https://t.me/stub123",
    "status": "stock",
    "order": 3,
    "section": "home"
  }
];

const $catalog = document.getElementById('catalog');
let currentTab = 'home';
let activeFilter = 'all';

function renderCollection(arr) {
  if(!$catalog) return;
  
  $catalog.innerHTML = '';
  
  arr.forEach(it => {
    const card = document.createElement('div');
    card.className = 'card';
    
    const imgBox = document.createElement('div');
    imgBox.className = 'card-img';
    
    const img = document.createElement('img');
    img.src = 'img/' + it.images[0];
    img.alt = it.title;
    imgBox.appendChild(img);
    card.appendChild(imgBox);
    
    const h3 = document.createElement('h3');
    h3.textContent = it.title;
    card.appendChild(h3);
    
    const price = document.createElement('div');
    price.className = 'price';
    price.textContent = it.price;
    card.appendChild(price);
    
    $catalog.appendChild(card);
  });
}

function renderActive() {
  const arr = items.filter(item => item.section === currentTab);
  const src = arr.filter(it => activeFilter === 'all' ? true : it.status === activeFilter);
  
  renderCollection(src);
  $catalog.style.display = 'grid';
  $catalog.style.visibility = 'visible';
  $catalog.style.opacity = '1';
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM загружен');
  console.log('Товары:', items);
  console.log('Каталог:', $catalog);
  
  renderActive();
});
