import pygame
from pygame.locals import *
import sys
import random
import math
import time

class Agent:

    # エージェントの位置と速度を__init__で初期化して定義
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y  # 位置
        self.vx, self.vy = vx, vy  # 速度

    # 移動するためのメソッド
    def update(self, WINDOW_W, WINDOW_H):
        self.x += self.vx
        self.y += self.vy

        #画面端に行ったら跳ね返る
        ##画面はしに行ったときに画面を球体と考えたときの座標に移動する
        if self.x > WINDOW_W:  # 右端
            self.vx = -self.vx
            #self.x = WINDOW_W
            #self.x, self.y = 0, self.y + 2 * (WINDOW_H / 2 - self.y)
            #return
        if self.x < 0:  # 左端
            self.vx = -self.vx
            #self.x, self.y = WINDOW_W, self.y + 2 * (WINDOW_H / 2 - self.y)
            #return
        if self.y > WINDOW_H:  # 下
            self.vy  = -self.vy
            self.y = WINDOW_H
            #self.x, self.y = self.x + 2 * (WINDOW_W / 2 - self.x), 0
            #return
        if self.y < 0:  # 上
            self.vy  = -self.vy
            #self.x, self.y = self.x + 2 * (WINDOW_W / 2 - self.x), WINDOW_H
        #if self.y > WINDOW_H + 1:
            #self.y = random.uniform(0, WINDOW_H)
            #self.x = random.uniform(0, WINDOW_W)
            #self.vx = random.uniform(-1.5, 1.5)
            #self.vy = random.uniform(-1.5, 1.5)


    # エージェントを小さな緑丸で画面に表示
    def draw(self, screen):
        x, y = int(self.x), int(self.y)
        pygame.draw.circle(screen, (0, 255, 0), (x, y), 5)

    def draw_red(self, screen):
        x, y = int(self.x), int(self.y)
        pygame.draw.circle(screen, (255, 0, 0), (x, y), 5)

    #分離のルール
    def separation(self, r_s):
        tvx = tvy = c = 0
        #自分以外の全エージェントを処理する
        for a in self.others:
            #近すぎるかどうかの判定
            if a[1] < r_s and a[1] != 0:
                #離れる方向の単位ベクトルを蓄積
                tvx -= (a[0].x - self.x) / a[1]
                tvy -= (a[0].y - self.y) / a[1]
                c += 1

            if c != 0:
                #単位ベクトルの平均を求める
                self.vx_s, self.vy_s = tvx / c, tvy / c
            else:
                self.vx_s, self.vy_s = self.vx, self.vy

    #整列のルール
    def alignment(self, r_a):
        tvx = tvy = c = 0
        for a in self.others:
            #周囲のエージェントかの判定
            if a[1] < r_a:
                tvx += a[0].vx
                tvy += a[0].vy
                c += 1

        if c != 0:
            #速度の平均を求める
            self.vx_a, self.vy_a = tvx / c, tvy / c
        else:
            self.vx_a, self.vy_a = self.vx, self.vy

    #結合のルール
    def cohesion(self, r_c):
        tx = ty = c = 0
        for a in self.others:
            if a[1] < r_c:
                tx += a[0].x
                ty += a[0].y
                c += 1

        if c != 0:
            tx, ty = tx / c, ty / c
            d = math.sqrt((tx - self.x)**2 + (ty - self.y)**2)
            if d != 0:
                #重心を向いた単位ベクトルを求める
                self.vx_c = (tx - self.x) / d
                self.vy_c = (tx - self.y) / d
        else:
            self.vx_c, self.vy_c = self.vx, self.vy


    def rule(self, agent_list, r_s, r_a, r_c):
        #ほかのエージェントとの距離を求める
        self.others = tuple([(a, math.sqrt((a.x - self.x)**2 + (a.y - self.y)**2)) for a in agent_list if a!=self])
        if len(self.others) < 1: return

        #3つのルールを適応
        self.separation(r_s)
        self.alignment(r_a)
        self.cohesion(r_c)

        tvx = self.vx_s * 1 + self.vx_a * 0.4 + self.vx_c * 0.2
        tvy = self.vy_s * 1 + self.vy_a * 0.4 + self.vy_c * 0.2
        n = math.sqrt(tvx**2 + tvy**2)
        #新しい速度を指定
        self.vx, self.vy = 2 * tvx / n, 2 * tvy / n

