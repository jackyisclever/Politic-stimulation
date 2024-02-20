import math
import random
import copy

"""
#######################
Understanding:
1. winning a little and winning a lot are both winning.
2. Summing the society welfare is not the same is different from summing the vote.
#######################
"""

## Tools

def find_highest_n_affinities(input_list, n):
    # 创建一个与输入列表相同长度的新列表，初始值为0
    output_list = [0] * len(input_list)

    # 找到输入列表中最大的n个数的索引
    indices = sorted(range(len(input_list)), key=lambda i: input_list[i], reverse=True)[:n]

    # # 将最大的n个数对应的索引位置设为1
    # for index in indices:
    #     output_list[index] = 1

    return indices

def random_elements(list1, list2, n):     #  Select n element that is in list1 but not in list2

  if not isinstance(list1, list):
     if not all(isinstance(x, int) for x in list1):
        raise TypeError("list1 elements must be int")

  if not isinstance(list2, list):
     raise TypeError("list2 must be list")

  remaining_elements = [elem for elem in list1 if elem not in list2]

  if n > len(remaining_elements):
    #  print(remaining_elements,n)
    #  raise ValueError("n should be less than number of remaining elements")
     return remaining_elements        ### Warning, ERROR MAY POSSIBLE !!!

  sampled_elements = random.sample(remaining_elements, n)

  return sampled_elements

def generate_with_probability(p):
    if random.random() < p:
        return 1
    else:
        return 0

## Key Objects

class Policy:
  def __init__(self, owner, tax_rate = None, nPublicGood = None, nPrivateGood = None, PrivateGood_agent_names = None):
    # Content
    self.tax_rate = tax_rate             # float in [0,1], r
    self.nPublicGood = nPublicGood       # Int, x
    self.nPrivateGood = nPrivateGood     # Int, g
    self.PrivateGood_agent_names = PrivateGood_agent_names    # List of index of citizens

  # Binding
    self.owner = owner
    self.game = self.owner.game

  def update(self, tax_rate, nPublicGood, nPrivateGood, PrivateGood_agent_names = None):
    self.tax_rate = tax_rate
    self.nPublicGood = nPublicGood
    self.nPrivateGood = nPrivateGood

    if PrivateGood_agent_names is not None:
      self.PrivateGood_agent_names = PrivateGood_agent_names
  
  def compute_leisure(self):
    l = 1/(2-self.tax_rate)
    return l

  def isFeasible(self):
    r = self.tax_rate
    x = self.nPublicGood
    g = self.nPrivateGood
    N = self.owner.game.nCitizen
    l = self.compute_leisure()
    n = len(self.PrivateGood_agent_names)

    if r * N * (1-l) - self.owner.game.PublicGoodPrice * x - n * g >=0:
      return True
    else:
      return False
    
  def payoff(self, citizen):
    # Compute the general term
    r = self.tax_rate
    x = self.nPublicGood
    g = self.nPrivateGood
    l = self.compute_leisure()
    y = (1-r) * (1-l)

    delta = self.game.discounting_factor

    # Check if the policy is Propose by Leader
    if self.owner.isLeader:
      try:
        factor = 1 if citizen.name in self.PrivateGood_agent_names else 0             # Check if recieve the PrivateGood; indicator factor = 0 or 1
      except:
        factor = 1 if citizen in self.PrivateGood_agent_names else 0             # This case is for inputing a integer as citizen instead of using a citizen object
    else:   # When Proposed by Challenger
      factor = self.game.W/self.game.nSelectors      # Simplified, in view of the V is Linear

    ####################################################################################################
      # # Define V based on the factor
      # def V(x,g,y,l):
      #   value = math.sqrt(x)+factor*math.sqrt(g)+math.sqrt(y)+math.sqrt(l)
      #   return value

      # # Define the continuation value based on the isLeader
      # def Z(x,g,y,l):
      #   value = (1/ (1- self.game.discounting_factor)) * V(x,g,y,l)
      #   return value

      # # Summary
      # value = V(x,g,y,l) + self.game.discounting_factor * Z(x,g,y,l)
    ####################################################################################################
   
    if self.isFeasible():
      value = (1/ 1- delta) * (math.sqrt(x)+factor*math.sqrt(g)+math.sqrt(y)+math.sqrt(l))
    else:
      v0 = 0
      value = v0 + (delta / (1- delta)) * (math.sqrt(x)+factor*math.sqrt(g)+math.sqrt(y)+math.sqrt(l))
  
    # value = (1/ 1- delta) * (math.sqrt(x)+factor*math.sqrt(g)+math.sqrt(y)+math.sqrt(l))
    return value

  def show(self):
    # return (self.tax_rate, self.nPublicGood, self.nPrivateGood, self.PrivateGood_agent_names
    return (self.tax_rate, self.nPublicGood, self.nPrivateGood, self.payoff(self.game.citizens[0]))

  def copy(self):
    return copy.deepcopy()

  # def toDict(self, all = False):
  #   if all:
  #     return {'tax_rate': self.tax_rate, 'nPublicGood': self.nPublicGood, 'nPrivateGood': self.nPrivateGood, 'PrivateGood_agent_names': self.PrivateGood_agent_names}
  #   else:
  #     return {'tax_rate': self.tax_rate, 'nPublicGood': self.nPublicGood, 'nPrivateGood': self.nPrivateGood}


