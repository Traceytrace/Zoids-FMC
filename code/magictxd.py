import pyautogui
import subprocess
import os
from config import magic_txd_exe_path
import tkinter as tk
from tkinter import messagebox
import shutil

mass_build_input_path_field = [784, 358]
mass_export_input_path_field = [950, 375]
tools_button = [760, 335]
mass_build_button = [762, 444]
mass_export_button = [800, 400]
platform_dropdown = [868, 458]
game_dropdown = [875, 500]
gamecube_selection = [870, 600]
sonic_heroes_selection = [900, 700]
build_button = [1148, 681]
export_button = [1000, 655]
X_button = [1337,220]

def mass_build_txd(input_path_string, 
                  output_txd_folder,
                  click_build_button=False):

    #warn user to not touch the mouse while the automation runs
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Automation Starting", "Press OK or Enter to begin.\nPlease do not touch your mouse during the process.")
    root.destroy()

    # ensure the main monitor is the active monitor
    pyautogui.click(1, 1)

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
    pyautogui.click(*mass_build_input_path_field)
    pyautogui.click(*mass_build_input_path_field)
    pyautogui.click(*mass_build_input_path_field)
    pyautogui.write(input_path_string)

    # tab over to the output folder field and write the output path
    pyautogui.press('tab')  # Move to the next field
    pyautogui.press('tab')  # Move to the next field
    pyautogui.write(output_txd_folder)

    # select the platform from the dropdown
    pyautogui.click(*platform_dropdown)
    pyautogui.sleep(0.1)  # Wait for the dropdown to open
    pyautogui.click(*gamecube_selection)  # Select GameCube

    # select the game from the dropdown
    pyautogui.click(*game_dropdown)
    pyautogui.sleep(0.1)  # Wait for the dropdown to open
    pyautogui.click(*sonic_heroes_selection)  # Select Sonic Heroes

    # click the build button
    if click_build_button:
        pyautogui.click(*build_button)

def mass_export_txd_to_png(txd_filled_input_root, 
                  png_filled_output_folder,
                  click_export_button=False):

    #warn user to not touch the mouse while the automation runs
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Automation Starting", "Press OK or Enter to begin.\nPlease do not touch your mouse during the process.")
    root.destroy()

    # ensure the main monitor is the active monitor
    pyautogui.click(1, 1)

    # open magic txd
    subprocess.Popen(magic_txd_exe_path)
    pyautogui.sleep(0.1)  # Wait for the application to open

    # click the tools button and select mass build
    pyautogui.click(*tools_button)
    pyautogui.sleep(0.1)  # Wait for the application to open
    pyautogui.click(*mass_export_button)

    # triple click the input path field and write the input path
    pyautogui.click(*mass_export_input_path_field)
    pyautogui.click(*mass_export_input_path_field)
    pyautogui.click(*mass_export_input_path_field)
    pyautogui.write(txd_filled_input_root)

    # tab over to the output folder field and write the output path
    pyautogui.press('tab')  # Move to the next field
    pyautogui.press('tab')  # Move to the next field
    pyautogui.write(png_filled_output_folder)

    pyautogui.click(795, 597)
    # click the export button
    if click_export_button:
        pyautogui.click(*export_button)

    
        