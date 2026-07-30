
from tkinter import filedialog
import tkinter as tk
import matplotlib.pyplot as plt
from fileinput import filename
from datetime import date
import pandas as pd

class DensityHistogram:
    def __init__(self):
        self.group_densities = {}

    def get_density(self):
        # Create hidden root window for file dialog
        root = tk.Tk()
        root.withdraw()

        print("\nSelect your density CSV file...")
        csv_path = filedialog.askopenfilename(
            title="Select Density CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if not csv_path:
            raise FileNotFoundError("No CSV file selected.")
            # Load density CSV

        df = pd.read_csv(csv_path)

        self.group_densities = {}
        data = []
        # Fill dictionary from CSV
        for _, row in df.iterrows():
            density = float(row["density"])

            data.append(density)
    
        print("\nLoaded density values from .csv")

        return data

density_histogram = DensityHistogram()
data = density_histogram.get_density()

# Create density histogram
plt.figure(figsize=(10, 6))
plt.hist(data, bins=30, alpha=0.7, color='lightblue', edgecolor='black')
plt.xlabel('Density (g/cm³)', fontsize = 15)
plt.ylabel('Frequency', fontsize = 15)
plt.title('Density Histogram From All Moisture Density Trials', fontsize = 18)
#plt.savefig(f'density_histogram.png, {date.today()}')
plt.show()