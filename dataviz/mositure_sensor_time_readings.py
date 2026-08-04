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
    # Define compaction order to match your sketch
    compaction_order = ["Airy", "Loose", "Moderate", "High", "Super"]
    trial_order = ["T1", "T2"]

    # Create x-axis labels in correct order
    x_labels = []
    for c in compaction_order:
        for t in trial_order:
            x_labels.append(f"{c}-{t}")

    # Group by moisture level
    grouped = df.groupby("moisture")

    plt.figure(figsize=(12, 6))

    # Color map for lines
    colors = ["#fde725", "#7ad151", "#22a884", "#2a788e", "#414487", "#440154"]

    for (moisture, group), color in zip(grouped, colors):
        y = []
        for c in compaction_order:
            for t in trial_order:
                row = group[(group["compaction_level"] == c) &
                            (group["trial"] == t)]
                if not row.empty:
                    y.append(row["sensor_reading"].values[0])
                else:
                    y.append(None)

        x = range(len(x_labels))

        # Plot main line
        plt.plot(x, y, marker="o", label=f"{moisture}", color=color, linewidth=4)

    plt.xticks(range(len(x_labels)), x_labels, rotation=45, fontsize=15)
    plt.yticks(fontsize=15)
    plt.xlabel("Compaction Level + Trial", fontsize=18)
    plt.ylabel("Moisture Sensor Reading (Low reading = wetter sample)", fontsize=18)
    plt.title("Moisture Read vs. Time (Trials)", fontsize=20)
    plt.legend(title="Moisture Level", fontsize=15)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    sensor = MoistureSensor()
    df = sensor.load_csv()
    plot_moisture_graph(df)
if __name__ == "__main__":
    main()