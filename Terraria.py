import pygame
from pygame import mixer

import math
import datetime


screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Terraria")


# ----------------------------オブジェクトの定義------------------------------


class Timer():
    def __init__(self):
        self.first_time = datetime.datetime.today().timestamp()
        self.second_time = datetime.datetime.today().timestamp()
        self.time_interval = self.second_time - self.first_time
    
    def start(self):
        self.first_time = datetime.datetime.today().timestamp()
        self.second_time = datetime.datetime.today().timestamp()
    
    def measure(self, standard_time):
        self.second_time = datetime.datetime.today().timestamp()
        self.time_interval = self.second_time - self.first_time

        if self.time_interval >= standard_time:
            return True
        else:
            return False
    
    def tell_time(self):
        self.second_time = datetime.datetime.today().timestamp()
        self.time_interval = self.second_time - self.first_time
        return self.time_interval


# キーオブジェクト
class Key():
    def __init__(self, **dictionary):
        self.key_list = dictionary # キーのリストと状態を格納する辞書オブジェクト
    
    # typeがkeydownまたはkeyupのイベントを取得できるジェネレーター
    @classmethod
    def get_key_event(cls):
        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                yield event
            elif event.type == pygame.KEYUP:
                yield event


class Map():
    def __init__(self, initial_left_map_x, initial_top_map_y):
        self.map = "" # マップ全体のデータ
        self.map_line_list = [] # 一行分のマップ(map_line)を束ねたリスト

        # マップ座標系とは
        # マップの左上を(0, 0), ブロックの長さを30とした座標系
        # 右に進むほど、xは正の方向に大きくなる
        # 下に進むほど、yは正の方向に大きくなる

        self.current_left_map_x = initial_left_map_x # 現時点での画面の左側のx座標(マップ座標系)
        self.current_right_map_x = self.current_left_map_x + 1000 # 現時点での画面の右側のx座標(マップ座標系)
        self.current_top_map_y = initial_top_map_y # 現時点での画面の上側のy座標(マップ座標系)
        self.current_bottom_map_y = self.current_top_map_y + 600 # 現時点での画面の下側のy座標(マップ座標系)

        self.end_x = 6000 # マップの右端のx座標(マップ座標系)
        self.end_y = 1950 # マップの下端のy座標(マップ座標系)

        # ブロック座標系とは
        # マップの左上のブロックを(0, 0)とした座標系
        # 一ブロック分右に進むごとに、xは1大きくなる
        # 一ブロック分下に進むごとに、yは1大きくなる

        self.current_left_block_x = math.ceil(self.current_left_map_x / 30) - 1 # 現時点での画面の左側のx座標(ブロック座標系)
        self.current_right_block_x = math.ceil(self.current_right_map_x / 30) - 1 # 現時点での画面の右側のx座標(ブロック座標系)
        self.current_top_block_y = math.ceil(self.current_top_map_y / 30) - 1 # 現時点での画面の上側のy座標(ブロック座標系)
        self.current_bottom_block_y = math.ceil(self.current_bottom_map_y / 30) - 1 # 現時点での画面の下側のy座標(ブロック座標系)

        self.end_block_x = (self.end_x / 30) - 1 # マップの右端のx座標(ブロック座標系)
        self.end_block_y = (self.end_y / 30) - 1 # マップの下端のy座標(ブロック座標系)

        self.drawing_x = -(self.current_left_map_x % 30) # これから描画するブロックの左上の点のx座標(画面座標系)
        self.drawing_y = -(self.current_top_map_y % 30) # これから描画するブロックの左上の点のy座標(画面座標系)

        self.drawing_map_x = self.current_left_block_x # これから描画するブロックの左上の点のx座標(マップ座標系)
        self.drawing_map_y = self.current_top_block_y # これから描画するブロックの左上の点のy座標(マップ座標系)
    
    # drawing_x, drawing_yの値を描画前の値に戻す
    def reset_drawing(self):
        self.drawing_x = -(self.current_left_map_x % 30)
        self.drawing_y = -(self.current_top_map_y % 30)
    
    # block_numberに代入されたブロック番号に対応したブロックを生成する
    # drawing_xに30を加算する
    # drawing_map_xがend_xよりも大きければ、drawing_map_xをcurrent_left_xに戻し、drawing_map_yに30を加算する
    # drawing_xが1000よりも大きければ、drawing_x, drawing_map_xを元に戻し、drawing_y, drawing_map_yに30を加算する。
    # drawing_map_yがend_yよりも大きければ、Trueを返す
    def draw_block(self, block_number):

        # 空気ブロック
        if block_number == "0":
            self.drawing_x += 30
            self.drawing_map_x += 30
        
        # 土ブロック
        elif block_number == "1":
            soil_block = SoilBlock(self.drawing_x, self.drawing_y)
            soil_block.display()
            
            self.drawing_x += 30
            self.drawing_map_x += 30
        
        # 草ブロック
        elif block_number == "2":
            grass_block = GrassBlock(self.drawing_x, self.drawing_y)
            grass_block.display()

            self.drawing_x += 30
            self.drawing_map_x += 30
        
        if self.drawing_x >= 1000 or self.drawing_map_x >= self.end_x:
            self.drawing_x = -(self.current_left_map_x % 30)
            self.drawing_map_x = self.current_left_block_x
            self.drawing_y += 30
            self.drawing_map_y += 30
        
        if self.drawing_map_y >= self.end_y:
            return True
    
    def is_collision_left(self, block_number):

        # 空気ブロック
        if block_number == "0":
            return None

        # 土ブロック
        elif block_number == "1":
            soil_block = SoilBlock(self.drawing_x, self.drawing_y)
            return soil_block.is_collision_left()
        
        # 草ブロック
        elif block_number == "2":
            grass_block = GrassBlock(self.drawing_x, self.drawing_y)
            return grass_block.is_collision_left()
        
    def is_collision_right(self, block_number):

        # 空気ブロック
        if block_number == "0":
            return None

        # 土ブロック
        elif block_number == "1":
            soil_block = SoilBlock(self.drawing_x, self.drawing_y)
            return soil_block.is_collision_right()
        
        # 草ブロック
        elif block_number == "2":
            grass_block = GrassBlock(self.drawing_x, self.drawing_y)
            return grass_block.is_collision_right()
        
    def is_collision_top(self, block_number):

        # 空気ブロック
        if block_number == "0":
            return None
        
        # 土ブロック
        elif block_number == "1":
            soil_block = SoilBlock(self.drawing_x, self.drawing_y)
            return soil_block.is_collision_top()
        
        # 草ブロック
        elif block_number == "2":
            grass_block = GrassBlock(self.drawing_x, self.drawing_y)
            return grass_block.is_collision_top()

    def is_collision_bottom(self, block_number):

        # 空気ブロック
        if block_number == "0":
            return None
        
        # 土ブロック
        elif block_number == "1":
            soil_block = SoilBlock(self.drawing_x, self.drawing_y)
            return soil_block.is_collision_bottom()
        
        # 草ブロック
        elif block_number == "2":
            grass_block = GrassBlock(self.drawing_x, self.drawing_y)
            return grass_block.is_collision_bottom()

    
    def move_left(self):
        self.current_left_map_x += -8.0
        self.current_right_map_x += -8.0

        self.current_left_block_x = math.ceil(self.current_left_map_x / 30) - 1 
        self.current_right_block_x = math.ceil(self.current_right_map_x / 30) - 1 
        
        self.drawing_x = -(self.current_left_map_x % 30) # これから描画するブロックの左上の点のx座標
        self.drawing_y = -(self.current_top_map_y % 30) # これから描画するブロックの左上の点のy座標

        self.drawing_map_x = self.current_left_block_x # これから描画するブロックの左上の点のx座標(マップ座標系)
        self.drawing_map_y = self.current_top_block_y # これから描画するブロックの左上の点のy座標(マップ座標系)

    def move_right(self):
        self.current_left_map_x += 8.0
        self.current_right_map_x += 8.0

        self.current_left_block_x = math.ceil(self.current_left_map_x / 30) - 1 
        self.current_right_block_x = math.ceil(self.current_right_map_x / 30) - 1 

        self.drawing_x = -(self.current_left_map_x % 30) # これから描画するブロックの左上の点のx座標
        self.drawing_y = -(self.current_top_map_y % 30) # これから描画するブロックの左上の点のy座標

        self.drawing_map_x = self.current_left_block_x # これから描画するブロックの左上の点のx座標(マップ座標系)
        self.drawing_map_y = self.current_top_block_y # これから描画するブロックの左上の点のy座標(マップ座標系)

    def move_top(self):
        self.current_top_map_y += -8.0
        self.current_bottom_map_y += -8.0

        self.current_top_block_y = math.ceil(self.current_top_map_y / 30) - 1 # 現時点での画面の上側のy座標(ブロック座標系)
        self.current_bottom_block_y = math.ceil(self.current_bottom_map_y / 30) - 1 # 現時点での画面の下側のy座標(ブロック座標系)

        self.drawing_x = -(self.current_left_map_x % 30) # これから描画するブロックの左上の点のx座標
        self.drawing_y = -(self.current_top_map_y % 30) # これから描画するブロックの左上の点のy座標

        self.drawing_map_x = self.current_left_block_x # これから描画するブロックの左上の点のx座標(マップ座標系)
        self.drawing_map_y = self.current_top_block_y # これから描画するブロックの左上の点のy座標(マップ座標系)

    def move_down(self):
        self.current_top_map_y += 8.0
        self.current_bottom_map_y += 8.0

        self.current_top_block_y = math.ceil(self.current_top_map_y / 30) - 1 # 現時点での画面の上側のy座標(ブロック座標系)
        self.current_bottom_block_y = math.ceil(self.current_bottom_map_y / 30) - 1 # 現時点での画面の下側のy座標(ブロック座標系)

        self.drawing_x = -(self.current_left_map_x % 30) # これから描画するブロックの左上の点のx座標
        self.drawing_y = -(self.current_top_map_y % 30) # これから描画するブロックの左上の点のy座標

        self.drawing_map_x = self.current_left_block_x # これから描画するブロックの左上の点のx座標(マップ座標系)
        self.drawing_map_y = self.current_top_block_y # これから描画するブロックの左上の点のy座標(マップ座標系)


