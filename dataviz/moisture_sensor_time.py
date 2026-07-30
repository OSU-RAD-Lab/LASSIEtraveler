from datetime import date
from fileinput import filename
from math import erf
from tokenize import group
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, leastsq
import os
from scipy.special import erf
from scipy.interpolate import UnivariateSpline
import tkinter as tk
from tkinter import filedialog



class Curves:

    def __init__(self, data_src_folder_path, plot_dst_folder_path, plot_color1='grey', plot_color2='grey', plot_color3='grey', plot_color4='grey', plot_color5='grey', plot_color6='grey'):
        self.data_src_folder_path = data_src_folder_path
        self.plot_dst_folder_path = plot_dst_folder_path
        self.plot_color1 = plot_color1
        self.plot_color2 = plot_color2
        self.plot_color3 = plot_color3
        self.plot_color4 = plot_color4
        self.plot_color5 = plot_color5
        self.plot_color6 = plot_color6

        self.filenames = []
        self.curve_data = []
        self.ground_height = []
        self.force_zero_trendline = True  # default to forcing trendline through origin

        self.group_slopes = {}
        self.group_densities = {}
        self.group_moisture_levels = {}
        self.plot_data = []

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

        # Fill dictionary from CSV
        for _, row in df.iterrows():
            moisture_str = row["moisture"]
            moisture = float(moisture_str.replace("%", ""))
            compaction = row["compaction"]
            group = row["group"]
            density = float(row["density"])

            # Create moisture level if missing
            if moisture not in self.group_densities:
                self.group_densities[moisture] = {}

            # Create compaction level if missing
            if compaction not in self.group_densities[moisture]:
                self.group_densities[moisture][compaction] = {}
            
            self.group_densities[moisture][compaction][group] = density
            
        print("\nLoaded density values from .csv")

    # ---------------------------------------------------------
    # BUILD PLOT DATA
    # ---------------------------------------------------------

    def build_plot_data(self):
        self.plot_data = []
        x_vals = np.linspace(0, 40, 100)

        for moisture_level in self.group_slopes:
            for compaction_level in self.group_slopes[moisture_level]:
                for group in self.group_slopes[moisture_level][compaction_level]:
                    slopes = self.group_slopes[moisture_level][compaction_level][group]
                    if not slopes:
                        continue

                    # Skip if density missing
                    if (moisture_level not in self.group_densities or
                        compaction_level not in self.group_densities[moisture_level] or
                        group not in self.group_densities[moisture_level][compaction_level]):
                            continue

                    density = self.group_densities[moisture_level][compaction_level][group]
                    color = (
                        self.plot_color1 if compaction_level == "Airy" else
                        self.plot_color2 if compaction_level == "Loose" else
                        self.plot_color3 if compaction_level == "Moderate" else
                        self.plot_color4 if compaction_level == "High" else
                        self.plot_color5 if compaction_level == "Super" else
                        'black'
                    )

                    # Store each slope individually
                    for slope in slopes:
                        self.plot_data.append({
                            "moisture_level": moisture_level,
                            "density": density,
                            "slope": slope,
                            "compaction" : compaction_level,
                            "label": f"{moisture_level} {compaction_level} {group} (slope={slope:.2f} N/m)",
                            "color": color
                        })

    # ---------------------------------------------------------
    # PLOTTING
    # ---------------------------------------------------------

    def plot(self):
        plt.figure(figsize=(10, 10))
        plt.xlabel('Moisture Level (%)', fontsize=15)
        plt.ylabel('Slope (N/m)', fontsize=15)

        x = np.array([item["moisture_level"] for item in self.plot_data])
        y = np.array([item["slope"] for item in self.plot_data])

        ymin, ymax = np.min(y), np.max(y)

        plt.xlim(0,40)
        plt.ylim(ymin - ymin*.1, ymax + ymax*.1)

        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)

    def plot_variable(self, x, y, label, color):
        plt.scatter(x, y, label=label, color=color)
    
    def plot_all(self):
        print("Plotting curves...")

        # Compute slopes first
        self.compute_slopes()

        # Get densities
        self.get_density()

        # Get moisture levels
        #for i in range(len(self.curve_data)):
            #moisture_level = self.get_moisture_level(self.filenames[i])

        # Build plot data (now contains individual slopes)
        self.build_plot_data()

        # Now create the figure with dynamic bounds
        self.plot()

        # Scatter each slope individually
        seen = set()

        for item in self.plot_data:
            jitter = np.random.uniform(-0.4, 0.4)
            plt.scatter(
            item["moisture_level"]+jitter,
            item["slope"],
            color=item["color"],   # moisture-level color
            s=40,
            alpha=0.9
        )
            
        compaction_colors = {
            "Airy": self.plot_color1,
            "Loose": self.plot_color2,
            "Moderate": self.plot_color3,
            "High": self.plot_color4,
            "Super": self.plot_color5
        }

        for comp, col in compaction_colors.items():
            plt.scatter([],[],color=col)

        plt.legend(title = "Compaction Level", fontsize=12)

        # ---------------------------------------------------------
        # TRENDLINES PER COMPACTION LEVEL
        # ---------------------------------------------------------

        compaction_groups = {}

        for item in self.plot_data:
            compaction = item["compaction"]
            color = item["color"]

            if compaction not in compaction_groups:
                compaction_groups[compaction] = {"moisture": [], "slope": [], "color": color}

            compaction_groups[compaction]["moisture"].append(item["moisture_level"])
            compaction_groups[compaction]["slope"].append(item["slope"])

        for compaction, data in compaction_groups.items():
            x_vals = np.array(data["moisture"])
            y_vals = np.array(data["slope"])
            color = data["color"]

            moisture_unique = {}
            for x,y in zip(x_vals, y_vals):
                moisture_unique.setdefault(x, []).append(y)

            x_clean = np.array(sorted(moisture_unique.keys()))
            y_clean = np.array([np.mean(moisture_unique[x]) for x in x_clean])

            initials = [max(y_clean), np.mean(x_clean), np.std(x_clean),0]

            params, _ = leastsq(self.residuals, initials, args=(y_clean, x_clean))

            spread_threshold = np.std(x_clean) * 0.15

            is_monotonic = np.all(np.diff(y_clean) <= 0) or np.all(np.diff(y_clean) >= 0)
            
            if is_monotonic:
                use_gaussian = False
            else:
                use_gaussian = True

            spread_too_small = params[2] < (np.std(x_clean) * 0.15)
            center_outside_range = (params[1] < x_clean.min()) or (params[1] > x_clean.max())
            amplitude_unrealistic = params[0] > (max(y_clean) *3)

            reject_gaussian = spread_too_small or center_outside_range or amplitude_unrealistic

            if is_monotonic or reject_gaussian:
                spline = UnivariateSpline(x_clean, y_clean, s=np.var(y_clean) * .5)
                x_line = np.linspace(x_clean.min(), x_clean.max(), 300)
                y_line = spline(x_line)

            else:
                x_line = np.linspace(x_clean.min(), x_clean.max(), 300)
                y_line = self.asymGaussian(x_line, params)

            # Plot spline curve
            plt.plot(
                x_line, y_line,
                color=color,
                linewidth=4,
                label=f"{compaction} trendline"
            )

        plt.title(f'Overlayed Moisture Level vs Force Depth Trendlines', fontsize=18)
        plt.legend(fontsize=12)
        plt.savefig(f'{self.plot_dst_folder_path}/{date.today().strftime("%b_%d_%Y")}_moisture_overlay_plot.png')
        plt.show()

def main():
        if len(sys.argv) != 9:
            print("incorrect number of arguments given")
            print("incorrect number of arguments given")
            print("python moisture_slope_plotter.py data_src_folder plot_dst_folder color1 color2 color3 color4 color5 color6")
            sys.exit()

        curves = Curves(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])

        curves.get_curve_data()
        curves.flip_curve_over_yaxis()
        curves.remove_points_after_max_depth()
        curves.remove_points_before_min_depth()
        curves.remove_data_prior_first_ground_contact()
        curves.interpolate(500)
        curves.force_zero_trendline = False # or True


        curves.plot_all()


if __name__ == "__main__":
    main()
