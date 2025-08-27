# SafariCrafts API Documentation

## Overview
SafariCrafts is a comprehensive ecommerce platform for Tanzanian African art featuring:
- User authentication with role-based access (Buyer, Artist, Admin)
- Artwork catalog with advanced filtering and search
- Shopping cart and checkout functionality
- Payment processing (Stripe, M-Pesa, etc.)
- Artist management and payouts
- Certificate of authenticity generation
- Shipping and fulfillment
- Review and rating system

## Base URL
- Development: `http://localhost:8000/api/v1/`
- API Documentation: `http://localhost:8000/api/docs/`

## Authentication
The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## API Endpoints

### Authentication (`/api/v1/auth/`)

#### User Registration
- **POST** `/auth/register/`
  - Register a new user account
  - Body: `{ "email", "username", "first_name", "last_name", "phone", "role", "password", "password_confirm" }`
  - Response: User data + JWT tokens

#### User Login
- **POST** `/auth/login/`
  - Authenticate user credentials
  - Body: `{ "email", "password" }`
  - Response: User data + JWT tokens

#### Token Refresh
- **POST** `/auth/token/refresh/`
  - Refresh access token
  - Body: `{ "refresh": "refresh_token" }`

#### User Profile
- **GET** `/auth/profile/`
  - Get current user profile
- **PATCH** `/auth/profile/`
  - Update user profile

#### Password Management
- **POST** `/auth/password/change/`
  - Change user password
  - Body: `{ "old_password", "new_password", "new_password_confirm" }`

#### Address Management
- **GET** `/auth/addresses/`
  - List user addresses
- **POST** `/auth/addresses/`
  - Create new address
- **PATCH** `/auth/addresses/{id}/`
  - Update address
- **DELETE** `/auth/addresses/{id}/`
  - Delete address

### Catalog (`/api/v1/catalog/`)

#### Categories
- **GET** `/catalog/categories/`
  - List all categories with hierarchical structure

#### Collections
- **GET** `/catalog/collections/`
  - List all collections
  - Query params: `?featured=true`
- **GET** `/catalog/collections/{slug}/`
  - Get collection details

#### Artworks
- **GET** `/catalog/artworks/`
  - List artworks with filtering and search
  - Query params:
    - `search`: Search query
    - `category`: Category slug
    - `collection`: Collection slug
    - `tribe`: Tribe name
    - `region`: Region name
    - `material`: Material type
    - `price_min`, `price_max`: Price range
    - `featured`: Featured only
    - `ordering`: Sort order (`created_at`, `-created_at`, `price`, `-price`, etc.)

- **GET** `/catalog/artworks/{slug}/`
  - Get artwork details (increments view count)

- **POST** `/catalog/artworks/create/` (Artists only)
  - Create new artwork
  - Body: Artwork data

- **PATCH** `/catalog/artworks/{id}/update/` (Owner only)
  - Update artwork

#### Shopping Cart
- **GET** `/catalog/cart/`
  - Get user's cart
- **DELETE** `/catalog/cart/`
  - Clear cart
- **POST** `/catalog/cart/items/`
  - Add item to cart
  - Body: `{ "artwork_id", "quantity" }`
- **PATCH** `/catalog/cart/items/{id}/`
  - Update cart item quantity
- **DELETE** `/catalog/cart/items/{id}/`
  - Remove item from cart

#### Utility Endpoints
- **GET** `/catalog/stats/`
  - Get artwork statistics
- **GET** `/catalog/filter-options/`
  - Get available filter options (tribes, regions, materials, price ranges, etc.)

### Artists (`/api/v1/artists/`)
- Artist profile management
- Artwork management for artists
- Payout requests and tracking

### Orders (`/api/v1/orders/`)
- Order creation and management
- Order history
- Order status tracking
- Refund management

### Payments (`/api/v1/payments/`)
- Payment processing
- Multiple payment providers (Stripe, M-Pesa, etc.)
- Payment history
- Webhook handling

### Shipping (`/api/v1/shipping/`)
- Shipping methods and rates
- Shipment tracking
- Label generation

