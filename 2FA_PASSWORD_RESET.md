# 2FA and Password Reset Implementation

This document describes the 2FA (Two-Factor Authentication) and Password Reset functionality implemented in the backend.

## Features Added

### 1. Two-Factor Authentication (2FA)

#### Enable 2FA
- **Endpoint**: `POST /api/v1/auth/2fa/enable`
- **Body**: `{ "email": "user@example.com" }`
- **Response**: Sends a 6-digit verification code to the user's email
- **Code expires**: 10 minutes

#### Verify 2FA Code
- **Endpoint**: `POST /api/v1/auth/2fa/verify`
- **Body**: `{ "email": "user@example.com", "code": "123456" }`
- **Response**: Enables 2FA for the user

#### Login with 2FA
1. User logs in with email/password
2. If 2FA is enabled, receives `requires_2fa: true` in response
3. System sends 6-digit code to user's email
4. User submits code via `/api/v1/auth/2fa/complete-login`
5. Receives access and refresh tokens

#### Complete 2FA Login
- **Endpoint**: `POST /api/v1/auth/2fa/complete-login`
- **Body**: `{ "email": "user@example.com", "code": "123456" }`
- **Response**: Returns JWT tokens after successful verification

#### Disable 2FA
- **Endpoint**: `POST /api/v1/auth/2fa/disable`
- **Authorization**: Requires Bearer token
- **Response**: Disables 2FA for the authenticated user

### 2. Password Reset

#### Request Password Reset
- **Endpoint**: `POST /api/v1/auth/forgot-password`
- **Body**: `{ "email": "user@example.com" }`
- **Response**: Sends password reset link to email
- **Token expires**: 1 hour
- **Note**: Always returns success to prevent email enumeration

#### Reset Password with Token
- **Endpoint**: `POST /api/v1/auth/reset-password`
- **Body**: `{ "token": "reset_token_here", "new_password": "newpass123" }`
- **Response**: Resets password and clears reset token

#### Change Password (Authenticated)
- **Endpoint**: `POST /api/v1/auth/change-password`
- **Authorization**: Requires Bearer token
- **Body**: `{ "current_password": "oldpass", "new_password": "newpass123" }`
- **Response**: Changes password after verifying current password

## Database Schema Updates

### User Model Extensions

```python
{
    # Existing fields
    "email": "user@example.com",
    "hashed_password": "...",
    "full_name": "John Doe",
    "role": "user",
    "is_active": true,

    # New 2FA fields
    "two_factor_enabled": false,
    "two_factor_secret": null,
    "two_factor_code": "123456",
    "two_factor_code_expires": "2025-11-24T10:30:00",

    # New password reset fields
    "reset_token": "secure_random_token",
    "reset_token_expires": "2025-11-24T11:00:00",

    # Timestamps
    "created_at": "2025-11-24T10:00:00",
    "updated_at": "2025-11-24T10:00:00"
}
```

## Email Configuration

### Development Mode
Currently using mock email sender that prints to console. Perfect for development and testing.

### Production Setup
To use real email in production, update `.env` file:

```env
FRONTEND_URL=https://your-frontend.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@stockpredict.com
```

Then update `app/core/email.py` to use real SMTP instead of mock.

## Security Features

1. **OTP Codes**: 6-digit random codes, expire after 10 minutes
2. **Reset Tokens**: Cryptographically secure random tokens (32 bytes), expire after 1 hour
3. **Password Hashing**: Bcrypt hashing for all passwords
4. **Email Enumeration Prevention**: Password reset always returns success
5. **Token Cleanup**: Expired codes/tokens are cleared after use

## API Flow Examples

### Enable 2FA Flow

```bash
# 1. Request 2FA enable (sends code to email)
curl -X POST http://localhost:8000/api/v1/auth/2fa/enable \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# 2. Verify code to enable 2FA
curl -X POST http://localhost:8000/api/v1/auth/2fa/verify \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "code": "123456"}'
```

### Login with 2FA Flow

```bash
# 1. Login (returns requires_2fa: true if enabled)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Response: {"access_token": "", "refresh_token": "", "requires_2fa": true}

# 2. Check email for 6-digit code

# 3. Complete login with 2FA code
curl -X POST http://localhost:8000/api/v1/auth/2fa/complete-login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "code": "123456"}'

# Response: {"access_token": "jwt_token", "refresh_token": "jwt_token"}
```

### Password Reset Flow

```bash
# 1. Request password reset (sends email with token)
curl -X POST http://localhost:8000/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# 2. Check email for reset link with token

# 3. Reset password with token
curl -X POST http://localhost:8000/api/v1/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"token": "reset_token_from_email", "new_password": "newpassword123"}'
```

## Frontend Integration

The frontend already has pages for these features:
- `/auth/2fa` - 2FA verification page
- `/auth/forgot-password` - Password reset request page
- `/auth/reset-password` - Password reset form with token

Update the frontend API client to use these new endpoints.

## Dependencies

Added to `requirements.txt`:
- `pyotp==2.9.0` - For OTP generation
- `fastapi-mail==1.4.1` - For email functionality (optional, using mock for now)

## Testing

1. **Test 2FA Enable**: Request code, check console output, verify code
2. **Test 2FA Login**: Login with 2FA enabled user, verify code flow
3. **Test Password Reset**: Request reset, check console for token, reset password
4. **Test Expiration**: Wait for codes/tokens to expire, verify they're rejected

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Notes

- All timestamps use UTC
- Email mock prints to console in development
- Tokens are securely generated using `secrets` module
- All endpoints have proper error handling
- Password validation requires minimum 6 characters
