# Checkout Flow API Documentation

## Overview
The checkout flow allows authenticated users to convert their shopping cart into an order, select shipping methods, enter billing/shipping addresses, and process payments. This document provides complete integration guidance for frontend developers.

**Payment Integration**: The system now uses **Azam Pay** for all Tanzanian payment methods (M-Pesa, Airtel Money, Tigo Pesa, Bank Transfers) and **PayPal** for international payments. Stripe has been removed from the default configuration.

## Checkout Flow Architecture

### 1. Multi-Step Checkout Process
1. **Cart Review** - Review items in cart
2. **Shipping Address** - Enter/select shipping address
3. **Shipping Method** - Choose shipping method and calculate costs
4. **Billing Address** - Enter/select billing address
5. **Payment Method** - Choose payment method
6. **Order Review** - Final review before payment
7. **Payment Processing** - Process payment and create order
8. **Order Confirmation** - Display order confirmation

### 2. Data Models Overview

#### Order Model
- **Order Number**: Auto-generated (e.g., SC2025001234)
- **Status Flow**: pending → confirmed → processing → shipped → delivered → completed
- **Price Breakdown**: subtotal, shipping, tax, discount, total
- **Address Storage**: JSON format preserves address data

#### Payment Model
- **Providers**: Azam Pay, PayPal
- **Methods**: M-Pesa, Airtel Money, Tigo Pesa, Bank Transfer (CRDB & NMB), PayPal
- **Status Tracking**: pending → processing → completed/failed

#### Shipping Model
- **Methods**: Various carriers with cost calculation
- **Tracking**: Full shipment lifecycle tracking
- **Geographic**: Domestic and international support

---

## API Endpoints

### 1. Get Available Shipping Methods
**Endpoint:** `GET /api/v1/shipping/methods/`

**Purpose:** Retrieve available shipping methods for cart items

**Authentication:** Required (JWT Bearer Token)

**Query Parameters:**
- `country` (string, optional): Destination country code (default: 'TZ')
- `weight` (decimal, optional): Total weight in kg for cost calculation

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
```

**Response Example:**
```json
[
    {
        "id": 1,
        "name": "Standard Delivery",
        "description": "Regular delivery within Tanzania",
        "carrier": "DHL",
        "base_cost": "5000.00",
        "cost_per_kg": "2000.00",
        "calculated_cost": "9000.00",
        "min_delivery_days": 3,
        "max_delivery_days": 7,
        "max_weight": "30.000",
        "max_dimensions": "60x40x40 cm",
        "domestic_only": true,
        "supported_countries": [],
        "is_active": true,
        "estimated_delivery": "2025-08-30 to 2025-09-03"
    },
    {
        "id": 2,
        "name": "Express Delivery",
        "description": "Fast delivery within Dar es Salaam",
        "carrier": "Local Courier",
        "base_cost": "8000.00",
        "cost_per_kg": "1000.00",
        "calculated_cost": "10000.00",
        "min_delivery_days": 1,
        "max_delivery_days": 2,
        "max_weight": "10.000",
        "max_dimensions": "40x30x30 cm",
        "domestic_only": true,
        "supported_countries": [],
        "is_active": true,
        "estimated_delivery": "2025-08-28 to 2025-08-29"
    }
]
```

---

### 2. Calculate Shipping Cost
**Endpoint:** `POST /api/v1/shipping/calculate/`

**Purpose:** Calculate shipping cost for specific method and cart

**Authentication:** Required (JWT Bearer Token)

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
    "shipping_method_id": 1,
    "country": "TZ",
    "weight": 2.5
}
```

**Response Example:**
```json
{
    "shipping_method": {
        "id": 1,
        "name": "Standard Delivery",
        "carrier": "DHL"
    },
    "cost": "10000.00",
    "currency": "TZS",
    "estimated_delivery_date": "2025-09-03",
    "delivery_window": "3-7 business days"
}
```

---

### 3. Create Order from Cart
**Endpoint:** `POST /api/v1/orders/create/`

**Purpose:** Convert cart to order with shipping and billing information

