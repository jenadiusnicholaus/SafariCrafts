# Artwork Like Feature API Documentation

## Overview
The artwork like feature allows authenticated users to like/unlike artworks and view their liked artworks. This document provides complete integration guidance for frontend developers.

## API Endpoints

### 1. Like/Unlike Artwork
**Endpoint:** `POST /api/v1/catalog/artworks/{artwork_id}/like/`

**Purpose:** Toggle like status for an artwork (like if not liked, unlike if already liked)

**Authentication:** Required (JWT Bearer Token)

**URL Parameters:**
- `artwork_id` (UUID): The unique identifier of the artwork

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
Content-Type: application/json
```

**Request Body:** None required

**Response Examples:**

**Success - Artwork Liked (201 Created):**
```json
{
    "message": "Artwork liked successfully",
    "liked": true,
    "like_count": 15
}
```

**Success - Artwork Unliked (200 OK):**
```json
{
    "message": "Artwork unliked successfully",
    "liked": false,
    "like_count": 14
}
```

**Error - Artwork Not Found (404):**
```json
{
    "error": "Artwork not found"
}
```

**Error - Unauthorized (401):**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

---

### 2. Get User's Liked Artworks
**Endpoint:** `GET /api/v1/catalog/artworks/liked/`

**Purpose:** Retrieve all artworks liked by the current authenticated user

**Authentication:** Required (JWT Bearer Token)

**Query Parameters:**
- `limit` (integer, optional): Number of items per page (default: 20)
- `offset` (integer, optional): Number of items to skip for pagination
- `ordering` (string, optional): Sort order
  - Options: `created_at`, `-created_at`, `price`, `-price`, `title`, `-title`, `view_count`, `-view_count`
  - Default: `-created_at`

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
```

**Response Example:**
```json
{
    "count": 25,
    "next": "http://127.0.0.1:8082/api/v1/catalog/artworks/liked/?limit=20&offset=20",
    "previous": null,
    "results": [
        {
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
        }
    ]
}
```

---

### 3. Enhanced Artwork List/Detail with Like Status
**Endpoints:** 
- `GET /api/v1/catalog/artworks/` (List view)
- `GET /api/v1/catalog/artworks/{slug}/` (Detail view)

**Purpose:** Regular artwork endpoints now include like status when user is authenticated

**New Fields Added:**
- `is_liked` (boolean): Whether current user has liked this artwork
- `like_count` (integer): Total number of likes for this artwork

**Example Response (authenticated user):**
```json
{
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
    "is_liked": true  // ← New field
}
```

**For unauthenticated users:** `is_liked` will always be `false`

---

## Frontend Implementation Guide

### React/Next.js Implementation

#### 1. API Service Functions

```javascript
// services/artworkApi.js
const API_BASE_URL = 'http://127.0.0.1:8082/api/v1';

// Get JWT token from your auth context/store
const getAuthHeaders = () => ({
  'Authorization': `Bearer ${getJWTToken()}`,
  'Content-Type': 'application/json'
});

// Like/Unlike artwork
export const toggleArtworkLike = async (artworkId) => {
  const response = await fetch(`${API_BASE_URL}/catalog/artworks/${artworkId}/like/`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to toggle like');
  }
  
  return response.json();
};

// Get liked artworks
export const getLikedArtworks = async (page = 1, limit = 20, ordering = '-created_at') => {
  const offset = (page - 1) * limit;
  const response = await fetch(
    `${API_BASE_URL}/catalog/artworks/liked/?limit=${limit}&offset=${offset}&ordering=${ordering}`,
    {
      headers: getAuthHeaders(),
    }
  );
  
  if (!response.ok) {
    throw new Error('Failed to fetch liked artworks');
  }
  
  return response.json();
};

// Get regular artworks (now includes is_liked field)
export const getArtworks = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const headers = isAuthenticated() ? getAuthHeaders() : {};
  
  const response = await fetch(`${API_BASE_URL}/catalog/artworks/?${params}`, {
    headers
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch artworks');
  }
  
  return response.json();
};
```

#### 2. React Hook for Like Functionality