# メインキャラクターの縦幅は32
class MainCharacter():

    X = 490
    Y = 260 

    def __init__(self, map_x, map_y):
        self.img = pygame.image.load("Image/Character/MainCharacter/MainCharacter_Right1.png")
        self.x = MainCharacter.X # メインキャラクターのx座標(画面座標系)
        self.y = MainCharacter.Y # メインキャラクターのy座標(画面座標系)
        self.map_x = map_x # メインキャラクターのx座標(マップ座標系)
        self.map_y = map_y # メインキャラクターのy座標(マップ座標系)
        self.block_x = math.ceil(self.map_x / 30) - 1 # メインキャラクターのx座標(ブロック座標系)
        self.block_y = math.ceil(self.map_y / 30) - 1 # メインキャラクターのy座標(ブロック座標系)
        self.is_moving_down = "move_down"# 下へ下降しているかどうかを示す。
                                    # メインキャラクターが真下の地面と衝突している場合、またはジャンプ中は下降を行わない
                                    # それ以外の場合は下降を行う
        self.jumping = "not_jumping" # ジャンプ中かどうかを示す
        self.jumping_timer = Timer() # ジャンプ時間をカウントする

        self.can_move_left = "can_move_left" # 左へ移動可能かどうかを示す
        self.can_move_right = "can_move_right" # 右へ移動可能かどうかを示す
        self.can_move_top = "can_move_top" # 上へ移動可能かどうかを示す

        self.key = Key(key_left="not_pushed", key_right="not_pushed", key_z="not_pushed") # メインキャラクターのキー情報を格納

        self.items = Items() # メインキャラクターが持っているアイテム
        
    
    def display(self):
        screen.blit(self.img, (self.x, self.y))
    
    # can_move_leftの値がcan_move_left, key_leftの値がpushed, key_zの値がnot_pushedであれば、左へ移動する
    def move_left(self, map):
        if self.can_move_left == "can_move_left" and self.key.key_list["key_left"] == "pushed" and self.key.key_list["key_z"] == "not_pushed":
            map.move_left()
            self.map_x += -8.0
            self.block_x = math.ceil(self.map_x / 30) - 1 
    
    # can_move_rightの値がcan_move_right, key_rightの値がpushed, key_zの値がnot_pushedであれば、右へ移動する
    def move_right(self, map):
        if self.can_move_right == "can_move_right" and self.key.key_list["key_right"] == "pushed" and self.key.key_list["key_z"] == "not_pushed":
            map.move_right()
            self.map_x += 8.0
            self.block_x = math.ceil(self.map_x / 30) - 1 

    def move_top(self, map):
        if self.can_move_top == "can_move_top":
            map.move_top()
            self.map_y += -8.0
            self.block_y = math.ceil(self.map_y / 30) - 1 

    
    # move_downの値がmove_downであれば、下降する
    def move_down(self, map):
        if self.is_moving_down == "move_down":
            map.move_down()
            self.map_y += 8.0
            self.block_y = math.ceil(self.map_y / 30) - 1 
    
    # jumpingの値がjumpingであれば、上昇(ジャンプ)する
    # ジャンプを開始してから2秒が経過したら、jumpingの値はjumpingからnot_jumpingに変わる
    def jump(self):
        if self.jumping == "jumping":
            if self.jumping_timer.measure(0.5):
                self.jumping = "not_jumping"
                self.is_moving_down = "move_down"
            else:
                self.move_top(map)
    
    # キーリストを変更する
    def change_key_list(self, event):

        if event.type == pygame.KEYDOWN:
            # 左矢印キーが押されたら、key_leftの値を更新する。
            if event.key == pygame.K_LEFT:
                self.key.key_list["key_left"] = "pushed"

            # 右矢印キーが押されたら、key_rightの値を更新する。
            elif event.key == pygame.K_RIGHT:
                self.key.key_list["key_right"] = "pushed"
            
            # スペースキーが押されたら、jumpingをjumpingに、is_moving_downをnot_move_downに変更する。
            if event.key == pygame.K_SPACE:
                if self.jumping == "not_jumping":
                    self.jumping = "jumping"
                    self.is_moving_down = "not_move_down"
                    self.jumping_timer = Timer()
            
            # zキーが押されたら、key_zの値を更新する。
            if event.key == pygame.K_z:
                self.key.key_list["key_z"] = "pushed"

        if event.type == pygame.KEYUP:

            # 指がキーから離れたら、key_leftの値を更新
            if event.key == pygame.K_LEFT:
                self.key.key_list["key_left"] = "not_pushed"
            
            # 指がキーから離れたら、key_rightの値を更新
            elif event.key == pygame.K_RIGHT:
                self.key.key_list["key_right"] = "not_pushed"
            
            # 指がキーから離れたら、key_zの値を更新
            if event.key == pygame.K_z:
                self.key.key_list["key_z"] = "not_pushed"