**Authentication:** Required (JWT Bearer Token)

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
    "shipping_address": {
        "first_name": "John",
        "last_name": "Doe",
        "company": "",
        "address_line_1": "123 Main Street",
        "address_line_2": "Apt 4B",
        "city": "Dar es Salaam",
        "region": "Dar es Salaam",
        "postal_code": "12345",
        "country": "TZ",
        "phone": "+255712345678"
    },
    "billing_address": {
        "first_name": "John",
        "last_name": "Doe",
        "company": "",
        "address_line_1": "123 Main Street",
        "address_line_2": "Apt 4B",
        "city": "Dar es Salaam",
        "region": "Dar es Salaam",
        "postal_code": "12345",
        "country": "TZ",
        "phone": "+255712345678"
    },
    "shipping_method_id": 1,
    "customer_notes": "Please handle with care",
    "same_as_shipping": true
}
```

**Response Example:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "order_number": "SC2025001234",
    "status": "pending",
    "currency": "TZS",
    "subtotal": "240000.00",
    "shipping_cost": "10000.00",
    "tax_amount": "0.00",
    "discount_amount": "0.00",
    "total_amount": "250000.00",
    "shipping_address": {
        "first_name": "John",
        "last_name": "Doe",
        "address_line_1": "123 Main Street",
        "address_line_2": "Apt 4B",
        "city": "Dar es Salaam",
        "region": "Dar es Salaam",
        "postal_code": "12345",
        "country": "TZ",
        "phone": "+255712345678"
    },
    "billing_address": {...},
    "items": [
        {
            "id": 15,
            "artwork": {
                "id": "4fc3ff2e-eb37-4d3a-8274-ebb9fa216fb6",
                "title": "Ceremonial Bracelet Set",
                "artist_name": "Fatuma Maasai",
                "main_image": {
                    "file": "http://127.0.0.1:8082/media/artwork_media/image.jpg",
                    "thumbnail": "http://127.0.0.1:8082/media/artwork_thumbnails/image.jpg"
                }
            },
            "quantity": 2,
            "unit_price": "120000.00",
            "total_price": "240000.00",
            "tax_rate": "0.0000",
            "tax_amount": "0.00",
            "snapshot": {
                "title": "Ceremonial Bracelet Set",
                "artist": "Fatuma Maasai",
                "price": "120000.00",
                "currency": "TZS"
            }
        }
    ],
    "shipping_method": {
        "id": 1,
        "name": "Standard Delivery",
        "carrier": "DHL",
        "estimated_delivery": "3-7 business days"
    },
    "customer_notes": "Please handle with care",
    "created_at": "2025-08-27T15:30:00.000000+03:00",
    "payment_required": true,
    "payment_url": null
}
```

---

### 4. Get Payment Methods
**Endpoint:** `GET /api/v1/payments/methods/`

**Purpose:** Get available payment methods for the user

**Authentication:** Required (JWT Bearer Token)

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
```

**Response Example:**
```json
[
    {
        "provider": "azampay",
        "method": "mpesa",
        "name": "M-Pesa",
        "description": "Pay with your M-Pesa mobile money",
        "icon": "https://example.com/icons/mpesa.png",
        "fees": {
            "percentage": 2.5,
            "fixed_amount": "0.00"
        },
        "supported_currencies": ["TZS"],
        "is_active": true
    },
    {
        "provider": "azampay",
        "method": "airtel_money",
        "name": "Airtel Money",
        "description": "Pay with your Airtel Money wallet",
        "icon": "https://example.com/icons/airtel.png",
        "fees": {
            "percentage": 2.5,
            "fixed_amount": "0.00"
        },
        "supported_currencies": ["TZS"],
        "is_active": true
    },
    {
        "provider": "azampay",
        "method": "tigo_pesa",
        "name": "Tigo Pesa",
        "description": "Pay with your Tigo Pesa wallet",
        "icon": "https://example.com/icons/tigo.png",
        "fees": {
            "percentage": 2.5,
            "fixed_amount": "0.00"
        },
        "supported_currencies": ["TZS"],
        "is_active": true
    },
    {
        "provider": "azampay",
        "method": "bank_transfer",
        "name": "Bank Transfer (CRDB & NMB)",
        "description": "Pay directly from your CRDB Bank or NMB Bank account",
        "icon": "https://example.com/icons/bank.png",
        "fees": {
            "percentage": 1.5,
            "fixed_amount": "0.00"
        },
        "supported_currencies": ["TZS"],
        "is_active": true
    },
    {
        "provider": "paypal",
        "method": "paypal",
        "name": "PayPal",
        "description": "Pay with your PayPal account (International payments)",
        "icon": "https://example.com/icons/paypal.png",
        "fees": {
            "percentage": 4.0,
            "fixed_amount": "0.00"
        },
        "supported_currencies": ["USD", "EUR"],
        "is_active": true
    }
]
```

---

### 5. Initialize Payment
**Endpoint:** `POST /api/v1/payments/initialize/`

**Purpose:** Initialize payment for an order

**Authentication:** Required (JWT Bearer Token)

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
    "order_id": "550e8400-e29b-41d4-a716-446655440000",
    "payment_method": {
        "provider": "azampay",
        "method": "mpesa"
    },
    "return_url": "https://yourapp.com/checkout/success",
    "cancel_url": "https://yourapp.com/checkout/cancel"
}
```

