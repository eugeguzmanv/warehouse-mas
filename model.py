from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import time
from agents import RobotAgent, Box, Shelf, Obstacle

class WarehouseModel(Model):
   # The environment for the simulation
    def __init__(self, M=20, N=20, num_robots=5, num_boxes=20):
        super().__init__()
        self.num_robots = num_robots
        self.num_boxes = num_boxes
       #Track time of exec
        self.start_time = time.time()
        # Bounded grid for warehouse
        self.grid = MultiGrid(M, N, False)  
        self.schedule = RandomActivation(self)
        self.running = True
        
        # Data Collection
        self.datacollector = DataCollector(
            model_reporters={
                "Total Movements": lambda m: sum([a.movements_made for a in m.schedule.agents if isinstance(a, RobotAgent)]),
                "Boxes Stacked": lambda m: sum([s.stack_height for s in m.schedule.agents if isinstance(s, Shelf)])
            }
        )

        # Fixed locations of the shelves
        shelf_positions = [(2, 2), (M-3, 2), (2, N-3), (M-3, N-3), (M//2, N//2)]
        for pos in shelf_positions:
            shelf = Shelf(self.next_id(), self)
            self.grid.place_agent(shelf, pos)
            self.schedule.add(shelf)

        # Place Obstacles in pre-defined coordinates
        obstacle_groups_coords = [
            [(1, 1), (1, 2), (1, 3)],
            [(3, 3), (4, 3), (5, 3)],
            [(7, 7), (7, 8), (7, 9)],
            [(10, 2), (10, 3), (10, 4)],
            [(15, 15), (15, 16), (15, 17)],
        ]

        for i, group in enumerate(obstacle_groups_coords):
            for pos in group:
                # Basic bounds check and simple conflict avoidance
                if 0 <= pos[0] < self.grid.width and 0 <= pos[1] < self.grid.height:
                    contents = self.grid.get_cell_list_contents([pos])
                    if any(isinstance(c, (Shelf, RobotAgent, Obstacle)) for c in contents):
                        # Skip placing on occupied/invalid cells.
                        continue
                    obs = Obstacle(self.next_id(), self, group_id=i)
                    self.grid.place_agent(obs, pos)
                    self.schedule.add(obs)

        # 2. Place Robots on random empty locations
        for i in range(self.num_robots):
            robot = RobotAgent(self.next_id(), self)
            self.place_randomly(robot)
            self.schedule.add(robot)

        # 3. Place Boxes on random empty locations
        for i in range(self.num_boxes):
            box = Box(self.next_id(), self)
            self.place_randomly(box)
            self.schedule.add(box)

    def place_randomly(self, agent):
       #Function to check if the cell is occupied by another agent or an obstacle
        while True:
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
           
            cell_contents = self.grid.get_cell_list_contents([(x, y)])
           
            if not any(isinstance(c, (Shelf, RobotAgent, Obstacle)) for c in cell_contents):
                self.grid.place_agent(agent, (x, y))
                break

    def step(self): #Run one iteration of the model
        
        self.datacollector.collect(self)
        self.schedule.step()
        
        # Check Completion Condition
        total_stacked = sum([s.stack_height for s in self.schedule.agents if isinstance(s, Shelf)])
        if total_stacked >= self.num_boxes:
            self.running = False
            print("All boxes stacked! Simulation stopping.")