# 🏙️ City Onboarding Guide

Administrators can dynamically register new metropolitan regions, municipal corporations, and microclimate wards directly from the web interface without modifying code or restarting the server.

---

## 🧭 Step-by-Step Onboarding via Admin Control Center

1. **Open Admin Control Center**:
   - Log in as Super Admin (`srbodkhe@gmail.com`).
   - Click the **⚙️ Admin** button in the header.
2. **Navigate to the "🏙️ Onboard New City" Tab**:
   - Fill in:
     - **Country**: Select existing country (India, UAE, etc.) or type a new country.
     - **City Name**: e.g., `Nagpur`, `Pune`, `Singapore`.
     - **Geographic Coordinates**: Center Latitude & Longitude (e.g. `21.1458, 79.0882`).
     - **Default Surface Temperature**: Ambient baseline (e.g., $43.2^\circ\text{C}$).
     - **Average Albedo & Vegetation (NDVI)**: e.g., $0.15$ albedo, $0.12$ NDVI.
     - **Initial Wards List**: Comma-separated list of municipal wards or neighborhoods (e.g., *Sitabuldi, Dharampeth, Sadar, Wardhaman Nagar, MIDC Butibori*).
3. **Submit**:
   - Click **"🚀 Onboard City into Platform"**.
   - The city is immediately registered in `CITIES_REGISTRY`, added to the Country $\to$ City cascading dropdown, and initialized with synthetic/interpolated microclimate heat cells.

---

## 💻 API Endpoint

```http
POST /api/admin/cities/add
Content-Type: application/json
Authorization: Bearer <ADMIN_TOKEN>

{
  "country": "India",
  "city": "Nagpur",
  "lat": 21.1458,
  "lon": 79.0882,
  "surface_temp_c": 43.5,
  "albedo": 0.15,
  "ndvi": 0.12,
  "wards": ["Sitabuldi", "Dharampeth", "Sadar", "Wardhaman Nagar", "MIDC Butibori"]
}
```