**Response Example:**
```json
{
    "payment_id": "payment_123456789",
    "status": "pending",
    "payment_url": "https://azampay.co.tz/checkout/session_abc123",
    "client_secret": "azam_1234567890_secret_abc",
    "provider_data": {
        "session_id": "azam_session_abc123",
        "reference": "AZ123456789"
    },
    "expires_at": "2025-08-27T16:30:00.000000+03:00"
}
```

---

### 6. Process Payment (Mobile Money)
**Endpoint:** `POST /api/v1/payments/process-mobile/`

**Purpose:** Process mobile money payments (M-Pesa, Airtel Money, etc.)

**Authentication:** Required (JWT Bearer Token)

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
Content-Type: application/json
```

**Request Body:**
```json
{
    "order_id": "550e8400-e29b-41d4-a716-446655440000",
    "payment_method": {
        "provider": "azampay",
        "method": "mpesa"
    },
    "phone_number": "+255712345678"
}
```

**Response Example:**
```json
{
    "payment_id": "payment_123456789",
    "status": "processing",
    "message": "Payment request sent to your phone. Please check your M-Pesa and enter your PIN to complete the payment.",
    "reference": "MP12345678",
    "instructions": "Enter your M-Pesa PIN when prompted on your phone",
    "timeout": 300,
    "status_check_url": "/api/v1/payments/payment_123456789/status/"
}
```

---

### 7. Check Payment Status
**Endpoint:** `GET /api/v1/payments/{payment_id}/status/`

**Purpose:** Check the current status of a payment

**Authentication:** Required (JWT Bearer Token)

**URL Parameters:**
- `payment_id` (string): Payment identifier

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
```

**Response Examples:**

**Payment Completed:**
```json
{
    "payment_id": "payment_123456789",
    "status": "completed",
    "order_id": "550e8400-e29b-41d4-a716-446655440000",
    "amount": "250000.00",
    "currency": "TZS",
    "provider_ref": "MP12345678",
    "processed_at": "2025-08-27T15:35:00.000000+03:00",
    "receipt_url": "https://payments.example.com/receipt/abc123"
}
```

**Payment Failed:**
```json
{
    "payment_id": "payment_123456789",
    "status": "failed",
    "order_id": "550e8400-e29b-41d4-a716-446655440000",
    "failure_reason": "Insufficient funds",
    "failure_code": "INSUFFICIENT_FUNDS",
    "retry_allowed": true
}
```

---

### 8. Get Order Details
**Endpoint:** `GET /api/v1/orders/{order_id}/`

**Purpose:** Retrieve detailed order information

**Authentication:** Required (JWT Bearer Token)

**URL Parameters:**
- `order_id` (UUID): Order identifier

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
```

**Response Example:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "order_number": "SC2025001234",
    "status": "confirmed",
    "currency": "TZS",
    "subtotal": "240000.00",
    "shipping_cost": "10000.00",
    "tax_amount": "0.00",
    "discount_amount": "0.00",
    "total_amount": "250000.00",
    "shipping_address": {...},
    "billing_address": {...},
    "items": [...],
    "payment": {
        "id": "payment_123456789",
        "status": "completed",
        "method": "mpesa",
        "provider": "azampay",
        "amount": "250000.00",
        "processed_at": "2025-08-27T15:35:00.000000+03:00"
    },
    "shipment": {
        "id": "shipment_abc123",
        "status": "pending",
        "tracking_number": null,
        "carrier": "DHL",
        "estimated_delivery": "2025-09-03"
    },
    "status_history": [
        {
            "status": "pending",
            "changed_at": "2025-08-27T15:30:00.000000+03:00",
            "note": "Order created"
        },
        {
            "status": "confirmed",
            "changed_at": "2025-08-27T15:35:00.000000+03:00",
            "note": "Payment received"
        }
    ],
    "customer_notes": "Please handle with care",
    "created_at": "2025-08-27T15:30:00.000000+03:00",
    "updated_at": "2025-08-27T15:35:00.000000+03:00",
    "is_paid": true,
    "can_be_cancelled": false,
    "can_be_refunded": true
}
```

