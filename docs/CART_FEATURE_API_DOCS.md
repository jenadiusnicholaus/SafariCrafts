# Shopping Cart Feature API Documentation

## Overview
The shopping cart feature allows authenticated users to add, remove, update artwork items and manage their shopping cart. This document provides complete integration guidance for frontend developers.

## API Endpoints

### 1. Get Current User's Cart
**Endpoint:** `GET /api/v1/catalog/cart/`

**Purpose:** Retrieve the current user's shopping cart with all items

**Authentication:** Required (JWT Bearer Token)

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
```

**Response Example:**
```json
{
    "id": 1,
    "currency": "TZS",
    "items": [
        {
            "id": 15,
            "artwork": {
                "id": "4fc3ff2e-eb37-4d3a-8274-ebb9fa216fb6",
                "title": "Ceremonial Bracelet Set",
                "slug": "ceremonial-bracelet-set-fatuma-maasai",
                "artist_name": "Fatuma Maasai",
                "category_name": "Jewelry",
                "price": "120000.00",
                "currency": "TZS",
                "main_image": {
                    "id": 1,
                    "kind": "image",
                    "file": "http://127.0.0.1:8082/media/artwork_media/image.jpg",
                    "thumbnail": "http://127.0.0.1:8082/media/artwork_thumbnails/image.jpg",
                    "alt_text": "Ceremonial bracelet",
                    "caption": "",
                    "is_primary": true,
                    "sort_order": 0,
                    "file_size": null,
                    "width": null,
                    "height": null,
                    "duration": null,
                    "created_at": "2025-08-25T02:52:28.328731+03:00"
                },
                "is_featured": false,
                "tribe": "Maasai",
                "region": "Arusha",
                "material": "Glass beads, leather, brass",
                "view_count": 0,
                "like_count": 14,
                "is_liked": true
            },
            "quantity": 2,
            "unit_price": "120000.00",
            "total_price": "240000.00",
            "snapshot": {
                "title": "Ceremonial Bracelet Set",
                "artist": "Fatuma Maasai",
                "price": "120000.00",
                "currency": "TZS",
                "image_url": "http://127.0.0.1:8082/media/artwork_media/image.jpg"
            },
            "created_at": "2025-08-27T10:30:00.000000+03:00",
            "updated_at": "2025-08-27T10:35:00.000000+03:00"
        }
    ],
    "total_amount": "240000.00",
    "total_items": 2,
    "created_at": "2025-08-27T10:30:00.000000+03:00",
    "updated_at": "2025-08-27T10:35:00.000000+03:00"
}
```

**Response - Empty Cart:**
```json
{
    "id": 1,
    "currency": "TZS",
    "items": [],
    "total_amount": "0.00",
    "total_items": 0,
    "created_at": "2025-08-27T10:30:00.000000+03:00",
    "updated_at": "2025-08-27T10:30:00.000000+03:00"
}
```

---

### 2. Add Item to Cart
**Endpoint:** `POST /api/v1/catalog/cart/items/`

**Purpose:** Add an artwork to the shopping cart

**Authentication:** Required (JWT Bearer Token)

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
    "artwork_id": "4fc3ff2e-eb37-4d3a-8274-ebb9fa216fb6",
    "quantity": 1
}
```

**Request Parameters:**
- `artwork_id` (UUID, required): The unique identifier of the artwork
- `quantity` (integer, required): Number of items to add (must be > 0)

**Response Examples:**

**Success - Item Added (201 Created):**
```json
{
    "id": 15,
    "artwork": {
        "id": "4fc3ff2e-eb37-4d3a-8274-ebb9fa216fb6",
        "title": "Ceremonial Bracelet Set",
        "slug": "ceremonial-bracelet-set-fatuma-maasai",
        "artist_name": "Fatuma Maasai",
        "category_name": "Jewelry",
        "price": "120000.00",
        "currency": "TZS",
        "main_image": {...},
        "is_featured": false,
        "tribe": "Maasai",
        "region": "Arusha",
        "material": "Glass beads, leather, brass",
        "view_count": 0,
        "like_count": 14,
        "is_liked": true
    },
    "quantity": 1,
    "unit_price": "120000.00",
    "total_price": "120000.00",
    "snapshot": {
        "title": "Ceremonial Bracelet Set",
        "artist": "Fatuma Maasai",
        "price": "120000.00",
        "currency": "TZS",
        "image_url": "http://127.0.0.1:8082/media/artwork_media/image.jpg"
    },
    "created_at": "2025-08-27T10:30:00.000000+03:00",
    "updated_at": "2025-08-27T10:30:00.000000+03:00"
}
```

