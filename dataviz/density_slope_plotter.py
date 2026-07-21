from datetime import date
from fileinput import filename
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os


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

    # ---------------------------------------------------------
    # SLOPE COMPUTATION
    # ---------------------------------------------------------

    def func(self, x, a):
        return a * x

    def compute_slopes(self):
        # initialize slope storage
        self.group_slopes = {
            "Airy": {f"Group{i}": [] for i in range(1, 6)},
            "Loose": {f"Group{i}": [] for i in range(1, 6)},
            "Moderate": {f"Group{i}": [] for i in range(1, 6)},
            "High": {f"Group{i}": [] for i in range(1, 6)},
            "Super": {f"Group{i}": [] for i in range(1, 6)}
        }

        for i, df in enumerate(self.curve_data):
            filename = self.filenames[i]
            category, group = self.parse_category_group(filename)

            if category and group:
                slope, _ = curve_fit(self.func, df['depth'], df['resistance'])
                self.group_slopes[category][group].append(slope[0])
        #print("SLOPES AFTER COMPUTE:", self.group_slopes)
    
    def get_moisture_level(self, filename):
        moisture_levels = ["Water2.5", "Water5", "Water7.5", "Water10", "Water15", "Water20", "Water30"]
        for moisture in moisture_levels:
            if moisture in filename:
                return moisture
        return None

    # ---------------------------------------------------------
    # DENSITY INPUT
    # ---------------------------------------------------------

    def get_density(self):
        self.group_densities = {
            "Airy": {},
            "Loose": {},
            "Moderate": {},
            "High": {},
            "Super" :{}
        }

        for category in ["Airy","Loose", "Moderate", "High", "Super"]:
            for i in range(1, 5):
                g = f"Group{i}"
                self.group_densities[category][g] = float(
                    input(f"Enter density for {category} {g}: ")
                )
        #print("DENSITIES:", self.group_densities)

    # ---------------------------------------------------------
    # BUILD PLOT DATA
    # ---------------------------------------------------------

    def build_plot_data(self):
        self.plot_data = []
        x_vals = np.linspace(0, 0.05, 100)

        for category in ["Airy","Loose", "Moderate", "High", "Super"]:
            for group in self.group_slopes[category]:
                slopes = self.group_slopes[category][group]
                if not slopes:
                    continue

                density = self.group_densities[category][group]
                color = (
                    self.plot_color1 if category == "Airy" else
                    self.plot_color2 if category == "Loose" else
                    self.plot_color3 if category == "Moderate" else
                    self.plot_color4 if category == "High" else
                    self.plot_color5
            )

                # Store each slope individually
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
        plt.xlabel('Density (g/cm^3)')
        plt.ylabel('Slope (N/m)')
        
        x = np.array([item["density"] for item in self.plot_data])
        y = np.array([item["slope"] for item in self.plot_data])

        xmin, xmax = np.min(x), np.max(x)
        ymin, ymax = np.min(y), np.max(y)

        plt.xlim(xmin - xmin*.1, xmax + xmax*.1)
        plt.ylim(ymin - ymin*.1, ymax + ymax*.1)

    def plot_variable(self, x, y, label, color):
        plt.scatter(x, y, label=label, color=color)
    
    def plot_all(self):
        print("Plotting curves...")

        # Compute slopes first
        self.compute_slopes()

        # Get densities
        self.get_density()

        # Get moisture levels
        for i in range(len(self.curve_data)):
            moisture_level = self.get_moisture_level(self.filenames[i])

        # Build plot data (now contains individual slopes)
        self.build_plot_data()

        # Now create the figure with dynamic bounds
        self.plot()

        # Scatter each slope individually
        seen = set()

        for item in self.plot_data:
            category = item["label"].split()[0]   # extract category name (airy, loose etc.)

            if category not in seen:
                plt.scatter(item["density"], item["slope"], color=item["color"], label=category)
                seen.add(category)
            else:
                plt.scatter(item["density"], item["slope"], color=item["color"])


    # ---------------------------------------------------------
    # BEST-FIT TRENDLINE THROUGH SCATTER POINTS
    # ---------------------------------------------------------

        densities = np.array([item["density"] for item in self.plot_data])
        slopes = np.array([item["slope"] for item in self.plot_data])

        # Read axis limits AFTER plotting
        x_min, x_max = plt.xlim()
        x_line = np.linspace(x_min, x_max, 200)

        # Fit quadratic constrained to pass through (0,0)
        # y = a*x^2 + b*x
        A = np.column_stack([densities**2, densities])
        coeffs, _, _, _ = np.linalg.lstsq(A, slopes, rcond=None)
        a, b = coeffs

        x_line = np.linspace(0, max(densities), 100)

        # Build trendline function
        y_line = a * x_line**2 + b * x_line


        plt.plot(x_line, y_line, linestyle='--', linewidth=2,
                color='black', label=f'Trendline: y = {a:.2f}x² + {b:.2f}x')

        plt.title(f'{moisture_level} Density vs Force Depth Slopes')
        plt.legend()
        plt.savefig(f'{self.plot_dst_folder_path}/{date.today().strftime("%b_%d_%Y")}_density_plot.png')
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
