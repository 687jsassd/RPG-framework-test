import sys
import os

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)

# 获取当前文件所在的目录
current_dir = os.path.dirname(current_file_path)

# 获取项目的根目录（假设项目的根目录是当前目录的上一级目录）
project_root = os.path.dirname(current_dir)

# 构建debugger.py文件的完整路径
debugger_path = os.path.join(project_root, 'syst', 'debugger.py')

# 将项目的根目录添加到sys.path
sys.path.append(project_root)


from syst.imprt_all import *
import time
import tracemalloc
import cProfile


def test_heal():
    """性能分析数据:
        原仓库系统(Inventory):
        添加10000个不同的Heal_potion对象 用时4.52s
        添加10000个相同的Heal_potion对象 用时0.09s
    
        改进后(Inventory_improved):
        添加10000个不同的Heal_potion对象 用时0.05s
        添加10000个相同的Heal_potion对象 用时0.04s"""

    hero = Character("Hero")

    for i in range(10):
        hero.inventory.add_item(Heal_potion())
    for i in range(1):
        hero.inventory.add_item(Heal_potion())
    hero.take_damage(20)
    print(hero.hp)
    print(hero.inventory.get_items(Heal_potion))
    print(hero.inventory.get_items(Heal_potion,23,mode='display'))
    print(hero.inventory.get_exact_item(24, Heal_potion))
    #hero.use_item_fuzzy(Heal_potion,hero,23)
    print(hero.hp)
    print(hero.inventory.get_items(Heal_potion,mode='display'))
    #hero.inventory.show_inventory()
    #hero.inventory.show_inventory(Dart)
    print("Success\n")
    

def test_equipment():
    hero = Character(f"{YELLOW}Hero{RESET}")
    print(hero.get_cur_status())
    print(hero.get_cur_equipment())
    print(hero.get_cur_status(turns=0))
    print(hero.get_cur_status(turns=1))
    sw=Weapon(name=f"{GREEN}长剑{RESET}", bonuses={'spd': 10,'eva':0.03})
    hero.equip_item(sw)
    print(hero.get_cur_status(turns=2))
    print(hero.get_cur_equipment())
    am=Armor(name="皮甲", bonuses={'spd': -10,'crit_dmg':0.2},resistances={'fire': -0.1,'unknown':1.0})
    hero.equip_item(am)
    print(hero.get_cur_status(turns=3))
    print(hero.get_cur_equipment())
    hero.unequip_item(sw)
    hero.unequip_item(am)
    print(hero.get_cur_status(turns=4))
    print(hero.get_cur_equipment())
    ac=Accessory(name="护身符", bonuses={'spd': -1,'eva':0.1})
    hero.inventory.add_item(ac)
    ac=Accessory(name="护身符2",resistances={'normal':1.0})
    hero.inventory.add_item(ac)
    print(hero.inventory.get_items(Accessory))
    print(hero.get_cur_status(turns=0))
    print(hero.get_cur_status(turns=1))
    print("Success\n")
#test_heal()
#test_equipment()

def test_lv():
    hero = Character("Hero")
    hero.attitude['player']='friendly'
    for i in range(100):
        print(f"LV{i}, {hero.exp_curve_func(i)}")
    for i in [1,10,100,1000,10000]:
        hero.exp=hero.exp_curve_func(i)
        print(hero.get_cur_status(turns=2))
        print('\n')
    i=5
    hero.exp=hero.exp_curve_func(i)
    print(hero.get_cur_status(turns=1))
    print('\n')
    hero.exp=hero.exp_curve_func(i+1)
    hero.equip_item(Weapon(name='长剑',bonuses={'max_hp':-50},resistances={'normal':0.2},spe_effect_id=-1,durability=27))
    print(hero.get_cur_status(turns=1))
    #print(hero.resistances)
    hero.gain_exp(53)
    hero.take_damage(20)
    hero.take_mp_damage(20)
    print(hero.get_cur_status(turns=2))
    hero.gain_exp(1)
    print(hero.get_cur_status(turns=3))
    print(hero.get_cur_equipment())
    print("Success\n")

