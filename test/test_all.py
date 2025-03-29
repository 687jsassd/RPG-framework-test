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
from logging.handlers import SocketHandler
import inspect,gc

import time
import tracemalloc
import cProfile

def start_console_logger():
    # 启动新终端运行日志服务器
    if sys.platform == "win32":
        subprocess.Popen(f'start cmd /k python "{debugger_path}"', shell=True)
    
    # 配置Socket日志处理器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    socket_handler = SocketHandler('localhost', 9020)
    root_logger.addHandler(socket_handler)

def execute_statement(statement,vars):
    obj.log_info(f"执行语句: {statement}")
    try:
        exec(statement,{},vars)
    except Exception as e:
        obj.log_error(f"执行语句时发生错误: {e}")
        print(f"{RED}执行语句时发生错误: {e}{RESET}")

def clear_screen():
    if sys.platform == "win32":
        os.system('cls')
    else:
        os.system('clear')

def get_instance_ret_by_index(class_name, idx):
    """
    根据类名和索引获取对应的实例，并找出所有引用该实例的变量。
    
    :param class_name: 类名
    :param idx: 实例的索引
    :return: 对应的实例或 None
    """
    if class_name in global_vars and inspect.isclass(global_vars[class_name]):
        target_class = global_vars[class_name]
        instances = []
        # 遍历垃圾回收器跟踪的所有对象
        for objt in gc.get_objects():
            if isinstance(objt, target_class) and not isinstance(objt, type):
                instances.append(objt)
        
        if 1 <= idx <= len(instances):
            instance = instances[idx - 1]
            print(f"获取到的实例: {repr(instance)}")
            
            # 找出所有引用该实例的变量
            references = []
            for name, value in global_vars.items():
                if repr(value) == repr(instance):
                    references.append(name)
            
            if references:
                print(f"引用该实例的变量: {', '.join(references)}")
                obj.log_info(f"引用该实例{repr(instance)}的变量: {', '.join(references)}")
            else:
                print("没有找到引用该实例的变量。")
                obj.log_info(f"没有找到引用该实例{repr(instance)}的变量。")
            instance=None
            return references
        else:
            print(f"索引 {idx} 超出范围，当前类 {class_name} 有 {len(instances)} 个实例。")
            instance=None
            return 
    else:
        print(f"类 {class_name} 不存在")
        return 

def get_instance_by_index(class_name, idx):
    """
    根据类名和索引获取对应的实例
    """
    if class_name in global_vars and inspect.isclass(global_vars[class_name]):
        target_class = global_vars[class_name]
        instances = []
        # 遍历垃圾回收器跟踪的所有对象
        for objt in gc.get_objects():
            if isinstance(objt, target_class) and not isinstance(objt, type):
                instances.append(objt)
        
        if 1 <= idx <= len(instances):
            return instances[idx - 1]  # 修改点：直接返回实例对象
        print(f"索引 {idx} 超出范围")
    return None

def delete_references_to_instance(class_name, idx):
    """
    获取指定类的指定索引的对象，并把其所有引用设为 None
    """
    instance = get_instance_by_index(class_name, idx)
    if not instance:
        print("实例不存在")
        return

    # 获取所有引用该对象的变量
    referrers = gc.get_referrers(instance)
    variables = []
    
    # 遍历所有引用者
    for referrer in referrers:
        # 处理字典类型的引用（通常是模块/类的__dict__）
        if isinstance(referrer, dict):
            for key, value in referrer.items():
                if value is instance:
                    # 如果是全局变量
                    if referrer is global_vars:
                        print(f"找到全局变量引用: {key}")
                        variables.append(key)
                    # 如果是实例属性（需要更复杂处理）
                    else:
                        print(f"找到字典属性引用: {key} in {repr(referrer)}")
    
    # 设置为None
    for var_name in variables:
        if var_name in global_vars:
            global_vars[var_name] = None
            print(f"已清除全局变量: {var_name}")
            obj.log_info(f"已清除全局变量: {var_name}")
    instance = None
    # 强制垃圾回收
    gc.collect()
    print(f"已清除 {len(variables)} 个引用")
    obj.log_info(f"已清除 {len(variables)} 个引用")

set_debug_mode(True)  # 启用调试模式
start_console_logger()
    
# 示例游戏代码
obj = BaseClass()
obj.log_info("测试程序启动")  # 仅在DEBUG_MODE=True时记录
hero = Character("Hero")

