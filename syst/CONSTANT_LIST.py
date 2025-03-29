from enum import Enum
#使用物品的错误信息表
USE_ITEM_ERROR_MESSAGES = {
    -1: "ERR-a1 物品不能使用或直接使用",
    -2: "ERR-a2 物品未指定",
    -3: "ERR-a3 物品不存在",
    -4: "ERR-a4 物品未指定目标",
    -5: "ERR-a5 对象已经满血",
    -6: "ERR-a6 没有此类物品",
    -7: "ERR-a7 物品类型未指定",
    -8: "ERR-a8 你不是该物品的主人",
    -9: "ERR-a9 不能把拥有者从自己转给自己",
    -10: "ERR-a10 多物品使用的对象数不匹配",
    -11: "ERR-b1 物品不能装备",
    -12: "ERR-b2 不能装备/卸下此类装备",
    -13: "ERR-b3 指定卸下的装备不存在",
    -14: "ERR-b4 装备不能卸下",
    -15: "ERR-b5 没有装备此类型的装备",
    -16: "ERR-b6 不能卸下不是你装备的装备",
    -17: "ERR-b7 这个装备已经有其他人装备了",
    -18: "ERR-b8 这个装备已经被装备了",
    -19: "ERR-b9 这个装备并没有被装备",
    -20: "ERR-b10 未知的装备者(考虑删除此错误装备)",
    -21: "ERR-c1 未知物主(考虑删除此物品)",
    -22: "ERR-c2 物品未知来源",
    -23: "ERR-c3 物品未鉴定",
    -24: "ERR-c4 物品已经鉴定",
    -25: "ERR-c5 背包空间不足，尝试清理空间",
    -26: "ERR-c6 物品太大",
    -27: "ERR-c7 背包负重不足，尝试清理物品",
    -28: "ERR-c8 物品太重",
    -29: "ERR-c9 未选定材料",
    -30: "ERR-c10 物品耐久已满",
    -31: "ERR-d1 索引访问超限",
    -32: "ERR-d2 mode参数未正确指定",
    -33: "ERR-d3 物品类型不正确",
    -34: "ERR-d4 不能选择自己",
    -35: "ERR-d5 ",
    -36: "ERR-d6 ",
    -37: "ERR-d7 ",
    -38: "ERR-d8 ",
    -39: "ERR-d9 ",
    -40: "ERR-d10 ",
    -41: "ERR-e1 ",
    -42: "ERR-e2 ",
}

#其他错误信息表
REMAIN_ERROR_MESSAGES={
    1:'ERR-RA1 已有队伍',
    2:'ERR-RA2 队伍已满',
    3:'ERR-RA3 未找到该索引的队员'
}

#物品效果ID对照表
SPE_EFFECT_ID= {
    -1: "测试效果",
    0: "无",
    1:'',
    2:'铜材质用效果',
    3:'',
    4:'',
    5:'',
    6:'',
}

#仓库的自定义排序方式
INV_SORT_METHODS ={
    'Heal_potion':'heal_amount',
    'Dart':'damage',
    'Accessory':'score',
    'Weapon':'score',
    'Armor':'score',
}

#物品名称ID表
ITEM_ID = {
    0: "未定义ID物品",
    1: "治疗药水",
    2: "飞镖",
    3: "小铁块",
    4: "小铜块",
    5: "小生命精华",
    6: "大剑",
}

#技能名称ID表
SKILL_ID = {
    0: "未定义ID技能",
    1: "普通攻击",
    2: "",
    3: "",
    4: "",
    5: "",
    6: "",
}

#材料名称ID表
MATERIAL_ID = {
    0: "未定义ID材料",
    1: "铁",
    2: "铜",
    3: "",
    4: "",
    5: "",
}

#全属性表
ALL_BONUS=['atk',
            'defe',
            'spd',
            'lck',
            'max_hp',
            'max_mp',
            'eva',
            'crit',
            'crit_dmg',
            'hp_heal',#按点数的每回合回血
            'mp_heal',
            'hp_heal_percent',#按百分比的每回合回血
            'mp_heal_percent',
            'dmg_resistance',#按数值的伤害减免
            'dmg_resistance_percent',#按百分比的伤害减免
            'dmg_increase',#按数值的伤害增加
            'dmg_increase_percent',#按百分比的伤害增加
            'moving_speed',#战斗中每时序的前进量
            ]

