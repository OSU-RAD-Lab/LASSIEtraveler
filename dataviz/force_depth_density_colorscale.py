
from datetime import date
from tokenize import group
from unicodedata import category
from matplotlib.pylab import norm
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
import plotly.express as px
from textwrap import wrap
import matplotlib as mpl

class Curves:

    def __init__(self, data_src_folder_path:str, plot_dst_folder_path:str, plot_color:str = 'black'):
        self.data_src_folder_path = data_src_folder_path
        self.plot_dst_folder_path = plot_dst_folder_path
        self.plot_color = plot_color
        self.filenames= []
        self.curve_data = []
        self.ground_height = []
        self.group_densities = {}


    def get_curve_data(self):
        for filename in os.listdir(self.data_src_folder_path):

            df = pd.read_csv(f"{self.data_src_folder_path}/{filename}")
            self.ground_height.append(float(df['ground_height'].loc[0]) * 1/100)

            df = pd.read_csv(f"{self.data_src_folder_path}/{filename}", skiprows=2)
            df = df[['toeforce_y', 'toe_position_y']] # takes just the two important columns
            df.columns = ["resistance", "depth"] # rename columns
            self.curve_data.append(df)
            self.filenames.append(filename)
    
    def flip_curve_over_yaxis(self):
        cleaned_df_list = []
        for df in self.curve_data:
            copy_df = df.copy()
            copy_df['depth'] = -copy_df['depth']
            cleaned_df_list.append(copy_df)
        self.curve_data = cleaned_df_list

    def remove_points_after_max_depth(self):
        cleaned_list = []
        for i, df in enumerate(self.curve_data):
            end_idx = df[df["depth"] == df["depth"].max()].index[0]
            cleaned_df = df.iloc[:end_idx+1]
            cleaned_list.append(cleaned_df)
        self.curve_data = cleaned_list
    
    def remove_points_before_min_depth(self):
        cleaned_list = []
        for i, df in enumerate(self.curve_data):
            min_idx = df[df["depth"] == df["depth"].min()].index[0]
            cleaned_df = df.iloc[min_idx:]
            cleaned_list.append(cleaned_df)
        self.curve_data = cleaned_list

    def remove_data_prior_first_ground_contact(self):
        cleaned_list = []
        for i in range(len(self.curve_data)):
            df = self.curve_data[i]
            if df['depth'].iloc[0] < self.ground_height[i]:
                df = df[df['depth'] >= self.ground_height[i]]
            cleaned_list.append(df)
            df.loc[:,'depth'] = df['depth'] - df['depth'].min()
        self.curve_data = cleaned_list

    def interpolate(self, num_points):
        interp_df_list = []
        for df in self.curve_data:
            x_intervals = np.linspace(0, df['depth'].max(), num_points, endpoint=True) # 100 points between 0 and trunc_level
            y_new = np.interp(x_intervals, df["depth"], df["resistance"])
            new_df = pd.DataFrame({'depth': x_intervals, 'resistance': y_new})
            interp_df_list.append(new_df)
        self.curve_data = interp_df_list


    def func(self, x, a):
        return a * x
    
    def parse_filename(self, filename):
        categories = ["Airy", "Loose", "Moderate", "High", "Super"]
        groups = ["Group1", "Group2", "Group3", "Group4"]
        moisture_levels = ["Water2.5", "Water5", "Water7.5", "Water10", "Water15", "Water20", "Water30"]

        category = None
        group = None
        moisture_level = None

        for cat in categories:
            if cat in filename:
                category = cat
                break

        for g in groups:
            if g in filename:
                group = g
                break

        for m in moisture_levels:
            if m in filename:
                moisture_level = m
                break

        if category is None or group is None:
            raise ValueError(f"Could not parse category/group from filename: {filename}")

        return category, group, moisture_level

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
        print("DENSITIES:", self.group_densities)


    def get_global_axis_bounds(self):
        all_depths = []
        all_resistances = []

        for df in self.curve_data:
            all_depths.extend(df["depth"])
            all_resistances.extend(df["resistance"])

        return (0, 0.05), (0, max(all_resistances)*1.1)

    def plot_combined(self):
        # Extract category + group from filename
        for i in range(len(self.curve_data)):
            category, group, moisture_level = self.parse_filename(self.filenames[i])

        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_xlabel('Depth (m)')
        ax.set_ylabel('Resistance (N)')
        ax.set_title(f"{moisture_level}% Force Depth Curves Colored by Density with Nonlinear Trendlines")
        # Continuous Cividis colormap
        cividis_r = plt.cm.get_cmap("cividis_r")

        # Collect all densities to normalize color scale
        all_densities = [
            self.group_densities[cat][grp]
            for cat in self.group_densities
            for grp in self.group_densities[cat]
        ]
        
        min_density = min(all_densities)
        max_density = max(all_densities)

        # For axis bounds
        all_depths = []
        all_resistances = []

        # Plot each curve + nonlinear trendline
        for i in range(len(self.curve_data)):
            df = self.curve_data[i]
            depth = df["depth"]
            resist = df["resistance"]

            category, group, moisture_level = self.parse_filename(self.filenames[i])

            # Track for axis bounds
            all_depths.extend(depth)
            all_resistances.extend(resist)

            # making higher and lower bounds for the color scale
            expanded_min = 1.005 * min_density
            expanded_max = 1.005 * max_density

            # Density → normalized → Cividis color
            density = self.group_densities[category][group]
            norm_density = (density - expanded_min) / (expanded_max - expanded_min)
            norm_density = np.clip(norm_density, 0, 1)  # Ensure within [0, 1]
            color = cividis_r(norm_density)

            # Plot raw curve
            ax.plot(depth, resist, color=color, linewidth=2, alpha=0.8)

            # Fit quadratic constrained to pass through (0,0)
            # y = a*x^2 + b*x
            A = np.column_stack([depth**2, depth])
            coeffs, _, _, _ = np.linalg.lstsq(A, resist, rcond=None)
            a, b = coeffs

            x_line = np.linspace(0, max(depth), 100)

            # Build trendline function
            y_line = a * x_line**2 + b * x_line


            ax.plot(x_line, y_line, linestyle='--', linewidth=2,
                color='black')

        # AXIS BOUNDS START AT ZERO + BUFFER
        x_bounds, y_bounds = self.get_global_axis_bounds()
        ax.set_xlim(x_bounds)
        ax.set_ylim(y_bounds)

        # ---- LEGEND WITH INPUTTED DENSITIES ----
        legend_entries = []
        for category in self.group_densities:
            text = f"{category}: " + ", ".join(
                f"{group}={self.group_densities[category][group]} (g/cm^3)" 
                for group in self.group_densities[category]
            )
            legend_entries.append(text)

        # Invisible handles (so legend shows only text)
        handles = [plt.Line2D([], [], color='white') for _ in legend_entries]
        ax.legend(handles, legend_entries, fontsize=9, loc='upper right', frameon=True)

        # ---- SINGLE COLORBAR PER FIGURE ----
        norm = mpl.colors.Normalize(vmin=expanded_min, vmax=expanded_max)
        cmap = plt.cm.get_cmap("cividis_r")
        sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])

        cbar = fig.colorbar(sm, ax=ax, ticks=np.linspace(expanded_min, expanded_max, 10))
        cbar.set_label("Density (g/cm^3)", fontsize=12)

        save_path = f'{self.plot_dst_folder_path}/ALL_CURVES_{date.today().strftime("%b_%d_%Y")}_{moisture_level}.png'
        fig.savefig(save_path)
        print(f"Saved combined plot to: {save_path}")
        plt.show()

    def plot_indiviual_groups(self):

        # Extract moisture level from filename
        _, _, moisture_level = self.parse_filename(self.filenames[0])

        for category in self.group_densities:
            for group in self.group_densities[category]:
                
                fig, ax = plt.subplots(figsize=(12, 10))

                ax.set_xlabel('Depth (m)')
                ax.set_ylabel('Resistance (N)')
                ax.set_title(f"{moisture_level}% {category} {group} -Force Depth Curve Colored by Density with Nonlinear Trendline")
                # Continuous Cividis colormap
                cividis_r = plt.cm.get_cmap("cividis_r")

                # Collect all densities to normalize color scale
                all_densities = [
                    self.group_densities[cat][grp]
                    for cat in self.group_densities
                    for grp in self.group_densities[cat]
                ]
        
                min_density = min(all_densities)
                max_density = max(all_densities)

                # making higher and lower bounds for the color scale
                expanded_min = 1.005 * min_density
                expanded_max = 1.005 * max_density

                # For axis bounds
                all_depths = []
                all_resistances = []

                trendline_equations = []

                # Plot each curve + nonlinear trendline
                for i in range(len(self.curve_data)):
                    cat_i, group_1, moisture_level = self.parse_filename(self.filenames[i])

                    if cat_i != category or group_1 != group:
                        continue  # Skip this curve if it doesn't match the current category and group

                    df = self.curve_data[i]
                    depth = df["depth"]
                    resist = df["resistance"]

                    # Track for axis bounds
                    all_depths.extend(depth)
                    all_resistances.extend(resist)

                    # Density → normalized → Cividis color
                    density = self.group_densities[category][group]
                    norm_density = (density - expanded_min) / (expanded_max - expanded_min)
                    norm_density = np.clip(norm_density, 0, 1)  # Ensure within [0, 1]
                    color = cividis_r(norm_density)

                    # Plot raw curve
                    ax.plot(depth, resist, color=color, linewidth=2, alpha=0.8)

                    # Fit quadratic constrained to pass through (0,0)
                    # y = a*x^2 + b*x
                    A = np.column_stack([depth**2, depth])
                    coeffs, _, _, _ = np.linalg.lstsq(A, resist, rcond=None)
                    a, b = coeffs

                    x_line = np.linspace(0, max(depth), 100)

                    # Build trendline function
                    y_line = a * x_line**2 + b * x_line

                    ax.plot(x_line, y_line, linestyle='--', linewidth=2,
                        color='black')

                    equation_text = f"y = {a:.4f}x² + {b:.4f}x"
                    trendline_equations.append(equation_text)

                if len(all_resistances) == 0:
                    print(f"No curves found for {category} / {group}, skipping plot.")
                    plt.close(fig)
                    continue

                # AXIS BOUNDS START AT ZERO + BUFFER
                bounds_x, bounds_y = self.get_global_axis_bounds()
                ax.set_xlim(bounds_x)
                ax.set_ylim(bounds_y)

                density_val = self.group_densities[category][group]

                legend_lines = [f"{category} {group}: density={density_val} g/cm³"] + [
                    f"Trendline {idx+1}: {eq}" for idx, eq in enumerate(trendline_equations)
                ]

                handles = [plt.Line2D([], [], color='white') for _ in legend_lines]
                ax.legend(handles, legend_lines, fontsize=10, loc='upper right', frameon=True)

                norm = mpl.colors.Normalize(vmin=expanded_min, vmax=expanded_max)
                cmap = plt.cm.get_cmap("cividis_r")

                sm = mpl.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])

                cbar = fig.colorbar(sm, ax=ax, ticks=np.linspace(expanded_min, expanded_max, 10))
                cbar.set_label("Density (g/cm^3)", fontsize=12)

                save_path = (
                    f"{self.plot_dst_folder_path}/INDIVIDUAL_CURVE_"
                    f"{category}_{group}_{moisture_level}_"
                    f"{date.today().strftime('%b_%d_%Y')}.png"
                )
                fig.savefig(save_path)
                print(f"Saved individual plot to: {save_path}")

