
from datetime import date
from fileinput import filename
from fileinput import filename
from turtle import color
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os


class Curves:

    def __init__(self, data_src_folder_path:str, plot_dst_folder_path:str, plot_color1:str = 'grey', plot_color2:str = 'grey', plot_color3:str = 'grey', plot_color4:str = 'grey', plot_color5:str = 'grey', plot_color6:str = 'grey'):
        self.data_src_folder_path = data_src_folder_path
        self.plot_dst_folder_path = plot_dst_folder_path
        self.plot_color1 = plot_color1
        self.plot_color2 = plot_color2
        self.plot_color3 = plot_color3
        self.plot_color4 = plot_color4
        self.plot_color5 = plot_color5
        self.plot_color6 = plot_color6
        self.filenames= []
        self.curve_data = []
        self.slopes = []
        self.slopes_SuperSand = []
        self.slopes_ASTM = []
        self.slopes_Clay25 = []
        self.slopes_Clay50 = []
        self.slopes_Clay75 = []
        self.slopes_Clay100 = []
        self.slopes_other = []
        self.plot_data = []
        self.ground_height = []
        
    def get_curve_data(self):
        for filename in os.listdir(self.data_src_folder_path):
            df = pd.read_csv(f"{self.data_src_folder_path}/{filename}")
            self.ground_height.append(float(df['ground_height'].loc[0]) * 1/100)

            df = pd.read_csv(f"{self.data_src_folder_path}/{filename}", skiprows=2) #added this in
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

    def flip_over_x_axis(self):
        cleaned_df_list = []
        for df in self.curve_data:
            copy_df = df.copy()
            copy_df['resistance'] = -copy_df['resistance']
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
        
    def make_resistance_min_equal_zero(self):
        cleaned_df_list = []
        for df in self.curve_data:
            copy_df = df.copy()
            copy_df["resistance"] = copy_df["resistance"].clip(lower=0)
            cleaned_df_list.append(copy_df)
        self.curve_data = cleaned_df_list

    #def find_positive_subranges_of_resistance(self, df: pd.DataFrame):
        #ranges_above_zero_list = []
        #range_max_height_list = []
    
        #in_range = False
        #range_start_idx = None
        #range_max_resistance = 0
    
        #for i, res in enumerate(df["resistance"]):
            #if res > 0:
                #if not in_range:
                    # starting a new range
                    #in_range = True
                   # if i > 0: range_start_idx = i - 1
                   # else: range_start_idx = 0
                   # range_max_resistance = res
               # else:
               #     range_max_resistance = max(range_max_resistance, res)
           # elif in_range:
                # end of a positive range
               # ranges_above_zero_list.append((range_start_idx, i))
               # range_max_height_list.append(range_max_resistance)
               # in_range = False
    
        # handle if last element was part of a range
       # if in_range:
           # ranges_above_zero_list.append((range_start_idx, len(df["resistance"]) - 1))
           # range_max_height_list.append(range_max_resistance)
    
        #return ranges_above_zero_list, range_max_height_list

    #def filter_subranges(self, subrange_list, subrange_max_resistance_list, subrange_max_resistance):
      #  max_resistance_overall = max(subrange_max_resistance_list)
      #  filtered_subranges = []
      #  for i, pos_range in enumerate(subrange_list):
           # if subrange_max_resistance_list[i] > max_resistance_overall * subrange_max_resistance:
            #    filtered_subranges.append(pos_range)
       # return filtered_subranges
    
   # def get_ground_start_idx(self, df, subrange_max_resistance, spacing_between_ranges, idx):
       # subrange_list, subrange_max_resistance_list = self.find_positive_subranges_of_resistance(df)
        #if idx == 51:
           # print(f"subrange_list: {subrange_list}\nsubrange_max_resistane_list: {subrange_max_resistance_list}")

       # if len(subrange_list) < 1: return 0
        
        # removes subranes below subrange_max_resistance threshold
      #  filtered_subranges = self.filter_subranges(subrange_list, subrange_max_resistance_list, subrange_max_resistance)
       # if idx == 51:
            # print(f"filter_subranges: {filtered_subranges}")
           # depth_value_list = []
           # for start, end in filtered_subranges:
              #  depth_value_list.append((float(df['depth'].iloc[start]), float(df['depth'].iloc[end])))
            # print(f"filter_subranges_values: {depth_value_list}")

      #  ground_start_idx = filtered_subranges[-1][0] # init ground_start_idx with start of largest curve (last subrange in range_list)
       # if len(filtered_subranges) < 2: return ground_start_idx


        # reverse iterate over the filtered subranges and stop when the distance from subrange i to j is too high
      #  for i in range(len(filtered_subranges)-2, -1, -1): 
          #  subrange_i_start = df["depth"].iloc[filtered_subranges[i][1]]
          #  subrange_j_end = df["depth"].iloc[filtered_subranges[i+1][0]]
          #  if idx == 51: print(f"{subrange_j_end} - {subrange_i_start} > {spacing_between_ranges} * {df['depth'].iloc[-1] - df['depth'].iloc[0]}")
          #  if subrange_j_end - subrange_i_start > spacing_between_ranges * (df['depth'].iloc[-1] - df['depth'].iloc[0]):
            #    ground_start_idx = filtered_subranges[i+1][0]
             #   break # found our final ground_start_idx
          #  else:
              #  ground_start_idx = filtered_subranges[i][0]
                
     #   if idx == 51: print(f"ground_start_idx: {ground_start_idx}")
    
        #DEBUG####
     #   print("Max Depth:",df['depth'].max()-df['depth'].iloc[ground_start_idx])
        #########

       # return ground_start_idx
    
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

    def plot(self):
        """Set up the figure and draw all the category trendlines and cones."""
        plt.figure(figsize=(10,10))
        plt.xlabel('Depth (m)')
        plt.ylabel('Resistance (N)')
        plt.xlim(0, 0.05)
        plt.ylim(-2.25, 5)

    def plot_variable(self, x_vals, y_vals, x_upper, y_upper, x_lower, y_lower, label_mean, label_upper, label_lower, color):
        plt.plot(x_vals, y_vals, label=label_mean,color=color,linestyle='-')
        plt.plot(x_upper, y_upper, label=label_upper,color=color, linestyle='--')
        plt.plot(x_lower, y_lower, label=label_lower,color=color, linestyle='--')
        plt.fill_between(x_vals, y_lower, y_upper, color=color, alpha=0.3)


        #resist = self.curve_data[i]["resistance"]
        #depth = self.curve_data[i]["depth"]
        #plt.figure(figsize=(10,10))
        # prepare categories to colour mapping

    def compute_slopes(self):
        categories = {
            'Clay%0': self.plot_color1,
            'ASTM': self.plot_color2,
            'Clay25': self.plot_color3,
            'Water7.5': self.plot_color4,
            'Water10': self.plot_color5,
            'Water15': self.plot_color6,
        }

        slopes = {k: [] for k in  categories.keys()}
        slopes['other'] = []

        # compute slope for every curve and assign to category
        for i, df in enumerate(self.curve_data):
            filename = self.filenames[i]
            opt_slope, _ = curve_fit(self.func, df['depth'], df['resistance'])
            slope = opt_slope[0]
            print(f"{filename} slope: {slope}")
            matched = False
            for key in categories:
                if key in filename:
                    slopes[key].append(slope)
                    matched = True
                    break
            if not matched:
                slopes['other'].append(slope)
        
        self.plot_data = []
        x_vals = np.linspace(0, 0.05, 100)
        for key, slope_list in slopes.items():
            if not slope_list:
                continue
            mean_slope = np.mean(slope_list)
            std_slope = np.std(slope_list)
            upper = mean_slope + std_slope
            lower = mean_slope - std_slope
            colour = categories.get(key, 'grey')

            y_mean = self.func(x_vals, mean_slope)
            y_upper = self.func(x_vals, upper)
            y_lower = self.func(x_vals, lower)
 
            self.plot_data.append({
                "x_vals": x_vals,
                "y_mean": y_mean,
                "y_upper": y_upper,
                "y_lower": y_lower,
                "label_mean": f'{key} mean ({mean_slope:.2f})',
                "label_upper": f'{key} upper ({upper:.2f})',
                "label_lower": f'{key} lower ({lower:.2f})',
                "color": colour
            })

        
    def plot_all(self):
        self.plot()

        self.compute_slopes()

        for item in self.plot_data:
            self.plot_variable(
                item["x_vals"],
                item["y_mean"],
                item["x_vals"],   # upper uses same x
                item["y_upper"],
                item["x_vals"],   # lower uses same x
                item["y_lower"],
                item["label_mean"],
                item["label_upper"],
                item["label_lower"],
                item["color"]
            )
        plt.title("All Clay Data Force-Depth Curves")
        plt.legend()        
        plt.savefig(f'{self.plot_dst_folder_path}/{date.today().strftime("%b_%d_%Y")}_uncertaintycones_multitrendlines')
        plt.show()


        #ADD TRENDLINE #un-hashed everything inbetween hashed lines
        ##################################################

        # slopesmean = np.mean(self.slopes)
        # slopessd = np.std(self.slopes)

        # plt.plot(depth, resist, c=self.plot_color2, linewidth=2)
       
        # plt.plot(depth, self.func(depth, slopesmean), 'r--', label=f"slope: {round(opt_slope[0], 2)}")
 
    #plt.legend()
        ######################################################

        # Define slope (m) and intercept (b)
        # m = round(slopesmean, 3) #83.17875 - original number # slope 
        # I put in opt_slope to see if that was the correct function, I also put in 20 just to see what it would do but no change.
        # b = 0   # intercept #I kept this the same

        # Generate x values
        # x = np.linspace(0, .05, 100)  # from 0 to 0.05

        # Compute y values using y = mx + b
        # y = m * x + b

        # Plot the line
        #plt.plot(x, y, label=f'slope: {m}',color='red',linestyle='--')
        #plt.legend(loc='upper left')
        #########################################################


def main():
    if len(sys.argv) != 9:
        print(f'incorrect number of arguments given')
        print('\tpython3 plot_curve_overlay.py data_src_folder_path plot_dst_folder_path color1 color2 color3 color4 color5 color6')
        sys.exit()

    # Create the data object
    curves = Curves(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])
    
    # load the data in 
    curves.get_curve_data()

    # clean the data
    curves.flip_curve_over_yaxis()
    # curves.flip_over_x_axis() # this is needed depending on how data is formatted
    curves.remove_points_after_max_depth()
    curves.remove_points_before_min_depth()
    #curves.make_resistance_min_equal_zero() #taking out allows for negative forces to be shown
    #curves.remove_data_prior_to_ground(0.1, 0.05)
    curves.remove_data_prior_first_ground_contact()
    curves.interpolate(500)

    # plot the data
    curves.plot_all()
    



if __name__ == "__main__":
    main()
