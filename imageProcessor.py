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

def makeFolder(folderName):
    """
    Make folder
    """
    if not os.path.isdir(folderName):
        os.mkdir(folderName)
    return folderName

def saveCSV(folder, fileName):
    pass

def saveImage(folder, fileName, image):
    imagePath = os.path.join(folder, os.path.basename(fileName + '.png'))
    imageio.imwrite(imagePath, image)

def getImagePaths(fileName):
    """
    Get images from image file list
    """
    with open(fileName, 'r') as myFile:
        files = [f.strip() for f in myFile.readlines()]
        return files

def readImage(fileName):
    """
    Reads image using imageio, and returns greyscale image
    """
    temp = Image.open(fileName)
    imageShape = ImageOps.exif_transpose(temp).size
    image = imageio.imread(fileName)

    # Convert to grayscale if needed
    if len(image.shape) != 2:
        image = image[:, :, 0]

    # Rotate image if required
    if imageShape[0] != image.shape:
        image = np.rot90(np.fliplr(image.T))
    
    return image

def createGrid(image):
    """
    Takes image and returns nSquares ^ 2 grid coordinates
    """
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

def getPixelValues(image, tones, name):
    """
    Appends the luminance values for each pixel to the tones lib
    """
    for row in image:
        for val in row:
            tones[name].append(val)
    
def getGridValues(image, tones, name):
    """
    Appends the luminance values for each grid to the tones lib
    Also creates an image from mean grid pieces to demonstrate the effect
    """
    testImage = image  # test image visualises the grid
    # Get grid
    grid = createGrid(image)
    
    # Get tones 
    for piece in grid:
        newImage = image[piece[0]:piece[1], piece[2]:piece[3]]
        tones[name].append(newImage.mean())
        testImage[piece[0]:piece[1], piece[2]:piece[3]] = newImage.mean()

    # Save grid as image
    saveImage("gridImages", name, testImage)

def toneRange(tones):
    """
    Return min, max and tone increment luminance values 
    """
    allTones = []
    [allTones.extend(tones[each]) for each in tones]
    minTone = int(min(allTones))
    maxTone = int(max(allTones))

    # The tone increment
    toneIncrement = (maxTone - minTone) / 12
    
    print("Your lowest tone is {}".format(minTone))
    print("Your highest tone is {}".format(maxTone))
    print("Your tone increment is {}".format(toneIncrement))

    return minTone, maxTone, toneIncrement

def setToneLib(minTone, toneIncrement):
    """
    returns a tone dict, created using the toneRange
    """
    # The tone library starting at C (I think)
    return {
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

def getTone(lib, val):
    """
    Returns tone from tone lib associated with particular lum val
    """
    for tone in lib:
        if lib[tone]['tone'][0] <= int(val) <= lib[tone]['tone'][1]:
            return tone, lib[tone]['duration']

def saveMidiValues(folder, toneLibrary, tones, fileName):
    """
    Save raw luminance and midi values as csv
    """
    with open("./{}/{}.csv".format(folder, fileName), "w") as myFile:
        # Write column headers
        myFile.write("{0},{1},{2}\n".format("Index", "Luminance", "Tone"))
        # Write values
        for index, eachVal in enumerate(tones):
            myFile.write("{0},{1},{2}\n".format(index, eachVal, getTone(toneLibrary, eachVal)[0]))

def makeMidi(fileName, toneLibrary, tones):
    """
    Makes the midi file for a given set of tones
    """
    # Create midi file
    tempMIDI = MIDIFile(1)
    track    = 0
    channel  = 0
    time     = 0    # In beats
    tempo    = 60   # In BPM
    volume   = 100  # 0-127, as per the MIDI standard
    
    # Create the trackname and temp
    tempMIDI.addTrackName(track, time, fileName)
    tempMIDI.addTempo(track, time, tempo)
    
    # Add each tone from the current image
    for index, val in enumerate(tones):
        # Get tone from library
        tone = getTone(toneLibrary, val)[0]
        # Get duration from library
        duration = getTone(toneLibrary, val)[1]
        # Set interval between tones
        toneInterval = (index) * duration
        # Add note to track
        tempMIDI.addNote(track, channel, tone, time + toneInterval, duration, volume)
        
    # Write the midi track to a file
    with open("midiFiles/{}.mid".format(fileName), "wb") as midiFile:
        tempMIDI.writeFile(midiFile)

if __name__ == "__main__":

    args = parser.parse_args()

    if args.pixel:
        print("Creating midi from pixels...")
    else:
        print("Creating midi from grid...")
    
    # Make some relevant folders
    makeFolder("gridImages")
    makeFolder("imageData")
    makeFolder("midiFiles")

    for fileName in getImagePaths("./images.txt"):
        
        # Read image 
        image = readImage(fileName)
        
        # Get image name
        name = fileName.split('.')[0].split('/')[-1]
        
        # Get values for conversion to midi tones
        tones[name] = []
        [getGridValues, getPixelValues][args.pixel](image, tones, name)
        
        # Get tone ranges
        minTone, maxTone, toneInc = toneRange(tones)

        # Create the tone library based on current picture values
        toneLibrary = setToneLib(minTone, toneInc)

        # save midi data as csv
        saveMidiValues("imageData", toneLibrary, tones[name], name)
        
        import datetime
        start = datetime.datetime.now()
        print("script execution stared at:", start)
        print("script run times")
        
        # make the midi file
        makeMidi(name, toneLibrary, tones[name])

        end = datetime.datetime.now()
        print("Script execution ended at:", end)
        total_time = end - start
        print("Script totally ran for :", total_time)
    