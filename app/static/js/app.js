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

document.addEventListener("DOMContentLoaded", () => {
  initMap();
  initEventHandlers();
  loadSystemStatus();
  loadClimateCells();
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
      selectedScenario = btn.dataset.type;
    });
  });

  // Budget slider
  const slider = document.getElementById('budget-slider');
  const budgetDisplay = document.getElementById('budget-value-display');
  slider.addEventListener('input', (e) => {
    const lakhs = parseFloat(e.target.value);
    currentBudgetInr = lakhs * 100000.0;
    const cr = (lakhs / 100.0).toFixed(2);
    budgetDisplay.textContent = `₹${lakhs.toFixed(1)} Lakhs (₹${cr} Cr)`;
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
  document.getElementById('compare-btn').addEventListener('click', runComparison);

  // Results Tab Switching
  document.querySelectorAll('.tab-btn').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      tab.classList.add('active');
      const targetPane = document.getElementById(tab.dataset.tab);
      if (targetPane) targetPane.classList.add('active');
    });
  });

  // Close inspector button
  document.getElementById('close-inspector').addEventListener('click', () => {
    document.getElementById('cell-inspector').classList.add('hidden');
  });

  // Export JSON
  document.getElementById('export-json-btn').addEventListener('click', exportPlanJson);
}

// ================= API CALLS =================
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

async function loadClimateCells() {
  try {
    const res = await fetch('/api/cells');
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
  btnText.textContent = "Synthesizing Prescriptive Plan...";

  try {
    const res = await fetch('/api/action-plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        city: 'Bengaluru',
        budget_inr: currentBudgetInr,
        scenario_type: selectedScenario
      })
    });
    
    const plan = await res.json();
    currentActionPlan = plan;
    currentScenarioResult = plan.scenario_result;
    
    updateKpiCards(currentScenarioResult);
    renderActionPlan(plan);
    renderAllocationsTable(currentScenarioResult);
    renderInterventionMarkers(currentScenarioResult);
    
    // Switch to Plan tab
    document.querySelector('[data-tab="tab-plan"]').click();
  } catch (err) {
    console.error("Action plan generation error:", err);
    alert("Could not generate action plan. Check console for details.");
  } finally {
    btn.disabled = false;
    spinner.classList.add('hidden');
    btnText.textContent = "🚀 Run Avani Climate Agent";
  }
}

async function runComparison() {
  try {
    const res = await fetch(`/api/scenarios/compare?budget_inr=${currentBudgetInr}`);
    const data = await res.json();
    renderComparisonGrid(data.scenarios);
    document.querySelector('[data-tab="tab-comparison"]').click();
  } catch (err) {
    console.error("Error fetching comparison:", err);
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
          💰 Cost: ₹${(alloc.total_cost/100000).toFixed(2)}L
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
            Target Cooling: <b style="color: #38bdf8;">-${alloc.cooling_reduction_c}°C</b> | Budget: <b>₹${(alloc.total_cost/100000).toFixed(2)}L</b>
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
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 11px;">
      <div>Surface Temp (LST): <b>${cell.lst}°C</b></div>
      <div>Heat Anomaly: <b style="color: #f43f5e;">+${cell.heat_anomaly}°C</b></div>
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
    ${allocHtml}
  `;

  inspector.classList.remove('hidden');
}

// ================= RESULTS RENDERING =================
function updateKpiCards(scenario) {
  document.getElementById('kpi-cooling').textContent = `-${scenario.avg_temp_reduction_c.toFixed(2)} °C`;
  document.getElementById('kpi-max-cooling').textContent = `Peak: -${scenario.max_temp_reduction_c.toFixed(2)} °C in Hotspots`;
  document.getElementById('kpi-beneficiaries').textContent = scenario.total_beneficiaries.toLocaleString();
  document.getElementById('kpi-budget').textContent = `₹${scenario.budget_spent_lakhs.toFixed(1)} Lakhs`;
  
  const pct = ((scenario.budget_spent_inr / scenario.total_budget_inr) * 100).toFixed(1);
  const cr = (scenario.total_budget_inr / 10000000.0).toFixed(2);
  document.getElementById('kpi-budget-pct').textContent = `${pct}% of ₹${cr} Cr budget`;
  document.getElementById('kpi-exposure').textContent = `${scenario.heat_exposure_reduction_pct.toFixed(1)}%`;
}

function renderActionPlan(plan) {
  document.getElementById('plan-model-badge').textContent = plan.llm_model;
  document.getElementById('plan-solver-badge').textContent = `OR-Tools SCIP • ${plan.scenario_result.computation_time_ms}ms`;
  document.getElementById('plan-title').textContent = plan.scenario_result.scenario_title;
  document.getElementById('plan-exec-summary').textContent = plan.executive_summary;
  document.getElementById('plan-rationale').textContent = plan.rationale;

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

  // Implementation phases
  const timelineContainer = document.getElementById('timeline-container');
  timelineContainer.innerHTML = plan.implementation_phases.map(p => `
    <div class="phase-card">
      <div class="phase-title">${p.phase}</div>
      <div class="phase-time">⏱️ ${p.timeline} • Estimated Spend: <b>₹${(p.estimated_spend_inr/100000).toFixed(1)}L</b></div>
      <ul class="phase-milestones">
        ${p.key_milestones.map(m => `<li>${m}</li>`).join('')}
      </ul>
    </div>
  `).join('');

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
    <span>💰 Total Spend: <b>₹${scenario.budget_spent_lakhs}L</b></span>
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
      <td><b>₹${(a.total_cost/100000).toFixed(2)}</b></td>
    </tr>
  `).join('');
}

function renderComparisonGrid(scenarios) {
  const grid = document.getElementById('comparison-grid');
  grid.innerHTML = Object.entries(scenarios).map(([key, s]) => `
    <div class="comp-card ${key === selectedScenario ? 'highlight' : ''}">
      <div class="comp-header">
        <span>${s.title}</span>
        <span style="color: #38bdf8;">-${s.avg_temp_reduction_c}°C</span>
      </div>
      <div class="comp-metrics">
        <div class="comp-metric-item">
          <small>Beneficiaries</small>
          <strong>${s.total_beneficiaries.toLocaleString()}</strong>
        </div>
        <div class="comp-metric-item">
          <small>Budget Used</small>
          <strong>₹${s.budget_spent_lakhs}L</strong>
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
    </div>
  `).join('');
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
