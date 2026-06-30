# Zentra backend

This lightweight backend exposes a JSON endpoint for Google/Firebase auth verification.

## Run locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the server:
   ```bash
   node server.js
   ```
3. The endpoint will be available at:
   ```text
   http://127.0.0.1:5000/api/verify-user/
   ```

## Configure Firebase Admin SDK

Set either of the following before starting the server:

- `FIREBASE_SERVICE_ACCOUNT` with the full service-account JSON as a single-line JSON string
- `GOOGLE_APPLICATION_CREDENTIALS` pointing to a service-account JSON file

## Expected responses

- `200` with `{ success: true, ... }` when the Firebase ID token is verified
- `400` with `{ success: false, error: "Missing token" }` when no token is provided
- `401/500` with structured JSON errors for invalid or expired tokens
