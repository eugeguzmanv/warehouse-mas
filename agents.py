from mesa import Agent


class Box(Agent):
    """
    A box that needs to be stacked.
    It is a passive object and does not move on its own.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.is_stacked = False

    def step(self):
        pass


class Shelf(Agent):
    """
    A fixed location where boxes are stacked.
    """

    def __init__(self, unique_id, model, max_height=5):
        super().__init__(unique_id, model)
        self.stack_height = 0
        self.max_height = max_height

    def step(self):
        pass


class RobotAgent(Agent):
    """
    The Robot Agent that moves boxes to shelves.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.carrying_box = False
        self.movements_made = 0
        self.state = "RETRIEVING"  # States: RETRIEVING, STACKING

    def step(self):
        """
        The main decision loop (BDI architecture simplified).
        1. Perceive: Check internal state (carrying box?).
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
        # 1. Scan for boxes at current location
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for obj in cell_contents:
            if isinstance(obj, Box) and not obj.is_stacked:
                self.pick_up_box(obj)
                return

        # 2. Find closest known box
        target = self.find_closest_object(Box, lambda b: not b.is_stacked)

        # 3. Move towards it
        if target:
            self.move_towards(target.pos)
        else:
            self.random_move()  # Explore if no boxes found

    def execute_stacking_strategy(self):
        # 1. Check if at a shelf
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        shelf = None
        for obj in cell_contents:
            if isinstance(obj, Shelf):
                shelf = obj
                break

        # 2. If at valid shelf, place box
        if shelf and shelf.stack_height < shelf.max_height:
            self.place_box(shelf)
            return

        # 3. Find closest non-full shelf
        target = self.find_closest_object(
            Shelf, lambda s: s.stack_height < s.max_height
        )

        # 4. Move towards it
        if target:
            self.move_towards(target.pos)
        else:
            self.random_move()  # Should not happen if logic is correct, but safety fallback

    def find_closest_object(self, agent_type, condition=None):
        """
        Scans the grid for the closest object of type 'agent_type'
        that meets the optional 'condition'.
        """
        closest_dist = float("inf")
        closest_obj = None

        # In a real simulation, agents might have limited vision.
        # Here we assume shared knowledge for efficiency (or full vision).
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
        Simple greedy pathfinding with collision avoidance.
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

        # If blocked, wait (do nothing) or random move to unstuck
        self.random_move()

    def is_cell_available(self, pos):
        """
        Checks if a cell is free of obstacles (Walls/Other Robots).
        """
        if not self.model.grid.out_of_bounds(pos):
            contents = self.model.grid.get_cell_list_contents([pos])
            for obj in contents:
                if isinstance(obj, RobotAgent):
                    return False  # Collision!
            return True
        return False

    def random_move(self):
        """
        Moves to a random adjacent cell.
        """
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
        # Remove box from grid so it "disappears" into the robot inventory
        self.model.grid.remove_agent(box)
        # We don't remove it from the schedule so we can still track it if needed,
        # or we can just mark it as picked up.
        # For visualization, removing from grid is sufficient.

    def place_box(self, shelf):
        self.carrying_box = False
        shelf.stack_height += 1
        # Create a new box visual representation on the shelf (optional,
        # or just use the shelf color to indicate fullness)
        # For logic, we just increment shelf height.
