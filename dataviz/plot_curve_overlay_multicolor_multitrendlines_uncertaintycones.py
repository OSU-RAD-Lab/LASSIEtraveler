
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
        self.slopes_0 = []
        self.slopes_25 = []
        self.slopes_50 = []
        self.slopes_75 = []
        self.slopes_100 = []
        self.slopes_other = []
        
    def get_curve_data(self):
        for filename in os.listdir(self.data_src_folder_path):
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

    def find_positive_subranges_of_resistance(self, df: pd.DataFrame):
        ranges_above_zero_list = []
        range_max_height_list = []
    
        in_range = False
        range_start_idx = None
        range_max_resistance = 0
    
        for i, res in enumerate(df["resistance"]):
            if res > 0:
                if not in_range:
                    # starting a new range
                    in_range = True
                    if i > 0: range_start_idx = i - 1
                    else: range_start_idx = 0
                    range_max_resistance = res
                else:
                    range_max_resistance = max(range_max_resistance, res)
            elif in_range:
                # end of a positive range
                ranges_above_zero_list.append((range_start_idx, i))
                range_max_height_list.append(range_max_resistance)
                in_range = False
    
        # handle if last element was part of a range
        if in_range:
            ranges_above_zero_list.append((range_start_idx, len(df["resistance"]) - 1))
            range_max_height_list.append(range_max_resistance)
    
        return ranges_above_zero_list, range_max_height_list

    def filter_subranges(self, subrange_list, subrange_max_resistance_list, subrange_max_resistance):
        max_resistance_overall = max(subrange_max_resistance_list)
        filtered_subranges = []
        for i, pos_range in enumerate(subrange_list):
            if subrange_max_resistance_list[i] > max_resistance_overall * subrange_max_resistance:
                filtered_subranges.append(pos_range)
        return filtered_subranges
    
    def get_ground_start_idx(self, df, subrange_max_resistance, spacing_between_ranges, idx):
        subrange_list, subrange_max_resistance_list = self.find_positive_subranges_of_resistance(df)
        if idx == 51:
            print(f"subrange_list: {subrange_list}\nsubrange_max_resistane_list: {subrange_max_resistance_list}")

        if len(subrange_list) < 1: return 0
        
        # removes subranes below subrange_max_resistance threshold
        filtered_subranges = self.filter_subranges(subrange_list, subrange_max_resistance_list, subrange_max_resistance)
        if idx == 51:
            # print(f"filter_subranges: {filtered_subranges}")
            depth_value_list = []
            for start, end in filtered_subranges:
                depth_value_list.append((float(df['depth'].iloc[start]), float(df['depth'].iloc[end])))
            # print(f"filter_subranges_values: {depth_value_list}")

        ground_start_idx = filtered_subranges[-1][0] # init ground_start_idx with start of largest curve (last subrange in range_list)
        if len(filtered_subranges) < 2: return ground_start_idx


        # reverse iterate over the filtered subranges and stop when the distance from subrange i to j is too high
        for i in range(len(filtered_subranges)-2, -1, -1): 
            subrange_i_start = df["depth"].iloc[filtered_subranges[i][1]]
            subrange_j_end = df["depth"].iloc[filtered_subranges[i+1][0]]
            if idx == 51: print(f"{subrange_j_end} - {subrange_i_start} > {spacing_between_ranges} * {df['depth'].iloc[-1] - df['depth'].iloc[0]}")
            if subrange_j_end - subrange_i_start > spacing_between_ranges * (df['depth'].iloc[-1] - df['depth'].iloc[0]):
                ground_start_idx = filtered_subranges[i+1][0]
                break # found our final ground_start_idx
            else:
                ground_start_idx = filtered_subranges[i][0]
                
        if idx == 51: print(f"ground_start_idx: {ground_start_idx}")
    
        #DEBUG####
        print("Max Depth:",df['depth'].max()-df['depth'].iloc[ground_start_idx])
        #########

        return ground_start_idx

    def remove_data_prior_to_ground(self, subrange_max_resistance, spacing_between_ranges):
        cleaned_df_list = []
        for idx, df in enumerate(self.curve_data):
            copy_df = df.copy()
            start_idx = self.get_ground_start_idx(copy_df, subrange_max_resistance, spacing_between_ranges, idx)
            copy_df = copy_df.iloc[start_idx:]
            # copy_df = start_curve_at_ground(copy_df, subrange_max_resistance, spacing_between_ranges)
            # I've un hashed the above code but "start_curve_at_ground" was undefined,
            # I've input ground_start_idx in place of it to see if that was the problem, again it was undefined
            copy_df["depth"] = copy_df["depth"] - copy_df['depth'].iloc[0]
            cleaned_df_list.append(copy_df)
        self.curve_data = cleaned_df_list
    
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
        plt.figure(figsize=(10,10))
        plt.xlabel('Depth (m)')
        plt.ylabel('Resistance (N)')
        plt.title('Depth vs Resistance Curve')
        plt.xlim(0, 0.05)
        plt.ylim(-1.75, 3.3)
        
        
        for i in range(len(self.curve_data)):
            # if i == 1:
           
            if "Clay0" in self.filenames[i]:
                #plot raw data
                #plt.plot(self.curve_data[i]["depth"], self.curve_data[i]["resistance"], c=self.plot_color1, linewidth=2,alpha=0.2)
                
                opt_slope, _ = curve_fit(self.func, self.curve_data[i]["depth"], self.curve_data[i]["resistance"])
                self.slopes_0.append(opt_slope[0])
                slopesmean_zero = np.mean(self.slopes_0)
                #calculate upper and lower bounds for uncertainty cone using a 5th and 95th percentile of the slopes
                upper_bound_zero = slopesmean_zero + np.std(self.slopes_0)
                lower_bound_zero = slopesmean_zero - np.std(self.slopes_0)
                #upper_bound_zero = slopesmean_zero + np.std(self.slopes_0)
                #lower_bound_zero = slopesmean_zero - np.std(self.slopes_0)

                x_upper_zero = np.linspace(0, 0.05, 100)  # from 0 to max depth
                y_upper_zero = self.func(x_upper_zero, upper_bound_zero)
                
                x_lower_zero = np.linspace(0, 0.05, 100)  # from 0 to max depth
                y_lower_zero = self.func(x_lower_zero, lower_bound_zero)
                # Generate x values
                x_zero = np.linspace(0, 0.05, 100)  # from 0 to max depth
                # Compute y values using y = mx + b where m is the slope and b is 0
                y_zero = self.func(x_zero, slopesmean_zero)
                
            elif "Clay25" in self.filenames[i]:
                #plot raw data
                #plt.plot(self.curve_data[i]["depth"], self.curve_data[i]["resistance"], c=self.plot_color2, linewidth=2,alpha=0.2)
                
                opt_slope, _ = curve_fit(self.func, self.curve_data[i]["depth"], self.curve_data[i]["resistance"])
                self.slopes_25.append(opt_slope[0])
                slopesmean_twentyfive = np.mean(self.slopes_25)

                upper_bound_twentyfive = slopesmean_twentyfive + np.std(self.slopes_25)
                lower_bound_twentyfive = slopesmean_twentyfive - np.std(self.slopes_25)

                x_upper_twentyfive = np.linspace(0, 0.05, 100)  # from 0 to max depth
                y_upper_twentyfive = self.func(x_upper_twentyfive, upper_bound_twentyfive)

                x_lower_twentyfive = np.linspace(0, 0.05, 100)  # from 0 to max depth
                y_lower_twentyfive = self.func(x_lower_twentyfive, lower_bound_twentyfive)
                # Generate x values
                x_twentyfive = np.linspace(0, 0.05, 100)  # from 0 to max depth
                # Compute y values using y = mx + b where m is the slope and b is 0
                y_twentyfive = self.func(x_twentyfive, slopesmean_twentyfive)
                
            elif "Clay50" in self.filenames[i]:
                #plot raw data
                #plt.plot(self.curve_data[i]["depth"], self.curve_data[i]["resistance"], c=self.plot_color3, linewidth=2,alpha=0.2)
                
                opt_slope, _ = curve_fit(self.func, self.curve_data[i]["depth"], self.curve_data[i]["resistance"])
                self.slopes_50.append(opt_slope[0])
                slopesmean_fifty = np.mean(self.slopes_50)

                upper_bound_fifty = slopesmean_fifty + np.std(self.slopes_50)
                lower_bound_fifty = slopesmean_fifty - np.std(self.slopes_50)

                x_upper_fifty = np.linspace(0, 0.05, 100)  # from 0 to max depth
                y_upper_fifty = self.func(x_upper_fifty, upper_bound_fifty)

                x_lower_fifty = np.linspace(0, 0.05, 100)  # from 0 to max depth
                y_lower_fifty = self.func(x_lower_fifty, lower_bound_fifty)
                # Generate x values
                x_fifty = np.linspace(0, 0.05, 100)  # from 0 to max depth
                # Compute y values using y = mx + b where m is the slope and b is 0
                y_fifty = self.func(x_fifty, slopesmean_fifty)
                
            elif "Clay75" in self.filenames[i]:
                #plot raw data
                #plt.plot(self.curve_data[i]["depth"], self.curve_data[i]["resistance"], c=self.plot_color4, linewidth=2,alpha=0.2)
                
                opt_slope, _ = curve_fit(self.func, self.curve_data[i]["depth"], self.curve_data[i]["resistance"])
                self.slopes_75.append(opt_slope[0])
                slopesmean_seventyfive = np.mean(self.slopes_75)

                upper_bound_seventyfive = slopesmean_seventyfive + np.std(self.slopes_75)
                lower_bound_seventyfive = slopesmean_seventyfive - np.std(self.slopes_75)

                x_upper_seventyfive = np.linspace(0, 0.05, 100)  # from 0 to max depth
                y_upper_seventyfive = self.func(x_upper_seventyfive, upper_bound_seventyfive)

                x_lower_seventyfive = np.linspace(0, 0.05, 100)  # from 0 to max depth
                y_lower_seventyfive = self.func(x_lower_seventyfive, lower_bound_seventyfive)
                # Generate x values
                x_seventyfive = np.linspace(0, 0.05, 100)  # from 0 to max depth
                # Compute y values using y = mx + b where m is the slope and b is 0
                y_seventyfive = self.func(x_seventyfive, slopesmean_seventyfive)
                
            elif "Clay100" in self.filenames[i]:
                #plot raw data
                #plt.plot(self.curve_data[i]["depth"], self.curve_data[i]["resistance"], c=self.plot_color5, linewidth=2,alpha=0.2)

                opt_slope, _ = curve_fit(self.func, self.curve_data[i]["depth"], self.curve_data[i]["resistance"])
                self.slopes_100.append(opt_slope[0])
                slopesmean_onehundred = np.mean(self.slopes_100)

                upper_bound_onehundred = slopesmean_onehundred + np.std(self.slopes_100)
                lower_bound_onehundred = slopesmean_onehundred - np.std(self.slopes_100)

                x_upper_onehundred = np.linspace(0, 0.05, 100)  # from 0 to max depth
                y_upper_onehundred = self.func(x_upper_onehundred, upper_bound_onehundred)

                x_lower_onehundred = np.linspace(0, 0.05, 100)  # from 0 to max depth
                y_lower_onehundred = self.func(x_lower_onehundred, lower_bound_onehundred)
                # Generate x values
                x_onehundred = np.linspace(0, 0.05, 100)  # from 0 to max depth
                # Compute y values using y = mx + b where m is the slope and b is 0
                y_onehundred = self.func(x_onehundred, slopesmean_onehundred)
              
            else:
                #plot raw data
                #plt.plot(self.curve_data[i]["depth"], self.curve_data[i]["resistance"], c=self.plot_color6, linewidth=2,alpha=0.2)
                
                opt_slope, _ = curve_fit(self.func, self.curve_data[i]["depth"], self.curve_data[i]["resistance"])
                self.slopes_other.append(opt_slope[0])
                slopesmean = np.mean(self.slopes_other)

                upper_bound_other = slopesmean + np.std(self.slopes_other)
                lower_bound_other = slopesmean - np.std(self.slopes_other)

                x_upper_other = np.linspace(0, 0.05, 100)  # from 0 to max depth
                y_upper_other = self.func(x_upper_other, upper_bound_other)

                x_lower_other = np.linspace(0, 0.05, 100)  # from 0 to max depth
                y_lower_other = self.func(x_lower_other, lower_bound_other)
                # Plot uncertainty cones
                # plt.plot(x_upper_other, y_upper_other, color='purple', linestyle='-', alpha=0.5)
                # plt.plot(x_lower_other, y_lower_other, color='purple', linestyle='-', alpha=0.5)
                # shade area between upper and lower bounds
                # plt.fill_between(x_other, y_lower_other, y_upper_other, color='purple', alpha=0.1)
                # Generate x values
                x_else = np.linspace(0, 0.05, 100)  # from 0 to max depth
                # Compute y values using y = mx + b where m is the slope and b is 0
                y_else = self.func(x_else, slopesmean)
                #plt.plot(x_else, y_else, label=f'slope: {slopesmean:.2f}',color='purple',linestyle='--')
        
        resist = self.curve_data[i]["resistance"]
        depth = self.curve_data[i]["depth"]

        # trendline plots
        plt.plot(x_zero, y_zero, label=f'ASTM Jan 30th slope: {slopesmean_zero:.2f}',color=self.plot_color1,linestyle='-')
        plt.plot(x_twentyfive, y_twentyfive, label=f'25% slope: {slopesmean_twentyfive:.2f}',color=self.plot_color2,linestyle='-')
        plt.plot(x_fifty, y_fifty, label=f'50% slope: {slopesmean_fifty:.2f}',color=self.plot_color3,linestyle='-')
        plt.plot(x_seventyfive, y_seventyfive, label=f'75% slope: {slopesmean_seventyfive:.2f}',color=self.plot_color4,linestyle='-')
        plt.plot(x_onehundred, y_onehundred, label=f'ASTM Feb 23rd slope: {slopesmean_onehundred:.2f}',color=self.plot_color5,linestyle='-')
        
        #Uncertainty cone plots
        plt.plot(x_upper_zero, y_upper_zero, color=self.plot_color1, linestyle='--')
        plt.plot(x_lower_zero, y_lower_zero, color=self.plot_color1, linestyle='--')
        # shade area between upper and lower bounds
        plt.fill_between(x_zero, y_lower_zero, y_upper_zero, color=self.plot_color1, alpha=0.3)
        #repeat
        plt.plot(x_upper_twentyfive, y_upper_twentyfive, color=self.plot_color2, linestyle='--' )
        plt.plot(x_lower_twentyfive, y_lower_twentyfive, color=self.plot_color2, linestyle='--')
        plt.fill_between(x_twentyfive, y_lower_twentyfive, y_upper_twentyfive, color=self.plot_color2, alpha=0.3)
        plt.plot(x_upper_fifty, y_upper_fifty, color=self.plot_color3, linestyle='--')
        plt.plot(x_lower_fifty, y_lower_fifty, color=self.plot_color3, linestyle='--')
        plt.fill_between(x_fifty, y_lower_fifty, y_upper_fifty, color=self.plot_color3, alpha=0.3)
        plt.plot(x_upper_seventyfive, y_upper_seventyfive, color=self.plot_color4, linestyle='--')
        plt.plot(x_lower_seventyfive, y_lower_seventyfive, color=self.plot_color4, linestyle='--')
        plt.fill_between(x_seventyfive, y_lower_seventyfive, y_upper_seventyfive, color=self.plot_color4, alpha=0.3)
        plt.plot(x_upper_onehundred, y_upper_onehundred, color=self.plot_color5, linestyle='--')
        plt.plot(x_lower_onehundred, y_lower_onehundred, color=self.plot_color5, linestyle='--')
        plt.fill_between(x_onehundred, y_lower_onehundred, y_upper_onehundred, color=self.plot_color5, alpha=0.3)

            #opt_slope, _ = curve_fit(self.func, depth, resist)
           # print(i)
            #print(self.slopes)
            #self.slopes.append(opt_slope[0])


        #ADD TRENDLINE #un-hashed everything inbetween hashed lines
        ##################################################

        # slopesmean = np.mean(self.slopes)
        # slopessd = np.std(self.slopes)

        # plt.plot(depth, resist, c=self.plot_color2, linewidth=2)
       
        # plt.plot(depth, self.func(depth, slopesmean), 'r--', label=f"slope: {round(opt_slope[0], 2)}")
 
        plt.legend()
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

        # Add title
        plt.title("All Data Force-Depth Curves")

        plt.savefig(f'{self.plot_dst_folder_path}/overlayed_curves')
        plt.show()

    #self.slopes = []


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
    # curves.make_resistance_min_equal_zero() #taking out allows for negative forces to be shown
    curves.remove_data_prior_to_ground(0.1, 0.05)
    curves.interpolate(500)

    # plot the data
    curves.plot()


if __name__ == "__main__":
    main()
