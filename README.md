# RetagHelper

A lightweight local web app to simulate IIT Bombay course retagging and instantly visualize its impact on **SPI, CPI, GPA, and credit distribution**.

Built as a **single-file Python application** with an embedded frontend — no frameworks, setup, or external dependencies required.

---

## Features

* Real-time CPI / SPI / GPA recalculation
* Interactive course retagging simulator
* IIT Bombay UG Rulebook 2025–26 based tag transitions
* Total CPI credits + tag-wise credit tracking
* Detailed retag summary panel with CPI impact
* 💾 Save current state as `.json`
* 📂 Load previous analysis anytime
* Add/remove semesters and courses dynamically
* Responsive modern UI
* Runs entirely locally

---

## Save / Load Feature

RetagHelper allows you to save your entire analysis state and continue later.

### 💾 Save

Exports a `.json` file containing:

* Original course tags
* Updated/retagged course tags
* Added/removed courses
* Credits and grades
* Entire current analysis state

### 📂 Load

Load a previously saved `.json` file to instantly restore your work and continue analysis from where you left off.

> **Important:**
> The `.json` file stores the internal state and is not meant for easy manual reading.
> After finalizing your retagging, it is recommended to take a screenshot of the **📊 Summary** panel (top-right button), since it provides a clean readable overview of:
>
> * Retagged courses
> * Tag changes
> * CPI/GPA impact
> * Tag-wise credit redistribution

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

```bash id="5tlivq"
python RetagHelper.py
```

Then open:

```text id="0k4f4g"
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

```text id="jlwmvn"
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
