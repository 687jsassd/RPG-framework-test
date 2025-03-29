from syst.init_pkg import *
from syst.Materials import *
#注意,在定义物品时,如想要自定义排序方式,需要加入__lt__方法,
#例子见Heal_potion类
#如不加入,则按照物品名称的字典序排序
#改变常量表请在CONSTANT_LIST.py中修改
#公共常用函数请在base_func.py中修改

#注释格式:名称(特殊值意义)


class Citem(Item):
    """
    Citem类是用于暂时存放新物品的类，当新物品尚未归入已有类时，可以使用此类。

    此类继承自Item类.

    核心功能：
    - __init__：构造函数，用于初始化Citem对象。
    - use：使用Citem的方法，由于Citem是临时存放处，因此打印提示信息并返回-1。

    使用示例：

    构造函数参数：
    任意Item类的初始化参数。

    注意：
    - Citem是临时存放处，因此使用Citem时，不会对目标角色产生实际效果。
    - spe_val属性是可选的，用于存储额外的信息。
    """
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def use(self, target: 'Character' = None) -> int:
        """
        使用Citem，由于Citem是临时存放处，因此打印提示信息并返回-1。

        :param target: 目标角色，默认为None
        :return: 始终返回-1
        """
        return -1

#ID:1 治疗药水(治疗值)
class Heal_potion(Item):
    def __init__(self,**kwargs):
        """
        初始化治疗药水对象

        :param heal_amount: 治疗药水回复的生命值，默认为10
        """
        if not kwargs.get('item_id'):
            kwargs['item_id']=1
        if not kwargs.get('materials'):
            kwargs['materials']={m_Life_essence:0.5,m_Iron:0.5}
        if kwargs.get('heal_hp',0)<0:
            kwargs['heal_hp']=0
        super().__init__(**kwargs)
        if kwargs.get('attributes_affected_by_materials'):
            self.heal_amount = material_bonus_cal(self,special_rule=1)
        else:
            self.heal_amount = kwargs.get('heal_hp',0)
        self.final_attributes['hp_heal']=self.heal_amount
        self.name=f'治疗药水({self.heal_amount})'
        self.description=f'回复{self.heal_amount}的生命值'
        self.price=int(1.4*pow(1.002,pow(self.heal_amount,0.37))+pow(self.heal_amount,1.25))
        if kwargs.get('attributes_affected_by_materials'):
            self.price=material_bonus_cal(self,special_rule=-2)    
    def use(self,target: 'Character' = None) ->int:
        """
        使用治疗药水回复目标的生命值

        :param target: 目标角色对象，默认为None
        :return: 使用治疗药水后的回复信息
        """
        if target.hp == target.max_hp:
            return -5
        else:
            actual_heal=target.heal(self.heal_amount)
            print(f"{target} {GREEN}healed for {actual_heal} HP {RESET}.")
            return 1
#ID:2 飞镖(伤害)
class Dart(Item):
    def __init__(self,**kwargs):
        if not kwargs.get('item_id'):
            kwargs['item_id']=2
        if not kwargs.get('materials'):
            kwargs['materials']={m_Iron:1}


        super().__init__(**kwargs)
        self.base_attributes['atk']=max(0,self.base_attributes['atk'])
        self.damage = material_bonus_cal(self)['atk']
        self.name=f'飞镖({self.damage})'
        self.description=f'造成{self.damage}点伤害'
        self.price=int(2*pow(1.01,pow(self.damage,0.55))+pow(self.damage,1.33))
    
    def use(self, target: 'Character' = None) ->int:
        """
        使用飞镖攻击目标

        :param target: 目标角色对象，默认为None
        :return: 使用飞镖后的攻击信息
        """
        target.take_damage(self.damage)
        print(f"{target} {YELLOW}took {self.damage} damage{RESET}.")
        return 1

class Source_material(Item):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    
    def use(self, target: 'Character' = None) ->int:
        """
        使用材料，由于材料不可使用，因此打印提示信息并返回-1。

        :param target: 目标角色，默认为None
        :return: 始终返回-1
        """
        return -1

i_small_copper_block=Source_material(name='小铜块',
                                     description='小铜块，用来打造或者修复装备',
                                     price=10,
                                     materials={m_Copper:1},
                                     item_id=4,
                                     size=1)
i_small_iron_block=Source_material(name='小铁块',
                                     description='小铁块，用来打造或者修复装备',
                                     price=10,
                                     materials={m_Iron:1},
                                     item_id=3,
                                     size=1)
i_small_life_essence=Source_material(name='小生命精华',
                                     description='小生命精华，用来打造或者修复装备',
                                     price=30,
                                     materials={m_Life_essence:1},
                                     item_id=5,
                                     size=1)

#强化石类({加成字典},{成功率字典})
class Enhance_stone(Item):
    def __init__(self,name='强化石',description='用于强化装备',enhance_dict: dict=None, success_rate_dict: dict=None,quality:int = 1):
        """
        初始化强化石对象

        :param enhance_dict: 加成字典，键为属性名，值为加成值
        :param success_rate_dict: 成功率字典，键为属性名，值为成功率
        """
        if not enhance_dict:
            enhance_dict = {}
        if not success_rate_dict:
            success_rate_dict = {}
        super().__init__(
            name=name,
            description=description,
            price=100,
            quality=quality
                         )
        self.enhance_dict = enhance_dict
        self.success_rate_dict = success_rate_dict

    def use(self, target: 'Character' = None) ->int:
        #不能直接使用,用于Equipment中的enhance方法
        return -1
    
            
