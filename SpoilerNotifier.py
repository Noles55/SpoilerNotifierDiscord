from lxml import html
import requests
import discord
import time
import io
import os
import re

mainSite = 'http://mythicspoiler.com/'
BOT_TOKEN = os.environ['BOT_TOKEN']
CHANNEL_ID = os.environ['CHANNEL_ID']
client = discord.Client()
threshold = 40
sleepTime = 5


async def checkForNewCards(channel):

    print("Checking for new cards")

    firstLoop = False

    # Get the newest spoilers page
    page = requests.get(mainSite + 'newspoilers.html')

    # Get the page tree from the page contents
    pageTree = html.fromstring(page.content)

    # Find all card images
    allCards = pageTree.xpath('//img[contains(@src,\'/cards/\')]/@src')

    # Get the last card spoiled from previous post
    lastCardFile = open("LastCard.txt", 'r')
    lastCard = lastCardFile.readline()

    # List for new cards to post
    cardsToSpoil = list()

    # Add the card paths to the cardsToSpoil list, stopping once we reach the last card spoiled from the previous
    # post
    for card in allCards:

        if lastCard in card:
            break

        cardsToSpoil.append(card)

    # Write to the last card file with the newest, most recent card, since we don't want to post it again
    lastCardFile.close()
    if len(cardsToSpoil) == 0:
        return
    elif len(cardsToSpoil) > threshold:
        writeLastCard(cardsToSpoil[0])
        await channel.send("Many new spoilers")
        return

    writeLastCard(cardsToSpoil[0])

    # Retrieve each card image and post it to discord
    for card in cardsToSpoil:

        time.sleep(1)

        print("Posting " + mainSite + card)

        cardString = re.search('(.*/[^.[0-9]+)[0-9]*.jpg', card)
        cardLink = mainSite + cardString.group(1) + ".html"
        cardImageLink = mainSite + cardString.group(1) + ".jpg"

        embeddedContent = discord.Embed(description=cardLink)
        embeddedContent.set_image(url=cardImageLink)
        await channel.send(embed=embeddedContent)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = "Hello " + message.author.mention
        await message.channel.send(msg)

@client.event
async def on_ready():
    print("Logged in as " + client.user.name + ", " + str(client.user.id))
    channel = client.get_channel(CHANNEL_ID)
    firstLoop = True

    while True:
        if not firstLoop:
            time.sleep(60 * sleepTime)

        firstLoop = False
        await checkForNewCards(channel)

def writeLastCard(card):
    lastCardFile = open("LastCard.txt", 'w')
    cardRegex = re.search('/cards/(.*[^0-9])[0-9]*\..+', card)
    lastCardFile.write(cardRegex.group(1))
    lastCardFile.close()


client.run(BOT_TOKEN)