## Strategy
def Random_Strategy(Leader, citizens):
  tax_rate = random.random()
  nPublicGood = random.randint(0, 10000)
  nPrivateGood = random.randint(0, 10000)
  output = (tax_rate,nPublicGood,nPrivateGood)
  return output


## Agents
class citizen:
  def __init__(self, name, game):
    # Neccessary property
      self.name = name    # The index while created
      self.l = random.random()
      self.is_selector = False

      # only for selector
      self.vote = None
      self.affinity_to_current_leader = random.random() if self.is_selector else None

      # Game binding
      self.game = game
  
  def payoff(self,policy):
    value = policy.payoff(self)
    return value

  def compute_leisure(self, policy):
    l = 1/(2-policy.tax_rate)
    return l

  def update_leisure(self,policy):
    l = self.compute_leisure(policy)
    self.l = l

  def select_leader(self):
    if self.is_selector:
      Leader_payoff = self.payoff(self.game.Leader.policy)
      Challenger_payoff = self.payoff(self.game.Challenger.policy)

      if Leader_payoff >= Challenger_payoff:
        vote = 'leader'
  # elif self.payoff(self.game.Leader_policy) == self.payoff(self.game.Challenger_policy) and M == self.game.challenger.tax_rate*E:  # to fix
  #   vote = 'leader'
      else:
        vote = 'challenger'
      self.vote = vote
      return vote
    else:
       print('Unexpected, the current agent could not vote')

class leader():
  def __init__(self,game, leader_strategy = Random_Strategy):
    self.game = game
    self.policy = Policy(self)
    self.policy_strategy = leader_strategy

    # Adiitional
    self.isLeader = True

    # Data
    self.winning_coalition = None

  def offer_policy(self):
    output = self.policy_strategy(self.game.Leader, self.game.citizens)        # output is in tuple form
    self.policy.update(*output)

  def select_winning_coalition(self):
      winning_coalition = find_highest_n_affinities(self.game.affinities, self.game.W) if self.game.quick is False else random.sample(self.game.selector_names, self.game.W)     # Return a list of index.
      self.winning_coalition = winning_coalition
      self.policy.PrivateGood_agent_names = self.winning_coalition

