#!/usr/bin/env python3
import sys
import csv
import os

sys.argv = [sys.argv[0]]


import threading
import time
import csv

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from control_msgs.msg import DynamicJointState
from std_msgs.msg import Float64MultiArray
from geometry_msgs.msg import Pose
from kivy.config import Config
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.image import Image
from kivy.properties import StringProperty
from kivy.uix.slider import Slider
from kivy.graphics import Color, Bezier, Line
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import *

Config.set('graphics', 'width', '2736')
Config.set('graphics', 'height', '1824')
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.behaviors import RoundedRectangularElevationBehavior
from kivymd.uix.list import OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import IRightBodyTouch, ILeftBody
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineAvatarListItem
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.icon_definitions import md_icons
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.list import TwoLineAvatarListItem
from kivymd.icon_definitions import md_icons
from kivymd.uix.selectioncontrol import MDCheckbox








import numpy as np
import matplotlib.pyplot as plt



class Card(MDCard, RoundedRectangularElevationBehavior):
    '''Implements a material design v3 card.'''

    text = StringProperty()

class IconListItem(OneLineIconListItem):
    icon = StringProperty()

class MyCheckbox(IRightBodyTouch, MDCheckbox):
    pass

class LeftCheckbox(ILeftBody,MDCheckbox):
    pass

class MyAvatar(ILeftBody, Image):
    pass


class ShearMoistureTab(MDFloatLayout, MDTabsBase):
    pass
    # def __init__(self, **kwargs):
    #     super(ShearMoistureTab, self).__init__(**kwargs)
        # self.ids.shearMoisturePlot.add_widget(FigureCanvasKivyAgg(plt.gcf()))


    # def __init__(self, points=[], loop=False, *args, **kwargs):
    #     super(ShearMoistureTab, self).__init__(*args, **kwargs)
    #     self.d = 10  # pixel tolerance when clicking on a point
    #     self.points = points
    #     self.loop = loop
    #     self.current_point = None  # index of point being dragged

    #     with self.canvas:
    #         Color(1.0, 0.0, 0.0)

    #         self.bezier = Bezier(
    #                 points=self.points,
    #                 segments=150,
    #                 loop=self.loop,
    #                 dash_length=100,
    #                 dash_offset=10)

    #         Color(1.0, 0.0, 1.0)
    #         self.line = Line(
    #                 points=self.points + self.points[:2],
    #                 dash_offset=10,
    #                 dash_length=100)

    #     s = Slider(y=0, pos_hint={'x': .3}, size_hint=(.7, None), height=50)
    #     s.bind(value=self._set_bezier_dash_offset)
    #     self.add_widget(s)

    #     s = Slider(y=50, pos_hint={'x': .3}, size_hint=(.7, None), height=50)
    #     s.bind(value=self._set_line_dash_offset)
    #     self.add_widget(s)

    # def _set_bezier_dash_offset(self, instance, value):
    #     # effect to reduce length while increase offset
    #     self.bezier.dash_length = 100 - value
    #     self.bezier.dash_offset = value

    # def _set_line_dash_offset(self, instance, value):
    #     # effect to reduce length while increase offset
    #     self.line.dash_length = 100 - value
    #     self.line.dash_offset = value

    # def on_touch_down(self, touch):
    #     if self.collide_point(touch.pos[0], touch.pos[1]):
    #         for i, p in enumerate(list(zip(self.points[::2],
    #                                        self.points[1::2]))):
    #             if (abs(touch.pos[0] - self.pos[0] - p[0]) < self.d and
    #                     abs(touch.pos[1] - self.pos[1] - p[1]) < self.d):
    #                 self.current_point = i + 1
    #                 return True
    #         return super(ShearMoistureTab, self).on_touch_down(touch)

    # def on_touch_up(self, touch):
    #     if self.collide_point(touch.pos[0], touch.pos[1]):
    #         if self.current_point:
    #             self.current_point = None
    #             return True
    #         return super(ShearMoistureTab, self).on_touch_up(touch)

    # def on_touch_move(self, touch):
        # if self.collide_point(touch.pos[0], touch.pos[1]):
        #     c = self.current_point
        #     if c:
        #         self.points[(c - 1) * 2] = touch.pos[0] - self.pos[0]
        #         self.points[(c - 1) * 2 + 1] = touch.pos[1] - self.pos[1]
        #         self.bezier.points = self.points
        #         self.line.points = self.points + self.points[:2]
        #         return True
        #     return super(ShearMoistureTab, self).on_touch_move(touch)
    #pass
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.samples = 512
    #     self.shearMoisturePlot = Graph()
    #     self.ids.shearMoisturePlot.add_widget(self.shearMoisturePlot)

    

