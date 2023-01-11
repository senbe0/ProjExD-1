import pygame as pg
import os
import random
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
    def __init__(self, color, rad, vxy, scr:Screen,  posx=None, posy=None):
        # 正方形の空のSurface
        self.sfc = pg.Surface((2*rad, 2*rad))
        self.sfc.set_colorkey((0, 0, 0))
        pg.draw.circle(self.sfc, color, (rad, rad), rad)
        self.rct = self.sfc.get_rect()
        # 変更点(壁に当たっているかのための判断)
        self.rct.centerx = random.randint(0, scr.rct.width) if posx is None else posx
        self.rct.centery = random.randint(0, scr.rct.height) if posy is None else posy
        self.vx, self.vy = vxy
        self.countwall = 0

    def blit(self, scr:Screen):
        scr.sfc.blit(self.sfc, self.rct)

    def update(self, scr:Screen):
        self.rct.move_ip(self.vx, self.vy)
        yoko, tate = check_bound(self.rct, scr.rct)
        self.countwall = check_bound_count(self.rct, scr.rct, self.countwall)
        # 無条件で加速する爆弾(追加)
        self.vx *= yoko * 1.0002
        self.vy *= tate * 1.0002
        self.blit(scr)


# キノコを生成する関数 長濱
class BigMushroom:
    def __init__(self, img_path, vxy, xy, ratio):
        self.sfc = pg.image.load(img_path)
        self.sfc = pg.transform.rotozoom(self.sfc, 0, ratio)
        self.rct = self.sfc.get_rect()
        self.rct.center = xy
        self.vx, self.vy = vxy

    def blit(self, scr:Screen):
        scr.sfc.blit(self.sfc, self.rct)

    def update(self, scr:Screen):
        self.rct.move_ip(self.vx, self.vy)
        yoko, tate = check_bound(self.rct, scr.rct)
        self.vx *= yoko
        self.vy *= tate
        self.blit(scr)


# 三瓶栄治(C0A21163)：第13回 個人機能追加
class Up_kinoko(object):
    def __init__(self, lives, scr:Screen):
        self.text_font = pg.font.Font("font/Pixeltype.ttf", 50)
        self.lives = lives
        self.kinoko_sfc = pg.image.load("fig/1up.png").convert_alpha()
        self.kinoko_rct = self.kinoko_sfc.get_rect(midbottom=(500, 600))

    # キノコを表示
    def blit_kinoko(self, scr:Screen):
        scr.sfc.blit(self.kinoko_sfc, self.kinoko_rct)

    # 残機表示する
    def blit_zanki(self, scr:Screen):
        self.text_sfc = self.text_font.render(f"HP =  {self.lives}   !!", False, "Red")
        scr.sfc.blit(self.text_sfc, (1000, 100))

    # キノコを削除
    def hide_kinoko(self, scr:Screen):
        self.kinoko_rct = self.kinoko_sfc.get_rect(midbottom=(-10, -10))
        scr.sfc.blit(self.kinoko_sfc, self.kinoko_rct)

    # HPを回復する
    def plusLives(self):
        self.lives += 100

    # HPが減少する
    def minusLives(self):
        self.lives -= 1


# スコアを計測する関数
class Score:
    def __init__(self):
        # 時間の変数
        self.t = 0
        # スコアの変数
        self.sco = 0

    def update(self):
        self.t += 1
        # 一定時間ごとにスコアを１追加する
        if self.t % 200 == 0:
            self.sco += 1
            # 時間が長くなるにつれ、スコアの上がり幅が上がる
            if self.t >= 5000:
                if self.t % 100 == 0:
                    self.sco += 2
        return self.sco


# 安全地帯関連作成者：C0A21015 市古周馬
# 安全地帯生成アイテム
class Guard_item:
    def __init__(self,image,ratio,xy):
        self.sfc = pg.image.load(image)
        self.sfc = pg.transform.rotozoom(self.sfc, 0, ratio)
        self.rct = self.sfc.get_rect()
        self.rct.center = xy

    def blit(self, scr:Screen):
        scr.sfc.blit(self.sfc, self.rct)

    def update(self, scr:Screen):
        self.blit(scr)


# 安全地帯の生成
class Guard:
    def __init__(self, color, rad, x, y, scr:Screen):
        # 正方形の空のSurface
        self.sfc = pg.Surface((2*rad, 2*rad))
        self.sfc.set_colorkey((0, 0, 0))
        pg.draw.circle(self.sfc, color, (rad, rad), rad)
        self.rct = self.sfc.get_rect()
        self.rct.centerx = x
        self.rct.centery = y

    def blit(self, scr:Screen):
        scr.sfc.blit(self.sfc, self.rct)

    def update(self, scr:Screen):
        self.blit(scr)


# x座標とy座標で反射した時の反射回数のカウント
def check_bound_count(obj_rct, scr_rct, countup: int) -> int:
    if obj_rct.left < scr_rct.left or scr_rct.right < obj_rct.right:
        countup += 1
    if obj_rct.top < scr_rct.top or scr_rct.bottom < obj_rct.bottom:
        countup += 1
    return countup

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