class challenger(): 
  def __init__(self,game, challenger_strategy = Random_Strategy):
    self.game = game
    self.policy = Policy(self)
    self.policy_strategy = challenger_strategy

    # Adiitional
    self.isLeader = False

    # Data
    self.winning_coalition = None

  def offer_policy(self):
    output = self.policy_strategy(self.game.Leader, self.game.citizens)        # output is in tuple form
    self.policy.update(*output)
    
  def select_winning_coalition(self):
      winning_coalition = [random.choice(self.game.Leader.winning_coalition)]

      to_add = random_elements(self.game.selector_names, winning_coalition, self.game.W-1)
      if len(to_add) < self.game.W-1:    # When no sufficient elemt from 'all_indices - winning_coalition'
        to_add += random_elements(self.game.Leader.winning_coalition, winning_coalition, self.game.W-1-len(to_add))         

      winning_coalition += to_add
      # winning_coalition = random.sample(range(len(affinities)), W)
      self.winning_coalition = winning_coalition
      self.policy.PrivateGood_agent_names = self.winning_coalition

class The_Public():
  def __init__(self, nCitizen, nSelector, game):
  # Neccessary property
    self.nCitizen = nCitizen
    self.nSelector = nSelector
    self.l = random.random()

    self.citizen_names = [i for i in range(nCitizen)]
    self.selector_names = random.sample(self.citizen_names, nSelector)

    # only for selector
    self.vote = None
    # self.affinity_to_current_leader = random.random() if self.is_selector else None

    # Game binding
    self.game = game
  
  def payoff(self,policy):     
    PG_selectors = [name for name in self.selector_names if name in policy.PrivateGood_agent_names]
    non_PG_selectors = [name for name in self.selector_names if name not in policy.PrivateGood_agent_names]

    PG_selector = random.choice(PG_selectors)
    non_PG_selector = random.choice(non_PG_selectors)
    n1 = len(PG_selectors)
    n2 = len(non_PG_selectors)

    PG_value = policy.payoff(PG_selector) * n1
    non_PG_value = policy.payoff(non_PG_selector) * n2

    value = (PG_value + non_PG_value) / (n1 + n2)       # (n1 + n2) is constant, hence in fact not quite matter if divide or not
    
    return value

  def compute_leisure(self, policy):
    l = 1/(2-policy.tax_rate)
    return l

  def update_leisure(self,policy):
    l = self.compute_leisure(policy)
    self.l = l

  def select_leader(self):
    Challenger_payoff = self.payoff(self.game.Challenger.policy)
    Leader_payoff = self.payoff(self.game.Leader.policy)

    if Leader_payoff >= Challenger_payoff:
      vote = 'leader'
  # elif self.payoff(self.game.Leader_policy) == self.payoff(self.game.Challenger_policy) and M == self.game.challenger.tax_rate*E:  # to fix
  #   vote = 'leader'
    else:
      vote = 'challenger'
    self.vote = vote
    return vote

  def __iter__(self):
      self.temp_mark_ygfkei = False
      return self

  def __next__(self):
      if not self.temp_mark_ygfkei:
         self.temp_mark_ygfkei = True
         return self
      else:
          raise StopIteration
    


## MAIN Game