parameterfile = open("Parameterfile.txt", 'r')
for frequency in range(54):
    #設定
    tick = 30              #1秒間にループする回数（処理を行う回数
    window_wide = 700
    window_high = 700
    agent_amount = 100      #エージェントの数
    sep = int(parameterfile.readline())       #分離のルール（群仲間との距離が遠いときはゆるやかに，近づきすぎると急旋回して避けるようにする）
    alig = int(parameterfile.readline())              #整列のルール（群れ（視界内のエージェント）全体の速度ベクトルの平均に合わせるようにする ）
    coh = int(parameterfile.readline())                #結合のルール（群れの中心に移動しようとする．群れの重心位置へ向かうベクトルを返す）
    prob = int(parameterfile.readline())               #一定範囲内にいた時の感染する確率(%)
    radius = int(parameterfile.readline())             #感染する半径(pixel)

    if prob == 66:
        mask = " マスクなし→マスクなし"
    elif prob == 33:
        mask = " マスクなし→マスクあり"
    elif prob == 16:
        mask = " マスクあり→マスクなし"
    if radius == 8:
        rad = " 会話"
    elif radius == 25:
        rad = " 咳"
    elif radius == 42:
        rad = " くしゃみ"
    file_name = "分裂" + str(sep) + " 整列" + str(alig) + " 結合" + str(coh) + mask + rad

    #メイン
    WINDOW_W, WINDOW_H  = window_wide, window_high
    pygame.init()
    #画面を生成
    screen = pygame.display.set_mode((WINDOW_W,WINDOW_H))
    #時間を管理するオブジェクト
    clock = pygame.time.Clock()
    #fontオブジェクトの生成
    font = pygame.font.Font(None,28)
    agent_list = []
    rule_on = 1 #ルールの適用、非適用を選択するフラグ

    simuration_count = 1
    tick_count = 0
    tick_count_text = 0
    make_text = open(str(file_name) + '.txt', 'w')
    Configuration = "agents : " + str(int(agent_amount)) + "\n" + "wide : " + str(int(window_wide)) + " \n"\
         + "high : " + str(int(window_high)) + " \n" + "separation : " + str(int(sep)) + " \n"\
             + "alignment : " + str(int(alig)) + " \n" + "cohesion : " + str(int(coh)) + " \n" \
                 + "probability : " + str(int(prob)) + "%/sec" + "\n" + "radius : " + str(int(radius)) + "\n" + "-------------" + "\n"
    make_text.write(Configuration)
    make_text.close()

    for num_of_time in range(1):

        random.seed(time.time())
        for a in range(agent_amount):
            # 速度を乱数で設定
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-1.5, 1.5)
            #vx = -1
            #vy = 0
            x = random.uniform(0, window_wide)
            y = random.uniform(0, window_high)
            #x = random.uniform(900, 1000)
            #y = random.uniform(500, 600)
            # エージェントの生成
            a = Agent(x, y, vx, vy)
            agent_list.append(a)
    
    
        agent_list_red = []
        agent_list_all = []
        agent_flag = 1
        agent_list_all.extend(agent_list)
        agent_list_red.append(agent_list.pop(0))
        #agent_flag = 0


        while True:
            clock.tick(tick)  # 進行速度を60fpsにセット
            screen.fill((255, 255, 255))  # 背景は白色


            for a in agent_list:
                #if rule_on == 1:
                    #ルールの適応
                    #a.rule(agent_list, sep, alig, coh)
                a.update(WINDOW_W, WINDOW_H)
                a.draw(screen)

            #ここら辺に、赤色に一定距離近づいたら、近づいたエージェントの色を変えるようにしたい
            #if agent_flag == 1:
                #agent_list_all.extend(agent_list)
            #agent_list_red.append(agent_list.pop(0))
            #agent_flag = 0

            for g in agent_list_red:
                #if rule_on == 1:
                    #ルールの適応
                    #g.rule(agent_list_red, sep, alig, coh)
                g.update(WINDOW_W, WINDOW_H)
                g.draw_red(screen)

            for agent in agent_list_all:
                agent.rule(agent_list_all, sep, alig, coh)

            if len(agent_list) != 0:
                #listが正常かどうかの確認
                #print(len(agent_list))
                for q in agent_list_red:
                    for o in agent_list:
                        if math.sqrt((q.x - o.x) ** 2 + (q.y - o.y) ** 2) <= radius:
                            if random.randint(1,100 * tick) < prob + 1:
                                agent_list_red.append(o)
                                agent_list.remove(o)
            elif len(agent_list) == 0:
                text_data = str(int(simuration_count)) + " : " + str(round(tick_count_text / tick, 1)) + "sec\n"
                text = open(str(file_name)+'.txt', 'a')
                text.write(text_data)
                text.close()
                tick_count_text = 0
                agent_list.clear()
                agent_list_red.clear()
                agent_list_all.clear()
                simuration_count += 1
                break

            s1 = "agents : " + str(len(agent_list_all)) + " / "
            s3 = "wide : " + str(int(window_wide)) + " / "
            s4 = "high : " + str(int(window_high))
            s5 = "separation : " + str(int(sep)) + " / "
            s6 = "alignment : " + str(int(alig)) + " / "
            s7 = "cohesion : " + str(int(coh)) + " / probability : " + str(int(prob)) + "%/sec / " + "radius : " + str(int(radius))
            s8 = "infected : " + str(int(len(agent_list_red))) + " / "
            s9 = "healthy : " + str(int(len(agent_list)))
            s10 = "simuration count : " + str(int(simuration_count)) + " / "
            s11 = "elapsed time : " + str(round(tick_count_text / tick, 1)) + " / "
            s12 = "avarage time : " + str(round(tick_count / tick / simuration_count, 1)) + "sec"
            text = font.render(s1 + " " + s3 + s4, True, (0, 0, 0))
            text_2 = font.render(s5 + s6 + s7, True, (0,0,0))
            text_3 = font.render(s8 + s9, True, (0,0,0))
            text_4 = font.render(s10 + s11 + s12, True, (0,0,0))
            screen.blit(text, (1, 1))
            screen.blit(text_2, (1, 20))
            screen.blit(text_3, (1, 40))
            screen.blit(text_4, (1, 60))

            for e in pygame.event.get():
                if e.type == MOUSEBUTTONDOWN and e.button == 2:
                    rule_on = 1 - rule_on
                if e.type == QUIT:
                    pygame.quit()
                    sys.exit()
            pygame.display.update()
            tick_count += 1
            tick_count_text += 1
        text = open(str(file_name)+'.txt', 'a')
        text.write(s12)
        text.close()