def test_color_items():
    hero = Character("Hero")
    for i in [1,2,3,4,5,6,7,8,9,10,20,30,40,50,60,70,80,90,100,1000,10000,100000,1000000]:
        wp=Heal_potion(quality=i)
        fb=Dart(quality=i)
        print(wp.get_basic_status())
        print(fb.get_basic_status())
    print("Success\n")

def test_inventory_show_and_durability():
    hero = Character("Hero")
    print("物品添加和库存显示测试:\n")
    for i in [1,10,-22,888]:
        hero.inventory.add_item(Dart(base_attributes={'atk':i}))
        hero.inventory.add_item(Weapon(name=f'武器{i}', base_attributes={'spd': i,'eva':0.03},quality=4,description='测试下,这个装备应该被装备'))
    hero.inventory.show_inventory(checker=hero)
    print("Success\n")
    print("特定索引物品的获取和信息显示测试:\n")
    speeq=hero.inventory.idxit(Weapon,1)
    print(speeq.get_basic_status())
    print("Success\n")
    print("装备和装备后各面板变化测试:\n")
    print(hero.get_cur_equipment())
    hero.equip_item(speeq)
    print(hero.get_cur_equipment())
    hero.inventory.show_inventory(checker=hero)
    print("Success\n")
    print("装备耐久度消耗测试:\n")
    print(speeq.get_basic_status())
    speeq.durability_down(33)
    print(speeq.get_basic_status())
    speeq.durability_down(33)
    print(speeq.get_basic_status())
    speeq.durability_down(33)
    print(speeq.get_basic_status())
    print(hero.get_cur_equipment())
    cppr=Dart()
    cppr.max_durability=20
    cppr.durability=20
    for i in range(20):
        cppr.durability_down(1)
        print(cppr.get_basic_status())
    print("Success\n")
    print("耐久度归0时自动破坏测试:\n")
    print(hero.inventory.show_inventory(Weapon))
    speeq.durability_down(33)
    print(speeq.get_basic_status())
    print(hero.inventory.show_inventory(Weapon))
    print(hero.get_cur_equipment())
    print("Success\n")
    print("装备所有者变更测试:\n")
    test_owner_changer = Character(f'{YELLOW}Test{RESET}')
    speeq.owner_change(test_owner_changer)
    print(speeq.get_basic_status())
    hero.inventory.show_inventory(Weapon,checker=hero)
    print("Success\n")
    print("非自己装备的尝试装备和卸下测试:\n")
    speeq.durability_up(33)
    hero.inventory.add_item(speeq)
    hero.inventory.show_inventory(Weapon,checker=hero)
    print(speeq.get_basic_status())
    hero.equip_item(speeq)
    print(hero.get_cur_equipment())
    hero.use_item(speeq)
    print(hero.get_cur_equipment())
    print("\n")
    hero.unequip_item(speeq)
    print(hero.get_cur_equipment())
    hero.use_item(speeq)
    print(hero.get_cur_equipment())
    print("Success\n")
    print("非自己装备的装备的尝试使用测试:\n")
    print("\n")
    hero.inventory.show_inventory(Weapon,checker=hero)
    speeq.owner_change(hero)
    print(speeq.get_basic_status())
    test_owner_changer.equip_item(speeq)
    print(test_owner_changer.get_cur_equipment())
    hero.use_item(speeq)
    hero.inventory.show_inventory(Weapon,checker=hero)
    hero.use_item(speeq)
    print(hero.get_cur_equipment())
    print(test_owner_changer.get_cur_equipment())
    hero.inventory.show_inventory(checker=hero)
    test_owner_changer.inventory.show_inventory(checker=test_owner_changer)
    test_owner_changer.inventory.add_item(cppr)
    test_owner_changer.inventory.add_item(copy.deepcopy(speeq))
    test_owner_changer.inventory.show_inventory(checker=test_owner_changer)
    test_owner_changer.use_item(speeq)
    print("Success\n")

