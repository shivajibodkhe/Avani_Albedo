// Global fetch interceptor to securely attach bearer token & credentials
const _originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
  const token = localStorage.getItem('avani_token');
  const opts = Object.assign({}, options);
  opts.credentials = opts.credentials || 'same-origin';
  if (token && typeof url === 'string' && url.startsWith('/api/') && !url.includes('/api/auth/login') && !url.includes('/api/auth/firebase-login')) {
    opts.headers = Object.assign({}, opts.headers);
    if (!opts.headers['Authorization']) {
      opts.headers['Authorization'] = `Bearer ${token}`;
    }
  }
  return _originalFetch.call(this, url, opts);
};

// Initialize Firebase for 1-Click Google Sign-In
try {
  if (window.firebase && !firebase.apps.length) {
    firebase.initializeApp({
      projectId: "avani-albedo",
      appId: "1:615055398519:web:f6c09d29e5bb2982d6d872",
      storageBucket: "avani-albedo.firebasestorage.app",
      apiKey: "AIzaSyDrRVQqwPRA8vGdpHgzZlDNgwqN4XzxeNc",
      authDomain: "avani-albedo.firebaseapp.com",
      messagingSenderId: "615055398519"
    });
  }
} catch (e) {
  console.warn("Firebase initialization notice:", e);
}

// Avani Albedo Interactive GIS Client
let map;
let climateCells = [];
let currentScenarioResult = null;
let currentActionPlan = null;

// Layer Groups
let heatPolygonGroup;
let assetsMarkerGroup;
let interventionMarkerGroup;

let selectedScenario = "optimized";
let currentBudgetInr = 10000000.0; // 1 Crore default

// Geographic State (Cascading Country -> City -> Ward)
let geographicHierarchy = null;
let currentSelectedCity = "Bengaluru";
let currentSelectedCountry = "India";
let selectedPersona = "Municipal Commissioner";
let selectedWardId = null;

// Chart Instances
let diurnalChartInstance = null;
let wardMicroChartInstance = null;
let currentTempSensorMode = "lst"; // 'lst' (satellite surface skin) or 'air' (ambient weather station)
let currentTimelineData = null;

// Multi-Currency & Global Economics State
let currentCurrency = "INR";
let currentCurrencySymbol = "₹";
let currentUsdRate = 0.012; // 1 INR = $0.012 USD
let activeCurrencyDisplayMode = "dual"; // 'dual', 'usd', or 'local'

function formatCurrency(amountInLocal) {
  if (amountInLocal === undefined || amountInLocal === null || isNaN(amountInLocal)) amountInLocal = 0;
  const usdAmount = amountInLocal * currentUsdRate;

  // Local currency formatted string
  let localStr = "";
  if (currentCurrency === "INR") {
    const lakhs = amountInLocal / 100000.0;
    if (lakhs >= 100) {
      localStr = `₹${(lakhs / 100).toFixed(2)} Cr`;
    } else {
      localStr = `₹${lakhs.toFixed(1)}L`;
    }
  } else if (currentCurrency === "USD") {
    if (amountInLocal >= 1000000) {
      localStr = `$${(amountInLocal / 1000000).toFixed(2)}M`;
    } else if (amountInLocal >= 1000) {
      localStr = `$${(amountInLocal / 1000).toFixed(0)}k`;
    } else {
      localStr = `$${amountInLocal.toFixed(0)}`;
    }
    return `${localStr} USD`;
  } else {
    // AED, GBP, SGD, etc.
    if (amountInLocal >= 1000000) {
      localStr = `${currentCurrencySymbol}${(amountInLocal / 1000000).toFixed(2)}M`;
    } else if (amountInLocal >= 1000) {
      localStr = `${currentCurrencySymbol}${(amountInLocal / 1000).toFixed(0)}k`;
    } else {
      localStr = `${currentCurrencySymbol}${amountInLocal.toFixed(0)}`;
    }
  }

  // USD formatted string
  let usdStr = "";
  if (usdAmount >= 1000000) {
    usdStr = `$${(usdAmount / 1000000).toFixed(2)}M USD`;
  } else if (usdAmount >= 1000) {
    usdStr = `$${(usdAmount / 1000).toFixed(1)}k USD`;
  } else {
    usdStr = `$${usdAmount.toFixed(0)} USD`;
  }

  if (activeCurrencyDisplayMode === 'usd') {
    return usdStr;
  } else if (activeCurrencyDisplayMode === 'local') {
    return localStr;
  } else {
    // Dual mode (Default)
    if (currentCurrency === "USD") return usdStr;
    return `${localStr} (${usdStr})`;
  }
}

function updateBudgetDisplay() {
  const display = document.getElementById('budget-value-display');
  const secDisplay = document.getElementById('budget-secondary-display');
  if (display) {
    display.textContent = formatCurrency(currentBudgetInr);
  }
  if (secDisplay) {
    if (activeCurrencyDisplayMode === 'dual' && currentCurrency === "INR") {
      const cr = (currentBudgetInr / 10000000.0).toFixed(2);
      secDisplay.textContent = `₹${cr} Cr`;
    } else {
      secDisplay.textContent = "";
    }
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  initEventHandlers();
  loadSystemStatus();
  initCopilot();
  await initAuth();
});


// ================= MAP INITIALIZATION =================
function initMap() {
  map = L.map('gis-map', {
    zoomControl: true,
    attributionControl: false
  }).setView([12.9716, 77.5946], 11);

  // 1. Sleek Dark Canvas (OpenStreetMap with dark CSS filter - 100% Free, No Watermark, No Key)
  const darkLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    className: 'dark-osm-tiles',
    attribution: '&copy; OpenStreetMap'
  });

  // 2. High-Resolution Satellite View (Esri World Imagery - 100% Free, No Watermark, No Key)
  const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19,
    attribution: 'Tiles &copy; Esri'
  });

  // 3. Clean Street Map
  const streetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap'
  });

  // Add default dark layer
  darkLayer.addTo(map);

  // Basemap Switcher Control (Top Right)
  const baseLayers = {
    "🌙 Dark Canvas": darkLayer,
    "🛰️ Satellite Imagery": satelliteLayer,
    "🗺️ Clean Streets": streetLayer
  };
  L.control.layers(baseLayers, null, { position: 'topright' }).addTo(map);

  heatPolygonGroup = L.layerGroup().addTo(map);
  assetsMarkerGroup = L.layerGroup().addTo(map);
  interventionMarkerGroup = L.layerGroup().addTo(map);
}

// ================= EVENT HANDLERS =================
function initEventHandlers() {
  // Scenario button toggles
  document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.scenario-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectAndLoadScenario(btn.dataset.type);
    });
  });

  // Budget slider
  const slider = document.getElementById('budget-slider');
  if (slider) {
    slider.addEventListener('input', (e) => {
      const lakhs = parseFloat(e.target.value);
      currentBudgetInr = lakhs * 100000.0;
      updateBudgetDisplay();
    });
    slider.addEventListener('change', () => {
      const activeTab = document.querySelector('.tab-btn.active');
      if (activeTab && activeTab.dataset.tab === 'tab-comparison') {
        runComparison();
      }
    });
  }

  // Multi-Currency Display Mode Toggle
  document.querySelectorAll('.currency-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.currency-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCurrencyDisplayMode = btn.dataset.cur;
      updateBudgetDisplay();
      if (currentScenarioResult) {
        updateKpiCards(currentScenarioResult);
        renderAllocationsTable(currentScenarioResult);
      }
      if (currentActionPlan) {
        renderActionPlan(currentActionPlan);
      }
    });
  });

  // Layer toggles
  document.getElementById('layer-heat').addEventListener('change', (e) => {
    if (e.target.checked) map.addLayer(heatPolygonGroup);
    else map.removeLayer(heatPolygonGroup);
  });
  document.getElementById('layer-infra').addEventListener('change', (e) => {
    if (e.target.checked) map.addLayer(assetsMarkerGroup);
    else map.removeLayer(assetsMarkerGroup);
  });
  document.getElementById('layer-interventions').addEventListener('change', (e) => {
    if (e.target.checked) map.addLayer(interventionMarkerGroup);
    else map.removeLayer(interventionMarkerGroup);
  });

  // Run Agent Button
  document.getElementById('run-agent-btn').addEventListener('click', runAvaniAgent);

  // Compare Scenarios Button
  document.getElementById('compare-btn').addEventListener('click', () => {
    switchResultsTab('tab-comparison');
  });

  // Results Tab Switching
  document.querySelectorAll('.tab-btn').forEach(tab => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      switchResultsTab(tab.dataset.tab);
    });
  });

  // Temperature Sensor Mode Toggle (LST vs Shaded Air Temp)
  const btnLst = document.getElementById('temp-mode-btn-lst');
  const btnAir = document.getElementById('temp-mode-btn-air');
  if (btnLst && btnAir) {
    btnLst.addEventListener('click', () => setTemperatureSensorMode("lst"));
    btnAir.addEventListener('click', () => setTemperatureSensorMode("air"));
  }

  // Close inspector button
  document.getElementById('close-inspector').addEventListener('click', () => {
    document.getElementById('cell-inspector').classList.add('hidden');
  });

  // Export JSON
  document.getElementById('export-json-btn').addEventListener('click', exportPlanJson);

  // Auth Form & Handlers
  const loginForm = document.getElementById('login-form');
  if (loginForm) loginForm.addEventListener('submit', handleLoginSubmit);

  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);

  // Firebase Google Login
  const firebaseGoogleBtn = document.getElementById('firebase-google-btn');
  if (firebaseGoogleBtn) firebaseGoogleBtn.addEventListener('click', handleFirebaseGoogleLogin);

  const closeGoogleBtn = document.getElementById('close-google-auth-btn');
  if (closeGoogleBtn) closeGoogleBtn.addEventListener('click', () => {
    const modal = document.getElementById('google-auth-modal');
    if (modal) modal.classList.add('hidden');
  });

  const cancelGoogleBtn = document.getElementById('google-auth-cancel-btn');
  if (cancelGoogleBtn) cancelGoogleBtn.addEventListener('click', () => {
    const modal = document.getElementById('google-auth-modal');
    if (modal) modal.classList.add('hidden');
  });

  // Admin Portal Trigger & Close
  const openAdminBtn = document.getElementById('open-admin-btn');
  if (openAdminBtn) openAdminBtn.addEventListener('click', openAdminModal);

  const closeAdminBtn = document.getElementById('close-admin-btn');
  if (closeAdminBtn) closeAdminBtn.addEventListener('click', closeAdminModal);

  // Admin Tab Switching
  document.querySelectorAll('.admin-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.admin-tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.admin-tab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const pane = document.getElementById(btn.dataset.tab);
      if (pane) pane.classList.add('active');
      if (btn.dataset.tab === 'admin-tab-satellite') {
        populateAdminSatDropdowns();
      }
    });
  });

  // Admin Settings Form
  const adminSettingsForm = document.getElementById('admin-settings-form');
  if (adminSettingsForm) adminSettingsForm.addEventListener('submit', handleSaveAdminSettings);

  // Key Visibility Toggle
  const toggleKeyBtn = document.getElementById('toggle-key-visibility');
  if (toggleKeyBtn) {
    toggleKeyBtn.addEventListener('click', () => {
      const input = document.getElementById('admin-gemini-key');
      input.type = input.type === 'password' ? 'text' : 'password';
    });
  }

  // Admin Satellite Ingestion Handlers
  const satCountrySelect = document.getElementById('admin-sat-country');
  if (satCountrySelect) {
    satCountrySelect.addEventListener('change', (e) => onAdminSatCountryChanged(e.target.value));
  }

  const startSatIngestionBtn = document.getElementById('start-sat-ingestion-btn');
  if (startSatIngestionBtn) {
    startSatIngestionBtn.addEventListener('click', handleSatelliteIngestion);
  }

  const quickFillNagpur = document.getElementById('quick-fill-nagpur-btn');
  if (quickFillNagpur) {
    quickFillNagpur.addEventListener('click', () => {
      const nameEl = document.getElementById('new-city-name');
      const countryEl = document.getElementById('new-city-country');
      const flagEl = document.getElementById('new-city-flag');
      const latEl = document.getElementById('new-city-lat');
      const lngEl = document.getElementById('new-city-lng');
      const currEl = document.getElementById('new-city-currency');
      const budgetEl = document.getElementById('new-city-budget');
      if (nameEl) nameEl.value = "Nagpur";
      if (countryEl) countryEl.value = "India";
      if (flagEl) flagEl.value = "🇮🇳";
      if (latEl) latEl.value = "21.1458";
      if (lngEl) lngEl.value = "79.0882";
      if (currEl) currEl.value = "INR|₹";
      if (budgetEl) budgetEl.value = "12000000";
    });
  }

  // Target Geography Cascading Handlers
  const countrySelect = document.getElementById('country-select');
  if (countrySelect) {
    countrySelect.addEventListener('change', (e) => {
      onCountryChanged(e.target.value);
    });
  }

  const citySelect = document.getElementById('city-select');
  if (citySelect) {
    citySelect.addEventListener('change', (e) => {
      onCityChanged(e.target.value);
    });
  }

  // Ward Precision Selector Handler
  const wardSelect = document.getElementById('ward-select');
  if (wardSelect) {
    wardSelect.addEventListener('change', (e) => {
      onWardPrecisionChanged(e.target.value);
    });
  }

  // Decision-Maker Persona Selector Handler
  const personaSelect = document.getElementById('persona-select');
  if (personaSelect) {
    personaSelect.addEventListener('change', (e) => {
      selectedPersona = e.target.value;
      const badge = document.getElementById('plan-persona-badge');
      if (badge) badge.textContent = selectedPersona;
      runAvaniAgent();
    });
  }

  // Paid GCP Infra Modal Triggers
  const infraModalBtn = document.getElementById('infra-modal-btn');
  const infraModal = document.getElementById('infra-modal');
  const closeInfraBtn = document.getElementById('close-infra-btn');
  if (infraModalBtn && infraModal) {
    infraModalBtn.addEventListener('click', () => {
      infraModal.classList.remove('hidden');
    });
  }
  if (closeInfraBtn && infraModal) {
    closeInfraBtn.addEventListener('click', () => {
      infraModal.classList.add('hidden');
    });
  }

  // Satellite Data Lineage Modal Triggers
  const dataSourcesBtn = document.getElementById('data-sources-btn');
  const dataSourcesModal = document.getElementById('data-sources-modal');
  const closeDataSourcesBtn = document.getElementById('close-data-sources-btn');
  if (dataSourcesBtn && dataSourcesModal) {
    dataSourcesBtn.addEventListener('click', () => {
      const gcpModal = document.getElementById('gcp-stack-modal');
      const infModal = document.getElementById('infra-modal');
      if (gcpModal) gcpModal.classList.add('hidden');
      if (infModal) infModal.classList.add('hidden');
      dataSourcesModal.classList.remove('hidden');
    });
  }
  if (closeDataSourcesBtn && dataSourcesModal) {
    closeDataSourcesBtn.addEventListener('click', () => {
      dataSourcesModal.classList.add('hidden');
    });
  }
  if (dataSourcesModal) {
    dataSourcesModal.addEventListener('click', (e) => {
      if (e.target === dataSourcesModal) dataSourcesModal.classList.add('hidden');
    });
  }

  // Google Cloud Stack Modal Triggers
  const gcpStackBtn = document.getElementById('gcp-stack-btn');
  const gcpStackModal = document.getElementById('gcp-stack-modal');
  const closeGcpStackBtn = document.getElementById('close-gcp-stack-btn');
  if (gcpStackBtn && gcpStackModal) {
    gcpStackBtn.addEventListener('click', () => {
      const dsModal = document.getElementById('data-sources-modal');
      const infModal = document.getElementById('infra-modal');
      if (dsModal) dsModal.classList.add('hidden');
      if (infModal) infModal.classList.add('hidden');
      gcpStackModal.classList.remove('hidden');
    });
  }
  if (closeGcpStackBtn && gcpStackModal) {
    closeGcpStackBtn.addEventListener('click', () => {
      gcpStackModal.classList.add('hidden');
    });
  }
  if (gcpStackModal) {
    gcpStackModal.addEventListener('click', (e) => {
      if (e.target === gcpStackModal) gcpStackModal.classList.add('hidden');
    });
  }

  // Timelapse Play & Slider Listeners
  const tlPlayBtn = document.getElementById('timelapse-play-btn');
  if (tlPlayBtn) tlPlayBtn.addEventListener('click', toggleTimelapsePlay);

  const btn12yr = document.getElementById('tl-mode-12yr');
  const btn20yr = document.getElementById('tl-mode-20yr');
  if (btn12yr && btn20yr) {
    btn12yr.addEventListener('click', () => switchTimelapseMode("12yr"));
    btn20yr.addEventListener('click', () => switchTimelapseMode("20yr"));
  }

  const tlSlider = document.getElementById('timelapse-year-slider');
  if (tlSlider) {
    tlSlider.addEventListener('input', (e) => {
      currentTimelapseYearIndex = parseInt(e.target.value);
      renderTimelapseYear(currentTimelapseYearIndex);
    });
  }

  bindTimelapseTicks();
}