**Success - Quantity Updated (if item already exists):**
```json
{
    "id": 15,
    "artwork": {...},
    "quantity": 3,
    "unit_price": "120000.00",
    "total_price": "360000.00",
    "snapshot": {...},
    "created_at": "2025-08-27T10:30:00.000000+03:00",
    "updated_at": "2025-08-27T10:35:00.000000+03:00"
}
```

**Error - Artwork Not Found (400):**
```json
{
    "artwork_id": ["Artwork not found or not available"]
}
```

**Error - Invalid Quantity (400):**
```json
{
    "quantity": ["Quantity must be greater than 0"]
}
```

**Error - Artwork Not Available (400):**
```json
{
    "artwork_id": ["This artwork is not available"]
}
```

---

### 3. Update Cart Item Quantity
**Endpoint:** `PATCH /api/v1/catalog/cart/items/{item_id}/`

**Purpose:** Update the quantity of a specific cart item

**Authentication:** Required (JWT Bearer Token)

**URL Parameters:**
- `item_id` (integer): The unique identifier of the cart item

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
    "quantity": 5
}
```

**Response Examples:**

**Success - Quantity Updated (200 OK):**
```json
{
    "id": 15,
    "artwork": {...},
    "quantity": 5,
    "unit_price": "120000.00",
    "total_price": "600000.00",
    "snapshot": {...},
    "created_at": "2025-08-27T10:30:00.000000+03:00",
    "updated_at": "2025-08-27T10:40:00.000000+03:00"
}
```

**Error - Cart Item Not Found (404):**
```json
{
    "error": "Cart item not found"
}
```

**Error - Invalid Quantity (400):**
```json
{
    "quantity": ["Quantity must be greater than 0"]
}
```

---

### 4. Remove Item from Cart
**Endpoint:** `DELETE /api/v1/catalog/cart/items/{item_id}/`

**Purpose:** Remove a specific item from the cart

**Authentication:** Required (JWT Bearer Token)

**URL Parameters:**
- `item_id` (integer): The unique identifier of the cart item

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
```

**Response Examples:**

**Success - Item Removed (200 OK):**
```json
{
    "message": "Item removed from cart"
}
```

**Error - Cart Item Not Found (404):**
```json
{
    "error": "Cart item not found"
}
```

---

### 5. Clear Entire Cart
**Endpoint:** `DELETE /api/v1/catalog/cart/`

**Purpose:** Remove all items from the cart

**Authentication:** Required (JWT Bearer Token)

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
```

**Response Example:**

**Success - Cart Cleared (200 OK):**
```json
{
    "message": "Cart cleared"
}
```

---

## Frontend Implementation Guide

### React/Next.js Implementation

#### 1. API Service Functions

```javascript
// services/cartApi.js
const API_BASE_URL = 'http://127.0.0.1:8082/api/v1';

// Get JWT token from your auth context/store
const getAuthHeaders = () => ({
  'Authorization': `Bearer ${getJWTToken()}`,
  'Content-Type': 'application/json'
});

// Get cart
export const getCart = async () => {
  const response = await fetch(`${API_BASE_URL}/catalog/cart/`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch cart');
  }
  
  return response.json();
};

// Add item to cart
export const addToCart = async (artworkId, quantity = 1) => {
  const response = await fetch(`${API_BASE_URL}/catalog/cart/items/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      artwork_id: artworkId,
      quantity: quantity
    }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to add item to cart');
  }
  
  return response.json();
};

// Update cart item quantity
export const updateCartItem = async (itemId, quantity) => {
  const response = await fetch(`${API_BASE_URL}/catalog/cart/items/${itemId}/`, {
    method: 'PATCH',
    headers: getAuthHeaders(),
    body: JSON.stringify({ quantity }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to update cart item');
  }
  
  return response.json();
};

// Remove item from cart
export const removeFromCart = async (itemId) => {
  const response = await fetch(`${API_BASE_URL}/catalog/cart/items/${itemId}/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to remove item from cart');
  }
  
  return response.json();
};

