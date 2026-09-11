import requests
import json
import tkinter as tk
import threading
import time
import re
from pathlib import Path
from PIL import Image, ImageTk

import sys

from pathlib import Path

if getattr(sys, "frozen", False):

    BASE_DIR = Path(getattr(sys, "_MEIPASS"))

else:

    BASE_DIR = Path(__file__).resolve().parent

url = "https://pillowmeow.tail6d1b7e.ts.net/pub/"

with open(f'{BASE_DIR}/emojilist/data.json', "r") as f:
    data = json.load(f)
    name = data.get("name", "")
gameurl = ""
gameversion = 0


class Player:
    def __init__(self,root,index):
        self.root = root
        self.index = index
        datajs = ingamesearch(f"/player/{self.index}")
        if isinstance(datajs,int) or "embeds" not in datajs:
            raise ValueError("플레이어 정보를 불러오지 못했습니다.")
        self.datajs = datajs["embeds"][0]
        self.name = self.datajs["title"]
        self.health = iconify(self.datajs["fields"][0]["value_text"])
        stat = self.datajs["fields"][1]["value_text"].split('\n                                   ')
        self.status = iconify(stat[0]) if len(stat) > 0 else ""
        self.stack = iconify(stat[1]) if len(stat) > 1 else ""
        if self.datajs["fields"][2]["name_text"] == "​":
            self.card = iconify(self.datajs["fields"][3]["value_text"])
            self.buff = iconify(self.datajs["fields"][2]["value_text"])
        else:
            self.card = iconify(self.datajs["fields"][2]["value_text"])
            self.buff = ""
        self.magicused = iconify(self.datajs["footer"])

    def formcard(self,frame):
        cardframe = tk.Frame(frame)
        nametitle = tk.Label(cardframe,text=self.name,font=("Arial",12))
        nametitle.pack(side="top")
        for value in [self.health,self.status,self.stack,self.buff,self.magicused]:
            row = tk.Frame(cardframe)
            row.pack(anchor="w")
            texteditor(row,value)
        tk.Label(cardframe,text="-------------------------------").pack(side="left")
        cardframe.pack(side="left")

class Enemy:
    def __init__(self,root,index):
        self.root = root
        self.index = index
        datajs = ingamesearch(f"/enemy/{self.index}")
        if not isinstance(datajs, dict) or "embeds" not in datajs:
            raise ValueError("적 정보를 불러오지 못했습니다.")
        self.datajs = datajs["embeds"][0]
        self.name = self.datajs["title"]
        self.health = iconify(self.datajs["fields"][0]["value_text"])
        stat = self.datajs["fields"][1]["value_text"].split('\n                   ')
        self.status = iconify(stat[0]) if len(stat) > 0 else ""
        self.stack = iconify(stat[1]) if len(stat) > 1 else ""
        if self.datajs["fields"][2]["name_text"] == "​":
            self.card = iconify(self.datajs["fields"][3]["value_text"])
            self.buff = iconify(self.datajs["fields"][2]["value_text"])
        else:
            self.card = iconify(self.datajs["fields"][2]["value_text"])
            self.buff = ""

    def formcard(self,frame):
        cardframe = tk.Frame(frame)
        nametitle = tk.Label(cardframe,text=self.name,font=("Arial",12))
        nametitle.pack(side="top")
        print([self.health,self.status,self.stack,self.buff])
        for value in [self.health,self.status,self.stack,self.buff]:
            row = tk.Frame(cardframe)
            row.pack()
            texteditor(row,value)
        tk.Label(cardframe,text="-------------------------------").pack(side="left")
        cardframe.pack(side="left")

        
def texteditor(frame,values):
    if isinstance(values,str):
        values = [values]
    for value in values:
        if value.endswith('.png'):
            photo = Image.open(f'{BASE_DIR}/emojilist/emoji/{value}').resize((12,12))
            img = ImageTk.PhotoImage(photo)
            lb = tk.Label(frame, image=img)
            setattr(lb, "image", img)
            lb.pack(side="left")
        else:
            tk.Label(frame, text=value,font=("Arial",10)).pack(side="left")



def checkgamevaild(): # 게임이 유효한지 확인(t/f), 게임이 유효하지 않으면 자동으로 gameurl 초기화|| 솔직히 이거 왜 만든지 모르겠음, 더미데이터
    global gameversion
    global gameurl
    if gameurl == "":
        gameversion = 0
        return False
    game = response(f'ingame/{gameurl}')
    if "error" in game:
        if game["status"] == 404:
            gameurl = ""
            gameversion = 0
            return False
    return True

    
    

def ingamesearch(index="")-> int|dict: # 게임을 자동으로 찾고 반환, 없으면 0 반환, 이미 아는값이여도 강제로 불러옴
    game = foundgame()
    if not game:
        return 0
    if not checkgamevaild():
        return 0
    return response(f'ingame/{gameurl}{index}')
    
