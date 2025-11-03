# Troubleshooting API Errors - JLC Application

## Common API Errors and Solutions

### Error: `/auth-api/auth/security/users:1` - Status 500, "Method Not Allowed"

**Symptom**: Browser console shows error:
```
Failed to load resource: the server responded with a status of 500 ()
{"detail":"Method Not Allowed"}
URL: /auth-api/auth/security/users:1
```

**Possible Causes**:

1. **RTK Query Cache Tag Appended to URL**
   - The `:1` suggests RTK Query might be incorrectly appending a tag to the URL
   - This can happen if there's a configuration issue with the API slice

2. **Authentication Token Expired**
   - The user session may have expired, causing API calls to fail
   - Solution: Refresh the page and log in again

3. **Method Mismatch**
   - The frontend might be using the wrong HTTP method (GET/POST/PUT/DELETE)
   - Backend endpoint: `POST /auth/security/users` (Create User)

**Solutions**:

#### Solution 1: Check RTK Query Configuration
Verify the `securityApi.ts` endpoint configuration:

```typescript
// Correct configuration
createUser: builder.mutation<any, CreateUserRequest>({
  query: (data) => ({
    url: '/users',  // Should NOT have dynamic parameters here
    method: 'POST',
    body: data,
  }),
}),
```

#### Solution 2: Clear Browser Cache and Refresh
1. Open DevTools (F12)
2. Go to Application/Storage tab
3. Click "Clear site data"
4. Refresh the page (Ctrl+Shift+R)

#### Solution 3: Check Authentication Status
1. Verify you're logged in (check localStorage for `token`)
2. If session expired, log out and log back in
3. Check token expiration in JWT

#### Solution 4: Verify Backend Endpoint
Check if the backend endpoint is properly registered:

```bash
# Check backend logs
tail -f /var/log/supervisor/backend.err.log

# Look for endpoint registration
# Should see: POST /auth/security/users
```

#### Solution 5: Test Endpoint Directly
Use curl to test the endpoint:

```bash
# Get admin token first
TOKEN="your_jwt_token_here"

# Test create user endpoint
curl -X POST http://localhost:8001/api/auth/security/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "Test123!",
    "roles": ["interim"],
    "group_ids": [],
    "send_invitation": false
  }'
```

---

### Error: 401 Unauthorized on Protected Routes

**Symptom**: API calls fail with 401 status

**Solutions**:
1. Check if JWT token is present in localStorage
2. Verify token hasn't expired
3. Log out and log back in
4. Check if backend authentication middleware is working

**Check token expiration**:
```javascript
// In browser console
const token = localStorage.getItem('token')
if (token) {
  const payload = JSON.parse(atob(token.split('.')[1]))
  const expiry = new Date(payload.exp * 1000)
  console.log('Token expires:', expiry)
  console.log('Is expired:', expiry < new Date())
}
```

---

### Error: 404 Not Found

**Symptom**: API endpoint returns 404

**Common Causes**:
1. Route not registered in FastAPI
2. Incorrect base URL configuration
3. Typo in endpoint path

**Solutions**:
1. Check `main.py` to ensure the router is included:
```python
app.include_router(security_router)
```

2. Verify base URL in frontend:
```typescript
// Should be '/auth-api'
baseQuery: fetchBaseQuery({ baseUrl: '/auth-api/auth/security' })
```

3. Check Vite proxy configuration in `vite.config.ts`:
```typescript
proxy: {
  '/auth-api': {
    target: 'http://localhost:8001',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/auth-api/, '/api')
  }
}
```

---

### Error: CORS Issues

**Symptom**: Console shows CORS error

**Solution**: Check backend CORS configuration in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Error: Connection Refused

**Symptom**: `ERR_CONNECTION_REFUSED`

**Solutions**:
1. Check if backend service is running:
```bash
sudo supervisorctl status backend
```

2. Restart backend if needed:
```bash
sudo supervisorctl restart backend
```

3. Check if port 8001 is accessible:
```bash
curl http://localhost:8001/api/health
```

---

## Debugging Tips

### Enable Detailed API Logging

**Frontend** (RTK Query):
```typescript
// In store.ts, add logger middleware
import { createLogger } from 'redux-logger'

const logger = createLogger({
  collapsed: true,
  duration: true,
})

// Add to middleware
middleware: (getDefaultMiddleware) =>
  getDefaultMiddleware()
    .concat(logger)  // Add this
    .concat(authApi.middleware)
    // ... other middleware
```

**Backend** (FastAPI):
```python
# In main.py, add logging middleware
import logging

logging.basicConfig(level=logging.DEBUG)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

### Check Network Tab in DevTools

1. Open DevTools (F12)
2. Go to Network tab
3. Reproduce the error
4. Look for failed request
5. Check:
   - Request URL
   - Request Method
   - Request Headers (Authorization token)
   - Request Payload
   - Response Status
   - Response Body

### Check Backend Logs

```bash
# All backend logs
tail -f /var/log/supervisor/backend.*.log

# Error logs only
tail -f /var/log/supervisor/backend.err.log

# Output logs only
tail -f /var/log/supervisor/backend.out.log
```

---

## Quick Fixes Checklist

When you encounter an API error:

- [ ] Check if you're logged in
- [ ] Verify token hasn't expired
- [ ] Clear browser cache
- [ ] Check Network tab in DevTools
- [ ] Check backend logs
- [ ] Restart backend service if needed
- [ ] Test endpoint with curl
- [ ] Check if endpoint exists in backend
- [ ] Verify HTTP method matches

---

## Getting Help

If the issue persists:

1. **Gather Information**:
   - Screenshot of browser console error
   - Screenshot of Network tab showing failed request
   - Backend logs from time of error
   - Steps to reproduce

2. **Check Documentation**:
   - `/app/docs/` directory for specific feature docs
   - API endpoint documentation in backend code

3. **Contact Support**:
   - Email: support@jlcgroup.com
   - Include all gathered information above
