import pandas as pd

def export_to_csv(data, filename):
    """Exports the given data to a CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def export_report(data, filename):
    """Generates a report and saves it to a text file."""
    with open(filename, 'w') as f:
        for key, value in data.items():
            f.write(f"{key}: {value}\n")