class Tab(MDFloatLayout, MDTabsBase):
    pass

class QA0(Screen):
    def ansSelected(self,nextScreen):
        self.nextScreen = nextScreen


    def changeScreen(self):
        self.manager.current = self.nextScreen
    # def checkbox_click(self,instance,value,topping):
    #     pass
    pass

class QA1(Screen):
    # def checkbox_click(self,instance,value,topping):
    #     pass
    pass

class QA2(Screen):
    pass



class QuestionManager(ScreenManager):
    pass



class ControlNode_Turtle(Node):
    def __init__(self):
        super().__init__('control_node')
        self.id = "turtle"
        self.publisher_ = self.create_publisher(Float64MultiArray, '/Gui_information', 10)
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

        self.Servo_Position_Left = self.create_subscription(
            Float64MultiArray,
            '/traveler_servo_big_1',
            self.ServoTurtleStateLeft,
            10)

        self.Servo_Position_Right = self.create_subscription(
            Float64MultiArray,
            '/traveler_servo_big_2',
            self.ServoTurtleStateRight,
            10)

        self.turtle_subscriber = self.create_subscription(
            Float64MultiArray,
            '/turtle_status',
            self.turtle_status,
            10)

        self.Optitrack_State = self.create_subscription(
            Pose,
            '/optitrack',
            self.OptitrackState,
            10)
        

        ## some parameters to specify here
        self.tab_control = ['turtle']

        
        self.temperature = 0.0
        self.controller_error = 0.0
        self.encoder_error = 0.0
        self.motor_error = 0.0
        self.position = 0.0
        self.torque = 0.0

        self.motor_velocity_left = 0.0
        self.ServoPositionLeft = 0.0
        self.toeforce_left = 0.0

        self.temperature1 = 0.0
        self.controller_error1 = 0.0
        self.encoder_error1 = 0.0
        self.motor_error1 = 0.0
        self.position1 = 0.0
        self.torque1 = 0.0

        self.motor_velocity_right = 0.0
        self.ServoPositionRight = 0.0
        self.toeforce_right = 0.0

        self.OptitrackPosition_x = 0.0
        self.OptitrackPosition_y = 0.0
        self.OptitrackPosition_z = 0.0
        self.OptitrackOrientation_x = 0.0
        self.OptitrackOrientation_y = 0.0
        self.OptitrackOrientation_z = 0.0
        self.OptitrackOrientation_w = 0.0
        


        self.toeforce_x = 0
        self.toeforce_y = 0
        self.toeposition_x = 0
        self.toeposition_y = 0
        self.toevelocity_x = 0
        self.toevelocity_y = 0
        
        self.ServoPositionLeft = 0
        self.ServoPositionRight = 0
        self.toeforce_right = 0

        self.OptitrackPosition_x = 0
        self.OptitrackPosition_y = 0
        self.OptitrackPosition_z = 0
        self.OptitrackOrientation_x = 0
        self.OptitrackOrientation_y = 0
        self.OptitrackOrientation_z = 0
        self.OptitrackOrientation_w = 0
        self.turtle_state = 0



        self.control_message = Float64MultiArray()
        self.drag_times = Float64MultiArray()
        self.drag_traj = Float64MultiArray()
        self.drag_angle = Float64MultiArray()
        self.static_length = Float64MultiArray()
        self.static_angle = Float64MultiArray()

        # print('aefasdf')
        self.force_list_x = []
        self.force_list_y = []
        self.start_time = time.time()
        self.time_list = []
        self.motor_position1_list = []
        self.motor_torque_right_list = []
        self.motor_position_list = []
        self.motor_torque_left_list = []

        self.servo_position_left_list = []
        self.servo_position_right_list = []
        self.motor_velocity_left_list = []
        self.motor_velocity_right_list = []
        self.toeforce_left_list = []
        self.toeforce_right_list =[]

        self.OptitrackPosition_x_list = []
        self.OptitrackPosition_y_list = []
        self.OptitrackPosition_z_list = []
        self.OptitrackOrientation_x_list = []
        self.OptitrackOrientation_y_list = []
        self.OptitrackOrientation_z_list = []
        self.OptitrackOrientation_w_list = []

        self.temperature_LeftMotor_list = []
        self.temperature_RightMotor_list = []
        self.toeposition_x_list = []
        self.toeposition_y_list = []
        self.toevelocity_x_list = []
        self.toevelocity_y_list = []

        self.turtle_state_list = []

        self.fpx = None
        self.fpy = None
        self.fpz = None
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
        self.fp.set_title('displacements Measurements vs Time', fontsize=10)
        self.fp.set_xlabel('Time(t)', fontsize=10)
        self.fp.set_ylabel('Distance(m)', fontsize=10)
        self.fp.grid(True)
        self.fpx, = self.fp.plot([],[], 'r', linewidth=3)
        self.fpy, = self.fp.plot([],[], 'g', linewidth=3)
        self.fpz, = self.fp.plot([],[], 'b', linewidth=3)
        self.fp.legend(['x','y','z'])
        self.fig5, self.speed_p = plt.subplots()
        self.speed_p.set_title('Speed vs time', fontsize=10)
        self.speed_p.set_xlabel('Time(t)', fontsize=10)
        self.speed_p.set_ylabel('Speed(m/s)', fontsize=10)
        self.speed_p.grid(True)
        self.speed_px, = self.speed_p.plot([],[], 'r', linewidth=3)
        self.speed_py, = self.speed_p.plot([],[], 'g', linewidth=3)
        self.speed_p.legend(['x','y'])
        self.fig6, self.pp = plt.subplots()
        self.pp.set_title('position trajectories', fontsize=10)
        self.pp.set_xlabel('X', fontsize=10)
        self.pp.set_ylabel('Y', fontsize=10)
        self.pp.grid(True)
        self.ppp, = self.pp.plot([],[], 'r', linewidth=3)

    def calibrate(self):
        self.start_time = time.time()
        self.force_list_x = []
        self.force_list_y = []
        self.time_list = []
        self.position1_list = []
        self.torque1_list = []
        self.position_list = []
        self.torque_list = []
        self.temperature_list = []
        self.temperature1_list = []
        self.toeposition_x_list = []
        self.toeposition_y_list = []
        self.toevelocity_x_list = []
        self.toevelocity_y_list = []
        self.OptitrackPosition_x_list = []
        self.OptitrackPosition_y_list = []
        self.OptitrackPosition_z_list = []
        self.OptitrackOrientation_x_list = []
        self.OptitrackOrientation_y_list = []
        self.OptitrackOrientation_z_list = []
        self.OptitrackOrientation_w_list = []
        self.turtle_state_list = []




    def get_fp(self):
        return self.fp
    
    def get_pp(self):
        return self.pp
    
    def get_speed_p(self):
        return self.speed_p


    def update_plot(self):
        self.fpx.set_xdata(self.time_list)
        self.fpx.set_ydata(self.OptitrackPosition_x_list)
        self.fpy.set_xdata(self.time_list)
        self.fpy.set_ydata(self.OptitrackPosition_y_list)
        self.fpz.set_xdata(self.time_list)
        self.fpz.set_ydata(self.OptitrackPosition_z_list)
        # print(self.time_list, self.force_list_x)
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
      
    def update_force_plot(self, real_time_plot_active, updateplotflag):
        if (real_time_plot_active and updateplotflag):
            self.update_plot()
    def update_force_data(self, updateplotflag):
        # self.run_time += 1
        # # print(self.run_time)
        # print('frequency: ', self.run_time/(time.time()-self.start_time) )       
        if(updateplotflag):
            current_time = time.time() - self.start_time
            self.time_list.append(current_time)

            self.force_list_x.append(self.toeforce_x)
            self.force_list_y.append(self.toeforce_y)
            self.motor_position1_list.append(self.position1)
            self.motor_torque_right_list.append(self.torque1)
            self.motor_position_list.append(self.position)
            self.motor_torque_left_list.append(self.torque)

            self.motor_velocity_left_list.append(self.motor_velocity_left)
            self.motor_velocity_right_list.append(self.motor_velocity_right)
            self.servo_position_left_list.append(self.ServoPositionLeft)
            self.servo_position_right_list.append(self.ServoPositionRight)
            

            self.toeforce_left_list.append(self.toeforce_left)
            self.toeforce_right_list.append(self.toeforce_right)

            self.OptitrackPosition_x_list.append(self.OptitrackPosition_x)
            self.OptitrackPosition_y_list.append(self.OptitrackPosition_y)
            self.OptitrackPosition_z_list.append(self.OptitrackPosition_z)
            self.OptitrackOrientation_x_list.append(self.OptitrackOrientation_x)
            self.OptitrackOrientation_y_list.append(self.OptitrackOrientation_y)
            self.OptitrackOrientation_z_list.append(self.OptitrackOrientation_z)
            self.OptitrackOrientation_w_list.append(self.OptitrackOrientation_w)
            
            


            self.temperature_LeftMotor_list.append(self.temperature)
            self.temperature_RightMotor_list.append(self.temperature1)
            self.toeposition_x_list.append(self.toeposition_x)
            self.toeposition_y_list.append(self.toeposition_y)
            self.toevelocity_x_list.append(self.toevelocity_x)
            self.toevelocity_y_list.append(self.toevelocity_y)

            self.turtle_state_list.append(self.turtle_state)


    def download_data(self, file_name, node_id, real_time_plot, gui_message ):

        path = "./experiment_data/turtle/" + file_name + ".csv"

        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, 'w', newline='') as f:
            
            writer=csv.writer(f)
          
            writer.writerow(["scenario","real_time_plot", "lateral_angle_range","drag_speed", "wiggle_time", "servo_speed", "extraction_height", "wiggle frequency",
                            "insertion_angle", "wiggle_amplitude"])
            writer.writerow([node_id, real_time_plot, gui_message[2],gui_message[3],gui_message[4],gui_message[5],
                                 gui_message[6],gui_message[7],gui_message[8],gui_message[9]])
            
            writer.writerow(["time", "turtle_state",
                                "Motor_Velocity_Left","Motor_Velocity_Right",
                                "Servo_Postion_Left", "Servo_Position_Right",
                                "Motor_Position_Left", "Motor_Position_Right",
                                "Motor_Torque_Left", "Motor_Torque_Right",
                                "OptitrackPosition_x","OptitrackPosition_y","OptitrackPosition_z",
                                "OptitrackOrientation_x", "OptitrackOrientation_y", "OptitrackOrientation_z", "OptitrackOrientation_w"])
            
            
            for i in range(len(self.time_list)):
                writer.writerow([self.time_list[i],  self.turtle_state_list[i],
                                self.motor_velocity_left_list[i], self.motor_velocity_right_list[i],
                                self.servo_position_left_list[i], self.servo_position_right_list[i],
                                self.motor_position_list[i], self.motor_position1_list[i],
                                self.motor_torque_left_list[i], self.motor_torque_right_list[i],
                                self.OptitrackPosition_x_list[i],self.OptitrackPosition_y_list[i],self.OptitrackPosition_z_list[i],
                                self.OptitrackOrientation_x_list[i], self.OptitrackOrientation_y_list[i],
                                self.OptitrackOrientation_z_list[i], self.OptitrackOrientation_w_list[i]])


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
        # print(msg.interface_values[0].values[2])

    def ServoTurtleStateLeft(self, msg):
        self.ServoPositionLeft = msg.data[0]
        
    def ServoTurtleStateRight(self, msg):
        self.ServoPositionRight = msg.data[0]

    def turtle_status(self, msg):
        self.turtle_state = msg.data[0]


    def OptitrackState(self, msg):
        self.OptitrackPosition_x = msg.position.x
        self.OptitrackPosition_y = msg.position.y
        self.OptitrackPosition_z = msg.position.z
        self.OptitrackOrientation_x = msg.orientation.x
        self.OptitrackOrientation_y = msg.orientation.y
        self.OptitrackOrientation_z = msg.orientation.z
        self.OptitrackOrientation_w = msg.orientation.w

        

    def handle_travelerstate(self, msg):
        self.toeforce_x = msg.data[0]
        self.toeforce_y = msg.data[1]
        self.toeposition_x = msg.data[2]
        self.toeposition_y = msg.data[3]
        self.toevelocity_x = msg.data[4]
        self.toevelocity_y = msg.data[5]
        



    def get_angular_error(self):
        return self.angular_error

    def publish_gui_information(self, msg):
        self.publisher_.publish(msg)

    # def publish_control_msg(self, msg):
    #     self.publisher_.publish(msg)
    # def publish_drag_times(self, msg):
    #     self.publisher_2.publish(msg)
    # def publish_drag_angle(self, msg):
    #     self.publisher_4.publish(msg)
    # def publish_drag_traj(self, msg):
    #     self.publisher_3.publish(msg)
    # def publish_static_angle(self, msg):
    #     self.publisher_5.publish(msg)
    # def publish_static_length(self, msg):
    #     self.publisher_6.publish(msg)
    def save_data(self):
        pass

    def start_robot_leg(self):
        pass



