import interactions, json, asyncio, copy
from interactions import Client, Intents, listen
from interactions.ext import prefixed_commands
from interactions.ext.prefixed_commands import prefixed_command, PrefixedContext
from environment import environment


bot = Client(token="ODUyOTMwMzAwMTIzMTUyMzk0.GEAAuR.7z2c0Kbs073jIK0zblLEvCYEvOTR1uGjJO9AsE",
intents=Intents.new(default=True, guild_messages=True, message_content=True))
env : environment = None
gameMessage : interactions.Message = None
selected : environment.gridsquare = None
f = open('levels.json')
data : dict= json.load(f)
f.close()
selectedMessage : interactions.Message = None
isListening = False
selectedLabel = 0
currentLevelDat = None

prefixed_commands.setup(bot, default_prefix=">")

@listen()
async def on_startup():
    print("Citds started")

@listen()
async def on_message_create(event : interactions.events.MessageCreate):
    if event.message.author.bot:
        return
    if event.message.content.startswith(">"):
        return;
    if not isListening:
        return;
    global selectedMessage
    if selectedMessage == None:
        return
    if event.message.channel.id != selectedMessage.channel.id:
        return;
    global selected
    global selectedLabel
    if selected == None:
        return;
    await event.message.delete()
    selected.code = event.message.content
    selected.line = 0
    code = ""
    itterator = 1
    for x in selected.code.split("\n"):
        code = code+f"{itterator}] {x}\n"
        itterator+=1
    await selectedMessage.edit(content=f"```CURRENTLY SELECTED NODE [{selectedLabel}]. CURRENT CODE:\n{code}```")



@prefixed_command(name="test")
async def on_test(ctx : PrefixedContext):
    global gameMessage
    await gameMessage.edit(file="test.png")


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

@prefixed_command(name="start")
async def onStart(ctx : PrefixedContext, level= ""):
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
    lDat = data[level]
    currentLevelDat = copy.deepcopy(lDat)
    env = None
    env = environment(rows=lDat["rows"],collums=lDat["collums"], input=lDat["input"], output=lDat["output"])
    env.inputList = lDat["inpList"]
    env.expectedOutput = lDat["outList"]
    emb = getGameEmbed()
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
    await gameMessage.edit(components=actionRow)
    await selectedMessage.delete()
    env = None

@interactions.component_callback("reset")
async def resetGame(ctx : interactions.ComponentContext):
    global env
    global currentLevelDat
    global gameMessage
    env.stepInt = 0
    env.inputList = currentLevelDat["inpList"]
    print(f"Resetting... inputList= {env.inputList}")
    env.output = []
    await gameMessage.edit(embed=getGameEmbed())
    msg : interactions.Message = await ctx.send("Game reset")
    await asyncio.sleep(1)
    await msg.delete()

def getGameEmbed():
    global currentLevelDat
    emb = interactions.Embed(title=currentLevelDat["name"], color=(0,255,0), fields=[
        interactions.EmbedField("Input", surroundIndex("**",0, env.inputList)),
        interactions.EmbedField("Expected Output", str(env.expectedOutput), True),
        interactions.EmbedField("Current Output", str(env.output)),
    ],footer=interactions.EmbedFooter(f"Node is on step {env.stepInt}"))
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
    elif res != "OK":
        await ctx.send(res)
        return
    await gameMessage.edit(embed=getGameEmbed())
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
    await gameMessage.edit(embed=getGameEmbed())

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

@prefixed_command(name= "code")
async def getCode(ctx : PrefixedContext, arg = None):
    global selected
    await ctx.send(f"Current code: {selected.code}")
    if arg != None:
        selected.code = arg
        await ctx.send(f"New code: {selected.code}")

bot.start()