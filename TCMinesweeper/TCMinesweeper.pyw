'''
PYMinesweeper
一个用python和tkinter制作的扫雷游戏
中心目标：以单文件形式完成全部功能，只导入必须的标准库以及非标准库（pygame用于播放音乐）
作者：Tilawa Cesoil
本项目完全开源，开源地址：https://github.com/Tilawa-Cesoil/Tilawa-Cesoil/tree/main/PYMinesweeper
'''


# 用于存储临时变量
class Tempvar:pass


# 导入标准库并计时
import time,os,sys
Tempvar.firsttime=time.time()
# 更改运行目录以确保图片可以被导入
os.chdir('.')
path='.'
# 创建窗口和加载界面
import tkinter as tk,tkinter.messagebox as tkmessage
window=tk.Tk()
window.title("PYMinesweeper ———— By Tilawa Cesoil")
window.iconphoto(True,tk.PhotoImage(file=path+'/title.png'))
window.geometry('1355x325')
Tempvar.loadingword=tk.StringVar()
Tempvar.loading=tk.Label(window,textvariable=Tempvar.loadingword,bg='black',fg='white',bd=0,font=(None,20,''),justify='left',anchor='nw')
Tempvar.loading.pack(expand=True,fill='both')
window.update_idletasks()
# 重定向输出流到loading组件
class Restdout:
    def write(self,word):
            Tempvar.loadingword.set(Tempvar.loadingword.get()+word)
            window.update_idletasks()
Tempvar.output=sys.stdout
sys.stdout=Restdout()
# 导入标准库模块和资源，并将其显示在屏幕上
Tempvar.splitline='—'*50
print(Tempvar.splitline)
print('游戏正在加载中……')
print('下面是来自各python标准与非标准库的欢迎信息。')
# 音频支持
print('音频支持：',end='')
from pygame import mixer
mixer.init()
# 数据和运行支持
import random,pickle,threading,socket
print(f'GUI支持：Tkinter（{tk.TkVersion}）；本程序有多线程（threading）和网络通讯（socket）应用。')
# 图片支持
import PIL,PIL.Image,PIL.ImageTk
print(f'图像处理支持：Python Image Library（{PIL.__version__}）https://github.com/python-pillow/Pillow/')

# 无限迭代
sys.setrecursionlimit(1000000)
# 慢速显示用于排查问题，真实游戏中无用
def slowcheck():
    window.update_idletasks()
    time.sleep(0.1)

def fastdata(awidth=None,aheight=None,abomb=None):
    global dif,width,height,bomb,space
    # 1、2、3表示简单、一般、困难，4表示自定义，5表示挑战模式,6表示创造模式
    if dif==1:width,height,bomb=9,9,10
    elif dif==2:width,height,bomb=16,16,40
    elif dif==3:width,height,bomb=30,16,99
    elif dif==4:width,height,bomb=awidth,aheight,abomb
    space=width*height

# 读取存档文件数据
try:
    with open(path+'/savefile','rb') as file:Tempvar.filedata=pickle.load(file)
# 没有就创建新存档
except:
    with open(path+'/savefile','wb') as file:
        Tempvar.filedata=[1,[[0,0,0],[0,0,0],[0,0,0],[0,0,0]],'classic','CN',(False,False,False),(0.5,True)]
        pickle.dump(Tempvar.filedata,file)
dif,data,stylemode,language,Tempvar.controls,Tempvar.musics=Tempvar.filedata
autoflag_control,animation_control,undo_control=(tk.BooleanVar(value=Tempvar.controls[i])for i in range(3))
volume,ifplaybgm=Tempvar.musics
fastdata()
try:
    with open(path+'/basicfile','rb') as file:Tempvar.basicdata=pickle.load(file)
except:pass
version=2.1
# 存档，同时自动更新全局变量
def save():
    threading.Thread(target=save_func,daemon=True).start()
def save_func():
    global dif
    if dif not in range(1,4):dif=1
    with open(path+'/savefile','wb') as file:
        pickle.dump([dif,data,stylemode,language,autoflag_control.get(),animation_control.get(),undo_control.get(),volume,ifplaybgm],file)


# ————————————————————
# 外观主题
# ————————————————————

# rgb颜色转十六进制表示法
def rgb(r:int,g:int,b:int):return '#%02x%02x%02x' % (r,g,b)

# 判断时间为白天还是黑夜
def ifday():
    t=int(time.strftime('%H'))
    if t>6 and t<18:return True
    else:return False

