# User Registration Flow

## 1. Flow Diagram
```
User Submits Registration Form (email, password, full_name, terms, privacy)
                   │
                   ▼
       Input & Password Validation (min 8 chars)
                   │
                   ▼
       Duplicate Email Check (409 Conflict if exists)
                   │
                   ▼
       Password Hashed (Bcrypt / Argon2id)
                   │
                   ▼
       Create User Record (status="pending_verification", is_verified=False)
                   │
                   ▼
       Generate 32-byte Opaque Token -> Hash with SHA-256
                   │
                   ▼
       Store Token in email_verification_tokens (expires in 30 mins)
                   │
                   ▼
       Dispatch Verification Email -> Return 201 Created
```

## 2. API Contract
- **Endpoint:** `POST /api/v1/auth/register`
- **Request:**
  ```json
  {
    "email": "user@example.com",
    "password": "Password123!",
    "confirm_password": "Password123!",
    "full_name": "Alex Mercer",
    "native_language": "Spanish",
    "terms_accepted": true,
    "privacy_accepted": true
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "id": "uuid",
      "email": "user@example.com",
      "status": "pending_verification",
      "is_verified": false
    },
    "message": "Registration successful. Please check your email to verify your account."
  }
  ```
