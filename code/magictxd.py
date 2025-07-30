import pyautogui
import subprocess
import os
from config import magic_txd_exe_path
import tkinter as tk
from tkinter import messagebox


input_path_field = [784, 358]
tools_button = [760, 335]
mass_build_button = [762, 444]
build_button = [1148, 681]

def mass_build_txd(input_path_string, 
                  output_txd_folder,
                  click_build_button=False):
    """
    """
    #ensure the main monitor is the active monitor
    pyautogui.click(1, 1)

    #warn user to not touch the mouse while the automation runs
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Automation Starting", "Press OK or Enter to begin.\nPlease do not touch your mouse during the process.")
    root.destroy()

    # open magic txd
    subprocess.Popen(magic_txd_exe_path)
    pyautogui.sleep(0.1)  # Wait for the application to open

    # click the tools button and select mass build
    pyautogui.click(*tools_button)
    pyautogui.sleep(0.1)  # Wait for the application to open
    pyautogui.click(*mass_build_button)

    # press enter to remove the popup window
    pyautogui.press('enter')

    # triple click the input path field and write the input path
    pyautogui.click(*input_path_field)
    pyautogui.click(*input_path_field)
    pyautogui.click(*input_path_field)
    pyautogui.write(input_path_string)

    # tab over to the output folder field and write the output path
    pyautogui.press('tab')  # Move to the next field
    pyautogui.press('tab')  # Move to the next field
    pyautogui.write(output_txd_folder)

    # click the build button
    if click_build_button:
        pyautogui.click(*build_button)