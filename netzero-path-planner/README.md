## 🧾 NetZero Path Planner Documentation

### 📌 Project Name: NetZero Path Planner

### 🎯 Project Goal:

To build a web application that allows companies to input baseline emission data (Scope 1 and 2) and select different domestic and international carbon reduction reference models to generate annual carbon reduction target data tables and visualized curves, along with report paragraph exports.

### 🧱 Project Structure:

```
netzero-path-planner/
├── src
│   ├── models                  # Model logic modules
│   ├── utils                   # Utility functions
│   └── main.py                 # Streamlit main interface
├── data
│   └── sample_input.xlsx       # Sample data
├── tests                       # Unit tests
├── requirements.txt            # Python package list
├── .gitignore                  # Git ignore file
├── setup.py                    # Project setup
└── README.md                   # Project documentation
```

### 🔧 Input Parameters (User Input):

- Scope 1 Emissions (S1): Integer, unit tCO₂e
- Scope 2 Emissions (S2): Integer, unit tCO₂e
- Baseline Year (default=2020)
- Carbon Reduction Reference Path (single choice):
  - `SBTi_1.5C`
  - `Taiwan_Policy`
- Apply RE100 (applicable to S2, zero by 2030) ✅/❌
- Enable Advanced Path Customization (available in second phase) ❌

### 🔢 Model Formulas (Core Logic):

- **SBTi_1.5C**: Emission calculation based on annual reduction.
- **Taiwan_Policy**: Emission calculation based on Taiwan's policy targets.
- **RE100**: Emission calculation for Scope 2 based on RE100 targets.

### 📊 Expected Output:

- Line charts: Annual total carbon emissions (comparison of multiple paths)
- Tables: Annual emissions, relative reduction percentages
- CSV download
- Automatically generated report paragraphs

### 🛠 Recommended Tools and Packages:

| Name                      | Purpose             |
| ----------------------- | ------------------ |
| `Streamlit`             | Web front-end interface |
| `pandas`                | Data manipulation and processing |
| `matplotlib` / `plotly` | Visualization tools |
| `yaml` / `json`         | Configuration management |
| `openpyxl`              | Excel import (future expansion) |

### 🧩 Expected Future Features (Not Enabled):

- Custom annual target values
- Internal carbon pricing simulation
- Integration with equipment inventory data analysis

### 📄 Setup Instructions:

1. Clone the repository.
2. Install the required packages using `pip install -r requirements.txt`.
3. Run the application using `streamlit run src/main.py`.

### 📞 Contact:

For any inquiries, please reach out to the project maintainers.