#关于此文件的说明:
#此文件为初始化包,用于导入所用的包和关键类
#常量表见CONSTANT_LIST.py
from abc import ABC, abstractmethod
from itertools import chain
from bisect import bisect_left, bisect_right
from collections import defaultdict
from logging.handlers import SocketHandler
import copy,uuid,logging,os,random,subprocess,socket,threading,sys
from sortedcontainers import SortedList
from typing import List, Dict, Tuple, Union
from syst.CONSTANT_LIST import *
from syst.base_func import *
from syst.debugger import *

DEBUG_MODE = False
logger = logging.getLogger(__name__)
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



def set_debug_mode(enabled):
    global DEBUG_MODE
    DEBUG_MODE = enabled
def start_console_logger():
    # 启动新终端运行日志服务器
    if sys.platform == "win32":
        subprocess.Popen(f'start cmd /k python "{debugger_path}"', shell=True)
    
    # 配置Socket日志处理器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    socket_handler = SocketHandler('localhost', 9020)
    root_logger.addHandler(socket_handler)


class BaseClass:
    def log_debug(self, message):
        if DEBUG_MODE:
            logger.debug(message)

    def log_info(self, message):
        logger.info(message)
    def log_warning(self, message):
        logger.warning(f"{YELLOW}{message}{RESET}")

    def log_error(self, message):
        logger.error(f"{RED}{message}{RESET}")

    def log_critical(self, message):
        logger.critical(f"{RED}{message}{RESET}")

    def log_exception(self, message):
        logger.exception(f"{RED}{message}{RESET}")
debug_log=BaseClass()

#FIXME:材料类
class Material():
    """
    Material类用于表示一种材料，包含其基本属性和特殊效果。

    核心功能包括：
    - 初始化材料的基本属性，如材料ID、质量、名称、相性、密度、加成和特殊效果。
    - 显示材料的当前状态，包括密度、相性、加成和特殊效果。
    - 支持材料的比较和哈希操作，以便于在集合中使用。

    使用示例：
    m_Copper=Material(name="铜",
              compatibilities={'A':1,'B':3,'C':0},
              density=8,
              bonuses={'atk*':0.05,'def*':0.05,'spd*':-0.1},
              spe_effects={0.7:2},
              material_id=2
              )

    构造函数参数：
    - material_id (int): 材料的唯一标识符，默认为0。
    - quality (int): 材料的质量等级，默认为1。
    - name (str): 材料的名称，默认为"未知材料"。
    - compatibilities (dict): 材料与其他材料的相性字典，键为材料类型，值为相性值，默认为{'A': 0, 'B': 0, 'C': 0}。
    - density (float): 材料的密度，默认为1。
    - bonuses (dict): 材料的加成效果字典，支持一般加减和乘法加成（如"'atk*': 0.1"表示攻击力加成10%），默认为空字典。
    - spe_effects (dict): 材料的特殊效果字典，键为材料占比，值为特殊效果ID，默认为空字典。
    - **kwargs: 其他可选参数，用于扩展材料的属性。

    特殊说明：
    - `spe_effects`字典中的键值对表示材料占比多少时获得此效果以及特殊效果ID。
    - `bonuses`字典中的键值对支持一般加减和乘法加成，如"'atk*': 0.1"表示攻击力加成10%。
    - 类中的`show_status`方法用于打印材料的详细信息。
    - 类支持比较操作和哈希操作，以便于在集合中使用。
    """
    
    def __init__(self,
                 material_id=0,
                 quality=1,
                 name="未知材料",
                 compatibilities=None,
                 density=1,
                 bonuses=None,
                 resistance_bonuses=None,
                 spe_effects=None,
                 **kwargs):
        if not compatibilities:
            compatibilities={'A':0,'B':0,'C':0}
        if not bonuses:
            bonuses={}
        if not resistance_bonuses:
            resistance_bonuses={}
        if not spe_effects:
            spe_effects={}
        self.name=name
        self.compatibilities=compatibilities
        self.density=density
        self.bonuses=bonuses
        self.resistance_bonuses=resistance_bonuses
        self.spe_effects=spe_effects
        self.material_id=material_id
        self.quality=quality
    def show_status(self):
        print(f"{self},ID:{self.material_id}")
        print(f"密度:{self.density}")
        print(f"相性:{self.compatibilities}")
        print(f"材料加成:{self.bonuses}")
        if self.resistance_bonuses:
            print(f"抗性加成:{self.resistance_bonuses}")
        if self.spe_effects:
            print(f"特殊效果:")
            for key,value in self.spe_effects.items():
                print(f"*构成材料占比超过{key*100:.2f}%时获得特殊效果:{SPE_EFFECT_ID[value]}")
        else:
            print(f"无特殊效果")
        print('\n')
    
    def __str__(self):
        return convert_colorful_text(self.name, get_quality_color(self.quality))
    def __eq__(self, other):
        return self.material_id == other.material_id
    def __hash__(self):
        return hash((self.material_id, self.name))
    
m_Unknown=Material(name="未知材料",
              material_id=0,
              compatibilities={'A':1,'B':1,'C':1},
              density=1,
              bonuses={},
              resistance_bonuses={},
              spe_effects={}
              )

def material_bonus_cal(item, convert_type='all', special_rule=0):
    final_bonus_dict = {i: 0 for k in ALL_BONUS for i in [k, f'{k}*', f'{k}L', f'{k}*L']}
    final_resistance_dict = {i: 0 for k in ALL_RESISTANCE for i in [k, f'{k}*', f'{k}L', f'{k}*L']}
    if not special_rule:
            for i in final_bonus_dict.keys():
                base_bonus = item.base_attributes.get(i, 0)
                material_bonus = sum((mt.bonuses.get(i, 0) * parts for mt, parts in item.materials.items()))
                if i in ['eva','crit','crit_dmg'] or '*'in i:
                    final_bonus_dict[i] = (base_bonus + material_bonus)*(1+(item.quality-2)/13)*0.975**item.size if 10>item.quality>=0 else (base_bonus + material_bonus) *0.9 *0.97**item.size
                else:
                    final_bonus_dict[i] = int((base_bonus + material_bonus)*(1+(item.quality-2)/8)*1.018**item.size) if 10>item.quality>=0 else int((base_bonus + material_bonus) *0.9*1.015**item.size)
    elif special_rule==-1:
        #抗性专用计算
            for i in final_resistance_dict.keys():
                base_bonus = item.base_resistance.get(i, 0)
                material_bonus = sum((mt.resistance_bonuses.get(i, 0) * parts for mt, parts in item.materials.items()))
                final_resistance_dict[i] = (base_bonus + material_bonus)*1.01**item.size
            return final_resistance_dict
    elif special_rule==-2:
        #价格用公式
        material_bonus=1+sum(mt.quality * parts * parts for mt, parts in item.materials.items())
        base_bonus=item.base_price if item.base_price !=0 else 16*material_bonus+5 if isinstance(item,Equipment) else 0
        final_price=int((base_bonus+0.4*material_bonus)*0.9*1.04**item.size*1.03**material_bonus*(1.15**item.quality)) if 10>=item.quality>0 else int((base_bonus+0.4*material_bonus)*0.9*1.04**item.size*1.03**material_bonus*1.12)
        return max(final_price,0)
    elif special_rule==-3:
        #最大耐久用公式(仅装备)
        material_bonus=1+sum(mt.density/4.3 * parts for mt, parts in item.materials.items())
        base_bonus=item.base_durability/3.15
        final_durability=int(base_bonus*material_bonus*1.27**item.quality*1.03**item.size) if 10>=item.quality>0 else int(base_bonus*material_bonus*1.12*1.03**item.size)
        return final_durability
    
    elif special_rule==1:
        #治疗药水用公式
        base_bonus=item.base_attributes.get('hp_heal', 0)
        material_bonus=sum((mt.bonuses.get('hp_heal', 0) * (parts*parts/max(0.01,1-parts)+7.5*parts+3*(1+parts)**2) for mt, parts in item.materials.items()))
        final_bonus_dict['hp_heal']=int(max(base_bonus+material_bonus,1))
        return final_bonus_dict['hp_heal']
    
    #进行类型特别计算
    if convert_type == 'all':
        if 10>=item.quality>=0:
            for k,i in final_bonus_dict.items():
                if k in ['eva','crit','crit_dmg'] or '*'in k:
                    i*=(1+item.quality/12)
                else:
                    i*=(1+item.quality/12)
                    i=int(i)

    elif convert_type == 'weapon':
        for k,i in final_bonus_dict.items():
            i*=WEAPON_MATERIAL_BONUS.get(k,1)
    elif convert_type == 'armor':
        for k,i in final_bonus_dict.items():
            i*=ARMOR_MATERIAL_BONUS.get(k,1)
    elif convert_type == 'accessory':
        for k,i in final_bonus_dict.items():
            i*=ACCESSORY_MATERIAL_BONUS.get(k,1)
    elif convert_type == 'normal':
        for k,i in final_bonus_dict.items():
            i*=NORMAL_MATERIAL_BONUS.get(k,1)
    elif convert_type == 'legendary':
        for k,i in final_bonus_dict.items():
            i*=LEGENDARY_MATERIAL_BONUS.get(k,1)
    
    for k,v in final_bonus_dict.items():
        if k in ['eva','crit','crit_dmg'] or '*'in k:
           if v<0.01:
               final_bonus_dict[k]=0
        else:
            if -1<v<1:
               final_bonus_dict[k]=0
    return final_bonus_dict
        


        
    

