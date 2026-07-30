from datetime import date
from fileinput import filename
import re
from secrets import choice
from tokenize import group
from matplotlib import category
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit, root
import os
import tkinter as tk
from tkinter import filedialog



class Curves:

    def __init__(self, data_src_folder_path, plot_dst_folder_path, plot_color1='grey', plot_color2='grey', plot_color3='grey', plot_color4='grey', plot_color5='grey'):
        self.data_src_folder_path = data_src_folder_path
        self.plot_dst_folder_path = plot_dst_folder_path
        self.plot_color1 = plot_color1
        self.plot_color2 = plot_color2
        self.plot_color3 = plot_color3
        self.plot_color4 = plot_color4
        self.plot_color5 = plot_color5

        self.filenames = []
        self.curve_data = []
        self.ground_height = []
        self.force_zero_trendline = True  # default to forcing trendline through origin

        self.group_slopes = {}
        self.group_densities = {}
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

    def parse_category_group(self, filename):
        filename_lower = filename.lower()

        categories = {
            "airy": "Airy",
            "loose": "Loose",
            "moderate": "Moderate",
            "high": "High",
            "super": "Super"
        }

        category = None
        for key, proper in categories.items():
            if key in filename_lower:   # works for AiryCompaction, LooseSoil, etc.
                category = proper
                break

        group = None
        for i in range(1, 4):
            if f"group{i}".lower() in filename_lower:
                group = f"Group{i}"
                break

        return category, group
    
    # ---------------------------------------------------------
    # SLOPE COMPUTATION
    # ---------------------------------------------------------

    def func(self, x, a):
        return a * x

    def compute_slopes(self):
        # initialize slope storage
        self.group_slopes = {
            "Airy": {f"Group{i}": [] for i in range(1, 4)},
            "Loose": {f"Group{i}": [] for i in range(1, 4)},
            "Moderate": {f"Group{i}": [] for i in range(1, 4)},
            "High": {f"Group{i}": [] for i in range(1, 4)},
            "Super": {f"Group{i}": [] for i in range(1, 4)}
        }

        for i, df in enumerate(self.curve_data):
            filename = self.filenames[i]

            # moisture filter based on filename
            file_moisture = self.get_moisture_from_filename(filename)
            if file_moisture != self.selected_moisture:
                continue

            category, group = self.parse_category_group(filename)

            if category and group:
                slope, _ = curve_fit(self.func, df['depth'], df['resistance'])
                self.group_slopes[category][group].append(slope[0])
        #print("SLOPES AFTER COMPUTE:", self.group_slopes)
    
    def get_density(self):
        root = tk.Tk()
        root.withdraw()

        print("\nSelect your density CSV file...")
        csv_path = filedialog.askopenfilename(
            title="Select Density CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if not csv_path:
            raise FileNotFoundError("No CSV file selected.")

        df = pd.read_csv(csv_path)

        self.group_densities = {}

        for _, row in df.iterrows():
            moisture = row["moisture"]
            compaction = row["compaction"]
            group = row["group"]
            density = float(row["density"])

            if moisture not in self.group_densities:
                self.group_densities[moisture] = {}

            if compaction not in self.group_densities[moisture]:
                self.group_densities[moisture][compaction] = {}

            self.group_densities[moisture][compaction][group] = density

        print("\nLoaded density values from .csv")

    import re

    def get_moisture_from_filename(self, filename):
        """
        Find 'WaterX' (e.g., Water2.5, Water5) anywhere in the filename.
        """
        match = re.search(r"Water[\d\.]+", filename)
        if match:
            return match.group(0)
        return None


    def choose_moisture_level(self):
        root = tk.Tk()
        root.withdraw()

        print("\nSelect moisture level for density mapping:")
        moisture_levels = list(self.group_densities.keys())

        # Simple popup selection
        import tkinter.simpledialog as sd
        choice = sd.askstring(
            "Moisture Level",
            f"Available moisture levels:\n{', '.join(moisture_levels)}\n\nType one:"
        )

        if choice not in moisture_levels:
            raise ValueError(f"Invalid moisture level: {choice}")

        self.selected_moisture = choice
        print(f"Using moisture level: {choice}")

    def filter_slopes_by_moisture(self, moisture):
        """
        Keep only slopes whose (category, group) exist in the selected moisture
        section of the density CSV. Filenames do NOT determine moisture.
        """

        # Density dictionary for the selected moisture
        if moisture not in self.group_densities:
            print(f"No density data for moisture {moisture}")
            return

        valid_categories = self.group_densities[moisture]

        for category in self.group_slopes:
            for group in list(self.group_slopes[category].keys()):

                # If this category does not exist in the density CSV for this moisture → remove
                if category not in valid_categories:
                    print(f"Removing slopes for {category} {group} (category not in density CSV for {moisture})")
                    self.group_slopes[category][group] = []
                    continue

                # If this group does not exist in the density CSV for this moisture → remove
                if group not in valid_categories[category]:
                    print(f"Removing slopes for {category} {group} (group not in density CSV for {moisture})")
                    self.group_slopes[category][group] = []
                    continue

    # ---------------------------------------------------------
    # BUILD PLOT DATA
    # ---------------------------------------------------------

    def build_plot_data(self):
        self.plot_data = []

        for category in ["Airy","Loose","Moderate","High","Super"]:
            for group, slopes in self.group_slopes[category].items():
                if not slopes:
                    continue

                # Check moisture exists
                if self.selected_moisture not in self.group_densities:
                    print(f"No density data for moisture {self.selected_moisture}")
                    continue

                # Check category exists
                if category not in self.group_densities[self.selected_moisture]:
                    print(f"Skipping {category} — no density category found.")
                    continue

                # Check group exists
                if group not in self.group_densities[self.selected_moisture][category]:
                    print(f"Skipping {category} {group} — no density value found.")
                    continue

                density = self.group_densities[self.selected_moisture][category][group]

                color = (
                    self.plot_color1 if category == "Airy" else
                    self.plot_color2 if category == "Loose" else
                    self.plot_color3 if category == "Moderate" else
                    self.plot_color4 if category == "High" else
                    self.plot_color5 if category == "Super" else
                    'black'
                )

                for slope in slopes:
                    self.plot_data.append({
                        "density": density,
                        "slope": slope,
                        "label": f"{category} {group} (slope={slope:.2f} N/m)",
                        "color": color
                    })

    # ---------------------------------------------------------
    # PLOTTING
    # ---------------------------------------------------------

    def plot(self):
        plt.figure(figsize=(10, 10))
        plt.xlabel('Density (g/cm^3)', fontsize=18)
        plt.ylabel('Slope (N/m)', fontsize=18)

        ### Unhash if you want adaptive bounds ###
        #x = np.array([item["density"] for item in self.plot_data])
        #y = np.array([item["slope"] for item in self.plot_data])

        #xmin, xmax = np.min(x), np.max(x)
        #ymin, ymax = np.min(y), np.max(y)

        #plt.xlim(xmin - xmin*.1, xmax + xmax*.1)
        #plt.ylim(ymin - ymin*.1, ymax + ymax*.1)

        plt.xlim(1.2, 1.9)
        plt.ylim(0, 900)

        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)

    def plot_variable(self, x, y, label, color):
        plt.scatter(x, y, label=label, color=color)
    
    def plot_all(self):
        print("Plotting curves...")

        # Get densities
        self.get_density()

        self.choose_moisture_level()

        # Compute slopes first
        self.compute_slopes()

        self.filter_slopes_by_moisture(self.selected_moisture)

        # Build plot data (now contains individual slopes)
        self.build_plot_data()

        # Now create the figure with dynamic bounds
        self.plot()

        # Scatter each slope individually
        seen = set()

        for item in self.plot_data:
            plt.scatter(item["density"], item["slope"], color=item["color"])

    # ---------------------------------------------------------
    # BEST-FIT TRENDLINE THROUGH SCATTER POINTS
    # ---------------------------------------------------------

        densities = np.array([item["density"] for item in self.plot_data])
        slopes = np.array([item["slope"] for item in self.plot_data])

        # Read axis limits AFTER plotting
        x_min, x_max = plt.xlim()
        #x_line = np.linspace(x_min, x_max, 200)
        x_line = np.linspace(1.2, 1.9, 200)

        # Fit quadratic constrained to pass through (0,0)
        # y = a*x^2 + b*x
        A = np.column_stack([densities**2, densities])
        coeffs, _, _, _ = np.linalg.lstsq(A, slopes, rcond=None)
        a, b = coeffs

        #x_line = np.linspace(0, max(densities), 100)
        x_line = np.linspace(1.2, 1.9, 200)

        # Build trendline function
        y_line = a * x_line**2 + b * x_line


        plt.plot(x_line, y_line, linestyle='--', linewidth=2,
                color='black', label=f'Trendline: y = {a:.2f}x² + {b:.2f}x')

        plt.title(f'{self.selected_moisture} Density vs Force Depth Slopes', fontsize=20)
        import matplotlib.patches as mpatches

        category_colors = {
            "Airy": self.plot_color1,
            "Loose": self.plot_color2,
            "Moderate": self.plot_color3,
            "High": self.plot_color4,
            "Super": self.plot_color5
        }

        handles = []

        # Add category handles only if that category appears in plot_data
        present_categories = {item["label"].split()[0] for item in self.plot_data}

        for cat, col in category_colors.items():
            if cat in present_categories:
                handles.append(mpatches.Patch(color=col, label=cat))

        # Add trendline handle
        trendline_handle = plt.Line2D([], [], linestyle='--', linewidth=2,
                                    color='black',
                                    label=f'Trendline: y = {a:.2f}x² + {b:.2f}x')

        handles.insert(0, trendline_handle)

        plt.legend(handles=handles, fontsize=14)
        plt.savefig(f'{self.plot_dst_folder_path}/{date.today().strftime("%b_%d_%Y")}_{self.selected_moisture}_density_plot.png')
        plt.show()

def main():
        if len(sys.argv) != 8:
            print("incorrect number of arguments given")
            print("python density_plotter.py data_src_folder plot_dst_folder color1 color2 color3 color4")
            sys.exit()

        curves = Curves(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])

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
