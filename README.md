# 🌸 KRISHU X AUTH — RED CHERRY BLOSSOM EDITION

All-In-One Enterprise KeyAuth Authentication & Licensing Platform.
Supports **100% Official KeyAuth v1.2 Protocol** (drop-in compatibility for C++, C#, ImGui, Python, Android Dark X Auth clients) as well as modern REST JSON APIs.

---

## 🌺 What Makes This The Best All-In-One KeyAuth Platform?

1. **🌸 Red Cherry Blossom Modern Glassmorphism UI:**
   - Obsidian crimson dark mode with vibrant sakura red & petal rose accents.
   - Dynamic 3D Falling Cherry Blossom Petals physics simulation on canvas with interactive mouse wind gusts and petal ripples.
   - Animated conic glow borders, glowing pill badges, smooth frosted blurs, and responsive mobile sidebar.

2. **⚡ KeyAuth v1.0 / v1.1 / v1.2 Protocol Engine:**
   - Native support for `/api/1.2/`, `/api/1.0/`, and `/api/` endpoints.
   - Any official KeyAuth client (C++, C#, ImGui, Dark X Auth Android APK) works **without modifying client code** — just change the API URL to your server!
   - Supports `type`: `init`, `login`, `register`, `license`, `check`, `fetchStats`, `fetchOnline`, `var`, `getvar`, `setvar`, `log`, `logout`.

3. **🔒 SHA-256 Hardware Fingerprint Locking:**
   - Prevents license sharing. Single-click HWID reset from user dashboard or admin console.

4. **🔑 Bulk License Engine & Reseller Portal:**
   - Generate up to 500 keys in seconds with custom prefixes, durations (1 day, 7 days, 30 days, lifetime), and subscription tiers.
   - Per-app reseller master keys allowing resellers to log in and create keys without admin panel access.

5. **☁️ Dual Database Sync:**
   - Automatic MongoDB Atlas cloud connection with local JSON fallback. Data is safe across cloud server sleeps.

6. **🛠️ Interactive Live Key Tester & SDK Viewer:**
   - Test licenses live right on the landing page.
   - Multi-language SDKs for C++, C#, Python, Android Java/Kotlin, and cURL.

---

## 💻 Local Quick Start

1. Double-click `start.bat` or run:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
2. Open in your browser: `http://127.0.0.1:5000`
3. **Public Registration:** `http://127.0.0.1:5000/register` (Instant free developer account with starter application)
4. **Developer & Admin Console:** `http://127.0.0.1:5000/admin`
   - Sign in with your registered account or master credentials.
5. **User Portal:** `http://127.0.0.1:5000/login`
   - License subscribers and developers can both sign in from the portal.

---

## 🔌 API Endpoints Reference

### Official KeyAuth v1.2 Format:
```http
POST /api/1.2/
Content-Type: application/x-www-form-urlencoded

type=license&key=KRISHU-XXXX-XXXX&hwid=MACHINE-HWID-001&name=KRISHU+X+CHEATS
```

### Modern REST JSON Format:
```http
POST /api/v1/license
Content-Type: application/json

{
  "appId": "app_krishu_main",
  "key": "KRISHU-XXXX-XXXX",
  "hwid": "MACHINE-HWID-001"
}
```
