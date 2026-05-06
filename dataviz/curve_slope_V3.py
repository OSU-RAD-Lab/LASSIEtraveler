
from datetime import date
import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os

class Curves:

    def __init__(self, data_src_folder_path:str, plot_dst_folder_path:str, plot_color:str = 'black'):
        self.data_src_folder_path = data_src_folder_path
        self.plot_dst_folder_path = plot_dst_folder_path
        self.plot_color = plot_color
        self.filenames= []
        self.curve_data = []
        self.ground_height = []

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

    def plot(self):
        for i in range(len(self.curve_data)):
            plt.figure(figsize=(8,8))
            plt.xlabel('Depth (m)')
            plt.ylabel('Resistance (N)')
            plt.title(self.filenames[i], fontsize=8)
            plt.xlim(0, 0.05)
            plt.ylim(-1.75, 3.3)
        

            resist = self.curve_data[i]["resistance"]
            depth = self.curve_data[i]["depth"]

            plt.plot(depth, resist, c=self.plot_color, linewidth=2)
            opt_slope, _ = curve_fit(self.func, depth, resist)
            plt.plot(depth, self.func(depth, opt_slope), 'r--', label=f"slope: {round(opt_slope[0], 2)}")
            plt.legend()
            save_path = f'{self.plot_dst_folder_path}/{date.today().strftime("%b_%d_%Y")}/{self.filenames[i]}.png'
            print(f'save path: {save_path}')
            plt.savefig(save_path)
            #plt.show()

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
    
    curves.interpolate(500)

    # plot the data
    curves.plot()
    #output the compiled data to a CSV file
    compiled_df = pd.DataFrame(compiled_data)
    compiled_df.to_csv(f'{sys.argv[2]}/compiled_curve_data.csv', index=False)  

    

if __name__ == "__main__":
    main()