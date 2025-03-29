from syst.init_pkg import *

class Team:
    def __init__(self,team_id:int,volume:int=1,now_mm:dict[int,Character]=None,**kwargs):
        self.team_id = team_id
        self.volume = volume
        if not now_mm:
            now_mm={}
        self.members=now_mm
        self.battle_handler='cpu'
    

    
    def sort_members(self):
        atmp={i+1:list(self.members.values())[i] for i in range(len(self.members))}
        self.members=atmp
        
    def add_member(self,ch:Character=None):
        if not ch:
            return False
        elif ch.team_id:
            debug_log.log_error(REMAIN_ERROR_MESSAGES[1])
            print(REMAIN_ERROR_MESSAGES[1])
            return False
        elif len(self.members)>=self.volume:
            debug_log.log_error(REMAIN_ERROR_MESSAGES[2])
            print(REMAIN_ERROR_MESSAGES[2])
            return False
        else:
            self.sort_members()
            self.members.update({len(self.members)+1:ch})
            ch.team_id=self.team_id
            debug_log.log_debug(f"ID为{self.team_id}的队伍添加了队员{ch}")
    def discard_member(self,idx:int=0):
        if not(idx in self.members):
            debug_log.log_error(REMAIN_ERROR_MESSAGES[3])
            return 
        if self.members[idx]:
            self.members[idx].team_id=0
        return self.members.pop(idx)

    def change_seat(self,idx1:int=0,idx2:int=0):
        if idx1 in self.members and idx2 in self.members:
            self.members[idx1],self.members[idx2]=self.members[idx2],self.members[idx1]
            return True
        return False
    
    def show(self):
        parts=[]
        parts.append(f"队伍 {TEAM_IDS[self.team_id]}:  |人数:{len(self.members)}/{self.volume}\n")
        for k,v in self.members.items():
            parts.append(f"{k}位次 {v}\n")
        print(''.join(parts))
        return 
            
            