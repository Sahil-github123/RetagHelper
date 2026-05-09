# RetagHelper

A lightweight local web app to simulate IIT Bombay course retagging and instantly visualize its impact on **SPI, CPI, and GPA**.

Built as a single-file Python application with an embedded modern frontend - no frameworks, databases, or setup hassle.

## Features

* Interactive retagging simulator
* Real-time CPI / SPI / GPA recalculation
* IIT Bombay UG rulebook-based tag transition logic
* Semester-wise performance tracking
* Add/remove semesters and courses dynamically
* Clean responsive UI with zero dependencies
* Runs entirely locally in your browser

## Supported Tags

* Core Courses (C)
* Department Electives (D)
* STEM Electives (SE)
* HASMED Electives (HE)
* Minor Courses (M)
* Honors / Honors Electives
* Additional Learning Courses (T)
* Non-credit Courses (N)

## Run Locally

```bash
python RetagHelper.py
```

Then open:

```text
http://localhost:5000
```

## Requirements

* Python 3.x
* No external packages required

## How It Works

The app launches a local HTTP server using Python’s built-in `http.server` module and serves an embedded HTML/CSS/JS frontend.

All calculations are performed client-side in real time.

## Screenshots / UI Highlights

* Semester-wise SPI cards
* Live CPI delta tracking
* Retag impact indicators
* Dynamic course management

## Notes

* Retagging rules follow IIT Bombay UG Rulebook 2025-26.
* CPI includes only CPI-counting tags.
* Non-credit and excluded categories are ignored in CPI calculations.
* GPA is just taken as 0.4*CPI

## License

MIT License
