import os
import copy
import argparse
import imageio
import numpy as np
from PIL import ImageOps, Image
from random import shuffle

from midiutil.MidiFile import MIDIFile
from scales import scales, BASE_NOTES, BASE_MIDI_NOTE

hasSkimage=False
try:
    import skimage
    from skimage.viewer import ImageViewer
    hasSkimage=True
except ImportError:
    pass


# Set command line interface
parser = argparse.ArgumentParser()
parser.add_argument('--pixel', help='Use to write midi from pixels, not grid', default=False, action='store_true')
tones = {}

def makeFolder(folderName):
    """
    Make folder
    """
    if not os.path.isdir(folderName):
        os.mkdir(folderName)
    return folderName

def saveImage(folder, fileName, image):
    imagePath = os.path.join(folder, os.path.basename(fileName + '.png'))
    try:
        imageio.imwrite(imagePath, image)
    except Exception as e:
        print(e)
        im = Image.fromarray(image)
        im.save(imagePath)

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
    image = np.array(temp)
    meanRed = 0

    # Get mean red value, if image is color
    if len(image.shape) > 2:
        meanRed = image[:, :, 0].mean()
       
    return image, meanRed



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
    
def getGridValues(image, tones, name, greyScale=False):
    """
    Appends the luminance values for each grid to the tones lib
    Also creates an image from mean grid pieces to demonstrate the effect
    """
    testImage = image  # test image visualises the grid
    redImage = copy.copy(image)  # needs copy of image to change individually
    # Get grid
    grid = createGrid(image)

    # Make mask size of image
    mask = np.ones(shape=image.shape[0:2], dtype="bool") 
    mod =  np.random.choice(np.arange(-200, 200, 20), size=1)[0]

    # Get tones 
    for piece in grid:
        newImage = image[piece[0]:piece[1], piece[2]:piece[3]]
        tones[name].append(newImage.mean())
        testImage[piece[0]:piece[1], piece[2]:piece[3]] = newImage.mean()
        
        # Mask drawn using code adapted from 
        # https://datacarpentry.org/image-processing/04-drawing/

        offsetY = piece[3] - piece[2]   # Y offset
        offsetX = piece[1] - piece[0]   # X offset
        offset = min(offsetX, offsetY)  # take the smallest size for radius
        radius = offset / 2             # Radius from grid size
        
        mod = mod * -1  # modify start point for offsetting rows
        x = piece[0] + offset / 2 - mod 
        y = piece[2] + offset / 2 

        if hasSkimage:
            rr, cc = skimage.draw.circle(x, y, radius=radius, shape=image.shape[0:2])
            mask[rr, cc] = False

        # Create grid image in red only
        if not greyScale:
            redImage[piece[0]:piece[1], piece[2]:piece[3], :] = newImage.mean()
            redImage[piece[0]:piece[1], piece[2]:piece[3], 1] = 0
            redImage[piece[0]:piece[1], piece[2]:piece[3], 2] = 0

    if hasSkimage:
        testImage[mask] = 0
        redImage[mask] = 0

    # Save grid as image
    saveImage("gridImages", name, testImage)
    if not greyScale:
        saveImage("gridImages", 'red{}'.format(name), redImage)

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
    
    print("Your lowest luminance is {}".format(minTone))
    print("Your highest luminance is {}".format(maxTone))
    print("Your luminance increment is {}".format(toneIncrement))

    return minTone, maxTone, toneIncrement

def setToneLib(midiNote, musicNote, minTone, toneIncrement):
    """
    returns a tone dict, created using the toneRange
    """
    
    return {
            midiNote[0] : {'tone': [minTone, minTone + toneIncrement]},
            midiNote[1] : {'tone': [minTone + toneIncrement, minTone + (toneIncrement*2)]},
            midiNote[2] : {'tone': [minTone + (toneIncrement*2), minTone + (toneIncrement*3)]},
            midiNote[3] : {'tone': [minTone + (toneIncrement*3), minTone + (toneIncrement*4)]},
            midiNote[4] : {'tone': [minTone + (toneIncrement*4), minTone + (toneIncrement*5)]},
            midiNote[5] : {'tone': [minTone + (toneIncrement*5), minTone + (toneIncrement*6)]},
            midiNote[6] : {'tone': [minTone + (toneIncrement*6), minTone + (toneIncrement*7)]},
            midiNote[7] : {'tone': [minTone + (toneIncrement*7), minTone + (toneIncrement*8)]},
            midiNote[8] : {'tone': [minTone + (toneIncrement*8), minTone + (toneIncrement*9)]},
            midiNote[9] : {'tone': [minTone + (toneIncrement*9), minTone + (toneIncrement*10)]},
            midiNote[10] : {'tone': [minTone + (toneIncrement*10), minTone + (toneIncrement*11)]},
            midiNote[11] : {'tone': [minTone + (toneIncrement*11), minTone + (toneIncrement*12)]},
           }

