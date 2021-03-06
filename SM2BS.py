import argparse
import glob
import sys
import tkinter
import tkinter.filedialog

LEFT_LINE_INDEX     = '0'
DOWN_LINE_INDEX     = '1'
UP_LINE_INDEX       = '2'
RIGHT_LINE_INDEX    = '3'

LEFT_LINE_LAYER    = '0'
DOWN_LINE_LAYER    = '0'
UP_LINE_LAYER      = '0'
RIGHT_LINE_LAYER   = '0'

INFO_FILE           = 'info.json'
EASY_FILE           = 'Easy.json'
NORMAL_FILE         = 'Normal.json'
HARD_FILE           = 'Hard.json'
EXPERT_FILE         = 'Expert.json'
EXPERT_PLUS_FILE    = 'ExpertPlus.json'
#expirmenting with constant song speed and calculating everythign off of that
#with song speed 60 the not beat value will be the number of seconds since start of song
SONG_SPEED = 200

#beat saber version
VERSION = '"1.5.0"'

#need to figure out these variables, setting them as constants for now
BEATS_PER_BAR = '8'
NOTE_JUMP_SPEED = '10.0'
SHUFFLE = '0.0'
SHUFFLE_PERIOD = '0.5'
COVER = 'cover.png'

def stripComments(simFile):
    simLines=[]
    for line in simFile:
        simLines.append(line.split('//')[0])
    simText =''
    for line in simLines:
        simText+=line
    return simText

def getSimFile(smFile):
    # garb the song file
    with open(smFile,'r', encoding='UTF-8') as simFile:
        simFileText = simFile.readlines()
    return stripComments(simFileText)

def parseSimfile(simFile):
    simParsed = simFile.split(';')
    stripCmds =[]
    for cmd in simParsed:
        stripCmds.append(cmd.strip())

    return stripCmds

def getHeader(simFile):
    header =[]
    for line in simFile:
        if line[1:6].upper() != 'NOTES':
            header.append(line)

    headerDict={}
    for item in header:
        if item == '':
            continue
        item = item.split('#')
        if len(item) >1:
            item = item[1]
        sItem = item.split(':')
        if len(sItem) > 1:
            headerDict[sItem[0].upper()]=sItem[1]
    return headerDict

def parseNote(note):

    splitNote = note.split(':')
    sNote = []
    for item in splitNote:
        sNote.append(item.strip())

    noteHeader = dict([('type',sNote[1]),('author',sNote[2]),('diff',sNote[3]),('diffNum',sNote[4])])
    if noteHeader['diff'].lower() == 'beginner':
        noteHeader['diff'] = 'Easy'
    elif noteHeader['diff'].lower() == 'easy':
        noteHeader['diff'] = 'Normal'
    elif noteHeader['diff'].lower() == 'medium':
        noteHeader['diff'] = 'Hard'
    elif noteHeader['diff'].lower() == 'hard':
        noteHeader['diff'] = 'Expert'
    elif noteHeader['diff'].lower() == 'challenge':
        noteHeader['diff'] = 'ExpertPlus'
    measures = sNote[6].split(',')
    sMeasurses = []
    for measure in measures:
        sMeasurse = measure.strip().split()

        sMeasurses.append(sMeasurse)
    return [noteHeader,sMeasurses]

def getNotes(simFile):
    notes =[]
    for line in simFile:
        if line[0:6] == '#NOTES':
            notes.append(line)
    parsedNotes = []
    for note in notes:
        parsedNotes.append(parseNote(note))

    return parsedNotes

def genLevelInfoJSON(header,level):

    info  = '{'
    info += '"difficulty":"'    + level[0]['diff']      +'",'
    info += '"difficultyRank":' + level[0]['diffNum']   +','
    info += '"audioPath":"'     + header['MUSIC']     +'",'
    info += '"jsonPath":"'      + level[0]['diff']      +'.json"},'

    return info

