import pygame
import random
import math
from datetime import datetime

WIDTH, HEIGHT = 1800, 900
FPS = 30
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

n_clients = 2000
n_restaurants = 100
max_orders = 10
n_distributors = 300
dist_limit = 500**2

registry = []

class Agent:
  def __init__(self, id, x, y):
    self.id = id
    self.x = x
    self.y = y
  def update(self):
    pass
  def decide(self):
    pass

class RestaurantAgent(Agent):
  def __init__(self, id, x, y, dP):
    super().__init__(id, x, y) 
    self.orders = []
    self.statusOrders = []
    self.dP = dP
    
  def to_string(self):
    print('I am Restaurant',self.id, '- Orders:', self.orders, '- StatusOrders:', self.statusOrders, '- Speed', self.dP, f'Pos({self.x};{self.y})')

  def update(self):         
    if(len(self.statusOrders)):      
      for i in range(len(self.statusOrders)):        
        self.statusOrders[i] += self.dP
        if(self.statusOrders[i] >= 100): 
            self.statusOrders[i] = 100
            

  def decide(self):
    pass

class ClientAgent(Agent):
  def __init__(self, id, x, y, dH):
    super().__init__(id, x, y)     
    self.hunger = random.randint(0, 50)
    self.dH = dH
    self.status = 1

  def to_string(self):
    print('I am Client',self.id, '- Hunger:', self.hunger, f'Pos({self.x};{self.y})')

  def update(self):
    self.hunger += self.dH

  def decide(self):

    if(self.hunger >= 100 and self.status):
      global agentList
      Resagents = [agent for agent in agentList if (agent.__class__.__name__ == 'RestaurantAgent' and len(agent.statusOrders) < max_orders )]

      if len(Resagents) > 0:

        best_res = None
        best_dist = math.inf
        for ra in Resagents:
          dist = (ra.x - self.x)**2 + ((ra.y - self.y)**2)
          if dist < best_dist:
            best_dist = dist
            best_res = ra            
        
        if best_res != None:
          best_res.orders.append(self.id)
          best_res.statusOrders.append(0)
          self.status = 0
          now = datetime.now()
          text = f"{now} - Client {self.id} has placed order in Restaurant {best_res.id}"
          print(text)
          registry.append(text)

class DistributorAgent(Agent):
  def __init__(self, id, x, y, dV):
    super().__init__(id, x, y)     
    self.status = 0
    self.dV = dV
    self.xi = None
    self.yi = None
    self.target = None
    self.Order = None

  def to_string(self):    
    print(f'I am Distributor {self.id} - Pos({self.x};{self.y}) - Status: {self.status} - PosIni({self.xi};{self.yi}) - Target: {self.target}  - Order: {self.Order}')

  def update(self):
    if(self.status): 
      angle = math.atan2(self.target.y - self.yi, self.target.x - self.xi)           
      dX = self.dV*math.cos(angle)
      dY = self.dV*math.sin(angle)
    else:
      dX = random.randint(-5,5) * self.dV
      dY = random.randint(-5,5) * self.dV    
    self.x += dX
    self.y += dY
      

  def decide(self):
    global agentList
    if(self.status == 0):      
      Resagents = [agent for agent in agentList if (agent.__class__.__name__ == 'RestaurantAgent' and (100 in agent.statusOrders) and ( ((agent.x-self.x)**2 + (agent.y-self.y)**2 )) <= dist_limit )]

      if len(Resagents) > 0:

        best_res = None
        best_dist = math.inf
        for ra in Resagents:
          dist = (ra.x - self.x)**2 + ((ra.y - self.y)**2)
          if dist < best_dist:
            best_dist = dist
            best_res = ra            
        
        if best_res != None:
          self.status = 1

          self.target = best_res
          self.xi = self.x
          self.yi = self.y

          idxOrder = best_res.statusOrders.index(100)
          best_res.statusOrders.pop(idxOrder)
          self.Order = best_res.orders.pop(idxOrder)
    
    if(self.status == 1 and (abs(self.target.x - self.x) <= self.dV) and (abs(self.target.y - self.y) <= self.dV)):
      self.x = self.target.x
      self.y = self.target.y

      self.status = 2

      self.target = [agent for agent in agentList if (agent.__class__.__name__ == 'ClientAgent' and (agent.id == self.Order))][0]
      self.xi = self.x
      self.yi = self.y

    if(self.status == 2 and (abs(self.target.x - self.x) <= self.dV) and (abs(self.target.y - self.y) <= self.dV)):
      self.x = self.target.x
      self.y = self.target.y

      self.target.hunger = 0
      self.target.status = 1
      
      now = datetime.now()
      text = f"{now} - Distributor {self.id} has delivered order to Client {self.target.id}"
      print(text)
      registry.append(text)
      
      self.status = 0
      self.xi = None
      self.yi = None
      self.target = None
      self.Order = None

agentList = []
for i in range(n_restaurants): 
  r = RestaurantAgent(i, random.randint(20, WIDTH-20), random.randint(20, HEIGHT-20), random.randint(5, 15))
  agentList.append(r)
  
for i in range(n_clients):
  c = ClientAgent(i, random.randint(20, WIDTH-20), random.randint(20, HEIGHT-20), random.randint(1, 10)/50)
  agentList.append(c)
  
for i in range(n_distributors):
  d = DistributorAgent(i,  random.randint(20, WIDTH-20), random.randint(20, HEIGHT-20), (random.randint(1, 5)/5))
  agentList.append(d)



def main(): 
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                
                now = str(datetime.now())
                now=now.replace(".", "-")
                now=now.replace(":", "-")
                now=now.replace(" ", "")
                
                with open(f'Registro-{now}.txt', 'w') as f:
                  for line in registry:
                    f.write(line)
                    f.write('\n')
                run = False
        
        WIN.fill((0,0,0))
        random.shuffle(agentList)
        for a in agentList:
            if (a.__class__.__name__ == 'RestaurantAgent'):
                pygame.draw.rect(WIN,   (255, 0, 255), [a.x, a.y, 5, 5])
                
            if (a.__class__.__name__ == 'ClientAgent'):
                if(a.hunger<100):
                    pygame.draw.rect(WIN,   (0, 255, 0), [a.x, a.y, 3, 3])
                if(a.hunger>=100):
                    pygame.draw.rect(WIN,   (255, 0, 0), [a.x, a.y, 3, 3])
                
            if (a.__class__.__name__ == 'DistributorAgent'):
                pygame.draw.circle(WIN, (0, 0, 255), (a.x, a.y), 3)
            #a.to_string()
            a.update()
            a.decide()

        pygame.display.update()
    
    pygame.quit()
    
    
if __name__ == "__main__":
    main()