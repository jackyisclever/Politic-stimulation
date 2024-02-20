import main as m
def performance(challenger_strategy, n =100, k=80, W=40):
    game = m.Game(n, k ,W, challenger_strategy = challenger_strategy)       # leader_strategy = m.Random_Strategy
    game.mute = True
    game.play(nTimes = 1000)
    count = game.history['challenger']
    return count/1000

performance(m.Random_Strategy)



import torch
import torch.nn as nn
import torch.optim as optim

class PolicyNet(nn.Module):

  def __init__(self, state_dim, action_dim):
    super().__init__()
    
    self.fc1 = nn.Linear(state_dim, 256)
    self.fc2 = nn.Linear(256, 128) 
    self.fc3 = nn.Linear(128, 64)
    self.fc4 = nn.Linear(64, action_dim)
    
    self.dropout = nn.Dropout(p=0.1)
    
  def forward(self, state):
    
    x = F.relu(self.fc1(state))
    x = F.relu(self.fc2(x))
    x = self.dropout(x)
    
    x = F.relu(self.fc3(x))
    x = self.dropout(x)
    
    actions_values = self.fc4(x)
    return actions_values

  def get_action(self, state):
    # epsilon greedy logic

  def train_step(self, optimizer):
    # forward, loss, backward, optimize
    
  
def train():

  policy_net = PolicyNet(state_dim, action_dim)
  optimizer = optim.Adam(policy_net.parameters())

  for epoch in range(100):
    # sampling training data
    policy_net.train_step(optimizer)

if __name__ == '__main__':
  train()