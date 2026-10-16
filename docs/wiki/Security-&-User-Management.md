# 🔐 Security & User Management

Avani Albedo enforces strict, role-based access control (RBAC) and Google Cloud Native identity verification.

---

## 🛡️ Authentication Architecture

1. **Firebase Google 1-Click Login**:
   - Integrates with Google OAuth 2.0 via Firebase Client SDK.
   - Upon successful sign-in, the Google ID token is submitted to `/api/auth/firebase-login`.
2. **Access Control & Approval Flow**:
   - **Pre-Approved Super Admin**: `srbodkhe@gmail.com` (Unrestricted access).
   - **Judges / Evaluators**: Credentials account with 1-click evaluation access.
   - **Unregistered Google Accounts**: Automatically quarantined with HTTP `403 Forbidden` and generates an instant access request alert in the Admin Control Center.
   - **Admin Approval**: Super Admin can approve, reject, suspend, or promote users to *Municipal Planner*, *Climate Scientist*, or *Urban Resilience Director*.
3. **Session Cookies & Bearer Tokens**:
   - Signs sessions with HS256 JWT tokens.
   - Sets secure session cookie `avani_token` so browser reloads and Swagger documentation (`/docs`) work seamlessly.

---

## 💾 Live Database Persistence (Google Cloud Firestore)

- User profiles and access roles are stored in Firestore collection **`avani_users`**.
- Registration requests and notifications are stored in Firestore collection **`avani_alerts`**.
- When Cloud Run containers restart, cold-start, or deploy a new revision, all users remain permanently preserved.
- Local fallback caching in `data/registered_users.json` ensures offline resilience during development.
