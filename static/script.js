// Initialize the cart object
let cart = {};

// Fetch products from server
async function fetchProducts() {
    try {
        const response = await fetch('/products', {method: 'GET'});
        const products = await response.json();
        
        const productContainer = document.getElementById('products');
        productContainer.innerHTML = '';
        
        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.classList.add('product-card');
            
            const truncatedDescription = product.description.length > 100
                ? product.description.slice(0, 100) + '...'
                : product.description;

            productCard.innerHTML = `
                <img src="${product.image}" alt="${product.name}">
                <h3>${product.name}</h3>
                <p class="price">$${product.price}</p>
                <p class="description">${truncatedDescription}</p>
                <button class="add-to-cart" onclick="addToCart('${product._id}')">Add to Cart</button>
            `;
            
            productContainer.appendChild(productCard);
        });
    } catch (error) {
        console.error('Error fetching products:', error);
    }
}

// Add product to cart
function addToCart(productId) {
    // Check if product is already in the cart
    if (cart[productId]) {
        cart[productId].quantity += 1;  // If it is, increment quantity
    } else {
        cart[productId] = { quantity: 1 };  // Otherwise, add it to the cart
    }
    
    // Update cart count
    updateCartCount();
}

// Update the cart icon and the cart count
function updateCartCount() {
    const cartCount = Object.values(cart).reduce((total, product) => total + product.quantity, 0);
    document.getElementById('cartCount').textContent = cartCount;
}

// Fetch products on page load
fetchProducts();