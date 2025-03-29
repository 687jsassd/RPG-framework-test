from syst.Teams import *
from syst.base_func import *
class BattleSystem:
    def __init__(self,team1=None,team2=None,place=None,special=None):
        if not team1:
            team1=Team()
        if not team2:
            team2=Team()
        self.team1=team1
        self.team2=team2
        self.characters=[team1[i] for i in team1.members if team1[i]].extend([team2[i] for i in team2.members if team2[i]])
        self.id_characters={i:self.characters[i] for i in len(self.characters)}
        #时序
        self.battle_speed=1
        self.tick_time=0.3
        #时序上限
        self.limit_tick=2500
        self.current_tick=0
        #时序条上限(下限为0)
        self.max_time=50
        self.character_times={self.characters[i]:i for i in len(self.characters)}    
    @property
    def tick_time(self):
        return 0.3/min(6,max(0.5,self.battle_speed))
    
    def change_battle_speed(self,spd):
        self.battle_speed=min(6,max(0.5,spd))
        debug_log.log_debug(f'设置战斗速度为{self.battle_speed}')
        print(f'设置战斗速度为{self.battle_speed}')
        
    def update_moving_speed(self):
        atmp=self.character_times.copy()
        atmp.sort(key=lambda x:x.final_spd,reverse=True)
        cutoff=len(atmp)//2
        for idx,i in atmp:
            if idx<cutoff:
                i.moving_speed=1
            else:
                i.moving_speed=2
    #①角色的集气条步进
    def update_character_time_line(self):
        for i in self.characters:
            self.character_times[i]+=i.final_moving_speed
            self.character_times[i]=max(self.max_time,self.character_times[i])
    #②角色的集气条调整（不大于上限），获取即将行动角色
    def check_action_character(self) ->List[Character]:
        action_characters=[]
        for i in self.characters:
            if self.character_times[i]==self.max_time:
                 action_characters.append(i)
        action_characters.sort(reverse=True,key=lambda x:x.final_spd)
        return action_characters
    #③处理按时序或者回合数触发和持续的状态效果和被动技能和法术吟唱等，并刷新角色状态、属性和存活
    #FIXME
        """⑤行动流程
5.1：准备阶段：处理在准备阶段触发和持续的状态效果和被动技能和法术吟唱等
5.2：选择行动：如果是玩家控制，就列出可能的行动，让玩家选择然后进入分支进行处理，分支会发送特定消息到实际行动阶段的处理数组、结束阶段控制回退格数的数组等
5.3：效果处理阶段：按照入组的顺序，依次处理行动。对于伤害、回复值等均发送到伤害结算阶段的数组。如有在本阶段触发的状态效果、被动技能等，则进行处理（如“使对方下一次行动无效化”的状态异常的处理）
5.4：伤害结算阶段：进行伤害结算并应用到角色上。如有在本阶段触发的状态效果、被动技能等，则进行处理（如“20%概率减伤50%，10%概率额外受伤100%，10%概率由攻击者承受伤害”的复杂被动技能的处理）
5.5结束阶段：进行角色的格数回退，时序停滞，回合数增加等操作。如有在本阶段触发的状态效果、被动技能等，则进行处理。_summary_
        """
    def action(self,ch:Character,mode='player'):
        def wait(ch):
            print(f"{ch}等待...")
            self.character_times[ch]-=3
        def normal_attack(ch):
            while True:
                print('选择攻击对象:')
                for i in self.id_characters.keys():
                    print(f'{i}:{self.id_characters[i]}')
                ipt=input()
                if ipt not in self.id_characters.keys():
                    print('未知对象')
                else:
                    break
            print(f'{ch}对{self.id_characters[ipt]}使用普通攻击')
            self.character_times[ch]-=3
            self.character_times[self.id_characters[ipt]]-=1
            
            
        possible_actions={0:'等待',1:'普通攻击',2:'防御',3:'使用物品',4:'休息'}
        #技能？
        if ch.a_skills:
            possible_actions[possible_actions.keys()[-1]+1]='使用技能'
        #查看被动技能
        if ch.p_skills:
            possible_actions[possible_actions.keys()[-1]+1]='查看被动技能'
        #查看自身状态
        if ch.status:
            possible_actions[possible_actions.keys()[-1]+1]='查看自身状态'
        if mode=='player':
            while True:
                print(f'{ch}选择行动:')
                for i in possible_actions.keys():
                    print(i,':',possible_actions[i])
                ipt=input('::')
                if ipt not in possible_actions.keys():
                    print("未知操作")
                else:
                    break
            
            
            
    #④排序即将行动角色，对每个角色依次进入行动流程
    def process_action(self,action_characters=None):
        for i in action_characters:
            self.action(i,i.battle_handler)
    
    
            
        
        
                