import os
from tkinter import *
from tkinter import messagebox
from tkcolorpicker import askcolor
from PIL import Image, ImageOps, ImageDraw

def main():
    prompt()

##########################
#      SEGMENT ONE       #
#     GUI  elements      #
##########################

def prompt():
    """
    Prompt the user via GUI for the inputs.
    """
    global entries
    global frame_color
    global overlay_color
    frame_color = (255, 0, 0)
    overlay_color = (255, 0, 0, 127)

    entries = []

    root = Tk()

    # First, we'll add all the labels and text inputs.
    # We'll access them in order from a global entries list.
    entries.append(make_text_input(root, "Image folder: ","pics"))
    entries.append(make_text_input(root, "Output folder: ", "out"))
    entries.append(make_text_input(root, "Stamp location: ", "default"))
    entries.append(make_text_input(root, "Stamp offset %: ", "0.1"))
    entries.append(make_text_input(root, "Frame width %: ", "0.1"))

    # Now, we'll add all our buttons.
    # The "command" attribute is the function that'll be called when the button is clicked.
    frame_btn = Button(root, text='Select frame color', command=choose_frame_color)
    frame_btn.pack(side=LEFT, padx=5, pady=5)
    
    overlay_btn = Button(root, text='Select overlay color', command=choose_overlay_color)
    overlay_btn.pack(side=RIGHT, padx=5, pady=5)

    preview_btn = Button(root, text='Show preview', command=show_preview)
    preview_btn.pack(side=TOP, padx=5, pady=5)

    save_btn = Button(root, text='Process all images', command=process_all)
    save_btn.pack(side=BOTTOM, padx=5, pady=5)

    # Show the GUI.
    root.mainloop()

def make_text_input(root, label, default=""):
    """
    Makes a text input area, with its own row, label, and entry box.

    :param root: the root frame to add to
    :param label: the text to use for the label
    :param default: the default value for the entry area
    """

    # We're defining a label that will be 22 pixels wide, and an entry text field.
    row = Frame(root)
    lab = Label(row, width=22, text=label, anchor='w')
    ent = Entry(row)
    ent.insert(0, default)

    # pack() sets the grid settings
    row.pack(side=TOP, fill=X, padx=5, pady=5)
    lab.pack(side=LEFT)
    ent.pack(side=RIGHT, expand=YES, fill=X)
    return ent

def choose_frame_color():
    global frame_color

    color = askcolor(color=frame_color, parent=None, title="Frame color", alpha=False)[0]
    frame_color = color
    print(frame_color)

def choose_overlay_color():
    global overlay_color

    color = askcolor(color=overlay_color, parent=None, title="Overlay color", alpha=True)[0]
    overlay_color = color
    print(overlay_color)

def show_preview():
    preview_file = os.listdir(entries[0].get())[0]
    doctor(entries[0].get() + "/" + preview_file)

def process_all():
    for file in os.listdir(entries[0].get()):
        doctor(entries[0].get() + "/" + file, True)
    messagebox.showinfo("Success", "Your images have been processed and written to output directory \"" + entries[1].get() + "\".")

##########################
#      SEGMENT TWO       #
#     Image  editing     # 
##########################

def doctor(image_file, save=False):
    global entries
    global frame_color
    global overlay_color

    # Open the image and give it an alpha channel for editing transparency
    image = Image.open(image_file)
    image = image.convert('RGBA')

    # Perform all our steps
    image = draw_overlay(image, overlay_color)
    image = frame(image, frame_color, float(entries[4].get()))
    image = stamp(image, entries[2].get(), float(entries[3].get()))

    # Show the image or save it if we say to
    if save:
        image.save(entries[1].get() + "/out-" + os.path.basename(image_file))
    else:
        image.show()

def frame(image, color, percent):
    """
    Adds a frame to the image.

    :param image: the image itself
    :param color: the color of the border (label)
    :param percent: the percent of the image's width to make the frame.
    """
    return ImageOps.expand(image, border=int(image.size[0] * percent), fill=color)

def draw_overlay(image, color):
    """
    Draws a translucent square overlay on the image.

    :param image: the image to draw on
    :param color: the color of the overlay
    """

    # Create an empty image that we'll draw our overlay onto.
    tmp = Image.new('RGBA', image.size, (0,0,0,0))
    draw = ImageDraw.Draw(tmp)

    # Calculate the starting point of our overlay to be centered.
    # We check to see if the width or height is greater so that we don't end up with negatives.
    if image.size[0] > image.size[1]:
        size = image.size[1]
        llx, lly = (image.size[0] - image.size[1]) // 2, 0
    else:
        size = image.size[0]
        llx, lly = 0, (image.size[1] - image.size[0]) // 2

    # Calculate the ending points of our overlay to be centered.
    urx, ury = llx + size + 1, lly + size + 1

    # Draw the rectangle using the specified color as the fill.
    draw.rectangle(((llx, lly), (urx, ury)), fill=color)

    # Alpha-composite, or combine with translucensy, the pictures.
    image = Image.alpha_composite(image, tmp)

    # Convert back to RGB since JPG doesn't have alpha color channel, and return.
    image = image.convert("RGB")
    return image

def stamp(image, stamp, offsetPercent):
    """
    Stamps the image with the specified stamp, or the default stamp if not specified.

    :param image: the image to stamp on
    :param stamp: the stamp to use, or default if the default stamp is desired
    :param offsetPercent: the percentage of the image's size to offset the stamp 
    """

    # Use the default stamp if none is specified
    if(stamp == "default"):
        stamp = Image.open('stamps/stamp.jpg')
    else:
        stamp = Image.open(stamp)

    # Resize the stamp to 50x50 so it doesn't cover too much up
    stamp.thumbnail((50, 50))
    
    # Paste the stamp onto the image at the specified offset and return it
    image.paste(stamp, (int(image.size[0] * offsetPercent), int(image.size[1] * offsetPercent)))
    return image

main()
