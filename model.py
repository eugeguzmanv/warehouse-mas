from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import RobotAgent, Box, Shelf

class WarehouseModel(Model):
    """
    The Simulation Model Environment.
    """
    def __init__(self, M=20, N=20, num_robots=5, num_boxes=20):
        super().__init__()
        self.num_robots = num_robots
        self.num_boxes = num_boxes
        self.grid = MultiGrid(M, N, True) # Torus=True for easier movement, or False for walls
        self.schedule = RandomActivation(self)
        self.running = True
        
        # Data Collection
        self.datacollector = DataCollector(
            model_reporters={
                "Total Movements": lambda m: sum([a.movements_made for a in m.schedule.agents if isinstance(a, RobotAgent)]),
                "Boxes Stacked": lambda m: sum([s.stack_height for s in m.schedule.agents if isinstance(s, Shelf)])
            }
        )

        # 1. Place Shelves (Fixed Locations - e.g., corners and middle)
        shelf_positions = [(2, 2), (M-3, 2), (2, N-3), (M-3, N-3), (M//2, N//2)]
        for pos in shelf_positions:
            shelf = Shelf(self.next_id(), self)
            self.grid.place_agent(shelf, pos)
            self.schedule.add(shelf)

        # 2. Place Robots (Random Empty Locations)
        for i in range(self.num_robots):
            robot = RobotAgent(self.next_id(), self)
            self.place_randomly(robot)
            self.schedule.add(robot)

        # 3. Place Boxes (Random Empty Locations)
        for i in range(self.num_boxes):
            box = Box(self.next_id(), self)
            self.place_randomly(box)
            self.schedule.add(box)

    def place_randomly(self, agent):
        """
        Helper to place agent in an empty cell.
        """
        while True:
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            # Ensure we don't spawn on top of a shelf or robot
            cell_contents = self.grid.get_cell_list_contents([(x, y)])
            if not any(isinstance(c, (Shelf, RobotAgent)) for c in cell_contents):
                self.grid.place_agent(agent, (x, y))
                break

    def step(self):
        """
        Run one step of the model.
        """
        self.datacollector.collect(self)
        self.schedule.step()
        
        # Check Completion Condition
        total_stacked = sum([s.stack_height for s in self.schedule.agents if isinstance(s, Shelf)])
        if total_stacked >= self.num_boxes:
            self.running = False
            print("All boxes stacked! Simulation stopping.")