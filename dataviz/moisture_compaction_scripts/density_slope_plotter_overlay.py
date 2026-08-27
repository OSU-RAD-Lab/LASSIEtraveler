from datetime import date
from fileinput import filename
from tokenize import group
from tokenize import group
from turtle import lt
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os


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

    # ---------------------------------------------------------
    # DATA LOADING + CLEANING
    # ---------------------------------------------------------

    def get_curve_data(self):
        for filename in os.listdir(self.data_src_folder_path):
            df0 = pd.read_csv(f"{self.data_src_folder_path}/{filename}")
            self.ground_height.append(float(df0['ground_height'].loc[0]) * 1/100)

            df = pd.read_csv(f"{self.data_src_folder_path}/{filename}", skiprows=2)
            df = df[['toeforce_y', 'toe_position_y']]
            df.columns = ["resistance", "depth"]

            self.curve_data.append(df)
            self.filenames.append(filename)

    def flip_curve_over_yaxis(self):
        self.curve_data = [
            df.assign(depth=-df['depth']) for df in self.curve_data
        ]

    def remove_points_after_max_depth(self):
        cleaned = []
        for df in self.curve_data:
            end_idx = df['depth'].idxmax()
            cleaned.append(df.loc[:end_idx])
        self.curve_data = cleaned

    def remove_points_before_min_depth(self):
        cleaned = []
        for df in self.curve_data:
            start_idx = df['depth'].idxmin()
            cleaned.append(df.loc[start_idx:])
        self.curve_data = cleaned

    def remove_data_prior_first_ground_contact(self):
        cleaned = []
        for i, df in enumerate(self.curve_data):
            gh = self.ground_height[i]
            df = df[df['depth'] >= gh]
            df = df.assign(depth=df['depth'] - df['depth'].min())
            cleaned.append(df)
        self.curve_data = cleaned

    def interpolate(self, num_points):
        new_list = []
        for df in self.curve_data:
            x_new = np.linspace(0, df['depth'].max(), num_points)
            y_new = np.interp(x_new, df['depth'], df['resistance'])
            new_list.append(pd.DataFrame({'depth': x_new, 'resistance': y_new}))
        self.curve_data = new_list

    # ---------------------------------------------------------
    # CATEGORY + GROUP PARSING
    # ---------------------------------------------------------

    def parse_compaction_group(self, filename):
        if "Airy" in filename:
            category = "Airy"
        elif "Loose" in filename:
            category = "Loose"
        elif "Moderate" in filename:
            category = "Moderate"
        elif "High" in filename:
            category = "High"
        elif "Super" in filename:
            category = "Super"
        else:
            return None, None

        for g in ["Group1", "Group2", "Group3", "Group4", "Group5"]:
            if g in filename:
                return category, g

        return category, None
    
    def parse_moisture_level(self, filename):
        moisture_levels = ["Water2.5", "Water5", "Water7.5", "Water10", "Water15", "Water20", "Water30"]
        for moisture in moisture_levels:
            if moisture in filename:
                return moisture
        return None

    # ---------------------------------------------------------
    # SLOPE COMPUTATION
    # ---------------------------------------------------------

    def func(self, x, a):
        return a * x

    def compute_slopes(self):
        # initialize slope storage
        moisture_levels = ["Water2.5", "Water5", "Water10", "Water15", "Water20", "Water30"]
        compaction_levels = ["Airy", "Loose", "Moderate", "High", "Super"]
        groups = [f"Group{i}" for i in range(1, 6)]

        self.group_slopes = {
            moisture: {
                compaction: {group: [] for group in groups}
                for compaction in compaction_levels
            }
            for moisture in moisture_levels
        }

        for i, df in enumerate(self.curve_data):
            filename = self.filenames[i]
            
            moisture = self.parse_moisture_level(filename)
            compaction, group = self.parse_compaction_group(filename)

            # Skip files missing moisture or compaction/group info
            if not moisture or not compaction or not group:
                continue

            # Fit slope
            slope, _ = curve_fit(self.func, df['depth'], df['resistance'])

            # Store slope under correct moisture + compaction + group
            self.group_slopes[moisture][compaction][group].append(slope[0])
    
    # ---------------------------------------------------------
    # DENSITY INPUT
    # ---------------------------------------------------------

    def get_density(self):
        import tkinter as tk
        from tkinter import filedialog
        import pandas as pd

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
            moisture = row["moisture"]
            compaction = row["compaction"]
            group = row["group"]
            density = float(row["bulk_density"])

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
        x_vals = np.linspace(0, 0.05, 100)

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
                        self.plot_color1 if moisture_level == "Water2.5" else
                        self.plot_color2 if moisture_level == "Water5" else
                        self.plot_color3 if moisture_level == "Water10" else
                        self.plot_color4 if moisture_level == "Water15" else
                        self.plot_color5 if moisture_level == "Water20" else
                        self.plot_color6 if moisture_level == "Water30" else
                        'black'
                    )

                    # Store each slope individually
                    for slope in slopes:
                        self.plot_data.append({
                            "moisture_level": moisture_level,
                            "density": density,
                            "slope": slope,
                            "label": f"{moisture_level} {compaction_level} {group} (slope={slope:.2f} N/m)",
                            "color": color
                        })

    # ---------------------------------------------------------
    # PLOTTING
    # ---------------------------------------------------------

    def plot(self):
        plt.figure(figsize=(15,15))
        plt.xlabel('Bulk Density (g/cm^3)', fontsize=30)
        plt.ylabel('Soil Strength (N/m)', fontsize=30)

        x = np.array([item["density"] for item in self.plot_data])
        y = np.array([item["slope"] for item in self.plot_data])

        xmin, xmax = np.min(x), np.max(x)
        ymin, ymax = np.min(y), np.max(y)

        plt.xlim(xmin - xmin*.01, xmax + xmax*.01)
        plt.ylim(ymin - ymin*.1, ymax + ymax*.1)

        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)

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
            plt.scatter(
            item["density"],
            item["slope"],
            color=item["color"],   # moisture-level color
            s=100, # size of the point
            alpha=0.9
        )


# ---------------------------------------------------------
# TRENDLINES PER MOISTURE LEVEL
# ---------------------------------------------------------
        
        moisture_groups = {}

        for item in self.plot_data:
            m = item["moisture_level"]
            if m not in moisture_groups:
                moisture_groups[m] = {"densities": [], "slopes": [], "color": item["color"]}
            moisture_groups[m]["densities"].append(item["density"])
            moisture_groups[m]["slopes"].append(item["slope"])

        for moisture, data in moisture_groups.items():
            densities = np.array(data["densities"])
            slopes = np.array(data["slopes"])
            color = data["color"]

            # Standard linear fit: y = m x + c
            m, c = np.polyfit(densities, slopes, 1)

            x_line = np.linspace(0, max(densities), 200)
            y_line = m * x_line + c
            
            # Plot trendline (solid, full color)
            plt.plot(
                x_line, y_line,
                color=color,
                linewidth=7,
                label=f"{moisture}% Trendline: y = {m:.2f}x + {c:.2f}"
            )

        plt.title(f'Soil Strength Trendlines Vs. Bulk Density', fontsize=40)
        plt.legend(fontsize=20)
        plt.savefig(f'{self.plot_dst_folder_path}/{date.today().strftime("%b_%d_%Y")}_density_overlay_plot.png')
        plt.show()

def main():
        if len(sys.argv) != 9:
            print("incorrect number of arguments given")
            print("incorrect number of arguments given")
            print("python density_plotter.py data_src_folder plot_dst_folder color1 color2 color3 color4 color5 color6")
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
