# -*- coding: utf-8 -*-
"""
Created on Mon May 31 17:28:05 2021

@author: Administrator
"""
import os
import tkinter as tk
from tkinter import messagebox
import configparser
import math
import pygame
import pygame.freetype
from pygame.locals import *
from sys import exit
import random
import asyncio
import websockets
import nest_asyncio
nest_asyncio.apply()






window = tk.Tk()
window.title('贪 吃 蛇')

window.geometry('300x300')
score=0
globalscore=0
# imgpath=''
# field_width=0
# field_height=0
# start_x=0
# start_y=0
# superfoodrate=0
# helperrate=0
def game(name):
    class playerhead(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.originimage = pygame.image.load(imgpath+'head.png')
            self.angle=0
            self.v=[0,0]
            self.accr_rotate=0
            self.maxspeed=0
            self.vsave0=0
            self.vsave1=0
            self.image=pygame.transform.rotate(self.originimage,-math.degrees(self.angle))
            self.rect = self.originimage.get_rect()
        def isInBorder(self):
            #边界检测
            if (self.rect.left >= 0 and self.rect.right <= field_width) and (self.rect.top >= 0 and self.rect.bottom <= field_height):
                return True
            else:
                return False
        def move(self):
            #限制角度范围，防止游戏过久后溢出
            if abs(math.degrees(self.angle))>=360:
                self.angle-=(math.pi*2)*self.angle/abs(self.angle)
            #边界检测。在边界内就执行运动代码
            if self.isInBorder():
                a=math.cos(self.angle)
                b=math.sin(self.angle)
                #旋转。1.0001是为了防止出现除0错误
                self.angle+=math.radians(move_lr)
                #旋转车体
                self.image=pygame.transform.rotate(self.originimage,-math.degrees(self.angle))
                self.rect = self.image.get_rect(center=self.rect.center)
                #用累积法储存速度，速度超过1就把整数部分加到坐标上，然后扣掉自己的整数部分
                self.v=[self.maxspeed*a,self.maxspeed*b]
                self.vsave0+=self.v[0]
                self.vsave1+=self.v[1]
                if abs(self.vsave0)>=1:
                    self.rect.centerx+=int(self.vsave0)
                    self.vsave0-=int(self.vsave0)
                if abs(self.vsave1)>=1:
                    self.rect.centery+=int(self.vsave1)
                    self.vsave1-=int(self.vsave1)
    class playerbody(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.number=0
            self.originimage = pygame.image.load(imgpath+'body.png')
            self.angle=0
            self.rect = self.originimage.get_rect()
            self.image=pygame.transform.rotate(self.originimage,-math.degrees(self.angle))
        def update(self):
            if self.number==len(body_group.sprites())-1:
                self.angle=body_group.sprites()[0].angle
                self.image=pygame.transform.rotate(self.originimage,-math.degrees(self.angle))
                self.rect = self.image.get_rect(center=self.rect.center)
                self.rect.move_ip(body_group.sprites()[0].rect.centerx-self.rect.centerx,body_group.sprites()[0].rect.centery-self.rect.centery)
                self.number=1
            else:
                self.number+=1
        
    class foodSprite(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load(imgpath+'food.png')
            self.rect = self.image.get_rect()
            self.type = 0
            #0为普通食物，1为超级食物，2为遥控器
    class poisonSprite(pygame.sprite.Sprite):
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load(imgpath+'poison.png')
            self.rect = self.image.get_rect()
    pygame.init()
    #global field_width,field_height,start_x,start_y,superfoodrate,helperrate
    imgpath=''
    field_width=0
    field_height=0
    start_x=0
    start_y=0
    superfoodrate=0
    helperrate=0
    config = configparser.ConfigParser()
    config.read('./resources/'+name+'/config.ini',encoding='utf-8')
    field_width = config.getint('basic', 'field_width')
    field_height = config.getint('basic', 'field_height')
    start_x = config.getint('basic', 'start_x')
    start_y = config.getint('basic', 'start_y')
    superfoodrate=config.getint('basic', 'super_food_rate')
    helperrate=config.getint('basic', 'helper_rate')
    backgroundimg=pygame.image.load('./resources/'+name+'/bg.png')
    imgpath='./resources/'+name+'/'
    #设置游戏帧数。每一帧，屏幕画面就会被刷新一次。
    fps = 60
    fcclock = pygame.time.Clock()
    game_over = False
    #分辨率设置
    screen=pygame.display.set_mode([field_width,field_height])
    pygame.display.set_caption('CLICK SPACE TO START THE GAME')
    pygame.display.set_icon(pygame.image.load('./resources/icon.png'))
    #初始化按键控制部分
    keys = {'right':False, 'left':False}
    #初始化游戏，创建坦克对象和资源对象
    bodyhead = playerhead()
    bodyhead.rect.move_ip(start_x,start_y)
    bodyhead.accr_rotate=config.getfloat('player', 'accr_rotate')
    bodyhead.maxspeed=config.getfloat('player', 'maxspeed')
    body_group = pygame.sprite.Group()
    body_group2 = pygame.sprite.Group()
    body_group.add(bodyhead)
    food_group = pygame.sprite.Group()
    poison_group = pygame.sprite.Group()
    for n in range(1,30):
        food = foodSprite();
        food.position = random.randint(0,field_width-100),random.randint(0,field_height-100)
        food.rect.move_ip(food.position)
        food_group.add(food)
    for n in range(1,5):
        poison = poisonSprite();
        poison.position = random.randint(0,field_width-100),random.randint(0,field_height-100)
        poison.rect.move_ip(poison.position)
        poison_group.add(poison)
    global score,globalscore
    score=0
    #游戏tick
    body=playerbody()
    body.number=len(body_group.sprites())
    body.angle=body_group.sprites()[len(body_group.sprites())-1].angle
    body.rect.move_ip(body_group.sprites()[len(body_group.sprites())-1].rect.centerx,body_group.sprites()[len(body_group.sprites())-1].rect.centery)
    body_group.add(body)
    paused=False
    startgame=0
    health=1
    while True:
        if len(food_group)<20:
            food = foodSprite();
            n=random.randint(1,100)
            if n<superfoodrate:
                food.type=1
                food.image = pygame.image.load(imgpath+'superfood.png')
            if n<superfoodrate+helperrate and n>=superfoodrate:
                food.type=2
                food.image = pygame.image.load(imgpath+'helper.png')
            food.position = random.randint(0,field_width-100),random.randint(0,field_height-100)
            food.rect.move_ip(food.position)
            food_group.add(food)
            t1=random.randint(0,field_width-100)
            t2=random.randint(0,field_height-100)
            if (t1-body.rect.centerx)*(t1-body.rect.centerx)+(t2-body.rect.centerx)*(t1-body.rect.centerx)>5000:
                poison = poisonSprite();
                poison.position = t1,t2
                poison.rect.move_ip(poison.position)
                poison_group.add(poison)
        move_lr=0
        #显示背景
        screen.fill((102,204,255))
        screen.blit(backgroundimg,[0,0])
        #获取鼠标位置
        mousepos_x,mousepos_y = pygame.mouse.get_pos()
        #f1.render_to(screen,[0,0],'%d,%d'%(mousepos_x,mousepos_y),fgcolor=(255,255,255),size=50)
        #事件处理
        for event in pygame.event.get():
            if event.type==QUIT:
                #退出游戏事件
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                #按键检测，移动
                if event.key == pygame.K_d:
                    keys['right'] = True
                if event.key == pygame.K_a:
                    keys['left'] = True
                if event.key == pygame.K_SPACE:
                    if paused:
                        paused=False
                        pygame.display.set_caption('Your score is:'+str(score)+'. Press SPACE to pause/unpause.')
                    else:
                        paused=True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    keys['right'] = False
                if event.key == pygame.K_a:
                    keys['left'] = False
        food_group.draw(screen)
        poison_group.draw(screen)
        buttons = pygame.mouse.get_pressed()
        if paused:
            body_group.draw(screen)
            pygame.display.update()
            continue
        #速度处理
        if keys['right']:
            move_lr = bodyhead.accr_rotate
        if keys['left']:
            move_lr = -bodyhead.accr_rotate
        if keys['right'] and keys['left']:
            move_lr = 0
        attacker = None
        attacker = pygame.sprite.spritecollideany(bodyhead, food_group)
        if attacker != None:
            if pygame.sprite.collide_circle_ratio(0.65)(bodyhead,attacker):
                #player_health +=2;
                if attacker.type==0:
                    body=playerbody()
                    body.number=len(body_group.sprites())
                    body.angle=body_group.sprites()[len(body_group.sprites())-1].angle
                    body.rect.move_ip(body_group.sprites()[len(body_group.sprites())-1].rect.centerx,body_group.sprites()[len(body_group.sprites())-1].rect.centery)
                    #body.rect.move(     -10*math.cos(body_group.sprites()[len(body_group.sprites())-1].angle)  , -10*math.sin(body_group.sprites()[len(body_group.sprites())-1].angle)   )
                    body_group.add(body)
                    if body.number>40: body_group2.add(body)
                    score+=1
                if attacker.type==1:#超级食物，加一次生命值
                    score+=5
                    health+=1
                if attacker.type==2:#遥控器，引爆场上所有炸弹
                    score+=10
                    for i in poison_group:
                        poison_group.remove(i)
                food_group.remove(attacker);
                pygame.display.set_caption('Your score is:'+str(score)+'. Press SPACE to pause/unpause.')
        attacker = None
        attacker = pygame.sprite.spritecollideany(bodyhead, poison_group)
        if attacker != None:
            if pygame.sprite.collide_mask(bodyhead,attacker) and health<=1:
                game_over=True
            if health>1:
                health-=1
                poison_group.remove(attacker)
        attacker = None
        attacker = pygame.sprite.spritecollideany(bodyhead, body_group2)
        if attacker != None:
            if pygame.sprite.collide_mask(bodyhead,attacker) and attacker.number>40:
                game_over=True
        bodyhead.move()
        #更新并移动身体
        for i in range(len(body_group.sprites())-1):
            body_group.sprites()[len(body_group.sprites())-i-1].update()
        body_group.draw(screen)
        food_group.update(1, 50)
    
        if len(food_group) == 0:
            game_over = True
        if bodyhead.isInBorder()==False:
            game_over = True
        #调试
        #pygame.draw.circle(screen, (0, 255, 0), bodyhead.rect.center, 5, width=1)
        #pygame.draw.line(screen, (255, 0, 0), bodyhead.rect.center, (mousepos_x,mousepos_y), width=1)
        #pygame.draw.line(screen, (0, 255, 0), bodyhead.rect.center, (bodyhead.rect.centerx+50*math.cos(bodyhead.angle),bodyhead.rect.centery+50*math.sin(bodyhead.angle)), width=1)
        fcclock.tick(fps)
        #pygame.draw.rect(screen, (255,0,0,220), Rect(bodyhead.rect.centerx-25,bodyhead.rect.centery-30,player_health*0.5,5))
        #pygame.draw.rect(screen, (0,0,0,220), Rect(bodyhead.rect.centerx-25,bodyhead.rect.centery-30,50,5), 2)
        
        if game_over:
            break
        pygame.display.update()
        if startgame==0:
            paused=True
            startgame=1
    async def getglobalmaxscore(websocket):
        global score,globalscore
        await websocket.send(str(score))
        globalscore = await websocket.recv()
    async def refreshglobalmaxscore(websocket):
        global score
        await websocket.send(str(score))
    
    async def main_logic():
        async with websockets.connect('ws://47.101.138.238:26535') as websocket:
            await getglobalmaxscore(websocket)
            await refreshglobalmaxscore(websocket)
    asyncio.get_event_loop().run_until_complete(main_logic())
    if int(score)<=int(globalscore):
        messagebox.showinfo('Game Over','Your score is:'+str(score)+'\nGlobal highest score is:'+str(globalscore))
    else:
        messagebox.showinfo('Game Over','Your score is:'+str(score)+'\nFormer lobal highest score is:'+str(globalscore)+'.Congratulations!')
    pygame.quit()
    window.deiconify()




var1 = tk.StringVar()
def startGame():
    window.withdraw()
    game(maplistbox.get(maplistbox.curselection()))
def showTips():
    messagebox.showinfo('Tips','场地上会随机出现四种道具：红苹果，金苹果，遥控器和炸弹\n获取红苹果后加1分并加长身体\n获取金苹果后增加1生命值和5分\n获取遥控器后会清除所有炸弹\n获取炸弹后会扣除1生命值，直到生命值为0\n贪吃蛇的初始生命值为1，按空格可以开启/解除暂停状态\n使用A/D控制蛇的转向')

b1 = tk.Button(window, text='选择地图', width=15, height=1, command=startGame)
b2 = tk.Button(window, text='查看教程', width=15, height=1, command=showTips)

maplist = tk.StringVar()

maplistbox = tk.Listbox(window, listvariable=maplist)
files=os.listdir('./resources/')
for item in files:
    if os.path.isdir('./resources/'+item):
        maplistbox.insert('end', item)
maplistbox.pack()
b1.pack()
b2.pack()

window.mainloop()