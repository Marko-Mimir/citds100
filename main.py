import interactions, json, asyncio, copy, pickle, os, random, pyotp, datetime
from interactions import Client, Intents, listen
from interactions.ext import prefixed_commands
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext
from environment import environment

signedIn = False
bot = Client(token="ODUyOTMwMzAwMTIzMTUyMzk0.GEAAuR.7z2c0Kbs073jIK0zblLEvCYEvOTR1uGjJO9AsE",
intents=Intents.new(default=True, guild_messages=True, message_content=True),
status=interactions.Status.DND, activity= interactions.Activity("the nodemap", interactions.ActivityType.WATCHING))
env : environment = None
gameMessage : interactions.Message = None
selected : environment.gridsquare = None
f = open('levels.json')
data : dict= json.load(f)
f.close()
pdat : dict= {}
selectedMessage : interactions.Message = None
isListening = False
selectedLabel = 0
currentLevelDat = None
listeningPlayers : list[interactions.User] = []

prefixed_commands.setup(bot, default_prefix=">")

@listen()
async def on_startup():
    global pdat
    print("Startup] Starting CITDS")
    if os.path.isfile("player.dat"):
        with open('player.dat', 'rb') as file:
            pdat = pickle.load(file)
            print(f"Startup] Loaded player.dat: {pdat}")

@listen(interactions.events.Disconnect)
async def on_disconnect():
    print("Disconnect] CITDS Disconnected.")

@listen()
async def on_message_create(event : interactions.events.MessageCreate):
    if event.message.author.bot:
        return
    if event.message.content.startswith(">"):
        return;
    if not isListening:
        return;
    global selectedMessage;
    if selectedMessage == None:
        return
    if event.message.channel.id != selectedMessage.channel.id:
        return;
    global listeningPlayers
    if event.message.author.user not in listeningPlayers:
        return;
    global selected
    global selectedLabel
    if selected == None:
        return;
    await event.message.delete()
    newline = "\n"
    if selected.code == "":
        newline = ""
    selected.code = f"{selected.code}{newline}{event.message.content.upper()}"
    selected.line = 0
    code = ""
    itterator = 1
    for x in selected.code.split("\n"):
        code = code+f"{itterator}] {x}\n"
        itterator+=1
    await selectedMessage.edit(content=f"```CURRENTLY SELECTED NODE [{selectedLabel}]. CURRENT CODE:\n{code}```")

@prefixed_command(name="test") #https://www.geeksforgeeks.org/two-factor-authentication-using-google-authenticator-in-python/
async def on_test(ctx : PrefixedContext, password: int = 0):
    key = "restineDevLongPasswordSecret"
    totp = pyotp.TOTP(key)
    await ctx.send(f"Password is: {str(totp.verify(str(password)))}")

def save():
    global pdat
    with open('player.dat', 'wb') as file:
        print(f"Saving] Writing plater.dat: {pdat}")
        pickle.dump(pdat, file)

@prefixed_command(name="send")
async def send(ctx : PrefixedContext, id : str, content : interactions.ConsumeRest[str]):
    if not ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
              return
    else:
        rem = ["<","#",">"]
        for x in rem:
            id = id.replace(x,"") #get(bot, interactions.Channel, object_id=int(id))
        channel : interactions.GuildChannel = await ctx.guild.fetch_channel(id)
        async with interactions.Typing(channel):      
            await asyncio.sleep(len(content)*0.015)
            await channel.send(content)

@prefixed_command(name="signup", aliases=["login"])
async def onLogin(ctx : PrefixedContext, name : str = "", password : str = ""):
    global pdat
    global signedIn
    message : interactions.Message;
    if "name" in pdat.keys():
        if name == "" or password == "":
            message = await ctx.send("ACCOUNT DETECTED. >LOGIN [NAME] [PASSWORD]")
        elif pdat["name"] != name:
            message = await ctx.send("ERROR: [BAD USERNAME]")
        elif pdat["pass"] != password:
            message = await ctx.send("ERROR: [BAD PASSWORD]")
        else:
            await ctx.send(f"WELCOME [{name}]")
            await ctx.send("STARTING CITDS REPAIR...")
            await progress(ctx, "WAIT", "DONE", 0.2, 1.0)

            signedIn = True
            return
    else:
        if name == "" or password == "":
            message = await ctx.send("ERROR: [INVALID SYNTAX. >SIGNUP (USERNAME) (PASSWORD)]")
        else:
            pdat["name"] = name
            pdat["pass"] = password
            message = await ctx.send(f"ACCOUNT CREATED SUCESSFULLY...\nUSERNAME:{name}\nPASSWORD:{password}")
            save()
            await ctx.send("CHECKING FUNCTIONALITY...")
            await progress(ctx, "WAIT", "DONE", 0.5, 2.0)
            await ctx.send("CRITICAL FAILIURE. STARTING REPAIR BACKUP SYSTEMS.")
            await progress(ctx, "WAIT", "DONE")
            signedIn = True 
            return
    if message != None:
        await message.delete(2)

