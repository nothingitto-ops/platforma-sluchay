// Тест форматирования цены
const priceText = '3001 р.'.replace(' р.', '').replace('р', '');
const formattedPrice = priceText.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ₽';

console.log('Исходная цена:', '3001 р.');
console.log('После replace:', priceText);
console.log('Форматированная:', formattedPrice);

// Тест с разными вариантами
const testPrices = ['3000 р.', '3001 р.', '3500 р.', '10000 р.'];
testPrices.forEach(price => {
  const clean = price.replace(' р.', '').replace('р', '');
  const formatted = clean.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ₽';
  console.log(`${price} -> ${formatted}`);
});
