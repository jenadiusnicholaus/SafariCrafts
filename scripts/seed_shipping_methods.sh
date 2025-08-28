#!/bin/bash
# Script to seed shipping methods using the API

API_URL="http://127.0.0.1:8082/api/v1/shipping/methods/?country=TZ"

# You can set your JWT token here
JWT_TOKEN="YOUR_JWT_TOKEN_HERE"

curl -X 'GET' \
  "$API_URL" \
  -H "accept: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN"

echo "\nShipping methods seeded (fetched) from $API_URL"
