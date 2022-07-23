import sys              # sysモジュールを読み込む
import pygame as pg     # pygameモジュールをpgとして読み込む
from random import randint     # randomモジュール内にあるrandint関数を読み込む

bar_num = 5  # 落ちてくる障害物の最大数
rz_num = 10 # 弾数を1000で初期化
HP = 500 # HPを500で初期化

# Screen クラスを定義
class Screen:
    def __init__(self, title, wh, image):   # wh:幅高さタプル, image:背景画像ファイル名
        pg.display.set_caption(title)       # タイトルバーにtitleを表示
        self.sfc = pg.display.set_mode(wh)      # Surface
        self.rct = self.sfc.get_rect()          # Rect
        self.bgi_sfc = pg.image.load(image)     # Surface
        self.bgi_rct = self.bgi_sfc.get_rect()  # Rect  

    def blit(self):
        self.sfc.blit(self.bgi_sfc, self.bgi_rct) 


# Player クラスを定義
class Player:
    def __init__(self, image, size, xy):    # image:画像ファイル名, size:拡大率, xy:初期座標タプル
        self.sfc = pg.image.load(image)                        # Surface
        self.sfc = pg.transform.rotozoom(self.sfc, 0, size)    # Surface
        self.rct = self.sfc.get_rect()                         # Rect
        self.rct.center = xy    # こうかとんを表示する座標をxyに設定
    
    def blit(self, scr: Screen):
        scr.sfc.blit(self.sfc, self.rct)
    
    def update(self, scr: Screen):
        key_states = pg.key.get_pressed() # 辞書
        if key_states[pg.K_LEFT]:
            self.rct.centerx -= 1.0
        if key_states[pg.K_RIGHT]:
            self.rct.centerx += 1.0
        if check_bound(self.rct, scr.rct) != (1, 1): # 領域外だったら
            if key_states[pg.K_LEFT]:
                self.rct.centerx += 1.0
            if key_states[pg.K_RIGHT]:
                self.rct.centerx -= 1.0
        self.blit(scr)


# 上から下にバーが落ちてくるオブジェクトを生成するクラス
class Bar:
    def __init__(self, size, color, scr: Screen):
        self.sfc = pg.Surface(size)
        pg.Surface.fill(self.sfc, color)
        self.rct = self.sfc.get_rect()
        self.rct.centerx = randint(0, scr.rct.width-self.rct.width)
        self.rct.centery = -randint(0, 500)
        self.w, self.h = size
        self.rct.width = randint(80, self.w)
        self.vy  = 1
    
    def blit(self, scr: Screen):
        scr.sfc.blit(self.sfc, self.rct)
        
    def update(self, scr: Screen):
        self.rct.move_ip(0, self.vy)
        if self.rct.centery > scr.rct.height:
            self.rct.centerx = randint(0, scr.rct.width-self.rct.width)
            self.rct.centery = -randint(0, 500)
            self.rct.width = randint(80, self.w)
        scr.sfc.blit(self.sfc, self.rct)

# メダルを生成するクラス 安野裕貴
class Medal:
    def __init__(self, scr):
        self.sfc = pg.Surface((100, 100))
        self.sfc.set_colorkey((0, 0, 0))
        pg.draw.circle(self.sfc, (255, 255, 0), (50, 50), 50)
        self.rct = self.sfc.get_rect()
        self.rct.centerx = randint(0, scr.rct.width)
        self.rct.centery = randint(0, scr.rct.height)

    def blit(self, scr):
        scr.sfc.blit(self.sfc, self.rct)

    def update(self, scr, player):
        self.rct.move_ip(0, 1)
        if self.rct.centery > scr.rct.height:
            self.rct.centerx = randint(0, scr.rct.width-self.rct.width)
            self.rct.centery = -randint(0, 500)
        result = self.check_hit(player, scr)
        self.blit(scr)
        return result

    # メダルがプレイやーかレーザーにぶつかったときにスコアを増やすように命令する
    def check_hit(self, player, scr):
        if self.rct.colliderect(player.rct):
            # if self.rct.colliderect(player.rct) or self.rct.colliderect("razerオブジェクト"):
            self.rct.centerx = randint(0, scr.rct.width-self.rct.width)
            self.rct.centery = -randint(0, 500)
            return 1
        return 0


