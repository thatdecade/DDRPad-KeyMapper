"""
DDR Game Dance Pad to Keyboard Mapper
================================
Author: Dustin Westaby
Date: February 8, 2025

This script maps a DDR dance pad's button presses to keyboard key presses in real-time.

WHY WAS THIS WRITTEN?

- My old DDRGame branded dance pad was detected in Windows as generic HID input devices rather than game controller. Preventing use in stepmania.
- This script reads raw HID data, decodes button presses, and simulates keyboard input.

REQUIREMENTS:

- Python 3.x
- pip install hidapi pynput

USAGE:

1. Plug in your DDR dance pad.
2. Create or edit keymap.json in the same folder as this script.
3. Run the script:
    python ddr2key.py
4. Press buttons on your dance pad to trigger keypresses.

ADDITIONAL MODES:

* Print button names on press
python ddr2key.py --print-buttons

* Listen to all HID devices (for debugging)
python ddr2key.py --all-hid


CONFIGURATION (keymap.json):
- This file defines the USB ID and which keyboard keys correspond to which buttons.
- Example:  keymap.json
{
    "VID": "0x0B43",
    "PID": "0x0001",
    "keymap": {
        "B0": "y",
        "B1": "a",
        "B2": "b",
        "B3": "x",
        "B4": null,
        "B5": null,
        "B6": null,
        "B7": null,
        "B8": "esc",
        "B9": "enter",
        "B10": null,
        "B11": null,
        "B12": "up",
        "B13": "right",
        "B14": "down",
        "B15": "left"
    }
}

"""
import hid
import json
import threading
import argparse
from pynput.keyboard import Controller, Key
import sys

# File path for configuration and key mappings
KEYMAP_FILE = "keymap.json"

# Initialize keyboard controller
keyboard = Controller()

# Special keys mapping for pynput
SPECIAL_KEYS = {
    "esc": Key.esc,
    "enter": Key.enter,
    "up": Key.up,
    "down": Key.down,
    "left": Key.left,
    "right": Key.right
}

# Track currently pressed buttons
pressed_buttons = set()
running = True  # Flag to control the loop

def load_keymap():
    """Load device VID, PID, and key mappings from keymap.json"""
    try:
        with open(KEYMAP_FILE, "r") as f:
            config = json.load(f)
            vid = int(config["VID"], 16)  # Convert hex string to integer
            pid = int(config["PID"], 16)
            keymap = config["keymap"]
            return vid, pid, keymap
    except FileNotFoundError:
        print(f"Error: {KEYMAP_FILE} not found. Make sure it's in the same folder as the script.")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing key in {KEYMAP_FILE}: {e}")
        sys.exit(1)

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Map buttons to keyboard keys.")
    parser.add_argument("--all-hid", action="store_true", help="Listen to all HID devices")
    parser.add_argument("--print-buttons", action="store_true", help="Print button names when pressed")
    return parser.parse_args()

def find_hid_devices():
    """Find and return all available HID devices"""
    return hid.enumerate()

def find_usb_input_device(vid, pid):
    """Find and open the dance pad HID device using VID and PID"""
    devices = find_hid_devices()
    for d in devices:
        if d["vendor_id"] == vid and d["product_id"] == pid:
            try:
                device = hid.device()
                device.open(vid, pid)
                device.set_nonblocking(True)
                print(f"Connected to: {d['product_string']} (VID: {vid:04X}, PID: {pid:04X})")
                return device
            except Exception as e:
                print(f"Failed to open device: {e}")
    return None

def get_pressed_buttons(byte0, byte1):
    """Extract pressed buttons from two bytes using bitwise operations"""
    pressed = []
    for i in range(8):  # Process first byte (B0-B7)
        if byte0 & (1 << i):
            pressed.append(f"B{i}")
    for i in range(8, 16):  # Process second byte (B8-B15)
        if byte1 & (1 << (i - 8)):
            pressed.append(f"B{i}")
    return pressed

def handle_keypress(buttons, keymap, print_buttons):
    """Ensures key is held while button is held, and released when button is lifted"""
    global pressed_buttons
    new_presses = set(buttons) - pressed_buttons  # Buttons that were just pressed
    released_buttons = pressed_buttons - set(buttons)  # Buttons that were just released

    for button in new_presses:
        mapped_key = keymap.get(button)
        if mapped_key:
            key_to_press = SPECIAL_KEYS.get(mapped_key, mapped_key)  # Use special keys if needed
            if print_buttons:
                print(f"Pressing: {button} -> {key_to_press}")
            keyboard.press(key_to_press)  # HOLD the key down

    for button in released_buttons:
        mapped_key = keymap.get(button)
        if mapped_key:
            key_to_release = SPECIAL_KEYS.get(mapped_key, mapped_key)
            if print_buttons:
                print(f"Releasing: {button} -> {key_to_release}")
            keyboard.release(key_to_release)  # Release key when button is lifted

    pressed_buttons = set(buttons)  # Update pressed state

def listen_for_button_presses(device, keymap, print_buttons):
    """Continuously listen for button presses in a high-speed loop"""
    global running
    print("Listening for button presses... (Press Ctrl+C to exit)")

    try:
        while running:
            data = device.read(64)  # Read HID report
            if data and len(data) >= 2:
                byte0, byte1 = data[0], data[1]
                pressed_buttons_list = get_pressed_buttons(byte0, byte1)
                handle_keypress(pressed_buttons_list, keymap, print_buttons)
    except KeyboardInterrupt:
        print("\nExiting... (KeyboardInterrupt received)")
        running = False
        device.close()
        sys.exit(0)

def listen_to_all_hid():
    """Listen for any button presses across all HID devices"""
    global running
    print("Listening to all HID devices for button presses...")
    devices = find_hid_devices()

    opened_devices = []
    for d in devices:
        try:
            device = hid.device()
            device.open_path(d["path"])
            device.set_nonblocking(True)
            opened_devices.append(device)
            print(f"Listening on device: {d.get('product_string', 'Unknown Device')} (VID: {d['vendor_id']:04X}, PID: {d['product_id']:04X})")
        except Exception as e:
            print(f"Failed to open device {d.get('product_string', 'Unknown Device')}: {e}")

    try:
        while running:
            for device in opened_devices:
                try:
                    data = device.read(64)  # Try reading data from the device
                    if data:
                        print(f"Raw Data from {device}: {data}")
                except OSError:
                    pass  # Skip unreadable devices
    except KeyboardInterrupt:
        print("\nExiting... (KeyboardInterrupt received)")
        running = False
        for device in opened_devices:
            device.close()
        sys.exit(0)

if __name__ == "__main__":
    args = parse_arguments()
    vid, pid, keymap = load_keymap()  # Load VID, PID, and key mappings from keymap.json

    try:
        if args.all_hid:
            listen_to_all_hid()
        else:
            pad = find_usb_input_device(vid, pid)
            if pad:
                listen_for_button_presses(pad, keymap, args.print_buttons)
            else:
                print(f"Device not found: VID=0x{vid:04X}, PID=0x{pid:04X}. Make sure it's connected.")
    except KeyboardInterrupt:
        print("\nExiting... (KeyboardInterrupt received)")
        running = False
        sys.exit(0)