def test_idt():#测试一模一样的两个物品使用时会不会被判定为同一个物品
    hero = Character("Hero")
    hero.inventory.add_item(Dart(1))
    hero.inventory.add_item(Dart(1))
    hero.inventory.show_inventory()
    hei=hero.inventory
    hero.use_item_fuzzy(Dart,hero)
    hei.show_inventory()
    print("完成\n")
    hero.use_item_fuzzy(Dart,hero)
    hei.show_inventory()
    print("完成\n")
    hero.use_item_fuzzy(Dart,hero)
    hei.show_inventory()
    print("完成\n")
    hero.use_item_fuzzy(Dart,hero)
    hei.show_inventory()
    print("Success\n")

def test_idt_equipment():
    hero = Character("Hero")
    wp=Weapon(name='武器', bonuses={'spd': 1,'eva':0.03},quality=4,description='测试下,这个装备应该被装备')
    hero.inventory.add_item(wp)
    hero.inventory.add_item(wp)
    hero.inventory.show_inventory()
    print(hero.get_cur_equipment())
    hero.inventory.show_inventory()
    
def test_speed():
    hero = Character("Hero")
    for i in range(1,25):
        wp=Weapon(item_id=6,materials={m_Life_essence:0.05*i,m_Iron:1-0.05*i},size=int(0.3*i))
        hero.inventory.add_item(wp)
    hero.inventory.sub_sort()
    hero.inventory.show_inventory(item_type=Weapon,checker=hero)
    print("Success\n")
def test_breakable():
    hero = Character("Hero")
    wp=Weapon(name='武器', bonuses={'spd': 1,'eva':0.03},quality=4,description='这个装备可以损毁')
    hero.inventory.add_item(wp)
    wp=hero.inventory.idxit(Weapon,0)
    hero.equip_item(wp)
    hero.inventory.show_inventory(checker=hero)
    print(hero.get_cur_equipment())
    for i in range(3):
        wp.durability_down(40)
    hero.inventory.show_inventory(checker=hero)
    print(hero.get_cur_equipment())
    print('\n')
    wp=Weapon(name='武器', bonuses={'spd': 100,'eva':0.03},quality=6,breakable=False,description='这个装备不能损毁')
    hero.inventory.add_item(wp)
    wp=hero.inventory.idxit(Weapon,0)
    hero.equip_item(wp)
    hero.inventory.show_inventory(checker=hero)
    print(hero.get_cur_equipment())
    for i in range(3):
        wp.durability_down(40)
    hero.inventory.show_inventory(checker=hero)
    print(hero.get_cur_equipment())
    print(wp.durability)
    print('\n')
    itm=Heal_potion()
    itm.breakable=False
    hero.inventory.add_item(itm)
    itm=hero.inventory.idxit(Heal_potion,0)
    print(itm.get_basic_status(checker=hero))
    itm.durability_down(40)
    print(itm.get_basic_status(checker=hero))
    hero.use_item(itm,hero)
    print(itm.get_basic_status(checker=hero))
    print("Success\n")

def test_use_item_advanced():
    hero = Character("Hero")
    hero2 = Character("Hero2")
    hero.hp=1
    hero2.hp=1
    itm=Heal_potion()
    itm.breakable=True
    itm.max_durability=4
    itm.durability=4
    hero.inventory.add_item(itm)
    hero.inventory.show_inventory()
    itm=hero.inventory.idxit(Heal_potion,0)
    print("\n")
    print(itm.get_basic_status())
    #hero.use_item_for_many_times(itm,hero2,6)
    fake_itm=Heal_potion()
    fake_itm.owner=hero
    hero.use_more_items([itm,fake_itm,itm],[hero2])
    print(itm.get_basic_status())
    hero.inventory.show_inventory()
    print(hero.hp)
    print(hero2.hp)
    print("Success\n")

