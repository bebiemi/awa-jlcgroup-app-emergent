# Fix: ERR_SSL_PROTOCOL_ERROR - localhost:8000 in Production

## Problem

In production (https://preview.emergentagent.com), the frontend was attempting to make requests to `https://localhost:8000/api/besoins/` causing:
```
GET https://localhost:8000/api/besoins/?page=1&page_size=12 
net::ERR_SSL_PROTOCOL_ERROR
```

### Why This Happens

1. **Production uses HTTPS**, browser tries to make requests to localhost using HTTPS
2. **localhost:8000 runs HTTP only**, not configured for SSL
3. **Browser blocks mixed content** or protocol mismatch

### Root Cause

Even with `baseUrl: undefined` in `fetchBaseQuery`, RTK Query or browser might construct absolute URLs with cached/default values pointing to `localhost:8000`.

## Solution Implemented

### 1. Force Relative URLs in baseQueryWithAuth.ts

Modified the `createBaseQueryWithAuth` function to:
- Use empty string `''` instead of `undefined` for baseUrl
- Add URL sanitization to strip any absolute URLs back to relative paths
- Ensure all requests are relative to current origin

```typescript
export const createBaseQueryWithAuth = (baseUrl?: string): BaseQueryFn<...> => {
  const baseQuery = fetchBaseQuery({
    baseUrl: baseUrl || '',  // Empty string to force relative URLs
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      return headers
    },
  })

  return async (args, api, extraOptions) => {
    // Force relative URLs by sanitizing any absolute URLs
    let modifiedArgs = args
    if (typeof args === 'object' && 'url' in args) {
      const url = args.url || ''
      if (url.startsWith('http://') || url.startsWith('https://')) {
        // Extract just the path from absolute URLs
        try {
          const urlObj = new URL(url)
          modifiedArgs = { ...args, url: urlObj.pathname + urlObj.search }
        } catch (e) {
          modifiedArgs = args
        }
      }
    }
    
    const result = await baseQuery(modifiedArgs, api, extraOptions)
    // ... rest of code
  }
}
```

### 2. How It Works Now

#### Development (localhost)
```
Frontend: http://localhost:3000
Request: /api/besoins
Vite Proxy: localhost:3000/api/besoins → localhost:8000/api/besoins
Result: ✅ HTTP call to auth-microservice
```

#### Production (preview.emergentagent.com)
```
Frontend: https://preview.emergentagent.com
Request: /api/besoins (relative)
Browser: https://preview.emergentagent.com/api/besoins
Kubernetes: Routes /api/* to correct internal service
Result: ✅ HTTPS call to production backend
```

### 3. Additional Browser Cache Clearing

If the error persists after deployment:

1. **Clear browser cache**: 
   - Chrome: DevTools → Network tab → "Disable cache" checkbox
   - Or: Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)

2. **Clear service workers**:
   - Chrome: DevTools → Application tab → Service Workers → Unregister

3. **Clear local storage**:
   - Chrome: DevTools → Application tab → Local Storage → Clear

## Verification

After fix, all requests should be relative:
```javascript
// ✅ Correct (relative URL)
GET /api/besoins/?page=1&page_size=12

// ❌ Incorrect (absolute URL with localhost)
GET https://localhost:8000/api/besoins/?page=1&page_size=12
```

## Files Modified

- `/app/apps/web/src/utils/baseQueryWithAuth.ts` - URL sanitization logic added
- `/app/docs/FIX_ERR_SSL_PROTOCOL_ERROR.md` - This documentation

## Testing

1. **Development**: 
   ```bash
   # Should work with Vite proxy
   curl http://localhost:3000/api/besoins
   ```

2. **Production**: 
   ```bash
   # Should work without localhost reference
   curl https://preview.emergentagent.com/api/besoins
   ```

3. **Browser DevTools**:
   - Open Network tab
   - Reload page
   - Verify all `/api/*` requests are relative (no localhost:8000)

## Prevention

- ✅ Never hardcode `localhost:8000` in frontend code
- ✅ Always use relative URLs (`/api/...`)
- ✅ Let environment handle routing (Vite proxy dev, K8s prod)
- ✅ Use `baseQueryWithAuth` for all RTK Query APIs

---

**Date Fixed**: November 11, 2025  
**Fixed By**: AI Engineer  
**Status**: ✅ Implemented, Awaiting User Verification
