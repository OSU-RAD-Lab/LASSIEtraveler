# LASSIE Traveler — Discovery Log

> Purpose: recoverable notes from a session that builds an understanding of the `src/` code,
> oriented around robot control with `lassie_gui.py`. The final deliverable is a human-readable
> `.md` inside `src/` describing the construction & control architecture so a new robot could be
> built along the same architecture.

## Status
- [x] Phase 0 — Repo inventory (2026-11-13)
- [x] Phase 1 — GUI (`lassie_gui.py`) control flow (2026-11-13)
- [ ] Phase 2 — Traveler controller (C++/ROS2)
- [ ] Phase 3 — Motor driver (odrive / ros2_control)
- [ ] Phase 4 — Write final architecture doc in `src/`

## Phase 0 — Repo inventory (discovered 2026-11-13)

### Top-level layout
- `src/` — ROS2 workspace sources (3 projects):
  - `LASSIE_ROBOT_GUI-v1.0/LASSIE_ROBOT_GUI-master/` — Python GUI (`LASSIE_GUI/lassie_gui.py` presumably), config, resource, experiment data
  - `LASSIE_TRAVELER_CONTROLLER-v1.0/LASSIE_TRAVELER_CONTROLLER-master/` — C++ ROS2 package `controller`
    - `src/controller/`: `Inverse_kinematics.cpp`, `controller_monitor.cpp`, `pid_speed_controller.cpp`, `trajectories_parser.cpp`
    - `src/proxy/`: `lowerproxy.cpp`, `upperproxy.cpp`
    - `src/`: `main.cpp`, `shearing.cpp`
    - `include/proxy/`: `control_data.h`, `lowerproxy.h`, `upperproxy.h`
    - `include/controller/`: `pid_speed_controller.h`, `trajectories_parser.h`
    - `include/utils/`: `lowpassfilter.hpp`, `traveler_utils.h`
    - `gait_parameter_scripts/`
  - `LASSIE_MOTOR_DRIVER-v1.0/LASSIE_MOTOR_DRIVER-master/` — ROS2 packages:
    - `odrive_hardware_interface` (ros2_control plugin)
    - `odrive_ros2_control`
    - `odrive_description` (urdf)
    - launch dir (odrive_bringup)

### Open questions
1. How does `lassie_gui.py` talk to the robot? ROS2 client? TCP? Direct CAN?
2. What is the "traveler" (mobile base) vs "shearing" (gripper/actuator) split?
3. What hardware is in the loop: ODrive motors, ESP32 CAN bridge, moisture sensor?
4. Trajectory format expected by `trajectories_parser`?

## Phase 1 — GUI discoveries (2026-11-13)

### What LASSIE is
`LASSIE_ROBOT_GUI` readme: **L**egged **A**utonomous **S**urface **S**cience in **A**nalogue **E**nvironments.
Goal: legged robots + embedded terrain sensing (direct-drive force sensing at the toe) +
human-robot collaborative decision making for planetary-like field science.

### GUI stack
- **Kivy 2.1.0 + KivyMD 0.104.2** (`depend.txt`), UI declarative in `resource/style.kv` (2074 lines).
- `lassie_gui.py` (841 ln) = `TravelerApp(MDApp)` + `DrawCanvasWidget(Widget)`.
- Matplotlib figures embedded via `kivy.garden.matplotlib.FigureCanvasKivyAgg`
  (force vs time/distance, toe speed, toe position trajectory).
- CLI: `python3 LASSIE_GUI/lassie_gui.py -m <mode>` where mode 0 = leg (field),
  1 = turtle (lab), 2 = minirhex (lab), 3 = leg + HX711 loadcell.
- `main()` builds a robot-specific rclpy node (`ControlNode_Leg` / turtle / MiniRhex) and passes it
  into `TravelerApp(node, ...)` — the GUI is robot-agnostic, the *interface node* carries robot logic.

