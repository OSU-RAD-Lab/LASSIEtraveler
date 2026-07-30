from datetime import date
from fileinput import filename
from math import erf
from tokenize import group
from matplotlib import cm, colors
from matplotlib.pylab import norm
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, leastsq
import os
import plotly.express as px
from textwrap import wrap
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap


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
        moisture_levels = ["Water2.5", "Water5", "Water10", "Water15", "Water20", "Water30"]
        for moisture in moisture_levels:
            if moisture in filename:
                #replace Water2.5 to 2.5
                moisture = float(moisture.replace("Water", ""))
                return moisture
        return None

    # ---------------------------------------------------------
    # SLOPE COMPUTATION
    # ---------------------------------------------------------

    def func(self, x, a):
        return a * x

    def compute_slopes(self):
        # initialize slope storage
        moisture_levels = [2.5, 5, 10, 15, 20, 30]
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
            moisture_str = row["moisture"]
            moisture = float(moisture_str.replace("Water", ""))
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

        all_densities = [
            self.group_densities[m][c][g]
            for m in self.group_densities
            for c in self.group_densities[m]
            for g in self.group_densities[m][c]
        ]

        dmin, dmax = min(all_densities), max(all_densities)

        self.dmin = dmin
        self.dmax = dmax

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

                    norm_density = (density - self.dmin) / (self.dmax - self.dmin) if self.dmax != self.dmin else 0
                    grey_color = plt.cm.Greys(norm_density)  # darker = higher density

                    # Store each slope individually
                    for slope in slopes:
                        self.plot_data.append({
                            "moisture_level": moisture_level,
                            "density": density,
                            "slope": slope,
                            "compaction" : compaction_level,
                            "label": f"{moisture_level} {compaction_level} {group} (slope={slope:.2f} N/m)",
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

        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)

        cividis_r = plt.cm.get_cmap("cividis_r")

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

        norm = colors.Normalize(vmin=self.dmin, vmax=self.dmax)
        cmap = plt.cm.Greys

        colors_array = cmap(np.linspace(0.2, 1.0, 256))  # shift bottom up to 20% brightness
        darker_light_cmap = colors.LinearSegmentedColormap.from_list("darker_light_greys", colors_array)

        scatter_points = []

        for item in self.plot_data:
            jitter = np.random.uniform(-0.2, 0.2)
            sc = plt.scatter(
            item["moisture_level"] + jitter,
            item["slope"],
            c=item["density"],
            cmap=darker_light_cmap,
            norm=norm,   # moisture-level color
            s=40,
            alpha=0.9
        )
        scatter_points.append(sc)

        cbar = plt.colorbar(scatter_points[-1])
        cbar.set_label("Density (g/cm³)", fontsize=15)

        
        # Compaction legend colors
        compaction_colors = {
            "Airy": self.plot_color1,
            "Loose": self.plot_color2,
            "Moderate": self.plot_color3,
            "High": self.plot_color4,
            "Super": self.plot_color5
        }
        
        for comp, col in compaction_colors.items():
            plt.scatter([],[],color=col)

        plt.legend(title = "Compaction Level", fontsize=15)
        plt.title(f'Overlayed Moisture Level vs Force Depth Trendlines', fontsize=20)
        plt.legend(fontsize=15)
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
