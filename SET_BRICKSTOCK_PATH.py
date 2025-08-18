from os import listdir

# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/workspaces/UntilVrac.github.io"

n = 0

def set_brickstock_path(current_path:str) -> None :
    global n
    for f in listdir(current_path) :
        if f != "SET_BRICKSTOCK_PATH.py" :
            path = current_path + "/" + f
            if f.split(".")[-1] == "py" :
                file = open(path, "r")
                content = file.read()
                file.close()
                if "BRICKSTOCK_PATH = " in content :
                    content = content.split("\n")
                    content_bis = []
                    for e in content :
                        if e.startswith("BRICKSTOCK_PATH = ") :
                            e = f'BRICKSTOCK_PATH = "{BRICKSTOCK_PATH}"'
                        content_bis.append(e)
                    file = open(path, "w")
                    file.write("\n".join(content_bis))
                    file.close()
                    n += 1
            elif "." not in f :
                set_brickstock_path(path)

if __name__ == "__main__" :
    set_brickstock_path(BRICKSTOCK_PATH)
    print(f"end : {n} files affected")
    n = 0