#FIXME:物品基类
class Item(ABC):
    """
    物品类，用于表示游戏中的物品。该类是一个抽象基类，不能直接实例化。
    
    核心功能：
    - 初始化物品的基本属性，如名称、描述、消耗性、价格等。
    - 提供物品的使用、耐久度变化、所有者变更等操作。
    - 支持物品的基本状态获取和显示。
    - 支持物品的堆叠、比较和深拷贝。
    
    使用示例：
    
    构造函数参数：
    - name (str): 物品的名称。
    - description (str): 物品的描述。
    - consumable (bool): 物品是否为消耗品，默认为True。
    - price (int): 物品的价格，默认为0。
    - sellable (bool): 物品是否可出售，默认为True。
    - need_target (bool): 使用物品是否需要目标，默认为True。
    - durability (int): 物品的耐久度，默认为1。
    - max_durability (int): 物品的最大耐久度，默认为1。
    - owner: 物品的所有者，默认为None。
    - is_stackable (bool): 物品是否可堆叠，默认为True。
    - breakable (bool): 物品是否可损坏，默认为True。
    - revealed (bool): 物品是否已揭示，默认为True。
    - materials: 物品的材料组成，默认为None。
    - size (int): 物品的大小，默认为0。
    - weight (int): 物品的重量，默认为0。
    - item_id: 物品的唯一标识符，默认为None。
    - quality (int): 物品的质量，默认为0。
    - **kwargs: 其他可选参数。
    
    特殊限制或副作用：
    - 如果未定义物品ID，将自动使用UUID作为ID。
    - 如果物品的材料占比总和不为100%，将自动调整材料占比。
    - 如果物品的价格为负数，将自动设置为0。
    - 如果物品的耐久度为负数，将自动设置为0。
    - 如果物品的重量为负数，将自动设置为0。
    - 如果物品的所有者与目标相同，将不会更改所有者。
    """
    
    def __init__(self,
                 name: str = None,
                 description: str = None,
                 consumable: bool = True,
                 price: int = 0,
                 sellable: bool = True,
                 need_target: bool = True,
                 durability: int = 1,
                 max_durability: int = 1,
                 owner=None,
                 is_stackable=True,
                 breakable=True,
                 revealed=True,
                 materials=None,
                 size=1,
                 weight=0,
                 item_id=0,
                 quality=0,
                 base_attributes=None,
                 base_resistance=None,
                 convert_type='normal',
                 attributes_affected_by_material=False,
                 upgrade_level=0,
                 prefix=None,
                 **kwargs):
        self.name = name
        self.prefix=prefix
        self.item_id = item_id
        self.description = description
        self.consumable = consumable
        self.sellable = sellable
        self.base_price=price #用于计算价格
        self.price = price #最终价格
        self.need_target = need_target
        self.quality = quality
        self.base_durability=durability #用于计算耐久度
        self.durability = durability #最终耐久度
        self.max_durability = max_durability
        self.owner=owner
        self.is_stackable=is_stackable
        self.breakable=breakable
        self.revealed=revealed
        self.materials=materials
        self.size=size
        self.weight=weight
        self.base_attributes=base_attributes
        self.base_resistance=base_resistance
        self.convert_type=convert_type
        self.attributes_affected_by_material=attributes_affected_by_material
        self.upgrade_level=upgrade_level
        self.uuid=uuid.uuid4()
        #输入偏差的修正(如复数)
        self.materials=kwargs.get('material',self.materials)
        self.base_attributes=kwargs.get('base_attribute',self.base_attributes)
        self.base_resistance=kwargs.get('base_resistances',self.base_resistance)

        #处理未定义基础属性
        if not self.base_attributes:
            self.base_attributes = {i: 0 for i in ALL_BONUS}
        self.final_attributes=self.base_attributes
        #处理未定义基础抗性
        if not self.base_resistance:
            self.base_resistance = {i: 0 for i in ALL_RESISTANCE}
        self.final_resistance=self.base_resistance
        #处理无意义前缀(注:前缀格式:{前缀名:等级})
        if not self.prefix:
            self.prefix={}
        #处理无意义图鉴ID
        #无意义物品，直接返回
        if not (self.item_id or self.name):
            self.name='未知物品'
            self.item_id=0
            self.quality=0
            self.materials = {m_Unknown: 1}
            return 
        #有ID物品，检查ID表
        if self.item_id not in ITEM_ID:
            if self.name:
                ITEM_ID[self.item_id]=self.name
            else:
                ITEM_ID[self.item_id]=f"不知名物品"
            debug_log.log_error(f"物品{self.name}不在ID表中,已自动添加到ID表中:{self.item_id}")
        #处理品质
        if not self.quality:
            self.quality=0
        #处理物品名(根据ID)
        if not self.name:
            self.name=convert_colorful_text(f"{ITEM_ID.get(self.item_id,'未知物品')}", get_quality_color(self.quality))
        # 处理负数价格
        self.price = max(0, self.price)
        # 处理无意义耐久度
        self.max_durability = max(1, self.max_durability)
        self.durability = min(self.durability, self.max_durability)
        # 处理未定义材料
        mt_sums = 0
        if not self.materials:
            self.materials = {m_Unknown: 1}
        btmp={}
        for key, value in self.materials.items():
            if 0 < value:
                mt_sums += value
                btmp[key] = value
        self.materials = btmp
        if mt_sums > 0 and mt_sums != 1:
            debug_log.log_error(f"尝试修正物品{self.name}的材料占比")
            # 处理材料占比总和不为100%的情况
            btmp={}
            for key, value in self.materials.items():
                btmp[key] = value / mt_sums
            self.materials = btmp
            debug_log.log_debug(f"尝试修正后物品{self.name}的材料占比为{self.materials}")
        # 处理未定义大小和重量
        if self.size < 0:
            self.size = 1
        if self.weight <= 0:
            for key,value in self.materials.items():
                self.weight += key.density * value * size
            weight=max(0,weight)
        #根据材料重处理物品名(如果没有被初始命名而是被以ID取名)
        if self.materials and not name:
            mts=sorted(self.materials.items(),key=lambda x:x[1],reverse=True)
            mtss=[]
            prfs=[]
            if len(self.prefix)>2:
                prfs=['♢多前缀']
            else:
                for key,value in self.prefix.items():
                    prfs.append(f"{key}{value}")
                
            if len(mts)>2:
                mtss=['♢复合构成',mts[0][0]]
            else:
                for key,value in mts:
                    mtss.append(f"{key}")
            self.name=f"{' '.join(prfs)+'-'.join(mtss)}"+'的 '+f"{convert_colorful_text(self.name,get_quality_color(self.quality))} {convert_colorful_text(f'self.upgrade_level:+d',get_quality_color(self.upgrade_level))}"
        
        #处理默认下最终属性和价格
        if self.attributes_affected_by_material:
            if not isinstance(self,Equipment):
                self.final_attributes=self.base_attributes
            else:
                self.final_attributes = material_bonus_cal(self,convert_type=self.convert_type)
            self.final_resistance = material_bonus_cal(self,special_rule=-1)
            self.price=material_bonus_cal(self,special_rule=-2)
            if self.price<self.base_price:
                self.base_price=self.price
            atmp=self.max_durability
            self.max_durability = material_bonus_cal(self,special_rule=-3)+1
            if self.max_durability<self.base_durability:
                self.base_durability=self.max_durability
            if atmp==self.durability:
                self.durability=self.max_durability
            

    @abstractmethod
    def use(self, target: 'Character' = None) -> int:
        """使用物品的抽象方法"""
        pass

    def rename(self, new_name: str):
        """重命名物品"""
        self.name=new_name
        return self.name
    
    def re_ini_name(self,mode='prior_id'):
        if mode=='prior_id':
            self.name=convert_colorful_text(f"{ITEM_ID.get(self.item_id,'未知物品')}", get_quality_color(self.quality))
            if not ITEM_ID.get(self.item_id):
                mode='prior_material'
        
        if mode!='prior_id':
            """按照初始化的重命名方法进行重命名"""
            mts=sorted(self.materials.items(),key=lambda x:x[1],reverse=True)
            mtss=[]
            prfs=[]
            if len(self.prefix)>2:
                prfs=['♢多前缀 ']
            else:
                for key,value in self.prefix.items():
                    prfs.append(f"{key}{value} ")
                
            if len(mts)>2:
                mtss=['♢复合构成',f'{mts[0][0]}']
            else:
                for key,value in mts:
                    mtss.append(f"{key}")
            self.name=f"{''.join(prfs)+'-'.join(mtss)}"+'的 '+f"{convert_colorful_text(self.name,get_quality_color(self.quality))}"
            if self.upgrade_level:
                self.name+=f'{convert_colorful_text(f'{self.upgrade_level:+d}',get_quality_color(self.upgrade_level))}'
        return self.name
    
    def re_cal_material_bonus(self):
        if self.attributes_affected_by_material:
            if not isinstance(self,Equipment):
                self.final_attributes=self.base_attributes
            else:
                self.final_attributes = material_bonus_cal(self,convert_type=self.convert_type)
            self.final_resistance = material_bonus_cal(self,special_rule=-1)
            self.price=material_bonus_cal(self,special_rule=-2)
            if self.price<self.base_price:
                self.base_price=self.price
            atmp=self.max_durability
            self.max_durability = material_bonus_cal(self,special_rule=-3)+1
            if self.max_durability<self.base_durability:
                self.base_durability=self.max_durability
            if atmp==self.durability:
                self.durability=self.max_durability
    
    def owner_change(self,target: 'Character' = None):
        if target == self.owner:
            print(USE_ITEM_ERROR_MESSAGES[-9])
        else:
            self.owner=target   

    def reveal(self):
        self.revealed=True
            

    def get_basic_status(self, mode='display',checker:'Character'=None):
        if not checker:
            checker=Character(name="未知观察者")
        if not self.owner:
            self.owner=Character(name="未知物主")
        if mode == 'display':
            if not self.revealed:
                ret=[]
                ret.append(f"{ORANGE}<?>未揭示的物品{RESET}:尝试{GREEN}鉴定{RESET}此物品以揭示 |大小:{get_float_val_color(1-(self.size/20))}{self.size}{RESET}|重量:{get_float_val_color(1-(self.weight/75))}{self.weight:.1f}{RESET}\n")
                known_materials=[]
                for key in self.materials:
                    if checker.knowledge.check(key):
                        known_materials.append(f"{key}")
                if known_materials:
                    ret.append(f"{YELLOW}*{RESET}你知道它的一些构成材料:{','.join(known_materials)} ")
                if checker.knowledge.check(self):
                    ret.append(f"{GREEN}**{RESET}你知道它是{self} ")
                else:
                    ret.append(f"{RED}***{RESET}你完全不知道它是什么")
                return ''.join(ret)


            status_parts = [f'ID:{self.item_id} |{convert_colorful_text(self.name, get_quality_color(self.quality))}:{self.description}']
            status_parts.append(f'|持有者:{self.owner} |大小:{get_float_val_color(1-(self.size/20))}{self.size}{RESET}|重量:{get_float_val_color(1-(self.weight/75))}{self.weight:.1f}{RESET}\n')
            if checker!=self.owner:
                    return ' '.join(status_parts)
            for k,v in self.final_attributes.items():
                if v!=0:
                    color = RED if v < 0 else GREEN
                    status_parts.append(f'|{BLUE}效果{RESET}:{k.upper()}:{color}{v:.2f}{RESET}')
            for k,v in self.final_resistance.items():
                if v!=0:
                    color = RED if v < 0 else GREEN
                    status_parts.append(f'|{ORANGE}抗性{RESET}:{k.upper()}:{color}{v*100:.2f}{RESET}%')
            status_parts.append('\n')
            if self.sellable:
                status_parts.append(f'|{YELLOW}价格:{self.price}{RESET}')
            else:
                status_parts.append(f'|{RED}不可出售{RESET}')
            
            # 耐久
            if self.breakable:
                durability_ratio = self.durability / self.max_durability
                if durability_ratio > 0.75:
                    durability_color = GREEN
                elif durability_ratio > 0.5:
                    durability_color = YELLOW
                elif durability_ratio > 0.25:
                    durability_color = MAGENTA
                else:
                    durability_color = RED
                
                if isinstance(self, Equipment):
                    status_parts.append(f'|耐久 {durability_color}{self.durability}/{self.max_durability}{RESET}')
                else:
                    status_parts.append(f'|使用次数 {durability_color}{self.durability}/{self.max_durability}{RESET}')
            
            else:
                status_parts[-1]=f"{ORANGE}| ★ 永不损毁{RESET}"
                
            status_parts.append(f'||材质:')
            for key,value in self.materials.items():
                status_parts.append(f'{key} ({value*100:.1f}%)')
                
            return ' '.join(status_parts)
        else:
            return {
                'name': self.name,
                'description': self.description,
                'consumable': self.consumable,
                'sellable': self.sellable,
                'price': self.price,
                'quality': self.quality,
                'need_target': self.need_target,
                'durability': self.durability,
                'max_durability': self.max_durability,
                'owner': self.owner,
                'is_stackable': self.is_stackable,
                'breakable': self.breakable,
                'revealed': self.revealed
            }

    def show(self):
        print(self.get_basic_status(mode='display',checker=self.owner))

    def durability_down(self, value: int = 1):
        if not self.breakable:
            return self
        self.durability = max(0, self.durability - value)
        if self.durability <= 0:
            
            if isinstance(self, Equipment):
                if self.equipper:
                    self.equipper.unequip_item(self)
                print(f"{self} {YELLOW}已损毁{RESET}.")
                debug_log.log_debug(f"{self.get_basic_status()} 已损毁.|UUID:{self.uuid}")
                self.owner.inventory.remove_item(self)
            else:
                print(f"1个 {self} {YELLOW}已用尽{RESET}.")
                debug_log.log_debug(f"1个{self.get_basic_status()} 已用尽.|UUID:{self.uuid}")
            return None
        else:
            return self

    def durability_up(self, value: int = 1):
        self.durability = min(self.max_durability, self.durability + value)


        

    def __str__(self) -> str:
        return self.name 

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        if self.is_stackable:
            self_dict = {k: v for k, v in self.__dict__.items() if k not in ['uuid', 'name', 'description']}
            other_dict = {k: v for k, v in other.__dict__.items() if k not in ['uuid', 'name', 'description']}
            return self_dict == other_dict
        else:
            return self.uuid == other.uuid

    def __lt__(self, other):  # 默认按字典序
        if isinstance(other, Item):
            return self.name < other.name
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __deepcopy__(self, memo):
        # 创建一个新的实例，不传递参数
        new_item = self.__class__()
        # 复制所有属性
        for key, value in self.__dict__.items():
            if key not in  ['uuid']:  # 排除uuid，因为它需要是唯一的
                setattr(new_item, key, copy.deepcopy(value, memo))
            if key in ['owner','equipper']:
                if value:
                    setattr(new_item, key, value.copy_with_same_uuid())
                else:
                    setattr(new_item, key, None)
        # 为新实例生成新的UUID
        new_item.uuid = uuid.uuid4()
        return new_item
