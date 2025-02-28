# Loan Management System API Documentation

This document provides detailed information about the Loan Management System API endpoints, request/response formats, and testing instructions.

## Table of Contents
- [Setup Instructions](#setup-and-installation)
- [Authentication Endpoints](#authentication-endpoints)
- [Loan Management Endpoints](#loan-management-endpoints)
- [Error Handling](#error-handling)
- [Testing Instructions](#testing-instructions)


## Setup and Installation

### Prerequisites

- Python 3.8+
- Django 4.0+
- PostgreSQL (recommended) or SQLite

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd loan_management
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Change .env accordingly to your specification.

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. import Postman_collection.json in postman client to easily test API endpoints.



## Features

- User registration with email verification
- JWT-based authentication
- Loan creation and management
- Installment tracking and payment
- Loan foreclosure with interest discounts
- Admin-specific controls


## Authentication Endpoints

### Register User
Creates a new user account and sends a verification email.

- **URL**: `/auth/register/`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "first_name": "string",
    "last_name": "string"
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**:
    ```json
    {
      "status": "success",
      "message": "Please check your email to complete registration"
    }
    ```
- **Error Response**:
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "status": "error",
      "message": { "field_name": ["error message"] }
    }
    ```

### Verify Email
Activates a user account using the verification link sent to their email.

- **URL**: `/auth/verify-email/<uidb64>/<token>/`
- **Method**: `GET`
- **Auth Required**: No
- **URL Parameters**:
  - `uidb64`: Base64 encoded user ID
  - `token`: Verification token
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "status": "success",
      "message": "Email verified successfully. You can now login."
    }
    ```
- **Error Response**:
  - **Code**: 400 BAD REQUEST
  - **Content**:
    ```json
    {
      "status": "error",
      "message": "Activation link is invalid or expired."
    }
    ```

### Login
Authenticates a user and provides JWT tokens.

- **URL**: `/auth/login/`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "status": "success",
      "data": {
        "refresh": "string",
        "access": "string",
        "user_id": "integer",
        "username": "string",
        "is_admin": "boolean"
      }
    }
    ```
- **Error Response**:
  - **Code**: 401 UNAUTHORIZED
  - **Content**:
    ```json
    {
      "status": "error",
      "message": "Invalid username or password"
    }
    ```

### Logout
Logs out the current user.

- **URL**: `/auth/logout/`
- **Method**: `POST`
- **Auth Required**: Yes (Bearer Token)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "status": "success",
      "message": "Successfully logged out. Please discard your token."
    }
    ```

### Register Admin
Creates a new admin user with elevated privileges.

- **URL**: `/auth/admin/register/`
- **Method**: `POST`
- **Auth Required**: No (Note: In production, this should be restricted to admin users)
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "first_name": "string",
    "last_name": "string"
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**:
    ```json
    {
      "status": "success",
      "data": {
        "user_id": "integer",
        "username": "string",
        "is_admin": true,
        "refresh": "string",
        "access": "string"
      }
    }
    ```

### Token Refresh
Refreshes an expired access token using a valid refresh token.

- **URL**: `/auth/token/refresh/`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "refresh": "string"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "access": "string"
    }
    ```

## Loan Management Endpoints

### Get Loans
Retrieves all loans for the authenticated user. Admins can view all loans.

- **URL**: `/loans/`
- **Method**: `GET`
- **Auth Required**: Yes (Bearer Token)
- **URL Parameters**: Optional
  - `status`: Filter loans by status (e.g., ACTIVE, CLOSED, FORECLOSED)
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "status": "success",
      "data": {
        "loans": [
          {
            "loan_id": "string",
            "amount": "number",
            "tenure": "integer",
            "interest_rate": "number",
            "monthly_installment": "number",
            "total_amount": "number",
            "amount_paid": "number",
            "amount_remaining": "number",
            "next_due_date": "date",
            "status": "string",
            "created_at": "datetime"
          }
        ]
      }
    }
    ```

### Create Loan
Creates a new loan for the authenticated user.

- **URL**: `/loans/`
- **Method**: `POST`
- **Auth Required**: Yes (Bearer Token)
- **Request Body**:
  ```json
  {
    "amount": "number",
    "tenure": "integer",
    "interest_rate": "number"
  }
  ```
- **Success Response**:
  - **Code**: 201 CREATED
  - **Content**:
    ```json
    {
      "status": "success",
      "data": {
        "loan_id": "string",
        "amount": "number",
        "tenure": "integer",
        "interest_rate": "string",
        "monthly_installment": "number",
        "total_interest": "number",
        "total_amount": "number",
        "payment_schedule": [
          {
            "installment_no": "integer",
            "amount": "number",
            "due_date": "date",
            "status": "string"
          }
        ]
      }
    }
    ```

### Get Loan Details
Retrieves detailed information about a specific loan.

- **URL**: `/loans/detail/`
- **Method**: `POST`
- **Auth Required**: Yes (Bearer Token)
- **Request Body**:
  ```json
  {
    "loan_id": "string"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "status": "success",
      "data": {
        "loan_id": "string",
        "amount": "number",
        "tenure": "integer",
        "interest_rate": "string",
        "monthly_installment": "number",
        "total_interest": "number",
        "total_amount": "number",
        "amount_paid": "number",
        "amount_remaining": "number",
        "next_due_date": "date",
        "status": "string",
        "created_at": "datetime",
        "payment_schedule": [
          {
            "installment_no": "integer",
            "amount": "number",
            "due_date": "date",
            "status": "string"
          }
        ]
      }
    }
    ```

### Pay Loan Installment
Pays a specific installment for a loan.

- **URL**: `/loans/pay/`
- **Method**: `POST`
- **Auth Required**: Yes (Bearer Token)
- **Request Body**:
  ```json
  {
    "loan_id": "string",
    "installment_no": "integer"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "status": "success",
      "message": "Installment X paid successfully.",
      "data": {
        "loan_id": "string",
        "amount_paid": "number",
        "amount_remaining": "number",
        "next_due_date": "date",
        "status": "string",
        "payment_schedule": [
          {
            "installment_no": "integer",
            "amount": "number",
            "due_date": "date",
            "status": "string"
          }
        ]
      }
    }
    ```

### Foreclose Loan
Closes a loan by paying off the remaining balance with a discount.

- **URL**: `/loans/foreclose/`
- **Method**: `POST`
- **Auth Required**: Yes (Bearer Token)
- **Request Body**:
  ```json
  {
    "loan_id": "string"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "status": "success",
      "message": "Loan foreclosed successfully.",
      "data": {
        "loan_id": "string",
        "amount_paid": "number",
        "foreclosure_amount": "number",
        "foreclosure_discount": "number",
        "final_settlement_amount": "number",
        "status": "FORECLOSED"
      }
    }
    ```

### Delete Loan
Deletes a loan (admin only).

- **URL**: `/loans-delete/`
- **Method**: `DELETE`
- **Auth Required**: Yes (Admin Bearer Token)
- **Request Body**:
  ```json
  {
    "loan_id": "string"
  }
  ```
- **Success Response**:
  - **Code**: 200 OK
  - **Content**:
    ```json
    {
      "status": "success",
      "message": "Loan deleted successfully."
    }
    ```

## Error Handling

The API uses standard HTTP status codes along with consistent error response formats:

- **400 Bad Request**:
  ```json
  {
    "error": "Bad Request",
    "message": "The request could not be understood or was missing required parameters."
  }
  ```

- **403 Forbidden**:
  ```json
  {
    "error": "Forbidden",
    "message": "You do not have permission to access this resource."
  }
  ```

- **404 Not Found**:
  ```json
  {
    "error": "Not Found",
    "message": "The requested resource was not found on this server."
  }
  ```

- **500 Internal Server Error**:
  ```json
  {
    "error": "Internal Server Error",
    "message": "An unexpected error occurred on the server."
  }
  ```

## Testing Instructions

Below are detailed steps to test the Loan Management API using Postman or any other API testing tool.

## API Testing Guide

### User Authentication

#### 1. Register a Regular User

- **Endpoint**: `POST /auth/register/`
- **Request Body**:
  ```json
  {
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "securepassword123",
    "first_name": "Test",
    "last_name": "User"
  }
  ```
- **Expected Response**:
  ```json
  {
    "status": "success",
    "message": "Please check your email to complete registration"
  }
  ```
- **Notes**: 
  - In a development environment, check the console/terminal for the email verification link
  - For production, configure proper email settings in settings.py

#### 2. Verify Email

- **Endpoint**: `GET /auth/verify-email/<uidb64>/<token>/`
- **How to Test**: 
  - Get the verification link from the email (or console in development)
  - Open the link in a browser or send a GET request to the URL
- **Expected Response**:
  ```json
  {
    "status": "success",
    "message": "Email verified successfully. You can now login."
  }
  ```

#### 3. Login

- **Endpoint**: `POST /auth/login/`
- **Request Body**:
  ```json
  {
    "username": "testuser",
    "password": "securepassword123"
  }
  ```
- **Expected Response**:
  ```json
  {
    "status": "success",
    "data": {
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
      "user_id": 1,
      "username": "testuser",
      "is_admin": false
    }
  }
  ```
- **Notes**: 
  - Save both the access and refresh tokens for subsequent requests
  - The access token typically expires after 15-60 minutes

#### 4. Create an Admin User

- **Endpoint**: `POST /auth/admin/register/`
- **Request Body**:
  ```json
  {
    "username": "adminuser",
    "email": "admin@example.com",
    "password": "secureadminpass456",
    "first_name": "Admin",
    "last_name": "User"
  }
  ```
- **Expected Response**:
  ```json
  {
    "status": "success",
    "data": {
      "user_id": 2,
      "username": "adminuser",
      "is_admin": true,
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."
    }
  }
  ```
- **Notes**: 
  - For production environments, this endpoint should be secured to allow only existing admins to create new admins

### Loan Management

#### 1. Create a New Loan

- **Endpoint**: `POST /loans/`
- **Headers**: 
  ```
  Authorization: Bearer <access_token>
  ```
- **Request Body**:
  ```json
  {
    "amount": 10000,
    "tenure": 12,
    "interest_rate": 10.5
  }
  ```
- **Expected Response**:
  ```json
  {
    "status": "success",
    "data": {
      "loan_id": "LOAN001",
      "amount": 10000.0,
      "tenure": 12,
      "interest_rate": "10.5% yearly",
      "monthly_installment": 879.16,
      "total_interest": 550.0,
      "total_amount": 10550.0,
      "payment_schedule": [
        {
          "installment_no": 1,
          "amount": 879.16,
          "due_date": "2025-03-31",
          "status": "PENDING"
        },
        // Additional installments...
      ]
    }
  }
  ```

#### 2. Get All Loans

- **Endpoint**: `GET /loans/`
- **Headers**: 
  ```
  Authorization: Bearer <access_token>
  ```
- **Optional Query Parameters**:
  ```
  ?status=ACTIVE
  ```
- **Expected Response**:
  ```json
  {
    "status": "success",
    "data": {
      "loans": [
        {
          "loan_id": "LOAN001",
          "amount": 10000.0,
          "tenure": 12,
          "interest_rate": 10.5,
          "monthly_installment": 879.16,
          "total_amount": 10550.0,
          "amount_paid": 0.0,
          "amount_remaining": 10550.0,
          "next_due_date": "2025-03-31",
          "status": "ACTIVE",
          "created_at": "2025-02-28T12:00:00Z"
        }
      ]
    }
  }
  ```

#### 3. View Loan Details

- **Endpoint**: `POST /loans/detail/`
- **Headers**: 
  ```
  Authorization: Bearer <access_token>
  ```
- **Request Body**:
  ```json
  {
    "loan_id": "LOAN001"
  }
  ```
- **Expected Response**:
  ```json
  {
    "status": "success",
    "data": {
      "loan_id": "LOAN001",
      "amount": 10000.0,
      "tenure": 12,
      "interest_rate": "10.5% yearly",
      "monthly_installment": 879.16,
      "total_interest": 550.0,
      "total_amount": 10550.0,
      "amount_paid": 0.0,
      "amount_remaining": 10550.0,
      "next_due_date": "2025-03-31",
      "status": "ACTIVE",
      "created_at": "2025-02-28T12:00:00Z",
      "payment_schedule": [
        {
          "installment_no": 1,
          "amount": 879.16,
          "due_date": "2025-03-31",
          "status": "PENDING"
        },
        // Additional installments...
      ]
    }
  }
  ```

#### 4. Pay a Loan Installment

- **Endpoint**: `POST /loans/pay/`
- **Headers**: 
  ```
  Authorization: Bearer <access_token>
  ```
- **Request Body**:
  ```json
  {
    "loan_id": "LOAN001",
    "installment_no": 1
  }
  ```
- **Expected Response**:
  ```json
  {
    "status": "success",
    "message": "Installment 1 paid successfully.",
    "data": {
      "loan_id": "LOAN001",
      "amount_paid": 879.16,
      "amount_remaining": 9670.84,
      "next_due_date": "2025-04-30",
      "status": "ACTIVE",
      "payment_schedule": [
        {
          "installment_no": 1,
          "amount": 879.16,
          "due_date": "2025-03-31",
          "status": "PAID"
        },
        {
          "installment_no": 2,
          "amount": 879.16,
          "due_date": "2025-04-30",
          "status": "PENDING"
        },
        // Additional installments...
      ]
    }
  }
  ```

#### 5. Foreclose a Loan

- **Endpoint**: `POST /loans/foreclose/`
- **Headers**: 
  ```
  Authorization: Bearer <access_token>
  ```
- **Request Body**:
  ```json
  {
    "loan_id": "LOAN001"
  }
  ```
- **Expected Response**:
  ```json
  {
    "status": "success",
    "message": "Loan foreclosed successfully.",
    "data": {
      "loan_id": "LOAN001",
      "amount_paid": 10050.0,
      "foreclosure_amount": 9670.84,
      "foreclosure_discount": 500.0,
      "final_settlement_amount": 9170.84,
      "status": "FORECLOSED"
    }
  }
  ```

#### 6. Delete a Loan (Admin Only)

- **Endpoint**: `DELETE /loans-delete/`
- **Headers**: 
  ```
  Authorization: Bearer <admin_access_token>
  ```
- **Request Body**:
  ```json
  {
    "loan_id": "LOAN001"
  }
  ```
- **Expected Response**:
  ```json
  {
    "status": "success",
    "message": "Loan deleted successfully."
  }
  ```

### Testing Error Scenarios

#### 1. Unauthorized Access

- **Test**: Try to access a protected endpoint without a token
- **Endpoint**: `GET /loans/`
- **Expected Response**:
  ```json
  {
    "detail": "Authentication credentials were not provided."
  }
  ```

#### 2. Invalid Loan ID

- **Test**: Try to view details of a non-existent loan
- **Endpoint**: `POST /loans/detail/`
- **Request Body**:
  ```json
  {
    "loan_id": "NONEXISTENT"
  }
  ```
- **Expected Response**:
  ```json
  {
    "error": "Not Found",
    "message": "The requested resource was not found on this server."
  }
  ```

#### 3. Insufficient Permissions

- **Test**: Try to delete a loan using a regular user account
- **Endpoint**: `DELETE /loans-delete/`
- **Headers**: 
  ```
  Authorization: Bearer <regular_user_token>
  ```
- **Request Body**:
  ```json
  {
    "loan_id": "LOAN001"
  }
  ```
- **Expected Response**:
  ```json
  {
    "error": "Forbidden",
    "message": "You do not have permission to access this resource."
  }
  ```

## Troubleshooting

### Common Issues

1. **Email Verification Not Working**
   - Check your email settings in settings.py
   - Check spam mail to check if its coming there

2. **Authentication Errors**
   - Ensure your access token is valid and not expired
   - Use refresh token to get a new access token if needed

3. **Permission Denied**
   - Verify that you're using the correct account type for the operation
   - Admin operations require an admin user token

### Refreshing Access Token

If your access token expires, use the refresh endpoint:

- **Endpoint**: `POST /auth/token/refresh/`
- **Request Body**:
  ```json
  {
    "refresh": "your-refresh-token"
  }
  ```
- **Expected Response**:
  ```json
  {
    "access": "new-access-token"
  }
  ```

## API Response Status Codes

- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **500**: Internal Server Error