// Clear entire cart
export const clearCart = async () => {
  const response = await fetch(`${API_BASE_URL}/catalog/cart/`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to clear cart');
  }
  
  return response.json();
};

// Get cart item count
export const getCartItemCount = async () => {
  try {
    const cart = await getCart();
    return cart.total_items;
  } catch (error) {
    return 0;
  }
};
```

#### 2. React Context for Cart State Management

```javascript
// contexts/CartContext.jsx
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { getCart, addToCart, updateCartItem, removeFromCart, clearCart } from '../services/cartApi';
import { useAuth } from './AuthContext';

// Cart reducer
const cartReducer = (state, action) => {
  switch (action.type) {
    case 'SET_CART':
      return {
        ...state,
        ...action.payload,
        loading: false,
        error: null,
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        loading: false,
      };
    
    case 'ADD_ITEM':
      const existingItemIndex = state.items.findIndex(
        item => item.artwork.id === action.payload.artwork.id
      );
      
      if (existingItemIndex > -1) {
        const updatedItems = [...state.items];
        updatedItems[existingItemIndex] = action.payload;
        return {
          ...state,
          items: updatedItems,
          total_items: updatedItems.reduce((sum, item) => sum + item.quantity, 0),
          total_amount: updatedItems.reduce((sum, item) => sum + parseFloat(item.total_price), 0).toFixed(2),
        };
      } else {
        const newItems = [...state.items, action.payload];
        return {
          ...state,
          items: newItems,
          total_items: newItems.reduce((sum, item) => sum + item.quantity, 0),
          total_amount: newItems.reduce((sum, item) => sum + parseFloat(item.total_price), 0).toFixed(2),
        };
      }
    
    case 'UPDATE_ITEM':
      const updatedItems = state.items.map(item =>
        item.id === action.payload.id ? action.payload : item
      );
      return {
        ...state,
        items: updatedItems,
        total_items: updatedItems.reduce((sum, item) => sum + item.quantity, 0),
        total_amount: updatedItems.reduce((sum, item) => sum + parseFloat(item.total_price), 0).toFixed(2),
      };
    
    case 'REMOVE_ITEM':
      const filteredItems = state.items.filter(item => item.id !== action.payload);
      return {
        ...state,
        items: filteredItems,
        total_items: filteredItems.reduce((sum, item) => sum + item.quantity, 0),
        total_amount: filteredItems.reduce((sum, item) => sum + parseFloat(item.total_price), 0).toFixed(2),
      };
    
    case 'CLEAR_CART':
      return {
        ...state,
        items: [],
        total_items: 0,
        total_amount: '0.00',
      };
    
    default:
      return state;
  }
};

// Initial state
const initialState = {
  id: null,
  currency: 'TZS',
  items: [],
  total_amount: '0.00',
  total_items: 0,
  loading: false,
  error: null,
};

// Context
const CartContext = createContext();

