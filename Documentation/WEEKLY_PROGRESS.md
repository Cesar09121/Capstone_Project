# Capstone Project Weekly Progress

This document provides a weekly record of the progress made throughout the development of the Rover with Robotic Arm and Thermal Detection project. Each section summarizes the major tasks, accomplishments, and milestones completed during that week.

---

## Week 1 - Project Planning and Research

### Accomplishments

- Developed the initial concept for a remotely controlled rover equipped with a robotic arm, thermal detection, object detection, and a user interface.
- Researched how the different hardware and software components of the rover could communicate and operate together as a complete system.
- Researched potential components and materials required to construct the rover.
- Compared different hardware options based on cost, performance, compatibility, and effectiveness to keep the project within a reasonable budget while still meeting its requirements.
- Determined the general system architecture and responsibilities of the major components.
- Created the project's initial `README.md` file.
- Documented the major components, project goals, planned functionality, and development tasks required to complete the rover.
- Created a functional diagram showing how the major components of the rover system will interact.

### Week 1 Outcome

By the end of Week 1, the overall project concept and system design had been established. The required hardware and software components were identified, and an initial development plan was created to guide the construction and implementation of the rover.

---

## Week 2 - Component Acquisition and Initial Assembly

### Accomplishments

- Purchased the initial materials and components required to begin constructing the rover.
- Continued improving and reorganizing the project's `README.md` documentation.
- Corrected formatting and image display issues within the GitHub documentation.
- Began physical assembly of the robotic arm.
- Completed the initial assembly of the robotic arm and inspected the system for proper installation of its components.
- Powered and booted the robotic arm to verify that the controller and servos initialized correctly.
- Verified that the robotic arm successfully moved to its pre-programmed zero position during startup.
- Confirmed that the initial robotic arm hardware was functioning properly before beginning software integration and custom control development.

### Week 2 Outcome

By the end of Week 2, the project had progressed from the planning stage into initial hardware implementation. The robotic arm was assembled and successfully tested through its startup procedure, while the project documentation was further organized and improved.

---

## Week 3 - Robotic Arm Testing and Verification

### Accomplishments
- Installed and configured the Hiwonder LeArm PC control software and required serial driver.
- Connected the robotic arm to the computer and verified successful communication through the PC software.
- Checked the arm's calibration and confirmed that the servos returned to their expected neutral positions.
- Made a small adjustment to the gripper calibration so that the jaws properly align when closed.
- Tested individual servo movement using Slider Control Mode and confirmed that all six joints and the gripper operate correctly.
- Tested Coordinate Control Mode and verified that the arm can move the end effector using X, Y, and Z commands.
- Investigated the provided factory action-group files and determined that the downloaded files were designed for the BUS-servo version of the arm rather than the PWM-servo version being used.
- Avoided using the incompatible BUS-servo action files after confirming that they caused incorrect arm movement.
- Tested the included wireless controller and verified that the arm is capable of receiving remote-control commands through the controller and receiver.
- Confirmed that the provided Arduino software supports PWM servo control, which will be useful when custom arm control is implemented later.

### Week 3 Outcome

The robotic arm was successfully connected, calibrated, and tested through both the PC software and the included wireless controller. Individual joint control and coordinate-based movement were verified, confirming that the arm hardware and controller are functioning properly. Compatibility differences between the PWM and BUS-servo versions were also identified, which will help ensure that the correct software and commands are used when Raspberry Pi and PS5 controller integration begins.