# API Documentation

Complete API documentation for the Supermarket microservices application.

## Overview

The application exposes three main APIs:
- **BFF (Backend for Frontend)**: Main API gateway for client applications
- **Core Service**: Business logic and data operations
- **UI Service**: Web interface

## BFF Service API

Base URL: `http://localhost:5000`

### Health Check

**Endpoint**: `GET /health`

**Description**: Check BFF service health status

**Response**:
```json
{
  "status": "healthy",
  "service": "bff",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

**Status Code**: 200

### Metrics

**Endpoint**: `GET /metrics`

**Description**: Prometheus metrics in text format

**Response**: Prometheus format metrics

**Status Code**: 200

### Get All Products

**Endpoint**: `GET /api/products`

**Description**: Retrieve list of all products

**Query Parameters**: None

**Response**:
```json
[
  {
    "id": "1",
    "name": "Milk",
    "price": 3.99,
    "category": "Dairy"
  },
  {
    "id": "2",
    "name": "Bread",
    "price": 2.49,
    "category": "Bakery"
  }
]
```

**Status Code**: 200

**Example**:
```bash
curl http://localhost:5000/api/products
```

### Get Product Details

**Endpoint**: `GET /api/products/{product_id}`

**Description**: Retrieve specific product details

**Path Parameters**:
- `product_id` (string, required): Product ID

**Response**:
```json
{
  "id": "1",
  "name": "Milk",
  "price": 3.99,
  "category": "Dairy"
}
```

**Status Codes**:
- 200: Product found
- 500: Error

**Example**:
```bash
curl http://localhost:5000/api/products/1
```

### Create Order

**Endpoint**: `POST /api/orders`

**Description**: Create a new order

**Request Body**:
```json
{
  "items": [
    {
      "id": "1",
      "name": "Milk",
      "price": 3.99,
      "quantity": 2
    },
    {
      "id": "4",
      "name": "Apples",
      "price": 1.99,
      "quantity": 3
    }
  ]
}
```

**Response**:
```json
{
  "id": "a1b2c3d4",
  "items": [...],
  "total": 13.95,
  "status": "created",
  "created_at": "2024-01-15T10:30:00.000000"
}
```

**Status Codes**:
- 201: Order created
- 500: Error

**Example**:
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id": "1", "name": "Milk", "price": 3.99, "quantity": 2}
    ]
  }'
```

### Get Order Details

**Endpoint**: `GET /api/orders/{order_id}`

**Description**: Retrieve specific order details

**Path Parameters**:
- `order_id` (string, required): Order ID

**Response**:
```json
{
  "id": "a1b2c3d4",
  "items": [...],
  "total": 13.95,
  "status": "created",
  "created_at": "2024-01-15T10:30:00.000000"
}
```

**Status Codes**:
- 200: Order found
- 500: Error

**Example**:
```bash
curl http://localhost:5000/api/orders/a1b2c3d4
```

## Core Service API

Base URL: `http://localhost:5001`

### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "service": "core-service",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

### Metrics

**Endpoint**: `GET /metrics`

**Description**: Prometheus metrics

**Response**: Prometheus format metrics

### Get All Products

**Endpoint**: `GET /products`

**Response**:
```json
[
  {
    "id": "1",
    "name": "Milk",
    "price": 3.99,
    "category": "Dairy"
  }
]
```

**Example**:
```bash
curl http://localhost:5001/products
```

### Get Product Details

**Endpoint**: `GET /products/{product_id}`

**Path Parameters**:
- `product_id` (string, required): Product ID

**Response**:
```json
{
  "id": "1",
  "name": "Milk",
  "price": 3.99,
  "category": "Dairy"
}
```

**Status Codes**:
- 200: Success
- 404: Product not found

### Create Product

**Endpoint**: `POST /products`

**Request Body**:
```json
{
  "name": "Cheese",
  "price": 5.99,
  "category": "Dairy"
}
```

**Response**:
```json
{
  "id": "a1b2c3d4",
  "name": "Cheese",
  "price": 5.99,
  "category": "Dairy"
}
```

**Status Code**: 201

**Example**:
```bash
curl -X POST http://localhost:5001/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cheese",
    "price": 5.99,
    "category": "Dairy"
  }'
```

### Create Order

**Endpoint**: `POST /orders`

**Request Body**:
```json
{
  "items": [
    {
      "id": "1",
      "name": "Milk",
      "price": 3.99,
      "quantity": 2
    }
  ]
}
```