// Provider component
export const CartProvider = ({ children }) => {
  const [cart, dispatch] = useReducer(cartReducer, initialState);
  const { isAuthenticated } = useAuth();

  // Load cart on mount and auth change
  useEffect(() => {
    if (isAuthenticated) {
      loadCart();
    } else {
      dispatch({ type: 'CLEAR_CART' });
    }
  }, [isAuthenticated]);

  const loadCart = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const cartData = await getCart();
      dispatch({ type: 'SET_CART', payload: cartData });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    }
  };

  const addItem = async (artworkId, quantity = 1) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const item = await addToCart(artworkId, quantity);
      dispatch({ type: 'ADD_ITEM', payload: item });
      return item;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const updateItem = async (itemId, quantity) => {
    try {
      const updatedItem = await updateCartItem(itemId, quantity);
      dispatch({ type: 'UPDATE_ITEM', payload: updatedItem });
      return updatedItem;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const removeItem = async (itemId) => {
    try {
      await removeFromCart(itemId);
      dispatch({ type: 'REMOVE_ITEM', payload: itemId });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const clearCartItems = async () => {
    try {
      await clearCart();
      dispatch({ type: 'CLEAR_CART' });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const value = {
    cart,
    loadCart,
    addItem,
    updateItem,
    removeItem,
    clearCart: clearCartItems,
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

// Hook to use cart context
export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};
```

#### 3. Add to Cart Button Component

```javascript
// components/AddToCartButton.jsx
import React, { useState } from 'react';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';

const AddToCartButton = ({ 
  artwork, 
  quantity = 1, 
  className = "",
  children = "Add to Cart",
  showQuantitySelector = false 
}) => {
  const [localQuantity, setLocalQuantity] = useState(quantity);
  const [loading, setLoading] = useState(false);
  const { addItem } = useCart();
  const { isAuthenticated, showLoginModal } = useAuth();

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      showLoginModal();
      return;
    }

    try {
      setLoading(true);
      await addItem(artwork.id, localQuantity);
      // Show success message
      toast.success(`${artwork.title} added to cart!`);
    } catch (error) {
      toast.error(error.message || 'Failed to add item to cart');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`add-to-cart-container ${className}`}>
      {showQuantitySelector && (
        <div className="quantity-selector">
          <label htmlFor="quantity">Qty:</label>
          <select
            id="quantity"
            value={localQuantity}
            onChange={(e) => setLocalQuantity(Number(e.target.value))}
            disabled={loading}
          >
            {[1, 2, 3, 4, 5].map(num => (
              <option key={num} value={num}>{num}</option>
            ))}
          </select>
        </div>
      )}
      
      <button
        onClick={handleAddToCart}
        disabled={loading || !artwork.is_available}
        className={`add-to-cart-btn ${loading ? 'loading' : ''}`}
      >
        {loading ? (
          <span className="loading-spinner">Adding...</span>
        ) : (
          children
        )}
      </button>
    </div>
  );
};

export default AddToCartButton;
```

#### 4. Cart Icon with Badge Component

```javascript
// components/CartIcon.jsx
import React from 'react';
import { useCart } from '../contexts/CartContext';
import { Link } from 'react-router-dom';

const CartIcon = ({ className = "" }) => {
  const { cart } = useCart();

  return (
    <Link to="/cart" className={`cart-icon ${className}`}>
      <div className="cart-icon-container">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path d="M7 18c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12L8.1 13h7.45c.75 0 1.41-.41 1.75-1.03L21.7 4H5.21l-.94-2H1zm16 16c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
        </svg>
        
        {cart.total_items > 0 && (
          <span className="cart-badge">
            {cart.total_items > 99 ? '99+' : cart.total_items}
          </span>
        )}
      </div>
    </Link>
  );
};

export default CartIcon;
```

#### 5. Cart Item Component

```javascript
// components/CartItem.jsx
import React, { useState } from 'react';
import { useCart } from '../contexts/CartContext';

const CartItem = ({ item }) => {
  const [isUpdating, setIsUpdating] = useState(false);
  const { updateItem, removeItem } = useCart();

  const handleQuantityChange = async (newQuantity) => {
    if (newQuantity === item.quantity) return;
    
    try {
      setIsUpdating(true);
      await updateItem(item.id, newQuantity);
    } catch (error) {
      toast.error('Failed to update quantity');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleRemove = async () => {
    if (window.confirm('Remove this item from cart?')) {
      try {
        await removeItem(item.id);
        toast.success('Item removed from cart');
      } catch (error) {
        toast.error('Failed to remove item');
      }
    }
  };

  return (
    <div className="cart-item">
      <div className="cart-item-image">
        <img 
          src={item.artwork.main_image?.file || '/placeholder.jpg'} 
          alt={item.artwork.title}
        />
      </div>
      
      <div className="cart-item-details">
        <h3 className="item-title">{item.artwork.title}</h3>
        <p className="item-artist">by {item.artwork.artist_name}</p>
        <p className="item-price">{item.unit_price} {item.artwork.currency}</p>
        
        <div className="quantity-controls">
          <label htmlFor={`qty-${item.id}`}>Quantity:</label>
          <select
            id={`qty-${item.id}`}
            value={item.quantity}
            onChange={(e) => handleQuantityChange(Number(e.target.value))}
            disabled={isUpdating}
          >
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
              <option key={num} value={num}>{num}</option>
            ))}
          </select>
        </div>
      </div>
      
      <div className="cart-item-actions">
        <div className="item-total">
          Total: {item.total_price} {item.artwork.currency}
        </div>
        <button 
          onClick={handleRemove}
          className="remove-btn"
          aria-label="Remove item"
        >
          Remove
        </button>
      </div>
    </div>
  );
};

export default CartItem;
```

#### 6. Full Cart Page Component

```javascript
// pages/CartPage.jsx
import React from 'react';
import { useCart } from '../contexts/CartContext';
import { Link } from 'react-router-dom';
import CartItem from '../components/CartItem';

const CartPage = () => {
  const { cart, clearCart, loading } = useCart();

  const handleClearCart = async () => {
    if (window.confirm('Are you sure you want to clear your cart?')) {
      try {
        await clearCart();
        toast.success('Cart cleared');
      } catch (error) {
        toast.error('Failed to clear cart');
      }
    }
  };

  if (loading) {
    return (
      <div className="cart-loading">
        <div className="loading-spinner">Loading your cart...</div>
      </div>
    );
  }

  if (cart.items.length === 0) {
    return (
      <div className="empty-cart">
        <div className="empty-cart-content">
          <h2>Your cart is empty</h2>
          <p>Discover amazing artworks and add them to your cart!</p>
          <Link to="/artworks" className="browse-artworks-btn">
            Browse Artworks
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="cart-page">
      <div className="cart-header">
        <h1>Shopping Cart ({cart.total_items} items)</h1>
        <button 
          onClick={handleClearCart}
          className="clear-cart-btn"
        >
          Clear Cart
        </button>
      </div>

      <div className="cart-content">
        <div className="cart-items">
          {cart.items.map(item => (
            <CartItem key={item.id} item={item} />
          ))}
        </div>

        <div className="cart-summary">
          <div className="summary-card">
            <h3>Order Summary</h3>
            
            <div className="summary-line">
              <span>Items ({cart.total_items}):</span>
              <span>{cart.total_amount} {cart.currency}</span>
            </div>
            
            <div className="summary-line">
              <span>Shipping:</span>
              <span>To be calculated</span>
            </div>
            
            <div className="summary-line total">
              <span>Total:</span>
              <span>{cart.total_amount} {cart.currency}</span>
            </div>

            <button className="checkout-btn">
              Proceed to Checkout
            </button>
            
            <Link to="/artworks" className="continue-shopping">
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;
```

### CSS Styling Examples

```css
/* Add to Cart Button */
.add-to-cart-container {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.quantity-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quantity-selector select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.add-to-cart-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s ease;
}

.add-to-cart-btn:hover:not(:disabled) {
  background: #0056b3;
}

.add-to-cart-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.add-to-cart-btn.loading {
  opacity: 0.7;
}

/* Cart Icon */
.cart-icon {
  position: relative;
  display: inline-block;
  color: inherit;
  text-decoration: none;
}

.cart-icon-container {
  position: relative;
}

.cart-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #dc3545;
  color: white;
  border-radius: 50%;
  min-width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: bold;
}

/* Cart Item */
.cart-item {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.cart-item-image {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
}

.cart-item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.cart-item-details {
  flex: 1;
}

.item-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.item-artist {
  color: #666;
  margin: 0 0 0.5rem 0;
}

.item-price {
  font-weight: 600;
  color: #007bff;
  margin: 0 0 1rem 0;
}

.quantity-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.quantity-controls select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.cart-item-actions {
  text-align: right;
}

.item-total {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.remove-btn {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.remove-btn:hover {
  background: #c82333;
}

/* Cart Page */
.cart-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.clear-cart-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.cart-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.cart-items {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.cart-summary {
  position: sticky;
  top: 2rem;
  height: fit-content;
}

.summary-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.summary-line {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.summary-line.total {
  border-top: 1px solid #eee;
  padding-top: 1rem;
  font-weight: 600;
  font-size: 1.1rem;
}

.checkout-btn {
  width: 100%;
  background: #28a745;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 6px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  margin: 1rem 0;
  transition: background 0.2s ease;
}

.checkout-btn:hover {
  background: #218838;
}

.continue-shopping {
  display: block;
  text-align: center;
  color: #007bff;
  text-decoration: none;
  margin-top: 1rem;
}

/* Empty Cart */
.empty-cart {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-cart-content h2 {
  margin-bottom: 1rem;
  color: #666;
}

.browse-artworks-btn {
  display: inline-block;
  background: #007bff;
  color: white;
  padding: 1rem 2rem;
  border-radius: 6px;
  text-decoration: none;
  margin-top: 2rem;
  transition: background 0.2s ease;
}

.browse-artworks-btn:hover {
  background: #0056b3;
}

/* Responsive Design */
@media (max-width: 768px) {
  .cart-content {
    grid-template-columns: 1fr;
  }
  
  .cart-item {
    flex-direction: column;
    text-align: center;
  }
  
  .cart-item-image {
    width: 100px;
    height: 100px;
  }
  
  .cart-header {
    flex-direction: column;
    gap: 1rem;
  }
}
```

### Mobile App Implementation (React Native)

```javascript
// components/AddToCartButton.native.js
import React, { useState } from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { useCart } from '../contexts/CartContext';

const AddToCartButton = ({ artwork, quantity = 1, style }) => {
  const [loading, setLoading] = useState(false);
  const { addItem } = useCart();

  const handleAddToCart = async () => {
    try {
      setLoading(true);
      await addItem(artwork.id, quantity);
      // Show success toast
    } catch (error) {
      // Show error toast
    } finally {
      setLoading(false);
    }
  };

  return (
    <TouchableOpacity 
      style={[styles.button, style]}
      onPress={handleAddToCart}
      disabled={loading || !artwork.is_available}
    >
      {loading ? (
        <ActivityIndicator color="white" />
      ) : (
        <Text style={styles.buttonText}>Add to Cart</Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#007bff',
    padding: 12,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 44,
  },
  buttonText: {
    color: 'white',
    fontWeight: '600',
    fontSize: 16,
  },
});

export default AddToCartButton;
```

## Error Handling

### Common Error Scenarios

1. **Unauthenticated User**: Redirect to login
2. **Artwork Not Available**: Show appropriate message
3. **Invalid Quantity**: Validate input
4. **Network Errors**: Show retry option
5. **Cart Item Not Found**: Handle gracefully

### Error Handling Example

```javascript
const handleCartError = (error) => {
  if (error.status === 401) {
    // Redirect to login
    showLoginModal();
  } else if (error.message.includes('not available')) {
    showToast('This artwork is no longer available', 'warning');
  } else if (error.message.includes('not found')) {
    showToast('Item not found in cart', 'error');
  } else {
    showToast('Something went wrong. Please try again.', 'error');
  }
};
```

## Performance Considerations

1. **Optimistic Updates**: Update UI immediately, revert on error
2. **Debouncing**: Prevent rapid quantity changes
3. **Local Storage**: Persist cart state for unauthenticated users
4. **Image Optimization**: Use thumbnails in cart
5. **Lazy Loading**: Load cart data only when needed

## Testing

### Test Cases to Implement

1. **Add to Cart**
   - ✅ Add new item to empty cart
   - ✅ Add duplicate item (should update quantity)
   - ✅ Handle artwork not available
   - ✅ Validate quantity input

2. **Cart Management**
   - ✅ Update item quantities
   - ✅ Remove individual items
   - ✅ Clear entire cart
   - ✅ Calculate totals correctly

3. **Authentication**
   - ✅ Handle unauthenticated users
   - ✅ Sync cart on login
   - ✅ Clear cart on logout

4. **Error Handling**
   - ✅ Network failure recovery
   - ✅ Invalid data handling
   - ✅ Cart item not found scenarios

This comprehensive documentation provides everything your frontend team needs to implement the shopping cart feature successfully!