def genInfoJSON(header,levels):
    info  ='{'
    if 'TITLETRANSLIT' in header.keys() and header['TITLETRANSLIT'] != '':
        info += '"songName":"'          + header['TITLETRANSLIT']       +'",'
    else:
        info += '"songName":"'          + header['TITLE']       +'",'

    if 'SUBTITLETRANSLIT' in header.keys() and header['SUBTITLETRANSLIT'] != '':
        info += '"songSubName":"'       + header['SUBTITLETRANSLIT']    +'",'
    elif 'SUBTITLE' in header.keys():
        info += '"songSubName":"'       + header['SUBTITLE']    +'",'
    else:
        info += '"songSubName":"",'

    if 'ARTISTTRANSLIT' in header.keys() and header['ARTISTTRANSLIT'] != '':
        info += '"authorName":"'        + header['ARTISTTRANSLIT']      +'",'
    else:
        info += '"authorName":"'        + header['ARTIST']      +'",'

    info += '"beatsPerMinute":'     + str(SONG_SPEED)       +','
    info += '"previewStartTime":'   + header['SAMPLESTART'] +','
    info += '"previewDuration":'    + header['SAMPLELENGTH']+','
    info += '"coverImagePath":"'    + COVER + '",'
    info += '"environmentName":"DefaultEnvironment",'
    info += '"difficultyLevels": ['
    for level in levels:
        if level[0]['type'].lower()=='dance-single':
            info += genLevelInfoJSON(header,level)
    info = info[:-1]
    info +=']}'

    return info

def getSeconds(beatCount):
    return beatCount * 60.0 /SONG_SPEED

def getBeat(seconds):
    return SONG_SPEED*seconds/60.0

def getCurBPM(bpms, beat):
    curBPM = bpms[0][1]
    for bpm in bpms:
        if beat >= bpm[0]:
            curBPM = bpm[1]
        else:
            return curBPM
    return curBPM

def setSongSpeed(header):
    bpms = header['BPMS'].split(',')

    sbpms =[]
    for bpm in bpms:
        bpm = bpm.split('=')
        bpm[0]= float(bpm[0])
        bpm[1]= float(bpm[1])
        sbpms.append(bpm)

    if (len(bpms)==1):
        global SONG_SPEED
        SONG_SPEED = sbpms[0][1]
    print (SONG_SPEED)



def getLevelNotesJSON(header,level):
    if 'OFFSET' in header.keys():
        offset =-1* float(header['OFFSET'])
    else:
        offset = 0
    sStops=[]

    if 'STOPS' in header.keys():
        stops = header['STOPS']
        stops = stops.split(',')
        for stop in stops:
            if stop == '':
                continue
            stop = stop.split('=')
            sStops.append([float(stop[0]),float(stop[1])])
#    print(sStops)
    bpms = header['BPMS'].split(',')

    sbpms =[]
    for bpm in bpms:
        bpm = bpm.split('=')
        bpm[0]= float(bpm[0])
        bpm[1]= float(bpm[1])
        sbpms.append(bpm)


    secondsPassed = offset
    measureCounter = 0
    curStop = 0
    stopped = []
    for stop in sStops:
        stopped.append(False)

#    print(stopped)
    notesJSON = []
    for measure in level[1]:
#        print ("Measure "+ str(measureCounter))
        noteCounter = 0
        numNotes = len(measure)
        for note in measure:

            curSongBeat = measureCounter*4 + float(noteCounter)/float(numNotes)
            curBPM = getCurBPM(sbpms,curSongBeat)
