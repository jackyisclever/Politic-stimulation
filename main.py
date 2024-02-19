import math
from scipy.optimize import minimize
import random

W = 4000
PublicGoodPrice = 10
discounting_factor = 0.1

## Strategy
def Strategy(Leader, citizens):
  tax_rate = random.random()
  nPublicGood = random_integer = random.randint(0, 10000)
  nPrivateGood = random_integer = random.randint(0, 10000)
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
     raise ValueError("n should be less than number of remaining elements")

  sampled_elements = random.sample(remaining_elements, n)

  return sampled_elements

def generate_with_probability(p):
    if random.random() < p:
        return 1
    else:
        return 0


## Agents

class citizen:
  def __init__(self, name):
      self.name = name
      self.l = random.random()
      self.is_selector = False
      self.vote = 'leader' if self.is_selector else None
      self.affinity_to_current_leader = random.random() if self.is_selector else None
  
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
      if selector.name in Leader.winning_coalition:
        Leader_payoff = self.payoff(*Leader.policy, self.compute_leisure(Leader.policy), 1)
      else: 
        Leader_payoff = self.payoff(*Leader.policy, self.compute_leisure(Leader.policy), 0)

      Challenger_payoff = self.payoff(*Challenger.policy, self.compute_leisure(Challenger.policy) , generate_with_probability(W/len(selectors)))

      if Leader_payoff >= Challenger_payoff:
        vote = 'leader'
  # elif self.payoff(*Leader_policy) == self.payoff(*Challenger_policy) and M == challenger.tax_rate*E:  # to fix
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





## MAIN Game

class Game:
    def __init__(self,nCitizen,nSelectors):
      # self.citizens = []
      # self.leader = Leader() 
      # self.challenger = Challenger()
      self.citizens = self.Initize_citizen(nCitizen)
      self.selectors = self.As_slector(nSelectors)
      self.Leader = leader()
      self.Challenger = challenger()
      self.Voting_box = []

      self.affinities = None

    class leader(politic_player):
      def __init__(self):
        super().__init__()

      def offer_policy(self):
        policy = Strategy(Leader, citizens)
        self.update_policy(*policy)

      def select_winning_coalition(self, affinities, n):
          winning_coalition = find_highest_n_affinities(affinities, n)      # Return a list of index.
          self.winning_coalition = winning_coalition

    class challenger(politic_player): 
      def __init__(self):
        super().__init__()

      def offer_policy(self):
        policy = Strategy(Leader, citizens)
        self.update_policy(*policy)

      def select_winning_coalition(self, affinities, W):
          winning_coalition = [random.choice(Leader.winning_coalition)]
          all_indices = [i for i in range(len(selectors))]
          to_add = random_elements(all_indices, winning_coalition, W-1)
          winning_coalition += to_add
          self.winning_coalition = winning_coalition

    def Initize_citizen(self, nCitizen):
        citizen_list = [citizen(i) for i in range(nCitizen)]
        return citizen_list

    def As_slector(self, nSelectors):
      selectors = random.sample(self.itizens, nSelectors)  
      for selector in selectors:
        selector.is_selector = True

    def Announce_new_leader(self):
      leader_count = self.Voting_box.count('leader')
      challenger_count = self.Voting_box.count('challenger')
      if leader_count >= W:
        winner = self.Leader
        text = 'Leader'
      elif challenger_count >= W:
        winner = self.Challenger
        text = 'Challenger'
      else:
        winner = None
      print(f'Leader : {leader_count}')
      print(f'Challenger : {challenger_count}')
      print(f'Winner : {text}')

      return winner

    def play(self):
        self.affinities = [selector.affinity_to_current_leader for selector in self.selectors]

        self.Leader.select_winning_coalition(self.affinities,W)
        self.Challenger.select_winning_coalition(self.affinities,W)

        self.Leader.offer_policy()
        self.Leader.Challenger.offer_policy()

        self.Voting_box = []
        for selector in self.selectors:
          vote = selector.select_leader()
          self.Voting_box.append(vote)

        Leader = self.Announce_new_leader(self.Voting_box)

        for citizen in self.citizens:
            citizen.update_leisure(Leader.policy)

