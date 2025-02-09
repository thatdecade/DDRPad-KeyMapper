# DDR Game Dance Pad to Keyboard Mapper

This script maps a HID "USB Input Device" button presses to keyboard key presses in real-time. 

* Reads raw HID data from the dance pad
* Decodes button presses from raw USB reports  
* Simulates keyboard input to work in any game  

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

---

**Why Was This Written?**

My old DDRGame dance pad is detected in Windows as a **generic HID input device** rather than a proper game controller.  This prevented its use in StepMania. 

I tested my pad on [HardwareTester.com](https://hardwaretester.com/gamepad),  which confirmed the dance pad was sending inputs, but it wasn't detected by Joy2Key.
