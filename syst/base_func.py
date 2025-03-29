from syst.CONSTANT_LIST import *
def ger_val_color(val: int = 0):
    if val > 0:
        return GREEN
    elif val < 0:
        return RED
    else:
        return WHITE

def get_float_val_color(value: int = 0):
            if value<=0.1:
                resi_color=GRAY
            elif value<=0.2:
                resi_color=RED
            elif value<=0.3:
                resi_color=ORANGE
            elif value<=0.4:
                resi_color=YELLOW
            elif value<=0.5:
                resi_color=GREEN
            elif value<=0.8:
                resi_color=CYAN
            elif value<=0.98:
                resi_color=BLUE
            else:
                resi_color=PURPLE+"★ "
            return resi_color
def get_quality_color(quality : int = 0):
    if quality == 1:
        return GREEN
    elif quality == 2:
        return CYAN
    elif quality == 3:
        return BLUE
    elif quality == 4:
        return BRIGHT_PURPLE
    elif quality == 5:
        return PURPLE
    elif quality == 6:
        return BRIGHT_ORANGE
    elif quality == 7:
        return ORANGE
    elif quality == 8:
        return MAGENTA
    elif quality == 9:
        return RED
    elif quality == 10:
        return DARK_GRAY
    elif quality >= 11:
        return GRAY
    else:
        return WHITE
    
def convert_colorful_text(txt: str, color: str = WHITE):
    # 定义一个函数convert_colorful_text，用于将文本添加颜色
    # 参数txt是字符串类型，表示要添加颜色的文本
    # 参数color是字符串类型，表示要添加的颜色，默认值为WHITE（假设WHITE是一个预定义的颜色常量）
    # 返回一个由颜色、文本和白色颜色拼接而成的字符串
    # 这样可以在终端或支持ANSI颜色代码的界面中显示带颜色的文本
    return color + txt + WHITE

# 删除对象
def delete_object(obj):
    # 找到所有引用这个对象的变量，并将它们设置为None
    for name, value in globals().items():
        if value is obj:
            globals()[name] = None

# 创建新的引用
def create_new_reference(obj, new_name):
    globals()[new_name] = obj