// ================= RESULTS TAB SWITCHING & SCENARIO SELECTION =================
function switchResultsTab(tabId) {
  // Update tab button styles
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabId);
  });

  // Update tab panels
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.toggle('active', pane.id === tabId);
  });

  // Handle specific tab data loading without synthetic re-clicks
  if (tabId === 'tab-timeline') {
    loadTemperatureTimeline(currentSelectedCity, selectedWardId);
    loadHeatCalendar(currentSelectedCity);
    setTimeout(() => {
      if (diurnalChartInstance) {
        diurnalChartInstance.resize();
        diurnalChartInstance.update();
      }
    }, 60);
  } else if (tabId === 'tab-comparison') {
    runComparison();
  }
}

function selectAndLoadScenario(scenarioKey) {
  if (!scenarioKey) return;
  selectedScenario = scenarioKey;

  // 1. Sync left sidebar scenario buttons
  document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.type === scenarioKey);
  });

  // 2. Sync comparison grid cards (if rendered)
  document.querySelectorAll('.comp-card').forEach(card => {
    const isSelected = card.dataset.key === scenarioKey;
    card.classList.toggle('highlight', isSelected);
    const badge = card.querySelector('.comp-status-badge');
    if (badge) {
      badge.innerHTML = isSelected 
        ? '<span style="color: #34d399; font-weight: 700;">● Active Scenario</span>' 
        : '<span style="color: #94a3b8;">Click to select</span>';
    }
    const sBtn = card.querySelector('.select-scenario-btn');
    if (sBtn) {
      sBtn.textContent = isSelected ? '✓ Loaded' : '👉 Select & Load';
      sBtn.style.background = isSelected ? 'rgba(52, 211, 153, 0.2)' : 'rgba(56, 189, 248, 0.15)';
      sBtn.style.borderColor = isSelected ? '#34d399' : 'rgba(56, 189, 248, 0.4)';
      sBtn.style.color = isSelected ? '#34d399' : '#38bdf8';
    }
  });

  // 3. Automatically run Avani agent to synthesize and compute this scenario
  runAvaniAgent();
}

// ================= AUTHENTICATION LOGIC =================
let cachedAuthConfig = null;
let isDashboardInitialized = false;

function launchDashboardSession(email) {
  const landing = document.getElementById('landing-gateway-page');
  const dashboard = document.getElementById('dashboard-app-layout');
  const navActions = document.getElementById('dashboard-nav-actions');
  const userPill = document.getElementById('auth-user-pill');
  const userText = document.getElementById('auth-user-email');

  if (landing) landing.classList.add('hidden');
  if (dashboard) dashboard.classList.remove('hidden');
  if (navActions) navActions.classList.remove('hidden');
  if (userPill && userText) {
    userText.textContent = email;
    userPill.classList.remove('hidden');
  }

  if (!isDashboardInitialized) {
    isDashboardInitialized = true;
    initMap();
    loadGeographicHierarchy().then(() => {
      loadClimateCells(currentSelectedCity);
      loadTimelapseData(currentSelectedCity);
    });
  } else {
    if (map) {
      setTimeout(() => map.invalidateSize(), 200);
    }
  }

  checkAdminAlerts();
}

function showLandingGateway() {
  const landing = document.getElementById('landing-gateway-page');
  const dashboard = document.getElementById('dashboard-app-layout');
  const navActions = document.getElementById('dashboard-nav-actions');
  const userPill = document.getElementById('auth-user-pill');

  if (landing) landing.classList.remove('hidden');
  if (dashboard) dashboard.classList.add('hidden');
  if (navActions) navActions.classList.add('hidden');
  if (userPill) userPill.classList.add('hidden');

  const emailInput = document.getElementById('login-email');
  const pwInput = document.getElementById('login-password');
  if (emailInput) emailInput.value = '';
  if (pwInput) pwInput.value = '';
  const errorMsg = document.getElementById('login-error-msg');
  if (errorMsg) errorMsg.classList.add('hidden');
}

async function initAuth() {
  try {
    const res = await fetch('/api/auth/config');
    cachedAuthConfig = await res.json();
    
    if (!cachedAuthConfig.auth_enabled) {
      launchDashboardSession('public@avani.eco');
      return;
    }

    const token = localStorage.getItem('avani_token');
    if (!token) {
      showLandingGateway();
      return;
    }

    // Verify token with backend
    const verifyRes = await fetch('/api/auth/verify', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (verifyRes.ok) {
      const data = await verifyRes.json();
      launchDashboardSession(data.email);
    } else {
      localStorage.removeItem('avani_token');
      localStorage.removeItem('avani_email');
      showLandingGateway();
    }
  } catch (err) {
    console.warn("Auth verification error:", err);
    showLandingGateway();
  }
}

function showAuthenticatedUser(email) {
  launchDashboardSession(email);
}

async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  const errorMsg = document.getElementById('login-error-msg');
  const submitBtn = document.getElementById('login-submit-btn');

  submitBtn.disabled = true;
  submitBtn.textContent = "Verifying Access...";
  errorMsg.classList.add('hidden');

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!res.ok) {
      throw new Error("Invalid credentials or unauthorized user");
    }

    const data = await res.json();
    localStorage.setItem('avani_token', data.token);
    localStorage.setItem('avani_email', data.email);
    showAuthenticatedUser(data.email);
  } catch (err) {
    errorMsg.textContent = "Access Denied: Invalid credentials or account is not authorized.";
    errorMsg.classList.remove('hidden');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Sign In to Decision Engine";
  }
}

async function handleFirebaseGoogleLogin() {
  const errorMsg = document.getElementById('login-error-msg');
  if (errorMsg) errorMsg.classList.add('hidden');

  // 1. Try 1-Click Google Sign-In via Firebase Popup
  if (window.firebase && window.firebase.auth) {
    try {
      const provider = new firebase.auth.GoogleAuthProvider();
      provider.setCustomParameters({ prompt: 'select_account' });
      const result = await firebase.auth().signInWithPopup(provider);
      if (result && result.user && result.user.email) {
        const idToken = await result.user.getIdToken();
        await executeGoogleLoginSubmit(result.user.email, result.user.displayName, idToken);
        return;
      }
    } catch (popupErr) {
      console.warn("Firebase popup closed or not enabled, displaying Google account access dialog:", popupErr);
    }
  }

  // 2. Fallback to Google Account modal dialog
  const modal = document.getElementById('google-auth-modal');
  const alertBox = document.getElementById('google-auth-alert');
  const emailInput = document.getElementById('google-auth-email');
  if (alertBox) alertBox.classList.add('hidden');
  if (emailInput) {
    emailInput.value = '';
    setTimeout(() => emailInput.focus(), 150);
  }
  if (modal) modal.classList.remove('hidden');
}

async function executeGoogleLoginSubmit(email, displayName, token) {
  const errorMsg = document.getElementById('login-error-msg');
  const modal = document.getElementById('google-auth-modal');
  const modalAlert = document.getElementById('google-auth-alert');
  if (errorMsg) errorMsg.classList.add('hidden');

  try {
    const res = await fetch('/api/auth/firebase-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email,
        displayName: displayName || email.split('@')[0],
        token: token || `google_token_${Date.now()}`
      })
    });

    const data = await res.json();

    if (!res.ok) {
      // 403: Pending review or Access Request submitted
      const msg = `<strong>⏳ Access Request Registered!</strong><br>${data.detail || 'Your Google account is awaiting Administrator approval.'}`;
      if (modal && !modal.classList.contains('hidden') && modalAlert) {
        modalAlert.style.background = 'rgba(245, 158, 11, 0.15)';
        modalAlert.style.border = '1px solid rgba(245, 158, 11, 0.4)';
        modalAlert.style.color = '#fbbf24';
        modalAlert.innerHTML = msg;
        modalAlert.classList.remove('hidden');
      } else if (errorMsg) {
        errorMsg.style.background = 'rgba(245, 158, 11, 0.15)';
        errorMsg.style.border = '1px solid rgba(245, 158, 11, 0.4)';
        errorMsg.style.color = '#fbbf24';
        errorMsg.innerHTML = msg;
        errorMsg.classList.remove('hidden');
      }
      return;
    }

    // Success (User is approved & active!)
    localStorage.setItem('avani_token', data.token);
    localStorage.setItem('avani_email', data.email);
    if (modal) modal.classList.add('hidden');
    showAuthenticatedUser(data.email);
  } catch (err) {
    if (errorMsg) {
      errorMsg.textContent = "Google Sign-In Error. Please try again.";
      errorMsg.classList.remove('hidden');
    }
  }
}