def main():
    pg.init()

    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)

    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    if pg.mixer:
        music = os.path.join(main_dir, "data", "house_lo.wav")
        pg.mixer.music.load(music)
        pg.mixer.music.play(-1)

    clock =pg.time.Clock()

    # 練習１
    scr = Screen("逃げろ！こうかとん", (1600,900), "fig/pg_bg.jpg")

    # 三瓶栄治(C0A21163)：「追加」キノコインスタンス生成
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

    # キノコの生成 長濱
    knk = BigMushroom("fig/bigkinoko.png", (random.choice(range(-2, 3)),
                      random.choice(range(-2, 3))), (100,100), 0.1)
    life = 0

    # 安全地帯生成アイテムの初期設定
    gd_x = random.randint(300,1500)
    gd_y = random.randint(300,700)
    gd_item = Guard_item("fig/7.png",0.5,(gd_x, gd_y))
    gd_item.update(scr)

    # 安全地帯の初期設定
    gd_rad = 100
    gd = Guard("pink", gd_rad, -100, -100, scr)

    font1 = pg.font.SysFont(None, 50)
    score = Score()

    # 練習２
    while True:
        scr.blit()

        # 三瓶栄治(C0A21163)：「追加」　キノコと残機の表示
        upkinoko.blit_zanki(scr)
        upkinoko.blit_kinoko(scr)

        # ゲーム中のスコアの表示
        ans = score.update()
        text = font1.render(f"{ans}", True, (255,0,0))
        scr.sfc.blit(text, (100, 100))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        kkt.update(scr)

        for i in range(len(bkd_lst)):
            bkd_lst[i].update(scr)
            # 壁に爆弾が反射すると分散する
            if bkd_lst[i].countwall == 3:
                bkd_lst[i].countwall = 0
                bkd = Bomb((255, 0, 0), 10, (+1, +1), scr, bkd_lst[i].rct.centerx, bkd_lst[i].rct.centery)
                # 個数に制限をかける
                if len(bkd_lst) <= 3:
                    bkd_lst.append(bkd)

        # 長濱
        if kkt.rct.colliderect(knk.rct):
            # 内部的なライフを増やす
            life += 1
            # 衝突時きのこを画面外に
            knk.rct.centerx = -9999
            knk.rct.centery = -9999
            # 大きさを変更
            kkt = Bird("fig/6.png", 4, kkt.rct.center)
        else:
            knk.update(scr)

        gd.update(scr)

        # 安全地帯生成アイテム取得時
        if kkt.rct.colliderect(gd_item.rct):
            # 半径を100に再設定
            gd_rad = 100
            # アイテムの場所に安置を生成
            gd = Guard("pink", gd_rad, gd_x, gd_y, scr)
            # 現在の安全地帯の座標を格納
            old_gd_x = gd_x
            old_gd_y = gd_y
            # 安全地帯生成アイテムの座標更新
            gd_x = random.randint(300,1500)
            gd_y = random.randint(300,700)
            gd_item = Guard_item("fig/7.png",0.5,(gd_x,gd_y))
            gd_item.update(scr)
            gd.update(scr)

        # 安全地帯にいる場合
        if kkt.rct.colliderect(gd.rct):
            for i in range(len(bkd_lst)):
                # 安全地帯に爆弾が触れた際
                if gd.rct.colliderect(bkd_lst[i].rct):
                    # 安全地帯の大きさが減少
                    gd_rad -= 0.15
                    gd = Guard("red", gd_rad, old_gd_x, old_gd_y, scr)
                    gd.update(scr)
                bkd_lst[i].update(scr)
        else:
            for i in range(len(bkd_lst)):
                # 安全地帯に爆弾が触れた際
                if gd.rct.colliderect(bkd_lst[i].rct):
                    # 画面から安全地帯が消失
                    gd =  Guard("pink", 100, -100, -100, scr)
                    gd.update(scr)
                bkd_lst[i].update(scr)
                if kkt.rct.colliderect(bkd_lst[i].rct):
                    # ライフがある場合 長濱
                    if life == 1:
                        life -= 1
                        # 爆弾を画面外に
                        bkd_lst[i].rct.centerx = -9999
                        bkd_lst[i].rct.centery = -9999
                        # 元の大きさに変更
                        kkt = Bird("fig/6.png", 2, kkt.rct.center)

                    for i in range(len(bkd_lst)):
                        bkd_lst[i].update(scr)
                        if kkt.rct.colliderect(bkd_lst[i].rct):
                            # 三瓶栄治(C0A21163)：「追加」HPを減らす
                            upkinoko.minusLives()
                            # ゲーム終了時のスコアの表示
                            # 三瓶栄治(C0A21163)：HP判定
                            if upkinoko.lives <= 0:
                                text_2 = font1.render(f"your score is {ans}", True, (255,0,0))
                                text_2_place = text_2.get_rect(midbottom=(800, 450))
                                scr.sfc.blit(text_2, text_2_place)
                                pg.display.update()
                                time.sleep(5)
                                return

        # 安全地帯の半径が65以下になったら
        if gd_rad <=65:
            # 画面から安全地帯の消失
            gd =  Guard("pink", 100, -100, -100, scr)
            gd.update(scr)

        gd_item.update(scr)
        kkt.update(scr)

        # 三瓶栄治(C0A21163)：HPを回復
        if kkt.rct.colliderect(upkinoko.kinoko_rct):
            upkinoko.plusLives()
            upkinoko.hide_kinoko(scr)

        pg.display.update()
        clock.tick(1000)


if __name__ == "__main__":
    import sys
    pg.init()
    main()
    pg.quit()
    sys.exit()