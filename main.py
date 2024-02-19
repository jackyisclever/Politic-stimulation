W = 4000
PublicGoodPrice = 10
discounting_factor = 0.1

class Game:
    def __init__(self,nCitizen,nSelectors):
      self.citizens = self.Initize_citizen(nCitizen)
      self.selectors = self.As_slector(nSelectors)
      self.Leader = leader()
      self.Challenger = challenger()
      self.Voting_box = []

      self.affinities = None


    def Initize_citizen(self, nCitizen):
        citizen_list = [citizen(i) for i in range(nCitizen)]
        return citizen_list

    def As_slector(self, nSelectors):
        To_be_selector = self.citizens[:nSelectors]
        selectors = [selector(citizen) for citizen in To_be_selector]
        self.citizens = selectors + self.citizens[nSelectors:]
        return selectors

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