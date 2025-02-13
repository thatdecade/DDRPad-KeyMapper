# DDR Game Dance Pad to Keyboard Mapper

This script maps a HID "USB Input Device" button presses to keyboard key presses in real-time. 

* Reads raw data from any HID USB Device (not just gamepads)
* Configurable button map to decode button presses from raw USB reports  
* Simulates keyboard input to work in any game  

Implementation is a proof of concept. Good enough for my game skill level at least. Polling could be faster using direct OS event injection, submit a pull request if you have a better way.

---

### Requirements
- Python 3.x  
- pip install hidapi pynput

### Setup and Usage
Remember: **Press Ctrl+C to exit**

1. **Find HID device**  
   - Run the following command to list all connected HID devices:  
     ```sh
     python ddr2key.py --all-hid
     ```
   - Find your device's VID and PID in the output.
   - Create a keymap.json file (see template) and update VID and PID to match your gamepad.

2. **Review Button Presses for Mapping**  
   - Now run the script in debug mode to see button presses:  
     ```sh
     python ddr2key.py --print-buttons
     ```
   - Press each button on the gamepad and note which button is which name.
   - Modify `keymap.json` to map buttons to the desired keyboard keys.

3. **Play your Game!**  
   - Now run the script in normal mode to to play your game:  
     ```sh
     python ddr2key.py
     ```
---

**Why Was This Written?**

My old DDRGame dance pad is detected in Windows as a **generic HID input device** rather than a proper game controller.  This prevented its use in StepMania. 

I tested my pad on [HardwareTester.com](https://hardwaretester.com/gamepad),  which confirmed the dance pad was sending inputs, but it wasn't detected by Joy2Key.  JoyToKey reported 0 Joystick Detected...
