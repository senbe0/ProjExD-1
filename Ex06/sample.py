import pygame as pg
import os
import random
import sys
import time


main_dir = os.path.split(os.path.abspath(__file__))[0]


class Screen:
    def __init__(self, title, wh, img_path):
        pg.display.set_caption(title) 
        self.sfc = pg.display.set_mode(wh)
        self.rct = self.sfc.get_rect()
        self.bgi_sfc = pg.image.load(img_path)
        self.bgi_rct = self.bgi_sfc.get_rect() 

    def blit(self):
        self.sfc.blit(self.bgi_sfc, self.bgi_rct) 


class Bird:
    key_delta = {
        pg.K_UP:    [0, -1],
        pg.K_DOWN:  [0, +1],
        pg.K_LEFT:  [-1, 0],
        pg.K_RIGHT: [+1, 0],
    }

    def __init__(self, img_path, ratio, xy):
        self.sfc = pg.image.load(img_path)
        self.sfc = pg.transform.rotozoom(self.sfc, 0, ratio)
        self.rct = self.sfc.get_rect()
        self.rct.center = xy

    def blit(self, scr:Screen):
        scr.sfc.blit(self.sfc, self.rct)

    def update(self, scr:Screen):
        key_dct = pg.key.get_pressed()
        for key, delta in Bird.key_delta.items():
            if key_dct[key]:
                self.rct.centerx += delta[0]
                self.rct.centery += delta[1]  
            if check_bound(self.rct, scr.rct) != (+1, +1):
                self.rct.centerx -= delta[0]
                self.rct.centery -= delta[1]
        self.blit(scr)                    


class Bomb:
    def __init__(self, color, rad, vxy, scr:Screen):
        self.sfc = pg.Surface((2*rad, 2*rad)) # 正方形の空のSurface
        self.sfc.set_colorkey((0, 0, 0))
        pg.draw.circle(self.sfc, color, (rad, rad), rad)
        self.rct = self.sfc.get_rect()
        self.rct.centerx = random.randint(0, scr.rct.width)
        self.rct.centery = random.randint(0, scr.rct.height)
        self.vx, self.vy = vxy

    def blit(self, scr:Screen):
        scr.sfc.blit(self.sfc, self.rct)

    def update(self, scr:Screen):
        self.rct.move_ip(self.vx, self.vy)
        yoko, tate = check_bound(self.rct, scr.rct)
        self.vx *= yoko
        self.vy *= tate
        self.blit(scr)


#　三瓶栄治：第13回　個人機能追加
class Up_kinoko(object):
    def __init__(self, lives, scr:Screen):
        self.text_font = pg.font.Font("font/Pixeltype.ttf", 50)
        self.lives = lives
        self.kinoko_sfc = pg.image.load("fig/1up.png").convert_alpha()
        self.kinoko_rct = self.kinoko_sfc.get_rect(midbottom=(500, 600))

    #　キノコを表示
    def blit_kinoko(self, scr:Screen):
        scr.sfc.blit(self.kinoko_sfc, self.kinoko_rct)

    #　残機表示する
    def blit_zanki(self, scr:Screen):
        self.text_sfc = self.text_font.render(f"HP =  {self.lives}   !!", False, "Red")
        scr.sfc.blit(self.text_sfc, (1000, 100))

    #　キノコを削除
    def hide_kinoko(self, scr:Screen):
        self.kinoko_rct = self.kinoko_sfc.get_rect(midbottom=(-10, -10))
        scr.sfc.blit(self.kinoko_sfc, self.kinoko_rct)

    # HPを回復する
    def plusLives(self):
        self.lives += 100    

    # HPを減らす
    def minusLives(self):
        self.lives -= 1

#スコアを計測する関数
class Score:
    def __init__(self):
        self.t = 0#時間の変数
        self.sco = 0#スコアの変数
    
    def update(self):
        self.t += 1
        if self.t % 200 == 0:#一定時間ごとにスコアを１追加する
            self.sco += 1
            if self.t >= 5000:#時間が長くなるにつれ、スコアの上がり幅が上がる
                if self.t % 100 == 0:
                    self.sco += 2
        return self.sco

def check_bound(obj_rct, scr_rct):
    """
    第1引数：こうかとんrectまたは爆弾rect
    第2引数：スクリーンrect
    範囲内：+1／範囲外：-1
    """
    yoko, tate = +1, +1
    if obj_rct.left < scr_rct.left or scr_rct.right < obj_rct.right:
        yoko = -1
    if obj_rct.top < scr_rct.top or scr_rct.bottom < obj_rct.bottom:
        tate = -1
    return yoko, tate


def load_sound(file):
    """because pygame can be be compiled without mixer."""
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print("Warning, unable to load, %s" % file)
    return None


#安全地帯関連作成者：C0A21015 市古周馬
class Guard_item: #安全地帯生成アイテム
    def __init__(self,image,ratio,xy):
        self.sfc = pg.image.load(image)
        self.sfc = pg.transform.rotozoom(self.sfc, 0, ratio)
        self.rct = self.sfc.get_rect()
        self.rct.center = xy

    def blit(self, scr:Screen):
        scr.sfc.blit(self.sfc, self.rct)
        
    def update(self, scr:Screen):
        self.blit(scr)   