def currentScale(meanRed):
    # Take mean red value from image returns numbers of divisions by 16.
    # This value is used to select the scale 
    return int(meanRed / 16)

def calculateScale(offset):
    # We need the offset, so we can calculate a new sequence of tones
    # We need the offset, so we can calculate a new sequence of midi tones
    # BASE_NOTES - list of notes, we need to take the offset, and slice the list, to make a new sequence
    # From the offset, we create a new list of midinotes : BASE_MIDI_NOTE + offset
    # The tone library starting at scale
    midiNote = []
    musicNote = []
    for idx in range(12):
        midiNote.append((BASE_MIDI_NOTE + offset) + idx)
    
    musicNote.extend(BASE_NOTES[offset:])
    musicNote.extend(BASE_NOTES[:offset])
    return midiNote, musicNote

def moveToneScale(values, toneLibrary, scaleDict, scale):
    
    #scaleDict contains the midivalues for the scale, and the music notes in order
    # Midi values and notes are key value pairs
    rescaledTones = []

    # Max allowable tone is used to check whether the tone exceeds the scale
    # If the tone exceeds the scale, it is scaled to a scale base note 
    # 12 tones is offset by one, because offset is inclusive of note 1
    maxAllowableTone = BASE_MIDI_NOTE + scale['offset'] + (12 - 1)

    # Loop through the mean grid values
    # Get the tone from the library
    # If the tone is in the scale, do nothing
    # Else, add a semitone to make the tone fit the scale

    for meanVal in values:
        tone = getTone(toneLibrary, meanVal)  
        if scaleDict[tone] in scale['scale']:
            rescaledTones.append(tone)
        elif (tone + 1) > maxAllowableTone:
            rescaledTones.append(tone - (12 - 1))
        else:
            rescaledTones.append(tone + 1)
    return rescaledTones

def getTone(lib, val):
    """
    Returns tone from tone lib associated with particular lum val
    """
    for tone in lib:
        if lib[tone]['tone'][0] <= int(val) <= lib[tone]['tone'][1]:
            return tone

def saveMidiValues(folder, meanLuminanceVals, convertedTone, scaleDict, scale, fileName):
    """
    Save raw luminance, converted midi values, and associated music note as csv
    """
    with open("./{}/{}.csv".format(folder, fileName), "w") as myFile:
        # Write column headers
        myFile.write("{0},{1},{2},{3},{4}\n".format("Index", "Luminance", "RescaledTone", "MusicNote", "Scale"))
        # Write values
        for index, eachVal in enumerate(meanLuminanceVals):
            tone = convertedTone[index]
            myFile.write("{0},{1},{2},{3},{4}\n".format(index, eachVal, tone, scaleDict[tone], scale))

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
    for index, tone in enumerate(tones):
        # Set duration 
        duration = .5
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
        print("\nCreating midi from pixels...")
    else:
        print("\nCreating midi from grid...")
    
    # Make some relevant folders
    makeFolder("gridImages")
    makeFolder("imageData")
    makeFolder("midiFiles")

    for fileName in getImagePaths("./images.txt"):
        fileName, greyScale = fileName.split(',')
        greyScale = bool(int(greyScale.strip()))

        print("\n******** Sonifying {} ********\n".format(fileName))
        print("Greyscale image? ", greyScale)                   
        # Read image 
        image, meanRed = readImage(fileName)
        print("The mean red value in the image: %d" % (meanRed))
        
        # Set scale information
        scaleIndex = currentScale(meanRed)
        scaleNote = list(scales.keys())[scaleIndex]
        scale = scales[scaleNote]
        print("The tones will be rescaled to ", scaleNote)

        midiNotes, musicNotes = calculateScale(scale['offset'])
        scaleDict = dict(zip(midiNotes, musicNotes))
        print("Miditone scale: \t", midiNotes)
        print("Resequenced note scale: ", musicNotes)
        print("Mean red value selected the {} scale: {}".format(scaleNote, scale['scale']))

        # Get image name
        name = fileName.split('.')[0].split('/')[-1]
        
        # Get values for conversion to midi tones
        tones[name] = []
        [getGridValues, getPixelValues][args.pixel](image, tones, name, greyScale=greyScale)
        
        # Get tone ranges
        minTone, maxTone, toneInc = toneRange(tones)

        # Create the tone library based on current picture values
        toneLibrary = setToneLib(midiNotes, musicNotes, minTone, toneInc)

        # Rescale tones
        covertedTones = moveToneScale(tones[name], toneLibrary, scaleDict, scale)

        # save midi data as csv
        saveMidiValues("imageData", tones[name], covertedTones, scaleDict, scaleNote, name)
        
        import datetime
        start = datetime.datetime.now()
        print("\nscript execution stared at:", start)
        print("script run times")
        
        # make the midi file
        makeMidi(name, toneLibrary, covertedTones)

        end = datetime.datetime.now()
        print("Script execution ended at:", end)
        total_time = end - start
        print("Script totally ran for :", total_time)
        print("\n******** Sonification of {} complete! ********\n".format(fileName))     