class Game:
    def __init__(self, nCitizen, nSelectors, W, leader_strategy = Random_Strategy, challenger_strategy = Random_Strategy, quick = False):
      # input Temp.
      self.leader_strategy = leader_strategy
      self.challenger_strategy = challenger_strategy
      self.nCitizen = nCitizen
      self.nSelectors = nSelectors

      # Settings
      self.mute = False
      self.quick = quick
      self.record_policy = False

      # Superparameter
      self.W = W 
      self.PublicGoodPrice = 10
      self.discounting_factor = 0.1

      # Game data
      self.initialized = False
      self.history = {'leader': 0, 'challenger': 0, 'no_winner': 0}
      self.policy_history = {'leader policy': [], 'challenger policy': []} if self.record_policy else 'self.record_policy is now False.'

    def initialize(self, nCitizen = None, nSelectors = None):
      if nCitizen == None:
        nCitizen = self.nCitizen
      if nSelectors == None:
        nSelectors = self.nSelectors

      self.citizens = self.Initize_citizen(nCitizen)
      self.selectors = self.As_slector(nSelectors)
      self.Leader = leader(self, self.leader_strategy)
      self.Challenger = challenger(self, self.challenger_strategy)
      self.Voting_box = []

      self.affinities = [selector.affinity_to_current_leader for selector in self.selectors] if self.quick is False else None
      self.citizen_names = [citizen.name for citizen in self.citizens] if self.quick is False else self.citizens.citizen_names
      self.selector_names = [selector.name for selector in self.selectors] if self.quick is False else self.selectors.selector_names

      self.initialized = True

    def Initize_citizen(self, nCitizen):
        if self.quick is False:
          citizen_list = [citizen(i,self) for i in range(nCitizen)]
          return citizen_list
        else:
           object = The_Public(self.nCitizen, self.nSelectors, self)
           return object

    def As_slector(self, nSelectors):
      if self.quick is False:
        selectors = random.sample(self.citizens, nSelectors)  
        for selector in selectors:
          selector.is_selector = True
          selector.affinity_to_current_leader = random.random()
        return selectors
      else:
         return self.citizens   # Selector and citizen would become one object when use The_Public object

    def Announce_new_leader(self):
      ### Record and announce winner

      leader_count = self.Voting_box.count('leader')
      challenger_count = self.Voting_box.count('challenger')

      if leader_count > challenger_count and leader_count >= self.W  :
        winner = self.Leader
        text = 'Leader'
        self.history['leader'] += 1
      elif challenger_count > self.W and challenger_count != leader_count:
        winner = self.Challenger
        text = 'Challenger'
        self.history['challenger'] += 1
        self.update_affinities
      else:
        winner = None
        text = 'No winner'
        self.history['no_winner'] += 1
      
      if self.mute is False:
        print(f'Leader : {leader_count} ; Policy : {self.Leader.policy.show()}')
        print(f'Challenger : {challenger_count} ; Policy : {self.Challenger.policy.show()}')
        print(f'Winner : {text}')

    ### Record Policy
      if self.record_policy:
        leader_policy = self.Leader.policy.show()
        challenger_policy = self.Challenger.policy.show()
        self.policy_history['leader policy'].append(leader_policy)
        self.policy_history['challenger policy'].append(challenger_policy)

      return winner

    def Announce_new_leader_quick(self):
      ### Record and announce winner
      leader_count = self.Voting_box.count('leader')
      # challenger_count = self.Voting_box.count('challenger')

      if leader_count:
        winner = self.Leader
        text = 'Leader'
        self.history['leader'] += 1
      else:
        winner = self.Challenger
        text = 'Challenger'
        self.history['challenger'] += 1
        self.update_affinities
            
      if self.mute is False:
        print(f'Leader payoff : {self.citizens.payoff(self.Leader.policy)} ; Policy : {self.Leader.policy.show()}')
        print(f'Challenger payoff : {self.citizens.payoff(self.Challenger.policy)} ; Policy : {self.Challenger.policy.show()}')
        print(f'Winner : {text}')

    ### Record Policy
      if self.record_policy:
        leader_policy = self.Leader.policy.show()
        challenger_policy = self.Challenger.policy.show()
        self.policy_history['leader policy'].append(leader_policy)
        self.policy_history['challenger policy'].append(challenger_policy)

      return winner

    def update_affinities(self):
      for selector in self.selectors:
        selector.affinity_to_current_leader = random.random()
      self.affinities = [selector.affinity_to_current_leader for selector in self.selectors]

    def play(self, nTimes = 1):
        if self.initialized == False:
            self.initialize(self.nCitizen,self.nSelectors)
        for i in range(nTimes):
          # if self.quick is False:   # Not applicable when quick mode
          self.Leader.select_winning_coalition()
          self.Challenger.select_winning_coalition()

          self.Leader.offer_policy()
          self.Challenger.offer_policy()

          self.Voting_box = []
          for selector in self.selectors:
            vote = selector.select_leader()
            self.Voting_box.append(vote)

          new_leader = self.Announce_new_leader() if self.quick is False else self.Announce_new_leader_quick()
          
          if new_leader is not None:
            for citizen in self.citizens:
                citizen.update_leisure(new_leader.policy)


# game = Game(12000, 8000)