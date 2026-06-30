const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const admin = require('firebase-admin');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors({ origin: true, credentials: true }));
app.use(express.json({ limit: '2mb' }));

let firebaseApp = null;
let firebaseInitError = null;

function readServiceAccount() {
  const serviceAccountJson = process.env.FIREBASE_SERVICE_ACCOUNT;
  if (serviceAccountJson) {
    return JSON.parse(serviceAccountJson);
  }

  const candidatePaths = [
    process.env.FIREBASE_SERVICE_ACCOUNT_PATH,
    process.env.GOOGLE_APPLICATION_CREDENTIALS,
    path.resolve(__dirname, 'firebase-service-account.json'),
    path.resolve(process.cwd(), 'firebase-service-account.json'),
    path.resolve(__dirname, '..', 'firebase-service-account.json'),
    path.resolve(process.cwd(), '..', 'firebase-service-account.json'),
    path.resolve(process.env.HOME || '', 'Downloads', 'firebase-service-account.json'),
    path.resolve(process.env.HOME || '', 'firebase-service-account.json')
  ].filter(Boolean);

  for (const candidatePath of candidatePaths) {
    if (!candidatePath) continue;

    const absolutePath = path.isAbsolute(candidatePath)
      ? candidatePath
      : path.resolve(process.cwd(), candidatePath);

    if (fs.existsSync(absolutePath)) {
      return JSON.parse(fs.readFileSync(absolutePath, 'utf8'));
    }
  }

  throw new Error('No Firebase service account was found. Set FIREBASE_SERVICE_ACCOUNT or FIREBASE_SERVICE_ACCOUNT_PATH.');
}

function initializeFirebase() {
  if (firebaseApp || admin.apps.length) {
    firebaseApp = firebaseApp || admin.apps[0];
    return firebaseApp;
  }

  if (firebaseInitError) {
    return null;
  }

  try {
    const serviceAccount = readServiceAccount();
    firebaseApp = admin.initializeApp({
      credential: admin.credential.cert(serviceAccount)
    });
    console.log('Firebase Admin SDK initialized successfully.');
    return firebaseApp;
  } catch (error) {
    firebaseInitError = error;
    console.error('Firebase initialization failed:', error.message);
    return null;
  }
}

function sendJson(res, statusCode, payload) {
  return res.status(statusCode).json(payload);
}

app.get('/health', (_req, res) => {
  sendJson(res, 200, { ok: true, message: 'Backend is healthy' });
});

app.post(['/api/verify-user/', '/api/auth/google', '/api/auth/google/'], async (req, res) => {
  try {
    const body = req.body || {};
    const token = body.token || body.idToken || body.id_token || body.credential || null;

    if (!token) {
      return sendJson(res, 400, {
        success: false,
        error: 'Missing token',
        message: 'A Firebase ID token is required.'
      });
    }

    const firebase = initializeFirebase();

    if (!firebase) {
      const message = firebaseInitError?.message || 'Firebase Admin SDK is not configured on this server.';
      return sendJson(res, 503, {
        success: false,
        error: 'Firebase not configured',
        message
      });
    }

    const decodedToken = await admin.auth().verifyIdToken(token);

    return sendJson(res, 200, {
      success: true,
      message: 'Google authentication verified successfully.',
      user: {
        uid: decodedToken.uid,
        email: decodedToken.email || null,
        name: decodedToken.name || null,
        picture: decodedToken.picture || null,
        role: body.role || body.accountType || 'student'
      }
    });
  } catch (error) {
    console.error('Google auth verification failed:', error);
    const statusCode = error.code === 'auth/argument-error' || error.code === 'auth/id-token-expired' ? 401 : 500;
    return sendJson(res, statusCode, {
      success: false,
      error: error.code || 'auth_error',
      message: error.message || 'Unable to verify Google authentication.'
    });
  }
});

app.use((err, _req, res, _next) => {
  console.error('Unhandled error:', err);
  sendJson(res, 500, {
    success: false,
    error: 'internal_error',
    message: 'An unexpected server error occurred.'
  });
});

app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});
