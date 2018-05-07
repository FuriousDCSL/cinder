import sys
#working on adding directions when true and implemented some kind of arrow algorithm will add direction arrows
DIRECTIONS = False

LEFT_LINE_INDEX     = '0'
DOWN_LINE_INDEX     = '1'
UP_LINE_INDEX       = '2'
RIGHT_LINE_INDEX    = '3'

LEFT_LINE_LAYER    = '0'
DOWN_LINE_LAYER    = '0'
UP_LINE_LAYER      = '0'
RIGHT_LINE_LAYER   = '0'
#song chart will be input from command line at some point
INFO_FILE           = 'info.json'
EASY_FILE           = 'Easy.json'
NORMAL_FILE         = 'Normal.json'
HARD_FILE           = 'Hard.json'
EXPERT_FILE         = 'Expert.json'
EXPERT_PLUS_FILE    = 'ExpertPlus.json'
#expirmenting with constant song speed and calculating everythign off of that
SONG_SPEED = 200.0

#beat saber version
VERSION = '"1.5.0"'

#need to figure out these variables, setting them as constants for now
BEATS_PER_BAR = '32'
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


def getLevelNotesJSON(header,level):
    if 'OFFSET' in header.keys():
        offset = float(header['OFFSET'])
    else:
        offset = 0
    bpms = header['BPMS'].split(',')
    beatCount = 0 +getBeat(offset)
    
    sbpms =[]
    for bpm in bpms:
        bpm = bpm.split('=')
        bpm[0]= float(bpm[0])
        bpm[1]= float(bpm[1])
        sbpms.append(bpm)
    
    secondsPassed = offset
    measureCounter = 0
    
    notesJSON = []
    for measure in level[1]:
#        print ("Measure "+ str(measureCounter))
        noteCounter = 0
        numNotes = len(measure)
        for note in measure:
            curBPM = getCurBPM(sbpms,measureCounter*4 + float(noteCounter)/float(numNotes))
#            print(curBPM,secondsPassed,getBeat(secondsPassed))
#            print (note)
            left = note[0]
            down = note[1]
            up = note[2]
            right = note[3]
            info = ''
            if left in ['1','2','4']:
                info += '{'
                info += '"_time":' + str(getBeat(secondsPassed)) + ','
                info += '"_lineIndex":' + LEFT_LINE_INDEX +','
                info += '"_lineLayer":' + LEFT_LINE_LAYER +','
                info += '"_type":0,"_cutDirection":8}'
                notesJSON.append(info)
            info =''
            if down in ['1','2','4']:
                info += '{'
                info += '"_time":' + str(getBeat(secondsPassed)) + ','
                info += '"_lineIndex":' + DOWN_LINE_INDEX +','
                info += '"_lineLayer":' + DOWN_LINE_LAYER +','
                info += '"_type":0,"_cutDirection":8}'
                notesJSON.append(info)
            info = ''
            if up in ['1','2','4']:
                info += '{'
                info += '"_time":' + str(getBeat(secondsPassed)) + ','
                info += '"_lineIndex":' + UP_LINE_INDEX +','
                info += '"_lineLayer":' + UP_LINE_LAYER +','
                info += '"_type":1,"_cutDirection":8}'
                notesJSON.append(info)
            info = ''
            if right in ['1','2','4']:
                info += '{'
                info += '"_time":' + str(getBeat(secondsPassed)) + ','
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

def exportInfo(info):
    print("Writing info.json")
    with open(INFO_FILE,'w') as infoFile:
        infoFile.write(info)

def exportLevelJSON(levels):
    for level in levels:
        level = level.split('|')
        print("Writing difficulty file "+level[0]+".json")
        with open(level[0]+'.json','w') as levelFile:
            levelFile.write(level[1])

def main():
    if len(sys.argv)==2:
        smFile = sys.argv[1]
        print("Processing "+smFile)
    else:
        print('To use please enter the name of .sm file to convert after SM2BS.py ')
        exit()
    simFile = getSimFile(smFile)
    
    simParsed = parseSimfile(simFile)    
    
    simHeader = getHeader(simParsed)

    simLevels = getNotes(simParsed)

    infoJSON = (genInfoJSON(simHeader,simLevels))
    levelsJSON =[]
    
    for level in simLevels:
        if level[0]['type'].lower() =='dance-single':
            levelsJSON.append( getLevelJSON(simHeader,level))

#    print(infoJSON)
    exportInfo(infoJSON)
    exportLevelJSON(levelsJSON)
#    print(levelsJSON)
        
if __name__ =='__main__':
    main()