---

### 9. Get User Orders
**Endpoint:** `GET /api/v1/orders/`

**Purpose:** Retrieve user's order history

**Authentication:** Required (JWT Bearer Token)

**Query Parameters:**
- `status` (string, optional): Filter by order status
- `limit` (integer, optional): Number of orders per page (default: 20)
- `offset` (integer, optional): Number of orders to skip for pagination
- `ordering` (string, optional): Sort order (-created_at, created_at, total_amount, etc.)

**Request Headers:**
```http
Authorization: Bearer {your_jwt_token}
```

**Response Example:**
```json
{
    "count": 15,
    "next": "http://127.0.0.1:8082/api/v1/orders/?limit=20&offset=20",
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "order_number": "SC2025001234",
            "status": "delivered",
            "total_amount": "250000.00",
            "currency": "TZS",
            "items_count": 2,
            "created_at": "2025-08-27T15:30:00.000000+03:00",
            "delivered_at": "2025-09-01T14:20:00.000000+03:00",
            "payment_status": "completed",
            "shipment_status": "delivered"
        }
    ]
}
```

---

## Frontend Implementation Guide

### React/Next.js Implementation

#### 1. Checkout Context for State Management

```javascript
// contexts/CheckoutContext.jsx
import React, { createContext, useContext, useReducer } from 'react';

const checkoutReducer = (state, action) => {
  switch (action.type) {
    case 'SET_STEP':
      return { ...state, currentStep: action.payload };
    
    case 'SET_SHIPPING_ADDRESS':
      return { ...state, shippingAddress: action.payload };
    
    case 'SET_BILLING_ADDRESS':
      return { ...state, billingAddress: action.payload };
    
    case 'SET_SHIPPING_METHOD':
      return { ...state, shippingMethod: action.payload };
    
    case 'SET_PAYMENT_METHOD':
      return { ...state, paymentMethod: action.payload };
    
    case 'SET_ORDER':
      return { ...state, order: action.payload };
    
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    
    case 'RESET_CHECKOUT':
      return initialState;
    
    default:
      return state;
  }
};

const initialState = {
  currentStep: 1,
  shippingAddress: null,
  billingAddress: null,
  shippingMethod: null,
  paymentMethod: null,
  order: null,
  loading: false,
  error: null,
};

const CheckoutContext = createContext();

export const CheckoutProvider = ({ children }) => {
  const [state, dispatch] = useReducer(checkoutReducer, initialState);

  const setStep = (step) => {
    dispatch({ type: 'SET_STEP', payload: step });
  };

  const setShippingAddress = (address) => {
    dispatch({ type: 'SET_SHIPPING_ADDRESS', payload: address });
  };

  const setBillingAddress = (address) => {
    dispatch({ type: 'SET_BILLING_ADDRESS', payload: address });
  };

  const setShippingMethod = (method) => {
    dispatch({ type: 'SET_SHIPPING_METHOD', payload: method });
  };

  const setPaymentMethod = (method) => {
    dispatch({ type: 'SET_PAYMENT_METHOD', payload: method });
  };

  const setOrder = (order) => {
    dispatch({ type: 'SET_ORDER', payload: order });
  };

  const setLoading = (loading) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  };

  const setError = (error) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  const resetCheckout = () => {
    dispatch({ type: 'RESET_CHECKOUT' });
  };

  const value = {
    ...state,
    setStep,
    setShippingAddress,
    setBillingAddress,
    setShippingMethod,
    setPaymentMethod,
    setOrder,
    setLoading,
    setError,
    resetCheckout,
  };

  return (
    <CheckoutContext.Provider value={value}>
      {children}
    </CheckoutContext.Provider>
  );
};

export const useCheckout = () => {
  const context = useContext(CheckoutContext);
  if (!context) {
    throw new Error('useCheckout must be used within a CheckoutProvider');
  }
  return context;
};
```

#### 2. API Service Functions

