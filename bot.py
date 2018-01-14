import discord
from discord.ext import commands
import random
import codenames
import trrutils
import asyncio

description = "The Reject Bot."
PREFIX = "."
CHANNELNAME = "spam"
bot = commands.Bot(command_prefix=PREFIX, description=description)
TOKEN = open('token.txt', 'r').read()
PERMLIST = open('permlist.txt', 'r')

gameBoard = None
lobbyDict = {}
mastersLink = False
gameProgress = False
teamLists = []
mastersList = []
teamTurn = False
mastersTurn = False
hintNumber = 0
teamDict = {False:"B", True:"I"}
remainingWords = [8,7]


def permCheck(authorID):
    PERMLIST.seek(0)
    for line in PERMLIST:
        if str(authorID) == line:
            return True
    return False

def checkTurn():
    if gameProgress == False:
        return "There is no game in progress!"
    strAnnounce = "Current Turn: "
    if teamTurn == False:
        strAnnounce += "**Bold** " 
    else:
        strAnnounce += "__*Italic*__ "
    if mastersTurn == False:
        strAnnounce += "codemaster ," + teamList[int(teamTurn)][0] + ". Use .hint [hint word] [number of guesses] to register your hint."
    else:
        strAnnounce += "team ," + teamList[int(teamTurn)][1:] + "Use .guess [word] to register your guess, or .passturn to end your turn."
    strAnnounce += "Words remaining: Bold ({}) - ({}) Italics".format(remainingWords[0],remainingWords[1])
    return strAnnounce

def checkGuess(guess):
    if guess in gameDict:
        gameDict[guess] = gameDict[guess].upper()
        if teamDict[teamTurn] == gameDict[guess]:
            return "Correct"
        elif teamDict[not teamTurn] == gameDict[guess]:
            return "Opponent"
        elif gameDict[guess] == "O":
            return "Incorrect"
        elif gameDict[guess] == "X":
            return "Death"
    return "Invalid"

def resetGame():
    global gameBoard
    global lobbyDict
    global mastersLink
    global gameProgress
    global teamLists
    global mastersList
    global teamTurn
    global mastersTurn
    global hintNumber
    global teamDict
    global remainingWords
    gameBoard = None
    lobbyDict = {}
    mastersLink = False
    gameProgress = False
    teamLists = []
    mastersList = []
    teamTurn = False
    mastersTurn = False
    hintNumber = 0
    teamDict = {False:"B", True:"I"}
    remainingWords = [8,7]    


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(pass_context=True)
async def exit(ctx):
    if (CHANNELNAME in ctx.message.channel.name) == False:
        return
    if permCheck(ctx.message.author.id) == True:
        await bot.say("Bye!")
        exit

@bot.command(pass_context=True)
async def forcereset(ctx):
    if (CHANNELNAME in ctx.message.channel.name) == False:
        return
    if permCheck(ctx.message.author.id) == True:
        resetGame()
        await bot.say("Game reset.")
        
'''codewords'''
@bot.command(pass_context=True)
async def refresh(ctx):
    if (CHANNELNAME in ctx.message.channel.name) == False:
        return
    if permCheck(ctx.message.author.id) == True:
        tally = codenames.cleanup()
        await bot.say("The codewords file has been refreshed, with " + str(tally) + " words.")

@bot.command(pass_context=True)
async def blacklist(ctx, arg):
    if (CHANNELNAME in ctx.message.channel.name) == False:
        return
    if permCheck(ctx.message.author.id) == True:
        codenames.blacklist(arg)
        await bot.say(arg + " has been added to the blacklist. Use !refreshcodewords to remove blacklisted words from the game.")

@bot.command(pass_context=True)
async def whitelist(ctx, arg):
    if (CHANNELNAME in ctx.message.channel.name) == False:
        return
    if permCheck(ctx.message.author.id) == True:
        codenames.whitelist(arg)
        await bot.say(arg + " has been added to the whitelist. Use !refreshcodewords to add whitelisted words into the game.")

@bot.command(pass_context=True)
async def join(ctx, arg=None):
    if (CHANNELNAME in ctx.message.channel.name) == False:
        return
    authorMember = ctx.message.author
    if gameProgress == True:
        await bot.say("There is a game already in progress! Joining in the middle of the game is currently not implemented.")
    if (arg in ["b", "i", "B", "I", "r", "R"]) == False:
        await bot.say(".join [team] requires a team preference: 'b', 'i', 'r'. r is for random assignment. Use capital letters ('B' or 'I') to preference being that team's codemaster.")
    elif authorMember in lobbyDict:
        lobbyDict[authorMember] = arg
        await bot.say(str(authorMember) + " has changed their team preference.")
    else:
        lobbyDict[authorMember] = arg
        await bot.say(str(authorMember) + " has joined the Codenames lobby.")

@bot.command(pass_context=True)
async def leave(ctx):
    authorMember = ctx.message.author
    if authorMember not in lobbyDict:
        await bot.say("You are not in the Codenames lobby.")
        return
    lobbyDict.pop(authorMember, None)
    await bot.say(str(authorMember) + " has left the Codenames lobby.")

@bot.command(pass_context=True)
async def lobby(ctx):
    if (CHANNELNAME in ctx.message.channel.name) == False:
        return
    lobbyStr = ""
    for member in lobbyDict:
        lobbyStr += (str(member) + " (" + str(lobbyDict[member]) + ") ")
    if lobbyStr == "":
        await bot.say("No-one in the lobby yet. Use '.join b' or '.join i' to join a team, or '.join r' to be randomly assigned. Use capital letters to preference being a codemaster.")
    else:
        await bot.say(lobbyStr)

