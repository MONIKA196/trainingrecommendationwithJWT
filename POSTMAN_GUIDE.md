# Postman API Testing Guide

This guide describes how to test the new JWT-protected API endpoints using Postman.

## 1. Authentication (Login)
- **Method**: `POST`
- **URL**: `http://localhost:5000/api/login`
- **Body**: Select `raw` and `JSON`
- **Content**:
  ```json
  {
      "username": "your_username",
      "password": "your_password"
  }
  ```
- **Response**:
  You will receive an `access_token`. Copy this token for the next steps.

## 2. Get Profile (Protected)
- **Method**: `GET`
- **URL**: `http://localhost:5000/api/profile`
- **Headers**:
  - `Authorization`: `Bearer <YOUR_ACCESS_TOKEN>`
- **Response**:
  Returns your user profile data.

## 3. OCR (Image Upload - Protected)
- **Method**: `POST`
- **URL**: `http://localhost:5000/api/ocr`
- **Headers**:
  - `Authorization`: `Bearer <YOUR_ACCESS_TOKEN>`
- **Body**: Select `form-data`
  - Key: `file`, Value: Select an image file (type 'File')
- **Response**:
  Returns the extracted text and key points from Gemini.

