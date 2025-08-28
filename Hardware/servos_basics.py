"""
Step 2: Basic Servo Movement Script

Uses the cvzone library to send in angles to your arduino board for
the 3 servos motors

"""
# ------------------- Import Libraries -------------------

from cvzone.SerialModule import SerialObject  # Import the SerialObject for serial communication with Arduino
from time import sleep  # Import sleep to add delays between actions

# ------------------- Initializations -------------------

# Create a Serial object with three digits precision for sending servo angles
arduino = SerialObject("/dev/tty.usbmodem101", digit=3)


# Initialize the last known positions for the three servos: Left (LServo), Right (RServo), Head (HServo)
# LServo starts at 180 degrees, RServo at 0 degrees, and HServo at 90 degrees
last_positions = [0, 0, 90]
#                [LServo , RServo ,HServo ]

# ------------------- Functions -------------------

# Function to smoothly move servos to target positions
def move_servo(target_positions, delay=0.0001):
    """
    Moves the servos smoothly to the target positions.

    :param target_positions: List of target angles [LServo, RServo, HServo]
    :param delay: Time delay (in seconds) between each incremental step
    """
    global last_positions  # Use the global variable to track servo positions
    # Calculate the maximum number of steps required for the largest position difference
    max_steps = max(abs(target_positions[i] - last_positions[i]) for i in range(3))

    # Incrementally move each servo to its target position over multiple steps
    for step in range(max_steps):
        # Calculate the current position of each servo at this step
        current_positions = [
            last_positions[i] + (step + 1) * (target_positions[i] - last_positions[i]) // max_steps
            if abs(target_positions[i] - last_positions[i]) > step else last_positions[i]
            for i in range(3)
        ]
        # Send the calculated positions to the Arduino
        arduino.sendData(current_positions)
        # Introduce a small delay to ensure smooth motion
        sleep(delay)

    # Update the last known positions to the target positions
    last_positions = target_positions[:]

def hello_gesture():
  """
  Makes robot wave hello by moving the right servo back and forth.
  """
  global last_positions
  # Move right arm to start waving
  move_servo([last_positions[0], 180, last_positions[2]])
  for _ in range(3):  # Perform the waving motion 3 times
     move_servo([last_positions[0], 150, last_positions[2]])  # Move arm slightly down
     move_servo([last_positions[0], 100, last_positions[2]])  # Move arm back up
  # Reset arm to original position
  move_servo([last_positions[0], 0, last_positions[2]])

def cute_shy_gesture():
    """
    A cute, shy gesture where the robot tilts its head and raises both arms.
    """
    global last_positions

    # Step 1: Tilt head slightly right
    move_servo([0, 0, 70], delay=0.005)  # Tilt head to 70 degrees

    # Step 2: Raise both arms slowly
    move_servo([120, 130, 80], delay=0.005)  # L arm up, R arm partially up

    # Step 3: Pause and 'hold the blush'
    sleep(1.0)

    # Step 4: Wiggle slightly like embarrassed
    move_servo([120, 120, 90], delay=0.005)
    move_servo([110, 110, 70], delay=0.005)
    move_servo([120, 120, 90], delay=0.005)
    move_servo([110, 110, 80 ], delay=0.005)


    # Step 5: Reset back to idle position
    move_servo([0, 0, 90], delay=0.005)



# --------------------Answer gesture-----------------------

def answer_gesture():
    """
    Makes Robot wave hand and head while answering.
    """
    global last_positions
    # Move right arm to start wave
    move_servo([last_positions[0],120,last_positions[2]])

    for _ in range(4):
        move_servo([last_positions[0], 150, last_positions[2]])  # Move right arm slightly down
        move_servo([last_positions[0], 110, last_positions[2]])  # Move right arm back up
        move_servo([last_positions[0], 150, 70])
        move_servo([last_positions[0], 110, 90])
     # Reset arm to original position
    move_servo([last_positions[0], 0, last_positions[2]])

# ------------------- Main Loop -------------------
while True:
   cute_shy_gesture()










