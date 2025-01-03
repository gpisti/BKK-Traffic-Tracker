# BKK-Traffic-Tracker
This analysis evaluates the efficiency and reliability of each bus route by examining average speed and on-time performance. It helps identify operational strengths and weaknesses, enabling more effective scheduling and resource allocation for improved overall service quality.

---
# Table of Contents

- [Overview](#overview)  
- [File Structure](#file-structure)  
- [Key Features](#key-features)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Core Analyses](#core-analyses)  
- [Additional Notes](#additional-notes)  
- [Contributing](#contributing)  
- [License](#license) 

---

## Overview

**BKK Traffic Tracker** is a data pipeline and analytics project designed to provide real-time and historical insights into Budapest’s public transportation network. By ingesting live GTFS data, storing it in a PostgreSQL database, and visualizing key metrics through Streamlit, this system enables stakeholders to identify inefficiencies, improve scheduling, and enhance overall route performance for passengers.


---

## File Structure
```bash
bkk_traffic_tracker/
├── config.py
├── data_collection.py
├── db/
│   ├── database_consumer.py 
│   ├── db_queries.py 
│   └── db_utils.py 
├── encoders/ 
│   ├── gtfs_realtime_pb2.py
│   └── gtfs_realtime_realcity_pb2.py
├── modules/
│   ├── kafka_utils.py
│   └── queries.py
├── analysis.py
├── data_collection.py
├── streamlit_gui.py
├── requirements.txt
└── README.md
```
> **Note**: You might see two `.pb2` files under `encoders/`. Both are required for development or backward compatibility, even if only one is actively referenced.


---

## Key Features

1. **Real-Time Data Ingestion**  
   - Collects live vehicle positions from BKK’s GTFS-Realtime endpoint (`data_collection.py`).
   - Streams data into Kafka for scalable, fault-tolerant message handling.

2. **Database Storage**  
   - Uses a PostgreSQL database (`db/database_consumer.py`) to store cleaned data for long-term analysis.
   - Custom SQL scripts and utilities (`db/db_queries.py`, `db/db_utils.py`) manage table creation and data upserts.

3. **Analytics & Visualization**  
   - Provides multiple analyses in `analysis.py` (e.g., route performance, traffic heatmaps).
   - A Streamlit dashboard (`streamlit_gui.py`) displays results with interactive charts and maps.

4. **Configurable & Extensible**  
   - Centralizes configs in `config.py` for easy updates (API keys, DB credentials).
   - Exclusion of non-standard routes (e.g., `9999`) ensures data integrity.
   - Modular design under `modules/` enables streamlined maintenance and feature additions.

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/bkk_traffic_tracker.git
   cd bkk_traffic_tracker


2 **Create & Activate a Virtual Environment** (optional, but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Configure Database

- Ensure PostgreSQL is running and credentials match what’s in `config.py`.
- Adjust parameters (e.g., `DB_HOST`, `DB_PORT`, `DB_NAME`) as needed.

---

## Usage

1. Run Data Collection

```bash
python data_collection.py
```
- Fetches live GTFS data and produces messages to Kafka.


2. Start Database Consumer

```bash
python db/database_consumer.py
```
- Consumes messages from Kafka, inserting/updating PostgreSQL tables.


3. Launch Analytics Dashboard

```bash
streamlit run streamlit_gui.py
```
- Access the Streamlit interface at `http://localhost:8501` (default port).
- View route performance metrics, real-time maps, and more.

---

## Core Analyses

1. **Route Performance Analysis**
Compares average speed and on-time performance across bus routes. Helps identify routes needing schedule adjustments or added resources.
![image](https://github.com/user-attachments/assets/59a2514a-ba7f-4da3-af6c-9c8e43b5ca96)


2. **Peak vs. Non-Peak Hour Analysis**
Evaluates traffic volume and speed fluctuations during different hours of the day. High-volume peak hours generally show lower average speeds.
![image](https://github.com/user-attachments/assets/64aac687-ee5a-4310-9ef7-06f47d599202)


3. **Traffic Density Heatmap**
Displays clustering of vehicles in real-time or historically across latitude/longitude points. Ideal for pinpointing congestion hotspots.
![image](https://github.com/user-attachments/assets/0c350ec4-610f-447b-8235-1fecb1199175)


4. **Correlation Analysis**
Investigates relationships among variables (e.g., speed vs. traffic count) to identify trends or bottlenecks in operations.
![image](https://github.com/user-attachments/assets/fa05852c-5c92-4944-a918-6445244209c2)

---

## Additional Notes

- **Custom Encoders**: `encoders/` holds `.pb2` files generated from GTFS-Realtime .proto definitions. Both files may be necessary for local testing or extended data parsing scenarios.
- **Excluded Routes**: Certain routes (like `9999`) are filtered out to prevent erroneous data from skewing analytics.
- **Configuration Management**: Place sensitive info (like API keys) in environment variables or a `.env` file, referencing them in config.py.

---

## Contributing
1. **Fork the Repo** and create a feature branch for your changes.
2. **Add/Improve Features** with well-documented commits.
3. **Open a Pull Request** and detail what the changes address or improve.

---

## License
This project is distributed under the [MIT License](https://mit-license.org/). See the `LICENSE` file for further details.