class Card(MDCard, RoundedRectangularElevationBehavior):
    '''Implements a material design v3 card.'''

    text = StringProperty()

class IconListItem(OneLineIconListItem):
    icon = StringProperty()

class MyCheckbox(IRightBodyTouch, MDCheckbox):
    pass


class MyAvatar(ILeftBody, Image):
    pass


# class TravelerApp(MDApp):

#     def __init__(self, node):
#         super().__init__()
#         self.start_robot = False
#         self.theme_cls.theme_style = "Light" 
#         self.theme_cls.primary_palette  = "DeepOrange"
        
#         self.screen = Builder.load_file('resource/style.kv')
#         menu_items = [
#             {
#                 "viewclass": "IconListItem",
#                 "icon": "git",
#                 "text": "Right Triangle",
#                 "height": dp(60),
#                 "on_release": lambda x="Right Triangle": self.set_item(x),
#             },
#             {
#                 "viewclass": "IconListItem",
#                 "icon": "git",
#                 "text": "Extrude",
#                 "height": dp(60),
#                 "on_release": lambda x="Extrude": self.set_item(x),
#             }
#         ]
#         self.menu = MDDropdownMenu(
#             caller=self.screen.ids.drop_item,
#             items=menu_items,
#             position="center",
#             width_mult=4,
#         )


