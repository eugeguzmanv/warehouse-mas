from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from model import WarehouseModel
from agents import RobotAgent, Box, Shelf

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
            portrayal["text"] = "📦"
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

    return portrayal

# Grid Setup
grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)

# Statistics Chart
chart = ChartModule([
    {"Label": "Boxes Stacked", "Color": "Black"},
    {"Label": "Total Movements", "Color": "Red"}
], data_collector_name='datacollector')

# Server Setup
server = ModularServer(
    WarehouseModel,
    [grid, chart],
    "Multi-Agent Warehouse",
    {
        "M": 20, 
        "N": 20,
        "num_robots": UserSettableParameter("slider", "Number of Robots", 5, 1, 20),
        "num_boxes": UserSettableParameter("slider", "Number of Boxes", 20, 5, 50)
    }
)