def main():
    if len(sys.argv) != 4:
        print(f'incorrect number of arguments given')
        print('Correct Format:\n\tpython3 curve_slope.py data_src_folder_path plot_dst_folder_path color')
        sys.exit()

    # Create the data object
    curves = Curves(sys.argv[1], sys.argv[2], sys.argv[3])
    
    os.chmod(sys.argv[1], 0o777)
    os.chmod(sys.argv[2], 0o777)

    
    # load the data in 
    curves.get_curve_data()

    # clean the data
    curves.flip_curve_over_yaxis()

    curves.remove_points_after_max_depth()

    curves.remove_points_before_min_depth()

    curves.remove_data_prior_first_ground_contact()

    #adds a CSV file output that compiles the condition types and response strengths in a long format for easier analysis in R or Python
    compiled_data = []
    for i in range(len(curves.curve_data)):
        df = curves.curve_data[i]
        condition = curves.filenames[i].split('.')[0]  # Assuming filename format is "condition.csv"
        slope, _ = curve_fit(curves.func, df['depth'], df['resistance'])
        slope_value = slope[0]
        for _, row in df.iterrows():
            compiled_data.append({
                'condition': condition,
                'depth': row['depth'],
                'resistance': row['resistance'],
                'slope': slope_value
            })
    
    curves.get_density()
    curves.plot_combined() 
    curves.plot_indiviual_groups()
    curves.interpolate(500)


    

if __name__ == "__main__":
    main()