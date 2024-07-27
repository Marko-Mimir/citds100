from PIL import Image, ImageDraw, ImageFont

class environment:

    class gridsquare:
        name = ""
        outputDir = None
        maxVert = 0;
        maxHor = 0;
        index = []
        eax = 0
        ebx = 0
        code = ""
        env = None;

        def __str__(self):
            eax = str(self.eax)
            ebx = str(self.ebx)
            test ="GridSquare ["+self.name+"] with an EAX["+eax+"] and EBX["+ebx+"]."
            return test

        def __init__(self, env, index, maxVert, maxHor, outputDir = None):
            self.env = env
            self.index = index
            # index[0] = collum, index[1] = row
            self.name = str(index[0])+"-"+str(index[1])
            self.maxVert = maxVert
            self.maxHor = maxHor
            if outputDir != null:
                self.outputDir = outputDir

        def storeCode(self, code):
            self.code = code

        def parseCode(self):
            split = self.code.split("\n")
            for x in split:
                match x.split(" ")[0]:
                    case "ADD":
                        self.add()
                    case "MOVE":
                        result = self.move(x[1].lower())
                        if result == "err":
                            return "Error at line ["+x+"]. Incorrect direction, syntax= MOVE [UP/LEFT/DOWN/RIGHT]"
                        if result == "NON EXIST":
                            if outputDir == x[1].lower():
                                env.output(self.eax)
                        else:
                            self.env.findGridSquare(result[0], result[1]).retreive(self.eax)
                        self.eax = 0;
                        print('worked somehow')
                    case "SUB":
                        self.sub()
                    case "STORE":
                        self.store()
                    case "SWP":
                        self.swap()
            return "OK"
                        
        def swap(self):
            temp = self.eax
            self.eax = self.ebx
            self.ebx = temp

        def store(self):
            self.ebx = self.eax
            print(self.ebx)

        def sub(self):
            self.ebx = self.ebx-self.eax
            print(self.ebx)

        def add(self):
            self.ebx = self.ebx+self.eax
            print(self.ebx)

        def retreive(self, val):
            self.eax = val
        
        def move(self, direction):
            move = self.index
            match direction:
                case "up" | "u":
                    move[1] = self.index[1]+1
                    if move[1] > self.maxVert:
                        return "NON EXIST"
                case "down" | "d":
                    move[1] = self.index[1]-1
                    if move[1] < 0:
                        return "NON EXIST"
                case "left" | "l":
                    move[0] = self.index[0]-1
                    if move[0] < 0:
                        return "NON EXIST"
                case "right" | "r":
                    move[0] = self.index[0]+1
                    if move[0] > self.maxHor:
                        return "NON EXIST"
                case "_":
                    return "err"
            return move

    grid = [];
    output = [];
    ecx = 0;

    def __init__(self, rows, collums):
        for x in range(collums):
            collum = []
            for y in range(rows):
                square = self.gridsquare(self, [x,y], rows-1, collums-1)
                collum.append(square)
                test = str(x)+"="
            self.grid.append(collum)

        #make grid image
        cellSize = 200
        gridSize = (rows*cellSize, collums*cellSize)
        mainSize = ((rows*cellSize)+100, (collums*cellSize)+100)
        mainImage = Image.new("RGB", mainSize, (100, 100, 100))
        gridImage = Image.new("RGB", gridSize, (255, 255, 255))

        draw = ImageDraw.Draw(gridImage)
        draw.font = ImageFont.truetype("FreeMono.ttf")
        for x in range(rows):
            if x != 0:
                lineCords = (x*cellSize, 0, x*cellSize, collums*cellSize)
                draw.line(lineCords, width=3, fill=(100, 100, 100))
        for x in range(collums):
            if x != 0:
                lineCords = (0, x*cellSize, rows*cellSize, x*cellSize)
                draw.line(lineCords, width=3, fill=(100, 100, 100))
        
        itterator = 0
        for row in range(collums):
            for collom in range(rows):
                itterator = itterator + 1
                xy = ((collom*cellSize)+20, (row*cellSize)+20)
                draw.text(xy, str(itterator), fill=(0,0,0), font_size=16)

        Image.Image.paste(mainImage, gridImage, (50,50))
        mainImage.save("image.png", "PNG")
    
    #rows = horizonatlly colloms = top and down
    def findGridSquare(self, collom, row):
        return self.grid[collom][row]

    def output(self, output):
        self.output.append(output)
    
test = environment(5, 3)
test.findGridSquare(0,0).storeCode("MOVE DOWN")
test.findGridSquare(0,0).parseCode()


