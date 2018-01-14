import discord
from discord.ext import commands
import random

def getMember (member_mention):
    member_id = member_mention[0]
    member_id = member_id.replace('[', '')
    member_id = member_id.replace(']', '')
    member_id = member_id.replace('\'', '')

def getMemberID (member_mention):
    member_id = member_mention[0]
    member_id = member_id.replace('<', '')
    member_id = member_id.replace('@', '')
    member_id = member_id.replace('>', '')
    del member_mention[0]
    return member_id
        
