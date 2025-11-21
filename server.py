from mesa.visualization.modules import CanvasGrid, TextElement
from mesa.visualization.ModularVisualization import ModularServer
from model import WarehouseModel
from agents import RobotAgent, Box, Shelf, Obstacle
import time

def agent_portrayal(agent):
    """
    Defines how agents look in the browser.
    """
    if agent is None:
        return

    portrayal = {}

    if isinstance(agent, RobotAgent):
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.8
        portrayal["Layer"] = 2
        portrayal["Filled"] = "true"
        
        if agent.carrying_box:
            portrayal["Color"] = "#FF0000" # Red if carrying
            portrayal["text_color"] = "white"
        else:
            portrayal["Color"] = "#0000FF" # Blue if empty

    elif isinstance(agent, Box):
        portrayal["Shape"] = "rect"
        portrayal["w"] = 0.6
        portrayal["h"] = 0.6
        portrayal["Layer"] = 1
        portrayal["Color"] = "#8B4513" # Brown 
        portrayal["Filled"] = "true"

    elif isinstance(agent, Shelf):
        portrayal["Shape"] = "rect"
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["Layer"] = 0
        portrayal["Filled"] = "true"
        # Gradient color based on fullness
        if agent.stack_height >= agent.max_height:
            portrayal["Color"] = "#000000" # Black if full
        else:
            portrayal["Color"] = "#CCCCCC" # Grey if space available
        
        portrayal["text"] = str(agent.stack_height)
        portrayal["text_color"] = "black"

    elif isinstance(agent, Obstacle):
        portrayal["Shape"] = "rect"
        portrayal["w"] = 0.9
        portrayal["h"] = 0.9
        portrayal["Layer"] = 1
        portrayal["Filled"] = "true"
        portrayal["Color"] = "#444444"  # Dark grey obstacle

    return portrayal

# Grid Setup
grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

# Simple text element to show total movements and running time
class MovementTimeElement(TextElement):
    """Displays total robot movements and elapsed running time."""

    def render(self, model):
        total_movements = sum(
            a.movements_made for a in model.schedule.agents if isinstance(a, RobotAgent)
        )
        # Use model.start_time if available, otherwise approximate with 0
        start = getattr(model, "start_time", None)
        if start is None:
            elapsed = 0.0
        else:
            elapsed = time.time() - start

        # Format elapsed as seconds with 1 decimal
        return f"Movements: {total_movements} — Elapsed: {elapsed:.1f}s"

movement_time = MovementTimeElement()

# Server Setup
server = ModularServer(
    WarehouseModel,
    [grid, movement_time],
    "Multi-Agent Warehouse",
    {
        "M": 20, 
        "N": 20,
        "num_robots": 5,
        "num_boxes": 20,
    }
)