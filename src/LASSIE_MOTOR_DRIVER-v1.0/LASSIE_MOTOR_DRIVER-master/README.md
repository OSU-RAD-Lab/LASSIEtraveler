<img align=right width=150px  src="logo.png" />

# LASSIE: Legged Autonomous Surface Science In Analogue Environments

Welcome to LASSIE! The overall study objective is to enhance scientific outcomes of robot-aided planetary explorations, by integrating high mobility legged robots with embedded
terrain-sensing technologies and cognitive human decision models. State-of-the-art rovers
and robots typically operate based on pre-programmed agenda, and have limited capabilities to: 

i) effectively detect unexpected changes in terrain properties and responses and adjust
locomotion or sampling strategies; 

ii) autonomously identify scientifically-valuable observations and adjust exploration strategies. 

Such inefficiency can lead to critical mobility
or sampling failures, and missed scientific discoveries. To bridge this gap, we propose to
integrate legged mobility, direct-drive embedded terrain-sensing, and human-robot collab-
orative decision-making workflow, to enable terrain-sensible, discovery-driven legged
robots that can effectively move, adaptively situate, and scientifically examine a wide range
of planetary environments. 

## 🛠 LASSIE_ROBOT_DRIVER
LASSIE_ROBOT_DRIVER is a repository that contains the low level driver for differnt robot we use including field robot and lab robot. 
- traveler_leg
- minirhex robot for lab
- turtle_robot for lab

## 🏫 Usage
- traveler_leg

hardware requirements: connects the odrive to your computer

run:
```
ros2 launch odrive_bringup odrive_bringup.launch
```
- minirhex robot

hardware requirements: connects the odrive board and servo board to your raspberry pi

```
ros2 run dynamixel_sdk_examples read_write_node
```
- turtle_robot

hardware requirements: connects the dynamixel shied to your computer through usb
```
ros2 launch odrive_bringup turtle_bringup.launch
```


## 📎 Useful commands
```
sudo chown qianlab /dev/ttyUSB0
```