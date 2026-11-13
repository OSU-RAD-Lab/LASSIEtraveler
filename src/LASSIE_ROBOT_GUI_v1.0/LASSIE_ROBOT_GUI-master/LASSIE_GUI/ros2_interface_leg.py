from crustProperties import *
from loadcell_hx711 import *
import numpy as np
import matplotlib.pyplot as plt
import csv
import time
import rclpy
import os
from rclpy.node import Node
from std_msgs.msg import Float32
from control_msgs.msg import DynamicJointState
from std_msgs.msg import Float64MultiArray
rclpy.init()

# pp.set_xlim([-0.15, 0.15])
# pp.set_ylim([-0.30, -0.10])


class ControlNode_Leg(Node):
    def __init__(self):
        super().__init__('control_node')
        self.id = "leg"
        self.publisher_ = self.create_publisher(
            Float64MultiArray, '/Gui_information', 10)
        self.linear_subscription = self.create_subscription(
            DynamicJointState,
            '/dynamic_joint_states',
            self.handle_joint_state,
            10)

        self.force_results = self.create_subscription(
            Float64MultiArray,
            '/travelerstate',
            self.handle_travelerstate,
            10)
        # some parameters to specify here
        self.tab_control = ['Extrude', 'Traverse Workspace',
                            'Penetrate and Shear', 'Free Moving', 'Detect Ground']
        self.temperature = 0.0
        self.controller_error = 0.0
        self.encoder_error = 0.0
        self.motor_error = 0.0
        self.position = 0.0
        self.torque = 0.0
        self.temperature1 = 0.0
        self.controller_error1 = 0.0
        self.encoder_error1 = 0.0
        self.motor_error1 = 0.0
        self.position1 = 0.0
        self.torque1 = 0.0
        self.toeforce_x = 0
        self.toeforce_y = 0
        self.toeposition_x = 0
        self.toeposition_y = 0
        self.toevelocity_x = 0
        self.toevelocity_y = 0
        self.theta_command = 0
        self.length_command = 0
        self.state_flag = 0
        self.velocity = 0
        self.velocity1 = 0
        self.running_curr = 0
        self.running_prev = 0

        self.start_time = time.time()
        self.num_data_points = 0
        self.config_name_list = ["scenario", "real_time_plot", "extrude_speed_slider", "extrude_angle_slider",
                                 "extrude_length_slider", "down_length_slider", "down_speed_slider", "delay_after_down",
                                 "shear_length", "shear_speed", "delay_after_shear", "back_speed",
                                 "moving_speed", "moving_step_angle", "time_delay", "variable1",
                                 "variable3",  "search_start", "search_end", "ground_height", "extrude_back_speed"]
        self.variable_name_list = ["time", "toeforce_x", "toeforce_y", "toeforce_x_loadcell",
                                   "toeforce_yloadcell", "toe_position_x", "toe_position_y", "toe_velocity_x", "toe_velocity_y",
                                   "position", "position1", "torque", "torque1",
                                   "theta command", "length command", "state flag", "current"]
        self.variable_array = np.zeros((50000, 17))
        self.time_list = []
        self.force_list_x = []
        self.force_list_y = []
        self.position1_list = []
        self.torque1_list = []
        self.position_list = []
        self.torque_list = []
        self.speed_list = []
        self.speed_list1 = []
        self.temperature_list = []
        self.temperature1_list = []
        self.toeposition_x_list = []
        self.toeposition_y_list = []
        self.toevelocity_x_list = []
        self.toevelocity_y_list = []
        self.theta_command_list = []
        self.length_command_list = []
        self.state_flag_list = []
        self.running_list = []
        self.force_list_loadcell_x = []
        self.force_list_loadcell_y = []

        self.run_time = 0

        self.fpx = None
        self.fpy = None
        self.fpxl = None
        self.fpyl = None
        self.fp = None
        self.fig4 = None
        self.fig5 = None
        self.fig6 = None
        self.speed_px = None
        self.speed_py = None
        self.speed_p = None
        self.ppp = None
        self.pp = None

        self.fig4, self.fp = plt.subplots()

        self.fp.set_title('Force Measurements vs Distance', fontsize=10)
        self.fp.set_xlabel('Distance(t)', fontsize=10)
        self.fp.set_ylabel('Force(N)', fontsize=10)
        self.fp.grid(True)
        self.fpx, = self.fp.plot([], [], 'r', linewidth=3)
        self.fpy, = self.fp.plot([], [], 'g', linewidth=3)
        self.fpxl, = self.fp.plot([], [], 'b', linewidth=3)
        self.fpyl, = self.fp.plot([], [], 'y', linewidth=3)
        self.crust_1, = self.fp.plot([], [])
        self.crust_2, = self.fp.plot([], [])
        self.crust_3, = self.fp.plot([], [], marker="o")
        self.crust_4, = self.fp.plot([], [], marker="o")
        self.crust_warning = self.fp.annotate(
            '', xy=(0.05, 0.95), xycoords='axes fraction')
        self.fp.legend(['x', 'y'])
        self.fig5, self.speed_p = plt.subplots()
        self.speed_p.set_title('Speed vs time', fontsize=10)
        self.speed_p.set_xlabel('Time(t)', fontsize=10)
        self.speed_p.set_ylabel('Speed(m/s)', fontsize=10)
        self.speed_p.grid(True)
        self.speed_px, = self.speed_p.plot([], [], 'r', linewidth=3)
        self.speed_py, = self.speed_p.plot([], [], 'g', linewidth=3)
        self.speed_p.legend(['x', 'y'])
        self.fig6, self.pp = plt.subplots()
        self.pp.set_title('position trajectories', fontsize=10)
        self.pp.set_xlabel('X', fontsize=10)
        self.pp.set_ylabel('Y', fontsize=10)
        self.pp.grid(True)
        self.ppp, = self.pp.plot([], [], 'r', linewidth=3)

    def calibrate_loadcell(self):
        self.loadcell1 = loadcell()
        self.loadcell1.setup()

    def calibrate(self, drag_traj, mode):
        self.start_time = time.time()
        self.run_time = 0
        self.variable_array = np.zeros((50000, 17))
        self.num_data_points = 0
        if (drag_traj != 1 and drag_traj != 3):
            self.fp.set_title('Force Measurements vs Time', fontsize=10)
            self.fp.set_xlabel('Time(t)', fontsize=10)
        else:
            self.fp.set_title('Force Measurements vs Distance', fontsize=10)
            self.fp.set_xlabel('Distance(t)', fontsize=10)
        if (mode == 3):
            self.fp.legend(['x', 'y', 'x-loadcell', 'y-loadcell'])
        else:
            self.fp.legend(['x', 'y'])

    def get_fp(self):
        return self.fp

    def get_pp(self):
        return self.pp

    def get_speed_p(self):
        return self.speed_p

    def update_plot(self, drag_traj, mode, ground_height):
        print(ground_height)
        index = np.linspace(0, self.num_data_points, self.num_data_points)
        self.time_list = self.variable_array[0:self.num_data_points-1, 0]
        self.force_list_x = self.variable_array[0:self.num_data_points-1, 1]
        self.force_list_y = self.variable_array[0:self.num_data_points-1, 2]
        self.force_list_loadcell_x = self.variable_array[0:self.num_data_points-1, 3]
        self.force_list_loadcell_y = self.variable_array[0:self.num_data_points-1, 4]
        self.toeposition_x_list = self.variable_array[0:self.num_data_points-1, 5]
        self.toeposition_y_list = self.variable_array[0:self.num_data_points-1, 6]
        self.toevelocity_x_list = self.variable_array[0:self.num_data_points-1, 7]
        self.toevelocity_y_list = self.variable_array[0:self.num_data_points-1, 8]

        # mode 3 is for field trip, in this case we need to plot the data when leg
        # penetrate into the terrain

        if (drag_traj == 1):
            depth = -ground_height - np.array(self.toeposition_y_list)
            index = np.where(depth > 0)[0]

            depth = depth[index]
            print('depth:', depth)
            assert (len(depth) == len(self.force_list_x[index]))
            self.fpx.set_xdata(depth)
            self.fpx.set_ydata(self.force_list_x[index])
            self.fpy.set_xdata(depth)
            self.fpy.set_ydata(self.force_list_y[index])
            if (mode == 3):
                self.fpxl.set_xdata(depth)
                self.fpxl.set_ydata(self.force_list_loadcell_x[index])
                self.fpyl.set_xdata(depth)
                self.fpyl.set_ydata(self.force_list_loadcell_y[index])
            # if penetrate, show the crust features in a real time mode
            if (mode == 0):
                try:
                    (crustStiffness, yieldDepth,
                     yieldForce, ultimateDepth,
                     ultimateForce, basinDepth,
                     basinForce, sandStiffness,
                     sandIntercept, depth_sand_linear,
                     sandInterceptY) = crust_properties(- np.array(self.toeposition_y_list),
                                                        np.array(
                                                            self.force_list_y),
                                                        ground_height,
                                                        1)
                    # print(crustStiffness)
                    self.crust_1.set_xdata([0, ultimateDepth])
                    self.crust_1.set_ydata([0, crustStiffness*ultimateDepth])
                    self.crust_2.set_xdata([ultimateDepth])
                    self.crust_2.set_ydata([ultimateForce])
                    self.crust_3.set_xdata([basinDepth])
                    self.crust_3.set_ydata([basinForce])
                    depth_end = depth[-1]
                    self.crust_4.set_xdata([depth_sand_linear, depth_end])
                    self.crust_4.set_ydata(
                        [sandStiffness*depth_sand_linear, sandStiffness*depth_end]+sandInterceptY)
                    # self.crust_warning.set_text("detecting crust feature failed")
                except:
                    self.crust_warning.set_text(
                        "detecting crust feature failed")
        elif (drag_traj == 3):
            y_index = np.where(
                np.array(self.toeposition_y_list) < -ground_height)[0]
            index = np.where(np.array(self.toeposition_x_list) > 0.001)[0]
            index = np.intersect1d(y_index, index)

            self.fpx.set_xdata(np.array(self.toeposition_x_list[index]))
            self.fpx.set_ydata(self.force_list_x[index])
            self.fpy.set_xdata(np.array(self.toeposition_x_list[index]))
            self.fpy.set_ydata(self.force_list_y[index])
            if (mode == 3):
                self.fpxl.set_xdata(np.array(self.toeposition_x_list[index]))
                self.fpxl.set_ydata(self.force_list_loadcell_x[index])
                self.fpyl.set_xdata(np.array(self.toeposition_x_list[index]))
                self.fpyl.set_ydata(self.force_list_loadcell_y[index])

        else:
            self.fpx.set_xdata(self.time_list)
            self.fpx.set_ydata(self.force_list_x)
            self.fpy.set_xdata(self.time_list)
            self.fpy.set_ydata(self.force_list_y)
        # print(self.time_list, self.force_list_x)
        if ((len(index)) > 0):
            self.fp.relim()
            self.fp.autoscale_view()
            self.fig4.canvas.draw()
            self.fig4.canvas.flush_events()

        self.speed_px.set_xdata(self.time_list)
        self.speed_px.set_ydata(self.toevelocity_x_list)
        self.speed_py.set_xdata(self.time_list)
        self.speed_py.set_ydata(self.toevelocity_y_list)
        self.speed_p.relim()
        self.speed_p.autoscale_view()
        self.fig5.canvas.draw()
        self.fig5.canvas.flush_events()

        self.ppp.set_xdata(self.toeposition_x_list)
        self.ppp.set_ydata(self.toeposition_y_list)
        self.pp.relim()
        self.pp.autoscale_view()
        self.fig6.canvas.draw()
        self.fig6.canvas.flush_events()

    def update_force_plot(self, real_time_plot_active, updateplotflag, drag_traj, mode, ground_height):
        if (real_time_plot_active and updateplotflag):
            self.update_plot(drag_traj, mode, ground_height)

    def update_force_data(self, updateplotflag, mode):
        if (updateplotflag):

            current_time = time.time() - self.start_time
            if (mode == 0):
                a, b = 0, 0
            else:
                try:
                    a, b = self.loadcell1.read_force()
                except:
                    a, b = 0, 0
            self.current_data = np.array([current_time, self.toeforce_x, -self.toeforce_y, a, b,
                                          self.toeposition_x, self.toeposition_y, self.toevelocity_x,
                                          self.toevelocity_y, self.position, self.position1, self.torque,
                                          self.torque1, self.theta_command, self.length_command, self.state_flag,
                                          self.running_curr])
            self.variable_array[self.num_data_points, :] = self.current_data
            self.num_data_points += 1
            print(self.num_data_points)
            print(self.variable_array)
            # print(len(self.force_list_loadcell_x), len(self.force_list_loadcell_y),len(self.time_list))

    # def data_append(self, start_flag, drag_traj)

    def download_data(self, file_name, node_id, real_time_plot, gui_message):

        path = "./experiment_data/leg/" + file_name + ".csv"

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        

        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)

            writer.writerow(["scenario", "real_time_plot", "extrude_speed_slider", "extrude_angle_slider", "extrude_length_slider", "down_length_slider", "down_speed_slider", "delay_after_down",
                            "shear_length", "shear_speed", "delay_after_shear", "back_speed",
                             "moving_speed", "moving_step_angle", "time_delay", "variable1", "variable3",  "search_start", "search_end", "ground_height", "extrude_back_speed"])
            writer.writerow([node_id, real_time_plot, gui_message[2], gui_message[3], gui_message[4], gui_message[5],
                             gui_message[6], gui_message[7], gui_message[8], gui_message[9],
                             gui_message[10], gui_message[11], gui_message[12], gui_message[13], gui_message[14], gui_message[15], gui_message[16], gui_message[17], gui_message[18], gui_message[19], gui_message[20]])

            writer.writerow(["time", "toeforce_x", "toeforce_y", "toeforce_x_loadcell", "toeforce_yloadcell",
                             "toe_position_x", "toe_position_y", "toe_velocity_x", "toe_velocity_y",
                             "position", "position1", "torque", "torque1",
                             "theta command", "length command", "state flag", "current"])
            for i in range(self.num_data_points-1):
                # print(i)
                writer.writerow(self.variable_array[i, :])

    def handle_joint_state(self, msg):
        self.temperature = 0
        self.controller_error = 0
        self.encoder_error = 0
        self.motor_error = 0
        self.position = msg.interface_values[0].values[1]
        self.torque = msg.interface_values[0].values[0]
        # self.motor_velocity_left = msg.interface_values[0].values[2]
        self.motor_velocity_left = 0

        self.temperature1 = 0
        self.controller_error1 = 0
        self.encoder_error1 = 0
        self.motor_error1 = 0
        self.position1 = msg.interface_values[1].values[1]
        self.torque1 = msg.interface_values[1].values[0]
        # self.motor_velocity_right = msg.interface_values[1].values[2]
        self.motor_velocity_right = 0

    def handle_travelerstate(self, msg):
        self.toeforce_x = msg.data[0]
        self.toeforce_y = msg.data[1]
        self.toeposition_x = msg.data[2]
        self.toeposition_y = msg.data[3]
        self.toevelocity_x = msg.data[4]
        self.toevelocity_y = msg.data[5]
        self.theta_command = msg.data[6]
        self.length_command = msg.data[7]
        self.state_flag = msg.data[8]
        # self.running_prev = self.running_curr
        # self.running_curr = msg.data[9]
        # print(self.toeforce_x)

    def get_angular_error(self):
        return self.angular_error

    def publish_gui_information(self, msg):
        self.publisher_.publish(msg)

    def save_data(self):
        pass

    def start_robot_leg(self):
        pass