# Itemクラスを定義 岡田
class Item:
    def __init__(self, r, color, scr: Screen):
        self.sfc = pg.Surface((r*2, r*2))
        self.sfc.set_colorkey((0, 0, 0))
        pg.draw.circle(self.sfc, color, (r, r), r)
        self.rct = self.sfc.get_rect()
        self.rct.centerx = randint(0, scr.rct.width-self.rct.width)
        self.rct.centery = 0
    
    def blit(self, scr: Screen):
        scr.sfc.blit(self.sfc, self.rct)
        
    def update(self, scr: Screen):
        self.rct.move_ip(0, 1) # 速度1で落下
        scr.sfc.blit(self.sfc, self.rct)


def check_bound(rct, scr_rct):
    
    # [1] rct: こうかとん or 爆弾のRect
    # [2] scr_rct: スクリーンのRect

    yoko, tate = 1, 1 # 領域内
    if rct.left < scr_rct.left or scr_rct.right  < rct.right:
        yoko = -1 # 領域外
    if rct.top  < scr_rct.top  or scr_rct.bottom < rct.bottom:
        tate = -1 # 領域外
    return yoko, tate


def main():
    # 山本琢未
    sound() #sound関数の反映
    
    # 岡田
    global rz_num, HP
    inv_point = 0 # 無敵ゲージを0で初期化
    inv = False # 無敵かどうかの判定
    st = 0 # 無敵の開始時刻を保存する関数
    # 岡田/

    clock = pg.time.Clock()  # 時間計測用のオブジェクト
    screen = Screen("", (700, 900), "fig/pg_bg.jpg") # スクリーンを生成する
    screen.blit()

    player = Player("fig/5.png", 1.5, (350, 848))

    bars = [0 for i in range(bar_num)]
    for i in range(bar_num):
        bars[i] = Bar((120, 30), (0,0,0), screen)
        bars[i].blit(screen)

    # メダルをクラスから生成する 安野裕貴
    medal = Medal(screen)
    medal.blit(screen)

    rz_plus = Item(10, (255, 0, 0), screen)
    rz_plus.rct.centerx = -30 # 弾数追加アイテムを画面外で初期化

    heal = Item(10, (0, 128, 0), screen)
    heal.rct.centerx = -30

    # 常にゲームを動かす
    while True:
        screen.blit()

        # 岡田
        time = pg.time.get_ticks()

        # 無敵ゲージの表示
        font = pg.font.Font(None, 40)
        txt = font.render("x"*inv_point, True, (0, 0, 0))
        screen.sfc.blit(txt, (0, 150))
        # 岡田/
        
        # プレイヤーを更新する
        player.update(screen)

        # バーを表示する
        for bar in bars:
            bar.update(screen)
        
            if player.rct.colliderect(bar.rct):
                return
        
        # 岡田
        if 0 <= time % 25000 <= 20: # 25秒おき
            rz_plus = Item(10, (255, 0, 0), screen) # 画面内に弾数追加アイテムを生成
            for bar in bars: # 障害物と被らないように
                while rz_plus.rct.colliderect(bar.rct):
                    rz_plus = Item(10, (255, 0, 0), screen)
        rz_plus.update(screen)

        if player.rct.colliderect(rz_plus.rct): # 弾数追加の処理
            rz_num += 3
            rz_plus.rct.centerx = -30
        
        if 0 <= time %40000 <= 20: # 40秒おき
            heal = Item(10, (0, 128, 0), screen) # 画面内に体力回復アイテムを生成
            for bar in bars: # 障害物と被らないように
                while heal.rct.colliderect(bar.rct):
                    heal = Item(10, (0, 128, 0), screen)
        heal.update(screen)

        if player.rct.colliderect(heal.rct): # 体力回復の処理
            HP += 100
            heal.rct.centerx = -30
        # 岡田/

        # メダルを更新する
        result = medal.update(screen, player)
        # 画面のばつボタンをクリックしたときに終了する
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        # 岡田
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LSHIFT and inv_point == 10:
                    inv_point = 0
                    inv = True
                    st = time # 無敵の開始時刻を保存
        if time - st > 5000: # 無敵は5秒継続
            inv = False
        # 岡田
        
        pg.display.update()   # 画面を更新する
        clock.tick(1000)

# 山本琢未
def sound():
    pg.mixer.init(frequency = 44100)    # 初期設定
    pg.mixer.music.load("fig/test.mp3")     # 音楽ファイルの読み込み
    pg.mixer.music.play(1)              # 音楽の再生回数(1回)
    #bgmの作製(山本琢未)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
