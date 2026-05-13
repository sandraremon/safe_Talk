# SafeTalk - Multi-Device Setup Guide

## Prerequisites
- SafeTalk running on **Device 1 (Your Mac)** at `192.168.1.51`
- Another device **(Device 2)** on the same WiFi network (phone, laptop, tablet, etc.)
- Both devices on the same network

---

## Step-by-Step Setup

### **STEP 1: Create Environment Configuration Files**

Navigate to the frontend folder and create two environment files:

#### File 1: `frontend/.env` (Local Development Fallback)
```bash
cd /Users/sandraremon/Desktop/safeTalk/frontend
touch .env
```

Edit the file and add:
```
VITE_API_URL=http://localhost:8000
```

#### File 2: `frontend/.env.local` (Network Configuration)
```bash
touch .env.local
```

Edit the file and add:
```
VITE_API_URL=http://192.168.1.51:8000
```

---

### **STEP 2: Update Frontend Code**

#### Update `frontend/app/webpages/Login.tsx`
Replace the hardcoded `http://localhost:8000` with the environment variable.

Add at the top of the file:
```typescript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

Then replace these lines:
```typescript
// OLD - Line ~27
const response = await fetch("http://localhost:8000/auth/login", {

// NEW
const response = await fetch(`${API_URL}/auth/login`, {
```

And replace:
```typescript
// OLD - Line ~70
const response = await fetch("http://localhost:8000/auth/register", {

// NEW
const response = await fetch(`${API_URL}/auth/register`, {
```

#### Update `frontend/components/application/app-navigation/sidebar-navigation/sidebar-section-dividers.tsx`
Add at the top of the file:
```typescript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

Replace all occurrences:
- `"http://localhost:8000/key/conversations"` → `${API_URL}/key/conversations`
- `"http://localhost:8000/key/mydetails"` → `${API_URL}/key/mydetails`
- `ws://localhost:8000/ws` → `${API_URL.replace('http', 'ws')}/ws`
- `"http://localhost:8000/key/messages/` → `${API_URL}/key/messages/`
- `"http://localhost:8000/key/users/search` → `${API_URL}/key/users/search`

---

### **STEP 3: Start the Backend (Device 1)**

Open a terminal and run:
```bash
cd /Users/sandraremon/Desktop/safeTalk
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Important:** Use `--host 0.0.0.0` to allow network access (not just localhost)

Expected output:
```
Uvicorn running on http://0.0.0.0:8000
```

---

### **STEP 4: Start the Frontend (Device 1)**

Open a **new terminal** and run:
```bash
cd /Users/sandraremon/Desktop/safeTalk/frontend
npm run dev
```

Expected output:
```
  VITE v... ready in ... ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.51:5173/
```

---

### **STEP 5: Test on Device 1 (Same Device)**

Open browser on your Mac:
- **Local:** http://localhost:5173
- **Network:** http://192.168.1.51:5173

Both should work. Open DevTools (F12) and check Console. You should see:
```
API URL: http://192.168.1.51:8000
```

---

### **STEP 6: Access from Device 2 (Different Device)**

On the second device (phone, tablet, another laptop):
1. Make sure it's on the **same WiFi network**
2. Open the browser
3. Go to: **http://192.168.1.51:5173**

That's it! The frontend will automatically connect to your backend at `192.168.1.51:8000`.

---

## Troubleshooting

### Issue: "Connection Refused" on Device 2
**Solution:** Backend not listening on network
```bash
# Kill the current backend
# Restart with:
# python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Issue: Frontend shows "API URL: http://localhost:8000" on Device 2
**Solution:** Frontend didn't load `.env.local`. Restart the dev server:
```bash
cd frontend
npm run dev
```

### Issue: Can't reach 192.168.1.51 from Device 2
**Solution:** Check if devices are on the same network
```bash
# On Device 1, run:
ifconfig | grep "inet " | grep -v 127.0.0.1

# Look for something like: inet 192.168.1.51
```

### Issue: WebSocket connection fails
**Solution:** Check browser Console (F12). Should show:
```
Connected to SafeTalk WebSocket
```
If it fails, verify:
1. Backend is running with `--host 0.0.0.0`
2. Frontend URL is correct in browser
3. Port 8000 is not blocked by firewall

---

## Environment Variable Behavior

- **`.env.local`** (Device 2 / Network setup)
  - Highest priority
  - Loaded automatically by Vite in dev mode
  - Contains: `VITE_API_URL=http://192.168.1.51:8000`

- **`.env`** (Device 1 / Local setup)
  - Fallback
  - Contains: `VITE_API_URL=http://localhost:8000`

- **Code fallback**
  - If no env files: `http://localhost:8000`

To switch between setups:
1. Edit the appropriate `.env` or `.env.local` file
2. Restart the dev server: `npm run dev`

---

## Quick Reference

| Setup | Device | Backend Command | Frontend URL | API URL |
|-------|--------|-----------------|--------------|---------|
| **Local** | Same Mac | `--host 127.0.0.1` | localhost:5173 | localhost:8000 |
| **Network** | Device 2 | `--host 0.0.0.0` | 192.168.1.51:5173 | 192.168.1.51:8000 |

---

## Files to Create/Update Summary

✅ **Create:**
- `frontend/.env` → `VITE_API_URL=http://localhost:8000`
- `frontend/.env.local` → `VITE_API_URL=http://192.168.1.51:8000`

✅ **Update:**
- `frontend/app/webpages/Login.tsx` → Replace hardcoded URLs
- `frontend/components/application/app-navigation/sidebar-navigation/sidebar-section-dividers.tsx` → Replace hardcoded URLs

✅ **Backend already configured:**
- `main.py` → CORS allows all origins
- Already set up for multi-device with `--host 0.0.0.0`