#         self.screen.ids.shearMoisturePlot.add_widget(FigureCanvasKivyAgg(smp.get_figure()))
#         self.screen.ids.shearStrengthPlot.add_widget(FigureCanvasKivyAgg(ssp.get_figure()))
#         self.screen.ids.moisturePlot.add_widget(FigureCanvasKivyAgg(mp.get_figure()))
#         self.screen.ids.rawForcePlot.add_widget(FigureCanvasKivyAgg(fp.get_figure()))
#         self.screen.ids.positionplot.add_widget(FigureCanvasKivyAgg(pp.get_figure()))
#         self.screen.ids.speedplot.add_widget(FigureCanvasKivyAgg(speed_p.get_figure()))
#         self.menu.bind()
#         self.control_message = Float64MultiArray()
#         self.drag_times = Float64MultiArray()
#         self.drag_traj = Float64MultiArray()
#         self.drag_angle = Float64MultiArray()
#         self.static_length = Float64MultiArray()
#         self.static_angle = Float64MultiArray()

#         # print('aefasdf')
#         self.ros_node = node
#         self.updateplotflag = False
#         self.force_list_x = []
#         self.force_list_y = []
#         self.start_time = time.time()
#         self.time_list = []
#         self.motor_position1_list = []
#         self.motor_torque_right_list = []
#         self.motor_position_list = []
#         self.motor_torque_left_list = []