```javascript
// services/checkoutApi.js
const API_BASE_URL = 'http://127.0.0.1:8082/api/v1';

const getAuthHeaders = () => ({
  'Authorization': `Bearer ${getJWTToken()}`,
  'Content-Type': 'application/json'
});

// Get shipping methods
export const getShippingMethods = async (country = 'TZ', weight = null) => {
  const params = new URLSearchParams({ country });
  if (weight) params.append('weight', weight);
  
  const response = await fetch(`${API_BASE_URL}/shipping/methods/?${params}`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch shipping methods');
  }
  
  return response.json();
};

// Calculate shipping cost
export const calculateShippingCost = async (shippingMethodId, country = 'TZ', weight) => {
  const response = await fetch(`${API_BASE_URL}/shipping/calculate/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      shipping_method_id: shippingMethodId,
      country,
      weight
    }),
  });
  
  if (!response.ok) {
    throw new Error('Failed to calculate shipping cost');
  }
  
  return response.json();
};

// Create order from cart
export const createOrder = async (orderData) => {
  const response = await fetch(`${API_BASE_URL}/orders/create/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(orderData),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to create order');
  }
  
  return response.json();
};

// Get payment methods
export const getPaymentMethods = async () => {
  const response = await fetch(`${API_BASE_URL}/payments/methods/`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch payment methods');
  }
  
  return response.json();
};

// Initialize payment
export const initializePayment = async (paymentData) => {
  const response = await fetch(`${API_BASE_URL}/payments/initialize/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(paymentData),
  });
  
  if (!response.ok) {
    throw new Error('Failed to initialize payment');
  }
  
  return response.json();
};

// Process mobile payment
export const processMobilePayment = async (paymentData) => {
  const response = await fetch(`${API_BASE_URL}/payments/process-mobile/`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(paymentData),
  });
  
  if (!response.ok) {
    throw new Error('Failed to process mobile payment');
  }
  
  return response.json();
};

// Check payment status
export const checkPaymentStatus = async (paymentId) => {
  const response = await fetch(`${API_BASE_URL}/payments/${paymentId}/status/`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to check payment status');
  }
  
  return response.json();
};

// Get order details
export const getOrder = async (orderId) => {
  const response = await fetch(`${API_BASE_URL}/orders/${orderId}/`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch order');
  }
  
  return response.json();
};

