full = "◼"
empty = "◻"
filling = "▨"
percent = 100
bar = ""
for x in range(10):
    if percent > ((x*10)+9):
        bar = bar+full
    elif percent < ((x*10)):
        bar = bar+empty
    else:
        bar = bar+filling
print(f"{percent}% {bar}")