#         self.servo_position_left_list = []
#         self.servo_position_right_list = []
#         self.motor_velocity_left_list = []
#         self.motor_velocity_right_list = []
#         self.toeforce_left_list = []
#         self.toeforce_right_list =[]

#         self.OptitrackPosition_x_list = []
#         self.OptitrackPosition_y_list = []
#         self.OptitrackPosition_z_list = []
#         self.OptitrackOrientation_x_list = []
#         self.OptitrackOrientation_y_list = []
#         self.OptitrackOrientation_z_list = []
#         self.OptitrackOrientation_w_list = []

#         self.temperature_LeftMotor_list = []
#         self.temperature_RightMotor_list = []
#         self.toeposition_x_list = []
#         self.toeposition_y_list = []
#         self.toevelocity_x_list = []
#         self.toevelocity_y_list = []
        
#     def set_item(self, text_item):
#         self.screen.ids.drop_item.text = text_item
#         self.menu.dismiss()
        
#     def build(self):
#         Clock.schedule_interval(self.update_force_plot, 0.001)
#         self.errors_writer = threading.Thread(target=self.write_errors)
#         self.errors_writer.start()
#         return self.screen
    
#     def update_force_plot(self, *args):
        
#         if(self.updateplotflag):
#             current_time = time.time() - self.start_time
#             self.time_list.append(current_time)
            
