// Cache busting script
// Version: 2025-08-14-00-45
console.log('Cache busted at:', new Date().toISOString());

// Force reload of products.json with cache busting
function loadProductsWithCacheBust() {
    const timestamp = new Date().getTime();
    return fetch(`products.json?v=${timestamp}`)
        .then(response => response.json())
        .then(data => {
            console.log('Products loaded with cache bust:', data);
            return data;
        });
}

// Export for use in other scripts
window.loadProductsWithCacheBust = loadProductsWithCacheBust;