```javascript
// hooks/useArtworkLike.js
import { useState, useCallback } from 'react';
import { toggleArtworkLike } from '../services/artworkApi';

export const useArtworkLike = (initialLiked = false, initialCount = 0) => {
  const [isLiked, setIsLiked] = useState(initialLiked);
  const [likeCount, setLikeCount] = useState(initialCount);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleToggleLike = useCallback(async (artworkId) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await toggleArtworkLike(artworkId);
      setIsLiked(result.liked);
      setLikeCount(result.like_count);
    } catch (err) {
      setError(err.message);
      // Revert optimistic update on error
      console.error('Like toggle failed:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLiked,
    likeCount,
    isLoading,
    error,
    toggleLike: handleToggleLike
  };
};
```

#### 3. Like Button Component

```javascript
// components/LikeButton.jsx
import React from 'react';
import { useArtworkLike } from '../hooks/useArtworkLike';
import { useAuth } from '../contexts/AuthContext';

const LikeButton = ({ 
  artworkId, 
  initialIsLiked = false, 
  initialLikeCount = 0,
  showCount = true,
  className = ""
}) => {
  const { isAuthenticated, showLoginModal } = useAuth();
  const { isLiked, likeCount, isLoading, toggleLike } = useArtworkLike(
    initialIsLiked, 
    initialLikeCount
  );

  const handleClick = async () => {
    if (!isAuthenticated) {
      showLoginModal();
      return;
    }
    
    await toggleLike(artworkId);
  };

  return (
    <button 
      onClick={handleClick}
      disabled={isLoading}
      className={`like-button ${isLiked ? 'liked' : ''} ${className}`}
      aria-label={isLiked ? 'Unlike artwork' : 'Like artwork'}
    >
      <span className="heart-icon">
        {isLiked ? '❤️' : '🤍'}
      </span>
      {showCount && (
        <span className="like-count">
          {likeCount}
        </span>
      )}
    </button>
  );
};

export default LikeButton;
```

#### 4. Artwork Card with Like Button

```javascript
// components/ArtworkCard.jsx
import React from 'react';
import LikeButton from './LikeButton';

const ArtworkCard = ({ artwork }) => {
  return (
    <div className="artwork-card">
      <div className="artwork-image">
        <img 
          src={artwork.main_image?.file || '/placeholder.jpg'} 
          alt={artwork.main_image?.alt_text || artwork.title}
        />
        <div className="like-overlay">
          <LikeButton 
            artworkId={artwork.id}
            initialIsLiked={artwork.is_liked}
            initialLikeCount={artwork.like_count}
          />
        </div>
      </div>
      
      <div className="artwork-info">
        <h3>{artwork.title}</h3>
        <p className="artist">{artwork.artist_name}</p>
        <p className="price">{artwork.price} {artwork.currency}</p>
        
        <div className="artwork-stats">
          <span>👁️ {artwork.view_count} views</span>
          <span>❤️ {artwork.like_count} likes</span>
        </div>
      </div>
    </div>
  );
};

export default ArtworkCard;
```

#### 5. Liked Artworks Page

```javascript
// pages/LikedArtworks.jsx
import React, { useState, useEffect } from 'react';
import { getLikedArtworks } from '../services/artworkApi';
import ArtworkCard from '../components/ArtworkCard';
import InfiniteScroll from 'react-infinite-scroll-component';

const LikedArtworksPage = () => {
  const [artworks, setArtworks] = useState([]);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  const loadLikedArtworks = async (pageNum = 1, reset = false) => {
    try {
      const data = await getLikedArtworks(pageNum, 20);
      
      if (reset) {
        setArtworks(data.results);
      } else {
        setArtworks(prev => [...prev, ...data.results]);
      }
      
      setHasMore(data.next !== null);
      setPage(pageNum + 1);
    } catch (error) {
      console.error('Failed to load liked artworks:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLikedArtworks(1, true);
  }, []);

  const loadMore = () => {
    loadLikedArtworks(page);
  };

  if (loading) {
    return <div className="loading">Loading your liked artworks...</div>;
  }

  if (artworks.length === 0) {
    return (
      <div className="empty-state">
        <h2>No Liked Artworks Yet</h2>
        <p>Start exploring and like artworks you love!</p>
        <a href="/artworks" className="browse-button">
          Browse Artworks
        </a>
      </div>
    );
  }

  return (
    <div className="liked-artworks-page">
      <h1>Your Liked Artworks ({artworks.length})</h1>
      
      <InfiniteScroll
        dataLength={artworks.length}
        next={loadMore}
        hasMore={hasMore}
        loader={<div>Loading more...</div>}
        endMessage={<div>You've seen all your liked artworks!</div>}
      >
        <div className="artworks-grid">
          {artworks.map(artwork => (
            <ArtworkCard 
              key={artwork.id} 
              artwork={artwork} 
            />
          ))}
        </div>
      </InfiniteScroll>
    </div>
  );
};

export default LikedArtworksPage;
```

