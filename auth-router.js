(function () {
  const AUTH_STORAGE_KEY = "zentra_google_auth";
  const LOGIN_PAGE_PATH = "../zentra_login/code.html";
  const STUDENT_DASHBOARD_PATH = "../New Student Dashboard /Home page.html";
  const EDUCATOR_DASHBOARD_PATH = "../Teacher Dashboard 1/code.html";

  function normalizeRole(role) {
    const value = (role || "student").toLowerCase();
    if (["educator", "teacher", "instructor", "mentor"].includes(value)) {
      return "educator";
    }
    return "student";
  }

  function getRouteName(role) {
    return normalizeRole(role) === "educator" ? "teacher-dashboard" : "student-dashboard";
  }

  function getDashboardPath(role) {
    return normalizeRole(role) === "educator" ? EDUCATOR_DASHBOARD_PATH : STUDENT_DASHBOARD_PATH;
  }

  function isCurrentPage(path) {
    try {
      const targetUrl = new URL(path, window.location.href);
      return targetUrl.href === window.location.href;
    } catch (error) {
      return false;
    }
  }

  function saveAuthSession(user, role, idToken, provider) {
    const authState = {
      idToken,
      uid: user?.uid || "",
      email: user?.email || "",
      displayName: user?.displayName || "",
      role: normalizeRole(role),
      route: getRouteName(role),
      provider,
      timestamp: Date.now()
    };
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authState));
    return authState;
  }

  function getStoredAuth() {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!stored) return null;

    try {
      return JSON.parse(stored);
    } catch (error) {
      localStorage.removeItem(AUTH_STORAGE_KEY);
      return null;
    }
  }

  function redirectForRole(role) {
    const dashboardPath = getDashboardPath(role);
    if (isCurrentPage(dashboardPath)) return;
    window.location.assign(dashboardPath);
  }

  function protectDashboard(expectedRole) {
    const authState = getStoredAuth();
    if (!authState) {
      if (!isCurrentPage(LOGIN_PAGE_PATH)) {
        window.location.replace(LOGIN_PAGE_PATH);
      }
      return null;
    }

    const role = normalizeRole(authState.role);
    if (role !== normalizeRole(expectedRole)) {
      redirectForRole(role);
      return null;
    }

    return authState;
  }

  function clearAuthSession() {
    localStorage.removeItem(AUTH_STORAGE_KEY);
    if (window.localStorage) {
      window.localStorage.removeItem(AUTH_STORAGE_KEY);
    }
    if (window.sessionStorage) {
      window.sessionStorage.removeItem(AUTH_STORAGE_KEY);
    }
    return true;
  }

  function logout() {
    clearAuthSession();
    if (window.ZentraAuth && typeof window.ZentraAuth.resetUserState === 'function') {
      window.ZentraAuth.resetUserState();
    }
    if (!isCurrentPage(LOGIN_PAGE_PATH)) {
      window.location.href = LOGIN_PAGE_PATH;
    }
  }

  function resetUserState() {
    if (typeof window.dispatchEvent === 'function') {
      window.dispatchEvent(new CustomEvent('zentra-auth-reset'));
    }
  }

  window.ZentraAuth = {
    AUTH_STORAGE_KEY,
    normalizeRole,
    getRouteName,
    getDashboardPath,
    saveAuthSession,
    getStoredAuth,
    redirectForRole,
    protectDashboard,
    clearAuthSession,
    resetUserState,
    logout
  };
})();