class No_item(Item):
    #ID: 0
    """
    无物品类，继承自Item类，用于表示无物品的情况。
    """
    def __init__(self,**kwargs):
        """
        初始化无物品对象。
        """
        super().__init__(
            name='无物品',
            description='无物品(测试用)',
            consumable=False,
            price=0,
            sellable=False,
            quality=-1
        )
    def use(self, target: 'Character' = None) -> int:
        """
        使用无物品，由于无物品不可使用，因此打印提示信息并返回-1。
        
        :param target: 目标角色，默认为None
        :return: 始终返回-1
        """
        return -1

#FIXME:装备子基类,作为Weapon,Armor等子类的基类
class Equipment(Item):
    """
    Equipment类表示游戏中的装备物品，继承自Item类。
    
    该类用于表示各种装备，如武器、防具等，具有装备类型、加成、抗性、特殊效果等属性。
    核心功能包括装备和卸下装备，以及获取装备的基本状态信息。
    
    构造函数参数:
    - equipment_type (str): 装备的类型，默认为'none_test'。
    - bonuses (dict): 装备提供的属性加成，默认为空字典。
    - resistances (dict): 装备提供的抗性，默认为空字典。
    - spe_effect_id (int): 特殊效果的ID，默认为0。
    - is_equipped (bool): 装备是否已装备，默认为False。
    - equipper ('Character'): 装备的持有者，默认为None。
    - **kwargs: 其他继承自Item类的参数。
    
    使用示例:
    
    注意事项:
    - 如果装备已装备，调用use方法会卸下装备。
    - 如果装备未装备，调用use方法会装备装备。
    - 装备的持有者必须是一个Character实例。
    """
    
    def __init__(
        self,
        equipment_type: str = 'none_test',
        spe_effect_id: int = 0,
        is_equipped: bool = False,
        equipper: 'Character' = None,
        **kwargs):
        kwargs['is_stackable'] = False
        kwargs['durability'] = kwargs.get('durability', 100)
        kwargs['max_durability'] = kwargs.get('max_durability', 100)
        
        super().__init__(**kwargs)
        self.equipment_type = equipment_type
        self.convert_type=self.equipment_type
        self.bonuses = self.final_attributes
        #print(self.bonuses)
        self.resistances = self.final_resistance
        self.spe_effect_id = spe_effect_id
        self.is_equipped = is_equipped
        self.equipper= equipper
        
        #处理装备状态与装备者的统一
        if not (self.is_equipped and self.equipper):
            self.equipper=None
            self.is_equipped=False
            
    def use(self, target:'Character'=None) -> int:
        if target is None:
            target=self.equipper
        if target is None and self.is_equipped:
            return -20
        if target is None and not self.is_equipped:
            target = self.owner
        if target is None:
            return -21
        if self.is_equipped:
            state = target.unequip_item(self)
            if state == 1:
                print(f"{target}卸下了 {self}")
                self.equipper=None
        else:
            state = target.equip_item(self)
            if state == 1:
                print(f"{target}装备了 {self}")
                self.equipper=target
        return state

    def get_basic_status(self, mode='display', checker=None):
        if not checker:
            checker = Character(name="未知观察者")
        if not self.owner:
            self.owner = Character(name="未知物主")
        
        if mode == 'display':
            if not self.revealed:
                ret = []
                ret.append(f"{ORANGE}<?>未揭示的物品{RESET}:尝试{GREEN}鉴定{RESET}此物品以揭示 |大小:{get_float_val_color(1-(self.size/20))}{self.size}{RESET}|重量:{get_float_val_color(1-(self.weight/75))}{self.weight:.1f}{RESET}\n")
                known_materials = []
                for key in self.materials:
                    if checker.knowledge.check(key):
                        known_materials.append(f"{key}")
                if known_materials:
                    ret.append(f"{YELLOW}*{RESET}你知道它的一些构成材料:{','.join(known_materials)}")
                if checker.knowledge.check(self):
                    ret.append(f"{GREEN}**{RESET}你知道它是{self}")
                else:
                    ret.append(f"{RED}***{RESET}你完全不知道它是什么")
                return ''.join(ret)
            
            if self.equipment_type == 'none_test':
                return '无'
            
            status_parts = [f'{convert_colorful_text(self.name, get_quality_color(self.quality))}:{self.description}']
            
            # 持有者
            status_parts.append(f'||持有者 {self.owner} |大小:{get_float_val_color(1-(self.size/20))}{self.size}{RESET}|重量:{get_float_val_color(1-(self.weight/75))}{self.weight:.1f}{RESET}')
            if self.is_equipped:
                status_parts.append(f' |<{self.equipper}>已装备')
            if checker != self.owner:
                return ' '.join(status_parts)
            status_parts.append(f'\n')
            
            for bonus, value in self.bonuses.items():
                if value == 0: continue
                color = RED if value < 0 else GREEN
                if bonus in ['crit', 'crit_dmg', 'eva'] or '*' in bonus:
                    status_parts.append(f'|属性:{bonus.upper()} {color}{value*100:.2f}%{RESET}')
                else:   
                    status_parts.append(f'|属性:{bonus.upper()} {color}{value:.0f}{RESET}')
            
            for resistance, value in self.resistances.items():
                if value == 0: continue
                color = RED if value < 0 else GREEN
                status_parts.append(f'|抗性:{resistance.upper()} {color}{value*100:+.2f}%{RESET}')
        
            # 特殊效果
            if self.spe_effect_id != 0:
                status_parts.append(f'|特殊效果 {CYAN}{SPE_EFFECT_ID[self.spe_effect_id]}{RESET}')
            status_parts.append(f'\n')
            
            # 耐久
            if self.breakable:
                durability_ratio = self.durability / self.max_durability
                if durability_ratio > 0.75:
                    durability_color = GREEN
                elif durability_ratio > 0.5:
                    durability_color = YELLOW
                elif durability_ratio > 0.25:
                    durability_color = MAGENTA
                else:
                    durability_color = RED
                status_parts.append(f'|耐久 {durability_color}{self.durability}/{self.max_durability}{RESET}')
            else:
                status_parts.append(f'||{ORANGE}★ 永不损毁{RESET}')
            
            if self.sellable:
                status_parts.append(f'|{YELLOW}价格:{self.price}{RESET}')
            else:
                status_parts.append(f'|{RED}不可出售{RESET}')
            
            status_parts.append(f'||材质：')
            for key, value in self.materials.items():
                status_parts.append(f'{key} ({value*100:.1f}%)')
                
            return ' '.join(status_parts)
        else:
            return {
                'name': self.name,
                'description': self.description,
                'bonuses': self.bonuses,
                'resistances': self.resistances,
                'spe_effect_id': self.spe_effect_id,
                'durability': self.durability,
                'max_durability': self.max_durability,
                'quality': self.quality,
                'equipment_type': self.equipment_type,
                'is_equipped': self.is_equipped,
                'equipper': self.equipper,
                'owner': self.owner,
            }

    def get_detailed_status(self,*args, **kwargs):
        return self.get_basic_status(checker=self.owner)

#FIXME:技能类
class Skill:
    def __init__(self,
                effect,
                quality:int=0,
                 skill_id:int=0,
                 name:str='不知名技能',
                 description:str='无',
                 cost:dict=None,
                 skill_type:str='active',
                 **kwargs):
        if not cost:
            cost={}
        self.name = name
        self.description = description
        self.skill_id = skill_id
        self.effect = effect
        self.cost = cost
        self.quality=quality
        self.skill_type = skill_type
        
        #处理技能ID(根据ID)
        if self.skill_id not in SKILL_ID:
            if self.name:
                SKILL_ID[self.skill_id]=self.name
                if not self.name:
                    SKILL_ID[self.skill_id]=f"不知名技能"
            else:
                SKILL_ID[self.skill_id]=len(SKILL_ID)+1
            debug_log.log_error(f"技能{self.name}不在ID表中,已自动添加到ID表中:{self.skill_id}")

        

    def get_basic_status(self, mode='display',checker=None):
        if mode == 'display':
            return f'{convert_colorful_text(self.name, get_quality_color(self.quality))}:{self.description}'
        else:
            return {
                'name': self.name,
                'description': self.description,
                'effect': self.effect,
                'cost': self.cost,
            }


    def __str__(self) -> str:
        return f'{convert_colorful_text(self.name, get_quality_color(self.quality))}'

    def __eq__(self, other):
        if not isinstance(other, Skill):
            return False
        return self.skill_id == other.skill_id

    def __lt__(self, other):
        if not isinstance(other, Skill):
            return NotImplemented
        return self.skill_id < other.skill_id

    def __hash__(self):
        return hash(self.skill_id)
#FIXME:主动技能
class ActiveSkill(Skill):
    def __init__(self,cooldown:int=0,scope:SkillScope=SkillScope.NONE,**kwargs):
        super().__init__(**kwargs)
        self.cooldown=cooldown
        self.scope=scope
        self.skill_type='active'
        self.cur_cooldown=0
    
    @abstractmethod
    def use(self, caster, targets: List['Character'], battle_system):
        pass
#FIXME:被动技能
class PassiveSkill(Skill):
    def __init__(self,bonuses:Dict[str,float],resistances:Dict[str,float],phase:Phase=Phase.NONE,**kwargs):
        super().__init__(**kwargs)
        self.bonuses=bonuses
        self.resistances=resistances
        self.phase=phase
        self.skill_type='passive'

    @abstractmethod
    def use(self, caster, targets: List['Character'], battle_system):
        pass
    


#FIXME:图鉴类
class illustrated_handbook:
    def __init__(self,owner,**kwargs):
        self.materials = {}
        self.skills = {}
        self.items = {}
        self.owner=owner

    def learn(self,object):
        if not object:
            return
        if isinstance(object, Skill):
            self.skills[object.skill_id]=object
        elif isinstance(object, Item):
            self.items[object.item_id]=object
        elif isinstance(object, Material):
            self.materials[object.material_id]=object
        print(f"{self.owner}学习到了{object.name}的一些鉴定知识")
        debug_log.log_debug(f"<Iv:learn>{self.owner}学习了{object.name}")

    def forget(self,object):
        if not object:
            return
        if isinstance(object, Skill):
            del self.skills[object.skill_id]
        elif isinstance(object, Item):
            del self.items[object.item_id]
        elif isinstance(object, Material):
            del self.materials[object.material_id]
        print(f"{self.owner}遗忘了一些鉴定知识")
        debug_log.log_debug(f"<Iv:forget>{self.owner}遗忘了{object.name}")

    def check(self,object):
        if not object:
            return False
        if isinstance(object, Skill):
            return object.skill_id in self.skills
        elif isinstance(object, Item):
            return object.item_id in self.items
        elif isinstance(object, Material):
            return object.material_id in self.materials
        return False

    def show(self,type:str='item'):
        if type=='skill':
            print(f"{self.owner}的技能图鉴:")
            for skill_id in self.skills:
                if self.skills[skill_id]:
                    print(self.skills[skill_id].get_basic_status())
        elif type=='item':
            print(f"{self.owner}的物品图鉴:")
            for item_id in self.items:
                if self.items[item_id]:
                    print(self.items[item_id].get_basic_status())
        elif type=='material':
            print(f"{self.owner}的素材图鉴:")
            for material_id in self.materials:
                if self.materials[material_id]:
                    self.materials[material_id].show_status()