global_vars=globals()
recent_operations=[]
objects_by_class = {}
atemp = None
while True:
    # 获取用户输入
    print("请输入Python语句（输入'END'结束多行输入,输入help以获得帮助）:")
    lines = []
    while True:
        line = input()
        if line.lower() == 'end':
            break
        lines.append(line)
    
    # 将所有行组合成一个完整的代码块
    statements = '\n'.join(lines)
    
    # 检查特别的命令
    if statements.lower().strip() == 'exit':
        print("退出程序")
        obj.log_info("退出程序")
        break
    elif statements.lower().strip() == 'vars':
        global_vars_copy = global_vars.copy()
        for name, objt in global_vars_copy.items():
            print(f"{name} = {objt}\n")
            
        obj.log_info("打印全局变量")
        recent_operations.append(f"打印全局变量")
        input("按任意键继续...")
        clear_screen()
        continue
    # 打印所有类
    elif statements.lower().strip() == 'classes':
        global_vars_copy = global_vars.copy()  # 创建global_vars的副本
        classes = []
        for name, objt in global_vars_copy.items():
            if inspect.isclass(objt):
                classes.append(name)
        for class_name in classes:
            print(class_name)
        obj.log_info("打印所有类")
        recent_operations.append(f"打印所有类")
        input("按任意键继续...")
        clear_screen()
        continue
    
    # 打印某个类的所有方法
    elif statements.lower().startswith('methods '):
        class_name = statements.split(' ')[1]
        if class_name in global_vars and inspect.isclass(global_vars[class_name]):
            methods = [method for method in dir(global_vars[class_name]) if callable(getattr(global_vars[class_name], method)) and not method.startswith("__")]
            print(f"Methods of {class_name}: {methods}")
            obj.log_info(f"打印类 {class_name} 的所有方法")
        else:
            print(f"类 {class_name} 不存在")
        input("按任意键继续...")
        clear_screen()
        continue
    
    elif statements.lower().startswith('objects '):
        parts = statements.strip().split()
        if len(parts) < 2:
            print("请输入完整的类名")
        else:
            class_name = parts[1]
            if class_name in global_vars and inspect.isclass(global_vars[class_name]):
                target_class = global_vars[class_name]
                instances = []
                # 遍历垃圾回收器跟踪的所有对象
                for objt in gc.get_objects():
                    if isinstance(objt, target_class) and not isinstance(objt, type):
                        instances.append(objt)

                print(f"\n类 [{class_name}] 的实例列表:")
                for idx, instance in enumerate(instances, 1):
                    print(f"{idx}. {repr(instance)}||{instance.name},UUID:{instance.uuid} ")

                # 记录到最近操作
                recent_operations.append(f"列出{class_name}实例({len(instances)}个)")
                obj.log_info(f"打印类 {class_name} 的实例列表")
            else:
                print(f"类 {class_name} 不存在")
        instance=None
        input("按任意键继续...")
        clear_screen()
        continue

    elif statements.lower().startswith('get_objects '):
        # 提取类名和索引
        parts = statements.split()
        if len(parts) == 3:
            class_name = parts[1]
            idx = int(parts[2])
            # 调用 get_instance_by_index 函数
            get_instance_ret_by_index(class_name, idx)
            obj.log_info(f"提取类 {class_name} 的实例列表第{idx}个对象")
        else:
            print("输入格式错误，应为 'get_objects <class_name> <index>'。")
        input("按任意键继续...")
        clear_screen()
        continue
    

    elif statements.lower().startswith('del_objects '):
            # 提取类名和索引
        parts = statements.split()
        if len(parts) == 3:
            class_name = parts[1]
            idx = int(parts[2])
            # 调用 delete_references_to_instance 函数
            obj.log_info(f"删除类 {class_name} 的实例列表第{idx}个对象(其所有引用被设为None)")
            delete_references_to_instance(class_name, idx)
        else:
            print("输入格式错误，应为 'del_objects <class_name> <index>'。")
        input("按任意键继续...")
        clear_screen()
        continue
       
    elif statements.lower().strip() == 'help':
        print("可用命令：exit - 退出,\n vars - 获取变量表,\n classes - 获取所有类,\n methods <类名> - 获取类的方法,\n objects <类名> - 获取类的所有对象,\n get_objects <类名> <索引>- 获取类的第索引个对象(需要先执行objects)并找出其所有引用,\n del_objects <类名> <索引> -删除类的第索引个对象(需要先执行objects),其引用将全部设为None,\n <Python语句>")
        obj.log_info("打印帮助信息")
        input("按任意键继续...")
        clear_screen()
        continue
    
    elif statements.lower() == 'end':
        print("忽略无效输入 'end'。")
        continue
    
    # 执行用户输入的语句
    execute_statement(statements, global_vars)
    recent_operations.append(statements)
    input("按任意键继续...")
    clear_screen()

    # 打印最近两次操作
    print("最近两次操作：")
    for operation in recent_operations[-2:]:
        print(operation)
    print("\n")