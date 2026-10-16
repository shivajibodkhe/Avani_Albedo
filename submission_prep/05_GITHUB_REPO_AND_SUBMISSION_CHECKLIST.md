# AI Builder Cup — GitHub Repository & Final Submission Checklist

> **Purpose:**  
> A pre-flight verification checklist for the team before clicking **"Submit"** on the official Google Cloud AI Builder Cup submission portal.

---

## 📋 1. Mandatory Rule Compliance Matrix

| Mandatory Rule | Submission Requirement | Avani Albedo Deliverable | Verification Status |
| :--- | :--- | :--- | :--- |
| **Pitch Deck** | Must follow prescribed challenge template (`AI Builder Cup.pptx`, 16 slides). Non-conforming formats face disqualification. | `submission_prep/02_PITCH_DECK_SLIDES.md` maps 1-to-1 to all 16 template slides. | 🟢 Completed & Aligned |
| **Video Demonstration** | Strictly **3 to 4 minutes** (180s - 240s). Exceeding duration attracts penalties or disqualification. Must demonstrate working functionality. | `submission_prep/03_3_TO_4_MIN_VIDEO_DEMO_SCRIPT.md` timed at exactly **3 minutes 30 seconds**. | 🟢 Script Ready & Timed |
| **Deployed Prototype Link** | Valid, accessible link to working prototype. Must remain functional throughout evaluation with no retry allowances. | `https://avani-albedo-hbxrfbol2a-el.a.run.app` deployed on Google Cloud Run with 99.9% SLA. | 🟢 Live & Health Checked (HTTP 200) |
| **GitHub Repository** | Accessible public repository with relevant source code, documentation, and supporting materials. | `https://github.com/shivajibodkhe/Avani_Albedo` with complete docs, tests, and clean architecture. | 🟢 Public & Up-to-Date |
| **Brief Description** | Must detail how **Firebase, Firestore, Cloud Run, and Gemini** are leveraged in the solution. | `submission_prep/01_MANDATORY_BRIEF_DESCRIPTION.md` contains the copy-paste text meeting all requirements. | 🟢 Formatted & Ready |

---

## 👥 2. Official Team Information Checklist

Verify that all team members are listed accurately in the submission portal:

- [ ] **Team Name:** `Avani Albedo`
- [ ] **Team Leader:**
  - **Full Name:** Shivaji Bodkhe
  - **Email:** `srbodkhe@gmail.com`
- [ ] **Team Members:**
  1. **Shivaji Bodkhe** (Leader) — `srbodkhe@gmail.com`
  2. **Niranchana K** — `niranchana.2001.17@gmail.com`
  3. **Anusha D** — `anushadhananjayamurthy@gmail.com`
  4. **Akshatha Ramachandra Prabhu** — `akshatha.r.prabhu@gmail.com`
- [ ] **Track / Category:** `Sustainability & Social Impact`

---

## 🔗 3. Public Accessibility & Link Verification Table

Every link below **MUST** be verified in an Incognito / Private window without personal Google accounts logged in:

| Link Name | Submission URL | Public Access Verified | Tested Date |
| :--- | :--- | :---: | :---: |
| **Live Deployed Prototype** | `https://avani-albedo-hbxrfbol2a-el.a.run.app` | [ ] Yes | Oct 16, 2026 |
| **Public API Status** | `https://avani-albedo-hbxrfbol2a-el.a.run.app/api/status` | [ ] Yes | Oct 16, 2026 |
| **OpenAPI / Swagger UI** | `https://avani-albedo-hbxrfbol2a-el.a.run.app/docs` | [ ] Yes | Oct 16, 2026 |
| **GitHub Public Repo** | `https://github.com/shivajibodkhe/Avani_Albedo` | [ ] Yes | Oct 16, 2026 |
| **GitHub Wiki / Docs** | `https://github.com/shivajibodkhe/Avani_Albedo/wiki` | [ ] Yes | Oct 16, 2026 |
| **Pitch Deck (PDF / PPTX)** | *(Add your Google Drive / SlideShare shareable link)* | [ ] Yes *(Ensure "Anyone with the link can view")* | Oct 16, 2026 |
| **Demo Video (YouTube / Drive)** | *(Add your YouTube Unlisted or Drive link)* | [ ] Yes *(Ensure "Anyone with the link can view")* | Oct 16, 2026 |