### Certificates (`/api/v1/certificates/`)
- Certificate generation
- QR code verification
- Public certificate verification

### Reviews (`/api/v1/reviews/`)
- Product reviews and ratings
- Review helpfulness voting
- Artist responses to reviews

## Response Format

### Success Response
```json
{
  "id": 1,
  "title": "Makonde Carving",
  "price": 150000,
  "currency": "TZS",
  ...
}
```

### List Response (Paginated)
```json
{
  "count": 150,                    // Total number of items
  "next": "http://localhost:8000/api/v1/catalog/artworks/?limit=20&offset=40",
  "previous": "http://localhost:8000/api/v1/catalog/artworks/?limit=20&offset=0", 
  "results": [...]                 // Array of items for current page
}
```

### Error Response
```json
{
  "error": "Validation failed",
  "details": {
    "field_name": ["Error message"]
  }
}
```

## Data Models

### User Roles
- `buyer`: Regular customers
- `artist`: Art creators who can list artworks
- `admin`: Platform administrators

### Artwork Status
- `draft`: Not yet submitted
- `pending`: Awaiting moderation
- `active`: Live and purchasable
- `sold`: No longer available
- `inactive`: Temporarily hidden
- `rejected`: Declined by moderation

### Payment Status
- `pending`: Awaiting payment
- `processing`: Payment being processed
- `completed`: Payment successful
- `failed`: Payment failed
- `cancelled`: Payment cancelled
- `refunded`: Payment refunded

### Order Status
- `pending`: Awaiting payment
- `confirmed`: Payment confirmed
- `processing`: Being prepared
- `shipped`: In transit
- `delivered`: Delivered to customer
- `completed`: Order complete
- `cancelled`: Order cancelled
- `refunded`: Order refunded

## Example Usage

### 1. Register a New Artist
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "artist@example.com",
    "username": "artist1",
    "first_name": "John",
    "last_name": "Makonde",
    "phone": "+255700000000",
    "role": "artist",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
```

### 2. Search for Artworks
```bash
curl "http://localhost:8000/api/v1/catalog/artworks/?search=makonde&tribe=Makonde&price_max=200000&ordering=-created_at"
```

### 3. Add Item to Cart
```bash
curl -X POST http://localhost:8000/api/v1/catalog/cart/items/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "artwork_id": "uuid-here",
    "quantity": 1
  }'
```

### 4. Get Artwork Details
```bash
curl http://localhost:8000/api/v1/catalog/artworks/makonde-carving-traditional/
```

## Error Codes
- `400`: Bad Request - Invalid input data
- `401`: Unauthorized - Authentication required
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource does not exist
- `500`: Internal Server Error - Server error

## Rate Limiting
- Authenticated users: 1000 requests/hour
- Anonymous users: 100 requests/hour

## Pagination
List endpoints use **LimitOffsetPagination** which is ideal for infinite scrolling:
- `limit`: Number of items per page (default: 20, max: 100)
- `offset`: Number of items to skip (used for infinite scroll)

### Infinite Scrolling Implementation
The offset-based pagination is perfect for infinite scrolling:

```javascript
// Infinite scroll example
let allArtworks = [];
let currentOffset = 0;
const limit = 20;
let hasMore = true;

async function loadMoreArtworks() {
  if (!hasMore) return;
  
  const response = await fetch(
    `/api/v1/catalog/artworks/?limit=${limit}&offset=${currentOffset}`
  );
  const data = await response.json();
  
  // Append new items to existing list
  allArtworks = [...allArtworks, ...data.results];
  
  // Update offset for next request
  currentOffset += limit;
  
  // Check if there are more items
  hasMore = data.next !== null;
  
  return data.results;
}
```

## Filtering and Search
Most list endpoints support:
- Text search via `search` parameter
- Field-specific filtering
- Range filtering for numeric fields
- Boolean filtering
- Ordering via `ordering` parameter

## Frontend Integration

## Frontend Integration

### Infinite Scrolling Implementation

#### React/Next.js with Hooks
```javascript
import { useState, useEffect, useCallback } from 'react';

