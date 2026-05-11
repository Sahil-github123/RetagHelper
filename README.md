# RetagHelper

Simulate IIT Bombay course retagging and instantly see the impact on **SPI, CPI, GPA, and credit distribution**.

Open `index.html` in any browser — no server, no setup.

---

## Features

- Real-time CPI / SPI / GPA recalculation
- Interactive retagging simulator with IIT Bombay UG Rulebook 2025–26 tag transition rules
- Tag-wise credit tracking + total CPI credits display
- Detailed retag summary panel (CPI impact, credit redistribution, retagged course list)
- 💾 Save state as `.json` · 📂 Load previous analysis
- Add/remove courses and semesters dynamically

---

## Usage

Just open `index.html` in a browser. No installation needed.

To continue a previous session, click **📂 Load** and select your saved `.json` file.  
After finalizing, use **📊 Summary** for a clean overview — recommended to screenshot before closing.

---

## Supported Tags

| Tag | Meaning | Counts toward CPI |
|-----|---------|:-----------------:|
| C | Core | ✓ |
| D | Department Elective | ✓ |
| SE | STEM Elective | ✓ |
| HE | HASMED Elective | ✓ |
| M | Minor | — |
| T | Additional Learning (ALC) | — |
| O | Honors | — |
| E | Honors Elective | — |
| N | Non-credit | — |

---

## Notes

- GPA is approximated as `0.4 × CPI`
- Retagging is allowed **twice** per program (pre-placements & post-curriculum)

---

## Tech Stack

HTML · CSS · Vanilla JavaScript (fully client-side)

---

## License
MIT