#FIXME:仓库类
class Inventory_improved:
    auto_sort_count=0

    def __init__(self,owner= None):

        self.subinventories = defaultdict(self.Subinventory)
        self.owner = owner
        self.max_size=100
        self.max_weight=500
        self.current_size=0
        self.current_weight=0
        
    class Subinventory:
        

        def __init__(self):
            self.items = SortedList() #格式:(特殊值,物品,数量)
        
        def _get_sort_key(self, item) ->int :
            # 根据物品类型定义排序规则
            sort_key = INV_SORT_METHODS.get(type(item).__name__)
            debug_log.log_debug(f"<Iv:Subiv:_get_sort_key>获取到{type(item).__name__}的排序键:{sort_key}")
            return getattr(item, sort_key, 0) if sort_key else 0               # 其他物品不排序
            
        def add_item(self, item: Item, quantity: int = 1) -> None:
            if quantity <= 0:
                return

            sort_key = self._get_sort_key(item)
            idx = self.items.bisect_left((sort_key, item, 0))
            if idx < len(self.items) and self.items[idx][1] == item:
                existing_item = self.items[idx]
                new_quantity = existing_item[2] + quantity
                del self.items[idx]
                self.items.add((sort_key, item, new_quantity))
            else:
                self.items.add((sort_key, item, quantity))

        def remove_item(self, item: Item, quantity: int = 1) -> None:
            if quantity <= 0:
                return

            sort_key = self._get_sort_key(item)
            idx = self.items.bisect_left((sort_key, item, 0))
            
            # 向左和向右查找匹配的物品
            while idx < len(self.items) and self.items[idx][0] == sort_key:
                if self.items[idx][1] == item:
                    existing_item = self.items[idx]
                    new_quantity = existing_item[2] - quantity
                    if new_quantity > 0:
                        del self.items[idx]
                        self.items.add((sort_key, item, new_quantity))
                    else:
                        del self.items[idx]
                    return
                idx += 1
        
        def catch_item(self, item: Item, quantity: int = 1) -> list:
            """
            从库存中拿取物品。

            参数：
            item (Item): 要拿取的物品实例
            quantity (int): 拿取的数量，默认为1
            """
            sort_key = self._get_sort_key(item)
            idx = self.items.bisect_left((sort_key, item, 0))
            if idx < len(self.items) and self.items[idx][1] == item:
                _, existing_item, existing_qty = self.items[idx]
                if existing_qty <= quantity:
                    del self.items[idx]
                else:
                    del self.items[idx]
                    self.items.add((sort_key, item, existing_qty - quantity))
                return [existing_item for _ in range(min(max(quantity, 0), existing_qty))]
            else:
                return []

        def find_closet(self, target_val: int = 0) -> list:
            """
            查找最接近目标值的物品。

            参数：
            target_val (int): 目标值，默认为0

            返回：
            list: 最接近目标值的物品列表
            """
            idx = self.items.bisect_left((target_val, None, 0))
            candidates = []
            if idx < len(self.items):
                candidates.append(self.items[idx])
            if idx > 0:
                candidates.append(self.items[idx - 1])
            return candidates
        
        def get_all(self, mode: str = 'all') -> list:
            """
            获取所有物品的视图。

            参数：
            mode (str): 视图模式，默认为'all'，可选值为'all'、'display'、'all_items'

            返回：
            list: 物品视图列表
            """
            if mode == 'all':
                return list(self.items)
            elif mode == 'display':
                return [f"{item.name} *{qty}" for _, item, qty in self.items]
            else:  # all_items
                return list(chain.from_iterable(
                    [item] * qty for _, item, qty in self.items
                ))

        def get_exact_item(self, spe_val: int = 0, uuid: str = None) -> Item:
            """
            获取特定物品。

            参数：
            - spe_val (int): 特殊值，默认为0
            - uuid (str): 物品UUID，默认为None

            返回：
            Item: 物品实例，如果未找到则返回None
            """
            if uuid is not None:
                for _, item, _ in self.items:
                    if item.uuid == uuid:
                        return item
                return None
            else:
                nums = [sort_key for sort_key, _, _ in self.items]
                idx = self.items.bisect_left((spe_val, None, 0))
                if idx < len(nums) and nums[idx] == spe_val:
                    return self.items[idx][1]
                else:
                    return None
                
        def auto_sort(self):
            if len(self.items) < 10:
                return
            if not self.items[0][1].is_stackable:
                return

            sorted_items = []
            current_item = self.items[0]
            count = self.items[0][2]

            for i in range(1, len(self.items)):
                if current_item[1] == self.items[i][1]:
                    count += self.items[i][2]
                else:
                    sorted_items.append((current_item[0], current_item[1], count))
                    current_item = self.items[i]
                    count = self.items[i][2]

            # 添加最后一个项目
            sorted_items.append((current_item[0], current_item[1], count))

            # 使用新的已排序项目列表重新创建 SortedList
            self.items = SortedList(sorted_items)
            
    def sub_sort(self,item_type = None):
        if not item_type:
            for i in self.subinventories:
                self.subinventories[i].auto_sort()
            return
        return self.subinventories[item_type].auto_sort()

    
    def idxit(self,item_type,idx):
        #判断
        if item_type not in self.subinventories:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-6])
            return None
        elif len(self.subinventories[item_type].items)<=idx:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-31])
            return None
        #执行
        debug_log.log_debug(f"<Iv:idxit>{self.owner.name}背包{item_type.__name__}索引{idx}物品{self.subinventories[item_type].items[idx][1].name}||UUID:{self.subinventories[item_type].items[idx][1].uuid}\n")
        return self.subinventories[item_type].items[idx][1]
    
    def add_item(self, item: Item, quantity: int = 1) -> list[Item]:
        #返回实际添加的复制品的实例
        debug_log.log_debug(f"<Iv:add_item>{self.owner}的背包添加物品方法被调用:{item.name} *{quantity}")
        #判断
        if not item:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-2])
            return [No_item()]
        if not item.owner:
            item.owner=self.owner
        if item.size*quantity+self.current_size>self.max_size:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-25])
            print(USE_ITEM_ERROR_MESSAGES[-25])
            return [No_item()]
        if item.size>self.max_size:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-26])
            print(USE_ITEM_ERROR_MESSAGES[-26])
            return [No_item()]
        if item.weight*quantity+self.current_weight>self.max_weight:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-27])
            print(USE_ITEM_ERROR_MESSAGES[-27])
            return [No_item()]
        if item.weight>self.max_weight:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-28])
            print(USE_ITEM_ERROR_MESSAGES[-28])
            return [No_item()]
            
        #仓库整理
        Inventory_improved.auto_sort_count+=1
        if Inventory_improved.auto_sort_count>=100:
            debug_log.log_info("<Iv:add_item>仓库自动整理")
            self.sub_sort()
            Inventory_improved.auto_sort_count=0
            
        #执行
        debug_log.log_debug(f"<Iv:add_item>物品堆叠?:{item.is_stackable}")
        added_items = []
        if item.is_stackable:
            self.subinventories[type(item)].add_item(item, quantity)
            added_items.extend([item] * quantity)
        else:
            for i in range(quantity):
                new_item = copy.deepcopy(item)
                new_item.owner=item.owner
                self.subinventories[type(item)].add_item(new_item, 1)
                added_items.append(new_item)
        self.current_size+=item.size*quantity
        self.current_weight+=item.weight*quantity
        debug_log.log_debug(f"<Iv:add_item>{self.owner.name}的背包添加了物品{item.name} *{quantity}||UUID:{item.uuid}\n")
        return added_items
        
    
    def remove_item(self, item: Item, quantity: int = 1) -> None:
        #判断
        if not item:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-2])
            return
        if isinstance(item, Equipment):
            if item.is_equipped:
                debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-18])
                return 
        #执行
        self.subinventories[type(item)].remove_item(item, quantity)
        if not self.subinventories[type(item)].items:
            del self.subinventories[type(item)]
        self.current_size-=item.size*quantity
        self.current_weight-=item.weight*quantity
        debug_log.log_debug(f"<Iv:remove_item>{self.owner.name}的背包移除了物品{item.name} *{quantity}\n")
        return

    def catch_remove_item(self, item: Item, quantity: int = 1) -> None:
        debug_log.log_debug(f"<Iv:catch_remove_item>{self.owner.name}的背包抓取移除物品方法被调用:{item.name} *{quantity}")
        #判断
        if not item:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-2])
            return
        if isinstance(item, Equipment):
            if item.is_equipped:
                debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-18])
                return 
        #执行
        catched=self.subinventories[type(item)].catch_item(item, quantity)
        if catched:
            for i in range(len(catched)):
                itemcp=copy.deepcopy(catched[i])
                itemcp.owner=None
                catched[i]=itemcp
            debug_log.log_debug(f"<Iv:catch_remove_item>{self.owner.name}的背包抓取了物品{item.name} *{quantity}")
            debug_log.log_debug(f"<Iv:catch_remove_item>物品列表:\n"+f"{i.name}||UUID:{i.uuid}" for i in catched +'\n')
            self.current_size-=item.size*quantity
            self.current_weight-=item.weight*quantity
            if not self.subinventories[type(item)].items:
                del self.subinventories[type(item)]
        else:
            debug_log.log_debug(f"<Iv:catch_remove_item>{self.owner.name}的背包没有抓取到物品{item.name}\n")
        return catched
    
    def get_items(self, item_type: type, spe_val: int = None, mode='all') ->list:
        """
        获取特定类型的物品。

        参数：
        item_type (type): 物品类型
        spe_val (int): 特殊值，默认为None
        mode (str): 视图模式，默认为'all'，可选值为'all'、'display'、'all_items'

        返回：
        list: 物品列表
        """
        #判断
        if item_type not in self.subinventories:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-6])
            return []
        debug_log.log_debug(f"<Iv:get_items>{self.owner.name}get_items: {item_type} {spe_val} {mode}方法被调用")
        sub_inv=self.subinventories[item_type]
        ret=[]
        if spe_val is None:
            if mode=='all':
                ret=[{
                    'value': c[0],
                    'item': c[1],
                    'quantity': c[2],
                    'description': c[1].description
                    } for c in sub_inv.get_all('all')
                ]
            else:
                ret= sub_inv.get_all(mode)
        else:
            if mode=='display':
                ret=[{
                    '名称': c[1].name,
                    '描述': c[1].description,
                    '耐久': f'{c[1].durability}/{c[1].max_durability}',
                    '数量': c[2],
                    '价格': c[1].price,
                    '可出售?': c[1].sellable,
                    } for c in sub_inv.find_closet(spe_val)
                ]
            else:
                ret=[{
                    'value': c[0],
                    'item': c[1],
                    'quantity': c[2],
                    'description': c[1].description
                } for c in sub_inv.find_closet(spe_val)
                ]
        debug_log.log_debug(f"<Iv:get_items>返回{ret}\n")
        return ret
        
    def get_exact_item(self, spe_val: int = None, item_type: type = None, item: Item = None, uuid: str = None) -> Item:
        """
        获取特定物品。

        参数：
        - spe_val (int): 特殊值，默认为None
        - item_type (type): 物品类型，默认为None
        - item (Item): 物品实例，默认为None
        - uuid (str): 物品UUID，默认为None

        返回：
        - Item: 物品实例，如果未找到则返回None
        """
        debug_log.log_debug(f"<Iv:get_exact_item>{self.owner.name}get_exact_item: {spe_val} {item_type} {item} {uuid} 方法被调用")
        ret = None

        if spe_val is not None and item_type is not None:
            ret = self.subinventories[item_type].get_exact_item(spe_val=spe_val)
        elif item is not None:
            item_type = type(item)
            ret = self.subinventories[item_type].get_exact_item(uuid=item.uuid)
        elif uuid is not None:
            for subinventory in self.subinventories.values():
                ret = subinventory.get_exact_item(uuid=uuid)
                if ret is not None:
                    break
        else:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-7])

        debug_log.log_debug(f"<Iv:get_exact_item>返回{ret}\n")
        return ret

    
    def get_all_items_view(self, mode: str = 'display') -> list:
        """
        获取所有物品的视图。

        参数：
        mode (str): 视图模式，默认为'display'，可选值为'display'、'all'

        返回：
        list: 物品视图列表
        """
        debug_log.log_debug(f"<Iv:get_all_items_view>{self.owner.name}get_all_items_view: {mode}方法被调用")
        ret=[]
        if mode == 'display':
            ret= [f"{item_type().__str__()} <{len(self.subinventories[item_type].items)}>" for item_type in self.subinventories.keys()]
        elif mode == 'all':
            ret= [item for item in self.subinventories.values()]
        else:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-32])
        debug_log.log_debug(f"<Iv:get_all_items_view>返回{ret}\n")
        return ret

            
    def show_items_types(self, mode:str = 'all') -> list:
        """
        显示所有物品类型。

        参数：
        mode (str): 视图模式，默认为'all'，可选值为'all'、'display'

        返回：
        list: 物品类型列表
        """
        debug_log.log_debug(f"<Iv:show_items_types>{self.owner.name}show_items_types: {mode}方法被调用")
        ret=[]
        if mode=='all':
            ret= list(self.subinventories.keys())
        else:#display
            ret= [f"{item_type.__name__} <{len(self.subinventories[item_type].items)}>" for item_type in self.subinventories.keys()]

        debug_log.log_debug(f"<Iv:show_items_types>返回{ret}\n")
        return ret
       
    def show_inventory(self,item_type=None,checker:'Character'=None,display_mode='undetailed'):
        debug_log.log_debug(f"<Iv:show_inventory>{self.owner}show_inventory: {item_type}方法被调用")
        debug_log.log_debug(f"{self.owner}的背包: |空间<{self.current_size}/{max(1,self.max_size)}>|负重<{self.current_weight}/{max(1,self.max_weight)}>|")
        print(f"\n{self.owner}的背包: |空间<{get_float_val_color(1-(self.current_size/self.max_size))}{self.current_size:.1f}{RESET}/{self.max_size:.1f}>|负重<{get_float_val_color(1-(self.current_weight/self.max_weight))}{self.current_weight:.1f}{RESET}/{self.max_weight:.1f}>|")
        if not self.subinventories.keys():
            debug_log.log_debug(f"{self.owner}的背包是空的。")
            print(f"{YELLOW}空空如也{RESET}\n")
        elif item_type is None:
            for item_type in self.subinventories.keys():
                if item_type(item_id=0).is_stackable:
                    debug_log.log_debug(f"{item_type.__name__} <{len(self.subinventories[item_type].items)}:{sum([item[2] for item in self.subinventories[item_type].items])}>:")
                    print(f"{item_type.__name__} <{len(self.subinventories[item_type].items)}:{sum([item[2] for item in self.subinventories[item_type].items])}>:")
                    if len(self.subinventories[item_type].items)<300:
                        self.sub_sort(item_type)
                    else:
                        print(f"{item_type.__name__}类物品过多，建议清理不想要的物品")
                else:
                    debug_log.log_debug(f"{item_type.__name__} <{len(self.subinventories[item_type].items)}>:")
                    print(f"{item_type.__name__} <{len(self.subinventories[item_type].items)}>:")
                cur_count=0
                for idx,item in enumerate(self.subinventories[item_type].items):
                    if cur_count>=7:
                        debug_log.log_debug(f"...")
                        print(f"...")
                        break
                    if item[1].owner !=self.owner:
                        if display_mode=='detailed':
                            debug_log.log_debug(f'{RED}*[{idx}]{RESET}'+f'({item[2]}个)' +item[1].get_detailed_status(checker=checker))
                            print(f'{RED}*[{idx}]{RESET}'+f'({item[2]}个)' +item[1].get_detailed_status(checker=checker))
                        else:
                            debug_log.log_debug(f'{RED}*[{idx}]{RESET}'+f'({item[2]}个)' +item[1].get_basic_status())
                            print(f'{RED}*[{idx}]{RESET}'+f'({item[2]}个)' +item[1].get_basic_status())
                    else:
                        if display_mode=='detailed':
                            debug_log.log_debug(f'[{idx}]'+f'({item[2]}个)' +item[1].get_detailed_status(checker=checker))
                            print(f'[{idx}]'+f'({item[2]}个)' +item[1].get_detailed_status(checker=checker))
                        else:
                            debug_log.log_debug(f'[{idx}]'+f'({item[2]}个)' +item[1].get_basic_status())
                            print(f'[{idx}]'+f'({item[2]}个)' +item[1].get_basic_status())
                    cur_count+=1
        elif item_type in self.subinventories:
            if item_type(item_id=0).is_stackable:
                debug_log.log_debug(f"{item_type.__name__} <{len(self.subinventories[item_type].items)}:{sum([item[2] for item in self.subinventories[item_type].items])}>:")
                print(f"{item_type.__name__} <{len(self.subinventories[item_type].items)}:{sum([item[2] for item in self.subinventories[item_type].items])}>:")
                if len(self.subinventories[item_type].items)<300:
                    self.sub_sort(item_type)
                else:
                    print(f"{item_type.__name__}类物品过多，建议清理不想要的物品")
            else:
                debug_log.log_debug(f"{item_type.__name__} <{len(self.subinventories[item_type].items)}>:")
                print(f"{item_type.__name__} <{len(self.subinventories[item_type].items)}>:")
            for idx,item in enumerate(self.subinventories[item_type].items):
                    if item[1].owner !=self.owner:
                        if display_mode=='detailed':
                            debug_log.log_debug(f'{RED}*[{idx}]{RESET}'+f'({item[2]}个)' +item[1].get_detailed_status(checker=checker))
                            print(f'{RED}*[{idx}]{RESET}'+f'({item[2]}个)' +item[1].get_detailed_status(checker=checker))
                        else:
                            debug_log.log_debug(f'{RED}*[{idx}]{RESET}'+f'({item[2]}个)' +item[1].get_basic_status())
                            print(f'{RED}*[{idx}]{RESET}'+f'({item[2]}个)' +item[1].get_basic_status())
                    else:
                        if display_mode=='detailed':
                            debug_log.log_debug(f'[{idx}]'+f'({item[2]}个)' +item[1].get_detailed_status(checker=checker))
                            print(f'[{idx}]'+f'({item[2]}个)' +item[1].get_detailed_status(checker=checker))
                        else:
                            debug_log.log_debug(f'[{idx}]'+f'({item[2]}个)' +item[1].get_basic_status())
                            print(f'[{idx}]'+f'({item[2]}个)' +item[1].get_basic_status())
        else:
            debug_log.log_error(f"<Iv:show_inventory>{self.owner}的背包中不存在{item_type}类型")
            print(f"{YELLOW}空空如也{RESET}\n")
        debug_log.log_debug(f"<Iv:show_inventory>处理完成\n")

