import re
import discord
from discord.ext import commands
import random
from collections import OrderedDict

num = 25

def cleanup():
    codewordslog = open('codewordslog.txt', 'r+')
    with codewordslog as codewordsFile:
        codewords = open('codewords.txt', 'w')
        lines_exclude = set() # holds lines already seen
        with open('blacklist.txt', 'r+') as blacklistFile:
            for line in blacklistFile:
                lines_exclude.add(line)
        tally = 0
        for line in codewordsFile:
            cease = False
            newline = ""
            line = line.strip()
            for char in line:
                if cease == False:
                    if char.isalpha() == False:
                        cease = True
                    else:
                        newline += char.lower()
            if len(newline) > 2:
                if newline not in lines_exclude: # not a duplicate
                    lines_exclude.add(newline)
                    tally += 1
                    codewords.write(newline + '\n')
    codewords.close()
    print(str(tally) + " items. Cleanup complete.")
    return (tally)

def blacklist(word):
    blacklist = open('blacklist.txt', 'a')
    blacklist.write(word.lower() + '\n')
    blacklist.close()
    
def whitelist(word):
    whitelist = open('codewordslog.txt', 'a')
    whitelist.write(word.lower() + '\n')
    whitelist.close()

def constructBoard():
    codeBoard = open('codewords.txt', 'r').readlines()
    codeBoard = [x.strip() for x in codeBoard] 
    codeBoard = random.sample(codeBoard, num)
    return codeBoard

def constructCipher():
    codeCipher = []
    for x in range(0, 8):
        codeCipher.append('b')
    for x in range(0, 7):
        codeCipher.append('i')
    for x in range(0, 9):
        codeCipher.append('o')
    codeCipher.append('x')
    random.shuffle(codeCipher)
    return (codeCipher)

def initGame():
    board = constructBoard()
    cipher = constructCipher()
    gameDict = OrderedDict(zip(board, cipher))
    print(board)
    return (gameDict)

def drawBoard(board):
    boardFormatted = []
    formatting = {'b':'"**{}**"','i':'"__*{}*__"','x':'"~~{}~~"','o':'"{}"'}
    for word in board:
        lineItem = ''
        formatCode = formatting[board[word].lower()]
        exeCode = formatCode + ".format('" + word + "')"
        boardFormatted.append(eval(exeCode))
    return boardFormatted

def progressBoard(board):
    boardProgressed = ""
    formatting = {'B':'"**{}**"','I':'"__*{}*__"','X':'"~~{}~~"','O':'"{}"'}
    for word in board:
        lineItem = ''
        formatCode = formatting[board[word]]
        exeCode = formatCode + ".format('" + word + "')"
        boardProgressed += eval(exeCode) + "\n"
    print (boardProgressed)
    return boardProgressed

def displayBoard(board):
    displayStr = ""
    for y in range(0, 5):
        displayLine = ""
        for x in range(0, 5):
            index = y * 5 + x
            displayLine += ("| " + list(board)[index] + " |")
        displayStr += displayLine + "\n"
    return displayStr

def generateTeams(lobbyDict):
    boldList = []
    italicList = []
    randList = []
    for upper in lobbyDict:
        if lobbyDict[upper] == 'B':
            boldList.append(upper)
        elif lobbyDict[upper] == 'I':
            italicList.append(upper)
    random.shuffle(boldList)
    random.shuffle(italicList)
    keys = list(lobbyDict.keys())
    random.shuffle(keys)
    for x in keys:
        if lobbyDict[x] == 'b':
            boldList.append(x)
        elif lobbyDict[x] == 'i':
            italicList.append(x)
        elif lobbyDict[x].lower() == 'r':
            randList.append(x)
    for y in randList:
        if len(boldList) < len(italicList):
            boldList.append(y)
        else:
            italicList.append(y)
    teamLists = [boldList,italicList]
    return teamLists

def debugDict():
    debugDict = {}
    foo = ['b', 'i', 'B', 'I', 'r']
    for i in range(0, 10):
        name = "player" + str(i)
        debugDict[name] = random.choice(foo)
    print (debugDict)
    return debugDict