### CSS Styling Examples

```css
/* Like Button Styles */
.like-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.like-button:hover {
  background: rgba(255, 255, 255, 1);
  transform: scale(1.05);
}

.like-button.liked {
  background: rgba(255, 182, 193, 0.9);
}

.like-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.heart-icon {
  font-size: 1.2rem;
  transition: transform 0.2s ease;
}

.like-button:hover .heart-icon {
  transform: scale(1.2);
}

/* Artwork Card Styles */
.artwork-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.artwork-card:hover {
  transform: translateY(-4px);
}

.artwork-image {
  position: relative;
  height: 250px;
  overflow: hidden;
}

.artwork-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.like-overlay {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.artwork-info {
  padding: 1rem;
}

.artwork-stats {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #666;
}

/* Liked Artworks Page */
.liked-artworks-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.artworks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.browse-button {
  display: inline-block;
  background: #007bff;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  text-decoration: none;
  margin-top: 1rem;
  transition: background 0.2s ease;
}

.browse-button:hover {
  background: #0056b3;
}

@media (max-width: 768px) {
  .artworks-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1rem;
  }
  
  .like-overlay {
    top: 0.5rem;
    right: 0.5rem;
  }
}
```

### Mobile App Implementation (React Native)

```javascript
// components/LikeButton.native.js
import React from 'react';
import { TouchableOpacity, Text, View, StyleSheet } from 'react-native';
import { useArtworkLike } from '../hooks/useArtworkLike';

const LikeButton = ({ artworkId, initialIsLiked, initialLikeCount }) => {
  const { isLiked, likeCount, isLoading, toggleLike } = useArtworkLike(
    initialIsLiked,
    initialLikeCount
  );

  const handlePress = () => {
    if (!isLoading) {
      toggleLike(artworkId);
    }
  };

  return (
    <TouchableOpacity 
      style={[styles.container, isLiked && styles.liked]}
      onPress={handlePress}
      disabled={isLoading}
    >
      <Text style={styles.heart}>
        {isLiked ? '❤️' : '🤍'}
      </Text>
      <Text style={styles.count}>{likeCount}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    gap: 4,
  },
  liked: {
    backgroundColor: 'rgba(255, 182, 193, 0.9)',
  },
  heart: {
    fontSize: 16,
  },
  count: {
    fontSize: 14,
    fontWeight: '600',
  },
});

export default LikeButton;
```

## Error Handling

### Common Error Scenarios

1. **Unauthenticated User**: Show login modal/redirect
2. **Network Errors**: Show retry option
3. **Artwork Not Found**: Handle gracefully with message
4. **Server Errors**: Show generic error message

### Error Handling Example

```javascript
const handleLikeError = (error) => {
  if (error.status === 401) {
    // Redirect to login
    showLoginModal();
  } else if (error.status === 404) {
    // Artwork not found
    showToast('Artwork not found', 'error');
  } else {
    // Generic error
    showToast('Something went wrong. Please try again.', 'error');
  }
};
```

## Performance Considerations

1. **Optimistic Updates**: Update UI immediately, revert on error
2. **Debouncing**: Prevent rapid like/unlike clicks
3. **Caching**: Cache liked status to reduce API calls
4. **Infinite Scroll**: Use for liked artworks list
5. **Image Optimization**: Use thumbnails for artwork cards

## Testing

### Test Cases to Implement

1. **Like Button Functionality**
   - ✅ Like artwork when not liked
   - ✅ Unlike artwork when already liked
   - ✅ Show correct like count
   - ✅ Handle unauthenticated user
   - ✅ Handle network errors

2. **Liked Artworks List**
   - ✅ Display user's liked artworks
   - ✅ Handle empty state
   - ✅ Implement pagination
   - ✅ Handle loading states

3. **Integration**
   - ✅ Like status syncs across components
   - ✅ Real-time updates when liking/unliking
   - ✅ Proper error handling

This comprehensive documentation should provide everything your frontend team needs to implement the artwork like feature successfully!
