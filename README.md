# Warehouse Cold Storage Monitoring System

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)

## Overview

This project is a real-time monitoring solution for warehouse cold storage zones, focusing on **temperature and humidity** tracking to ensure product safety, regulatory compliance, and operational efficiency. It features:

- Sensor data simulation with customizable thresholds
- AI-powered predictive alerts for early detection
- Dynamic dashboards with real-time and historical analytics
- Comprehensive performance scoring based on industry standards
- Cost impact analytics linking environmental control to financial outcomes

---

## Features

- **Multi-zone monitoring:** Separate handling for freezer, chiller, produce, and pharmaceutical zones
- **User-friendly UI:** Built with Streamlit; adjustable alert thresholds and visualization
- **Real-time and historical data:** Live updates, date range selection, trend comparisons
- **Predictive models:** ML-based alert prediction to anticipate violations
- **Financial analytics:** Dashboard integrating operational KPIs with estimated cost impacts
- **Export and reporting:** Downloadable CSVs for audits and presentations

---

## Tech Stack

- Python 3.8+
- [Streamlit](https://streamlit.io) for UI
- [Pandas](https://pandas.pydata.org) & [NumPy](https://numpy.org) for data processing
- [scikit-learn](https://scikit-learn.org) for ML models
- [Altair](https://altair-viz.github.io) for visualizations

---

## Setup Instructions

### Prerequisites

- Python 3.8 or newer installed
- Git

### Installation

1. Clone the repo:
   
git clone https://github.com/yourusername/warehouse-cold-storage-monitoring.git
cd warehouse-cold-storage-monitoring   

2. Create and activate a virtual environment (optional but recommended):

python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

3. Install dependencies:

pip install -r requirements.txt


4. Run the live data generator script (simulates sensor data):

python src/live_data_generator.py

5. Launch the dashboard:

streamlit run src/dashboard.py

---

## Project Structure

- `src/live_data_generator.py`: Simulates real-time sensor data with occasional alerts  
- `pages/`: Streamlit app pages with dashboards and zone details  
- `src/models/`: Machine learning code and saved models  
- `data/`: Sample generated data files  
- `docs/`: Project report and presentation slides  

---

## Usage

- Access the dashboard in your browser (usually at `http://localhost:8501`)  
- Use the sidebar to adjust alert thresholds and date filters  
- Monitor zone-specific KPIs and see predictive alerts  
- Export data and generate reports for compliance and decision-making  

---

## Future Enhancements

- Integration with real IoT sensors in warehouses  
- Advanced ML models with deep learning for anomaly detection  
- Mobile-responsive design and PWA version with push notifications  
- Automated mitigation controls interfacing with HVAC systems  

---

## Team & Acknowledgments

Developed by Group 4[csbs(2026),SRMIST] as part of the Cognizant SCM Hackathon 2025.

Special thanks to mentors and organizers for their support.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or collaboration, reach out at ss0506@srmist.edu.in

