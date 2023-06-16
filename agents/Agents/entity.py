import asyncio
import importlib
import json
import socket
import sys
import time

from dataclasses import dataclass

from queue import LifoQueue 

from spade.agent import Agent
from spade.message import Message
from spade.template import Template

from entity_behaviour import AgentBehaviour, AgentImageBehaviour
from entity_state import STATE_INIT, STATE_PERCEPTION, STATE_COGNITION, STATE_ACTION
from entity_state import StateInit, StatePerception, StateCognition, StateAction
from commander import Axis

class EntityAgent(Agent):
    def __init__(self, agent_jid: str, password: str, folder_capacity_size: int, image_folder_name: str, enable_agent_collision: bool, prefab_name: str, starter_position: dict, fiveserver_jid: str, behaviour_path: str):
        Agent.__init__(self, agent_jid, password)
        self.folder_capacity_size = folder_capacity_size
        self.image_folder_name = image_folder_name
        self.agent_collision = enable_agent_collision
        self.prefab_name = prefab_name
        self.starter_position = starter_position
        self.__server_jid = fiveserver_jid
        self.__behaviour_path = behaviour_path

    async def setup(self):
        class_name = "EntityShell"
        behaviour_class_path = f"behaviours.{self.__behaviour_path}"
        behaviour_class = getattr(importlib.import_module(behaviour_class_path), class_name)
        
        fsm_behaviour = AgentBehaviour()

        # STATES
        fsm_behaviour.add_state(name=STATE_INIT, state=StateInit(behaviour_class), initial=True)
        fsm_behaviour.add_state(name=STATE_PERCEPTION, state=StatePerception(behaviour_class))
        fsm_behaviour.add_state(name=STATE_COGNITION, state=StateCognition(behaviour_class))
        fsm_behaviour.add_state(name=STATE_ACTION, state=StateAction(behaviour_class))

        # TRANSITIONS
        fsm_behaviour.add_transition(source=STATE_INIT, dest=STATE_PERCEPTION)
        fsm_behaviour.add_transition(source=STATE_PERCEPTION, dest=STATE_COGNITION)
        fsm_behaviour.add_transition(source=STATE_COGNITION, dest=STATE_ACTION)
        fsm_behaviour.add_transition(source=STATE_ACTION, dest=STATE_PERCEPTION)
        
        # MESSAGE TEMPLATE
        fsm_template = Template()
        fsm_template.set_metadata("five", "command")

        # ADD BEHAVIOUR
        self.add_behaviour(fsm_behaviour, fsm_template)
        print(f"{self.name}: FSM behaviour is ready.")

        # ADD IMAGE BEHAVIOUR
        image_template = Template()
        image_template.set_metadata("five", "image")
        self.image_queue = LifoQueue()
        self.add_behaviour(AgentImageBehaviour(), image_template)


    async def send_msg_to_server_and_wait(self, msg:str) -> str:
        """
        Send a message and waits for a response
        """
        message = Message(to=self.__server_jid)
        message.body = msg
        message.set_metadata("five", "command")
        await self.behaviours[0].send(message)
        reply = await self.behaviours[0].receive(sys.float_info.max)
        if reply:
            return reply.body
        return None

    async def send_command_to_server_and_wait(self, msg:dict) -> str:
        """
        Send a command and waits for a response
        """
        await self.send_command_to_server(msg)
        reply = await self.behaviours[0].receive(sys.float_info.max)
        if reply:
            return reply.body
        return None


    async def send_command_to_server(self, msg:dict) -> None:
        """
        Send a command 
        """
        encoded_msg = json.dumps(msg)
        message = Message(to=self.__server_jid)
        message.body = encoded_msg
        message.set_metadata("five", "command")
        await self.behaviours[0].send(message)


    async def create_agent(self) -> None:
        command = { 'commandName': 'create', 'data': [self.name, self.prefab_name] }
        if isinstance(self.starter_position, str):
            command['data'].append(self.starter_position)
        else:
            command['data'].append(json.dumps(self.starter_position))
            # command['data'].append(f"({position['x']} {position['y']} {position['z']})")
        command['data'].append(self.agent_collision)
        response = (await self.send_command_to_server_and_wait(command)) # .decode('utf-8')
        self.position = json.loads(response)
        # self.position = [float(x) for x in (self.position.split())[1:]]

    async def move_agent(self, position: dict) -> dict:
        # formatted_position = f"({position[0]} {position[1]} {position[2]})"
        command = { 'commandName': 'moveTo', 'data': [ json.dumps(position) ] }
        response = (await self.send_command_to_server_and_wait(command)) # .decode('utf-8')
        # msg = msg.replace(',', '.')
        # new_position = [float(x) for x in (msg.split())[1:]]
        return json.loads(response)

    async def fov_camera(self, camera_id: int, fov: float):
        data = [ f"{camera_id}", f"{fov}" ]
        cameraRotateCommand = { 'commandName': 'cameraFov', 'data': data }
        await self.send_command_to_server(cameraRotateCommand)

    async def move_camera(self, camera_id: int, axis: Axis, relative_position: float):
        data = [ f"{camera_id}", f"{axis}", f"{relative_position}" ]
        cameraRotateCommand = { 'commandName': 'cameraMove', 'data': data }
        await self.send_command_to_server(cameraRotateCommand)

    async def rotate_camera(self, camera_id: int, axis: Axis, degrees: float):
        data = [ f"{camera_id}", f"{axis}", f"{degrees}" ]
        cameraRotateCommand = { 'commandName': 'cameraRotate', 'data': data }
        await self.send_command_to_server(cameraRotateCommand)

    async def take_image(self, camera_id: int, image_mode: float):
        command = { 'commandName': 'image', 'data': [ f"{camera_id}", f"{image_mode}" ] }
        await self.send_command_to_server(command)

    async def change_color(self, r: float, g: float, b: float, a: float = 1):
        ''' Color must be normalized between [0, 1]'''
        color = { 'r': r, 'g': g, 'b': b, 'a': a }
        command = { 'commandName': 'color', 'data': [ json.dumps(color) ] }
        await self.send_command_to_server(command)