# 颜色字体组合模式
def mode(ifcell=False):
    global bg,fg,hg,font,bd,fontsize,imgsize,cellsize
    if stylemode=='simple':
        if ifday():bg,hg=rgb(200,200,200),'white'
        else:bg,hg=rgb(100,100,100),'black'
        fglist=('blue','green','red','purple','brown','cyan','black','gray')
        fg='black'
        fontsize=20
        font=('Terminal',fontsize,'bold')
        bd=10
        if ifcell:return fglist
    elif stylemode=='classic':
        if ifday():bg,fg='white','black'
        else:bg,fg='black','white'
        hg='gray'
        fontsize=20
        font=('楷体',fontsize,'bold')
        bd=2
        if ifcell:return fg
    cellsize,imgsize=fontsize*1.5,fontsize*2
mode()

# 加载图片资源
flagimg=PIL.ImageTk.PhotoImage(PIL.Image.open(path+'/flag.png').resize((imgsize,imgsize)))
bombimg=PIL.ImageTk.PhotoImage(PIL.Image.open(path+'/bomb.png').resize((imgsize,imgsize)))
pixel_unit=tk.PhotoImage(path+'/pixel_unit.png')


# ————————————————————
# 格子类
# ————————————————————

class Cell:
    def __init__(self,x:int,y:int):
        # self.s表示展示，self.f表示标旗，self.c表示内容
        self.x,self.y=x,y
        self.c=get_content(x,y)
        # self.b表示按钮对象
        self.s=False
        self.f=False
        self.a=False
        self.b=tk.Button(playboardframe,state='normal',font=font,bd=bd/2,relief='raised',image=pixel_unit,width=cellsize,height=cellsize,compound='center',command=self.show)
        self.b.bind('<ButtonRelease-3>',lambda event:self.flag())
        self.b.bind('<Enter>',lambda event:self.motion())
        self.b.bind('<Leave>',lambda event:self.normal())
        self.b.grid(row=self.y,column=self.x)
        self.bg=bg
        self.fg=None

    # 快捷展示内容函数
    def showcontent(self):
        self.s=True
        # slowcheck()
        if self.c==9:
            self.config(image=bombimg)
            if not overgame:
                if undo_control.get():
                    self.s=False
                    undo(self.reset)
                else:gameover(False)
        elif self.c==0:
            if not (mixer.get_busy() or overgame):sound_showblock.play()
            self.config(image=pixel_unit,relief='sunken',state='disabled')
            self.showaround()
        else:self.config(relief='sunken',text=self.c,width=cellsize-2,height=cellsize-2)
    
    def reset(self):
        if not self.f:self.config(image=pixel_unit)
        tipclear()
    
    def rewrite(self):
        self.c=get_content(self.x,self.y)

    # 左键调用
    def show(self):
        global startgame
        if startgame:
            if overgame:
                if not self.s:self.showcontent()
            else:
                if self.s:
                    if self.c!=0 and self.c!=9:
                        if aroundflag(self.x,self.y)==self.c:self.showaround()
                else:
                    if not self.f:self.showcontent()
                    ifwin()
                    if autoflag_control.get():autoflag()
        else:
            if newgame:gamestart(self.x,self.y)
            else:
                startgame=True
                self.show()
    
    # 右键调用
    def flag(self):
        if startgame and not (overgame or self.s):
            self.f=not self.f
            if self.f:
                self.config(image=flagimg)
                countbomb(self.f)
            else:
                self.config(image=pixel_unit)
                countbomb(self.f)

    # 展示周围
    def showaround(self):
        l=around(self.x,self.y)
        for coord in l:
            item=get_item(coord[0],coord[1])
            if not item.ifshow():item.show()
    
    # 标旗周围
    def flagaround(self):
        l=around(self.x,self.y)
        a=len(l)
        for coord in l:
            if get_item(coord[0],coord[1]).ifshow():a-=1
        if a==self.c:
            for coord in l:
                item=get_item(coord[0],coord[1])
                if not (item.ifshow() or item.ifflag()):item.flag()

    # 中转函数
    def config(self,**infor):
        if self.a:
            if 'bg' in infor.keys():infor.pop('bg')
        self.b.config(**infor)

    def standard(self,fgl):
        if not animation_control.get():
            self.bg=bg
            if not (self.ifzero() or self.ifmine()):
                if isinstance(fgl,str):self.fg=fgl
                else:self.fg=fgl[self.c-1]
            else:self.fg=None
        self.config(bg=self.bg,fg=self.fg,font=font,bd=bd/2)

    def randomcolor(self):
        r=random.randint(0,255)
        g=random.randint(0,255)
        b=random.randint(0,255)
        self.bg=rgb(r,g,b)
        self.fg=rgb(255-r,255-g,255-b)
        self.config(bg=self.bg,fg=self.fg)

    # 快捷删除清理内存
    def kill(self):
        self.b.destroy()

    # 快捷函数防泄漏
    def get_coord(self):
        return self.x,self.y
    def ifzero(self):
        return self.c==0
    def ifmine(self):
        return self.c==9
    def ifshow(self):
        return self.s
    def ifflag(self):
        return self.f
    
    # 高亮函数
    def motion(self):
        movefocus(position=(self.x,self.y))
    def active(self):
        self.a=True
        self.b.config(bg=hg)
    def normal(self):
        self.a=False
        self.config(bg=self.bg)


