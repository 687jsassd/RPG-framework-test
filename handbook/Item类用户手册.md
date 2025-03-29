# Item类用户手册

## 目录
1. [类概述](#类概述)
2. [核心功能](#核心功能)
3. [创建物品规范](#创建物品规范)
4. [属性说明](#属性说明)
5. [方法详解](#方法详解)
6. [示例代码](#示例代码)
7. [注意事项](#注意事项)
8. [附录](#附录)

---

## 类概述
`Item` 是游戏物品系统的抽象基类（ABC），用于定义所有游戏物品的通用属性和行为。开发者在创建新物品时必须继承此类并实现抽象方法。

特性：
- 支持完整的物品生命周期管理（创建、使用、销毁）
- 内置材料复合系统（多材料组成影响属性）
- 完善的耐久度/堆叠机制
- 自动化属性计算系统
- 完整的物品状态管理（揭示/鉴定系统）

---

## 核心功能

### 1. 基础属性系统
| 属性类型                   | 说明                             | 计算规则                                      |
| -------------------------- | -------------------------------- | --------------------------------------------- |
| 基础属性(base_attributes)  | 物品的原始属性（不受材料影响）   | 手动设置或继承默认值                          |
| 最终属性(final_attributes) | 实际生效的属性（可能受材料影响） | 根据`attributes_affected_by_material`标志计算 |

### 2. 材料复合系统
```python
# 材料定义示例
self.materials = {
    m_Iron: 0.6,    # 铁占比60%
    m_Copper: 0.4   # 铜占比40%
}
```
- 材料占比自动归一化处理
- 材料影响：属性加成、抗性、耐久度、价格
- 材料知识系统：角色需要先学习材料才能识别

### 3. 耐久度机制
```python
# 耐久度变化示例
sword.durability_down(5)  # 减少5点耐久
potion.durability_up(3)   # 恢复3点耐久
```
- 自动销毁机制（耐久归零时从库存移除）
- 不同耐久阶段颜色提示（绿>75% → 红<25%）

### 4. 物品揭示系统
```python
if not item.revealed:
    print("未鉴定的物品")
item.reveal()  # 揭示物品
```
- 未揭示物品显示有限信息
- 需要角色具备相应知识才能完全识别

---

## 创建物品规范

### 1. 继承要求
```python
class CustomItem(Item):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # 必须传递kwargs
        # 自定义初始化逻辑
        
    @override
    def use(self, target):
        # 必须实现use方法
        return result_code
```

### 2. 初始化参数规范
| 参数名    | 类型 | 必需 | 默认值        | 说明                       |
| --------- | ---- | ---- | ------------- | -------------------------- |
| item_id   | int  | 是   | 无            | 必须存在于ITEM_ID常量表    |
| name      | str  | 否   | 自动生成      | 根据材料自动生成名称       |
| materials | dict | 否   | {m_Unknown:1} | 材料字典（Material: 占比） |

### 3. 命名规则
```python
# 自动命名结构
"前缀1 前缀2-主材料 的 基础名称 +强化等级"
示例："锋利III-精钢 的长剑 +5"
```

### 4. 材料系统规范
- 材料占比总和自动归一化为100%
- 材料密度影响物品重量
- 稀有材料显著影响属性加成

---

## 属性说明

### 关键属性表
| 属性                            | 类型 | 说明                               |
| ------------------------------- | ---- | ---------------------------------- |
| is_stackable                    | bool | 可堆叠（需所有属性相同）           |
| breakable                       | bool | 是否可损坏（False表示永久存在）    |
| upgrade_level                   | int  | 强化等级（影响名称显示）           |
| convert_type                    | str  | 材料转换类型（'weapon'/'armor'等） |
| attributes_affected_by_material | bool | 是否启用材料属性加成               |

### 特殊属性
```python
# 材料影响规则示例
self.convert_type = 'weapon'  # 使用武器类材料加成规则
self.attributes_affected_by_material = True
```

---

## 方法详解

### 核心方法
#### 1. `use()`
```python
def use(self, target) -> int:
    """抽象方法，必须实现
    返回状态码：
    1: 使用成功
    -5: 使用条件不满足（如目标满血）
    其他：自定义错误码
    """
```

#### 2.` get_basic_status()`
```python
# 显示模式示例
item.get_basic_status(mode='display')  # 返回格式化字符串
item.get_basic_status(mode='data')    # 返回字典
```

#### 3. `re_cal_material_bonus()`
```python
# 材料加成重计算
item.re_cal_material_bonus()  # 在材料变化后手动调用
```

### 辅助方法
| 方法名                 | 作用                   |
| ---------------------- | ---------------------- |
| `rename(new_name)`     | 自定义物品名称         |
| `owner_change(target)` | 转移所有权（触发事件） |
| `__deepcopy__()`       | 生成独立副本（新UUID） |

---

## 示例代码

### 1. 基础治疗药水
```python
class HealthPotion(Item):
    def __init__(self, **kwargs):
        kwargs.setdefault('item_id', 1)
        super().__init__(**kwargs)
        self.base_attributes['hp_heal'] = 50
        self.consumable = True
        
    def use(self, target):
        if target.hp >= target.max_hp:
            return -5
        target.heal(self.base_attributes['hp_heal'])
        return 1
```

### 2. 复合材料武器
```python
class MythrilSword(Item):
    def __init__(self, **kwargs):
        kwargs.update({
            'item_id': 102,
            'materials': {m_Mythril: 0.7, m_DragonScale: 0.3},
            'convert_type': 'weapon',
            'attributes_affected_by_material': True
        })
        super().__init__(**kwargs)
        self.base_attributes = {'atk': 20, 'crit_rate': 0.1}
        
    def use(self, target):
        # 作为装备使用时逻辑不同
        return -1  # 实际应在Equipment子类实现
```

---

## 注意事项

### 1. 开发规范
- 所有物品必须定义唯一`item_id`
- 材料占比总和必须≈100%（系统会自动修正）
- 修改材料后需调用`re_cal_material_bonus()`

### 2. 重要限制
```python
# 堆叠条件限制
item1 == item2 当且仅当：
- 所有非UUID属性相同
- is_stackable=True
```

### 3. 异常处理
| 错误情况        | 系统处理                      |
| --------------- | ----------------------------- |
| 材料占比和≠100% | 自动归一化处理                |
| 耐久度溢出      | 自动限制在[0, max_durability] |
| 价格负数        | 强制设为0                     |

---

## 附录

### 常量表（部分）
| 常量名         | 值   | 说明               |
| -------------- | ---- | ------------------ |
| ALL_BONUS      | list | 所有可用的属性类型 |
| ALL_RESISTANCE | list | 所有抗性类型       |

