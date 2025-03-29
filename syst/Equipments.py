from syst.init_pkg import *
#注意,在定义物品时,如想要自定义排序方式,需要加入__lt__方法,
#例子见Items的Heal_potion类
#如不加入,则按照物品名称的字典序排序
#改变常量表请在CONSTANT_LIST.py中修改



class Weapon(Equipment):
    """
    武器类，继承自装备类（Equipment），用于表示游戏中的武器。

    该类的主要功能是初始化武器的基本属性，并将其类型设置为'weapon'。

    构造函数参数:
    - **kwargs: 其他装备类（Equipment）的初始化参数。

    使用示例:
    >>> weapon = Weapon(name="剑")
    >>> print(weapon.name)
    '剑'

    注意事项:
    - 该类不直接定义武器的具体属性，而是通过继承装备类（Equipment）来定义。
    - 使用时需要确保传入的参数符合装备类的初始化要求。
    """
    def __init__(self,
        **kwargs):
        kwargs['equipment_type'] = 'weapon'
        super().__init__(**kwargs)
class Armor(Equipment):
    """
    Armor类表示装备中的护甲类型。

    该类继承自Equipment类，用于创建和管理护甲装备。护甲装备具有特定的属性，如防御值、重量等，这些属性可以通过构造函数的参数进行设置。

    核心功能:
    - 初始化护甲装备的基本属性。
    - 继承并扩展Equipment类的功能。

    使用示例:

    构造函数参数:
    - **kwargs: 关键字参数，用于设置护甲装备的各种属性。例如，名称(name)、防御值(defense)、重量(weight)等。

    特殊使用限制或潜在的副作用:
    - 无特殊使用限制或潜在的副作用。
    """
    def __init__(self,
        **kwargs):
        kwargs['equipment_type'] = 'armor'
        super().__init__(**kwargs)
class Accessory(Equipment):
    """
    Accessory类表示装备中的配件，继承自Equipment类。

    该类用于创建配件类型的装备对象，通过设置equipment_type为'accessory'来区分其他类型的装备。

    构造函数参数:
    - kwargs: 其他装备相关的参数，会被传递给父类Equipment的构造函数。

    使用示例:
    >>> accessory = Accessory(name="魔法戒指")
    >>> print(accessory.name)
    魔法戒指

    注意事项:
    - 该类主要用于创建配件类型的装备，不包含具体的装备功能或属性。
    - 所有装备相关的参数都会传递给父类Equipment，因此需要确保这些参数符合Equipment类的需求。
    """
    def __init__(self,
        **kwargs):
        kwargs['equipment_type'] = 'accessory'
        super().__init__(**kwargs)