async def progress(ctx : PrefixedContext, before : str = "", after : str = "", minimum : float = 0.5, maximum : float = 1.5):
    full = "◼"
    empty = "◻"
    filling = "▨"
    message = await ctx.send(f"{before} 0% ◻◻◻◻◻◻◻◻◻◻")
    
    percent = 0
    await asyncio.sleep(minimum)
    while percent<100: 
        percent += random.randint(5, 15)
        if percent>=100:
            break
        bar = ""
        for x in range(10):
            if percent > ((x*10)+9):
                bar = bar+full
            elif percent < ((x*10)):
                bar = bar+empty
            else:
                bar = bar+filling
        await message.edit(content=f"{before} {percent}% {bar}")
        await asyncio.sleep(random.uniform(minimum, maximum))
    await message.edit(content=f"{after} 100% ◼◼◼◼◼◼◼◼◼◼")

@prefixed_command(name="poll")
async def onPoll(ctx : PrefixedContext):
    poll :interactions.Poll = interactions.Poll(question=interactions.PollMedia(text="Testing poll"),
                                    answers=[
                                        interactions.PollAnswer(
                                            poll_media=interactions.PollMedia(text="Test1"),
                                            answer_id=1
                                        ),
                                        interactions.PollAnswer(
                                            poll_media=interactions.PollMedia(text="Test2"),
                                            answer_id=2
                                        )
                                    ])
    poll._duration = 1
    poll.layout_type
    await ctx.send(poll=poll)

@prefixed_command(name="kill")
async def killGame(ctx : PrefixedContext):
    global gameMessage
    global selectedMessage
    global isListening
    global selected
    await ctx.message.delete()
    if gameMessage != None:
        await gameMessage.delete()
        await selectedMessage.delete()
        selectedMessage = None
        gameMessage = None
        isListening = False
        elected = None

@prefixed_command(name="repair", aliases=["start"])
async def onStart(ctx : PrefixedContext, level= ""):
    global signedIn
    global pdat
    if signedIn == False:
        command = ">SIGNUP"
        if "name" in pdat.keys():
            command = ">LOGIN"
        #message : interactions.Message = await ctx.send(f"ERROR] NOT LOGGED ON. PLEASE {command}")
        message : interactions.Message = await ctx.send(f"TURN OFF SPOILER MODE <@350967470934458369>")
        await message.delete(1)
        return
    if level == "":
        await ctx.send("This command needs a [LEVEL] Attribute. Syntax: >start [LevelId]")
        return
    global env
    global gameMessage
    global selectedMessage
    await ctx.message.delete()
    if gameMessage != None:
        await gameMessage.delete()
        gameMessage = None

    if level not in data.keys():
        await ctx.send(f"[Levels.json] does not have levelId: [{level}]")
        return
    global currentLevelDat
    lDat = copy.deepcopy(data[level])
    currentLevelDat = copy.deepcopy(lDat)
    env = None
    env = environment(rows=lDat["rows"],collums=lDat["collums"], input=lDat["input"], output=lDat["output"])
    env.inputList = lDat["inpList"]
    env.expectedOutput = lDat["outList"]
    emb = getGameEmbed(env)
    actionRow: list[interactions.ActionRow] =[
        interactions.ActionRow(
            interactions.Button(
                style=interactions.ButtonStyle.BLURPLE,
                label="Step",
                emoji=":arrow_forward:",
                custom_id="step"
            ),
            interactions.Button(
                style=interactions.ButtonStyle.GREEN,
                label="Finish",
                emoji=":track_next:",
                custom_id="finish"
            ),
            interactions.Button(
                style=interactions.ButtonStyle.RED,
                label="Reset",
                emoji=":arrows_counterclockwise:",
                custom_id="reset"
            )
        )
    ]
    
    gameMessage = await ctx.send(components=actionRow, embed=emb, file="image.png")
    selectedMessage = await ctx.send("`CURRENTLY SELECTED NODE [none]. SELECT WITH >select [NODE ID]`")

async def disableGame(ctx : PrefixedContext):
    global gameMessage
    global selectedMessage
    global isListening
    global selected
    global env
    global listeningPlayers
    actionRow: list[interactions.ActionRow] =[
        interactions.ActionRow(
            interactions.Button(
                style=interactions.ButtonStyle.BLURPLE,
                label="Step",
                emoji=":arrow_forward:",
                custom_id="step",
                disabled=True
            ),
            interactions.Button(
                style=interactions.ButtonStyle.GREEN,
                label="Finish",
                emoji=":track_next:",
                custom_id="finish",
                disabled=True
            ),
            interactions.Button(
                style=interactions.ButtonStyle.RED,
                label="reset",
                emoji=":arrows_counterclockwise:",
                custom_id="reset",
                disabled=True
            )
        )
    ]
    isListening = False
    selected = None
    listeningPlayers = []
    enb = getGameEmbed(env)
    await gameMessage.edit(components=actionRow, embed=enb)
    await selectedMessage.delete()
    env.output = []

@interactions.component_callback("reset")
async def resetGame(ctx : interactions.ComponentContext):
    await reset(ctx)