# ————————————————————
# 主按钮
# ————————————————————

class Mainbutton:
    def __init__(self):
        self.button=tk.Button(playcontrol,text='新游戏',width=6,bg=bg,fg=fg,font=font,bd=bd,relief='groove',command=self.left)

    def config(self,**infor):
        self.button.config(**infor)

    def pack(self,**infor):
        self.button.pack(**infor)

    def left(self):
        global startgame,overgame,newgame,playmap
        if startgame and not overgame:
            timer.cancel()
            gameover(False)
        else:
            newgame=True
            startgame=False
            overgame=False
            resettime()
            resetbomb()
            tipclear()
            playmap=[[0 for _ in range(width)] for _ in range(height)]
            createmap()
            items['chest'].standard()
            self.config(text='新游戏')
            self.button.unbind('<ButtonRelease-3>')
            window.update_idletasks()

    def right(self):
        global startgame,overgame,newgame
        if startgame and overgame:
            newgame=False
            startgame=False
            overgame=False
            resettime()
            resetbomb(bomb)
            tipclear()
            createmap()
            items['chest'].standard()
            self.config(text='放弃')
            window.update_idletasks()
            timer.start()
    
    def buttonbind(self):
        self.button.bind('<ButtonRelease-3>',lambda event:self.right())

def createmap():
    global cellmap
    for line in cellmap:
        for item in line:item.kill()
    cellmap=[[None for _ in range(width)] for _ in range(height)]
    for ay in range(height):
        for ax in range(width):cellmap[ay][ax]=Cell(ax,ay)
    window.update_idletasks()
    playboard.config(scrollregion=playboardframe.bbox())

