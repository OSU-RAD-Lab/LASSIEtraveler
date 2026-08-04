from tkinter import filedialog
import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd

class MoistureSensor:
    def __init__(self):
        self.df = None

    def load_csv(self):
        # Create hidden root window for file dialog
        root = tk.Tk()
        root.withdraw()

        print("\nSelect your moisture CSV file...")
        csv_path = filedialog.askopenfilename(
            title="Select Moisture CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if not csv_path:
            raise FileNotFoundError("No CSV file selected.")

        # Load CSV
        self.df = pd.read_csv(csv_path)
        print("\nLoaded moisture CSV successfully.")

        return self.df


def plot_moisture_graph(df):
    plt.figure(figsize=(10, 6))

    # Unique moisture levels sorted
    moisture_levels = sorted(df["moisture"].unique())

    # Assign rainbow colors (repeat if needed)
    colors = ["#fde725", "#7ad151", "#22a884", "#2a788e", "#414487", "#440154"]

    # Build a lookup table: moisture → color
    color_map = {
        m: colors[i % len(colors)]
        for i, m in enumerate(moisture_levels)
    }

    # Scatter plot
    for m in moisture_levels:
        subset = df[df["moisture"] == m].sort_values("density")
        plt.scatter(
            subset["density"],
            subset["sensor_reading"],
            color=color_map[m],
            s=120,
            alpha=0.9,
            edgecolors="none"
        )

        # Draw line AFTER scatter so it sits on top
        plt.plot(
            subset["density"],
            subset["sensor_reading"],
            color=color_map[m],
            linewidth=3,
            alpha=0.9,
            label=f"Moisture {m}"
        )

    # Grid behind data
    ax = plt.gca()
    ax.set_axisbelow(True)
    plt.grid(True)

    plt.xlabel("Density", fontsize=18)
    plt.ylabel("Moisture Sensor Reading", fontsize=18)
    plt.title("Sensor Reading vs Density (Color-Coded Moisture Levels)", fontsize=20)

    plt.legend(title = "Moisture Level", fontsize = 15)
    plt.tight_layout()
    plt.show()

def main():
    sensor = MoistureSensor()
    df = sensor.load_csv()
    plot_moisture_graph(df)
if __name__ == "__main__":
    main()