window.submitGoogleAuth = async function(e) {
  if (e) e.preventDefault();
  const emailInput = document.getElementById('google-auth-email');
  const alertBox = document.getElementById('google-auth-alert');
  const submitBtn = document.getElementById('google-auth-submit-btn');
  const email = (emailInput.value || '').trim().toLowerCase();

  if (!email || !email.includes('@')) {
    alertBox.style.background = 'rgba(239, 68, 68, 0.15)';
    alertBox.style.border = '1px solid rgba(239, 68, 68, 0.4)';
    alertBox.style.color = '#f87171';
    alertBox.textContent = 'Please enter a valid Gmail address.';
    alertBox.classList.remove('hidden');
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span>⏳ Submitting...</span>';
  alertBox.classList.add('hidden');

  try {
    await executeGoogleLoginSubmit(email, email.split('@')[0], `google_token_${Date.now()}`);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<span>🚀 Continue with Google</span>';
  }
};

function handleLogout() {
  fetch('/api/auth/logout', { method: 'POST' }).catch(() => {});
  localStorage.removeItem('avani_token');
  localStorage.removeItem('avani_email');
  showLandingGateway();
}

// ================= ADMIN PORTAL LOGIC =================
async function checkAdminAlerts() {
  try {
    const res = await fetch('/api/admin/dashboard');
    const data = await res.json();
    const pendingAlerts = (data.alerts || []).filter(a => a.status === 'pending');
    const badge = document.getElementById('admin-alert-badge');
    const countTag = document.getElementById('admin-pending-count');
    
    if (badge) {
      badge.textContent = pendingAlerts.length;
      if (pendingAlerts.length > 0) badge.classList.remove('hidden');
      else badge.classList.add('hidden');
    }
    if (countTag) countTag.textContent = pendingAlerts.length;
  } catch (err) {
    console.warn("Could not check admin alerts", err);
  }
}

async function openAdminModal() {
  const adminOverlay = document.getElementById('admin-modal-overlay');
  adminOverlay.classList.remove('hidden');
  await loadAdminDashboard();
}

function closeAdminModal() {
  document.getElementById('admin-modal-overlay').classList.add('hidden');
}

async function loadAdminDashboard() {
  try {
    const res = await fetch('/api/admin/dashboard');
    const data = await res.json();
    
    renderAdminAlerts(data.alerts || []);
    renderAdminUsers(data.users || []);
    renderAdminQuotas(data.quotas || {});
    populateAdminSettings(data.config || {});
    populateAdminSatDropdowns();
  } catch (err) {
    console.error("Failed loading admin dashboard", err);
  }
}

function renderAdminAlerts(alerts) {
  const container = document.getElementById('admin-alerts-container');
  const pending = alerts.filter(a => a.status === 'pending');
  
  const countTag = document.getElementById('admin-pending-count');
  if (countTag) countTag.textContent = pending.length;

  if (pending.length === 0) {
    container.innerHTML = `
      <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 10px 14px; font-size: 12px; color: #34d399;">
        ✓ All user access requests are resolved. No pending alerts.
      </div>
    `;
    return;
  }

  container.innerHTML = pending.map(a => `
    <div class="admin-alert-card">
      <div class="alert-card-left">
        <span class="alert-card-title">🚨 ${a.type}: <code>${a.user_email}</code></span>
        <span class="alert-card-desc">${a.message}</span>
      </div>
      <div class="alert-actions" style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
        <select id="alert-role-${a.id}" style="background: rgba(255,255,255,0.08); color: var(--color-cyan); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px; padding: 5px 8px; font-size: 11px; cursor: pointer;">
          <option value="Municipal Planner" selected>Role: Municipal Planner</option>
          <option value="Climate Scientist">Role: Climate Scientist</option>
          <option value="Urban Resilience Director">Role: Urban Resilience Director</option>
          <option value="Judge / Evaluator">Role: Judge / Evaluator</option>
          <option value="Super Admin">Role: Super Admin</option>
        </select>
        <button class="btn-approve" onclick="approveAlertWithRole('${a.id}')">✓ Approve & Assign Role</button>
        <button class="btn-reject" onclick="resolveAdminAlert('${a.id}', 'reject')">✕ Reject</button>
      </div>
    </div>
  `).join('');
}

function renderAdminUsers(users) {
  const tbody = document.getElementById('admin-users-table-body');
  const countTag = document.getElementById('users-count-tag');
  if (countTag) countTag.textContent = `${users.length} Registered Users`;

  const availableRoles = [
    "Municipal Planner",
    "Climate Scientist",
    "Urban Resilience Director",
    "Judge / Evaluator",
    "Super Admin"
  ];

  tbody.innerHTML = users.map(u => {
    const statusClass = (u.status || 'active').toLowerCase();
    const isSuperAdmin = u.email === 'srbodkhe@gmail.com';
    return `
      <tr>
        <td><strong>${u.email}</strong> ${isSuperAdmin ? '👑 (Admin)' : ''}</td>
        <td>
          ${isSuperAdmin ? `
            <span style="color: var(--color-cyan); font-weight: 600;">Super Admin</span>
          ` : `
            <select class="admin-role-select" onchange="promoteUserRole('${u.email}', this.value)" title="Promote or Change Role" style="background: rgba(255,255,255,0.08); color: var(--color-cyan); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px; padding: 4px 6px; font-size: 12px; cursor: pointer;">
              ${availableRoles.map(r => `<option value="${r}" ${u.role === r ? 'selected' : ''}>${r}</option>`).join('')}
            </select>
          `}
        </td>
        <td><span class="user-status-badge ${statusClass}">${u.status}</span></td>
        <td><code>${u.provider || 'direct'}</code></td>
        <td>${u.login_count || 1}</td>
        <td>
          <button class="table-btn" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; margin-right: 4px;" onclick="promptResetPassword('${u.email}')">Reset Password</button>
          ${isSuperAdmin ? '<span style="color: var(--text-dim); font-size: 11px;">Protected</span>' : `
            ${u.status === 'Active' ? `
              <button class="table-btn suspend" onclick="performAdminUserAction('${u.email}', 'suspend')">Suspend</button>
            ` : `
              <button class="table-btn activate" onclick="performAdminUserAction('${u.email}', 'activate')">Approve / Activate</button>
            `}
            <button class="table-btn" style="background: rgba(255,255,255,0.06); color: #fff;" onclick="performAdminUserAction('${u.email}', 'delete')">Remove</button>
          `}
        </td>
      </tr>
    `;
  }).join('');
}

function renderAdminQuotas(quotas) {
  const container = document.getElementById('admin-quotas-container');
  container.innerHTML = Object.entries(quotas).map(([k, q]) => {
    const pct = Math.min(100, Math.round((q.used / q.limit) * 100));
    return `
      <div class="quota-card">
        <div class="quota-header">
          <span class="quota-title">${q.label}</span>
          <span class="quota-numbers">${q.used.toLocaleString()} / ${q.limit.toLocaleString()}</span>
        </div>
        <div class="quota-progress-track">
          <div class="quota-progress-fill" style="width: ${pct}%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--text-dim);">
          <span>Used: ${pct}%</span>
          <span>Available: ${(q.limit - q.used).toLocaleString()}</span>
        </div>
      </div>
    `;
  }).join('');
}

function populateAdminSettings(config) {
  document.getElementById('admin-gcp-project').value = config.gcp_project_id || 'avani-albedo';
  document.getElementById('admin-allowed-emails').value = config.allowed_emails || 'srbodkhe@gmail.com';
  document.getElementById('admin-earth-engine-toggle').checked = !!config.use_earth_engine_live;
  
  const keyNote = document.getElementById('gemini-key-status-note');
  if (keyNote) {
    keyNote.textContent = `Current: ${config.gemini_api_key_masked || 'Not Configured'}`;
  }
}

async function handleSaveAdminSettings(e) {
  e.preventDefault();
  const geminiKey = document.getElementById('admin-gemini-key').value.trim();
  const gcpProject = document.getElementById('admin-gcp-project').value.trim();
  const allowedEmails = document.getElementById('admin-allowed-emails').value.trim();
  const eeToggle = document.getElementById('admin-earth-engine-toggle').checked;
  const savedMsg = document.getElementById('settings-saved-msg');

  const payload = {
    gcp_project_id: gcpProject,
    allowed_emails: allowedEmails,
    use_earth_engine_live: eeToggle
  };
  if (geminiKey) payload.gemini_api_key = geminiKey;

  try {
    const res = await fetch('/api/admin/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      savedMsg.classList.remove('hidden');
      setTimeout(() => savedMsg.classList.add('hidden'), 3500);
      await loadAdminDashboard();
    }
  } catch (err) {
    alert("Could not update settings: " + err);
  }
}

// Global actions exposed for inline table onclick
window.promptResetPassword = async function(email) {
  const newPw = prompt(`🔑 Reset Password for ${email}:\n\nEnter new password:`, "AvaniAlbedo12042026#");
  if (!newPw) return;
  try {
    const res = await fetch('/api/admin/users/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, new_password: newPw })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to reset password");
    alert(`✅ Password for ${email} successfully updated!`);
    loadAdminDashboard();
  } catch (err) {
    alert(`❌ Error resetting password: ${err.message}`);
  }
};

window.performAdminUserAction = async function(email, action) {
  try {
    const res = await fetch('/api/admin/users/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, action })
    });
    if (res.ok) {
      const data = await res.json();
      renderAdminUsers(data.users || []);
    }
  } catch (err) {
    alert("User action error: " + err);
  }
};

window.resolveAdminAlert = async function(alertId, action) {
  try {
    const res = await fetch('/api/admin/alerts/resolve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alert_id: alertId, action })
    });
    if (res.ok) {
      const data = await res.json();
      renderAdminAlerts(data.alerts || []);
      renderAdminUsers(data.users || []);
      checkAdminAlerts();
    }
  } catch (err) {
    alert("Alert resolve error: " + err);
  }
};

function populateAdminSatDropdowns() {
  const satCountrySelect = document.getElementById('admin-sat-country');
  if (!satCountrySelect) return;

  if (geographicHierarchy && geographicHierarchy.countries && geographicHierarchy.countries.length > 0) {
    const currentVal = satCountrySelect.value || "India";
    satCountrySelect.innerHTML = geographicHierarchy.countries.map(c => 
      `<option value="${c.country}" ${c.country.toLowerCase() === currentVal.toLowerCase() ? "selected" : ""}>${c.flag || "🌍"} ${c.country}</option>`
    ).join('');
  }
  
  onAdminSatCountryChanged(satCountrySelect.value);
}

function onAdminSatCountryChanged(country) {
  const citySelect = document.getElementById('admin-sat-city');
  if (!citySelect) return;

  const targetCountry = (country || "India").trim().toLowerCase();

  // If geographicHierarchy is loaded, use it directly (matches country name or standard aliases)
  if (geographicHierarchy && geographicHierarchy.countries) {
    const countryObj = geographicHierarchy.countries.find(c => {
      const cName = c.country.toLowerCase();
      return cName === targetCountry || 
             (targetCountry === 'uae' && cName.includes('emirates')) ||
             (targetCountry === 'usa' && cName.includes('states')) ||
             (targetCountry === 'uk' && cName.includes('kingdom'));
    });

    if (countryObj && countryObj.cities && countryObj.cities.length > 0) {
      citySelect.innerHTML = countryObj.cities.map(ct => {
        const count = ct.wards_count || (ct.wards ? ct.wards.length : 0);
        return `<option value="${ct.key}">${ct.name} (${count} Wards)</option>`;
      }).join('');
      return;
    }
  }

  // Fallback map strictly grouped by country
  const fallbackMap = {
    "india": [
      { name: "Bengaluru (12 Wards)", val: "Bengaluru" },
      { name: "Mumbai MMR (6 Wards)", val: "Mumbai" },
      { name: "Delhi NCR (6 Wards)", val: "Delhi" },
      { name: "Hyderabad GHMC (4 Wards)", val: "Hyderabad" },
      { name: "Pune PMRDA (5 Wards)", val: "Pune" },
      { name: "Chennai GCC (5 Wards)", val: "Chennai" },
      { name: "Kolkata KMC (4 Wards)", val: "Kolkata" },
      { name: "Ahmedabad AMC (4 Wards)", val: "Ahmedabad" },
      { name: "Jaipur JDA (3 Wards)", val: "Jaipur" }
    ],
    "united arab emirates": [
      { name: "Dubai Urban Corridor (3 Wards)", val: "Dubai" }
    ],
    "uae": [
      { name: "Dubai Urban Corridor (3 Wards)", val: "Dubai" }
    ],
    "singapore": [
      { name: "Singapore Island State (3 Wards)", val: "Singapore" }
    ],
    "united kingdom": [
      { name: "Greater London Heat Basin (2 Wards)", val: "London" }
    ],
    "uk": [
      { name: "Greater London Heat Basin (2 Wards)", val: "London" }
    ],
    "united states": [
      { name: "Phoenix Metro (2 Wards)", val: "Phoenix" }
    ],
    "usa": [
      { name: "Phoenix Metro (2 Wards)", val: "Phoenix" }
    ]
  };

  const list = fallbackMap[targetCountry] || fallbackMap["india"];
  citySelect.innerHTML = list.map(c => `<option value="${c.val}">${c.name}</option>`).join('');
}

async function handleSatelliteIngestion() {
  const btn = document.getElementById('start-sat-ingestion-btn');
  const country = document.getElementById('admin-sat-country').value;
  const city = document.getElementById('admin-sat-city').value;
  const consoleEl = document.getElementById('sat-ingestion-console');

  if (!btn || !consoleEl) return;

  btn.disabled = true;
  btn.innerHTML = `<span>⏳ Ingesting Landsat & Sentinel Telemetry for ${city}...</span>`;
  consoleEl.classList.remove('hidden');
  consoleEl.innerHTML = `<div style="color: #38bdf8;">[INIT] Handshaking with Google Earth Engine & NASA/USGS Radiometric Catalogs...</div>`;

  try {
    const res = await fetch('/api/admin/satellite/fetch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ country, city })
    });

    if (!res.ok) {
      throw new Error(`Ingestion failed with HTTP ${res.status}`);
    }

    const data = await res.json();
    const logs = data.telemetry_logs || [];

    for (let i = 0; i < logs.length; i++) {
      await new Promise(r => setTimeout(r, 120));
      const line = document.createElement('div');
      line.textContent = logs[i];
      if (logs[i].includes('Complete')) {
        line.style.color = '#34d399';
        line.style.fontWeight = 'bold';
      }
      consoleEl.appendChild(line);
      consoleEl.scrollTop = consoleEl.scrollHeight;
    }

    if (city.toLowerCase() === currentSelectedCity.toLowerCase()) {
      await loadClimateCells(currentSelectedCity);
    }
    loadAdminDashboard();
  } catch (err) {
    const errLine = document.createElement('div');
    errLine.style.color = '#ef4444';
    errLine.textContent = `[ERROR] Failed to complete satellite ingestion: ${err.message}`;
    consoleEl.appendChild(errLine);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>🚀 Start Satellite Data Ingestion & Calibration</span>`;
  }
}

window.handleAddNewCitySubmit = async function(event) {
  event.preventDefault();
  const btn = document.getElementById('submit-add-city-btn');
  const consoleEl = document.getElementById('add-city-console');
  
  const name = document.getElementById('new-city-name').value.trim();
  const country = document.getElementById('new-city-country').value.trim();
  const flag = document.getElementById('new-city-flag').value.trim();
  const lat = parseFloat(document.getElementById('new-city-lat').value);
  const lng = parseFloat(document.getElementById('new-city-lng').value);
  const currVal = document.getElementById('new-city-currency').value;
  const [currency, currencySymbol] = currVal.split('|');
  const budget = parseFloat(document.getElementById('new-city-budget').value);

  if (!btn || !consoleEl) return;
  btn.disabled = true;
  btn.innerHTML = `<span>⏳ Onboarding ${name}...</span>`;
  consoleEl.classList.remove('hidden');
  consoleEl.innerHTML = `<div style="color: #38bdf8;">[INIT] Registering ${name} (${country}) into Avani Albedo Core Engine...</div>`;

  try {
    const res = await fetch('/api/admin/cities/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: name,
        country: country,
        country_flag: flag,
        latitude: lat,
        longitude: lng,
        currency: currency,
        currency_symbol: currencySymbol,
        default_budget: budget
      })
    });

    if (!res.ok) {
      throw new Error(`Onboarding failed with HTTP ${res.status}`);
    }

    const data = await res.json();
    
    consoleEl.innerHTML += `
      <div style="color: #60a5fa;">[GEOSPATIAL] Synthesized ${data.wards_count} microclimate polygons centered at [${lat}, ${lng}]...</div>
      <div style="color: #60a5fa;">[HVI] Calculated baseline thermal severity, built density & critical infrastructure...</div>
      <div style="color: #34d399; font-weight: bold;">[SUCCESS] ${data.message}</div>
    `;

    // Refresh geographic hierarchy and update all UI dropdowns
    await loadGeographicHierarchy();
    populateAdminSatDropdowns();

    // Select the new city on the dashboard automatically
    const countrySelect = document.getElementById('country-select');
    if (countrySelect) {
      for (let i = 0; i < countrySelect.options.length; i++) {
        if (countrySelect.options[i].value.toLowerCase() === country.toLowerCase()) {
          countrySelect.selectedIndex = i;
          break;
        }
      }
      populateCityDropdown(country);
    }

    const citySelect = document.getElementById('city-select');
    if (citySelect) {
      for (let i = 0; i < citySelect.options.length; i++) {
        if (citySelect.options[i].value.toLowerCase() === data.city_key.toLowerCase()) {
          citySelect.selectedIndex = i;
          currentSelectedCity = citySelect.value;
          await loadClimateCells(currentSelectedCity);
          break;
        }
      }
    }

    consoleEl.innerHTML += `<div style="color: #facc15;">[NAVIGATED] Switched main dashboard GIS view to ${name}!</div>`;

  } catch (err) {
    consoleEl.innerHTML += `<div style="color: #ef4444;">[ERROR] Failed to onboard city: ${err.message}</div>`;
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>🚀 Register City & Generate Microclimate Grid</span>`;
  }
};


