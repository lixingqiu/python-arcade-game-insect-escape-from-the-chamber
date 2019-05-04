"""
小虫密室逃脱.py
小虫子被困在密室了，只要帮它碰到密码箱，正确输入密码，才能让它逃脱。
可是有一只狗在把守密码箱，俗话说狗拿耗子，多管闲事。有一只老鼠被闲在笼子里。
只要小虫子拿到钥匙，笼子就会自动打开，耗子就会跑，狗就会去抓耗子。趁这个时候虫子就能去碰密码箱了。
请用上左右方向箭头操作小虫子，让它碰到钥匙后再去碰保险箱。

"""
 
import arcade

PASSWORD = "888"                      # 解锁密码
SPRITE_SCALING = 1                    # 定义缩放比例
SCREEN_WIDTH = 1280                   # 定义所渲染的屏幕宽度 
SCREEN_HEIGHT = 960                   # 定义所渲染的屏幕高度 
SCREEN_TITLE = "小虫密室逃脱by李兴球_arcade简易迷宫游戏"
SPRITE_PIXEL_SIZE = 64                # 地图方块尺寸 

# 定义物理常数 
MOVEMENT_SPEED = 5
JUMP_SPEED = 23
GRAVITY = 1.1

class MyGame(arcade.Window):
    """ 继承自窗口的游戏类. """
    input_password = False
    def __init__(self):
        """
        初始化方法
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        # 定义角色列表
        self.wall_list = None       
        self.key_list = None

        # 定义玩家相关变量        
        self.player_sprite = None
        self.physics_engine = None         
             

    def setup(self):
        """ 设置与初始化变量的值. """   

        # 老鼠，代表猎物
        self.rat = arcade.Sprite("images/mouse_right.png")
        self.rat.textures.append(arcade.load_texture("images/mouse_left.png"))
        self.rat.status = "hide"                                             # 这是自定义属性
        self.rat.center_x = 300
        self.rat.center_y = 80        

        # 笼子
        self.cage = arcade.Sprite("images/cage_close.png")
        self.cage.textures.append(arcade.load_texture("images/cage_open.png"))
        self.cage.bottom = 192
        self.cage.right = SCREEN_WIDTH//2
        self.cage.open = False
        
        # 狗，当笼子开启，老鼠会跑，它会去追猎物
        self.dog = arcade.Sprite("images/dog_left.png")
        self.dog.textures.append(arcade.load_texture("images/dog_right.png")) 
        self.dog.bottom = 380
        self.dog.right = SCREEN_WIDTH - 256
        self.dog.delay_frames = 0                                        # 自定义属性，老鼠跑后，狗要等待一定的帧数，然后才下去
        self.dog.move_frames = 0                                         # 自定义属性，老鼠跑了后，它要移动的帧数
        

        # 保险箱
        self.safe_box = arcade.Sprite("images/保险箱.png")
        self.safe_box.bottom = 384
        self.safe_box.right = SCREEN_WIDTH -64
        
        # 玩家操作的角色实例化，这里是一只昆虫，碰到狗或老鼠会死亡
        self.player_sprite = arcade.Sprite("images/lixingqiu.png", SPRITE_SCALING*0.5)
        self.player_sprite.status = "alive"
        # 给昆虫设定坐标
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 64       

        
        #  加载 地图
        my_map = arcade.read_tiled_map(f"house_1.tmx", SPRITE_SCALING)
        
        # 读取不可移动的平台数据阵列'ground'是一图层的名称
        map_array = my_map.layers_int_data['ground']        
          
        # 从墙生成地图列表
        self.wall_list = arcade.generate_sprites(my_map, 'ground', SPRITE_SCALING)
        self.wall_list.move(SPRITE_PIXEL_SIZE ,0)   # 水平方向和垂直方向移动
        
        # 加载平台型的物理引擎，简单的理解为让玩家和墙发生碰撞的封装好了的对象
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,self.wall_list,gravity_constant=GRAVITY)
        
        # 读取key阵列， picked是地图中的一个层，这个层里是可拾取的道具。
        keys_array = my_map.layers_int_data['picked']
        
        # 生成key列表，在地图设计中，可增加多个key
        self.key_list = arcade.generate_sprites(my_map, 'picked', SPRITE_SCALING)
        self.key_list.move(SPRITE_PIXEL_SIZE ,0)       
         
    
    def let_rat_go(self):
        """设定让耗子跑的状态"""
        self.rat.status = "run"
        self.rat.change_x =  10
        
    def let_rat_dead(self):
        """让老鼠死的状态"""        
        self.rat.status = "dead"
        self.rat.change_x =  0
        
        
    def on_draw(self):
        """        渲染屏幕        """
       

        # 开始渲染屏幕
        arcade.start_render()
       
        # 画所有的角色
       
        self.wall_list.draw()
        self.key_list.draw()
        self.cage.draw()        
        self.safe_box.draw()
        self.dog.draw()
        if self.player_sprite.status == "alive": self.player_sprite.draw()
        if self.rat.status == "run":self.rat.draw()

        
    def on_key_press(self, key, modifiers):
        """
        当按键时调用此方法
        """
        if key == arcade.key.UP:
            if self.physics_engine.can_jump():          # 这里是检测有没有在地面
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED
 

    def on_key_release(self, key, modifiers):
        """
        当松开键时调用此方法
        """
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def update(self, delta_time):
        """ 移动与游戏的逻辑，这个方法不断地执行，如果本关key数加载完了，那么此关结束 """

        if len(self.key_list)==0 and  self.cage.open == False: # 如果接到了钥匙，则放开猎物并且笼子是关着的
            print(self.cage.cur_texture_index )
            self.let_rat_go()                              # 打开笼子让它跑
            self.cage.open = True
            self.cage.cur_texture_index = 1
            self.cage.set_texture(1)                       # 切换笼子造型为没有装老鼠的图片
            self.dog.delay_frames = 60                     # 狗在一定的帧数后会去捉老鼠
            
        if self.dog.delay_frames>0 :                       # 开始延时等待，时间到了就往左下移
            self.dog.delay_frames -= 1
            if self.dog.delay_frames ==  0 :               # 时间到了启动狗
                self.dog.change_x = -12                    # 设定水平单位位移量
                self.dog.change_y = -5                     # 设定垂直单位位移量
                self.dog.move_frames = 66                  # 设定总共要移动的帧数

        if self.dog.move_frames > 0:                       # 移动过程中，此变量大于0，更新狗的坐标     
            self.dog.update()
            self.dog.move_frames -= 1
        else:
            # 所移动的帧数为0，则停止
            if self.dog.change_x != 0 :
                self.dog.change_x = 0
                self.dog.change_y = 0
                self.dog.set_texture(1)
        
        if self.rat.status == "run" and  not self.rat.status=='dead':
            
            if self.rat.left < SPRITE_PIXEL_SIZE or self.rat.right >  SCREEN_WIDTH-SPRITE_PIXEL_SIZE :
                self.rat.change_x = -self.rat.change_x
                self.rat.cur_texture_index = 1 - self.rat.cur_texture_index
                self.rat.set_texture(self.rat.cur_texture_index)                 
            self.rat.update()
            if arcade.check_for_collision(self.rat,self.dog): # 碰到小狗把它的状态标为dead
               self.let_rat_dead()

        # 物理引擎更新
        self.physics_engine.update()
        
        # 玩家与key的碰撞检测，返回列表，列表不为空则把里面的key删除
        keys_hit = arcade.check_for_collision_with_list(self.player_sprite, self.key_list)
        for key in keys_hit: key.kill()        

        # 碰到狗就死
        if arcade.check_for_collision(self.player_sprite,self.dog): 
            self.player_sprite.status = "dead"            # 自定义属性，让它的状态为死
        
        # 碰到保险箱只要把arcade窗口关闭就行。
        if arcade.check_for_collision(self.player_sprite,self.safe_box):
            MyGame.input_password = True                  # 这个是必需的，它能描述是否是正常碰到保险箱而不是玩家手动直接关闭窗口
            arcade.close_window()
          

def show_password_input_UI():
    """显示密码输入界面，本函数定义了一个Square类，用来实例化三个小方块，单击它们会换造型"""
    print(" 这里显示密码输入界面")
    images = ["images/" + str(i) + ".gif" for i in range(10)]
    import turtle
    import random
                      
    class Square(turtle.Turtle):
        """方块类"""
        liebiao = [ ]                     # 装方块的列表
        password = ""                     # 类变量密码
        def __init__(self,images):
            turtle.Turtle.__init__(self,visible=False)
            self.images = images
            self.penup()
            self.index = 0                 # 初始索引号
            self.set_shape(0)
            self.st()                      # 显示方块
            self.onclick(self.change_digit)
            Square.liebiao.append(self)    # 加入列表
            
        def set_shape(self,index):
            """根据索引号设定造型"""            
            self.shape(self.images[index])

        def change_digit(self,x,y):
            """随机生成一个索引号，再设定造型"""
            
            index= random.randint(0,9)     # 随机生成从0到9的索引号
            self.index = index             # 仅记录索引
            self.shape(self.images[index])
            # 合成密码            
            Square.password = "".join([str(square.index) for square in Square.liebiao])
            self.screen.title(Square.password) # 在标题显示密码
            if Square.password == PASSWORD:    # 密码正确，游戏结束
                self.screen.clear()
                self.screen.bgcolor("cyan")
                turtle.write("解锁成功！欢迎进入梦幻世界！",font=("黑体",16,"normal"),align='center')           
            
    screen = turtle.Screen()
    screen.delay(0)    
    screen.setup(SCREEN_WIDTH//3,SCREEN_HEIGHT//3)
    screen.bgcolor("#999999")
    screen.title("请输入密码，用鼠标单击数字即可")
    [screen.addshape(image) for image in images]
    turtle.penup()
    turtle.ht()
    turtle.goto(0,100)
    turtle.write("请用鼠标单击输入密码箱的密码：",font=("黑体",16,"normal"),align='center')
    square1 = Square(images)             # 左边方块
    square1.goto(-100,0)                  
    square2 = Square(images)             # 中间方块
    square3 = Square(images)             # 右边方块
    square3.goto(100,0)
    screen.mainloop()

def main():
    window = MyGame()
    window.setup()
    arcade.run()
    if MyGame.input_password:             # 如果虫子正常碰到保险箱，则这个界面会出现  
       print("arcade的窗口关闭后,run就会自动结束，这时显示turtle界面，单击鼠标的形式输入密码")
       show_password_input_UI()

if __name__ == "__main__":
    main()
