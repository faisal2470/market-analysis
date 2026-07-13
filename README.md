# market-analysis

## Overview

`market-analysis` is a modular Python foundation for a future professional stock
market analytics platform focused on the Indian markets (NSE and BSE). The
current project deliberately contains only package structure and typed
placeholders, allowing each capability to be developed and validated
incrementally.

## Planned Features

- Historical market data
- Live market data
- Market screeners
- Technical indicators
- Interactive charts
- Machine learning
- Web dashboard

## Project Architecture

- `market_analysis.data`: market data access, symbols, screeners, and watchlists.
- `market_analysis.indicators`: technical-indicator calculations.
- `market_analysis.charts`: chart and dashboard presentation helpers.
- `market_analysis.ml`: datasets, feature engineering, models, and training.
- `notebooks`: exploratory validation of individual modules.
- `tests`: automated package tests.
- `data`: local historical, live, and exported data storage (ignored by Git).

## Development Workflow

Each feature follows a deliberate progression:

`Module → Notebook Testing → Validation → Integration`

Implement one focused module, exercise it in a notebook, refine and validate it,
then integrate and commit the change before starting the next module.

## Installation

Use Python 3.12 or later. From the repository root, install the package in
editable mode:

```bash
pip install -e .
```

For development tools, install the development extra:

```bash
pip install -e ".[dev]"
```