### Control protocol (GUI ↔ robot) — pure ROS2 topics
- **GUI → robot:** publishes `std_msgs/Float64MultiArray` on topic **`/Gui_information`** (QoS 10).
  Packet layout (leg): `[0]=start_flag (1 start / 0 stop), [1]=drag_traj (scenario), [2..]=slider values`:
  extrude_speed(cm/s), extrude_angle(deg), extrude_length(cm), down_length, down_speed(cm/s),
  delay_after_down(s), shear_length(cm), shear_speed(cm/s), delay_after_shear(s), back_speed(cm/s),
  moving_speed(cm/s), moving_step_angle(deg), time_delay(s), variable1(cm), variable3(deg),
  search_start, search_end, ground_height(m), extrude_back_speed(cm/s)  (total 21 floats).
- **Robot → GUI:**
  - `control_msgs/DynamicJointState` on **`/dynamic_joint_states`** — per-motor
    `[0]=torque, [1]=position` (interface_values[0]=motor A, [1]=motor B).
  - `std_msgs/Float64MultiArray` on **`/travelerstate`** —
    `[0..5]=toe force x/y, toe pos x/y, toe vel x/y, [6]=theta_command, [7]=length_command, [8]=state_flag`.
- No services/actions: start/stop is a `start_flag` inside the same topic, re-published by every
  GUI interaction (each slider change triggers `publish_gui_information` with flag=0).

### Scenarios ("drag_traj" codes)
1 Extrude · 2 Traverse Workspace · 3 Penetrate & Shear · 4 Free Moving ·
5 turtle · 6 MiniRhex · 7 Detect Ground. GUI tab selection sets `drag_traj` + which slider card shows.

### GUI threading model (important pattern)
- Kivy main thread: UI + `Clock.schedule_interval(update_force_plot, 0.01)` (100 Hz plot refresh).
- Daemon thread `update_force_data`: 1 kHz loop sampling ROS-fed values into `variable_array[50000,17]`
  (columns: time, toeforce_x/y, toeforce_x/y_loadcell, toe_pos x/y, toe_vel x/y, pos/pos1/torque/torque1,
  theta_command, length_command, state_flag, current).
- Daemon thread `write_errors`: endless `rclpy.spin_once(node)` — this is what drives all subscriptions.
- Mode 3 also starts a loadcell calibration thread (HX711 over pyserial).
- On stop: final `update_plot`, stop+save camera recording, `download_data(...)` →
  `experiment_data/<robot>/<user>_<timestamp>.csv` (config header row + variable header + data rows).
- Config persistence: `config/last_config.csv` (written on stop/start, restored in `on_start`).

### Instrumentation
- `loadcell_hx711.py` (136 ln): HX711 load-cell driver over serial (2 axes: a,b forces) — external
  ground-truth force reference for the motor-estimated forces (mode 3 only).
- `logi_web_camera_record.py` / `logi_web_camera2_record.py`: Logi USB camera → `experiment_video/<robot>/camera_1/*.avi`
  via OpenCV (multi-camera optional via `multi_camera` flag).
- `crustProperties.py` (232 ln): fits crust/sand stiffness features (basinForce, sandStiffness,
  intercept) to the force-vs-depth plot — the "terrain science" analytics on live data.
- `DrawCanvasWidget`: 2-link planar leg (upper=100 px, lower=200 px, motor mount [500,350]) with
  analytic IK (`inverse_kinematics`), workspace annulus drawn from `|l2-l1|..l1+l2`, angle limits 45°..270°.
  Used to design toe trajectories (straight-line mode active; b-spline stubbed).
- `traveler_decision_making.py` (645 ln): not yet read — likely the human-decision-model side.

### Robot topology implied by GUI (traveler_leg)
- 2 joints driven by motors (pos/torque feedback per joint), 2-link leg, toe force estimated
  (motor torque-based) in x/y, toe kinematics (pos/vel) computed onboard, commands in
  (theta_command, length_command) = (angle, leg-length) space, plus a `state_flag` FSM reported back.
- Ground height (default 0.17 m) parameter for Detect-Ground scenario.