window.approveAlertWithRole = async function(alertId) {
  const select = document.getElementById(`alert-role-${alertId}`);
  const role = select ? select.value : "Municipal Planner";
  try {
    const res = await fetch('/api/admin/alerts/resolve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ alert_id: alertId, action: 'approve', role: role })
    });
    if (res.ok) {
      const data = await res.json();
      renderAdminAlerts(data.alerts || []);
      renderAdminUsers(data.users || []);
      checkAdminAlerts();
    }
  } catch (err) {
    alert("Approval error: " + err);
  }
};

window.promoteUserRole = async function(email, newRole) {
  try {
    const res = await fetch('/api/admin/users/role', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, role: newRole })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to update role");
    renderAdminUsers(data.users || []);
    alert(`👑 Role updated: ${email} is now a ${newRole}!`);
  } catch (err) {
    alert("Role update error: " + err.message);
  }
};

async function loadSystemStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    const statusText = document.getElementById('system-status-text');
    statusText.textContent = `Active • ${data.gemini_model} • ${data.cells_loaded} Wards`;
  } catch (err) {
    console.error("Status load failed", err);
    document.getElementById('system-status-text').textContent = "Offline Fallback Mode";
  }
}

// ================= GEOGRAPHY (COUNTRY & CITY) LOGIC =================
async function loadGeographicHierarchy() {
  try {
    const res = await fetch('/api/geography/countries-and-cities');
    geographicHierarchy = await res.json();
    populateCountryDropdown();
  } catch (err) {
    console.error("Failed to load geographic hierarchy", err);
  }
}

function populateCountryDropdown() {
  const countrySelect = document.getElementById('country-select');
  if (!countrySelect || !geographicHierarchy) return;

  countrySelect.innerHTML = '';
  geographicHierarchy.countries.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.country;
    opt.textContent = `${c.flag} ${c.country}`;
    if (c.country === geographicHierarchy.default_country) {
      opt.selected = true;
    }
    countrySelect.appendChild(opt);
  });

  currentSelectedCountry = geographicHierarchy.default_country;
  populateCityDropdown(currentSelectedCountry);
}

function populateCityDropdown(countryName) {
  const citySelect = document.getElementById('city-select');
  if (!citySelect || !geographicHierarchy) return;

  const countryObj = geographicHierarchy.countries.find(
    c => c.country.toLowerCase() === countryName.toLowerCase()
  );
  if (!countryObj) return;

  citySelect.innerHTML = '';
  countryObj.cities.forEach(city => {
    const opt = document.createElement('option');
    opt.value = city.key;
    opt.textContent = `${city.name} (${city.key})`;
    if (city.key === geographicHierarchy.default_city) {
      opt.selected = true;
    }
    citySelect.appendChild(opt);
  });

  currentSelectedCity = citySelect.value;
  populateWardDropdown(currentSelectedCity);
  const cityObj = countryObj.cities.find(ct => ct.key === currentSelectedCity);
  if (cityObj) {
    currentCurrency = cityObj.currency || "INR";
    currentCurrencySymbol = cityObj.currency_symbol || "₹";
    currentUsdRate = cityObj.usd_rate || (currentCurrency === "INR" ? 0.012 : (currentCurrency === "AED" ? 0.272 : (currentCurrency === "SGD" ? 0.746 : (currentCurrency === "GBP" ? 1.282 : 1.0))));
    updateBudgetDisplay();
  }
}

function populateWardDropdown(cityName) {
  const wardSelect = document.getElementById('ward-select');
  if (!wardSelect || !geographicHierarchy) return;

  wardSelect.innerHTML = '<option value="ALL" selected>🌐 All Metropolitan Wards (Full City)</option>';
  
  let cityMeta = null;
  for (const c of geographicHierarchy.countries) {
    const match = c.cities.find(ct => ct.key === cityName);
    if (match) {
      cityMeta = match;
      break;
    }
  }

  if (cityMeta && cityMeta.wards) {
    cityMeta.wards.forEach(w => {
      const opt = document.createElement('option');
      opt.value = w.cell_id;
      opt.textContent = `${w.name} (${w.zone} • LST ${w.lst}°C)`;
      wardSelect.appendChild(opt);
    });
  }
  selectedWardId = null;
}

async function onWardPrecisionChanged(wardId) {
  if (wardId === "ALL" || !wardId) {
    selectedWardId = null;
    loadTemperatureTimeline(currentSelectedCity, null);
    loadSpotPhaseEvaluation(currentSelectedCity, null);
    return;
  }
  selectedWardId = wardId;
  const targetCell = climateCells.find(c => c.cell_id === wardId);
  if (targetCell) {
    map.flyTo([targetCell.center_lat, targetCell.center_lng], 13, { duration: 1.2 });
    openCellInspector(targetCell);
  }
  loadTemperatureTimeline(currentSelectedCity, wardId);
  loadSpotPhaseEvaluation(currentSelectedCity, wardId);
}

async function onCountryChanged(countryName) {
  currentSelectedCountry = countryName;
  populateCityDropdown(countryName);
  const citySelect = document.getElementById('city-select');
  if (citySelect && citySelect.value) {
    await onCityChanged(citySelect.value);
  }
}

async function onCityChanged(cityKey) {
  currentSelectedCity = cityKey;
  selectedWardId = null;
  populateWardDropdown(cityKey);

  const wardSelect = document.getElementById('ward-select');
  if (wardSelect) wardSelect.value = "ALL";

  // Smooth camera flight to target city
  let cityMeta = null;
  if (geographicHierarchy) {
    for (const c of geographicHierarchy.countries) {
      const match = c.cities.find(ct => ct.key === cityKey);
      if (match) {
        cityMeta = match;
        break;
      }
    }
  }

  if (cityMeta) {
    currentCurrency = cityMeta.currency || "INR";
    currentCurrencySymbol = cityMeta.currency_symbol || "₹";
    currentUsdRate = cityMeta.usd_rate || (currentCurrency === "INR" ? 0.012 : (currentCurrency === "AED" ? 0.272 : (currentCurrency === "SGD" ? 0.746 : (currentCurrency === "GBP" ? 1.282 : 1.0))));
    updateBudgetDisplay();
    if (map) {
      map.flyTo(cityMeta.center, cityMeta.zoom, { duration: 1.5 });
    }
  }

  // Reload climate cells, timeline, calendar, and spot evaluations for the chosen city
  await loadClimateCells(currentSelectedCity);
  await loadTemperatureTimeline(currentSelectedCity, null);
  await loadHeatCalendar(currentSelectedCity);
  await loadSpotPhaseEvaluation(currentSelectedCity, null);
  loadTimelapseData(currentSelectedCity);
}

async function loadClimateCells(city = currentSelectedCity) {
  try {
    const res = await fetch(`/api/cells?city=${encodeURIComponent(city)}`);
    climateCells = await res.json();
    renderMapPolygons();
    // Auto-trigger default plan
    runAvaniAgent();
  } catch (err) {
    console.error("Error loading cells", err);
  }
}

async function runAvaniAgent() {
  const btn = document.getElementById('run-agent-btn');
  const spinner = document.getElementById('agent-spinner');
  const btnText = document.getElementById('btn-text');
  
  btn.disabled = true;
  spinner.classList.remove('hidden');
  btnText.textContent = `Synthesizing Plan for ${currentSelectedCity}...`;

  try {
    const res = await fetch('/api/action-plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        city: currentSelectedCity,
        budget_inr: currentBudgetInr,
        scenario_type: selectedScenario,
        persona: selectedPersona,
        selected_ward_id: selectedWardId
      })
    });
    
    const plan = await res.json();
    currentActionPlan = plan;
    currentScenarioResult = plan.scenario_result;
    
    updateKpiCards(currentScenarioResult);
    renderActionPlan(plan);
    renderAllocationsTable(currentScenarioResult);
    renderInterventionMarkers(currentScenarioResult);
    
    // If no tab is active yet (initial load), default to Plan tab
    const activeTab = document.querySelector('.tab-btn.active');
    if (!activeTab) {
      switchResultsTab('tab-plan');
    }
  } catch (err) {
    console.error("Action plan generation error:", err);
    alert("Could not generate action plan. Check console for details.");
  } finally {
    btn.disabled = false;
    spinner.classList.add('hidden');
    btnText.textContent = "🚀 Run Avani Climate Agent";
  }
}

// ================= TEMPERATURE TIMELINE & CHARTS =================
function setTemperatureSensorMode(mode) {
  currentTempSensorMode = mode;
  const btnLst = document.getElementById('temp-mode-btn-lst');
  const btnAir = document.getElementById('temp-mode-btn-air');
  const cardSurface = document.getElementById('card-mode-surface');
  const cardAmbient = document.getElementById('card-mode-ambient');
  const badgeSurface = document.getElementById('badge-mode-surface');
  const badgeAmbient = document.getElementById('badge-mode-ambient');
  const statusPill = document.getElementById('temp-mode-status-pill');
  const explainNote = document.getElementById('temp-explainability-note');
  const exampleSurface = document.getElementById('example-surface-text');
  const exampleAmbient = document.getElementById('example-ambient-text');

  const peakVal = currentTimelineData ? currentTimelineData.peak_high_c.toFixed(1) : '42.8';
  const airVal = currentTimelineData && currentTimelineData.air_temp_high_c ? currentTimelineData.air_temp_high_c.toFixed(1) : '31.5';
  const cityName = currentTimelineData ? currentTimelineData.city : 'Bengaluru';

  if (exampleSurface) {
    exampleSurface.textContent = `Bengaluru Surface Temperature: ~42.8°C (Current ${cityName}: ~${peakVal}°C)`;
  }
  if (exampleAmbient) {
    exampleAmbient.textContent = `Bengaluru Air Temperature: ~31.5°C (Current ${cityName}: ~${airVal}°C)`;
  }

  if (mode === "air") {
    if (btnLst) {
      btnLst.style.background = "transparent";
      btnLst.style.color = "#94a3b8";
    }
    if (btnAir) {
      btnAir.style.background = "#38bdf8";
      btnAir.style.color = "#020617";
    }
    if (cardSurface) {
      cardSurface.style.background = "rgba(244, 63, 94, 0.04)";
      cardSurface.style.border = "1px solid rgba(244, 63, 94, 0.2)";
      cardSurface.style.boxShadow = "none";
    }
    if (cardAmbient) {
      cardAmbient.style.background = "rgba(56, 189, 248, 0.12)";
      cardAmbient.style.border = "1.5px solid #38bdf8";
      cardAmbient.style.boxShadow = "0 0 12px rgba(56, 189, 248, 0.25)";
    }
    if (badgeSurface) {
      badgeSurface.textContent = "SWITCH";
      badgeSurface.style.background = "transparent";
      badgeSurface.style.color = "#64748b";
      badgeSurface.style.border = "1px solid #475569";
    }
    if (badgeAmbient) {
      badgeAmbient.textContent = "ACTIVE";
      badgeAmbient.style.background = "#38bdf8";
      badgeAmbient.style.color = "#020617";
      badgeAmbient.style.border = "none";
    }
    if (statusPill) {
      statusPill.textContent = "🌤️ Weather APIs (AccuWeather/IMD) • 2-Meter Shaded Air Temperature";
      statusPill.style.color = "#38bdf8";
      statusPill.style.background = "rgba(56, 189, 248, 0.15)";
      statusPill.style.borderColor = "rgba(56, 189, 248, 0.3)";
    }
    if (explainNote) {
      explainNote.innerHTML = `<strong style="color: #38bdf8;">🌤️ Ambient Air Temperature Mode:</strong> Sourced from <b>Weather APIs (AccuWeather/IMD)</b>. Measures human-experienced shaded air temperature recorded in a 2-meter Stevenson screen (e.g. Bengaluru Air: <b>~31.5°C</b>). Asphalt & concrete roof skins heat up <b>10°C–14°C hotter</b> under direct sunlight!`;
    }
  } else {
    if (btnLst) {
      btnLst.style.background = "var(--color-orange)";
      btnLst.style.color = "#020617";
    }
    if (btnAir) {
      btnAir.style.background = "transparent";
      btnAir.style.color = "#94a3b8";
    }
    if (cardSurface) {
      cardSurface.style.background = "rgba(244, 63, 94, 0.12)";
      cardSurface.style.border = "1.5px solid #f43f5e";
      cardSurface.style.boxShadow = "0 0 12px rgba(244, 63, 94, 0.25)";
    }
    if (cardAmbient) {
      cardAmbient.style.background = "rgba(56, 189, 248, 0.04)";
      cardAmbient.style.border = "1px solid rgba(56, 189, 248, 0.2)";
      cardAmbient.style.boxShadow = "none";
    }
    if (badgeSurface) {
      badgeSurface.textContent = "ACTIVE";
      badgeSurface.style.background = "#f43f5e";
      badgeSurface.style.color = "#fff";
      badgeSurface.style.border = "none";
    }
    if (badgeAmbient) {
      badgeAmbient.textContent = "SWITCH";
      badgeAmbient.style.background = "transparent";
      badgeAmbient.style.color = "#64748b";
      badgeAmbient.style.border = "1px solid #475569";
    }
    if (statusPill) {
      statusPill.textContent = "🛰️ Landsat 8/9 Thermal Infrared Sensor • Google Earth Engine";
      statusPill.style.color = "#f43f5e";
      statusPill.style.background = "rgba(244, 63, 94, 0.15)";
      statusPill.style.borderColor = "rgba(244, 63, 94, 0.3)";
    }
    if (explainNote) {
      explainNote.innerHTML = `<strong style="color: #38bdf8;">💡 Why Surface Temp (${peakVal}°C) differs from AccuWeather Air Temp (${airVal}°C):</strong> AccuWeather reports <i>2-meter shaded air temperature</i>. Landsat 8/9 satellite thermal radiometers measure the literal <i>radiometric surface skin</i> of asphalt & concrete roofs absorbing direct solar radiation (∼950 W/m²), which heats up <b>10°C–12°C hotter than ambient air</b>. Cool roofs block this surface heating directly!`;
    }
  }

  if (currentTimelineData) {
    renderTemperatureTimelineView(currentTimelineData);
  }
}

