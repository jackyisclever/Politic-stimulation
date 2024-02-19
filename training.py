import main as m
def performance(challenger_strategy, n =100, k=80, W=40):
    game = m.Game(n, k ,W, challenger_strategy = challenger_strategy)       # leader_strategy = m.Random_Strategy
    game.play(nTimes = 1000)
    count = game.history['challenger']
    return count/1000