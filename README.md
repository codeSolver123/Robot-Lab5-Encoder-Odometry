# Robot– Encoder Odometry

This project focuses on measuring and verifying robot motion using wheel encoder counts
and distance feedback while commanding the robot to drive straight.

---

## Project Overview

The goal of this lab was to understand how encoder data and distance measurements
can be used to estimate robot movement. The robot is commanded to drive straight
for a fixed duration, after which encoder counts and reported distance are read
and analyzed.

---

## How It Works

### Control Logic
- Establishes a TCP socket connection to the robot controller
- Initializes the robot in full mode
- Commands the robot to drive straight at a fixed speed
- Stops the robot after a short duration

### Sensing and Odometry
A separate sensing thread continuously polls:
- Left wheel encoder counts
- Right wheel encoder counts
- Distance traveled (mm)

These values are used to verify that the robot moved forward as expected and to
compare encoder-based motion with the controller’s reported distance.

---

## Design Notes

- Socket access is protected with a shared lock to prevent race conditions
- Encoder values are parsed robustly to handle malformed or partial responses
- The program executes a single drive–stop cycle for repeatable testing

---

## Files

- `lab5Robot.py` — Drive-straight test with encoder and distance polling