#             self.force_list_x.append(self.ros_node.toeforce_x)
#             self.force_list_y.append(self.ros_node.toeforce_y)
#             self.motor_position1_list.append(self.ros_node.position1)
#             self.motor_torque_right_list.append(self.ros_node.torque1)
#             self.motor_position_list.append(self.ros_node.position)
#             self.motor_torque_left_list.append(self.ros_node.torque)

#             self.motor_velocity_left_list.append(self.ros_node.motor_velocity_left)
#             self.motor_velocity_right_list.append(self.ros_node.motor_velocity_right)
#             self.servo_position_left_list.append(self.ros_node.ServoPositionLeft)
#             self.servo_position_right_list.append(self.ros_node.ServoPositionRight)
            

#             self.toeforce_left_list.append(self.ros_node.toeforce_left)
#             self.toeforce_right_list.append(self.ros_node.toeforce_right)

#             self.OptitrackPosition_x_list.append(self.ros_node.OptitrackPosition_x)
#             self.OptitrackPosition_y_list.append(self.ros_node.OptitrackPosition_y)
#             self.OptitrackPosition_z_list.append(self.ros_node.OptitrackPosition_z)
#             self.OptitrackOrientation_x_list.append(self.ros_node.OptitrackOrientation_x)
#             self.OptitrackOrientation_y_list.append(self.ros_node.OptitrackOrientation_y)
#             self.OptitrackOrientation_z_list.append(self.ros_node.OptitrackOrientation_z)
#             self.OptitrackOrientation_w_list.append(self.ros_node.OptitrackOrientation_w)
            
            


#             self.temperature_LeftMotor_list.append(self.ros_node.temperature)
#             self.temperature_RightMotor_list.append(self.ros_node.temperature1)
#             self.toeposition_x_list.append(self.ros_node.toeposition_x)
#             self.toeposition_y_list.append(self.ros_node.toeposition_y)
#             self.toevelocity_x_list.append(self.ros_node.toevelocity_x)
#             self.toevelocity_y_list.append(self.ros_node.toevelocity_y)
#             # print(self.motor_position1_list)
#             # print(self.force_list_x)
#             # print(self.force_list_x)
#             fpx.set_xdata(self.time_list)
#             fpx.set_ydata(self.force_list_x)
#             fpy.set_xdata(self.time_list)
#             fpy.set_ydata(self.force_list_y)
#             fp.relim()
#             fp.autoscale_view()
#             fig4.canvas.draw()
#             fig4.canvas.flush_events()


#             speed_px.set_xdata(self.time_list)
#             speed_px.set_ydata(self.toevelocity_x_list)
#             speed_py.set_xdata(self.time_list)
#             speed_py.set_ydata(self.toevelocity_y_list)
#             speed_p.relim()
#             speed_p.autoscale_view()
#             fig5.canvas.draw()
#             fig5.canvas.flush_events()


#             ppp.set_xdata(self.toeposition_x_list)
#             ppp.set_ydata(self.toeposition_y_list)
#             pp.relim()
#             pp.autoscale_view()
#             fig6.canvas.draw()
#             fig6.canvas.flush_events()