#            print (secondsPassed, curSongBeat, curBPM)
            counter  = 0
            for stop in sStops:
                if not stopped[counter]:
                    if stop[0]<curSongBeat:
                        stopped[counter]=True
                        print(str(stop[0]) +" STOPPED at beat "+str(curSongBeat)+" curSeconds "+str(secondsPassed)+" for "+ str(stop[1]))
                        secondsPassed += stop[1]
                        print(secondsPassed)
                counter += 1
            left = note[0]
            down = note[1]
            up = note[2]
            right = note[3]
            curBeat = getBeat(secondsPassed)
            curBeatStr = str(curBeat)

            info = ''
            if left in ['1','2','4']:
                info += '{'
                info += '"_time":' + curBeatStr + ','
                info += '"_lineIndex":' + LEFT_LINE_INDEX +','
                info += '"_lineLayer":' + LEFT_LINE_LAYER +','
                info += '"_type":0,"_cutDirection":8}'
                notesJSON.append(info)
            info =''
            if down in ['1','2','4']:
                info += '{'
                info += '"_time":' + curBeatStr + ','
                info += '"_lineIndex":' + DOWN_LINE_INDEX +','
                info += '"_lineLayer":' + DOWN_LINE_LAYER +','
                info += '"_type":0,"_cutDirection":8}'
                notesJSON.append(info)
            info = ''
            if up in ['1','2','4']:
                info += '{'
                info += '"_time":' + curBeatStr + ','
                info += '"_lineIndex":' + UP_LINE_INDEX +','
                info += '"_lineLayer":' + UP_LINE_LAYER +','
                info += '"_type":1,"_cutDirection":8}'
                notesJSON.append(info)
            info = ''
            if right in ['1','2','4']:
                info += '{'
                info += '"_time":' + curBeatStr + ','
                info += '"_lineIndex":' + RIGHT_LINE_INDEX +','
                info += '"_lineLayer":' + RIGHT_LINE_LAYER +','
                info += '"_type":1,"_cutDirection":8}'
                notesJSON.append(info)


            secondsPassed+= 4/float(numNotes) * 60.0/float(curBPM)
            noteCounter+=1


        measureCounter +=1

    notesJSONText = ''
    for note in notesJSON:
#        print(note)
        notesJSONText+=note+','
#    print(notesJSONText[:-1])
    return notesJSONText[:-1]



def getLevelJSON(header, level):

    info  = level[0]['diff']+'|{'
    info += '"_version":'           + VERSION           + ','
    info += '"_beatsPerMinute":'    + str(SONG_SPEED)        + ','
    info += '"_beatsPerBar":'       + BEATS_PER_BAR     + ','
    info += '"_noteJumpSpeed":'     + NOTE_JUMP_SPEED   + ','
    info += '"_shuffle":'           + SHUFFLE           + ','
    info += '"_shufflePeriod":'     + SHUFFLE_PERIOD    + ','
    info += '"_events":[],'
    info += '"_notes":['            + getLevelNotesJSON(header,level) +'],'
    info += '"_obstacles":[]}'

    return info

def exportInfo(info,dir):
    print("Writing info.json")
    infoStore = dir+'/'+INFO_FILE
    print(infoStore)
    with open(infoStore,'w') as infoFile:
        infoFile.write(info)

def exportLevelJSON(levels,dir):
    for level in levels:
        level = level.split('|')
        print("Writing difficulty file "+level[0]+".json")
        infoStore = dir+'/'+level[0]

        print(infoStore)

        with open(infoStore+'.json','w') as levelFile:
            levelFile.write(level[1])


def convertSimToJson(smFile, storageFolder=None):
    
    simFile = getSimFile(smFile)
    simParsed = parseSimfile(simFile)
    simHeader = getHeader(simParsed)
    setSongSpeed(simHeader)
    print(SONG_SPEED)
    simLevels = getNotes(simParsed)
    levelsJSON =[]
    for level in simLevels:
        if level[0]['type'].lower() =='dance-single':
            levelsJSON.append( getLevelJSON(simHeader,level))
    infoJSON = (genInfoJSON(simHeader,simLevels))


    if not storageFolder:
        storageFolder = tkinter.filedialog.askdirectory()
    
    exportInfo(infoJSON,storageFolder)
    exportLevelJSON(levelsJSON,storageFolder)


def main():
    
    storageFolder=None
    parser = argparse.ArgumentParser(description='Convert Stepmania songs into Beat Saber songs.')
    parser.add_argument('--file', action='store', help='specify an sm file to convert')
    parser.add_argument('--dir', action='store', help='specify a dir containing an sm file and possible image. New files are created in-place')
    #parser.add_argument('--img', action='store_true', help='Attempt to rename the image from common stepmania background names.')

    args = parser.parse_args()
    
    if args.file:
        smFile = args.file
    elif args.dir:
        storageFolder=args.dir
        if storageFolder[-1] != '/':
            storageFolder += '/'
        pattern = storageFolder + '*.sm'
        print(pattern)
        smFile=glob.glob(pattern)[0]
    else:
        smFile = tkinter.filedialog.askopenfilename()

    print("Processing "+smFile)

    convertSimToJson(smFile, storageFolder=storageFolder)

if __name__ =='__main__':
    main()