class Guard: #安全地帯の生成
    def __init__(self, color, rad, x, y, scr:Screen):
        self.sfc = pg.Surface((2*rad, 2*rad)) # 正方形の空のSurface
        self.sfc.set_colorkey((0, 0, 0))
        pg.draw.circle(self.sfc, color, (rad, rad), rad)
        self.rct = self.sfc.get_rect()
        self.rct.centerx = x
        self.rct.centery = y

    def blit(self, scr:Screen):
        scr.sfc.blit(self.sfc, self.rct)

    def update(self, scr:Screen):
        self.blit(scr)

def main():
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    boom_sound = load_sound("boom.wav")
    shoot_sound = load_sound("car_door.wav")
    if pg.mixer:
        music = os.path.join(main_dir, "data", "house_lo.wav")
        pg.mixer.music.load(music)
        pg.mixer.music.play(-1)

    clock =pg.time.Clock()

    # 練習１
    scr = Screen("逃げろ！こうかとん", (1600,900), "fig/pg_bg.jpg")

    #　三瓶栄治：「追加」キノコインスタンス生成
    upkinoko = Up_kinoko(200, scr)

    # 練習３
    kkt = Bird("fig/6.png", 2.0, (900,400))
    kkt.update(scr)

    # 練習５
    bkd_lst = []
    color_lst = ["red", "green", "blue", "yellow", "magenta"]
    for i in range(5):
        bkd = Bomb(color_lst[i%5], 10, (random.choice(range(-2, 3)), random.choice(range(-2, 3))), scr)
        bkd_lst.append(bkd)
    # bkd.update(scr)

    #安全地帯生成アイテムの初期設定
    gd_x = random.randint(300,1500)
    gd_y = random.randint(300,700)
    gd_item = Guard_item("fig/7.png",0.5,(gd_x, gd_y))
    gd_item.update(scr)

    #安全地帯の初期設定
    gd_rad = 100
    gd = Guard("pink", gd_rad, -100, -100, scr) 

    font1 = pg.font.SysFont(None, 50)
    score = Score()

    # 練習２
    while True:        
        scr.blit()

        # 三瓶栄治：「追加」　キノコと残機の表示
        upkinoko.blit_zanki(scr)
        upkinoko.blit_kinoko(scr)

        #ゲーム中のスコアの表示
        ans = score.update()
        text = font1.render(f"{ans}", True, (255,0,0))
        scr.sfc.blit(text, (100, 100))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        gd.update(scr)

        if kkt.rct.colliderect(gd_item.rct): #安全地帯生成アイテム取得時
            gd_rad = 100 #半径を100に再設定
            gd = Guard("pink", gd_rad, gd_x, gd_y, scr) #アイテムの場所に安置を生成
            old_gd_x = gd_x #現在の安全地帯の座標を格納
            old_gd_y = gd_y
            gd_x = random.randint(300,1500) #安全地帯生成アイテムの座標更新
            gd_y = random.randint(300,700)
            gd_item = Guard_item("fig/7.png",0.5,(gd_x,gd_y))
            gd_item.update(scr)
            gd.update(scr)       

        if kkt.rct.colliderect(gd.rct): #安全地帯にいる場合
            for i in range(len(bkd_lst)):
                if gd.rct.colliderect(bkd_lst[i].rct): #安全地帯に爆弾が触れた際
                    gd_rad -= 0.15 #安全地帯の大きさが減少
                    gd = Guard("red", gd_rad, old_gd_x, old_gd_y, scr)
                    gd.update(scr)
                bkd_lst[i].update(scr)    
        else:
            for i in range(len(bkd_lst)):
                if gd.rct.colliderect(bkd_lst[i].rct): #安全地帯に爆弾が触れた際
                    gd =  Guard("pink", 100, -100, -100, scr) #画面から安全地帯が消失
                    gd.update(scr)
                bkd_lst[i].update(scr)
                if kkt.rct.colliderect(bkd_lst[i].rct):
                #ゲーム終了時のスコアの表示

        #kkt.update(scr)
                    for i in range(len(bkd_lst)):
                        bkd_lst[i].update(scr)
                        if kkt.rct.colliderect(bkd_lst[i].rct):

                            #　三瓶栄治：「追加」HPを減らす
                            upkinoko.minusLives()

                            #ゲーム終了時のスコアの表示
                            #　三瓶栄治：HP判定
                            if upkinoko.lives <= 0:                    

                                text_2 = font1.render(f"your score is {ans}", True, (255,0,0))
                                text_2_place = text_2.get_rect(midbottom=(800, 450))
                                scr.sfc.blit(text_2, text_2_place)
                                pg.display.update()
                                time.sleep(5)
                                return

        if gd_rad <=65:  #安全地帯の半径が65以下になったら
            gd =  Guard("pink", 100, -100, -100, scr) #画面から安全地帯の消失
            gd.update(scr) 

        gd_item.update(scr) 
        kkt.update(scr)              

        #　三瓶栄治：HPを回復
        if kkt.rct.colliderect(upkinoko.kinoko_rct):
            upkinoko.plusLives()
            upkinoko.hide_kinoko(scr)


        pg.display.update()
        clock.tick(1000)
    

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()