// Get user orders
export const getUserOrders = async (params = {}) => {
  const queryParams = new URLSearchParams(params);
  const response = await fetch(`${API_BASE_URL}/orders/?${queryParams}`, {
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('Failed to fetch orders');
  }
  
  return response.json();
};
```

#### 3. Address Form Component

```javascript
// components/AddressForm.jsx
import React, { useState } from 'react';

const AddressForm = ({ 
  initialAddress = {}, 
  onSave, 
  title = "Shipping Address",
  showSameAsBilling = false 
}) => {
  const [address, setAddress] = useState({
    first_name: '',
    last_name: '',
    company: '',
    address_line_1: '',
    address_line_2: '',
    city: '',
    region: '',
    postal_code: '',
    country: 'TZ',
    phone: '',
    ...initialAddress
  });

  const [sameAsBilling, setSameAsBilling] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setAddress(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(address, sameAsBilling);
  };

  return (
    <div className="address-form">
      <h3>{title}</h3>
      
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="first_name">First Name *</label>
            <input
              type="text"
              id="first_name"
              name="first_name"
              value={address.first_name}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="last_name">Last Name *</label>
            <input
              type="text"
              id="last_name"
              name="last_name"
              value={address.last_name}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="company">Company (Optional)</label>
          <input
            type="text"
            id="company"
            name="company"
            value={address.company}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label htmlFor="address_line_1">Address Line 1 *</label>
          <input
            type="text"
            id="address_line_1"
            name="address_line_1"
            value={address.address_line_1}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="address_line_2">Address Line 2 (Optional)</label>
          <input
            type="text"
            id="address_line_2"
            name="address_line_2"
            value={address.address_line_2}
            onChange={handleChange}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="city">City *</label>
            <input
              type="text"
              id="city"
              name="city"
              value={address.city}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="region">Region *</label>
            <input
              type="text"
              id="region"
              name="region"
              value={address.region}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="postal_code">Postal Code</label>
            <input
              type="text"
              id="postal_code"
              name="postal_code"
              value={address.postal_code}
              onChange={handleChange}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="country">Country *</label>
            <select
              id="country"
              name="country"
              value={address.country}
              onChange={handleChange}
              required
            >
              <option value="TZ">Tanzania</option>
              <option value="KE">Kenya</option>
              <option value="UG">Uganda</option>
              <option value="RW">Rwanda</option>
              <option value="BI">Burundi</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="phone">Phone Number *</label>
          <input
            type="tel"
            id="phone"
            name="phone"
            value={address.phone}
            onChange={handleChange}
            placeholder="+255712345678"
            required
          />
        </div>

        {showSameAsBilling && (
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={sameAsBilling}
                onChange={(e) => setSameAsBilling(e.target.checked)}
              />
              Use same address for billing
            </label>
          </div>
        )}

        <div className="form-actions">
          <button type="submit" className="btn-primary">
            Save Address
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddressForm;
```

#### 4. Shipping Method Selector

```javascript
// components/ShippingMethodSelector.jsx
import React, { useState, useEffect } from 'react';
import { getShippingMethods } from '../services/checkoutApi';

const ShippingMethodSelector = ({ 
  country = 'TZ', 
  weight = null, 
  onSelect, 
  selectedMethod 
}) => {
  const [methods, setMethods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadShippingMethods = async () => {
      try {
        setLoading(true);
        const data = await getShippingMethods(country, weight);
        setMethods(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadShippingMethods();
  }, [country, weight]);

  if (loading) {
    return <div className="loading">Loading shipping methods...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (methods.length === 0) {
    return <div className="no-methods">No shipping methods available for your location.</div>;
  }

  return (
    <div className="shipping-methods">
      <h3>Select Shipping Method</h3>
      
      {methods.map(method => (
        <div 
          key={method.id} 
          className={`shipping-method ${selectedMethod?.id === method.id ? 'selected' : ''}`}
          onClick={() => onSelect(method)}
        >
          <div className="method-info">
            <div className="method-header">
              <h4>{method.name}</h4>
              <span className="method-cost">
                {method.calculated_cost} {method.currency || 'TZS'}
              </span>
            </div>
            
            <p className="method-description">{method.description}</p>
            
            <div className="method-details">
              <span className="carrier">Carrier: {method.carrier}</span>
              <span className="delivery-time">
                Delivery: {method.estimated_delivery}
              </span>
            </div>
          </div>
          
          <div className="method-selector">
            <input
              type="radio"
              name="shipping_method"
              value={method.id}
              checked={selectedMethod?.id === method.id}
              onChange={() => onSelect(method)}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

export default ShippingMethodSelector;
```

#### 5. Payment Method Selector

```javascript
// components/PaymentMethodSelector.jsx
import React, { useState, useEffect } from 'react';
import { getPaymentMethods } from '../services/checkoutApi';

const PaymentMethodSelector = ({ onSelect, selectedMethod }) => {
  const [methods, setMethods] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadPaymentMethods = async () => {
      try {
        setLoading(true);
        const data = await getPaymentMethods();
        setMethods(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadPaymentMethods();
  }, []);

  if (loading) {
    return <div className="loading">Loading payment methods...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="payment-methods">
      <h3>Select Payment Method</h3>
      
      {methods.map(method => (
        <div 
          key={`${method.provider}-${method.method}`}
          className={`payment-method ${selectedMethod?.method === method.method ? 'selected' : ''}`}
          onClick={() => onSelect(method)}
        >
          <div className="method-info">
            <div className="method-header">
              <img src={method.icon} alt={method.name} className="method-icon" />
              <h4>{method.name}</h4>
            </div>
            
            <p className="method-description">{method.description}</p>
            
            {method.fees && (
              <div className="method-fees">
                <small>
                  Fee: {method.fees.percentage}%
                  {method.fees.fixed_amount > 0 && ` + ${method.fees.fixed_amount} TZS`}
                </small>
              </div>
            )}
          </div>
          
          <div className="method-selector">
            <input
              type="radio"
              name="payment_method"
              value={`${method.provider}-${method.method}`}
              checked={selectedMethod?.method === method.method}
              onChange={() => onSelect(method)}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

export default PaymentMethodSelector;
```

#### 6. Main Checkout Page

```javascript
// pages/CheckoutPage.jsx
import React, { useState, useEffect } from 'react';
import { useCheckout } from '../contexts/CheckoutContext';
import { useCart } from '../contexts/CartContext';
import AddressForm from '../components/AddressForm';
import ShippingMethodSelector from '../components/ShippingMethodSelector';
import PaymentMethodSelector from '../components/PaymentMethodSelector';
import OrderSummary from '../components/OrderSummary';
import { createOrder, initializePayment, processMobilePayment } from '../services/checkoutApi';

const CheckoutPage = () => {
  const { cart } = useCart();
  const {
    currentStep,
    shippingAddress,
    billingAddress,
    shippingMethod,
    paymentMethod,
    setStep,
    setShippingAddress,
    setBillingAddress,
    setShippingMethod,
    setPaymentMethod,
    setOrder,
    setLoading,
    setError
  } = useCheckout();

  const [orderSummary, setOrderSummary] = useState(null);

  // Step navigation
  const nextStep = () => {
    if (currentStep < 6) {
      setStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setStep(currentStep - 1);
    }
  };

  const handleShippingAddress = (address, sameAsBilling) => {
    setShippingAddress(address);
    if (sameAsBilling) {
      setBillingAddress(address);
    }
    nextStep();
  };

  const handleShippingMethod = (method) => {
    setShippingMethod(method);
    nextStep();
  };

  const handleBillingAddress = (address) => {
    setBillingAddress(address);
    nextStep();
  };

  const handlePaymentMethod = (method) => {
    setPaymentMethod(method);
    nextStep();
  };

  const handleCreateOrder = async () => {
    try {
      setLoading(true);
      
      const orderData = {
        shipping_address: shippingAddress,
        billing_address: billingAddress,
        shipping_method_id: shippingMethod.id,
        customer_notes: ''
      };

      const order = await createOrder(orderData);
      setOrder(order);
      setOrderSummary(order);
      nextStep();
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    try {
      setLoading(true);
      
      if (paymentMethod.method === 'paypal') {
        // Handle PayPal payment
        const paymentData = {
          order_id: orderSummary.id,
          payment_method: paymentMethod,
          return_url: `${window.location.origin}/checkout/success`,
          cancel_url: `${window.location.origin}/checkout/cancel`
        };
        
        const payment = await initializePayment(paymentData);
        
        // Redirect to payment provider
        window.location.href = payment.payment_url;
      } else {
        // Handle Azam Pay mobile money payment
        const phoneNumber = prompt('Enter your phone number for mobile payment:');
        
        const paymentData = {
          order_id: orderSummary.id,
          payment_method: paymentMethod,
          phone_number: phoneNumber
        };
        
        const payment = await processMobilePayment(paymentData);
        
        // Show payment instructions and poll for status
        alert(payment.message);
        // TODO: Implement status polling
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <AddressForm
            title="Shipping Address"
            initialAddress={shippingAddress}
            onSave={handleShippingAddress}
            showSameAsBilling={true}
          />
        );
      
      case 2:
        return (
          <ShippingMethodSelector
            country={shippingAddress?.country}
            weight={2.5} // TODO: Calculate from cart
            onSelect={handleShippingMethod}
            selectedMethod={shippingMethod}
          />
        );
      
      case 3:
        return billingAddress ? (
          <div className="billing-address-review">
            <h3>Billing Address</h3>
            {/* Display billing address */}
            <button onClick={nextStep}>Continue</button>
          </div>
        ) : (
          <AddressForm
            title="Billing Address"
            initialAddress={billingAddress}
            onSave={handleBillingAddress}
          />
        );
      
      case 4:
        return (
          <PaymentMethodSelector
            onSelect={handlePaymentMethod}
            selectedMethod={paymentMethod}
          />
        );
      
      case 5:
        return (
          <div className="order-review">
            <h3>Review Your Order</h3>
            <OrderSummary 
              cart={cart}
              shippingMethod={shippingMethod}
              shippingAddress={shippingAddress}
              billingAddress={billingAddress}
              paymentMethod={paymentMethod}
            />
            <button onClick={handleCreateOrder} disabled={loading}>
              {loading ? 'Creating Order...' : 'Place Order'}
            </button>
          </div>
        );
      
      case 6:
        return (
          <div className="payment-processing">
            <h3>Complete Payment</h3>
            {orderSummary && (
              <div>
                <p>Order Number: {orderSummary.order_number}</p>
                <p>Total: {orderSummary.total_amount} {orderSummary.currency}</p>
                <button onClick={handlePayment} disabled={loading}>
                  {loading ? 'Processing...' : 'Pay Now'}
                </button>
              </div>
            )}
          </div>
        );
      
      default:
        return <div>Invalid step</div>;
    }
  };

  return (
    <div className="checkout-page">
      <div className="checkout-container">
        <div className="checkout-steps">
          <div className="step-indicator">
            {[1, 2, 3, 4, 5, 6].map(step => (
              <div 
                key={step}
                className={`step ${currentStep >= step ? 'active' : ''}`}
              >
                {step}
              </div>
            ))}
          </div>
        </div>

        <div className="checkout-content">
          <div className="checkout-main">
            {renderStep()}
            
            <div className="checkout-navigation">
              {currentStep > 1 && (
                <button onClick={prevStep} className="btn-secondary">
                  Previous
                </button>
              )}
            </div>
          </div>

          <div className="checkout-sidebar">
            <OrderSummary 
              cart={cart}
              shippingMethod={shippingMethod}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
```

### CSS Styling Examples

```css
/* Checkout Page Styles */
.checkout-page {
  min-height: 100vh;
  background: #f8f9fa;
  padding: 2rem 0;
}

.checkout-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.checkout-steps {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.step-indicator {
  display: flex;
  justify-content: center;
  gap: 2rem;
}

.step {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e9ecef;
  color: #6c757d;
  font-weight: 600;
  transition: all 0.3s ease;
}

.step.active {
  background: #007bff;
  color: white;
}

.checkout-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.checkout-main {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.checkout-sidebar {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  height: fit-content;
  position: sticky;
  top: 2rem;
}

/* Address Form Styles */
.address-form h3 {
  margin-bottom: 1.5rem;
  color: #333;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #555;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #007bff;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.form-actions {
  margin-top: 2rem;
}

/* Shipping Method Styles */
.shipping-methods h3 {
  margin-bottom: 1.5rem;
}

.shipping-method {
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.shipping-method:hover {
  border-color: #007bff;
}

.shipping-method.selected {
  border-color: #007bff;
  background: #f0f8ff;
}

.method-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.method-header h4 {
  margin: 0;
  color: #333;
}

.method-cost {
  font-weight: 600;
  color: #007bff;
  font-size: 1.1rem;
}

.method-description {
  color: #666;
  margin: 0.5rem 0;
}

.method-details {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: #777;
}

/* Payment Method Styles */
.payment-methods h3 {
  margin-bottom: 1.5rem;
}

.payment-method {
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.payment-method:hover {
  border-color: #28a745;
}

.payment-method.selected {
  border-color: #28a745;
  background: #f0fff4;
}

.method-icon {
  width: 40px;
  height: 40px;
  object-fit: contain;
  margin-right: 1rem;
}

.method-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.method-fees {
  margin-top: 0.5rem;
}

/* Button Styles */
.btn-primary {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-secondary:hover {
  background: #545b62;
}

/* Responsive Design */
@media (max-width: 768px) {
  .checkout-content {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .step-indicator {
    gap: 1rem;
  }
  
  .step {
    width: 30px;
    height: 30px;
    font-size: 0.9rem;
  }
}
```

## Error Handling

### Common Error Scenarios

1. **Invalid Address**: Validate all required fields
2. **Shipping Not Available**: Show appropriate message for unsupported regions
3. **Payment Failures**: Handle different failure reasons with retry options
4. **Session Timeouts**: Refresh authentication and retry
5. **Network Errors**: Show retry buttons

### Error Handling Example

```javascript
const handleCheckoutError = (error, step) => {
  console.error(`Checkout error at step ${step}:`, error);
  
  switch (step) {
    case 'shipping':
      if (error.message.includes('not available')) {
        showError('Shipping is not available to your location. Please contact support.');
      }
      break;
    
    case 'payment':
      if (error.message.includes('insufficient funds')) {
        showError('Payment failed due to insufficient funds. Please try a different payment method.');
      } else if (error.message.includes('timeout')) {
        showError('Payment request timed out. Please try again.');
      }
      break;
    
    default:
      showError('An unexpected error occurred. Please try again.');
  }
};
```

## Testing

### Test Cases to Implement

1. **Address Validation**
   - ✅ Required fields validation
   - ✅ Phone number format validation
   - ✅ Country-specific postal code validation

2. **Shipping Methods**
   - ✅ Available methods for different countries
   - ✅ Cost calculation accuracy
   - ✅ Weight limits validation

3. **Payment Processing**
   - ✅ Card payment flow
   - ✅ Mobile money payment flow
   - ✅ Payment status polling
   - ✅ Error handling and retries

4. **Order Creation**
   - ✅ Cart to order conversion
   - ✅ Address preservation
   - ✅ Order number generation
   - ✅ Status tracking

This comprehensive documentation provides everything your frontend team needs to implement a complete checkout flow with multiple payment methods, shipping options, and proper error handling!