async function loadTemperatureTimeline(city, wardId) {
  try {
    const url = `/api/temperature-timeline?city=${encodeURIComponent(city)}${wardId ? `&cell_id=${encodeURIComponent(wardId)}` : ''}`;
    const res = await fetch(url);
    if (!res.ok) return;
    const data = await res.json();
    currentTimelineData = data;
    renderTemperatureTimelineView(data);
  } catch (err) {
    console.error("Failed to load temperature timeline", err);
  }
}

function renderTemperatureTimelineView(data) {
  if (!data) return;
  const isAirMode = currentTempSensorMode === "air";

  const exampleSurface = document.getElementById('example-surface-text');
  const exampleAmbient = document.getElementById('example-ambient-text');
  const peakVal = data.peak_high_c.toFixed(1);
  const airVal = (data.air_temp_high_c ?? (data.peak_high_c - 11.3)).toFixed(1);
  if (exampleSurface) {
    exampleSurface.textContent = `Bengaluru Surface Temperature: ~42.8°C (Current ${data.city}: ~${peakVal}°C)`;
  }
  if (exampleAmbient) {
    exampleAmbient.textContent = `Bengaluru Air Temperature: ~31.5°C (Current ${data.city}: ~${airVal}°C)`;
  }

  const areaBadge = document.getElementById('timeline-area-badge');
  if (areaBadge) areaBadge.textContent = data.ward_name ? `${data.ward_name} (${data.city})` : `${data.city} Metropolitan Average`;

  const hazardBadge = document.getElementById('timeline-hazard-badge');
  if (hazardBadge) {
    hazardBadge.textContent = isAirMode 
      ? `AccuWeather Baseline: ${airVal}°C`
      : `Hazardous Hours: ${data.heat_hazard_duration_hours}h/day`;
  }

  const peakEl = document.getElementById('timeline-peak-temp');
  if (peakEl) {
    const val = isAirMode ? (data.air_temp_high_c ?? (data.peak_high_c - 11.3)) : data.peak_high_c;
    peakEl.textContent = `${val.toFixed(1)} °C`;
  }

  const peakTimeEl = document.getElementById('timeline-peak-time');
  if (peakTimeEl) {
    peakTimeEl.textContent = isAirMode ? "14:00 (Shaded 2m Air Peak)" : `${data.peak_time} (Solar Skin Peak)`;
  }

  const lowEl = document.getElementById('timeline-low-temp');
  if (lowEl) {
    const val = isAirMode ? (data.air_temp_low_c ?? (data.low_temp_c - 4.7)) : data.low_temp_c;
    lowEl.textContent = `${val.toFixed(1)} °C`;
  }

  const lowTimeEl = document.getElementById('timeline-low-time');
  if (lowTimeEl) {
    lowTimeEl.textContent = isAirMode ? "06:00 (Pre-Dawn Air Low)" : `${data.low_time} (Surface Skin Min)`;
  }

  const cooledEl = document.getElementById('timeline-cooled-temp');
  if (cooledEl) {
    if (isAirMode) {
      const airCooled = data.air_temp_cooled_c ?? ((data.air_temp_high_c ?? 31.5) - (data.cooling_delta_c * 0.45));
      cooledEl.textContent = `${airCooled.toFixed(1)} °C`;
    } else {
      const cooledPeak = data.cooled_temp_c[data.diurnal_hours.indexOf("14:00")] || (data.peak_high_c - data.cooling_delta_c);
      cooledEl.textContent = `${cooledPeak.toFixed(1)} °C`;
    }
  }

  const dropEl = document.getElementById('timeline-mitigation-drop');
  if (dropEl) {
    const drop = isAirMode ? (data.cooling_delta_c * 0.45) : data.cooling_delta_c;
    dropEl.textContent = `-${drop.toFixed(1)} °C Mitigation Drop`;
  }

  const alertEl = document.getElementById('timeline-alert-level');
  if (alertEl) {
    const activeAlert = data.forecast_7days[0]?.alert_level || "Normal";
    alertEl.textContent = activeAlert;
    if (activeAlert.includes("Red")) alertEl.className = "kpi-value red";
    else if (activeAlert.includes("Orange")) alertEl.className = "kpi-value orange";
    else if (activeAlert.includes("Yellow")) alertEl.className = "kpi-value yellow";
    else alertEl.className = "kpi-value emerald";
  }

  renderDiurnalChart(data);
  renderForecastCards(data.forecast_7days, isAirMode, data.lst_vs_air_delta_c || 11.3);
}

