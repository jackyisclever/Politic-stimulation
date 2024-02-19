import math
import random

PublicGoodPrice = 10
discounting_factor = 0.1

## Strategy
def Strategy(Leader, citizens):
  tax_rate = random.random()
  nPublicGood = random.randint(0, 10000)
  nPrivateGood = random.randint(0, 10000)
  policy = (tax_rate,nPublicGood,nPrivateGood)
  return policy


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


## Agents

class citizen:
  def __init__(self, name, game):
      self.name = name
      self.l = random.random()
      self.is_selector = False
      self.vote = None
      self.affinity_to_current_leader = random.random() if self.is_selector else None

      self.game = game
  
  # r = tax_rate, x = nPublicGood, g = nPrivateGood
  def payoff(self,r,x,g,l,factor):      # factor = 0 or 1, = 0 if citizen in Leader.winning_coalition, =1 if citizen in Leader.winning_coalition
    y = (1-r)*(1-l)
    value = math.sqrt(x)+factor*math.sqrt(g)+math.sqrt(y)+math.sqrt(l)
    return value

  def compute_leisure(self, policy):
    l = 1/(2-policy[0])
    return l

  def update_leisure(self,policy):
    l = self.compute_leisure(policy)
    self.l = l

  def select_leader(self):
    if self.is_selector:
      if self.name in self.game.Leader.winning_coalition:
        Leader_payoff = self.payoff(*self.game.Leader.policy, self.compute_leisure(self.game.Leader.policy), 1)
      else: 
        Leader_payoff = self.payoff(*self.game.Leader.policy, self.compute_leisure(self.game.Leader.policy), 0)

      Challenger_payoff = self.payoff(*self.game.Challenger.policy, self.compute_leisure(self.game.Challenger.policy) , generate_with_probability(self.game.W/len(self.game.selectors)))

      if Leader_payoff >= Challenger_payoff:
        vote = 'leader'
  # elif self.payoff(*self.game.Leader_policy) == self.payoff(*self.game.Challenger_policy) and M == self.game.challenger.tax_rate*E:  # to fix
  #   vote = 'leader'
      else:
        vote = 'challenger'
      self.vote = vote
      return vote
    else:
       print('Unexpected, the current agent could not vote')

class politic_player:
    def __init__(self):
        self.winning_coalition = None       # Index list
        self.tax_rate = None                # float in [0,1], r
        self.nPublicGood = None             # Int, x
        self.nPrivateGood = None            # Int, g
        self.policy = (self.tax_rate,self.nPublicGood,self.nPrivateGood)

    def update_policy(self, tax_rate, nPublicGood, nPrivateGood):
      self.tax_rate = tax_rate
      self.nPublicGood = nPublicGood 
      self.nPrivateGood = nPrivateGood
      self.policy = (self.tax_rate, self.nPublicGood, self.nPrivateGood)

class leader(politic_player):
  def __init__(self,game):
    super().__init__()
    self.game = game

  def offer_policy(self):
    policy = Strategy(self.game.Leader, self.game.citizens)
    self.update_policy(*policy)

  def select_winning_coalition(self):
      winning_coalition = find_highest_n_affinities(self.game.affinities, self.game.W)      # Return a list of index.
      self.winning_coalition = winning_coalition

class challenger(politic_player): 
  def __init__(self,game):
    super().__init__()
    self.game = game

  def offer_policy(self):
    policy = Strategy(self.game.Leader, self.game.citizens)
    self.update_policy(*policy)

  def select_winning_coalition(self):
      winning_coalition = [random.choice(self.game.Leader.winning_coalition)]
      all_indices = [i for i in range(len(self.game.selectors))]
      to_add = random_elements(all_indices, winning_coalition, self.game.W-1)
      if len(to_add) != self.game.W-1:    # When no sufficient elemt from 'all_indices - winning_coalition'
         to_add += random_elements(self.game.Leader.winning_coalition, winning_coalition, self.game.W-1-len(to_add))
      winning_coalition += to_add
      # winning_coalition = random.sample(range(len(affinities)), W)
      self.winning_coalition = winning_coalition
     


## MAIN Game

class Game:
    def __init__(self, nCitizen, nSelectors, W):
      self.initialized = False
      self.nCitizen = nCitizen
      self.nSelectors = nSelectors
      self.history = {'leader': 0, 'challenger': 0, 'no_winner': 0}
      self.mute = False
      self.W = W 

    def initialize(self, nCitizen = None, nSelectors = None):
      if nCitizen == None:
        nCitizen = self.nCitizen
      if nSelectors == None:
        nSelectors = self.nSelectors

      self.citizens = self.Initize_citizen(nCitizen)
      self.selectors = self.As_slector(nSelectors)
      self.Leader = leader(self)
      self.Challenger = challenger(self)
      self.Voting_box = []

      self.affinities = [selector.affinity_to_current_leader for selector in self.selectors]
      self.initialized = True

    def Initize_citizen(self, nCitizen):
        citizen_list = [citizen(i,self) for i in range(nCitizen)]
        return citizen_list

    def As_slector(self, nSelectors):
      selectors = random.sample(self.citizens, nSelectors)  
      for selector in selectors:
        selector.is_selector = True
        selector.affinity_to_current_leader = random.random()
      return selectors

    def Announce_new_leader(self):
      leader_count = self.Voting_box.count('leader')
      challenger_count = self.Voting_box.count('challenger')
      if leader_count >= self.W:
        winner = self.Leader
        text = 'Leader'
        self.history['leader'] += 1
      elif challenger_count >= self.W:
        winner = self.Challenger
        text = 'Challenger'
        self.history['challenger'] += 1
        self.update_affinities
      else:
        winner = None
        text = 'No winner'
        self.history['no_winner'] += 1
      
      if self.mute is False:
        print(f'Leader : {leader_count} ; Policy : {self.Leader.policy}')
        print(f'Challenger : {challenger_count} ; Policy : {self.Challenger.policy}')
        print(f'Winner : {text}')

      return winner

    def update_affinities(self):
      for selector in self.selectors:
        selector.affinity_to_current_leader = random.random()
      self.affinities = [selector.affinity_to_current_leader for selector in self.selectors]

    def play(self):
        if self.initialized == False:
            self.initialize(self.nCitizen,self.nSelectors)

        self.Leader.select_winning_coalition()
        self.Challenger.select_winning_coalition()

        self.Leader.offer_policy()
        self.Challenger.offer_policy()

        self.Voting_box = []
        for selector in self.selectors:
          vote = selector.select_leader()
          self.Voting_box.append(vote)

        Leader = self.Announce_new_leader()
        
        if Leader is not None:
          for citizen in self.citizens:
              citizen.update_leisure(Leader.policy)

# game = Game(12000, 8000)