def test_lv_stas():
    hero = Character("Hero")
    for i in [1,5,10,15,20,30,40,50,100,200,300,500,1000,10000]:
        hero.exp=hero.exp_curve_func(i)
        print(f"lv{i}的默认主角的ATK是{hero.atk},DEF是{hero.defe},HP最大值是{hero.max_hp}")
    print("Success\n")

def test_reveal_and_material():
    hero = Character("Hero")
    print("\n\n")
    for i in range(1,7):
        wp=Heal_potion(base_attributes={'hp_heal':7},materials={m_Iron:0.3+0.1*i,m_Copper:0.7-0.08*i},quality=4)
        wp.revealed=False
        hero.inventory.add_item(wp)
        #wp=hero.inventory.idxit(Heal_potion,i-1)
        #print(hp.get_basic_status(checker=hero))
        hero.inventory.show_inventory(checker=hero,item_type=Heal_potion)
        hero.reveal_item(wp)
    for i in range(1,7):
        wp=Heal_potion(base_attributes={'hp_heal':7},materials={m_Iron:0.3,m_Copper:0.7},quality=4)
        wp.revealed=False
        hero.inventory.add_item(wp)
        #wp=hero.inventory.idxit(Heal_potion,i-1)
        #print(hp.get_basic_status(checker=hero))
        hero.inventory.show_inventory(checker=hero,item_type=Heal_potion)
        hero.reveal_item(wp)
    print('\n\n')
    #hero.inventory.sub_sort(Heal_potion)
    #a=wp=hero.inventory.idxit(Heal_potion,0)
    #b=wp=hero.inventory.idxit(Heal_potion,1)
    #a_dict = {k: v for k, v in a.__dict__.items() if k not in ['uuid', 'name', 'description']}
    #b_dict = {k: v for k, v in b.__dict__.items() if k not in ['uuid', 'name', 'description']}
    #print(a_dict==b_dict)
    #for i in a_dict:
    #    if b_dict[i]!=a_dict[i]:
    #        print(f"不相符的部分{i}")
    #print("Success\n")
    hero.inventory.sub_sort(Heal_potion)
    hero.inventory.show_inventory(checker=hero,item_type=Heal_potion)
    hero.knowledge.show(type='item')
    hero.knowledge.show(type='material')
    print("Success\n")

def test_reveal_and_material_equipments():
    hero = Character("Hero")
    for i in range(1,100):
        wp=Weapon(item_id=6,base_attributes={'atk':7},materials={m_Iron:0.3+0.01*i,m_Copper:0.7-0.004*i},quality=4)
        #wp.revealed=False
        wp=hero.inventory.add_item(wp)[0]
        #print(hp.get_basic_status(checker=hero))
        #hero.inventory.show_inventory(checker=hero,item_type=Weapon)
        #hero.reveal_item(wp)
    print('\n\n')
    #hero.inventory.sub_sort(Weapon)
    #a=wp=hero.inventory.idxit(Weapon,0)
    #b=wp=hero.inventory.idxit(Weapon,1)
    #a_dict = {k: v for k, v in a.__dict__.items() if k not in ['uuid', 'name', 'description']}
    #b_dict = {k: v for k, v in b.__dict__.items() if k not in ['uuid', 'name', 'description']}
    #print(a_dict==b_dict)
    #for i in a_dict:
    #    if b_dict[i]!=a_dict[i]:
    #        print(f"不相符的部分{i}")
    #print("Success\n")
    hero.inventory.sub_sort(Weapon)
    hero.inventory.show_inventory(checker=hero,item_type=Weapon,display_mode='detailed')
    hero.knowledge.show(type='item')
    hero.knowledge.show(type='material')
    print("Success\n")