**Response**:
```json
{
  "id": "a1b2c3d4",
  "items": [...],
  "total": 7.98,
  "status": "created",
  "created_at": "2024-01-15T10:30:00.000000"
}
```

**Status Code**: 201

### Get Order Details

**Endpoint**: `GET /orders/{order_id}`

**Path Parameters**:
- `order_id` (string, required): Order ID

**Response**:
```json
{
  "id": "a1b2c3d4",
  "items": [...],
  "total": 7.98,
  "status": "created",
  "created_at": "2024-01-15T10:30:00.000000"
}
```

**Status Codes**:
- 200: Success
- 404: Order not found

### Update Order Status

**Endpoint**: `PUT /orders/{order_id}/status`

**Path Parameters**:
- `order_id` (string, required): Order ID

**Request Body**:
```json
{
  "status": "shipped"
}
```

**Response**:
```json
{
  "id": "a1b2c3d4",
  "items": [...],
  "total": 7.98,
  "status": "shipped",
  "created_at": "2024-01-15T10:30:00.000000"
}
```

**Status Code**: 200

**Example**:
```bash
curl -X PUT http://localhost:5001/orders/a1b2c3d4/status \
  -H "Content-Type: application/json" \
  -d '{"status": "shipped"}'
```

## UI Service API

Base URL: `http://localhost:5002`

### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "service": "ui-service",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

### Metrics

**Endpoint**: `GET /metrics`

**Description**: Prometheus metrics

**Response**: Prometheus format metrics

### Get Home Page

**Endpoint**: `GET /`

**Response**: HTML page

**Status Code**: 200

### Get Products Page

**Endpoint**: `GET /products`

**Response**: HTML page with product list

**Status Code**: 200

### Get Orders Page

**Endpoint**: `GET /orders`

**Response**: HTML page with order list

**Status Code**: 200

### Get Configuration

**Endpoint**: `GET /config`

**Response**:
```json
{
  "api_base_url": "http://bff-service:5000",
  "environment": "production"
}
```

**Status Code**: 200

**Example**:
```bash
curl http://localhost:5002/config
```

## Common Workflows

### Browse Products and Create Order

1. Get all products:
```bash
curl http://localhost:5000/api/products
```

2. Create order with selected products:
```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id": "1", "name": "Milk", "price": 3.99, "quantity": 1},
      {"id": "2", "name": "Bread", "price": 2.49, "quantity": 2}
    ]
  }'
```

3. Get order details:
```bash
curl http://localhost:5000/api/orders/[order_id]
```

### Add New Product and Verify

1. Create product:
```bash
curl -X POST http://localhost:5001/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Yogurt",
    "price": 4.99,
    "category": "Dairy"
  }'
```

2. Get all products to verify:
```bash
curl http://localhost:5001/products
```

3. Get specific product:
```bash
curl http://localhost:5001/products/[product_id]
```

### Order Fulfillment Workflow

1. Create order:
```bash
ORDER_ID=$(curl -X POST http://localhost:5001/orders \
  -H "Content-Type: application/json" \
  -d '{...}' | jq -r '.id')
```

2. Check order status:
```bash
curl http://localhost:5001/orders/$ORDER_ID
```

3. Update status to shipped:
```bash
curl -X PUT http://localhost:5001/orders/$ORDER_ID/status \
  -H "Content-Type: application/json" \
  -d '{"status": "shipped"}'
```

4. Verify status:
```bash
curl http://localhost:5001/orders/$ORDER_ID
```

## Error Handling

All APIs return appropriate HTTP status codes:

- **200**: Success
- **201**: Created
- **400**: Bad Request
- **404**: Not Found
- **500**: Internal Server Error
- **503**: Service Unavailable

Error Response Format:
```json
{
  "error": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. Production deployment should implement rate limiting via API Gateway or service mesh.

## Authentication

Currently, no authentication is required. Production deployment should implement:
- API keys
- OAuth 2.0
- JWT tokens
- mTLS for service-to-service communication

## Monitoring

All APIs emit metrics in Prometheus format at `/metrics` endpoint:

```promql
# Request metrics
[service]_requests_total
[service]_request_duration_seconds

# Business metrics
orders_created_total
products_queried_total
```

Access metrics:
```bash
curl http://localhost:5000/metrics
curl http://localhost:5001/metrics
curl http://localhost:5002/metrics
```