#FIXME:角色类  
class CharacterMeta(type):
    """元类用于动态生成属性"""
    def __new__(cls, name, bases, attrs):
        # 从 attrs 中获取类方法
        _get_all_properties = attrs.get('_get_all_properties')
        _get_all_resistances = attrs.get('_get_all_resistances')
        _create_property = attrs.get('_create_property')
        _create_resistance_property = attrs.get('_create_resistance_property')

        # 获取正在创建的类对象
        new_class = type(name, bases, attrs)

        # 动态生成基础属性
        if _get_all_properties and _create_property:
            for prop in _get_all_properties.__func__(new_class):
                attrs[prop] = _create_property.__func__(new_class, prop)

        # 动态生成抗性属性
        if _get_all_resistances and _create_resistance_property:
            for res in _get_all_resistances.__func__(new_class):
                attrs[f"res_{res}"] = _create_resistance_property.__func__(new_class, res)

        return super().__new__(cls, name, bases, attrs)

class Character(metaclass=CharacterMeta):
    #所用的一些变量:
    #1.用于多次使用物品的UUID传递:
    _1after_item_uuid = None
    #2.用于下一级的经验的计算:
    _2next_exp = 0
    _2cur_lv = 1
    def __init__(self,
             name: str = f'{YELLOW}主角{RESET}',
             data: dict = None,
             resistances: dict = None,
             equipped: dict = None,
             a_skills: dict = None,
             p_skills: dict = None,
             items: dict = None,
             team_id:int=1,
             battle_handler:str='cpu',
             **kwargs
             ):

        self.name = name
        if not data:
            data={
                 'max_hp': 100,
                 'hp': 100,
                 'max_mp': 10,
                 'mp': 10,
                 'atk': 10,
                 'defe': 0,
                 'spd': 5,
                 'lck': 1,
                 'crit': 0.05,
                 'crit_dmg': 1.5,
                 'eva': 0.05,
                 'lv':1,
                 'exp':0,
                 'quality':1,
                 'attitude':{'player':'neutral'},
                 'lv_status_bonuses':{},
                 'lv_resistance_bonuses':{},
                 }
        self.quality=data.get('quality',1)
        self.attitude = data.get('attitude',{'player':'neutral'})
        self.is_alive = True
        self.team_id=team_id
        self.inventory = Inventory_improved(self)
        self.knowledge = illustrated_handbook(self)
        self.battle_handler=battle_handler
        if not resistances:
            resistances={}
        if not items:
            items={}
        if not a_skills:
            a_skills={}
        self.a_skills = a_skills.copy()
        if not p_skills:
            p_skills={}
        self.p_skills = p_skills.copy()
        if not equipped:
            equipped={
                 'weapon': None,
                 'armor': None,
                 'accessory': None}
        self.equipped = equipped.copy()
        #战斗相关数据
        self.status=[]
        
        self.uuid= uuid.uuid4()
        
        #添加物品

        for i in items:
            self.inventory.add_item(i,items[i])
        # 存储基础属性
        self._base_data = {prop:0 for prop in self._get_all_properties()}
        self._equipment_bonus={prop:0 for prop in self._get_all_properties()}
        self._lv_bonus = {prop:0 for prop in self._get_all_properties()}
        self._skill_bonus = {prop:0 for prop in self._get_all_properties()}
        self._base_resistances = {res: 0 for res in self._get_all_resistances()}
        self._equipment_resistances = {res: 0 for res in self._get_all_resistances()}
        self._lv_resistances = {res: 0 for res in self._get_all_resistances()}
        self._skill_resistances = {res: 0 for res in self._get_all_resistances()}
        #更新数据
        for i in data:
            if i in self._base_data:
                self._base_data[i]=data[i]
        # 更新抗性数据
        self._base_resistances.update(resistances)
        # 当前状态数据
        self._current_data = {
            'hp': data.get('hp', self._base_data['max_hp']),
            'mp': data.get('mp', self._base_data['max_mp']),
            'exp': data.get('exp', 0),
        }
        self._2cur_lv = data.get('lv', 1)
        self._2next_exp = self.exp_curve_func(self._2cur_lv+1)
        # 等级加成相关数据
        self._lv_status_bonuses_dic = data.get('lv_status_bonuses', {
            'max_hp': lambda x: x * 10,
            'hp': lambda x: x * 10,
            'max_mp': lambda x: x * 5,
            'mp': lambda x: x * 5,
            'atk': lambda x: x * 2,
            'defe': lambda x: x * 1,
            'spd': lambda x: x * 1,  
        })
        self._lv_resistance_bonuses_dic = data.get('lv_resistance_bonuses', {})
    
        self.refresh_status()

    @classmethod
    def _get_all_properties(cls):
        variants=['','*','L','*L']
        return [f"{base}{variant}" for base in ALL_BONUS for variant in variants]
    @classmethod
    def _get_all_resistances(cls):
        variants=['','*','L','*L']
        return [f"{base}{variant}" for base in ALL_RESISTANCE for variant in variants]
    @classmethod
    def _create_property(cls, prop_name):
        """工厂方法创建动态属性"""
        def getter(self):
            # 计算总加成 = 基础值 + 装备加成 + 等级加成 + 技能加成
            return (
                self._base_data.get(prop_name, 0) +
                self._equipment_bonus.get(prop_name, 0) +
                self._lv_bonus.get(prop_name, 0) +
                self._skill_bonus.get(prop_name, 0)
            )
        return property(getter)
    @classmethod
    def _create_resistance_property(cls, res_name):
        """工厂方法创建动态抗性属性"""
        def getter(self):
            return min(
                self._base_resistances.get(res_name, 0) +
                self._equipment_resistances.get(res_name, 0) +
                self._lv_resistances.get(res_name, 0)+
                self._skill_resistances.get(res_name, 0),
                0.99  # 设置上限
            )
        return property(getter)

    #更新装备数据，此函数在refresh_status中调用
    def _update_equipment_bonus(self):
        for prop in self._get_all_properties():
            self._equipment_bonus[prop] = sum(
                item.bonuses.get(prop, 0) 
                for item in self.equipped.values() 
                if item
            )
    #更新装备抗性数据，此函数在refresh_status中调用
    def _update_equipment_resistances(self):
        for prop in self._get_all_resistances():
            self._equipment_resistances[prop] = sum(
                item.resistances.get(prop, 0)
                for item in self.equipped.values()
                if item
            )
    #更新等级加成数据，此函数在refresh_status中调用
    def _update_lv_bonus(self):
        for prop in self._get_all_properties():
            self._lv_bonus[prop] = self._lv_status_bonuses_dic.get(prop, lambda x: 0)(self.lv)
    #更新等级抗性加成数据，此函数在refresh_status中调用
    def _update_lv_resistances(self):
        for prop in self._get_all_resistances():
            self._lv_resistances[prop] = self._lv_resistance_bonuses_dic.get(prop, lambda x: 0)(self.lv)
    #更新技能加成数据，此函数在refresh_status中调用
    def _update_skill_bonus(self):
        if not self.p_skills:
            return
        for prop in self._get_all_properties():
            self._skill_bonus[prop] = sum(
                skill.bonuses.get(prop, 0)
                for skill in self.p_skills.values()
            )
    #更新技能抗性加成数据，此函数在refresh_status中调用
    def _update_skill_resistances(self):
        if not self.p_skills:
            return
        for prop in self._get_all_resistances():
            self._skill_resistances[prop] = sum(
                skill.resistances.get(prop, 0)
                for skill in self.p_skills.values()  
            )

    @property
    def final_atk(self):
        return int(max(0,self.atk * getattr(self,'atk*') * getattr(self,'atk*L') + getattr(self,'atkL')))
    @property
    def final_defe(self):
        return int(max(0,self.defe * getattr(self,'defe*') * getattr(self,'defe*L') + getattr(self,'defeL')))
    @property
    def final_spd(self):
        return int(max(1,self.spd * getattr(self,'spd*') * getattr(self,'spd*L') + getattr(self,'spdL')))
    @property
    def final_lck(self):
        return int(self.lck * getattr(self,'lck*') * getattr(self,'lck*L') + getattr(self,'lckL'))
    @property
    def final_crit(self):
        return float(min(1,self.crit * getattr(self,'crit*') * getattr(self,'crit*L') + getattr(self,'critL')))
    @property
    def final_crit_dmg(self):
        return float(max(0,self.crit_dmg * getattr(self,'crit_dmg*') * getattr(self,'crit_dmg*L') + getattr(self,'crit_dmgL')))
    @property
    def final_eva(self):
        return min(0.9,self.eva * getattr(self,'eva*') * getattr(self,'eva*L') + getattr(self,'evaL'))
    @property
    def final_hp_heal(self):
        return int(self.hp_heal * getattr(self,'hp_heal*') * getattr(self,'hp_heal*L') + getattr(self,'hp_healL'))
    @property
    def final_mp_heal(self):
        return int(self.mp_heal * getattr(self,'mp_heal*') * getattr(self,'mp_heal*L') + getattr(self,'mp_healL'))
    @property
    def final_hp_heal_percent(self):
        return min(1,self.hp_heal_percent * getattr(self,'hp_heal_percent*') * getattr(self,'hp_heal_percent*L') + getattr(self,'hp_heal_percentL'))
    @property
    def final_mp_heal_percent(self):
        return min(1,self.mp_heal_percent * getattr(self,'mp_heal_percent*') * getattr(self,'mp_heal_percent*L') + getattr(self,'mp_heal_percentL'))
    @property
    def final_dmg_resistance(self):
        return int(max(0,self.dmg_resistance * getattr(self,'dmg_resistance*') * getattr(self,'dmg_resistance*L') + getattr(self,'dmg_resistanceL')))
    @property
    def final_dmg_resistance_percent(self):
        return min(0.99,self.dmg_resistance_percent * getattr(self,'dmg_resistance_percent*') * getattr(self,'dmg_resistance_percent*L') + getattr(self,'dmg_resistance_percentL'))
    @property
    def final_dmg_increase(self):
        return int(self.dmg_increase * getattr(self,'dmg_increase*') * getattr(self,'dmg_increase*L') + getattr(self,'dmg_increaseL'))
    @property
    def final_dmg_increase_percent(self):
        return max(-1,self.dmg_increase_percent * getattr(self,'dmg_increase_percent*') * getattr(self,'dmg_increase_percent*L') + getattr(self,'dmg_increase_percentL'))
    @property
    def final_max_hp(self):
        return int(max(1,self.max_hp * getattr(self,'max_hp*') * getattr(self,'max_hp*L') + getattr(self,'max_hpL')))
    @property
    def final_max_mp(self):
        return int(max(0,self.max_mp * getattr(self,'max_mp*') * getattr(self,'max_mp*L') + getattr(self,'max_mpL')))
    @property
    def final_moving_speed(self):
        return int(max(0,self.moving_speed * getattr(self,'moving_speed*') * getattr(self,'moving_speed*L') + getattr(self,'moving_speedL')))
    
    @property
    def hp(self):
        return self._current_data['hp']
    @hp.setter
    def hp(self, value):
        self._current_data['hp'] = max(0, min(value, self.max_hp))
        if self._current_data['hp'] <= 0:
            self.is_alive = False          
    @property
    def mp(self):
        return self._current_data['mp']
    @mp.setter
    def mp(self, value):
        self._current_data['mp'] = max(0, min(value, self.max_mp))

    @property
    def exp(self):
        return self._current_data['exp']
    @exp.setter
    def exp(self, value):
        self._current_data['exp'] = max(0, value)

    @property
    def weapon(self):
        return self.equipped['weapon'] or Equipment()
    @property
    def armor(self):
        return self.equipped['armor'] or Equipment()
    @property
    def accessory(self):
        return self.equipped['accessory'] or Equipment()

    def equip_item(self, item: 'Equipment' = None) -> int:
        if item is None:
            return -2
        elif item.equipment_type not in self.equipped:
            return -12
        elif item.is_equipped and item.equipper == self:
            return -18
        elif item.is_equipped and item.equipper != self:
            return -17
        debug_log.log_debug(f"<equip_item>{self.name} 装上装备 {item.name}|UUID:{item.uuid}\n")
        cur_equipment = self.equipped[item.equipment_type]
        if cur_equipment:
            cur_equipment.is_equipped = False
            cur_equipment.equipper = None
        self.equipped[item.equipment_type] = item
        item.is_equipped = True
        item.equipper = self
        self._update_equipment_bonus()
        self._update_equipment_resistances()
        return 1

    def unequip_item(self, item: 'Equipment' = None) -> int:
        if item is None:
            return -2
        elif item.equipment_type not in self.equipped:
            return -12
        elif self.equipped[item.equipment_type] != item:
            return -13
        elif not item.is_equipped:
            return -19
        elif item.equipper != self:
            return -16
        debug_log.log_debug(f"<unequip_item>{self.name} 卸下装备 {item.name}|UUID:{item.uuid}\n")
        self.equipped[item.equipment_type] = None
        item.is_equipped = False
        item.equipper = None
        self._update_equipment_bonus()
        self._update_equipment_resistances()
        return 1

    @classmethod
    def exp_curve_func(self, lv):
        top_m = int(1.03 ** pow(lv,0.1) * 100)
        ans= int(lv * pow(lv, 1.6) * top_m // 100)
        return ans * int(pow(lv/1000,pow(lv,0.002))) if lv>1000 else ans

    @property
    def lv(self):
        if self.exp<self._2next_exp:
            return self._2cur_lv
        else:
            low, high = 1, 100000
            while low < high:
                mid = (low + high + 1) // 2
                if self.exp_curve_func(mid) <= self.exp:
                    low = mid
                else:
                    high = mid - 1
            self._2cur_lv = low
            self._2next_exp = self.exp_curve_func(low + 1)
            return low

    def gain_exp(self, exp: int = 0):
        self.exp += exp
        if self.exp>=self._2next_exp:
            debug_log.log_debug(f"<gain_exp>{self.name} 升到了 {self.lv} 级\n")
            self.hp=self.max_hp
            self.mp=self.max_mp
            self.refresh_status()

    @property
    def resistances(self):
        return {
            res: getattr(self, f"res_{res}")
            for res in self._get_all_resistances()
        }

    def change_battle_handler(self,target):
        if target in ['cpu','player']:
            self.battle_handler=target
            debug_log.log_debug(f"改变操控者为{target}")
            print(f"改变操控者为{target}")
            
    def take_damage(self, damage: int = 0) -> None:
        debug_log.log_debug(f'<take_damage>{self.name} takes {damage} damage\n')
        self.hp -= damage

    def take_mp_damage(self, damage: int = 0) -> None:
        debug_log.log_debug(f'<take_mp_damamge>{self.name} takes {damage} mp_damage\n')
        self.mp -= damage

    def heal(self, val: int = 0) -> int:
        if not self.is_alive:
            return 0
        heal_amount = min(val, self.max_hp - self.hp)
        self.hp += heal_amount
        debug_log.log_debug(f'\n<heal> {self.name} heals {heal_amount} hp')
        return heal_amount

    def heal_mp(self, val: int = 0) -> int:
        heal_amount = min(val, self.max_mp - self.mp)
        self.mp += heal_amount
        debug_log.log_debug(f'<heal_mp> {self.name} heals {heal_amount} mp\n')
        return heal_amount

    def revive(self, val: int = 1) -> int:
        if self.is_alive:
            debug_log.log_debug(f'<revive> {self.name} is already alive\n')
            return 0
        heal_amount = min(val, self.max_hp - self.hp)
        self.hp += heal_amount
        self.is_alive = True
        debug_log.log_debug(f'<revive> {self.name} is revived and heals {heal_amount} hp\n')
        return heal_amount

    def attack_target(self, target: 'Character', type: str = 'normal') -> int:
        resistance = target.resistances.get(type, 0)
        actual_damage = max(int((self.atk - target.defe) * (1 - resistance)), 1)
        target.take_damage(actual_damage)
        self.refresh_status()
        target.refresh_status()
        debug_log.log_debug(f'<attack_target> {self.name} attacks {target.name} for {actual_damage} damage\n')
        return actual_damage

    def refresh_status(self):
        for item in self.equipped.values():
            if item:
                if item.durability<=0:
                    self.unequip_item(item) 
        self._update_equipment_bonus()
        self._update_equipment_resistances()
        self._update_lv_bonus()
        self._update_lv_resistances()
        self._update_skill_bonus()
        self._update_skill_resistances()
        self.hp = min(self.hp, self.max_hp)
        self.mp = min(self.mp, self.max_mp)
 
    def use_item(self,item: Item = None, target: 'Character' = None,source:'Character'=None,multi=0) -> bool:
        """
        角色使用物品。

        参数：
        - source: 物品来源(角色,表示角色的仓库),用于删除旧物品和返回深拷贝的新物品
        - item: Item - 物品
        - target: Character - 目标角色
        - source:物品来源
        - multi:配合use_more_items()等使用,
        默认为0,当被use_more_items()调用时,同时传入参数multi=1目前只用于操控print和日志信息. 
        返回值：
        - bool - 是否成功使用物品
        """
        if not item:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-2])
            print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-2]}{RESET}")
            return False
        if not source:
            source=item.owner
            if not source:
                debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-22])
                print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-22]}{RESET}")
                return False
            elif source != self:
                debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-8])
                print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-8]}{RESET}")
                return False
            
        if not source.inventory.get_exact_item(item=item):
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-3])
            print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-3]}{RESET}")
            return False
        if not item.revealed:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-23])
            print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-23]}{RESET}")
            return False
        if item.need_target and not target:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-4])
            print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-4]}{RESET}")
            return False

        debug_log.log_debug(f"<use_item>尝试使用物品者:UUID:{self.uuid}|{self}||目标{target}")
        debug_log.log_debug(f"<use_item>UUID:{item.uuid}物品所有者:{item.owner}|UUID:{item.owner.uuid}||来源:UUID:{source.uuid}|{source}")
        
        if item.consumable:
            item_for_use=copy.deepcopy(item)
            item_for_use.owner=None
        else:
            item_for_use=item
        debug_log.log_debug(f"<use_item>UUID:{item_for_use.uuid}是用于使用的实际物品")
        state = item_for_use.use(target)
        if state == 1:
            if item.consumable:
                source.inventory.remove_item(item)
                debug_log.log_debug(f"<use_item>{source}移除了物品{item}")
                after_item=item_for_use.durability_down(1)
                if after_item:
                    debug_log.log_debug(f"<use_item>物品{item}耐久-1 :添加新物品{after_item}|UUID:{after_item.uuid}")
                    source.inventory.add_item(after_item)
                    self._1after_item_uuid=after_item.uuid
                else:
                    debug_log.log_debug(f"<use_item>物品{item}耐久-1 :损毁")
                    self._1after_item_uuid=None
                
            self.refresh_status()
            if not multi:
                print(f"对{target}使用 {item}{GREEN}成功{RESET}")
            debug_log.log_debug(f"<use_item>成功对{target}使用了 {item}\n")
            return True
        else:
            if not multi:
                print(f"对{target}使用 {item} {RED}失败:{USE_ITEM_ERROR_MESSAGES[state]}{RESET}")
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[state])
            return False

    def use_more_items(self, items: list[Item] = None, targets: list['Character'] = None) -> bool:
        """
        角色使用多个物品。

        参数：
        - items: list[Item] - 物品列表
        - targets: list[Character] - 目标角色列表

        返回值：
        - bool - 是否成功使用物品
        """
        lth= len(items)
        debug_log.log_debug(f"<use_more_items>尝试使用{lth}个物品")
        if len(targets)==1:
            debug_log.log_error(f"<use_more_items>目标列表只有一个元素,但物品列表有多个元素,执行默认纠正")
            targets = [targets[0] for _ in range(lth)]
        if len(targets)!=lth:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-10])
            print(USE_ITEM_ERROR_MESSAGES[-10])
            return False
            
        for i in range(len(items)):
            if not self.use_item(items[i], targets[i]):
                debug_log.log_error(f"<use_more_items>使用第{i+1}个物品<{items[i]}> 对 <{targets[i]}> {RED}失败{RESET}\n")
                print(f"使用第{i+1}个物品<{items[i]}> 对 <{targets[i]}> {RED}失败{RESET}")
                return False
        debug_log.log_debug(f"<use_more_items>成功使用{lth}个物品\n")
        return True

    def use_item_for_many_times(self, item: Item, target: 'Character', times: int = 1) -> bool:
        """
        角色多次使用物品。

        参数：
        - item: Item - 物品
        - target: Character - 目标角色
        - times: int - 使用次数

        返回值：
        - bool - 是否成功使用物品
        """
        debug_log.log_debug(f"<use_item_for_many_times>尝试使用{times}次物品<{item}> 对 <{target}>")
        if times <= 0:
            debug_log.log_error(f"<use_item_for_many_times>使用次数<{times}>小于等于0")
            print(USE_ITEM_ERROR_MESSAGES[-9])
            return False
        else:
            for _ in range(times):
                if not self.use_item(item, target):
                    debug_log.log_error(f"<use_item_for_many_times>使用第{_+1}次失败\n")
                    print(f"使用第{_+1}次{RED}失败{RESET}")
                    return False
                item=self.inventory.get_exact_item(uuid=self._1after_item_uuid)
            debug_log.log_debug(f"<use_item_for_many_times>成功使用{times}次物品{item} 对 {target}\n")
            return True

    def use_item_fuzzy(self, item_type: type = None, target: 'Character' = None, spe_val: int = None) -> bool:
        """
        角色使用模糊匹配的物品。

        参数：
        - item_type: type - 物品类型
        - target: Character - 目标角色
        - spe_val: int - 特殊值

        返回值：
        - bool - 是否成功使用物品
        """
        debug_log.log_debug(f"<use_item_fuzzy>尝试使用类型为<{item_type}>的物品，目标为<{target.name if target else '无'}>，特殊值为<{spe_val}>")
        
        if item_type is None:
            debug_log.log_error(f"<use_item_fuzzy>物品类型为空")
            print(USE_ITEM_ERROR_MESSAGES[-7])
            return False
        if item_type not in self.inventory.show_items_types():
            debug_log.log_error(f"<use_item_fuzzy>物品类型<{item_type}>不在库存中")
            print(USE_ITEM_ERROR_MESSAGES[-6])
            return False
        else:
            item_to_use = self.inventory.get_exact_item(spe_val, item_type)
            if item_to_use is None:
                debug_log.log_error(f"<use_item_fuzzy>未找到特殊值为<{spe_val}>的物品")
                print(USE_ITEM_ERROR_MESSAGES[-3])
                candidates = self.inventory.get_items(item_type, spe_val)
                if len(candidates) != 0:
                    debug_log.log_debug(f"<use_item_fuzzy>找到{len(candidates)}个候选物品")
                    print("可选已有物品：")
                    for i, c in enumerate(candidates):
                        print(f"[{i}] {c['item'].get_basic_status()}||UUID:{c['item'].uuid}")
                    choice = int(input("请输入选项编号 或输入其他数字取消："))
                    if 0 <= choice < len(candidates):
                        item_to_use = candidates[choice]["item"]
                        debug_log.log_debug(f"<use_item_fuzzy>选择使用物品<{item_to_use}>")
                    else:
                        debug_log.log_debug(f"<use_item_fuzzy>取消使用物品")
                        print("取消使用")
                        return False
                else:
                    debug_log.log_error(f"<use_item_fuzzy>没有找到任何候选物品")
                    return False
            if not self.use_item(item_to_use, target):
                debug_log.log_error(f"<use_item_fuzzy>使用物品<{item_to_use}>对<{target if target else '无'}>{RED}失败{RESET}")
                print(f"使用物品<{item_to_use}>对<{target if target else '无'}>{RED}失败{RESET}")
                return False
            debug_log.log_debug(f"<use_item_fuzzy>{GREEN}成功{RESET}使用物品<{item_to_use}>对<{target if target else '无'}>")
            return True

    def reveal_item(self, item: 'Item'=None):
        debug_log.log_debug(f"<reveal_item>角色{self}鉴定物品<{item}>")
        if not item:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-2])
            print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-2]}{RESET}")
            return False
        if item.revealed:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-24])
            print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-24]}{RESET}")
            return False
        item.reveal()
        print(f"{GREEN}成功{RESET}鉴定物品<{item}>")
        print(item.get_basic_status(checker=self))
        debug_log.log_debug(f"<reveal_item>成功鉴定物品<{item}>")
        debug_log.log_debug(f"<reveal_item>{item.get_basic_status(checker=self)}")
        #给角色图鉴学习相应物品知识
        if not self.knowledge.check(item):
            debug_log.log_debug(f"<reveal_item>角色{self}图鉴未学习过<{item}>:ID:{item.item_id}")
            debug_log.log_debug(f"<reveal_item>学习物品知识的概率为:{0.8*(1/max(item.quality,1))}")
            if random.random() < 0.8*(1/max(item.quality,1)):
                self.knowledge.learn(item)
        #根据材料占比，按概率给角色图鉴学习相应物品材料知识
        for mat in item.materials:
            if not self.knowledge.check(mat):
                debug_log.log_debug(f"<reveal_item>角色{self}图鉴未学习过<{mat}>")
                debug_log.log_debug(f"<reveal_item>学习物品材料的概率为:{0.9*(1.1/max(mat.quality,1))*item.materials[mat]}")
                if random.random() < 0.9*(1.1/max(mat.quality,1))*item.materials[mat]:
                    self.knowledge.learn(mat)
        return True
            
    def repair_item(self,item: 'Item'=None,material_item=None):
        debug_log.log_debug(f"<repair_item>角色{self}修理物品<{item}>")
        if not item:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-2])
            print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-2]}{RESET}")
            return False
        if not isinstance(item,Equipment):
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-33])
            print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-33]}{RESET}")
            return False
        if not material_item:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-29])
            print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-29]}{RESET}")
            return False
        if item.uuid == material_item.uuid:
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-34])
            print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-34]}{RESET}")
            return False
        if not (item.revealed and material_item.revealed):
            debug_log.log_error(USE_ITEM_ERROR_MESSAGES[-23])
            print(f"{RED}{USE_ITEM_ERROR_MESSAGES[-23]}{RESET}")
            return False
        repair_materials=material_item.materials
        rp_compatiblity={'A':0,'B':0,'C':0}
        for i in repair_materials:
            for j in rp_compatiblity:
                rp_compatiblity[j]+=i.compatibilities[j]*repair_materials[i]
            repair_materials[i]*=material_item.size
        source_materials = item.materials
        so_compatiblity={'A':0,'B':0,'C':0}
        for i in source_materials:
            for j in so_compatiblity:
                so_compatiblity[j]+=i.compatibilities[j]*source_materials[i]
            source_materials[i] *= item.size
        rp_sum=sum(repair_materials.values())
        sp_sum=sum(source_materials.values())
        uncompatiblity = abs(sum(abs(rp_compatiblity[i]-so_compatiblity[i]) for i in rp_compatiblity) / (sum(so_compatiblity.values()) or 1)) / 1.6
        print(f"被修理装备相性:{so_compatiblity}")
        print(f"修理材料相性:{rp_compatiblity}")
        print(f"不相容性:{get_float_val_color(1-uncompatiblity)}{uncompatiblity*100:.2f}{RESET}%")
        ipt=input("还要继续修复吗？(N以取消,输入其他任意内容或回车以继续)\n")
        if ipt.lower()=='n':
            return False
        #修复减少装备基础属性
        for i in item.base_attributes:
            item.base_attributes[i]*=1-min(0.8*uncompatiblity+0.02,0.8)*rp_sum/sp_sum
        for i in item.base_resistance:
            item.base_resistance[i]*=1-min(0.8*uncompatiblity+0.02,0.8)*rp_sum/sp_sum
        item.max_durability*=(1-min(uncompatiblity+0.02,0.8))
        # 修复会混合材料
        item_materials = {}
        for i in set(repair_materials.keys()).union(source_materials.keys()):
            total_materials = repair_materials.get(i, 0) + source_materials.get(i, 0)
            item_materials[i] = total_materials / (rp_sum + sp_sum) if (rp_sum + sp_sum) != 0 else 0
            if item_materials[i] > 0.999:
                item_materials[i] = 1
            if item_materials[i] < 0.001:
                del item_materials[i]
        item.materials = item_materials
         #重初始化
        item.final_attributes=material_bonus_cal(item,convert_type=item.convert_type)
        item.bonuses=item.final_attributes
        item.final_resistance=material_bonus_cal(item,special_rule=-1)
        item.resistances=item.final_resistance
        item.price*=(1-min(0.5*uncompatiblity+0.02,0.85))
        item.price=int(item.price)
        if item.price<item.base_price:
            item.base_price=item.price

        item.max_durability=int(max(min(material_bonus_cal(item,special_rule=-3)*1.2*(1-min(0.5*uncompatiblity+0.02,0.8)*rp_sum/sp_sum),item.max_durability-1),1))
        if item.max_durability<item.base_durability:
            item.base_durability=item.max_durability
        item.durability=int(min(item.max_durability,item.durability+item.max_durability*rp_sum/sp_sum))
        
        item.owner.inventory.current_weight-=item.weight
        item.weight=0
        for key,value in item.materials.items():
            item.weight += key.density * value * item.size
        item.weight=max(0,item.weight)
        item.owner.inventory.current_weight+=item.weight
        
        item.re_ini_name(mode='')
        
        
        material_item.owner.inventory.remove_item(material_item)
        print(f"{GREEN}成功{RESET}修理物品<{item}>")
        print(item.get_basic_status(checker=self))
        return True
    
    def get_cur_status(self, turns: int = 0):
        debug_log.log_debug(f"<get_cur_status>UUID:角色获取{self}的当前状态<{turns}>")
        self.refresh_status()
        if turns == 0:
            self.initial_status = {i: getattr(self, i) for i in self._base_data}
            self.initial_status['resistances'] = self.resistances.copy()
            return
        if not hasattr(self, 'initial_status') or not self.initial_status:
                self.initial_status = {i: getattr(self, i) for i in self._base_data}
                self.initial_status['resistances'] = self.resistances.copy()
        cur_status = {i: getattr(self, i) for i in self._base_data}
        cur_status['resistances'] = self.resistances.copy()
        if self.hp <= 0.25 * self.max_hp:
            hp_color = RED
        elif self.hp <= 0.5 * self.max_hp:
            hp_color = YELLOW
        elif self.hp <= 0.75 * self.max_hp:
            hp_color = GREEN
        else:
            hp_color = CYAN

        if self.mp <= 0.25 * self.max_mp:
            mp_color = RED
        elif self.mp <= 0.5 * self.max_mp:
            mp_color = YELLOW
        elif self.mp <= 0.75 * self.max_mp:
            mp_color = GREEN
        else:
            mp_color = CYAN
        
        if self.attitude.get('player','neutral')!='friendly':
            status_parts=[f"{self} LV:{self.lv} \nHP:{hp_color}{self.hp}{RESET}/{self.max_hp}, MP:{mp_color}{self.mp}{RESET}/{self.max_mp}"]
            return ''.join(status_parts)

        status_parts = [f"{self} LV:{self.lv} ({self.exp}/{self._2next_exp} - EXP距升级:{self._2next_exp - self.exp}) \nHP:{hp_color}{self.hp}{RESET}/{self.max_hp}, MP:{mp_color}{self.mp}{RESET}/{self.max_mp} ||  ATK:{self.atk}, DEF:{self.defe}, SPD:{self.spd} \n"]
        changes = []  # 初始化空列表，用于存储变化信息

        for key in ['max_hp', 'max_mp', 'atk', 'defe', 'spd', 'lck']:
            if self.initial_status[key] != cur_status[key]:
                change = cur_status[key] - self.initial_status[key]
                if change != 0:
                    color = RED if change < 0 else GREEN
                    changes.append(f"属{key.upper()}:{color}{change:+d}{RESET}")

        for key in ['crit', 'crit_dmg', 'eva']:
            if self.initial_status[key] != cur_status[key]:
                change = cur_status[key] - self.initial_status[key]
                if change != 0:
                    color = RED if change < 0 else GREEN
                    changes.append(f"属{key.upper()}:{color}{change * 100:+.2f}%{RESET}")

        for key in ALL_RESISTANCE:
            initial_value = self.initial_status['resistances'].get(f'{key}', 0)
            change = cur_status['resistances'].get(f'{key}',0) - initial_value
            if change != 0:
                color = RED if change < 0 else GREEN
                changes.append(f"抗{key.upper()}:{color}{change * 100:+.2f}%{RESET}")

        for attr in ALL_BONUS:
            for variant in [f'{attr}*', f'{attr}L', f'{attr}*L']:
                if variant in cur_status and variant in self.initial_status:
                    change = cur_status[variant] - self.initial_status[variant]
                    if change != 0:
                        color = RED if change < 0 else GREEN
                        if variant.endswith('*'):
                            display_text = f"属{attr}百分比修正*{color}{int((1 + cur_status[variant]) * 100)}{RESET}% (原{int((1 + self.initial_status[variant]) * 100)}%)"
                        elif variant.endswith('L') and not variant.endswith('*L'):
                            display_text = f"属{attr}最终数值修正{color}{cur_status[variant]:+}{RESET} (原{self.initial_status[variant]})"
                        elif variant.endswith('*L'):
                            display_text = f"属{attr}最终百分比修正*{color}{int((1 + cur_status[variant]) * 100)}{RESET}% (原{int((1 + self.initial_status[variant]) * 100)}%)"
                        changes.append(f"{display_text}")
        for attr in ALL_RESISTANCE:
            for variant in [f'{attr}*', f'{attr}L',f'{attr}*L']:
                if variant in cur_status['resistances'] and variant in self.initial_status['resistances']:
                    change = cur_status['resistances'][variant] - self.initial_status['resistances'][variant]
                    if change!= 0:
                        color = RED if change < 0 else GREEN
                        if variant.endswith('*'):
                            display_text = f"抗{attr.upper()}百分比修正*{color}{int((1 + cur_status['resistances'][variant]) * 100)}{RESET}% (原{int((1 + self.initial_status['resistances'][variant]) * 100)}%)"
                        elif variant.endswith('L') and not variant.endswith('*L'):
                            display_text = f"抗{attr.upper()}最终数值修正{color}{cur_status['resistances'][variant]*100:+.2f}{RESET}% (原{self.initial_status['resistances'][variant]*100:+.2f}%)"
                        elif variant.endswith('*L'):
                            display_text = f"抗{attr.upper()}最终百分比修正*{color}{int((1 + cur_status['resistances'][variant]) * 100)}{RESET}% (原{int((1 + self.initial_status['resistances'][variant]) * 100)}%)"
                        changes.append(f"{display_text}")

        if changes:
            status_parts.append(" | ".join(changes))
            status_parts.append('\n')

        debug_log.log_debug(f"<get_status>角色{self.name}的当前<{turns}>状态为：\n{' | '.join(status_parts)}\n")
        return " | ".join(status_parts)

    def learn_skill(self,skill:Skill=None):
        if not skill:
            return
        if isinstance(skill,PassiveSkill):
            self.p_skills.append(skill)
        elif isinstance(skill,ActiveSkill):
            self.a_skills.append(skill)
        return

    def forget_skill(self,skill:Skill=None):
        if not skill:
            return
        if isinstance(skill,PassiveSkill):
            self.p_skills.pop(skill)
        elif isinstance(skill,ActiveSkill):
            self.a_skills.pop(skill)
        return

    def get_cur_equipment(self):
        """
        获取角色当前装备。

        返回值：
        - str - 角色当前装备的字符串表示
        """
        self.refresh_status()
        debug_log.log_debug(f"<get_cur_equipment>角色{self.name}的当前装备为：{self.weapon.name}，{self.armor.name}，{self.accessory.name}\n")
        return f"{self} \n武器:{self.weapon.get_basic_status(mode='display')}\n防具:{self.armor.get_basic_status(mode='display')}\n饰品:{self.accessory.get_basic_status(mode='display')}"

    def show_status(self):
        debug_log.log_debug(f"<show_status>角色{self.name}获取状态表\n")
        if self.hp<=0.25*self.max_hp:
            hp_color=RED
        elif self.hp<=0.5*self.max_hp:
            hp_color=YELLOW
        elif self.hp<=0.75*self.max_hp:
            hp_color=GREEN
        else:
            hp_color=CYAN

        if self.mp<=0.25*self.max_mp:
            mp_color=RED
        elif self.mp<=0.5*self.max_mp:
            mp_color=YELLOW
        elif self.mp<=0.75*self.max_mp:
            mp_color=GREEN
        else:
            mp_color=CYAN
            
        status_parts = [f"{self} LV:{self.lv} ({self.exp}/{self._2next_exp} - EXP距升级:{self._2next_exp - self.exp}) \nHP:{hp_color}{self.hp}{RESET}/{self.max_hp}, MP:{mp_color}{self.mp}{RESET}/{self.max_mp} \nATK:{self.atk} DEF:{self.defe} SPD:{self.spd} LCK:{self.lck}\n闪避率:{get_float_val_color(self.eva)}{self.eva*100:.2f}{RESET}% 暴击率:{get_float_val_color(self.crit)}{self.crit*100:.2f}{RESET}% 暴击伤害:{get_float_val_color((self.crit_dmg-1.5)/1.8)}{self.crit_dmg*100:.2f}{RESET}%\n"]
        spe_status_parts = []
        spe_status=[]
        for attr in ALL_BONUS:
            spe_status.extend([f'{attr}*',f'{attr}L',f'{attr}*L'])
        for i in spe_status:
            if getattr(self,i)!=0:
                spe_status_parts.append(f' {i}:{getattr(self,i)}')
        status_parts.append("".join(spe_status_parts))
        status_parts.append('\n')
        resistance_parts = ["抗性：\n"]
        for key, value in self.resistances.items():
            if value !=0:
                resi_color = get_float_val_color(value)
                resistance_parts.append(f" {key.upper()}:{resi_color}{value*100:.2f}{RESET}%")
        if len(resistance_parts)==1:
            resistance_parts.append(f'{PURPLE}无{RESET}')
        status_parts.append("".join(resistance_parts))
        status_parts.append('\n')
        status_parts.append(self.get_cur_equipment())
        debug_log.log_debug(f"<show_status>角色{self.name}的状态表为：\n{''.join(status_parts)}\n")
        print("".join(status_parts))
    
    def recover_all(self):
        self.hp = self.max_hp
        self.mp = self.max_mp
        debug_log.log_debug(f"<recover_all>角色{self.name}已恢复所有状态\n")

    def copy_with_same_uuid(self):
        """
        仅拷贝名称和uuid,用于识别所有者等
        """
        new_char = self.__class__(self.name)
        new_char.uuid = self.uuid
        return new_char
    
    def __str__(self) -> str:
        """
        返回角色的字符串表示。

        返回值：
        - str - 角色的字符串表示
        """
        return convert_colorful_text(self.name, get_quality_color(self.quality))

    def __deepcopy__(self,memo):
        """
        用于深拷贝角色的方法。

        参数：
        - memo (dict) - 用于存储已经拷贝的对象的字典

        返回值：
        - Character - 拷贝后的角色对象
        """
        new_char = self.__class__(self.name)
        memo[id(self)]=new_char
        new_char.uuid = uuid.uuid4()
        for k,v in self.__dict__.items():
            if k not in ['uuid']:
                setattr(new_char,k,copy.deepcopy(v,memo))
        return new_char
        
    def __eq__(self, other):
        return self.uuid == other.uuid and isinstance(other,Character)
    
    def __hash__(self):
        return hash(self.uuid)
