import imageio
from random import shuffle
from midiutil.MidiFile import MIDIFile
import os

tones = {}

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
    if not os.path.isdir("./imageData"):
        os.mkdir("./imageData")

# Create the grid
def createGrid(image):
    nSquares = 25
    gridSize = int(image.shape[0] / nSquares)
    grid = []
    
    x1 = y1 = 0
    x2 = y2 = gridSize

    for col in range(25):
        for row in range(25):
            grid.append([x1, x2, y1, y2])
            y1 = y2
            y2 = y2 + gridSize
        
        # Increment row
        x1 = x2
        x2 = x2 + gridSize
        
        # Reset column
        y1 = 0
        y2 = gridSize
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
        if lib[tone]['tone'][0] <= val <= lib[tone]['tone'][1]:
            return tone, lib[tone]['duration']

def processImages(randomize=False, fileName="images.txt"):
    # Loop through each image and get the luminace values
    for eachImage in getImages(fileName):
        
        # Read image
        image = imageio.imread(eachImage)
        # Convert to grayscale if needed
        image = checkGrayScale(image)
        # Get grid
        grid = createGrid(image)
        # Randomize grid order if randomize==True
        randomizeGrid(grid, randomize)

        # Get image name
        name = eachImage.split('.')[0]
        tones[name] = []
        # Get tones 
        for piece in grid:
            newImage = image[piece[0]:piece[1], piece[2]:piece[3]]
            tones[name].append(newImage.mean())

def writeMidi():
    # Get all tones to find the min and max lumination values 
    allTones = []
    [allTones.extend(tones[each]) for each in tones]
    minTone = min(allTones)
    maxTone = max(allTones)
    # The tone increment
    toneIncrement = (maxTone - minTone) / 12
    
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
    
    for tone in tones:
        with open("imageData/{}.csv".format(tone.split('/')[1]), "w") as myFile:
            myFile.write("Index\tRawLuminance\tMidiTone\n")
            for index, eachVal in enumerate(tones[tone]):
                myFile.write("{0}\t{1}\t{2}\n".format(index, eachVal, getTone(toneLibrary, eachVal)[0]))

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
            # Get tone from library
            tone = getTone(toneLibrary, val)[0]
            # Get duration from library
            duration = getTone(toneLibrary, val)[1]
            # Set interval between tones
            toneInterval = index * duration
            # Add note to track
            tempMIDI.addNote(track, channel, tone, time + toneInterval, duration, volume)

        # Write the midi track to a file
        with open("midiFiles/{}.mid".format(eachImage.split('/')[1]), "wb") as midiFile:
            tempMIDI.writeFile(midiFile)

if __name__ == "__main__":
    processImages(randomize=False, fileName="images.txt")
    writeMidi()
