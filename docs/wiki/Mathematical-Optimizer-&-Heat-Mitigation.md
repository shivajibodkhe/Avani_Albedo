# 🧮 Mathematical Optimizer & Heat Mitigation

Avani Albedo replaces subjective municipal guesswork with mathematical rigor using **Google OR-Tools** and the **SCIP (Solving Constraint Integer Programs)** mixed-integer linear solver.

---

## 🎯 Formulation

$$\text{Maximize } \sum_{i \in \text{Cells}} \sum_{j \in \text{Interventions}} \text{HVI}_i \times \text{Pop}_i \times \Delta T_{i,j} \times x_{i,j}$$

Subject to:
1. **Municipal Budget Constraint**:
   $$\sum_{i} \sum_{j} \text{Cost}_j \times \text{Area}_{i,j} \times x_{i,j} \le \text{Total Budget (INR)}$$
2. **Feasibility & Land Capacity**:
   $$\sum_{j} x_{i,j} \le 1 \quad \forall i \in \text{Cells}$$
3. **Microclimate Diminishing Returns**:
   Maximum effective localized temperature drop capped by ambient boundary layer physics ($\Delta T \le 3.5^\circ\text{C}$).

---

## 🛠️ Interventions Supported

| Code | Cooling Intervention | Albedo ($\alpha$) | Unit Cost ($\text{INR/m}^2$) | $\Delta T$ Reduction |
| :--- | :--- | :--- | :--- | :--- |
| `cool_roof` | High-Reflectance Cool Roof Coatings | 0.85 – 0.90 | ₹120 | $-1.8^\circ\text{C}$ to $-2.5^\circ\text{C}$ |
| `urban_forest`| Miyawaki Urban Pocket Forests & Tree Canopies | 0.20 (Evaporative) | ₹450 | $-2.2^\circ\text{C}$ to $-3.2^\circ\text{C}$ |
| `permeable_pave`| Permeable & Reflective Cool Pavements | 0.55 – 0.65 | ₹320 | $-1.1^\circ\text{C}$ to $-1.6^\circ\text{C}$ |
| `shade_canopy`| Solar Photovoltaic Reflective Shading | 0.70 | ₹580 | $-1.4^\circ\text{C}$ to $-2.0^\circ\text{C}$ |
| `water_feature`| Bioswales & Urban Water Retention Basins | 0.10 (Latent Heat) | ₹650 | $-2.0^\circ\text{C}$ to $-3.0^\circ\text{C}$ |

---

## ⚡ Multi-Scenario Comparisons
The UI allows planners to compare:
- **Optimized (SCIP Algorithm)**: Maximizes lives protected per rupee spent.
- **Equal Allocation**: Divides budget evenly across all wards.
- **Targeted Vulnerable**: Allocates exclusively to Critical HVI wards.
