import discord
import asyncio
import random
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import wikipedia

client = discord.Client()
sid = SentimentIntensityAnalyzer()

pegasus = ["super_pegasus", "sumia", "pegasus_classic", "pegasus_776", "pegasus", "neo_pegasus"]
lucina = ["01.gif", "02.jpg", "03.png", "04.jpg", "05.png", "06.png", "07.png", "08.jpg",
          "09.png", "10.png", "11.png", "12.png", "13.jpg"]
lucina_prf = "http://ltrf.club/lucina/"

nah = ["01.png", "02.jpg", "03.jpg", "04.jpg", "05.png", "06.jpg", "07.png", "08.jpg",
       "09.png", "10.png", "11.jpg", "12.jpg"]
nah_prf = "http://ltrf.club/nah/img/"

tamamo = "http://ltrf.club/tamamo.png"

previous_search = []

def emoji(name):
    name = name.replace(":", "")
    for e in client.get_all_emojis():
        if e.name == name:
            return str(e)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content.startswith('!pegasus'):
        await client.send_message(message.channel, emoji(random.choice(pegasus)))
    elif message.content.startswith('!pascal'):
        await client.send_message(message.channel, emoji('pascal') + ' Pascal the dog is here.')
    elif message.content.startswith('!fate'):
        await client.send_message(message.channel, lucina_prf + random.choice(lucina))
    elif message.content.startswith('!wiki'):
        subject = message.content[message.content.find(" ") + 1:]
        searches = wikipedia.search(subject)
        if len(searches) == 0:
            await client.send_message(message.channel, "I'm sorry, I can't find {}, can you please rephrase that?".format(subject))
        else:
            try:
                response = "Here's what I found:\n\n" + wikipedia.summary(subject, sentences = 1)
            except wikipedia.exceptions.DisambiguationError as e:
                response = "Here's what I found:\n\n" + wikipedia.summary(e.options[0], sentences = 1)
                subject = e.options[0]
            response += "\n**Link:** " + wikipedia.page(subject).url
            response += "\n\n" + "I can show you other possible searches if you @ me and say 'other searches'."
            await client.send_message(message.channel, response)
            message = await client.wait_for_message(author=message.author, timeout=15)
            if message != None and client.user.mentioned_in(message) and "other searches" in message.content:
                response = "Here are the other searches. If you'd like the see the result for one, @ me with the number."
                for search in searches:
                    response += "\n\t" + search
                await client.send_message(message.channel, response)
                wait = True
                while wait:
                    message = await client.wait_for_message(author=message.author, timeout=15)
                    if message == None:
                        wait = False
                    elif len(message.content) > 0 and client.user.mentioned_in(message):
                        try:
                            idx = int(message.content[message.content.find(" ") + 1:]) - 1
                            if idx < len(searches):
                                response = "Here you go!\n\n"
                                try:
                                    response += wikipedia.summary(searches[idx], sentences = 1)
                                except wikipedia.exceptions.DisambiguationError as e:
                                    response += wikipedia.summary(e.options[0], sentences = 1)
                                response += "\n**Link:** " + wikipedia.page(searches[idx]).url
                                await client.send_message(message.channel, response)
                        except:
                            await client.send_message(message.channel, "Sorry, something went wrong! You can try again if you'd like.")
    elif 'tamamo' in message.content.lower():
        await client.send_message(message.channel, tamamo)
    elif 'nah' in message.content.lower().split(" "):
        await client.send_message(message.channel, nah_prf + random.choice(nah))
    elif "anime" in message.content.lower():
        await client.send_message(message.channel, message.author.mention + " " + emoji("gun"))
    elif "pegasus" in message.content.lower():
        await client.send_message(message.channel, message.author.mention + " " + emoji(random.choice(pegasus)))
    elif client.user.mentioned_in(message):
        lines_list = tokenize.sent_tokenize(message.content)
        sentiment = 0
        for line in lines_list:
            line = re.sub(r"((\W|^)[Ll]\s*([Oo]+|[Uu]+)\s*[Ll](\W|$)|(\W|^)[Ll]\s*[Mm]\s*[Aa]\s*[Oo](\W|$))",
                          "", line)
            sentiment += sid.polarity_scores(line)['compound']
        if sentiment < -0.1:
            await client.send_message(message.channel, message.author.mention + " " + emoji("STOP"))
        elif sentiment > 0.1:
            await client.send_message(message.channel, message.author.mention + " :)")
        else:
            if "thanks" in message.content.lower() or "thx" in message.content.lower():
                await client.send_message(message.channel, message.author.mention + " You're welcome! :)")
            else:
                await client.send_message(message.channel, message.author.mention + " Do you need something?")
    elif message.content.startswith('!help'):
        await client.send_message(message.channel, 'Here\'s a list of my commands:' + \
                                  '\n\t!pegasus: send a pegasus' + \
                                  '\n\t!pascal: pascal the dog is here' + \
                                  '\n\t!help: this command' + \
                                  '\n\t!fate: some meme shit prolly')

key = None
with open("secret.key") as f:
    key = f.readline()
if key != None:
    client.run(key)
