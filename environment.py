from PIL import Image, ImageDraw, ImageFont
import copy

class environment:

    class gridsquare:
        name = ""
        outputDir = None
        maxVert = 0;
        maxHor = 0;
        index = []
        eax = None
        ebx = None
        line = 0
        code = ""
        env = None;
        get = None;
        ret = None
        codeParser : dict;

        def __str__(self):
            eax = str(self.eax)
            ebx = str(self.ebx)
            test ="GridSquare ["+self.name+"] with an EAX["+eax+"] and EBX["+ebx+"]."
            return test

        def __init__(self, env, index, maxVert, maxHor, outputDir = None):
            self.env = env
            self.index = index
            # index[0] = horiz, index[1] = vert
            self.name = str(index[1])+"-"+str(index[0])
            self.maxVert = maxVert
            self.maxHor = maxHor
            if outputDir != None:
                self.outputDir = outputDir

        def storeCode(self, code):
            self.code = code

        def wait(self, line):
            return "OK"
        def recieve(self, line):
            print(f"WORK @ {self.name}: RECIEVING {self.ret}")
            if self.eax == None:
                if self.ret != None:
                    self.eax = self.ret
                    self.ret = None
                    return "OK"
        
        def parseCode(self) -> str:
            if self.code == "":
                return "OK"
            split = self.code.split("\n")
            
            if split[self.line].split(" ")[0] not in self.codeParser.keys():
                return f"error at line [{self.line}]. NODEID: {[(self.index[1]*(self.maxHor+1))+(self.index[0]+1)]}"
            
            res = self.codeParser[split[self.line].split(" ")[0]](self, split[self.line])
            if res == "OK":
                self.line += 1
                if self.line > len(split)-1:
                    self.line = 0
            elif res:
                return res
            return "OK"
        
        def move(self, line : str): # THIS IS A BIGG MESS :(((
            move = copy.deepcopy(self.index)#DEEP COPY BECAUSE PYTHON IS DUMB
            exist = True # index[0] = horiz, index[1] = vert
            direction = line.split(" ")[1].lower()
            match direction:
                case "up" | "u":
                    move[1] = move[1]-1
                    if move[1] <0:
                        exist = False
                case "down" | "d":
                    print("CASE DOWN")
                    move[1] = move[1]+1
                    if move[1] > self.maxVert:
                        exist = False
                case "left" | "l":
                    move[0] = move[0]-1
                    if move[0] < 0:
                        exist = False
                case "right" | "r":
                    move[0] = move[0]+1
                    if move[0] > self.maxHor:
                        exist = False
                case "_":
                    return "err"
            if exist == False:
                if self.outputDir == direction:
                    if self.eax == None:
                        return
                    self.env.placeOut(self.eax)
                    self.eax = None
                    return "OK"
            else:
                print(f"{self.index} is moving in the {direction} direction to {move}")
                res = self.env.findGridSquare(move[1], move[0]).retreive(self.eax)
                if res:
                    self.eax = None
                    return "OK"
                else:
                    print("MOVE FAIL")
                    return


        
        def swap(self, line):
            temp = self.eax
            self.eax = self.ebx
            self.ebx = temp
            return "OK"

        def store(self, line):
            if self.eax == None:
                return "OK"
            self.ebx = self.eax
            self.eax = None
            print(self.ebx)
            return "OK"

        def sub(self, line):
            if self.eax == None:
                return "OK"
            if self.ebx == None:
                self.ebx = 0
            self.ebx = self.ebx-self.eax
            self.eax = None
            print(self.ebx)
            return "OK"

        def add(self, line):
            if self.eax == None:
                return "OK"
            if self.ebx == None:
                self.ebx = 0
            self.ebx = self.ebx+self.eax
            self.eax = None
            print(self.ebx)
            return "OK"

        def retreive(self, val) -> bool:
            if self.ret == None:
                self.ret = val
                return True
            return False
        
        codeParser = {"WAIT":wait, "MOVE":move, "GET":recieve, "ADD":add, "SUB":sub, "SWP":swap,"STORE":store}

    grid = [];
    output = [];
    expectedOutput = [];
    inputList = [];
    inputSquare : gridsquare = None
    inputSpace = 0
    outputSpace = 0
    stepInt = 0;
    stepLimit = 256

    def __init__(self, rows, collums, input, output):
        self.grid = [] #FOR SOME REASON IT SAVES I HAVE NO IDEA WHY :(
        self.inputSpace = input
        self.outputSpace = output
        for y in range(collums):
            collum = []
            for x in range(rows):
                print(f"{x}=x, {y}=y")
                square = self.gridsquare(self, [x,y], collums-1, rows-1)
                collum.append(square)
            self.grid.append(collum)

        #make grid image
        cellSize = 200
        gridSize = (rows*cellSize, collums*cellSize)
        mainSize = ((rows*cellSize)+100, (collums*cellSize)+100)
        mainImage = Image.new("RGB", mainSize, (100, 100, 100))
        gridImage = Image.new("RGB", gridSize, (255, 255, 255))

        draw = ImageDraw.Draw(gridImage)
        draw.font = ImageFont.truetype("FreeMono.ttf")

        #draw grid
        for x in range(rows):
            if x != 0:
                lineCords = (x*cellSize, 0, x*cellSize, collums*cellSize)
                draw.line(lineCords, width=3, fill=(100, 100, 100))
        for x in range(collums):
            if x != 0:
                lineCords = (0, x*cellSize, rows*cellSize, x*cellSize)
                draw.line(lineCords, width=3, fill=(100, 100, 100))
        
        #add numbers
        itterator = 0
        for row in range(collums):
            for collom in range(rows):
                itterator = itterator + 1
                xy = ((collom*cellSize)+20, (row*cellSize)+20)
                draw.text(xy, str(itterator), fill=(0,0,0), font_size=16)
        #Add border
        Image.Image.paste(mainImage, gridImage, (50,50))

        #input/output text
        draw = ImageDraw.Draw(mainImage)
        draw.font = ImageFont.truetype("Arial.ttf")
        xy = ((input*cellSize)+50+(cellSize/4), 5)
        draw.text(xy, "Input", fill=(255,0,0), font_size=32)
        xy = ((output*cellSize)+50+(cellSize/4), (collums*cellSize)+55)
        draw.text(xy, "Output", fill=(255,0,0), font_size=32)

        #set grid output via code
        self.grid[len(self.grid)-1][output].outputDir = "down"
        #set inputGrid
        self.inputSquare = self.grid[0][input]

        mainImage.save("image.png", "PNG")
        print(self.grid)


    #rows = horizonatlly colloms = top and down
    def findGridSquare(self, collom, row):
        return self.grid[collom][row]

    def select(self, id):
        right = id
        max = len(self.grid[0])
        down = 0
        while right >max:
            right -= max
            down += 1
        return(self.grid[down][right-1])

    def placeOut(self, output):
        self.output.append(output)
        print(f"Output Updated: {self.output}")
    
    def step(self) -> str:
        #make sure its not impossible
        if self.stepInt >= self.stepLimit:
            return "ERROR: MEMORY ERROR. TRY FASTER APPROACH OR CURRENT APPROACH IS IMPOSSIBLE."
        elif not self.inputSquare.code:
            return "ERROR: IMPOSSIBLE. INPUT SQUARE HAS NO CODE."
        elif not self.grid[len(self.grid)-1][self.outputSpace].code:
            return "ERROR: IMPOSSIBLE. OUTPUT SQUARE HAS NO CODE."
        if self.inputList:
            result = self.inputSquare.retreive(self.inputList[0])
            if result:
                self.inputList.pop(0)
        for x in self.grid:
            for square in x:
                res = square.parseCode()
                if res != "OK":
                    return f"ERROR: [{res}]"
        if len(self.expectedOutput) == len(self.output):
            self.inputList = []
            return "DONE"
        self.stepInt += 1
        print(f"Grid is on step {self.stepInt}")
        return "OK"
        