> ⚠️ **CRITICAL WARNING FOR GOOGLE DRIVE LINKS:**  
> If you upload your Pitch Deck PPTX or Demo Video MP4 to Google Drive, verify that Link Sharing is set to:  
> **"Anyone with the link" → "Viewer"**. If it is set to "Restricted", judges cannot evaluate your submission and you may receive 0 points.

---

## 📽️ 4. Video Recording Duration & Quality Verification

Check these items before finalizing your video upload:

- [ ] **Exact Duration Check:** Is the video between **3:00 and 4:00 minutes**? (Recommended target: **3:30**).
  - *Under 3:00 may miss mandatory features.*
  - *Over 4:00 attracts disqualification or point penalties.*
- [ ] **Audio Quality:** Clear narration, no background hum, voiceover synchronized with UI clicks.
- [ ] **Resolution:** Minimum 1080p (Full HD) at 30fps or 60fps.
- [ ] **Key Features Demonstrated in Video:**
  - [ ] Satellite Heat Map exploration (LST, NDVI, NDBI, HVI).
  - [ ] Budget slider adjustment and Strategic Objective selection.
  - [ ] Google OR-Tools optimization run showing sub-50ms execution.
  - [ ] Gemini 2.0 Flash AI Action Plan generation for Municipal Commissioner.
  - [ ] Floating AI Help Bot interaction.
  - [ ] Scenario save to Cloud Firestore and export functionality.

---

## 💻 5. GitHub Repository Hygiene & Security Verification

Confirm the public GitHub repository is clean, professional, and compliant:

- [ ] **Branch Protection:** `main` branch protected from accidental force-pushes.
- [ ] **No Secret Exposure:**
  - `.env` and `.env.local` are listed in `.gitignore`.
  - No active Google API keys, GCP service account JSON files, or Gemini keys committed in git history.
  - Cloud Run revision uses Google Secret Manager for `GEMINI_API_KEY`.
- [ ] **README.md:** Clean, professional root README with architectural diagrams, feature list, GCP stack highlights, and setup instructions.
- [ ] **Code Hygiene:**
  - All temporary scratch files, debug logs, and unused mock scripts deleted.
  - All unit and integration tests passing (`pytest tests/`).
  - Formatted code structure following clean FastAPI and modular frontend standards.
- [ ] **License:** Open-source license (MIT / Apache 2.0) included.

---

## 🚀 6. Step-by-Step Submission Day Execution Plan

1. **Step 1 — Slides Finalization:**
   - Open `AI Builder Cup.pptx`.
   - Copy contents from `submission_prep/02_PITCH_DECK_SLIDES.md` into Slides 1 through 16.
   - Export as both `.pptx` and `.pdf`.
2. **Step 2 — Video Recording & Upload:**
   - Record the 3:30 walkthrough using `submission_prep/03_3_TO_4_MIN_VIDEO_DEMO_SCRIPT.md`.
   - Upload to YouTube as **Unlisted** (or Google Drive with public view permissions).
   - Test playback in an incognito window.
3. **Step 3 — Form Submission:**
   - Open the official AI Builder Cup submission form.
   - Paste the Brief Description from `submission_prep/01_MANDATORY_BRIEF_DESCRIPTION.md`.
   - Enter Deployed Prototype Link: `https://avani-albedo-hbxrfbol2a-el.a.run.app`
   - Enter Judge Credentials: `judges` / `AvaniAlbedo12042026#`
   - Enter GitHub Repo: `https://github.com/shivajibodkhe/Avani_Albedo`
   - Attach / link Pitch Deck & Video.
   - Review all fields against Section 2 of this checklist and submit!
