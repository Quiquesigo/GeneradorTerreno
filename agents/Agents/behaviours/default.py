from email.message import Message
import time
import os

from commander import Axis, ImageMode
from spade.agent import Agent
from spade.message import Message

from image_data import ImageData

class EntityShell:

    async def init(agent: Agent):
        behaviour = agent.behaviours[0]
        agent.total_moves = 16 #* 5 + 4
        agent.distancex = 6
        agent.distancey = 3
        agent.moves = 0
        agent.roads = 0
        if agent.name == "agente1":
            await agent.change_color(0.5, 0.5, 0, 0.8)
        else:
            await agent.change_color(0.5, 0, 0, 0.8)
        await agent.move_camera(0, Axis.Y, -1)
        await agent.fov_camera(0, 7)
        time.sleep(4)

    async def perception(agent: Agent, data: ImageData):
        await agent.change_color(1, 0, 0, 0.8)
        agent.image_data = data
        time.sleep(1)

    async def cognition(agent: Agent):
        await agent.change_color(0, 1, 0, 0.8)
        time.sleep(1)

    async def action(agent: Agent):
        await agent.change_color(0, 0, 1, 0.8)
        if agent.moves < agent.total_moves:
            agent.moves += 1
            if agent.moves % 17 != 0:
                await EntityShell.move_forward(agent, agent.roads)
                await EntityShell.take_picture(agent)
            else:
                agent.roads += 1
                camera_sign = -1 if agent.roads % 2 == 0 else 1
                await agent.move_camera(0, Axis.Z, 0.56 * camera_sign)
                await EntityShell.move_next_road(agent, agent.roads)
        else:
            time.sleep(1)

    async def move_forward(agent: Agent, road_number: int = 0):
        position = agent.position.copy()
        amount = agent.distancey
        if road_number % 2 == 1:
            amount = -amount
        position['z'] += amount
        agent.position = await agent.move_agent(position)

    async def move_next_road(agent: Agent, road_number: int = 0):
        space = agent.distancey * 3
        position = agent.position.copy()
        if road_number % 2 == 1:
            position['z'] += space
        else:
            position['z'] -= space
        position['x'] += agent.distancex
        agent.position = await agent.move_agent(position)
        position = agent.position.copy()
        position['x'] += agent.distancex
        if road_number % 2 == 1:
            position['z'] -= space - agent.distancey
        else:
            position['z'] += space - agent.distancey
        agent.position = await agent.move_agent(position)

    async def take_picture(agent: Agent):
        await agent.rotate_camera(0, Axis.Y, 90)
        time.sleep(1)
        await agent.take_image(0, ImageMode.INSTANT)