# --------ブロックのオブジェクト--------


class GrassBlock():

    def __init__(self, x, y):
        self.img = pygame.image.load("Image/Block/GrassBlock/GrassBlock.png")
        self.img = pygame.transform.scale(self.img, (30, 30))
        self.x = x
        self.y = y
    
    def display(self):
        screen.blit(self.img, (self.x, self.y))
    
    # 左側のブロックがメインキャラクターと衝突しているかどうかを判定
    def is_collision_left(self):
        x_distance = abs(self.x - MainCharacter.X)

        if x_distance <= STANDARD_DISTANCE_LEFT:
            return True
        else:
            return False
    
    # 右側のブロックがメインキャラクターと衝突しているかどうかを判定
    def is_collision_right(self):
        x_distance = abs(self.x - MainCharacter.X)

        if x_distance <= STANDARD_DISTANCE_RIGHT:
            return True
        else:
            return False
    
    # 上側のブロックがメインキャラクターと衝突しているかどうかを判定
    def is_collision_top(self):
        y_distance = abs(self.y - MainCharacter.Y)

        if y_distance <= STANDARD_DISTANCE_TOP:
            return True
        else:
            return False
    # 下側のブロックがメインキャラクターと衝突しているかどうかを判定
    def is_collision_bottom(self):
        y_distance = abs(self.y - MainCharacter.Y)

        if y_distance <= STANDARD_DISTANCE_BOTTOM:
            return True
        else:
            return False