ALL_RESISTANCE=['fire',
            'water',
            'ice',
            'lightning',
            'poison',
            'dark',
            'holy',
            'normal',
            'magic',
            'elemental',
            'all',]

#材质影响时 武器、护甲和饰品等的受加成表
WEAPON_MATERIAL_BONUS = {
    'atk':1.4,
    'def':0.4,
    'spd':1.1,
    'lck':0.8,
    'max_hp':0.8,
    'max_mp':0.8,
    'eva':0.9,
    'crit':1.0,
    'crit_dmg':1.1,
    'hp_heal':0.8,
    'mp_heal':0.8,
}
ARMOR_MATERIAL_BONUS = {
    'atk':0,
    'def':1.4,
    'spd':1.0,
    'lck':0.9,
    'max_hp':1.2,
    'max_mp':1.1,
    'eva':1.0,
    'crit':0.7,
    'crit_dmg':0.7,
    'hp_heal':1.0,
    'mp_heal':1.0,
}
ACCESSORY_MATERIAL_BONUS = {
    'atk':0.5,
    'def':0.5,
    'spd':1.2,
    'lck':1.4,
    'max_hp':1.4,
    'max_mp':1.4,
    'eva':1.1,
    'crit':1.1,
    'crit_dmg':1.1,
    'hp_heal':1.1,
    'mp_heal':1.1,
}
LEGENDARY_MATERIAL_BONUS = {
    'atk':1.5,
    'def':1.5,
    'spd':1.5,
    'lck':1.5,
    'max_hp':1.5,
    'max_mp':1.5,
    'eva':1.5,
    'crit':1.5,
    'crit_dmg':1.5,
    'hp_heal':1.5,
    'mp_heal':1.5,
}
NORMAL_MATERIAL_BONUS = {
    'atk':1.0,
    'def':1.0,
    'spd':1.0,
    'lck':1.0,
    'max_hp':1.0,
    'max_mp':1.0,
    'eva':1.0,
    'crit':1.0,
    'crit_dmg':1.0,
    'hp_heal':1.0,
    'mp_heal':1.0,
}
#材料数值计算的特殊情况表
MATERIAL_CAL_SPECIAL = {
    0: '一般情况',
    -1:'抗性用',
    -2:'价格用',
    -3:'最大耐久用',
    1: "治疗药水用",
}

#队伍（阵营）ID：
TEAM_IDS={
    0:'无',
    1:'玩家队伍',
    2:'敌对队伍'
}


class SkillScope(Enum):
    SELF = "自身"
    ENEMY_SINGLE = "敌人单体"
    ENEMY_ALL = "全体敌人"
    ALLY_SINGLE = "己方单体"
    ALLY_ALL = "全体友方"
    NONE = "无"

class Phase(Enum):
    BT_PREPARE = "准备阶段"
    BT_DAMAGE_CALC = "伤害计算"
    BT_POST_ACTION = "行动后阶段"
    CONTINUOUS = "持续" #(用于一些常驻加属性的被动技能)
    NONE = '无'

# 颜色常量
BLACK = '\033[90m'
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m' # 品红色
CYAN = '\033[96m'    # 青色
WHITE = '\033[97m'
ORANGE = '\033[38;2;255;165;0m'
PURPLE = '\033[95m'
GRAY = '\033[90m'
RESET = '\033[0m'

BRIGHT_BLACK = '\033[90m'
BRIGHT_RED = '\033[91m'
BRIGHT_GREEN = '\033[92m'
BRIGHT_YELLOW = '\033[93m'
BRIGHT_BLUE = '\033[94m'
BRIGHT_MAGENTA = '\033[95m' # 亮品红色
BRIGHT_CYAN = '\033[96m'    # 亮青色
BRIGHT_PURPLE = '\033[38;2;221;160;221m'
BRIGHT_ORANGE = '\033[38;2;255;200;0m'
DARK_GRAY = '\033[38;2;166;166;166m'
BRIGHT_WHITE = '\033[97m'