function renderDiurnalChart(data) {
  const canvas = document.getElementById('diurnal-chart');
  if (!canvas || typeof Chart === 'undefined') return;

  if (diurnalChartInstance) {
    diurnalChartInstance.destroy();
  }

  const isAirMode = currentTempSensorMode === "air";
  const delta = data.lst_vs_air_delta_c || 11.3;

  const baselineData = isAirMode 
    ? (data.air_baseline_temp_c || data.baseline_temp_c.map(v => Number((v - delta).toFixed(1))))
    : data.baseline_temp_c;

  const cooledData = isAirMode 
    ? (data.air_cooled_temp_c || data.cooled_temp_c.map(v => Number((v - (delta * 0.85)).toFixed(1))))
    : data.cooled_temp_c;

  const baselineLabel = isAirMode ? 'Ambient Shaded Air Temp (°C)' : 'Baseline Surface LST (°C)';
  const cooledLabel = isAirMode ? 'Air Temp with Avani Interventions (°C)' : 'Surface LST with Avani Albedo (°C)';
  const baselineColor = isAirMode ? '#38bdf8' : '#f43f5e';
  const baselineBg = isAirMode ? 'rgba(56, 189, 248, 0.12)' : 'rgba(244, 63, 94, 0.12)';

  const ctx = canvas.getContext('2d');
  diurnalChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.diurnal_hours,
      datasets: [
        {
          label: baselineLabel,
          data: baselineData,
          borderColor: baselineColor,
          backgroundColor: baselineBg,
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          pointBackgroundColor: baselineColor,
          pointRadius: 4,
          pointHoverRadius: 6
        },
        {
          label: cooledLabel,
          data: cooledData,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.12)',
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          pointBackgroundColor: '#10b981',
          pointRadius: 4,
          pointHoverRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          titleColor: '#38bdf8',
          bodyColor: '#f8fafc',
          borderColor: '#334155',
          borderWidth: 1,
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw}°C`
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#94a3b8', font: { size: 10 } }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: {
            color: '#94a3b8',
            font: { size: 10 },
            callback: (v) => `${v}°C`
          }
        }
      }
    }
  });
}

function renderForecastCards(forecast, isAirMode = false, deltaC = 11.3) {
  const container = document.getElementById('forecast-cards-container');
  if (!container || !forecast) return;

  const airOffset = isAirMode ? deltaC : 0;
  const lowAirOffset = isAirMode ? (deltaC * 0.4) : 0;

  container.innerHTML = forecast.map(f => {
    let badgeColor = '#10b981';
    let badgeBg = 'rgba(16, 185, 129, 0.15)';
    if (f.alert_level.includes('Red')) {
      badgeColor = '#ef4444';
      badgeBg = 'rgba(239, 68, 68, 0.2)';
    } else if (f.alert_level.includes('Orange')) {
      badgeColor = '#f97316';
      badgeBg = 'rgba(249, 115, 22, 0.2)';
    } else if (f.alert_level.includes('Yellow')) {
      badgeColor = '#eab308';
      badgeBg = 'rgba(234, 179, 8, 0.2)';
    }

    const dispHigh = Number((f.high_c - airOffset).toFixed(1));
    const dispLow = Number((f.low_c - lowAirOffset).toFixed(1));
    const dispMitigated = Number((f.mitigated_high_c - airOffset).toFixed(1));
    const coolingDrop = Number((dispHigh - dispMitigated).toFixed(1));

    return `
      <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid var(--border-color); border-radius: 6px; padding: 6px 4px; text-align: center;">
        <div style="font-size: 11px; font-weight: 700; color: #f8fafc;">${f.day}</div>
        <div style="font-size: 9px; color: var(--text-dim); margin-bottom: 4px;">${f.date}</div>
        <div style="font-size: 14px; font-weight: 800; color: ${isAirMode ? '#38bdf8' : '#f43f5e'};">${dispHigh}°</div>
        <div style="font-size: 11px; color: #64748b;">${dispLow}°</div>
        <div style="font-size: 11px; font-weight: 700; color: #10b981; margin-top: 2px;">-${coolingDrop > 0 ? coolingDrop : 1.2}° ❄️</div>
        <div style="margin-top: 4px; display: inline-block; font-size: 8px; font-weight: 700; color: ${badgeColor}; background: ${badgeBg}; padding: 1px 4px; border-radius: 3px;">
          ${f.alert_level.replace('Alert', '').trim()}
        </div>
      </div>
    `;
  }).join('');
}

let isComparisonLoading = false;

async function runComparison() {
  if (isComparisonLoading) return;
  isComparisonLoading = true;

  const grid = document.getElementById('comparison-grid');
  if (grid && (!grid.children.length || grid.querySelector('.loading-state'))) {
    grid.innerHTML = `
      <div class="loading-state" style="grid-column: 1 / -1; text-align: center; padding: 40px 20px; color: #94a3b8;">
        <div class="btn-spinner" style="display: inline-block; width: 26px; height: 26px; border: 3px solid rgba(56,189,248,0.2); border-top-color: #38bdf8; border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 12px;"></div>
        <div style="font-size: 13px; font-weight: 600; color: #e2e8f0;">Computing Pareto-optimal scenario matrix for ${currentSelectedCity}...</div>
        <div style="font-size: 11.5px; color: #64748b; margin-top: 4px;">Evaluating 4 Mixed-Integer Linear Programming models (Google OR-Tools SCIP)</div>
      </div>
    `;
  }

  try {
    const res = await fetch(`/api/scenarios/compare?budget_inr=${currentBudgetInr}&city=${encodeURIComponent(currentSelectedCity)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderComparisonGrid(data.scenarios);
  } catch (err) {
    console.error("Error fetching comparison:", err);
    if (grid) {
      grid.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 30px; color: #f87171;">
          ⚠️ Failed to compute scenario comparison. <button onclick="runComparison()" style="background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff; padding: 4px 8px; border-radius: 4px; margin-left: 8px; cursor: pointer;">Retry</button>
        </div>
      `;
    }
  } finally {
    isComparisonLoading = false;
  }
}

// ================= MAP RENDERING =================
function getHviColor(score) {
  if (score >= 85) return '#dc2626'; // Critical
  if (score >= 70) return '#ea580c'; // Severe
  if (score >= 50) return '#d97706'; // High
  if (score >= 30) return '#ca8a04'; // Moderate
  return '#16a34a';                  // Low
}

function renderMapPolygons() {
  heatPolygonGroup.clearLayers();
  assetsMarkerGroup.clearLayers();

  climateCells.forEach(cell => {
    const color = getHviColor(cell.hvi_score);
    
    // Draw polygon
    const polygon = L.polygon(cell.boundary, {
      color: color,
      weight: 2,
      opacity: 0.85,
      fillColor: color,
      fillOpacity: 0.45
    }).addTo(heatPolygonGroup);

    // Click handler & Leaflet popup on polygon
    polygon.bindPopup(`
      <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: #0f172a; min-width: 180px;">
        <strong style="color: #0369a1; font-size: 13px; display: block; margin-bottom: 4px;">${cell.name}</strong>
        <div><b>Zone:</b> ${cell.zone}</div>
        <div><b>HVI:</b> <span style="color: ${color}; font-weight: 700;">${cell.hvi_score} (${cell.hvi_category})</span></div>
        <div><b>LST Temp:</b> ${cell.lst}°C (<span style="color: #e11d48;">+${cell.heat_anomaly}°C</span>)</div>
        <div><b>Vegetation (NDVI):</b> ${cell.ndvi}</div>
        <div><b>Population:</b> ${cell.population.toLocaleString()}</div>
        <button style="margin-top: 8px; width: 100%; padding: 5px 8px; background: #0284c7; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 11px;" onclick="openCellInspectorById('${cell.cell_id}')">🔍 Open Detailed Inspector</button>
      </div>
    `);
    polygon.on('click', () => openCellInspector(cell));

    // Centered label marker with click handler
    const centerIcon = L.divIcon({
      className: 'map-ward-label',
      html: `<div style="background: rgba(10,14,26,0.92); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; border: 1px solid ${color}; white-space: nowrap; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.4);">
               ${cell.name} (${cell.hvi_score})
             </div>`,
      iconSize: [120, 20],
      iconAnchor: [60, 10]
    });
    const labelMarker = L.marker([cell.center_lat, cell.center_lng], { icon: centerIcon }).addTo(heatPolygonGroup);
    labelMarker.on('click', () => openCellInspector(cell));

    // Critical Infrastructure Markers
    if (cell.assets.hospitals > 0 || cell.assets.schools > 0) {
      const assetIcon = L.divIcon({
        className: 'asset-marker-icon',
        html: `<div style="background: rgba(245, 158, 11, 0.9); width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; box-shadow: 0 0 8px rgba(245, 158, 11, 0.6); cursor: pointer;">🏥</div>`,
        iconSize: [22, 22],
        iconAnchor: [11, 11]
      });
      const infraMarker = L.marker([cell.center_lat - 0.004, cell.center_lng + 0.004], { icon: assetIcon })
        .bindTooltip(`<b>${cell.name} Infrastructure</b><br>🏥 Hospitals: ${cell.assets.hospitals}<br>🏫 Schools: ${cell.assets.schools}<br>🚉 Transit: ${cell.assets.transit_stops}`)
        .addTo(assetsMarkerGroup);
      infraMarker.on('click', () => openCellInspector(cell));
    }
  });
}

// Global helper for popup button
window.openCellInspectorById = function(id) {
  const c = climateCells.find(x => x.cell_id === id);
  if (c) openCellInspector(c);
};

function renderInterventionMarkers(scenario) {
  interventionMarkerGroup.clearLayers();
  if (!scenario || !scenario.allocations) return;

  const cellMap = {};
  climateCells.forEach(c => cellMap[c.cell_id] = c);

  scenario.allocations.forEach(alloc => {
    const c = cellMap[alloc.cell_id];
    if (!c) return;

    if (alloc.trees > 0 || alloc.cool_roof_sqft > 0 || alloc.shade_structures > 0 || alloc.hydration_stations > 0) {
      const markerHtml = `
        <div style="background: rgba(16, 185, 129, 0.95); border: 1px solid #34d399; color: #000; padding: 2px 6px; border-radius: 12px; font-size: 10px; font-weight: 700; display: flex; gap: 4px; box-shadow: 0 0 10px rgba(16, 185, 129, 0.6);">
          ${alloc.trees > 0 ? `<span>🌳${alloc.trees}</span>` : ''}
          ${alloc.cool_roof_sqft > 0 ? `<span>🏢${Math.round(alloc.cool_roof_sqft/1000)}k</span>` : ''}
          ${alloc.shade_structures > 0 ? `<span>☂️${alloc.shade_structures}</span>` : ''}
          ${alloc.hydration_stations > 0 ? `<span>💧${alloc.hydration_stations}</span>` : ''}
        </div>
      `;
      const icon = L.divIcon({
        className: 'intervention-badge',
        html: markerHtml,
        iconSize: [110, 20],
        iconAnchor: [55, 25]
      });

      L.marker([c.center_lat + 0.005, c.center_lng], { icon: icon })
        .bindTooltip(`
          <b>${alloc.cell_name} Plan</b><br>
          🌳 Trees: ${alloc.trees}<br>
          🏢 Cool Roof: ${alloc.cool_roof_sqft.toLocaleString()} sq ft<br>
          ☂️ Shades: ${alloc.shade_structures}<br>
          💧 Hydration: ${alloc.hydration_stations}<br>
          ❄️ Cooling: -${alloc.cooling_reduction_c}°C<br>
          💰 Cost: ${formatCurrency(alloc.total_cost)}
        `)
        .addTo(interventionMarkerGroup);
    }
  });
}

function openCellInspector(cell) {
  const inspector = document.getElementById('cell-inspector');
  const title = document.getElementById('inspector-title');
  const content = document.getElementById('inspector-content');

  title.textContent = `${cell.name} (${cell.zone} Zone)`;
  
  // Find current allocation if available
  let allocHtml = "";
  if (currentScenarioResult) {
    const alloc = currentScenarioResult.allocations.find(a => a.cell_id === cell.cell_id);
    if (alloc) {
      allocHtml = `
        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border-color);">
          <strong style="color: var(--color-cyan); font-size: 11px; text-transform: uppercase;">Allocated Interventions</strong>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; font-size: 11px; margin-top: 4px;">
            <div>🌳 Trees: <b>${alloc.trees}</b></div>
            <div>🏢 Cool Roof: <b>${(alloc.cool_roof_sqft/1000).toFixed(0)}k sqft</b></div>
            <div>☂️ Shades: <b>${alloc.shade_structures}</b></div>
            <div>💧 Hydration: <b>${alloc.hydration_stations}</b></div>
          </div>
          <div style="margin-top: 6px; font-size: 11px;">
            Target Cooling: <b style="color: #38bdf8;">-${alloc.cooling_reduction_c}°C</b> | Budget: <b>${formatCurrency(alloc.total_cost)}</b>
          </div>
        </div>
      `;
    }
  }

  content.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
      <span style="font-size: 12px; color: var(--text-muted);">Heat Vulnerability Index:</span>
      <span style="background: ${getHviColor(cell.hvi_score)}; color: #fff; padding: 2px 8px; border-radius: 4px; font-weight: 700; font-size: 12px;">
        ${cell.hvi_score} (${cell.hvi_category})
      </span>
    </div>
    <div style="background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 6px 8px; margin-bottom: 8px;">
      <div style="font-size: 10px; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px; display: flex; justify-content: space-between;">
        <span>🌡️ Dual Temperature Readings</span>
        <span style="color: #cbd5e1; font-weight: 600;">Δ +11.3°C Surface Mass Gap</span>
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 11px;">
        <div style="background: rgba(244, 63, 94, 0.1); border-left: 2px solid #f43f5e; padding: 4px 6px; border-radius: 3px;">
          <div style="font-size: 9.5px; color: #f43f5e; font-weight: 700;">🛰️ Surface Temp (LST)</div>
          <div style="font-size: 13px; font-weight: 700; color: #f87171;">${cell.lst}°C <span style="font-size: 10px; color: #f43f5e;">(+${cell.heat_anomaly}°C)</span></div>
          <div style="font-size: 9px; color: #94a3b8;">Landsat 8/9 TIRS & GEE</div>
        </div>
        <div style="background: rgba(56, 189, 248, 0.1); border-left: 2px solid #38bdf8; padding: 4px 6px; border-radius: 3px;">
          <div style="font-size: 9.5px; color: #38bdf8; font-weight: 700;">🌤️ Ambient Air Temp</div>
          <div style="font-size: 13px; font-weight: 700; color: #38bdf8;">${(cell.lst - 11.3).toFixed(1)}°C</div>
          <div style="font-size: 9px; color: #94a3b8;">Weather APIs (AccuWeather/IMD)</div>
        </div>
      </div>
    </div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 11px;">
      <div>Vegetation (NDVI): <b>${cell.ndvi}</b></div>
      <div>Built Index (NDBI): <b>${cell.ndbi}</b></div>
      <div>Albedo Reflectance: <b>${cell.albedo}</b></div>
      <div>Built Density: <b>${Math.round(cell.built_density * 100)}%</b></div>
      <div>Population: <b>${cell.population.toLocaleString()}</b></div>
      <div>Days > 38°C: <b>${cell.heat_persistence_days} days</b></div>
    </div>
    <div style="margin-top: 8px; font-size: 11px; color: var(--text-dim);">
      Critical Assets: 🏫 ${cell.assets.schools} Schools • 🏥 ${cell.assets.hospitals} Hospitals • 🚉 ${cell.assets.transit_stops} Transit
    </div>
    
    <!-- Physical Land Feasibility Audit -->
    <div class="land-feasibility-box">
      <div class="land-feasibility-title">
        <span>🌱 Physical Land Feasibility</span>
        <span class="${cell.built_density >= 0.88 ? 'feasibility-tag constrained' : 'feasibility-tag'}">
          ${cell.built_density >= 0.88 ? '⚠️ Soil Capped' : '✅ Verified Viable'}
        </span>
      </div>
      <div class="land-metrics-row">
        <span>Permeable Soil: <b>${cell.permeable_land_sqm ? Math.round(cell.permeable_land_sqm).toLocaleString() : '28,000'} m²</b></span>
        <span>Tree Capacity: <b>${cell.tree_carrying_capacity ? cell.tree_carrying_capacity.toLocaleString() : '1,500'} max</b></span>
      </div>
      <p class="land-note-text">
        ${cell.land_feasibility_note || (cell.built_density >= 0.88 
          ? `High built density (${Math.round(cell.built_density*100)}%). Ground soil capped; excess cooling routed to Cool Roofs (0 m² soil).` 
          : `Viable soil footprint for native trees along medians, schoolyards & park setbacks.`)}
      </p>
    </div>

    ${allocHtml}
  `;

  inspector.classList.remove('hidden');

  // Update Hazard Badge and Micro-Chart in Inspector
  const hazardEl = document.getElementById('ward-hazard-hours');
  if (hazardEl) {
    hazardEl.textContent = `${cell.heat_persistence_days > 60 ? '8.5h' : '6.0h'} > 38°C peak hazard`;
  }
  renderWardMicroChart(cell);

  // Sync Ward Precision dropdown
  const wardSelect = document.getElementById('ward-select');
  if (wardSelect) {
    wardSelect.value = cell.cell_id;
  }
  selectedWardId = cell.cell_id;
  loadSpotPhaseEvaluation(currentSelectedCity, cell.cell_id);
}

function renderWardMicroChart(cell) {
  const canvas = document.getElementById('ward-micro-chart');
  if (!canvas || typeof Chart === 'undefined') return;

  if (wardMicroChartInstance) {
    wardMicroChartInstance.destroy();
  }

  const hours = ["00:00", "06:00", "12:00", "14:00", "18:00", "21:00"];
  const baseMin = cell.lst - 17.5;
  const baseline = [
    Math.round((baseMin + (cell.lst - baseMin) * 0.22) * 10) / 10,
    Math.round(baseMin * 10) / 10,
    Math.round((baseMin + (cell.lst - baseMin) * 0.88) * 10) / 10,
    cell.lst,
    Math.round((baseMin + (cell.lst - baseMin) * 0.65) * 10) / 10,
    Math.round((baseMin + (cell.lst - baseMin) * 0.38) * 10) / 10
  ];
  const cooled = baseline.map((v, i) => Math.round((v - (i === 3 ? 2.8 : 1.6)) * 10) / 10);

  const ctx = canvas.getContext('2d');
  wardMicroChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: hours,
      datasets: [
        {
          label: 'Baseline (°C)',
          data: baseline,
          borderColor: '#f43f5e',
          borderWidth: 2,
          pointRadius: 2,
          tension: 0.3
        },
        {
          label: 'Cooled (°C)',
          data: cooled,
          borderColor: '#10b981',
          borderWidth: 2,
          pointRadius: 2,
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          titleColor: '#38bdf8',
          bodyColor: '#f8fafc',
          callbacks: {
            label: (c) => ` ${c.dataset.label}: ${c.raw}°C`
          }
        }
      },
      scales: {
        x: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { display: false } },
        y: { ticks: { color: '#64748b', font: { size: 9 } }, grid: { color: 'rgba(255,255,255,0.05)' } }
      }
    }
  });
}

// ================= RESULTS RENDERING =================
function updateKpiCards(scenario) {
  document.getElementById('kpi-cooling').textContent = `-${scenario.avg_temp_reduction_c.toFixed(2)} °C`;
  document.getElementById('kpi-max-cooling').textContent = `Peak: -${scenario.max_temp_reduction_c.toFixed(2)} °C in Hotspots`;
  document.getElementById('kpi-beneficiaries').textContent = scenario.total_beneficiaries.toLocaleString();
  document.getElementById('kpi-budget').textContent = formatCurrency(scenario.budget_spent_inr);
  
  const pct = ((scenario.budget_spent_inr / scenario.total_budget_inr) * 100).toFixed(1);
  document.getElementById('kpi-budget-pct').textContent = `${pct}% of ${formatCurrency(scenario.total_budget_inr)} target`;
  document.getElementById('kpi-exposure').textContent = `${scenario.heat_exposure_reduction_pct.toFixed(1)}%`;
}