def gamestart(x:int,y:int):
    global startgame,playmap
    startgame=True
    resetbomb(bomb)
    # 随机布雷
    if space>9 and space-bomb>8:l=around(x,y)
    else:l=[]
    l.append((x,y))
    choice=random.sample(tuple(set(range(0,space))-set((ay*width+ax for ax,ay in l))),bomb)
    for num in choice:
        playmap[num//width][num%width]=9
    # 布置数字
    for ay in range(height):
        for ax in range(width):
            if get_content(ax,ay)!=9:
                playmap[ay][ax]=aroundbomb(ax,ay)
    # 重写cellmap
    for line in cellmap:
        for item in line:
                item.rewrite()
    sound_gamestart.play()
    items['chest'].standard()
    get_item(x,y).show()
    mainbutton.config(text='放弃')
    window.update_idletasks()
    timer.start()

def gameover(win:bool):
    global overgame,data
    overgame=True
    timer.cancel()
    resetbomb(bomb)
    for line in cellmap:
        for item in line:
            item.show()
    mainbutton.config(text='新游戏') 
    a=dif-1
    data[a][0]+=1
    if win:
        text='你赢了！'
        data[a][1]+=1
        if data[a][2]==0 or playtime<data[a][2]:
            data[a][2]=playtime
            text+='恭喜突破记录！'
            wintime=True
        tip.config(text=text)
        win_animation()
        if wintime:win_animation()
    else:
        tip.config(text='你输了！（右键重试）')
        mainbutton.buttonbind()
        items['chest'].warning()

def ifwin():
    if not overgame:
        num=space-bomb
        shownnum=0
        for line in cellmap:
            for item in line:
                if not item.ifmine() and item.ifshow():
                    shownnum+=1
        if shownnum>=num:gameover(True)

def win_animation():
    for _ in range(5):
        items['background'].randomcolor(can=False)
        items['chest'].randomeveryone(can=False)
        window.update_idletasks()
        time.sleep(0.1)
    for item in items.values():item.standard()

# 有关检查游戏区的基本函数
def get_content(x:int,y:int):
    return playmap[y][x]

def get_item(x:int,y:int):
    return cellmap[y][x]

def around(x:int,y:int):
    l=((x-1,y-1),(x,y-1),(x+1,y-1),(x-1,y),(x+1,y),(x-1,y+1),(x,y+1),(x+1,y+1))
    a=[]
    for coord in l:
        if -1<coord[0]<width and -1<coord[1]<height:a.append(coord)
    return a

# 周围雷数
def aroundbomb(x:int,y:int):
    l=around(x,y)
    a=0
    for coord in l:
        if get_content(coord[0],coord[1])==9:a+=1
    return a

# 周围旗数
def aroundflag(x:int,y:int):
    l=around(x,y)
    a=0
    for coord in l:
        if get_item(coord[0],coord[1]).ifflag():a+=1
    return a



# ————————————————————
# 计时器
# ————————————————————

def resettime():
    global playtime,timer
    playtime=0
    timeshower.config(text=playtime)
    timer=threading.Timer(1,addtime)
    timer.daemon=True

def addtime():
    global playtime
    if startgame and (not overgame) and playtime<999:
        with timelock:playtime+=1
        timeshower.config(text=playtime)
        timer.run()

timelock=threading.Lock()

# ————————————————————
# 计雷器
# ————————————————————

def resetbomb(bombnum=0):
    global remainbomb
    remainbomb=bombnum
    bombshower.config(text=remainbomb)

def countbomb(flag:bool):
    global remainbomb
    if flag:
        remainbomb-=1
        bombshower.config(text=remainbomb)
    else:
        remainbomb+=1
        bombshower.config(text=remainbomb)


# ————————————————————
# 创建游戏界面
# ————————————————————

# 扫雷区
playboard=tk.Canvas(window,bg=bg,bd=bd,relief='flat',highlightthickness=0)
playboardframe=tk.Frame(playboard)
playboardybarframe=tk.Frame(window)
playboardblock=tk.Label(playboardybarframe,width=13,height=13,image=pixel_unit,bg=bg)
playboardybar=tk.Scrollbar(playboardybarframe,orient='vertical',command=playboard.yview)
playboardxbar=tk.Scrollbar(window,orient='horizontal',command=playboard.xview)
playboard.config(yscrollcommand=playboardybar.set,xscrollcommand=playboardxbar.set)

# 状态区
playcontrol=tk.Frame(window,bd=0,relief='flat',bg=bg)

mainbutton=Mainbutton()
tip=tk.Label(playcontrol,bg=bg,fg=fg,font=font,height=1)
def tipclear():tip.config(text='')
timeshower=tk.Label(playcontrol,bg=bg,fg=fg,font=font,bd=bd,relief='ridge',width=3,height=1)
bombshower=tk.Label(playcontrol,bg=bg,fg=fg,font=font,bd=bd,relief='ridge',width=3,height=1)

# 测试用按钮
adminbutton=tk.Button(playcontrol,text='测试按钮（左赢右输）',bg=bg,fg=fg,font=font,bd=bd,relief='groove',command=lambda:gameover(True))
adminbutton.bind('<ButtonRelease-3>',lambda event:gameover(False))

# 数据区
playnet=tk.Frame(window,bd=0,relief='flat',bg=bg)


# ————————————————————
# 全局变量
# ————————————————————

# 三大状态控制变量
startgame=False
overgame=False
newgame=True

# 两大扫雷地图变量
playmap=[[0 for _ in range(width)] for _ in range(height)]
cellmap=[[None for _ in range(width)] for _ in range(height)]
for ay in range(height):
    for ax in range(width):cellmap[ay][ax]=Cell(ax,ay)


# ————————————————————
# 弹出窗口
# ————————————————————

# 查看数据
class Showdata:
    def __init__(self):
        showdata_root=tk.Toplevel(window,bg=bg,bd=bd)
        showdata_root.title('查看数据')
        note=tk.Label(showdata_root,text='注意：以下仅为本地保存数据；删除按钮将\n直接删除您的数据，无法反悔，请三思。',bg=bg,fg=fg,font=font,bd=bd)
        note.pack(side='top')
        diflist=['简单','一般','困难','挑战']
        text=''
        for i in range(4):text+=diflist[i]+'：'+f'共{data[i][0]}局，胜{data[i][1]}局，胜率为{self.winrate(data[i][0],data[i][1])}%，最快用时{data[i][2]}秒'+'\n'
        self.showdata_datalabel=tk.Label(showdata_root,text=text,bg=bg,fg=fg,font=font,bd=bd)
        self.showdata_datalabel.pack(expand=True,fill='both')
        deletebutton=tk.Button(showdata_root,text='删除数据',bg=bg,fg=fg,font=font,bd=bd,relief='groove',command=self.showdata)
        deletebutton.pack(side='left')
        okbutton=tk.Button(showdata_root,text='关闭窗口',bg=bg,fg=fg,font=font,bd=bd,relief='groove',command=showdata_root.destroy)
        okbutton.pack(side='right')
        showdata_root.resizable(False,False)
        showdata_root.focus_set()
        showdata_root.grab_set()
        showdata_root.wait_window()

    def showdata(self):
        global data
        data=[[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
        save()
        diflist=['简单','一般','困难','挑战']
        text=''
        for i in range(4):text+=diflist[i]+'：'+f'共{data[i][0]}局，胜{data[i][1]}局，胜率为{self.winrate(data[i][0],data[i][1])}%，最快用时{data[i][2]}秒'+'\n'
        self.showdata_datalabel.config(text=text)

    # 计算胜率
    def winrate(self,alltimes,wintimes):
        if alltimes==0 or wintimes==0:return 0
        else:return round(wintimes*100/alltimes,2)

# 选择难度
class Changedif:
    def __init__(self):
        global overgame,dif
        self.chosen=False
        self.dif=tk.IntVar(value=dif)
        self.root=tk.Toplevel(window,bg=bg,bd=bd)
        self.root.title('选择难度')
        self.note=tk.Label(self.root,text='注意：更改难度再点击确定后将会重\n新开始游戏，不会保存本局记录。',bg=bg,fg=fg,font=font,bd=bd)
        self.note.pack(side='top')
        self.easymode=tk.Radiobutton(self.root,variable=self.dif,value=1,bg=bg,fg=fg,font=font,bd=bd,text='简单：9×9大小，10个雷，12.35%密度',command=self.ifcustom)
        self.easymode.pack(anchor='w')
        self.middlemode=tk.Radiobutton(self.root,variable=self.dif,value=2,bg=bg,fg=fg,font=font,bd=bd,text='一般：16×16大小，40个雷，15.63%密度',command=self.ifcustom)
        self.middlemode.pack(anchor='w')
        self.hardmode=tk.Radiobutton(self.root,variable=self.dif,value=3,bg=bg,fg=fg,font=font,bd=bd,text='困难：30×16大小，99个雷，20.63%密度',command=self.ifcustom)
        self.hardmode.pack(anchor='w')
        self.custom=tk.Frame(self.root,bg=bg)

        self.custommode=tk.Radiobutton(self.custom,variable=self.dif,value=4,bg=bg,fg=fg,font=font,bd=bd,text='自定义：',command=self.ifcustom)
        self.custommode.pack(side='left')
        self.customtip=tk.Label(self.custom,text='宽度： 高度： 雷数： ',bg=bg,fg=fg,font=font)
        self.customtip.pack(side='top',anchor='w')
        self.width,self.height,self.bomb=(tk.Variable()for _ in range(3))
        self.entrylist=[
            tk.Spinbox(self.custom,bg=bg,fg=fg,font=font,width=5,disabledbackground='gray',from_=2,to=100,textvariable=self.width),
            tk.Spinbox(self.custom,bg=bg,fg=fg,font=font,width=5,disabledbackground='gray',from_=2,to=100,textvariable=self.height),
            tk.Spinbox(self.custom,bg=bg,fg=fg,font=font,width=5,disabledbackground='gray',from_=1,to=3,textvariable=self.bomb)]
        for item in self.entrylist:
            item.bind('<KeyPress>',lambda event:self.inputdata())
            item.pack(side='left')
        self.warn=tk.StringVar()
        self.customwarn=tk.Message(self.custom,width=90,bg=bg,fg=fg,font=(font[0],int(font[1]*0.5),font[2]),textvariable=self.warn)
        self.customwarn.pack(side='left')
        self.custom.pack(anchor='w')
        self.ifcustom()
        self.legal=False
        self.challengemode=tk.Radiobutton(self.root,variable=self.dif,value=5,bg=bg,fg=fg,font=font,bd=bd,text='挑战：',command=self.ifcustom)
        self.challengemode.pack(anchor='w')
        self.okbutton=tk.Button(self.root,text='选好啦',bg=bg,fg=fg,font=font,bd=bd,relief='groove',command=self.delete)
        self.okbutton.pack(side='bottom')
        self.root.resizable(False,False)
        self.root.focus_set()
        self.root.grab_set()
        self.root.wait_window()
        if self.chosen:
            dif=self.dif.get()
            if dif==4:
                if self.legal:fastdata(int(self.width.get()),int(self.height.get()),int(self.bomb.get()))
                else:
                    tkmessage.showwarning('提示','无法解析自定义输入，已自动将难度改为简单。')
                    dif=1
                    fastdata()
            else:fastdata()
            overgame=True
            mainbutton.left()

    def delete(self):
        self.chosen=True
        self.root.destroy()

    def ifcustom(self):
        if self.dif.get()==4:
            for item in self.entrylist:item.config(state='normal')
        else:
            for item in self.entrylist:item.config(state='disabled')
            self.warn.set('')

    def inputdata_infunc(self):
        widthlegal,heightlegal=False,False
        try:
            awidth=int(self.width.get())
            if awidth<2:self.width.set(2)
            elif awidth>100:self.width.set(100)
            else:widthlegal=True
            aheight=int(self.height.get())
            if aheight<2:self.height.set(2)
            elif aheight>100:self.height.set(100)
            else:heightlegal=True
            abomb=int(self.bomb.get())
            if not widthlegal:self.warn.set('长度输入范围为2~100')
            elif not heightlegal:self.warn.set('宽度输入范围为2~100')
            else:
                self.entrylist[2].config(to=awidth*aheight-1)
                if abomb<1:
                    self.bomb.set(1)
                    self.warn.set('不能没有雷')
                elif abomb>awidth*aheight-1:
                    self.bomb.set(awidth*aheight-1)
                    self.warn.set('雷数超过总格数')
                else:
                    threading.Timer(1,lambda:self.warn.set('')).start()
                    self.legal=True
        except:self.warn.set('请输入数字')
    
    def inputdata(self):
        threading.Timer(0.1,self.inputdata_infunc).start()

# 游戏设置
class Setting:
    def __init__(self):
        self.setting_root=tk.Toplevel(window,bg=bg,bd=bd)
        self.setting_root.title('设置')
        # 调节音量
        self.pausebutton=tk.Button(self.setting_root,bg=bg,fg=fg,font=font,bd=bd,command=self.pause,relief='groove')
        if mixer.music.get_busy():self.pausebutton.config(text='停止背景音乐')
        else:self.pausebutton.config(text='播放背景音乐')
        self.pausebutton.pack(side='top',anchor='e')
        self.avolume=tk.IntVar(value=volume*100)
        self.volumescale=tk.Scale(self.setting_root,label='调节音量：',bg=bg,fg=fg,font=font,orient='horizontal',from_=0,to=100,length=200,variable=self.avolume,command=setvolume)
        self.volumescale.pack(side='top',fill='x')
    def pause(self):
        global ifplaybgm
        if mixer.music.get_busy():
            mixer.music.stop()
            self.pausebutton.config(text='播放背景音乐')
            ifplaybgm=False
        else:
            mixer.music.play(-1)
            self.pausebutton.config(text='停止背景音乐')
            ifplaybgm=True


# ————————————————————
# 动画特效
# ————————————————————

items={}

# 针对所有组件的总控
class Animation:
    def __init__(self,*allitems):
        self.allitems=allitems
        self.bg=bg
        self.n=range(3)
        self.lock=threading.Lock()
    
    def all_config(self,**infor):
        for item in self.allitems:item.config(**infor)

    # 标准色
    def standard_func(self):
        with self.lock:
            self.bg=bg
            self.all_config(bg=self.bg)

    def standard(self):
        if not animation_control.get():threading.Thread(target=self.standard_func,daemon=True).start()

    # 渐变色
    def softcolor_func(self,fc,ec,speed):
        nc=list(fc)
        times=[ec[i]-fc[i] for i in self.n]
        maintime=max(map(abs,times))
        steps=[int(times[i]/maintime) for i in self.n]
        for _ in range(maintime):
            if not animation_control.get():break
            with self.lock:
                for i in self.n:nc[i]+=steps[i]
                self.bg=rgb(nc[0],nc[1],nc[2])
                self.all_config(bg=self.bg)
            time.sleep(speed)
        with self.lock:
            if animation_control.get():
                for i in self.n:nc[i]=ec[i]
                self.bg=rgb(nc[0],nc[1],nc[2])
                self.all_config(bg=self.bg)

    def softcolor(self,fc:tuple,ec:tuple,speed:int):
        threading.Thread(target=self.softcolor_func,kwargs={'fc':fc,'ec':ec,'speed':speed},daemon=True).start()

    # 循环五彩色
    def softloop_func(self,speed):
        colorlist=((255,0,0),(255,255,0),(0,255,0),(0,255,255),(0,0,255),(255,0,255))
        n=0
        while animation_control.get():
            if n==5:
                self.softcolor_func(colorlist[5],colorlist[0],speed)
                n=-1
            else:self.softcolor_func(colorlist[n],colorlist[n+1],speed)
            n+=1

    def softloop(self,speed=0.001):
        threading.Thread(target=self.softloop_func,kwargs={'speed':speed},daemon=True).start()

    # 警告动画
    def warning_func(self,times):
        with self.lock:
            for _ in range(times):
                time.sleep(0.1)
                self.all_config(bg='black')
                window.update_idletasks()
                time.sleep(0.1)
                self.all_config(bg=self.bg)
                window.update_idletasks()
    
    def warning(self,times=2):
        threading.Thread(target=self.warning_func,kwargs={'times':times},daemon=True).start()
    
    # 整体随机
    def randomcolor(self,speed=1,can=True):
        if not can or animation_control.get():
            r=random.randint(0,255)
            g=random.randint(0,255)
            b=random.randint(0,255)
            self.bg=rgb(r,g,b)
            self.all_config(bg=self.bg)
            if can:window.after(speed*1000,self.randomcolor)

items['background']=Animation(window,playboard,playcontrol,tip,mainbutton,timeshower,bombshower,playnet,playboardblock)
items['havewords']=Animation(tip,mainbutton,timeshower,bombshower)

# 专门针对扫雷棋盘区
class Animation_chest(Animation):
    def __init__(self):
        Animation.__init__(self,None)
        self.fg=fg

    # 重写变色函数
    def all_config(self,**infor):
        for line in cellmap:
            for item in line:item.config(**infor)

    # def line_config(self,**infor):

    # 标准色（只用于棋盘）
    def standard(self):
        fgl=mode(True)
        for line in cellmap:
            for item in line:item.standard(fgl)

    # 警告动画
    def warning(self,times=2):
        for _ in range(times):
            time.sleep(0.1)
            for line in cellmap:
                for item in line:
                    if item.ifmine():item.config(bg='black')
            window.update_idletasks()
            time.sleep(0.1)
            for line in cellmap:
                for item in line:
                    if item.ifmine():item.config(bg=item.bg)
            window.update_idletasks()

    # 整体随机
    def randomcolor(self,speed=1,can=True):
        if not can or animation_control.get():
            r=random.randint(0,255)
            g=random.randint(0,255)
            b=random.randint(0,255)
            self.bg=rgb(r,g,b)
            self.fg=rgb(255-r,255-g,255-b)
            for line in cellmap:
                for item in line:
                    item.bg=self.bg
                    item.fg=self.fg
                    item.config(bg=self.bg,fg=self.fg)
            if can:window.after(speed*1000,self.randomcolor)

    # 分别随机
    def randomeveryone(self,speed=1,can=True):
        if not can or animation_control.get():
            for line in cellmap:
                for item in line:item.randomcolor()
            if can:window.after(speed*1000,self.randomeveryone)

items['chest']=Animation_chest()

def animation_mode():
    for item in items.values():item.standard()
    if animation_control.get():
        items['background'].softloop()
        items['chest'].randomcolor()
    window.update_idletasks()

# 切换风格
def changestyle():
    global stylemode
    if stylemode=='classic':stylemode='simple'
    else:stylemode='classic'
    mode()
    items['background'].standard()
    items['havewords'].all_config(fg=fg,font=font,bd=bd)
    items['chest'].standard()
    window.update_idletasks()
    playboard.config(scrollregion=playboardframe.bbox())


# ————————————————————
# 键盘控制
# ————————————————————

def movefocus(event=None,position=None):
    global focuscoord
    get_item(focuscoord[0],focuscoord[1]).normal()
    key=''
    if event:
        key=event.keysym
        match key:
            case 'Left':
                focuscoord[0]-=1
                if focuscoord[0]<0:focuscoord[0]=width-1
            case 'Right':
                focuscoord[0]+=1
                if focuscoord[0]>=width:focuscoord[0]=0
            case 'Up':
                focuscoord[1]-=1
                if focuscoord[1]<0:focuscoord[1]=height-1
            case 'Down':
                focuscoord[1]+=1
                if focuscoord[1]>=height:focuscoord[1]=0
    else:focuscoord=list(position)
    item=get_item(focuscoord[0],focuscoord[1])
    item.active()
    if key=='Return' or key=='space':
        if event.state==8:item.show()
        elif event.state==12:item.flag()

focuscoord=[0,0]
window.bind(f'<KeyPress>',movefocus)


# ————————————————————
# 音乐播放
# ————————————————————

def setvolume(avolume):
    global volume
    volume=int(avolume)/100
    mixer.music.set_volume(volume)
    for sound in sounds:sound.set_volume(volume)

mixer.music.load(path+'/bgm.mp3')

sound_gamestart=mixer.Sound(path+'/gamestart.mp3')
sound_showblock=mixer.Sound(path+'/showblock.mp3')
sounds=(sound_gamestart,sound_showblock)

mixer.music.set_volume(volume)
for sound in sounds:sound.set_volume(volume)

window.bind('<Unmap>',lambda event:mixer.music.pause())
window.bind('<Map>',lambda event:mixer.music.unpause())


# ————————————————————
# 自动标旗
# ————————————————————

def autoflag():
    for line in cellmap:
        for item in line:
            if item.ifshow() and not item.ifzero():
                item.flagaround()

def autoflag_mode():
    if startgame and not overgame and autoflag_control.get():autoflag()


# ————————————————————
# 撤回模式
# ————————————————————

def undo(reset):
    global playtime
    with timelock:
        if dif in range(1,4):playtime+=dif*5
    tip.config(text='啊！你踩到了雷！')
    window.update_idletasks()
    items['background'].warning()
    a=threading.Timer(1,reset)
    a.daemon=True
    a.start()


# ————————————————————
# 互联网联机
# ————————————————————

server=socket.socket()
client=socket.socket()


# ————————————————————
# 初始化游戏界面
# ————————————————————

Tempvar.endtime=time.time()
print(f'Python版本：{sys.version}')
print(f'加载时间：{Tempvar.endtime-Tempvar.firsttime} 秒。加载成功！')
print(f'欢迎游玩PYMinesweeper（version:{version}）！ ——由Tilawa Cesoil开发')
print('更多内容请访问：https://github.com/Tilawa-Cesoil/Tilawa-Cesoil/tree/main/PYMinesweeper')
print(Tempvar.splitline)
# 重定向输出
sys.stdout=Tempvar.output
if ifplaybgm:mixer.music.play(-1)
# 关闭加载界面动画
for loadingcolor in range(255,-1,-1):
    time.sleep(0.02)
    Tempvar.loading.config(fg=rgb(loadingcolor,loadingcolor,loadingcolor))
    window.update_idletasks()
Tempvar.loading.destroy()
del Tempvar,Restdout,loadingcolor

# 重置窗口显示
window.bind('<Escape>',lambda event:window.quit())
window.config(bd=bd)
window.geometry('')
resettime()
resetbomb()
animation_mode()
autoflag_mode()

# 菜单栏
topmenu=tk.Menu(window)
window.config(bg=bg,menu=topmenu)
topmenu.add_command(label='选择难度',command=Changedif)
topmenu.add_command(label='查看数据',command=Showdata)
animation_menu=tk.Menu(topmenu,tearoff=False)
animation_menu.add_checkbutton(label='五彩特效',variable=animation_control,command=animation_mode)
animation_menu.add_checkbutton(label='自动标旗',variable=autoflag_control,command=autoflag_mode)
animation_menu.add_checkbutton(label='新手模式',variable=undo_control)
topmenu.add_cascade(menu=animation_menu,label='功能控制')
topmenu.add_command(label='设置',command=Setting)
topmenu.add_command(label='切换风格',command=changestyle)
# 主框架
playcontrol.pack(side='bottom',fill='x')
mainbutton.pack(side='right')
timeshower.pack(side='left',padx=5)
bombshower.pack(side='left',padx=5)
tip.pack(expand=True,fill='x')

playnet.pack(side='right',fill='y')

playboardybarframe.pack(side='right',fill='y')
playboardblock.pack(side='bottom')
playboardybar.pack(side='right',fill='y')
playboardxbar.pack(side='bottom',fill='x')
playboardframe.pack()
playboard.create_window(0,0,anchor='nw',window=playboardframe)
playboard.config(width=playboardframe.winfo_reqwidth(),height=playboardframe.winfo_reqheight(),scrollregion=playboardframe.bbox())
playboard.pack(fill='both',expand=True)

# 刷新屏幕
window.update_idletasks()
# 设定窗口居中展示
window.geometry(f'+{int(window.winfo_screenwidth()/2-window.winfo_reqwidth()/2)}+{int(window.winfo_screenheight()/2-window.winfo_reqheight()/2)}')

# 在主窗口退出前程序将在此停止
window.mainloop()


# ————————————————————
# 退出游戏
# ————————————————————

overgame=True
mixer.music.stop()
mixer.quit()
save_func()