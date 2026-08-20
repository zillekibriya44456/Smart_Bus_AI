# Smart Bus Stop AI - Traffic Simulation Architecture

## Overview
This document details the integration plan for **Eclipse SUMO** (Simulation of Urban MObility) within the Smart Bus Stop AI project. 
The simulation module runs completely independent of the frontend visualization, acting as a backend-controlled service.

## Simulation Goal
To mathematically compare two scenarios and measure traffic impact:
- **Scenario A (Baseline)**: The current, un-optimized configuration of a bus stop.
- **Scenario B (Optimized)**: The AI-recommended configuration (e.g., adding a dedicated bus bay, altering stop position, changing road width constraints).

## Monitored Metrics
The simulation tracks the following Key Performance Indicators (KPIs):
- Average vehicle speed
- Traffic delay
- Queue length
- Vehicle waiting time
- Bus travel time
- Bus dwell time
- Overall throughput

## Directory Structure
```
simulation/
├── configs/       # SUMO configuration files (*.sumocfg)
├── networks/      # Network files (*.net.xml)
├── outputs/       # Simulation result outputs (trips, edges, emissions)
├── routes/        # Vehicle demand generation (*.rou.xml)
├── scenarios/     # Scenario-specific overrides and configuration
│   ├── baseline/
│   └── optimized/
└── scripts/       # Python scripts to orchestrate traci / libsumo
```

## Installation Requirements (macOS)
Due to changes in Homebrew tap trust policies for Eclipse SUMO, the most reliable installation method is via `pip`, which bundles the precompiled `sumo` and `netconvert` binaries for your OS architecture:
```bash
pip install eclipse-sumo
```

## Data Flow
The architecture defines a clear pipeline from AI inference to simulation execution:

1. **Suitability Analysis**: The ML Engine (`predict_suitability`, `calculate_sub_scores`) evaluates a location.
2. **Infrastructure Recommendation**: The Rule Engine dictates modifications (e.g., "Add 15m bus bay").
3. **Simulation Configuration**: A Python service dynamically modifies `.rou.xml` and `.net.xml` parameters to represent the recommendations.
4. **SUMO**: Executed either via CLI or `traci`/`libsumo` python bindings to simulate both Baseline and Optimized states in parallel/sequence.
5. **Simulation Results**: Output XMLs are parsed back into JSON metrics.
6. **Frontend Visualization**: The React frontend pulls the JSON metrics and displays comparative charts.