function renderActionPlan(plan) {
  document.getElementById('plan-model-badge').textContent = plan.llm_model;
  document.getElementById('plan-solver-badge').textContent = `OR-Tools SCIP • ${plan.scenario_result.computation_time_ms}ms`;
  document.getElementById('plan-title').textContent = plan.scenario_result.scenario_title;
  document.getElementById('plan-exec-summary').textContent = plan.executive_summary;
  document.getElementById('plan-rationale').textContent = plan.rationale;

  // Persona Badge & AI Strategic Recommendations
  const personaBadge = document.getElementById('plan-persona-badge');
  if (personaBadge) personaBadge.textContent = plan.persona || selectedPersona;

  const recContainer = document.getElementById('plan-recommendations-container');
  if (recContainer && plan.strategic_recommendations && plan.strategic_recommendations.length > 0) {
    recContainer.innerHTML = plan.strategic_recommendations.map(r => `
      <li style="margin-bottom: 6px;">${r}</li>
    `).join('');
  }

  // Load and update temperature timeline
  loadTemperatureTimeline(currentSelectedCity, selectedWardId);

  // Ward priorities
  const priorityContainer = document.getElementById('ward-priority-container');
  priorityContainer.innerHTML = plan.ward_priorities.map(wp => `
    <div class="ward-priority-card">
      <div class="ward-priority-title">
        <span>#${wp.rank} ${wp.cell_name}</span>
        <span style="color: ${getHviColor(wp.hvi_score)};">HVI ${wp.hvi_score}</span>
      </div>
      <div class="ward-priority-tags">
        ${wp.primary_interventions.map(i => `<span class="tag-pill">${i}</span>`).join('')}
      </div>
      <p style="color: var(--text-muted); line-height: 1.4;">${wp.justification}</p>
    </div>
  `).join('');

  // Implementation phases - Guaranteed non-zero spend distribution with Multi-Currency
  const timelineContainer = document.getElementById('timeline-container');
  const totalSpentInr = (plan.scenario_result && plan.scenario_result.budget_spent_inr > 0)
    ? plan.scenario_result.budget_spent_inr
    : currentBudgetInr;
  const fallbackSpendsInr = [totalSpentInr * 0.22, totalSpentInr * 0.48, totalSpentInr * 0.30];

  timelineContainer.innerHTML = (plan.implementation_phases || []).map((p, idx) => {
    let spendInr = (p.estimated_spend_inr > 0) ? p.estimated_spend_inr : fallbackSpendsInr[idx % 3];
    if (spendInr <= 0 || isNaN(spendInr)) spendInr = fallbackSpendsInr[idx % 3];
    return `
      <div class="phase-card">
        <div class="phase-title">${p.phase}</div>
        <div class="phase-time">⏱️ ${p.timeline} • Estimated Spend: <b>${formatCurrency(spendInr)}</b></div>
        <ul class="phase-milestones">
          ${p.key_milestones.map(m => `<li>${m}</li>`).join('')}
        </ul>
      </div>
    `;
  }).join('');

  // Physical Land Feasibility Summary
  if (plan.land_feasibility_summary) {
    const lfsEl = document.getElementById('plan-land-feasibility-summary');
    if (lfsEl) lfsEl.textContent = plan.land_feasibility_summary;
  }

  // Spot-Specific Phase Comparison & Suitability Evaluator
  if (plan.spot_phase_evaluation) {
    renderSpotPhaseComparison(plan.spot_phase_evaluation);
  } else {
    loadSpotPhaseEvaluation(currentSelectedCity, selectedWardId);
  }

  // 12-Month Heat Calendar & Precaution Window
  if (plan.heat_calendar) {
    renderHeatCalendar(plan.heat_calendar);
  } else {
    loadHeatCalendar(currentSelectedCity);
  }

  // Co-benefits
  const coBenefitsContainer = document.getElementById('co-benefits-container');
  coBenefitsContainer.innerHTML = plan.co_benefits.map(cb => `<li>${cb}</li>`).join('');
}

function renderAllocationsTable(scenario) {
  const totalsBar = document.getElementById('totals-bar');
  totalsBar.innerHTML = `
    <span>🌳 Trees: <b>${scenario.total_trees.toLocaleString()}</b></span>
    <span>🏢 Cool Roofs: <b>${(scenario.total_cool_roof_sqft).toLocaleString()} sq ft</b></span>
    <span>☂️ Shades: <b>${scenario.total_shades}</b></span>
    <span>💧 Hydration: <b>${scenario.total_hydration}</b></span>
    <span>💰 Total Spend: <b>${formatCurrency(scenario.budget_spent_inr)}</b></span>
  `;

  const tbody = document.getElementById('allocations-table-body');
  tbody.innerHTML = scenario.allocations.map(a => `
    <tr>
      <td><b>${a.cell_name}</b></td>
      <td><span style="color: ${getHviColor(a.hvi_score)}; font-weight: 600;">${a.hvi_score}</span></td>
      <td>${a.trees > 0 ? a.trees : '-'}</td>
      <td>${a.cool_roof_sqft > 0 ? (a.cool_roof_sqft/1000).toFixed(0) + 'k sqft' : '-'}</td>
      <td>${a.shade_structures > 0 ? a.shade_structures : '-'}</td>
      <td>${a.hydration_stations > 0 ? a.hydration_stations : '-'}</td>
      <td style="color: #38bdf8; font-weight: 600;">-${a.cooling_reduction_c}°C</td>
      <td><b>${formatCurrency(a.total_cost)}</b></td>
    </tr>
  `).join('');
}

function renderComparisonGrid(scenarios) {
  const grid = document.getElementById('comparison-grid');
  if (!grid || !scenarios) return;

  grid.innerHTML = Object.entries(scenarios).map(([key, s]) => {
    const isSelected = key === selectedScenario;
    return `
      <div class="comp-card ${isSelected ? 'highlight' : ''}" data-key="${key}" title="Click to select and apply this scenario">
        <div class="comp-header">
          <span>${s.title}</span>
          <span style="color: #38bdf8; font-family: var(--font-mono); font-weight: 700;">-${s.avg_temp_reduction_c}°C</span>
        </div>
        <div class="comp-metrics">
          <div class="comp-metric-item">
            <small>Beneficiaries</small>
            <strong>${s.total_beneficiaries.toLocaleString()}</strong>
          </div>
          <div class="comp-metric-item">
            <small>Budget Used</small>
            <strong>${formatCurrency(s.budget_spent_inr || (s.budget_spent_lakhs * 100000))}</strong>
          </div>
          <div class="comp-metric-item">
            <small>Exposure Drop</small>
            <strong style="color: #34d399;">${s.heat_exposure_reduction_pct}%</strong>
          </div>
          <div class="comp-metric-item">
            <small>Trees</small>
            <strong>${s.trees.toLocaleString()}</strong>
          </div>
          <div class="comp-metric-item">
            <small>Cool Roofs</small>
            <strong>${(s.cool_roof_sqft/1000).toFixed(0)}k sqft</strong>
          </div>
          <div class="comp-metric-item">
            <small>Shade + Water</small>
            <strong>${s.shades + s.hydration} sites</strong>
          </div>
        </div>
        <div class="comp-card-footer" style="margin-top: 10px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 8px;">
          <span class="comp-status-badge" style="font-size: 11px;">
            ${isSelected 
              ? '<span style="color: #34d399; font-weight: 700;">● Active Scenario</span>' 
              : '<span style="color: #94a3b8;">Click to select</span>'}
          </span>
          <button type="button" class="select-scenario-btn" data-key="${key}" style="background: ${isSelected ? 'rgba(52, 211, 153, 0.2)' : 'rgba(56, 189, 248, 0.15)'}; border: 1px solid ${isSelected ? '#34d399' : 'rgba(56, 189, 248, 0.4)'}; color: ${isSelected ? '#34d399' : '#38bdf8'}; font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s ease;">
            ${isSelected ? '✓ Loaded' : '👉 Select & Load'}
          </button>
        </div>
      </div>
    `;
  }).join('');

  grid.querySelectorAll('.comp-card').forEach(card => {
    card.addEventListener('click', () => {
      const scenarioKey = card.dataset.key;
      if (scenarioKey) {
        selectAndLoadScenario(scenarioKey);
      }
    });
  });
}

function exportPlanJson() {
  if (!currentActionPlan) return;
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentActionPlan, null, 2));
  const downloadAnchor = document.createElement('a');
  downloadAnchor.setAttribute("href", dataStr);
  downloadAnchor.setAttribute("download", `avani_albedo_climate_plan_${Date.now()}.json`);
  document.body.appendChild(downloadAnchor);
  downloadAnchor.click();
  downloadAnchor.remove();
}

// ================= HISTORICAL GOOGLE EARTH TIMELAPSE ENGINE (2014 - 2026) =================
let timelapseData = null;
let isTimelapsePlaying = false;
let timelapseTimer = null;
let currentTimelapseYearIndex = 4; // Default to 2026 (current baseline)

async function loadTimelapseData(cityName = currentSelectedCity) {
  try {
    const res = await fetch(`/api/history/timelapse?city=${encodeURIComponent(cityName)}`);
    if (!res.ok) return;
    timelapseData = await res.json();
    
    // Set slider range & default position
    const slider = document.getElementById('timelapse-year-slider');
    if (slider && timelapseData.records) {
      slider.max = timelapseData.records.length - 1;
      slider.value = currentTimelapseYearIndex;
    }
    renderTimelapseYear(currentTimelapseYearIndex);
  } catch (err) {
    console.error("Error loading timelapse data:", err);
  }
}

function renderTimelapseYear(index) {
  if (!timelapseData || !timelapseData.records || !timelapseData.records[index]) return;
  const rec = timelapseData.records[index];

  // Update tick marks
  document.querySelectorAll('.year-tick').forEach((tick, idx) => {
    if (idx === index) tick.classList.add('active');
    else tick.classList.remove('active');
  });

  // Update telemetry stats
  const statLst = document.getElementById('tl-stat-lst');
  if (statLst) statLst.textContent = `${rec.avg_lst_c} °C`;

  const statAnomaly = document.getElementById('tl-stat-anomaly');
  if (statAnomaly) statAnomaly.textContent = `+${rec.heat_anomaly_c}°C anomaly`;

  const statTrees = document.getElementById('tl-stat-trees');
  if (statTrees) statTrees.textContent = `-${rec.trees_lost_cumulative.toLocaleString()}`;

  const statBuilt = document.getElementById('tl-stat-built');
  if (statBuilt) statBuilt.textContent = `${Math.round(rec.built_up_fraction * 100)}%`;

  const statNdvi = document.getElementById('tl-stat-ndvi');
  if (statNdvi) statNdvi.textContent = `NDVI: ${rec.ndvi}`;

  const statSensor = document.getElementById('tl-stat-sensor');
  if (statSensor) statSensor.textContent = rec.satellite_sensor;

  const statDate = document.getElementById('tl-stat-date');
  if (statDate) statDate.textContent = `Obs: ${rec.observation_date}`;

  const statRestoration = document.getElementById('tl-stat-restoration');
  if (statRestoration) {
    statRestoration.textContent = `${timelapseData.restoration_target_trees.toLocaleString()} native trees + ${timelapseData.restoration_cool_roof_sqft.toLocaleString()} sq ft zero-soil cool roofs`;
  }

  // Visual Heat Anomaly Overlay update across Leaflet polygons
  updateMapPolygonsForTimelapse(index);
}

function updateMapPolygonsForTimelapse(yearIndex) {
  if (!timelapseData || !timelapseData.records || !timelapseData.records[yearIndex]) return;
  const factor = yearIndex / (timelapseData.records.length - 1); // 0.0 in 2014, 1.0 in 2026

  heatPolygonGroup.eachLayer(layer => {
    if (layer instanceof L.Polygon) {
      // Dynamic decadal color shift from cooler green/gold to intense red/crimson
      let fillColor;
      if (factor < 0.25) {
        fillColor = '#16a34a'; // Green baseline
      } else if (factor < 0.50) {
        fillColor = '#ca8a04'; // Warm yellow
      } else if (factor < 0.75) {
        fillColor = '#ea580c'; // Hot orange
      } else {
        fillColor = '#dc2626'; // Peak severe heat
      }
      layer.setStyle({
        color: fillColor,
        fillColor: fillColor,
        fillOpacity: 0.35 + (factor * 0.22)
      });
    }
  });
}

function toggleTimelapsePlay() {
  if (!timelapseData || !timelapseData.records) return;
  const playIcon = document.getElementById('timelapse-play-icon');
  const playText = document.getElementById('timelapse-play-text');

  if (isTimelapsePlaying) {
    // Pause
    isTimelapsePlaying = false;
    clearInterval(timelapseTimer);
    timelapseTimer = null;
    if (playIcon) playIcon.textContent = '▶';
    if (playText) playText.textContent = 'Play';
  } else {
    // Play
    isTimelapsePlaying = true;
    if (playIcon) playIcon.textContent = '⏸';
    if (playText) playText.textContent = 'Pause';

    timelapseTimer = setInterval(() => {
      currentTimelapseYearIndex = (currentTimelapseYearIndex + 1) % timelapseData.records.length;
      const slider = document.getElementById('timelapse-year-slider');
      if (slider) slider.value = currentTimelapseYearIndex;
      renderTimelapseYear(currentTimelapseYearIndex);
    }, 1500);
  }
}

function bindTimelapseTicks() {
  document.querySelectorAll('.year-tick').forEach(tick => {
    tick.addEventListener('click', () => {
      const idx = parseInt(tick.dataset.idx);
      currentTimelapseYearIndex = idx;
      const tlSlider = document.getElementById('timelapse-year-slider');
      if (tlSlider) tlSlider.value = idx;
      renderTimelapseYear(idx);
    });
  });
}

let currentTimelapseMode = "12yr";