def test_repair():
    hero = Character("Hero")
    wp=Weapon(item_id=6,base_attributes={'atk':100},materials={m_Iron:0.33,m_Copper:0.33,m_Life_essence:0.33},quality=0)
    wp=hero.inventory.add_item(wp)[0]
    hero.inventory.show_inventory(checker=hero,item_type=Weapon)
    wp.durability_down(30)
    hero.inventory.show_inventory(checker=hero,item_type=Weapon)
    rp=hero.inventory.add_item(Weapon(item_id=6,base_attributes={'atk':1},materials={m_Iron:0.31,m_Copper:0.44,m_Life_essence:0.25},quality=0),1)[0]
    hero.inventory.show_inventory(checker=hero)
    for i in range(2):
        hero.repair_item(wp,rp)
    hero.inventory.show_inventory(checker=hero)
    print("Success\n")

def test_new_attributes():
    hero=Character("Hero")
    print(hero.get_cur_status())
    wp=Weapon(item_id=6,base_attributes={'atk':10,'defe':20,'atk*':0.13},base_resistance={'normal':0.1,'fireL':0.05,'water*L':0.4},quality=4)
    wp=hero.inventory.add_item(wp)[0]
    hero.use_item(wp,hero)
    hero.inventory.show_inventory(checker=hero,item_type=Weapon)
    print(hero.get_cur_status(turns=1))
    hero.attitude['player']='friendly'
    am=Armor(base_attributes={'atk':-70,'defe':200,'defe*':0.05},base_resistance={'normal':0.1,'fireL':0.05,'water*L':-1.99},quality=4)
    am=hero.inventory.add_item(am)[0]
    hero.use_item(am,hero)
    hero.inventory.show_inventory(checker=hero)
    print(hero.get_cur_status(turns=2))
    
    print("Success\n")
#测试队伍
def test_team():
    heroA=Character('heroA',team_id=0)
    heroB=Character('heroB',team_id=0)
    heroC=Character('heroC',team_id=2)
    teamA=Team(team_id=1,volume=2,now_mm={1:heroB})
    teamA.show()
    teamA.add_member(heroA)
    teamA.show()
    teamA.change_seat(1,2)
    teamA.show()
    teamA.add_member(heroC)
    teamA.discard_member(1)
    teamA.show()
    print('Success\n')

#测试新的物品命名规则
def test_new_name():
    heroA=Character('heroA',team_id=0)
    item1=Heal_potion(attributes_affected_by_materials=False)
    item1=heroA.inventory.add_item(item1)[0]
    item1.show()
    item1.rename("重命名后的生命药水")
    item1.show()
    item1.materials={m_Iron:0.3,m_Copper:0.7,m_Life_essence:0.2}
    item1.prefix={'前缀1':1,f'{RED}前缀2{RESET}':99}
    item1.upgrade_level=4
    item1.re_ini_name(mode='')
    item1.show()
    print('Success\n')
    
    


set_debug_mode(True)  # 调试模式
start_console_logger()
    
# 示例游戏代码
obj = BaseClass()
obj.log_info("测试开始")  # 仅在DEBUG_MODE=True时记录


tracemalloc.start()  # 开始跟踪内存分配
start_time = time.time()  # 开始计时

def run_all_tests():
    test_new_attributes()
    test_heal()
    test_equipment()
    test_lv()
    test_color_items()
    test_inventory_show_and_durability()
    test_idt_equipment()
    test_breakable()
    test_use_item_advanced()
    test_lv_stas()
    #test_reveal_and_material_equipments()
    #test_repair()
    test_speed()

#cProfile.run('run_all_tests()')
#test_repair()
print(f"{GREEN}All Success!{RESET}\n")
end_time = time.time()  # 结束计时
current, peak = tracemalloc.get_traced_memory()  # 获取当前和峰值内存使用情况
tracemalloc.stop()  # 停止跟踪内存分配
print(f"Time taken: {end_time - start_time} seconds")
print(f"Current memory usage: {current / 10**6} MB; Peak memory usage: {peak / 10**6} MB")

obj.log_info(f"{GREEN}测试结束{RESET}")  # 仅在DEBUG_MODE=True时记录
obj.log_info(f"用时: {end_time - start_time} 秒")
obj.log_info(f"当前内存使用: {current / 10**6} MB; 峰值内存使用: {peak / 10**6} MB")