@bot.command(pass_context=True)
async def start(ctx):
    if (CHANNELNAME in ctx.message.channel.name) == False:
        return
    global gameProgress
    if gameProgress == True:
        await bot.say("A game is running already!")
        return
    if ctx.message.author not in lobbyDict:
        await bot.say("You have not joined the Codenames lobby yet! Use '.join b' or '.join i' to join a team, or '.join r' to be randomly assigned. Use capital letters to preference being a codemaster.")
        return
    if len(lobbyDict) < 4:
        await bot.say("At least four players must join the lobby. Currently in the lobby: " + str(len(lobbyDict)) + ".")
        return
    teamLists = codenames.generateTeams(lobbyDict)
    if len(teamLists[0]) < 2:
        await bot.say("There are not enough players in **Bold** team! Use .join b to switch to or join them, or .join r to let the bot assign you.")
        return
    if len(teamLists[1]) < 2:
        await bot.say("There are not enough players in __*Italic*__ team! Use .join i to switch to or join them, or .join r to let the bot assign you.")
        return
    gameProgress = True
    gameDict = codenames.initGame()
    boardDrawn = codenames.drawBoard(gameDict)
    masterBoard = codenames.displayBoard(boardDrawn)
    mastersList.append(teamLists[0][0])
    mastersList.append(teamLists[1][0])
    for masterUser in mastersList:
        await bot.send_message(masterUser, "New game started! Good luck, codemaster. Private messages to this bot will automatically be sent to your opposing codemaster <This functionality still in development>.")
        await bot.send_message(masterUser, masterBoard)
        mastersLink = True
    announceStr = ("A game of Codenames has started. Going first, {} leads the **bold** team: {}. {} leads the __*italic*__ team: {}.").format(mastersList[0],teamLists[0][1:],mastersList[1],teamLists[1][1:])
    await bot.say(announceStr)
    gameBoard = codenames.displayBoard(gameDict)
    await bot.say(gameBoard)
    await bot.say(checkTurn())

@bot.command(pass_context=True)
async def hint(ctx, arg, param):
    if (CHANNELNAME in ctx.message.channel.name) == False:
        return
    if (mastersTurn == True):
        if ctx.message.author == mastersList[int(teamTurn)][0]:
            hintNumber = param + 1
            mastersTurn = not mastersTurn
            await bot.say("The hint is " + arg + " for " + str(param) + " guesses, and 1 bonus guess. Use .guess to guess, and .passturn to end guessing.")
    else:
        await bot.say(checkTurn())

@bot.command(pass_context=True)
async def guess(ctx, arg):
    if (CHANNELNAME in ctx.message.channel.name) == False:
        return
    if (mastersTurn == False):
        if ctx.message.author in mastersList[int(teamTurn)][1:]:
            response = checkGuess(arg)
            if response == "Correct":
                hintNumber += -1
                remainingWords[int(teamTurn)] += -1
                if remainingWords[int(teamTurn)] == 0:
                    await bot.say("Game over! " + ctx.message.author + "has revealed their last codeword. " + teamlist[int(teamTurn)][0] + "'s team has won the game!")
                    resetGame()
                if hintNumber == 0:
                    await bot.say(arg + " is one of your words! You have no more guesses for this turn.")
                    mastersTurn = not mastersTurn
                    teamTurn = not teamTurn
                    newBoard = codenames.progressBoard(gameDict)
                    await bot.say(checkTurn())
                    await bot.say(newBoard)
                else:
                    await bot.say(arg + " is one of your words! Remaining guesses: " + str(hintNumber))
            elif response == "Incorrect":
                await bot.say(arg + " is a neutral word! Your turn has ended.")
                mastersTurn = not mastersTurn
                teamTurn = not teamTurn
                await bot.say(checkTurn())
            elif response == "Opponent":
                remainingWords[int(not teamTurn)] += -1
                if remainingWords[int(not teamTurn)] == 0:
                    await bot.say("Game over! " + ctx.message.author + "has revealed their opponents' last codeword. " + teamList[int(not teamTurn)][0] + "'s team has won the game!")
                    resetGame()
                await bot.say(arg + " is one of your opponents' words! Your turn has ended.")
                mastersTurn = not mastersTurn
                teamTurn = not teamTurn
                await bot.say(checkTurn())
            elif response == "Death":
                newBoard = codenames.progressBoard(gameDict)
                await bot.say(progressBoard(newBoard))
                await bot.say("Game over!" + arg + " is the double agent!" + teamList[teamTurn][0] + "'s team has lost!")
                resetGame()
            else:
                await bot.say(arg + " is not a valid guess! Try again.")
    else:
        await bot.say(checkTurn())
                      
@bot.command(pass_context=True)
async def passturn(ctx, arg):
    if (CHANNELNAME in ctx.message.channel.name) == False:
        return
    if (mastersTurn == False):
        if ctx.message.author in mastersList[int(teamTurn)][1:]:
            mastersTurn = not mastersTurn
            teamTurn = not teamTurn
            await bot.say(str(ctx.message.author) + " has passed the turn.")
            await bot.say(checkTurn())
            
@bot.command(pass_context=True)
async def turn():
    if (CHANNELNAME in ctx.message.channel.name) == False:
        return
    await bot.say(checkTurn())
'''end codewords'''

bot.run(TOKEN)

