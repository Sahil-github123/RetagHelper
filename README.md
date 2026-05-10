# RetagHelper

A lightweight local web app to simulate IIT Bombay course retagging and instantly visualize its impact on **SPI, CPI, GPA, and credit distribution**.

Built as a **single-file Python application** with an embedded frontend — no frameworks, setup, or external dependencies required.

---

## Features

* Real-time CPI / SPI / GPA recalculation
* Interactive course retagging simulator
* IIT Bombay UG Rulebook 2025–26 based tag transitions
* Total CPI credits + tag-wise credit tracking
* Retag summary panel with CPI impact
* Save / Load progress as `.json`
* Add/remove semesters and courses dynamically
* Responsive modern UI
* Runs entirely locally

---

## Supported Tags

| Tag | Meaning                   |
| --- | ------------------------- |
| C   | Core                      |
| D   | Department Elective       |
| SE  | STEM Elective             |
| HE  | HASMED Elective           |
| M   | Minor                     |
| T   | Additional Learning (ALC) |
| O   | Honors                    |
| E   | Honors Elective           |
| N   | Non-credit                |

---

## Run Locally

```bash id="v5c3qv"
python RetagHelper.py
```

Then open:

```text id="l2d9jq"
http://localhost:5000
```

---

## Requirements

* Python 3.x
* No external packages required

---

## Notes

* CPI includes only CPI-counted tags (C, D, SE, HE)
* GPA is approximated as:

```text id="t7x7t6"
GPA = 0.4 × CPI
```

* Retagging rules follow IIT Bombay UG Rulebook 2025–26

---

## Tech Stack

* Python (`http.server`)
* Embedded HTML/CSS/JavaScript frontend
* Fully client-side calculations

---

## License

MIT License