async def reset(ctx : interactions.BaseContext):
    global env
    global currentLevelDat
    global gameMessage
    env.stepInt = 0
    env.inputList = currentLevelDat["inpList"]
    env.output = []
    await gameMessage.edit(embed=getGameEmbed(env))
    msg : interactions.Message = await ctx.send("Game reset")
    await asyncio.sleep(1)
    await msg.delete()

def getGameEmbed(env : environment):
    global currentLevelDat
    inputList = []
    expectedOutput = []
    output = []
    step = 0
    if env:
        inputList = env.inputList
        expectedOutput = env.expectedOutput
        output = env.output
        step = env.stepInt
    emb = interactions.Embed(title=currentLevelDat["name"], color=(0,255,0), fields=[
        interactions.EmbedField("Input", surroundIndex("**",0, inputList)),
        interactions.EmbedField("Expected Output", str(expectedOutput), True),
        interactions.EmbedField("Current Output", str(output)),
    ],footer=interactions.EmbedFooter(f"Node is on step {step}"))
    return emb

@interactions.component_callback("step")
async def nextStep(ctx : interactions.ComponentContext):
    global env
    temp : interactions.Message = None
    if env.output:
        temp =await ctx.send("SUGGESTION: After verifying the [**OUTPUT**] matches [**EXPECTED OUTPUT**], press [**FINISH**] to speed up the repair process.")
    res = env.step()
    if res == "DONE":
        await ctx.send("NODE REPAIRED")
        await disableGame(ctx) 
        await gameMessage.edit(embed=getGameEmbed(env))
        return
    elif res != "OK":
        await ctx.send(res)
        await reset(ctx)
    await gameMessage.edit(embed=getGameEmbed(env))
    tmp : interactions.Message = None
    if temp == None:
        tmp = await ctx.send(content="Node Stepped.")
    await asyncio.sleep(.5)
    if tmp != None:
        await tmp.delete()
    if temp != None:
        await asyncio.sleep(4)
        await temp.delete()

@interactions.component_callback("finish")
async def finishGame(ctx : interactions.ComponentContext):
    global env
    res = "OK"
    while res == "OK":
        res = env.step()
    print(res)
    if res == "DONE":
        await ctx.send("NODE REPAIRED")
        await disableGame(ctx)
    else:
        await ctx.send(res)
        await reset()
    await gameMessage.edit(embed=getGameEmbed(env))

def surroundIndex(surround, index, array) -> str:
    if index > len(array):
        return "index is out of Array."
    itterator = 0
    fString = "["
    for x in array:
        comma = ", "
        if itterator == 0:
            comma = ""
        if itterator == index:
            fString = fString+comma+surround+str(x)+surround
        else:
            fString = fString +comma+str(x)
        itterator += 1;
    fString = fString+"]"
    return fString

@prefixed_command(name="select")
async def onSelect(ctx : PrefixedContext, num):
    global selected
    global env
    if env == None:
        await ctx.send("ERROR: ENVIORMENT ISN'T SET. PLEASE START A NODE REPAIR")
        return
    await ctx.message.delete()
    square : environment.gridsquare = env.select(int(num))
    selected = square
    code = ""
    itterator = 1
    global selectedLabel
    global isListening
    global selectedMessage
    selectedLabel = num
    for x in selected.code.split("\n"):
        code = code+f"{itterator}] {x}\n"
        itterator+=1
    await selectedMessage.edit(content=f"```CURRENTLY SELECTED NODE [{num}]. CURRENT CODE:\n{code}```")
    isListening = True

@prefixed_command(name="delete", aliases=["del"])
async def delCode(ctx : PrefixedContext, lineNum : int = None):
    global selected
    if selected == None:
        return;
    global selectedMessage
    await ctx.message.delete()
    if lineNum == None:
        selected.code = ""
        await selectedMessage.edit(content=f"```CURRENTLY SELECTED NODE [{selectedLabel}]. CURRENT CODE:\n1]```")
    else:
        splitCode = selected.code.split("\n")
        if len(splitCode) < lineNum:
            msg = await ctx.send("ERROR] LineNum is out of range of CODE.")
            await msg.delete(1)
            return
        splitCode.pop(lineNum-1)
        code = ""
        itterator = 1
        for x in splitCode:
            code = code+f"{itterator}] {x}\n"
            itterator+=1
        selected.code = "\n".join(splitCode)
        await selectedMessage.edit(content=f"```CURRENTLY SELECTED NODE [{selectedLabel}]. CURRENT CODE:\n{code}```")

@prefixed_command(name= "code")
async def getCode(ctx : PrefixedContext):
    global listeningPlayers
    message : interactions.Message;
    if ctx.author.user in listeningPlayers:
        listeningPlayers.remove(ctx.author.user)
        message = await ctx.send(f"STOPPED LISTENING TO {ctx.author.display_name.upper()}'S MESSAGES.")
    else:
        listeningPlayers.append(ctx.author.user)
        message = await ctx.send(f"STARTED LISTENING TO {ctx.author.display_name.upper()}'S MESSAGES.")
    await asyncio.sleep(1)
    await message.delete()

bot.start()