def ingame(): # 게임을 자동으로 찾고 반환, 없으면 0 반환, 이미 아는값이면 1 반환, 아는값 반환 안하니 주의
    global gameversion
    game = foundgame()
    if not game:
        return 0
    res = response(f'ingame/{gameurl}?since={gameversion}')
    if "error" not in res:
        if res["version"] == gameversion: return 1
        gameversion = res["version"]
        return res
    return 0


def response(subd): # 게임 관련없는것들 호출할때 쓰셈
    return json.loads(requests.get(url + subd).text)

def foundgame(): # gameurl설정용, ingame에는 이미 들어가있음, 실제로 쓸일은 없을듯
    global gameurl
    for game in response("ingame")["games"]:
        for player in game["players"]:
            if player == name:
                gameurl = game["game_id"]
                return 1
    gameurl = ""
    return 0

def iconify(target):
    with open(f'{BASE_DIR}/emojilist/manifest.json', "r") as f:
        ref = json.load(f)["emoji"]
    target = re.sub(r"\*\*(.*?)\*\*", r"[\1]", target)
    target = target.replace("-#", "-")
    target = target.replace("    ", "|  ")
    target = target.replace("__", "")
    result = []
    parts = re.split(r"(:[^\s:]+:)", target)
    for part in parts:
        if not part:
            continue
        if re.fullmatch(r":[^\s:]+:", part):
            emojiname = part[1:-1]
            if emojiname not in ref:
                result.append(part)
                continue
            emoji = ref[emojiname]
            if emoji["type"] == "image":
                result.append(emoji["file"])
            elif emoji["type"] == "text":
                result.append(emoji["text"])
        else:
            result.append(part)
    return result


def printgame():
    def forgetall(list):
        for value in list:
            value.forget()
    def packall(list):
        for value in list:
            value.pack()
    def submit():
        global name
        name = name_enter.get()
        with open(f'{BASE_DIR}/emojilist/data.json', "w") as f:
            json.dump({"name": name}, f)
        label_name.config(text=f"닉네임: {name}")
    def detectgame():
        global gamejs
        global waiting
        gamejs = ingame()
        match gamejs:
            case 0:
                gameoff()
                waiting = 3000
            case 1:
                waiting = 500
            case _:
                gameon()
                waiting = 1500
        root.after(waiting, detectgame)
    def gameoff():
        nonlocal Playerbox
        nonlocal Enemybox
        label_title.config(text="게임 없음...",fg="gray")
        root.geometry("400x200")

        Playerbox.destroy()
        Enemybox.destroy()
        namegroup.pack()
        if Playerbox:Playerbox.forget()
    def gameon():
        nonlocal Playerbox, Enemybox
        global playerlist, enemylist

        Playerbox.destroy()
        Enemybox.destroy()
        
        Playerbox = tk.Frame(root)
        Enemybox = tk.Frame(root)

        if isinstance(gamejs, dict):
            gametitle = gamejs["stage"]["name"]
            label_title.config(text=gametitle, fg="systemTextColor")
            
            # 플레이어 카드
            mypf = gamejs.get("players", [])
            playerlist = [Player(root, p["index"]) for p in mypf]
            for p in playerlist:
                p.formcard(Playerbox)

            # 적 카드
            myef = gamejs.get("enemies", [])
            enemylist = [Enemy(root, e["index"]) for e in myef]
            for e in enemylist:
                if e.health[0][1] != '0':
                    e.formcard(Enemybox)

        max_count = max(len(playerlist), len(enemylist), 1)
        root.geometry(f"{max(400, 300 * max_count)}x500")
        
        Playerbox.pack(side="top", fill="x", pady=5)
        Enemybox.pack(side="top", fill="x", pady=5)
        namegroup.forget()

    def copy_adr():
        root.clipboard_clear()
        root.clipboard_append("/game abandon check_string:저는 허접입니다")
        root.update()
    
    waiting = 3000
        
    root = tk.Tk(className="지비의 게임 보조기")
    root.attributes("-topmost", True)
    root.geometry("400x200")


    namegroup = tk.Frame(root)
    label_name = tk.Label(root, text=f"닉네임: {name}")
    label_title = tk.Label(root, text="게임을 찾는 중...")
    name_enter = tk.Entry(namegroup)
    name_submit = tk.Button(namegroup, text="닉네임 설정", command=submit)

    label_name.pack()
    label_title.pack()

    name_enter.pack(side=tk.LEFT)
    name_submit.pack(side=tk.LEFT)
    namegroup.pack()

    button_adorb = tk.Button(root, text="항복",command=copy_adr,font=("Arial",8),width=5,height=1,bg="gray")
    button_adorb.pack(side=tk.BOTTOM)


    Playerbox = tk.Frame(root)
    Enemybox = tk.Frame(root)


    root.after(waiting, detectgame)
    root.mainloop()

    

#foundgame()
#print(json.loads(requests.get("https://pillowmeow.tail6d1b7e.ts.net/pub/ingame/1").text))


printgame()