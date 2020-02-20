import os
import argparse
import imageio
import numpy as np
from PIL import ImageOps, Image
from random import shuffle
from midiutil.MidiFile import MIDIFile

tones = {} 

# Set command line interface
parser = argparse.ArgumentParser()
parser.add_argument('--pixel', help='Use to write midi from pixels, not grid', default=False, action='store_true')

# Get the images from the image file
def getImages(fileName):
    with open(fileName, 'r') as myFile:
        files = [f.strip() for f in myFile.readlines()]
        return files

# If image is color, convert to grayscale
def checkGrayScale(image):
    if len(image.shape) == 2:
        return image
    else:
        return image[:, :, 0]

# Check midi directory exists, or create one
def setMidiDirectory():
    if not os.path.isdir("./midiFiles"):
        os.mkdir("./midiFiles")

# Create the grid
def createGrid(image):
    nSquares = 20
    gridSizeX = int(round(image.shape[0] / nSquares, 0))
    gridSizeY = int(round(image.shape[1] / nSquares, 0))
    grid = []
    
    x1 = y1 = 0
    x2 = gridSizeX
    y2 = gridSizeY

    for col in range(nSquares):
        for row in range(nSquares):
            grid.append([x1, x2, y1, y2])
            y1 = y2
            y2 = y2 + gridSizeY
        
        # Increment row
        x1 = x2
        x2 = x2 + gridSizeX
        
        # Reset column
        y1 = 0
        y2 = gridSizeY
    return grid

# Randomize the grid, if required
def randomizeGrid(grid, random=False):
    """
    type: string
        can be "random"  
    """
    if random:
        shuffle(grid)

# A function for getting the tones
def getTone(lib, val):

    for tone in lib:
        if lib[tone]['tone'][0] <= int(val) <= lib[tone]['tone'][1]:
            return tone, lib[tone]['duration']         

def saveGridImage(path, im):
    if not os.path.isdir("./gridImages"):
        os.mkdir("./gridImages")
    newImage = os.path.join("gridImages", os.path.basename(path))
    imageio.imwrite(newImage, im)

def processImages(randomize=False, fileName="images.txt", usePixel=False):
    # Loop through each image and get the luminace values
    for eachImage in getImages(fileName):
        # Read image
        temp = Image.open(eachImage)
        imageShape = ImageOps.exif_transpose(temp).size
        image = imageio.imread(eachImage)
        # Convert to grayscale if needed
        image = checkGrayScale(image)

        # Rotate iamge if required
        if imageShape[0] != image.shape:
            image = np.rot90(np.fliplr(image.T))      
        
        # Get image name
        name = eachImage.split('.')[0]
        tones[name] = []
        
        if usePixel:
            for row in image:
                for val in row:
                    tones[name].append(val)
            return
        
        testImage = image  # test image visualises the grid
        # Get grid
        grid = createGrid(image)
        # Randomize grid order if randomize==True
        randomizeGrid(grid, randomize)
        # Get image name
        
        # Get tones 
        for piece in grid:
            newImage = image[piece[0]:piece[1], piece[2]:piece[3]]
            tones[name].append(newImage.mean())
            testImage[piece[0]:piece[1], piece[2]:piece[3]] = newImage.mean()
        
        # Save grid as image
        saveGridImage(eachImage, testImage)

# Save each midi value in the csv
def saveMidiValues(toneLibrary, tones):
    if not os.path.isdir("./imageData"):
        os.mkdir("./imageData")

    for tone in tones:
        with open("./imageData/{}.csv".format(tone.split('/')[1]), "w") as myFile:
            # Write column headers
            myFile.write("{0},{1},{2}\n".format("Index", "Luminance", "Tone"))
            # Write values
            for index, eachVal in enumerate(tones[tone]):
                if index % 10 == 0:
                    myFile.write("{0},{1},{2}\n".format(index, eachVal, getTone(toneLibrary, eachVal)[0]))

def writeMidi():
    # Get all tones to find the min and max lumination values 
    allTones = []
    [allTones.extend(tones[each]) for each in tones]
    minTone = int(min(allTones))
    maxTone = int(max(allTones))

    # The tone increment
    toneIncrement = (maxTone - minTone) / 12
    
    print("Your lowest tone is {}".format(minTone))
    print("Your highest tone is {}".format(maxTone))
    print("Your tone increment is {}".format(toneIncrement))

    # The tone library starting at C (I think)
    toneLibrary = {
            60 : {'tone': [minTone, minTone + toneIncrement], 'duration': .5},
            61 : {'tone': [minTone + toneIncrement, minTone + (toneIncrement*2)], 'duration': .5},
            62 : {'tone': [minTone + (toneIncrement*2), minTone + (toneIncrement*3)], 'duration': .5},
            63 : {'tone': [minTone + (toneIncrement*3), minTone + (toneIncrement*4)], 'duration': .5},
            64 : {'tone': [minTone + (toneIncrement*4), minTone + (toneIncrement*5)], 'duration': .5},
            65 : {'tone': [minTone + (toneIncrement*5), minTone + (toneIncrement*6)], 'duration': .5},
            66 : {'tone': [minTone + (toneIncrement*6), minTone + (toneIncrement*7)], 'duration': .5},
            67 : {'tone': [minTone + (toneIncrement*7), minTone + (toneIncrement*8)], 'duration': .5},
            68 : {'tone': [minTone + (toneIncrement*8), minTone + (toneIncrement*9)], 'duration': .5},
            69 : {'tone': [minTone + (toneIncrement*9), minTone + (toneIncrement*10)], 'duration': .5},
            70 : {'tone': [minTone + (toneIncrement*10), minTone + (toneIncrement*11)], 'duration': .5},
            71 : {'tone': [minTone + (toneIncrement*11), minTone + (toneIncrement*12)], 'duration': .5},
            }      

    # Create midifile directory
    setMidiDirectory()

    # Save the midi values in csv file
    saveMidiValues(toneLibrary, tones)

    # Create the midi files from the images
    for eachImage in tones:
        # Create midi file
        tempMIDI = MIDIFile(1)
        track    = 0
        channel  = 0
        time     = 0    # In beats
        tempo    = 60   # In BPM
        volume   = 100  # 0-127, as per the MIDI standard
        
        # Create the trackname and temp
        tempMIDI.addTrackName(track, time, eachImage)
        tempMIDI.addTempo(track,time,tempo)
        
        # Add each tone from the current image
        for index, val in enumerate(tones[eachImage]):
            if index % 10 == 0:
                # Get tone from library
                tone = getTone(toneLibrary, val)[0]
                # Get duration from library
                duration = getTone(toneLibrary, val)[1]
                # Set interval between tones
                toneInterval = (index / 10) * duration
                # Add note to track
                tempMIDI.addNote(track, channel, tone, time + toneInterval, duration, volume)
            
        # Write the midi track to a file
        with open("midiFiles/{}.mid".format(eachImage.split('/')[1]), "wb") as midiFile:
            tempMIDI.writeFile(midiFile)


if __name__ == "__main__":
    
    args = parser.parse_args()

    if args.pixel:
        print("Creating midi from pixels...")

    processImages(randomize = False, fileName="images.txt", usePixel=args.pixel)

    # Get all images
    # 

    writeMidi()