async function switchTimelapseMode(mode) {
  currentTimelapseMode = mode;
  const btn12 = document.getElementById('tl-mode-12yr');
  const btn20 = document.getElementById('tl-mode-20yr');
  const titleText = document.getElementById('timelapse-title-text');
  const labelsContainer = document.querySelector('.timelapse-year-labels');

  if (mode === "20yr") {
    if (btn12) { btn12.classList.remove('active'); btn12.style.background = 'transparent'; btn12.style.color = '#94a3b8'; }
    if (btn20) { btn20.classList.add('active'); btn20.style.background = 'var(--color-cyan)'; btn20.style.color = '#020617'; }
    if (titleText) titleText.textContent = "🌍 20-Year Satellite Archive (2005 – 2025)";

    if (labelsContainer) {
      labelsContainer.innerHTML = `
        <span class="year-tick" data-idx="0">2005</span>
        <span class="year-tick" data-idx="1">2010</span>
        <span class="year-tick" data-idx="2">2015</span>
        <span class="year-tick" data-idx="3">2020</span>
        <span class="year-tick active" data-idx="4">2025</span>
      `;
      bindTimelapseTicks();
    }
    await loadTwentyYearTimelapse(currentSelectedCity);
  } else {
    if (btn20) { btn20.classList.remove('active'); btn20.style.background = 'transparent'; btn20.style.color = '#94a3b8'; }
    if (btn12) { btn12.classList.add('active'); btn12.style.background = 'var(--color-cyan)'; btn12.style.color = '#020617'; }
    if (titleText) titleText.textContent = "🌍 Earth Observation Archive (2014 – 2026)";

    if (labelsContainer) {
      labelsContainer.innerHTML = `
        <span class="year-tick" data-idx="0">2014</span>
        <span class="year-tick" data-idx="1">2017</span>
        <span class="year-tick" data-idx="2">2020</span>
        <span class="year-tick" data-idx="3">2023</span>
        <span class="year-tick active" data-idx="4">2026</span>
      `;
      bindTimelapseTicks();
    }
    await loadTimelapseData(currentSelectedCity);
  }
}

async function loadTwentyYearTimelapse(cityName = currentSelectedCity) {
  try {
    const res = await fetch(`/api/history/20yr-archive?city=${encodeURIComponent(cityName)}`);
    if (!res.ok) return;
    const arch = await res.json();
    timelapseData = {
      city: arch.city,
      records: arch.records,
      restoration_target_trees: arch.total_trees_lost_20yr,
      restoration_cool_roof_sqft: 1800000
    };
    currentTimelapseYearIndex = 4;
    const slider = document.getElementById('timelapse-year-slider');
    if (slider) {
      slider.max = timelapseData.records.length - 1;
      slider.value = 4;
    }
    renderTimelapseYear(4);
  } catch (err) {
    console.error("Error loading 20yr archive:", err);
  }
}

// ================= SPOT-SPECIFIC PHASE EVALUATION =================
let cachedSpotEvaluation = null;

async function loadSpotPhaseEvaluation(cityName = currentSelectedCity, wardId = selectedWardId) {
  try {
    let url = `/api/phases/spot-evaluation?city=${encodeURIComponent(cityName)}&budget_inr=${currentBudgetInr}`;
    if (wardId && wardId !== 'ALL') {
      url += `&ward_id=${encodeURIComponent(wardId)}`;
    }
    const res = await fetch(url);
    if (!res.ok) return;
    const data = await res.json();
    cachedSpotEvaluation = data;
    renderSpotPhaseComparison(data);
  } catch (err) {
    console.error("Error loading spot evaluation:", err);
  }
}

function renderSpotPhaseComparison(evaluation) {
  if (!evaluation) return;
  cachedSpotEvaluation = evaluation;

  const wardBadge = document.getElementById('spot-eval-ward-badge');
  if (wardBadge) wardBadge.textContent = `${evaluation.ward_name} (${evaluation.ward_id})`;

  const lstEl = document.getElementById('spot-eval-lst');
  if (lstEl) lstEl.textContent = `${evaluation.peak_lst} °C`;

  const hviEl = document.getElementById('spot-eval-hvi');
  if (hviEl) hviEl.textContent = evaluation.hvi_score;

  const builtEl = document.getElementById('spot-eval-built');
  if (builtEl) builtEl.textContent = `${evaluation.built_density_pct}%`;

  const soilEl = document.getElementById('spot-eval-soil');
  if (soilEl) soilEl.textContent = `${evaluation.unbuilt_pct}%`;

  const titleEl = document.getElementById('spot-eval-best-phase-title');
  if (titleEl) titleEl.textContent = `${evaluation.recommended_phase_name} is Top Choice for This Spot`;

  const starsEl = document.getElementById('spot-eval-best-phase-stars');
  const bestPhase = (evaluation.phases || []).find(p => p.is_recommended_best) || (evaluation.phases && evaluation.phases[0]);
  if (starsEl && bestPhase) {
    starsEl.textContent = `${bestPhase.suitability_rating} (${bestPhase.suitability_score_pct}% Match)`;
  }

  const ratEl = document.getElementById('spot-eval-best-phase-rationale');
  if (ratEl) ratEl.textContent = evaluation.why_recommended;

  const grid = document.getElementById('spot-phases-grid');
  if (!grid || !evaluation.phases) return;

  grid.innerHTML = evaluation.phases.map(p => {
    const isBest = p.is_recommended_best;
    const borderStyle = isBest ? '2px solid #10b981' : '1px solid rgba(255,255,255,0.08)';
    const bgStyle = isBest ? 'rgba(16, 185, 129, 0.08)' : 'rgba(15, 23, 42, 0.6)';
    const tagBg = isBest ? 'background: #10b981; color: #020617;' : 'background: rgba(255,255,255,0.1); color: #cbd5e1;';
    
    return `
      <div class="spot-phase-card ${isBest ? 'active-best' : ''}" style="border: ${borderStyle}; background: ${bgStyle}; border-radius: 8px; padding: 10px; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.2s ease;">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
            <strong style="font-size: 11.5px; color: ${isBest ? '#34d399' : '#f8fafc'};">${p.phase_title}</strong>
            <span style="${tagBg} font-size: 9.5px; padding: 2px 5px; border-radius: 3px; font-weight: 700; white-space: nowrap;">
              ${isBest ? '⭐ BEST OPTION' : `${p.suitability_score_pct}%`}
            </span>
          </div>
          <div style="font-size: 10px; color: #94a3b8; margin-bottom: 6px;">
            ⏱️ <b>${p.speed}</b> • <span>${p.land_requirement}</span>
          </div>
          <div style="display: flex; gap: 4px; align-items: center; margin-bottom: 6px;">
            <span style="font-size: 10px; color: #38bdf8; font-weight: 700; background: rgba(56, 189, 248, 0.15); padding: 2px 6px; border-radius: 4px;">
              Projected Cool: -${p.cooling_impact_c}°C
            </span>
          </div>
          <ul style="padding-left: 1rem; margin: 0 0 6px 0; font-size: 10.5px; color: #cbd5e1; line-height: 1.4;">
            ${p.focus_interventions.map(fi => `<li>${fi}</li>`).join('')}
          </ul>
        </div>
        <p style="margin: 4px 0 0 0; font-size: 10px; color: #94a3b8; line-height: 1.35; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 4px;">
          ${p.rationale}
        </p>
      </div>
    `;
  }).join('');
}

// ================= 12-MONTH HEAT CALENDAR & PRECAUTION WINDOW =================
async function loadHeatCalendar(cityName = currentSelectedCity) {
  try {
    const res = await fetch(`/api/heat-calendar?city=${encodeURIComponent(cityName)}`);
    if (!res.ok) return;
    const calendar = await res.json();
    renderHeatCalendar(calendar);
  } catch (err) {
    console.error("Error loading heat calendar:", err);
  }
}

function renderHeatCalendar(calendar) {
  if (!calendar) return;

  const cityBadge = document.getElementById('calendar-city-badge');
  if (cityBadge) cityBadge.textContent = `${calendar.city} (${calendar.country})`;

  const peakEl = document.getElementById('cal-peak-window');
  if (peakEl) peakEl.textContent = calendar.peak_heatwave_window;

  const prepEl = document.getElementById('cal-prep-window');
  if (prepEl) prepEl.textContent = calendar.precaution_prep_window;

  const plantEl = document.getElementById('cal-plant-window');
  if (plantEl) plantEl.textContent = calendar.planting_window;

  // Render 12 months heatmap strip
  const monthsGrid = document.getElementById('calendar-months-grid');
  if (monthsGrid && calendar.months) {
    monthsGrid.innerHTML = calendar.months.map(m => {
      let bg = '#10b981'; // Green
      let textCol = '#ffffff';
      if (m.status.includes('Critical')) {
        bg = '#ef4444'; // Red
      } else if (m.status.includes('High')) {
        bg = '#f97316'; // Orange
      } else if (m.status.includes('Moderate')) {
        bg = '#eab308'; // Yellow
        textCol = '#020617';
      }
      return `
        <div style="background: ${bg}; color: ${textCol}; padding: 6px 2px; border-radius: 4px; text-align: center; font-size: 9.5px; font-weight: 700; display: flex; flex-direction: column; gap: 2px;" title="${m.month}: ${m.high_lst}°C - ${m.action_note}">
          <span>${m.month}</span>
          <span style="font-size: 9px; opacity: 0.95;">${m.high_lst}°</span>
        </div>
      `;
    }).join('');
  }

  // Render Advisories
  const advList = document.getElementById('calendar-advisories-list');
  if (advList && calendar.advisories) {
    advList.innerHTML = calendar.advisories.map(a => `
      <li style="margin-bottom: 4px;">${a}</li>
    `).join('');
  }
}

// ================= DELEGATED AI PROJECT COPILOT CONTROLLER =================
let copilotHistory = [];
let isCopilotWaiting = false;

function initCopilot() {
  const toggleBtn = document.getElementById('copilot-toggle-btn');
  const panel = document.getElementById('copilot-chat-panel');
  const closeBtn = document.getElementById('copilot-close-btn');
  const clearBtn = document.getElementById('copilot-clear-btn');
  const form = document.getElementById('copilot-form');
  const input = document.getElementById('copilot-input');
  const chipsContainer = document.getElementById('copilot-quick-chips');

  if (!toggleBtn || !panel) return;

  // Toggle Panel
  toggleBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const isHidden = panel.classList.contains('hidden');
    if (isHidden) {
      panel.classList.remove('hidden');
      if (input) input.focus();
    } else {
      panel.classList.add('hidden');
    }
  });

  // Close Panel
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      panel.classList.add('hidden');
    });
  }

  // Clear Chat
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      copilotHistory = [];
      const messagesContainer = document.getElementById('copilot-messages');
      if (messagesContainer) {
        messagesContainer.innerHTML = `
          <div class="copilot-msg bot-msg">
            <div class="copilot-msg-bubble">
              👋 <b>Hi! I'm the Avani Project Help Bot.</b><br>
              Chat history cleared. What would you like to know about our project?
            </div>
          </div>
        `;
      }
    });
  }

  // Quick Chips
  if (chipsContainer) {
    chipsContainer.addEventListener('click', (e) => {
      const chip = e.target.closest('.quick-chip');
      if (chip && chip.dataset.query) {
        sendCopilotMessage(chip.dataset.query);
      }
    });
  }

  // Form Submit
  if (form && input) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text || isCopilotWaiting) return;
      input.value = '';
      sendCopilotMessage(text);
    });
  }
}

async function sendCopilotMessage(userText) {
  const messagesContainer = document.getElementById('copilot-messages');
  if (!messagesContainer) return;

  // 1. Render User Message
  const userMsgEl = document.createElement('div');
  userMsgEl.className = 'copilot-msg user-msg';
  userMsgEl.innerHTML = `
    <div class="copilot-msg-bubble">${escapeHtml(userText)}</div>
  `;
  messagesContainer.appendChild(userMsgEl);

  // 2. Render Typing Indicator
  const typingEl = document.createElement('div');
  typingEl.className = 'copilot-msg bot-msg copilot-typing-msg';
  typingEl.innerHTML = `
    <div class="copilot-msg-bubble">
      <div class="copilot-typing">
        <span class="copilot-typing-dot"></span>
        <span class="copilot-typing-dot"></span>
        <span class="copilot-typing-dot"></span>
        <span style="font-size: 11px; color: #94a3b8; margin-left: 6px;">Consulting Avani Help Bot...</span>
      </div>
    </div>
  `;
  messagesContainer.appendChild(typingEl);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  isCopilotWaiting = true;

  try {
    const res = await fetch('/api/help-bot/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userText,
        city: currentSelectedCity || 'Bengaluru',
        history: copilotHistory
      })
    });

    const data = await res.json();
    typingEl.remove();

    if (data.status === 'success' && data.response) {
      // Save history
      copilotHistory.push({ role: 'user', content: userText });
      copilotHistory.push({ role: 'assistant', content: data.response });

      // Format markdown response
      const formattedHtml = formatCopilotMarkdown(data.response);

      const botMsgEl = document.createElement('div');
      botMsgEl.className = 'copilot-msg bot-msg';
      botMsgEl.innerHTML = `
        <div class="copilot-msg-bubble">${formattedHtml}</div>
        <div class="copilot-msg-meta">
          <span>⚡ ${data.model}</span>
          ${data.sources && data.sources.length ? `<span>• 📑 ${data.sources[0]}</span>` : ''}
        </div>
      `;
      messagesContainer.appendChild(botMsgEl);
    } else {
      throw new Error(data.detail || 'Could not get response');
    }
  } catch (err) {
    typingEl.remove();
    console.error('Copilot request error:', err);
    const errEl = document.createElement('div');
    errEl.className = 'copilot-msg bot-msg';
    errEl.innerHTML = `
      <div class="copilot-msg-bubble" style="border-left: 3px solid #ef4444;">
        ⚠️ Sorry, I encountered an issue retrieving the response. Please check that the server is reachable and try again.
      </div>
    `;
    messagesContainer.appendChild(errEl);
  } finally {
    isCopilotWaiting = false;
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
}

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}

function formatCopilotMarkdown(text) {
  if (!text) return '';
  let html = text;

  // Headers
  html = html.replace(/^### (.*$)/gim, '<h4>$1</h4>');
  html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');

  // Bold & Italic
  html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');

  // Inline Code
  html = html.replace(/`([^`]+)`/gim, '<code>$1</code>');

  // Bullet items
  html = html.replace(/^\s*[-•*]\s+(.*$)/gim, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

  // Line breaks
  html = html.replace(/\n\n/g, '<br><br>');
  html = html.replace(/\n/g, '<br>');

  return html;
}