class SoilBlock():
    def __init__(self, x, y):
        self.img = pygame.image.load("Image/Block/SoilBlock/SoilBlock.png")
        self.img = pygame.transform.scale(self.img, (30, 30))
        self.x = x
        self.y = y
    
    def display(self):
        screen.blit(self.img, (self.x, self.y))

    # 左側のブロックがメインキャラクターと衝突しているかどうかを判定
    def is_collision_left(self):
        x_distance = abs(self.x - MainCharacter.X)

        if x_distance <= STANDARD_DISTANCE_LEFT:
            return True
        else:
            return False
    
    # 右側のブロックがメインキャラクターと衝突しているかどうかを判定
    def is_collision_right(self):
        x_distance = abs(self.x - MainCharacter.X)

        if x_distance <= STANDARD_DISTANCE_RIGHT:
            return True
        else:
            return False
    
    # 上側のブロックがメインキャラクターと衝突しているかどうかを判定
    def is_collision_top(self):
        y_distance = abs(self.y - MainCharacter.Y)

        if y_distance <= STANDARD_DISTANCE_TOP:
            return True
        else:
            return False
    # 下側のブロックがメインキャラクターと衝突しているかどうかを判定
    def is_collision_bottom(self):
        y_distance = abs(self.y - MainCharacter.Y)

        if y_distance <= STANDARD_DISTANCE_BOTTOM:
            return True
        else:
            return False