const useInfiniteArtworks = (filters = {}) => {
  const [artworks, setArtworks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  
  const limit = 20;
  
  const loadArtworks = useCallback(async (reset = false) => {
    if (loading) return;
    
    setLoading(true);
    const currentOffset = reset ? 0 : offset;
    
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: currentOffset.toString(),
        ...filters
      });
      
      const response = await fetch(`/api/v1/catalog/artworks/?${params}`);
      const data = await response.json();
      
      if (reset) {
        setArtworks(data.results);
        setOffset(limit);
      } else {
        setArtworks(prev => [...prev, ...data.results]);
        setOffset(prev => prev + limit);
      }
      
      setHasMore(data.next !== null);
    } catch (error) {
      console.error('Failed to load artworks:', error);
    } finally {
      setLoading(false);
    }
  }, [offset, loading, filters, limit]);
  
  // Load more when scrolling
  const loadMore = useCallback(() => {
    if (hasMore && !loading) {
      loadArtworks();
    }
  }, [hasMore, loading, loadArtworks]);
  
  // Reset when filters change
  useEffect(() => {
    setOffset(0);
    loadArtworks(true);
  }, [filters]);
  
  return { artworks, loading, hasMore, loadMore };
};

// Component usage
const ArtworkList = () => {
  const [filters, setFilters] = useState({});
  const { artworks, loading, hasMore, loadMore } = useInfiniteArtworks(filters);
  
  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + document.documentElement.scrollTop 
          >= document.documentElement.offsetHeight - 1000) {
        loadMore();
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [loadMore]);
  
  return (
    <div>
      {artworks.map(artwork => (
        <ArtworkCard key={artwork.id} artwork={artwork} />
      ))}
      {loading && <div>Loading more artworks...</div>}
      {!hasMore && <div>No more artworks to load</div>}
    </div>
  );
};
```

#### Vue 3 Composition API
```javascript
import { ref, computed, onMounted, onUnmounted } from 'vue';

export function useInfiniteArtworks(filters) {
  const artworks = ref([]);
  const loading = ref(false);
  const hasMore = ref(true);
  const offset = ref(0);
  const limit = 20;
  
  const loadArtworks = async (reset = false) => {
    if (loading.value) return;
    
    loading.value = true;
    const currentOffset = reset ? 0 : offset.value;
    
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: currentOffset.toString(),
        ...filters.value
      });
      
      const response = await fetch(`/api/v1/catalog/artworks/?${params}`);
      const data = await response.json();
      
      if (reset) {
        artworks.value = data.results;
        offset.value = limit;
      } else {
        artworks.value.push(...data.results);
        offset.value += limit;
      }
      
      hasMore.value = data.next !== null;
    } catch (error) {
      console.error('Failed to load artworks:', error);
    } finally {
      loading.value = false;
    }
  };
  
  const loadMore = () => {
    if (hasMore.value && !loading.value) {
      loadArtworks();
    }
  };
  
  const handleScroll = () => {
    if (window.innerHeight + document.documentElement.scrollTop 
        >= document.documentElement.offsetHeight - 1000) {
      loadMore();
    }
  };
  
  onMounted(() => {
    window.addEventListener('scroll', handleScroll);
    loadArtworks(true);
  });
  
  onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll);
  });
  
  return {
    artworks,
    loading,
    hasMore,
    loadMore,
    loadArtworks
  };
}
```

#### React Native with FlatList
```javascript
import React, { useState, useCallback } from 'react';
import { FlatList, ActivityIndicator, Text } from 'react-native';