#     def write_errors(self):
#         # self.ros_get_logger().info('Im inside the thread')
#         while(True):
#             self.screen.ids.temperature.value = self.ros_node.temperature
#             self.screen.ids.temperature_text.text = str(self.ros_node.temperature)
#             self.screen.ids.controller_error.text = str(self.ros_node.controller_error)
#             self.screen.ids.controller_error.text = str(self.ros_node.encoder_error)
#             self.screen.ids.controller_error.text = str(self.ros_node.motor_error)
#             # self.screen.ids.error_distance.text = str(self.ros_node.get_linear_error())
#             # self.screen.ids.error_angle.text = str(self.ros_node.get_angular_error())
#             rclpy.spin_once(self.ros_node)

#     def on_change_speed(self):
        
#         self.screen.ids.drag_speed_text.text = str(round(self.screen.ids.drag_speed.value))
#     def on_change_angle(self):
        
#         self.screen.ids.drag_angle_text.text = str(round(self.screen.ids.extrude_angle.value))
#     def on_change_drag_time(self):
        
#         self.screen.ids.drag_times_text.text = str(round(self.screen.ids.drag_times.value))
#     def on_change_static_length(self):
        
#         self.screen.ids.static_length_text.text = str(round(self.screen.ids.static_length.value))
#     def on_change_static_angle(self):
        
#         self.screen.ids.static_angle_text.text = str(round(self.screen.ids.static_angle.value))
#     def on_stop(self):
#         pass
#     def check_if_start(self):
#         if(self.start_robot == True):
#             print('end to sampling')
#             self.start_robot = False
#             self.updateplotflag = False
#             self.control_message.data.append(3)
#             self.drag_times.data.append(0)
#             self.drag_angle.data.append(0)
#             self.drag_traj.data.append(1)
#             self.publish(self.control_message)
#             self.publish_drag_times(self.drag_times)
#         else:
#             print('start to sampling')
#             self.updateplotflag = True
#             self.start_time = time.time()
#             self.start_robot = True
#             self.force_list_x = []
#             self.force_list_y = []
#             self.time_list = []
#             self.motor_position1_list = []
#             self.motor_torque_right_list = []
#             self.motor_position_list = []
#             self.motor_torque_left_list = []

#             self.servo_position_left_list = []
#             self.servo_position_right_list = []
#             self.motor_velocity_left_list = []
#             self.motor_velocity_right_list = []
#             self.toeforce_left_list = []
#             self.toeforce_right_list =[]

#             self.OptitrackPosition_x_list = []
#             self.OptitrackPosition_y_list = []
#             self.OptitrackPosition_z_list = []
#             self.OptitrackOrientation_x_list = []
#             self.OptitrackOrientation_y_list = []
#             self.OptitrackOrientation_z_list = []
#             self.OptitrackOrientation_w_list = []


#             self.temperature_LeftMotor_list = []
#             self.temperature_RightMotor_list = []
#             self.toeposition_x_list = []
#             self.toeposition_y_list = []
#             self.toevelocity_x_list = []
#             self.toevelocity_y_list = []


#             self.control_message.data.append(float(self.screen.ids.drag_speed_text.text))
#             self.publish(self.control_message)
#             self.drag_times.data.append(float(self.screen.ids.drag_times_text.text))
#             self.drag_angle.data.append(float(self.screen.ids.drag_angle_text.text))
#             self.static_length.data.append(float(self.screen.ids.static_length_text.text))
#             self.static_angle.data.append(float(self.screen.ids.static_angle_text.text))
#             # print(self.screen.ids.drop_item.text)
#             if(self.screen.ids.drop_item.text == "Right Triangle"):
#                 self.drag_traj.data.append(1.0)
#                 print('publish1')
#             elif(self.screen.ids.drop_item.text == "Extrude"):
#                 self.drag_traj.data.append(2.0)
#                 print('publish2')
#             else:
#                 self.drag_traj.data.append(0.0)
#             self.publish_drag_times(self.drag_times)
#             self.publish_drag_angle(self.drag_angle)
#             self.publish_drag_traj(self.drag_traj)
#             self.publish_static_length(self.static_length)
#             self.publish_static_angle(self.static_angle)

#     def on_connect_to_robot(self):
#         ip = self.screen.ids.ipaddress.text
#         # print(type(ip))
#         try:
#             ssh.connect(str(ip),port,user,password,timeout = 10)
#         except:
#             print("connected failed")
#         finally:
#             print("connected successfully!")

