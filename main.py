import math
import random

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

  def update(self, tax_rate, nPublicGood, nPrivateGood, PrivateGood_agent_names = None):
    self.tax_rate = tax_rate
    self.nPublicGood = nPublicGood
    self.nPrivateGood = nPrivateGood

    if PrivateGood_agent_names is not None:
      self.PrivateGood_agent_names = PrivateGood_agent_names

  def make_sense(self):
      if self.tax_rate is None or self.nPublicGood is None or self.nPrivateGood is None:
          return False
      elif self.tax_rate < 0 or self.tax_rate > 1 or self.nPublicGood < 0 or self.nPrivateGood < 0:
          return False
      else:
          return True
    
  def show(self):
    # return (self.tax_rate, self.nPublicGood, self.nPrivateGood, self.PrivateGood_agent_names
    return (self.tax_rate, self.nPublicGood, self.nPrivateGood)

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

    r = policy.tax_rate
    x = policy.nPublicGood
    g = policy.nPrivateGood

    if policy.owner.isLeader:
      factor = 1 if self.name in policy.PrivateGood_agent_names else 0      # factor = 0 or 1, = 0 if citizen in Leader.winning_coalition, =1 if citizen in Leader.winning_coalition
    else:
      p = self.game.W/self.game.nSelectors
      factor = generate_with_probability(p)
    l = self.compute_leisure(policy)
    y = (1-r) * (1-l)

    value = math.sqrt(x)+factor*math.sqrt(g)+math.sqrt(y)+math.sqrt(l)
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
    r = policy.tax_rate
    x = policy.nPublicGood
    g = policy.nPrivateGood

    if policy.owner.isLeader:     # Can directly do here in view of the linearity of the payoff function
      PG_selector = [name for name in self.selector_names if name in policy.PrivateGood_agent_names]
      factor = len(PG_selector)/len(self.game.selector_names)      
    else:
      factor = self.game.W/self.game.nSelectors

    l = self.compute_leisure(policy)
    y = (1-r) * (1-l)

    value = math.sqrt(x)+factor*math.sqrt(g)+math.sqrt(y)+math.sqrt(l)
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

      # Superparameter
      self.W = W 
      self.PublicGoodPrice = 10
      self.discounting_factor = 0.1

      # Game data
      self.initialized = False
      self.history = {'leader': 0, 'challenger': 0, 'no_winner': 0}

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

      return winner

    def Announce_new_leader_quick(self):
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