# --------アイテムのオブジェクト--------


# メインキャラクターが持っているアイテムの集合
class Items():

    def __init__(self):
        self.items = [Pickaxe(), Pickaxe()] # メインキャラクターが持っているアイテム
        self.selected_item_number = 0 # 選択されたアイテムの、リスト内での番号
        self.key = Key(key_z="not_pushed")
        self.changing_selected_item_timer = Timer() # 選択されたアイテムを変更するときに使うタイマー

        self.limited_items = [] # メインキャラクターが持っているアイテムを先頭10個分までまとめたリスト

        # limited_itemsに先頭10個分のアイテムを入れる
        for i, item in enumerate(self.items):

            if i <= 9:
                self.limited_items.append(item)

        self.item_area_list = ItemAreaList(self.selected_item_number, self.limited_items) # 画面右上に表示されている、アイテムエリアのリスト
    
    # キーリストを変更する
    def change_key_list(self, event):
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                self.key.key_list["key_z"] = "pushed"
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_z:
                self.key.key_list["key_z"] = "not_pushed"
    
    # 選択されたアイテムのリスト内での番号を変える。
    def change_selected_item_number(self, event):
        
        # 選択されたアイテムの番号の変更から0.1秒以上が経過していて、zキーが押されている状態で、
        # かつ左矢印キーが押されれば、選択されたアイテムの番号を1だけ減らす。
        # ただし、現在の選択されたアイテムの番号が0であれば、何も処理は行わない。
        if self.key.key_list["key_z"] == "pushed" and event.key == pygame.K_LEFT and self.changing_selected_item_timer.measure(0.1):

            if self.selected_item_number > 0:
                self.selected_item_number -= 1

                # 選択されたアイテムエリアを変更する
                self.change_selected_item_area()

                self.changing_selected_item_timer.start() # タイマーをスタート

            else:
                pass
        
        # 選択されたアイテムの番号の変更から0.1秒以上が経過していて、zキーが押されている状態で、
        # かつ右矢印キーが押されれば、選択されたアイテムの番号を1だけ増やす。
        # ただし、現在の選択されたアイテムの番号がlimited_itemsの数-1であれば、何も処理は行わない。
        elif self.key.key_list["key_z"] == "pushed" and event.key == pygame.K_RIGHT and self.changing_selected_item_timer.measure(0.1):

            if self.selected_item_number < len(self.limited_items)-1:
                self.selected_item_number += 1

                # 選択されたアイテムエリアを変更する
                self.change_selected_item_area()

                self.changing_selected_item_timer.start() # タイマーをスタート

            else:
                pass

    def display_item_area_list(self):
        self.item_area_list.display()
    
    # 選択されたアイテムエリアを変更
    def change_selected_item_area(self):

        self.limited_items = []
        
        # limited_itemsに先頭10個分のアイテムを入れる
        for i, item in enumerate(self.items):

            if i <= 9:
                self.limited_items.append(item)
        
        self.item_area_list.change_selected_item_area(self.selected_item_number, self.limited_items)


# アイテムエリア
class ItemArea():

    Y = 15 # ItemAreaのy座標(画面座標系)

    def __init__(self, x):
        self.img = pygame.image.load("Image/Item/ItemArea.png")
        self.img = pygame.transform.scale(self.img, (30, 30))
        self.x = x
        self.y = ItemArea.Y

    def display(self):
        screen.blit(self.img, (self.x, self.y))


# 選択されたアイテムエリア
class SelectedItemArea():

    Y = 15 # SelectedItemAreaのy座標(画面座標系)

    def __init__(self, x):
        self.img = pygame.image.load("Image/Item/SelectedItemArea.png")
        self.img = pygame.transform.scale(self.img, (30, 30))
        self.x = x
        self.y = SelectedItemArea.Y
    
    def display(self):
        screen.blit(self.img, (self.x, self.y))


