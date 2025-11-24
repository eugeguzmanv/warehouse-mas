from mesa import Agent


class Box(Agent): #Definition of the box

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.is_stacked = False

    def step(self):
        pass


class Shelf(Agent): #Definition of the shelves (default spawn spot)

    def __init__(self, unique_id, model, max_height=5):
        super().__init__(unique_id, model)
        self.stack_height = 0
        self.max_height = max_height

    def step(self):
        pass


class Obstacle(Agent): # Blocks of 3 that block the agents movements
    

    def __init__(self, unique_id, model, group_id=None):
        super().__init__(unique_id, model)
        self.group_id = group_id

    def step(self):
        pass


class RobotAgent(Agent): #The main agent that looks for and moves boxes

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.carrying_box = False
        self.movements_made = 0
        self.state = "RETRIEVING"  # States: RETRIEVING, STACKING

    def step(self):
        """
        The main decision loop:
        1. Roam: Move randomly until a box is found
        2. Decide: Choose target (Box or Shelf).
        3. Act: Move or Interact.
        """
        if self.carrying_box:
            self.state = "STACKING"
            self.execute_stacking_strategy()
        else:
            self.state = "RETRIEVING"
            self.execute_retrieval_strategy()

    def execute_retrieval_strategy(self):
        # Check for boxes at current location
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if isinstance(obj, Box) and not obj.is_stacked:
                self.pick_up_box(obj)
                return

        # Roam randomly until a box is found in the current cell. The agent knows where shelves are and will plan/move to them once a box is picked up.
  
        self.random_move()

    def execute_stacking_strategy(self):
        # Check if at a shelf
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        shelf = None
        for obj in cell_contents:
            if isinstance(obj, Shelf):
                shelf = obj
                break

        # If at valid shelf, place box
        if shelf and shelf.stack_height < shelf.max_height:
            self.place_box(shelf)
            return

        # Find closest non-full shelf
        target = self.find_closest_object(
            Shelf, lambda s: s.stack_height < s.max_height
        )

        # Move towards it
        if target:
            self.move_towards(target.pos)
        else:
            self.random_move()  # Should not happen if logic is correct,  fallback

    def find_closest_object(self, agent_type, condition=None):
        """
        Scans the grid for the closest object of type 'agent_type'
        that meets the optional 'condition'.
        """
        closest_dist = float("inf")
        closest_obj = None

        for agent in self.model.schedule.agents:
            if isinstance(agent, agent_type) and agent.pos is not None:
                if condition and not condition(agent):
                    continue

                # Calculate Manhattan distance
                dist = abs(self.pos[0] - agent.pos[0]) + abs(self.pos[1] - agent.pos[1])
                if dist < closest_dist:
                    closest_dist = dist
                    closest_obj = agent

        return closest_obj

    def move_towards(self, target_pos):
        """
        Greedy pathfinding with collision avoidance.
        """
        x_dir = 0
        y_dir = 0

        if target_pos[0] > self.pos[0]:
            x_dir = 1
        elif target_pos[0] < self.pos[0]:
            x_dir = -1

        if target_pos[1] > self.pos[1]:
            y_dir = 1
        elif target_pos[1] < self.pos[1]:
            y_dir = -1

        # Prioritize the axis with larger distance
        possible_moves = []
        if x_dir != 0:
            possible_moves.append((self.pos[0] + x_dir, self.pos[1]))
        if y_dir != 0:
            possible_moves.append((self.pos[0], self.pos[1] + y_dir))

        # Try to move
        for next_pos in possible_moves:
            if self.is_cell_available(next_pos):
                self.model.grid.move_agent(self, next_pos)
                self.movements_made += 1
                return

        # If blocked, wait or random move to unstuck
        self.random_move()

    def is_cell_available(self, pos): #Check if a cell is free of obstacles
       
        if not self.model.grid.out_of_bounds(pos):
            contents = self.model.grid.get_cell_list_contents([pos])
            for obj in contents:
                # Block movement into cells containing another robot or an obstacle
                if isinstance(obj, RobotAgent):
                    return False  # a collision would happen
                # Obstacle instances occupy cells and should block robots
                if isinstance(obj, Obstacle):
                    return False
            return True
        return False

    def random_move(self): #random movement to and adjacent cell
     
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=False, include_center=False
        )
        # Filter out occupied cells
        valid_steps = [p for p in possible_steps if self.is_cell_available(p)]

        if valid_steps:
            new_position = self.random.choice(valid_steps)
            self.model.grid.move_agent(self, new_position)
            self.movements_made += 1

    def pick_up_box(self, box):
        self.carrying_box = True
        # Remove box from grid so it's cell is now free
        self.model.grid.remove_agent(box)

    def place_box(self, shelf):
        """
        Attempt to place the carried box on the given shelf.
        If the shelf cell is currently occupied by an Obstacle, find an
        alternative shelf that has space and is not obstructed. If none
        is available, perform a random move to avoid deadlock.
        """
        # Ensure the shelf has a position
        if shelf.pos is None:
            # Shelf not on grid; cannot place here
            self.random_move()
            return

        # Check if the shelf cell contains an Obstacle
        cell_contents = self.model.grid.get_cell_list_contents([shelf.pos])
        for obj in cell_contents:
            if isinstance(obj, Obstacle):
                # Current shelf cell is obstructed. Find an alternative shelf
                alt = self.find_closest_object(
                    Shelf,
                    lambda s: s.stack_height < s.max_height
                    and s.pos is not None
                    and not any(isinstance(o, Obstacle) for o in self.model.grid.get_cell_list_contents([s.pos])),
                )

                if alt:
                    # Move towards alternative shelf (keep carrying box)
                    self.move_towards(alt.pos)
                else:
                    # No available shelf free of obstacles, try to unstuck
                    self.random_move()
                return

        # Place the box normally
        self.carrying_box = False
        shelf.stack_height += 1
      
