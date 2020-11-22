"""
# Script for collecting screenshots by tapping coordinates till 'q' key is pressed
# Generate pdf from collected screenshots, cropping the images first
"""
import glob
import os
import shutil
from fpdf import FPDF

import click
import pyautogui as gui, time
from playsound import playsound
from PIL import Image

import keyboard

key_pressed = False
key = None


def screenshot(i: int):
    dir_path = os.path.join(os.path.dirname(__file__), "output")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    screenshot_file_name = os.path.join(dir_path, f"screenshot{i}.png")
    gui.screenshot().save(screenshot_file_name)
    print(f"Screenshot: {i}")


def on_press(l_key):
    global key
    key = l_key.name
    print(key)


def crop_image(image_file_path, output_path):
    im = Image.open(image_file_path)
    region = im.crop((792, 471, 1750, 1063))
    file_output_path = os.path.join(output_path, os.path.basename(image_file_path))
    print(f"Cropped into {file_output_path}")
    region.save(file_output_path)
    im.close()


# Press the green button in the gutter to run the script.
@click.group()
def cli():
    pass


@cli.command()
def generate():
    dir_path = os.path.join(os.path.dirname(__file__), "output")
    working_copy_path = os.path.join(dir_path, ".wc")

    # prepare working directory
    if os.path.exists(working_copy_path):
        shutil.rmtree(working_copy_path)
    os.makedirs(working_copy_path, exist_ok=True)

    # crop images and save into working copy dir
    files = glob.glob(os.path.join(dir_path, "*.png"))
    files.sort(key=os.path.getmtime)

    for image in files:
        crop_image(image, working_copy_path)

    # create pdf from working copy dir
    pdf = FPDF()
    files = glob.glob(os.path.join(working_copy_path, "*.png"))
    files.sort(key=os.path.getmtime)
    for image in files:
        cover = Image.open(image)
        width, height = cover.size

        # convert pixel in mm with 1px=0.264583 mm
        width, height = float(width * 0.264583), float(height * 0.264583)

        # given we are working with A4 format size
        pdf_size = {'P': {'w': 210, 'h': 297}, 'L': {'w': 297, 'h': 210}}

        # get page orientation from image size
        orientation = 'P' if width < height else 'L'

        #  make sure image size is not greater than the pdf format size
        width = width if width < pdf_size[orientation]['w'] else pdf_size[orientation]['w']
        height = height if height < pdf_size[orientation]['h'] else pdf_size[orientation]['h']

        pdf.add_page(orientation=orientation)
        pdf.image(image, 0, 0, width, height)
        print(f"Adding image {os.path.basename(image)}")
    print(f"Generating pdf")
    output_file_name = os.path.join(dir_path, "output.pdf")
    pdf.output(output_file_name, "F")
    print(f"Pdf created at {output_file_name}")


@cli.command()
def record():
    global key
    keyboard.on_press(on_press)
    i = 0
    key = None
    # commands loop
    while key not in ["q"]:
        if key == "a":
            gui.moveTo(1711, 1089)
            gui.click()
            screenshot(i)
            i += 1
        elif key == "p":
            screenshot(i)
            playsound('beep-01a.mp3')
            i += 1
            key = None
        time.sleep(4)


if __name__ == '__main__':
    cli()
