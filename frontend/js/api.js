/**
 * EcoRetiro OS — API Client
 * Comunicación con el backend FastAPI
 */
(function () {
  'use strict';

  var BASE_URL = window.ECORETIRO_API_URL || 'http://127.0.0.1:8000';
  var TOKEN_KEY = 'ecoretiro-token';

  /* -------- Token helpers -------- */

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
  }

  function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
  }

  function redirectToLogin() {
    clearToken();
    var inPages = window.location.pathname.indexOf('/pages/') !== -1;
    window.location.href = inPages ? 'login.html' : 'pages/login.html';
  }

  /* -------- Fetch wrapper -------- */

  function authFetch(endpoint, options) {
    options = options || {};
    options.headers = options.headers || {};

    var token = getToken();
    if (token) {
      options.headers['Authorization'] = 'Bearer ' + token;
    }

    if (options.body && !options.headers['Content-Type']) {
      options.headers['Content-Type'] = 'application/json';
    }

    return fetch(BASE_URL + endpoint, options).then(function (res) {
      if (res.status === 401) {
        redirectToLogin();
        return Promise.reject(new Error('No autorizado'));
      }

      if (!res.ok) {
        return res.json().then(function (data) {
          var msg = parseError(data);
          return Promise.reject(new Error(msg));
        });
      }

      if (res.status === 204) return null;
      return res.json();
    });
  }

  function parseError(data) {
    if (!data || !data.detail) return 'Error desconocido';
    if (typeof data.detail === 'string') return data.detail;
    // Validation errors: array of { loc, msg, type }
    if (Array.isArray(data.detail)) {
      return data.detail.map(function (e) { return e.msg; }).join('. ');
    }
    return 'Error desconocido';
  }

  /* -------- Auth -------- */

  function login(email, password) {
    return authFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: email, password: password })
    }).then(function (data) {
      setToken(data.access_token);
      return data;
    });
  }

  function register(name, email, password, phone) {
    var body = { name: name, email: email, password: password };
    if (phone) body.phone = phone;

    return authFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify(body)
    }).then(function (user) {
      // Auto-login tras registro exitoso
      return login(email, password);
    });
  }

  /* -------- User -------- */

  function getCurrentUser() {
    return authFetch('/users/me');
  }

  function updateProfile(data) {
    return authFetch('/users/me', {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }

  /* -------- Requests -------- */

  function getMyRequests() {
    return authFetch('/requests/me');
  }

  function createRequest(data) {
    return authFetch('/requests', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  function getAllRequests() {
    return authFetch('/requests');
  }

  function updateRequestStatus(requestId, data) {
    return authFetch('/requests/' + requestId + '/status', {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }

  /* -------- Tracking (público) -------- */

  function getTrackingInfo(trackingNumber) {
    return fetch(BASE_URL + '/track/' + encodeURIComponent(trackingNumber))
      .then(function (res) {
        if (!res.ok) {
          return res.json().then(function (data) {
            var msg = parseError(data);
            return Promise.reject(new Error(msg));
          });
        }
        return res.json();
      });
  }

  /* -------- Admin -------- */

  function getDashboardStats() {
    return authFetch('/admin/stats');
  }

  /* -------- Notifications -------- */

  function getMyNotifications() {
    return authFetch('/notifications/me');
  }

  function markNotificationRead(id) {
    return authFetch('/notifications/' + id, {
      method: 'PATCH',
      body: JSON.stringify({ is_read: true })
    });
  }

  /* -------- Public API -------- */

  window.EcoRetiroAPI = {
    getToken: getToken,
    setToken: setToken,
    clearToken: clearToken,
    redirectToLogin: redirectToLogin,
    authFetch: authFetch,
    login: login,
    register: register,
    getCurrentUser: getCurrentUser,
    updateProfile: updateProfile,
    getMyRequests: getMyRequests,
    createRequest: createRequest,
    getAllRequests: getAllRequests,
    updateRequestStatus: updateRequestStatus,
    getTrackingInfo: getTrackingInfo,
    getDashboardStats: getDashboardStats,
    getMyNotifications: getMyNotifications,
    markNotificationRead: markNotificationRead
  };
})();