#     def on_run_low_controller(self):
#         stdin,stdout,stderr = ssh.exec_command(
#             "cd Traveler_Odrive_Lower_Control && . install/setup.bash && ros2 launch odrive_bringup odrive.launch.py")
#         result = str(stdout.read(), encoding = "utf-8")
#         self.root.ids.low_log.add_widget(MDLabel(text=re.sub('\s',' ',str(result)), font_style="H5"))
        
        
        
#     def on_download_data(self):
#         path = "./experiment_data/" + str(time.asctime( time.localtime(time.time()) )) + ".csv"
#         with open(path, 'w', newline='') as f:
            
#             writer=csv.writer(f)
#             writer.writerow(["time","Temperature_LeftMotor","Temperature_RightMotor", 
#                                 "Toeforce_Left", "Toeforce_Right",
#                                 "Motor_Velocity_Left","Motor_Velocity_Right",
#                                 "Servo_Postion_Left", "Servo_Position_Right",
#                                 "Motor_Position_Left", "Motor_Position_Right",
#                                 "Motor_Torque_Left", "Motor_Torque_Right",
#                                 "OptitrackPosition_x","OptitrackPosition_y","OptitrackPosition_z",
#                                 "OptitrackOrientation_x", "OptitrackOrientation_y", "OptitrackOrientation_z", "OptitrackOrientation_w"])
            
            
#             for i in range(len(self.time_list)):
#                 writer.writerow([self.time_list[i],  self.temperature_LeftMotor_list[i], self.temperature_RightMotor_list[i], 
#                                 self.toeforce_left_list[i], self.toeforce_right_list[i],
#                                 self.motor_velocity_left_list[i], self.motor_velocity_right_list[i],
#                                 self.servo_position_left_list[i], self.servo_position_right_list[i],
#                                 self.motor_position_list[i], self.motor_position1_list[i],
#                                 self.motor_torque_left_list[i], self.motor_torque_right_list[i],
#                                 self.OptitrackPosition_x_list[i],self.OptitrackPosition_y_list[i],self.OptitrackPosition_z_list[i],
#                                 self.OptitrackOrientation_x_list[i], self.OptitrackOrientation_y_list[i],
#                                 self.OptitrackOrientation_z_list[i], self.OptitrackOrientation_w_list[i]])

#     def publish(self, msg):
#         self.ros_node.publish_control_msg(msg)

#     def publish_drag_times(self, msg):
#         self.ros_node.publish_drag_times(msg)

#     def publish_drag_angle(self, msg):
#         self.ros_node.publish_drag_angle(msg)
#     def publish_drag_traj(self, msg):
#         self.ros_node.publish_drag_traj(msg)

#     def publish_static_angle(self, msg):
#         self.ros_node.publish_static_angle(msg)
#     def publish_static_length(self, msg):
#         self.ros_node.publish_static_length(msg)
#     def on_start(self):
#          pass
#         #self.root.ids.datafiguretabs.add_widget(ShearMoistureTab(title="Shear vs. Mositure"))    
#         #self.root.ids.datafiguretabs.add_widget(Tab(title="Shear Strength"))
#         #self.root.ids.datafiguretabs.add_widget(Tab(title="Moisture"))

#     #     for i in range(5):
#     #         self.root.ids.selection_list.add_widget(MyItem())
#     #         # self.root.ids.traveler_picture.add_widget(Card())
#     #         # self.root.ids.traveler_picture.add_widget(Card())
#     #         # self.root.ids.traveler_picture.add_widget(Card())
    
#     def on_tab_switch(
#         self, instance_tabs, instance_tab, instance_tab_label, tab_text
#     ):
#         pass
#         # '''Called when switching tabs.

#         # :type instance_tabs: <kivymd.uix.tab.MDTabs object>;
#         # :param instance_tab: <__main__.Tab object>;
#         # :param instance_tab_label: <kivymd.uix.tab.MDTabsLabel object>;
#         # :param tab_text: text or name icon of tab;
#         # '''
#         # instance_tab.ids.datafigurelabel.text = tab_text



def main(args=None):
    rclpy.init(args=args)

    ros_node = controlNode()
    app = TravelerApp(ros_node)
    
    app.run()
    

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    #uwbPub.destroy_node()
    rclpy.shutdown()
    ros_node.destroy_node()


if __name__ == '__main__':
    main()