# 画面右上に表示されている、アイテムエリアのリスト
class ItemAreaList():
    def __init__(self, selected_item_number, limited_items):
        self.item_area_list = []
        self.first_item_area_x = 640 # 一番左側のItemAreaのx座標(画面座標系)
        self.item_area_interval = 30 # ItemAreaの幅は30なので、ItemAreaどうしの間隔も30
        self.selected_item_area_number = selected_item_number # 選択されたアイテムエリアのアイテムエリア番号。0〜9のどれか。
        self.limited_items = limited_items
        self.first_item_x = 640 # 一番左側のアイテムのx座標(画面座標系)
        self.item_y = 15 # アイテムのy座標(画面座標系)
        self.item_interval = 30 # アイテムどうしの間隔

        for i in range(0, 10):
            if i == self.selected_item_area_number:
                self.item_area_list.append(SelectedItemArea(self.first_item_area_x + self.item_area_interval*i))
            else:
                self.item_area_list.append(ItemArea(self.first_item_area_x + self.item_area_interval*i))
    
    # itemsは、メインキャラクターが持っているアイテムを先頭10個分までまとめたリスト
    def display(self):
        for item_area in self.item_area_list:
            item_area.display()
        
        for i, item in enumerate(self.limited_items):
            item.display(self.first_item_x+i*self.item_interval, self.item_y)
    
    # 選択されたアイテムエリアを変更する
    def change_selected_item_area(self, selected_item_number, limited_items):

        self.selected_item_area_number = selected_item_number
        self.limited_items = limited_items

        # item_area_listを更新する
        for i in range(0, 10):
            if i == self.selected_item_area_number:
                self.item_area_list.append(SelectedItemArea(self.first_item_area_x + self.item_area_interval*i))
            else:
                self.item_area_list.append(ItemArea(self.first_item_area_x + self.item_area_interval*i))


# ピックアックスオブジェクト
class Pickaxe():

    def __init__(self):
        self.img = pygame.image.load("Image/Item/Pickaxe.png")
        self.img = pygame.transform.scale(self.img, (30, 30))
        self.x = None
        self.y = None

    def display(self, x, y):
        self.x = x
        self.y = y
        screen.blit(self.img, (self.x, self.y))

        

# -------------------------------主要な変数----------------------------------

game_scene = "playing_scene"
STANDARD_DISTANCE_LEFT = 25 # 左側のブロックと衝突した時の、左側のブロックとメインキャラクターとの距離
STANDARD_DISTANCE_RIGHT = 25 # 右側のブロックと衝突した時の、右側のブロックとメインキャラクターとの距離
STANDARD_DISTANCE_TOP = 50 # 上側のブロックと衝突した時の、上側のブロックとメインキャラクターとの距離
STANDARD_DISTANCE_BOTTOM = 32 # 下側のブロックと衝突した時の、下側のブロックとメインキャラクターとの距離



# -------------------------------処理の実装----------------------------------