const ArtworkList = ({ filters = {} }) => {
  const [artworks, setArtworks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  
  const limit = 20;
  
  const loadArtworks = useCallback(async (reset = false) => {
    if (loading) return;
    
    setLoading(true);
    const currentOffset = reset ? 0 : offset;
    
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: currentOffset.toString(),
        ...filters
      });
      
      const response = await fetch(`/api/v1/catalog/artworks/?${params}`);
      const data = await response.json();
      
      if (reset) {
        setArtworks(data.results);
        setOffset(limit);
      } else {
        setArtworks(prev => [...prev, ...data.results]);
        setOffset(prev => prev + limit);
      }
      
      setHasMore(data.next !== null);
    } catch (error) {
      console.error('Failed to load artworks:', error);
    } finally {
      setLoading(false);
    }
  }, [offset, loading, filters, limit]);
  
  const renderFooter = () => {
    if (!loading) return null;
    return <ActivityIndicator style={{ margin: 15 }} />;
  };
  
  const renderEmpty = () => {
    if (loading) return null;
    return <Text>No artworks found</Text>;
  };
  
  return (
    <FlatList
      data={artworks}
      renderItem={({ item }) => <ArtworkCard artwork={item} />}
      keyExtractor={item => item.id}
      onEndReached={() => loadArtworks()}
      onEndReachedThreshold={0.5}
      ListFooterComponent={renderFooter}
      ListEmptyComponent={renderEmpty}
      onRefresh={() => loadArtworks(true)}
      refreshing={loading && offset === 0}
    />
  );
};
```

### Infinite Scrolling Best Practices

#### 1. **Optimized Loading**
```javascript
// Load more when user is 1000px from bottom
const threshold = 1000;
const shouldLoadMore = (
  window.innerHeight + document.documentElement.scrollTop 
  >= document.documentElement.offsetHeight - threshold
);
```

#### 2. **Debounced Scroll Events**
```javascript
import { debounce } from 'lodash';

const debouncedHandleScroll = debounce(() => {
  if (shouldLoadMore()) {
    loadMore();
  }
}, 100);
```

#### 3. **Error Handling**
```javascript
const [error, setError] = useState(null);

const loadArtworks = async () => {
  try {
    setError(null);
    // ... fetch logic
  } catch (err) {
    setError('Failed to load artworks. Please try again.');
    console.error(err);
  }
};
```

#### 4. **Loading States**
```javascript
// Different loading states
const [initialLoading, setInitialLoading] = useState(true);
const [loadingMore, setLoadingMore] = useState(false);

// Show skeleton for initial load, spinner for load more
```

#### 5. **Filter Reset Handling**
```javascript
// Reset pagination when filters change
useEffect(() => {
  setArtworks([]);
  setOffset(0);
  setHasMore(true);
  loadArtworks(true);
}, [searchQuery, category, priceRange]);
```

#### 6. **Memory Management**
```javascript
// For very long lists, consider virtual scrolling
// or implement item recycling to prevent memory issues
const MAX_ITEMS = 1000;

if (artworks.length > MAX_ITEMS) {
  // Remove items from beginning and adjust offset
  setArtworks(prev => prev.slice(-MAX_ITEMS));
}
```

### API client setup
```javascript
// API client setup
const API_BASE = 'http://localhost:8000/api/v1';

const apiClient = {
  async get(endpoint, token) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
      },
    });
    return response.json();
  },
  
  async post(endpoint, data, token) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  }
};

// Usage examples
const artworks = await apiClient.get('/catalog/artworks/');
const cart = await apiClient.get('/catalog/cart/', accessToken);
const newItem = await apiClient.post('/catalog/cart/items/', {
  artwork_id: 'uuid',
  quantity: 1
}, accessToken);
```

### Vue/Nuxt Example
```javascript
// Nuxt plugin for API
export default function ({ $axios }, inject) {
  const api = $axios.create({
    baseURL: 'http://localhost:8000/api/v1'
  });
  
  // Add auth token to requests
  api.onRequest(config => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  });
  
  inject('api', api);
}

// Component usage
export default {
  async asyncData({ $api }) {
    const artworks = await $api.$get('/catalog/artworks/');
    return { artworks };
  },
  
  methods: {
    async addToCart(artworkId) {
      await this.$api.$post('/catalog/cart/items/', {
        artwork_id: artworkId,
        quantity: 1
      });
    }
  }
}
```

## WebSocket Support (Future)
Real-time features for:
- Order status updates
- Payment confirmations
- Shipping notifications
- Live chat support

## Mobile App Integration
The API is designed to support mobile applications with:
- Optimized payloads
- Image resizing endpoints
- Offline support considerations
- Push notification webhooks