running = True
while running:

    # ゲームプレイシーン
    if game_scene == "playing_scene":
        main_character = MainCharacter(825, 850) # yは元は850
        map = Map(320, 600)

        key = Key()

        # Map.txtからマップを読み込む
        with open("Map.txt", mode="r") as map_file:
            map.map = map_file.read()

            for map_line in map.map.split("\n"):
                map.map_line_list.append(map_line)
        
        
        playing_scene = True
        while playing_scene:

            # --------メインキャラクターの処理--------

            # メインキャラクターを表示
            main_character.display()

            # can_move_leftの値がcan_move_leftかつkey_leftの値がpushedであれば、左へ移動する
            main_character.move_left(map)

            # can_move_rightの値がcan_move_rightかつkey_rightの値がpushedであれば、左へ移動する
            main_character.move_right(map)
            
            # ジャンプ状態がjumpingであれば、上へ移動する
            main_character.jump()
            
            # move_downに入っている値がmove_downであれば、下へ移動する
            main_character.move_down(map)


            # --------ブロックの処理--------

            # ブロック生成処理 and メインキャラクターとブロックとの衝突判定

            map.reset_drawing()

            for block_y, map_line in enumerate(map.map_line_list):

                # map_lineのブロック座標が画面下側のブロック座標以下かつ画面上側のブロック座標以上ならば、
                if block_y <= map.current_bottom_block_y and block_y >= map.current_top_block_y:

                    for block_x, block in enumerate(map_line):

                        # x座標(ブロック座標系)が画面左側のブロック座標以上かつ画面右側のブロック座標以下ならば、
                        if block_x >= map.current_left_block_x and block_x <= map.current_right_block_x:

                            # 生成するブロックがメインキャラクターが含まれているブロック、あるいはそれに隣接したブロックならば
                            if main_character.block_x-1 <= block_x <= main_character.block_x+1 and main_character.block_y-1 <= block_y <= main_character.block_y+2:

                                # 生成するブロックがメインキャラクターの左側のブロックならば
                                if (block_y == main_character.block_y or block_y == main_character.block_y+1) and block_x == main_character.block_x-1:
                                    is_collision_left = map.is_collision_left(block) # 左側のブロックとメインキャラクターが衝突しているかどうかを判定

                                    # 左のブロックと衝突していれば、左へ移動できなくなる。衝突が解消されれば、左へ移動できるようになる。
                                    if is_collision_left:
                                        main_character.can_move_left = "cannot_move_left"
                                    else:
                                        main_character.can_move_left = "can_move_left"
                                
                                # 生成するブロックがメインキャラクターの右側のブロックならば
                                if (block_y == main_character.block_y or block_y == main_character.block_y+1) and block_x == main_character.block_x+1:
                                    is_collision_right = map.is_collision_right(block) # 右側のブロックとメインキャラクターが衝突しているかどうかを判定

                                    # 右のブロックと衝突していれば、右へ移動できなくなる。衝突が解消されれば、右へ移動できるようになる。
                                    if is_collision_right:
                                        main_character.can_move_right = "cannot_move_right"
                                    else:
                                        main_character.can_move_right = "can_move_right"

                                # 生成するブロックがメインキャラクターの上側(真上)のブロックならば
                                if block_y == main_character.block_y-1 and block_x == main_character.block_x:
                                    is_collision_top = map.is_collision_top(block) # 上側のブロックとメインキャラクターが衝突しているかどうかを判定

                                    # 上のブロックと衝突していれば、上へ移動できなくなる。衝突が解消されれば、上へ移動できるようになる。
                                    # ジャンプ中であれば、ジャンプは終了する。
                                    if is_collision_top:
                                        main_character.can_move_top = "cannot_move_top"
                                        main_character.jumping = "not_jumping"
                                        main_character.is_moving_down = "move_down"
                                    else:
                                        main_character.can_move_top = "can_move_top"
                                
                                # 生成するブロックがメインキャラクターの下側(真下)のブロックならば
                                if block_y == main_character.block_y+2 and block_x == main_character.block_x:
                                    is_collision_bottom = map.is_collision_bottom(block) # 下側のブロックとメインキャラクターが衝突しているかどうかを判定

                                    # 真下のブロックとメインキャラクターが衝突しており、かつジャンプ中でないならば、下降を止める
                                    if main_character.jumping == "not_jumping":
                                        if is_collision_bottom:
                                            main_character.is_moving_down = "not_move_down"
                                        else:
                                            main_character.is_moving_down = "move_down"
                                
                            
                            # ブロックを生成する
                            map.draw_block(block)

            
            # --------アイテムの処理--------

            # 画面右上に表示されている、アイテムエリアリストを表示
            main_character.items.item_area_list.display()


            # --------キーボード関連の処理--------
            
            # typeがkeydownまたはkeyupのイベントを取得
            for event in Key.get_key_event():

                # typeがkeydownのイベントを取得
                if event.type == pygame.KEYDOWN:

                    # メインキャラクターの処理

                    # メインキャラクターのキーリストを変更
                    main_character.change_key_list(event)

                    # アイテムの処理

                    # メインキャラクターのアイテムのキーリストを変更
                    main_character.items.change_key_list(event)

                    # メインキャラクターの選択されたアイテムの番号を変更
                    main_character.items.change_selected_item_number(event)

                
                # typeがkeyupのイベントを取得
                elif event.type == pygame.KEYUP:
                    
                    # メインキャラクターの処理

                    # メインキャラクターのキーリストを変更
                    main_character.change_key_list(event)

                    # アイテムの処理

                    # メインキャラクターのアイテムのキーリストを変更
                    main_character.items.change_key_list(event)

                    # メインキャラクターの選択されたアイテムの番号を変更
                    main_character.items.change_selected_item_number(event)

                
            
            # --------画面の処理--------

            # 画面の更新
            pygame.display.update()

            # 画面の初期化
            screen.fill((135, 206, 250))


