import json
import os
from queue import LifoQueue 
from datetime import datetime

from image_data import ImageData
from spade.behaviour import State

# --------------------------------------------- #
# BEHAVIOUR                                     #
# --------------------------------------------- #
STATE_INIT = "STATE_INITIALIZATION"
STATE_PERCEPTION = "STATE_PERCEPTION"
STATE_COGNITION = "STATE_COGNITION"
STATE_ACTION = "STATE_ACTION"
    
class StateInit(State):
    def __init__(self, shell):
        super().__init__()
        self.__shell = shell

    async def on_start(self):
        behaviour = self.agent.behaviours[0]
        # self.__image_socket = behaviour.image_socket
        # self.__commander = behaviour.commander
        # self.__commander = behaviour.commander
        # self.commander = Commander(self, self.command_socket)

        print(f"{self.agent.name}: Create command sent.")
        await self.agent.create_agent()
        
        self.agent.image_counter = 0
        # self.agent.images = LifoQueue()
        # self.agent.image_thread = image_manager.ImageManager(self.agent.name, self.__image_socket, 32768, self.agent.images)
        # self.agent.image_thread.daemon = True
        # self.agent.image_thread.start()
        # print(f"{self.agent.name}: ImageManager started.")

    async def run(self):
        print(f"{self.agent.name}: state {STATE_INIT}.")
        await self.__shell.init(self.agent)
        self.set_next_state(STATE_PERCEPTION)

class StatePerception(State):
    def __init__(self, shell):
        super().__init__()
        self.__shell = shell

    async def on_start(self):
        behaviour = self.agent.behaviours[0]
        # self.__commander = behaviour.commander
        
    async def run(self):
        print(f"{self.agent.name}: state {STATE_PERCEPTION}.")
        data = self.save_images()
        await self.__shell.perception(self.agent, data)
        self.set_next_state(STATE_COGNITION)

    def save_images(self):
        data = None
        if (not self.agent.image_queue.empty()):
            data = self.agent.image_queue.get()
            self.agent.image_counter += 1
            if (self.agent.folder_capacity_size > 0):
                if (not os.path.isdir(self.agent.image_folder_name)):
                    os.makedirs(self.agent.image_folder_name)
                self.agent.image_counter = self.agent.image_counter % (self.agent.folder_capacity_size + 1)
                if self.agent.image_counter == 0:
                    self.agent.image_counter = 1
                image_filename = f"{self.agent.name}_{data.camera_index}_{self.agent.image_counter}.jpg"
                with open(f"{self.agent.image_folder_name}/{image_filename}", "wb") as image_file:
                    image_file.write(data.image)
        return data


class StateCognition(State):
    def __init__(self, shell):
        super().__init__()
        self.__shell = shell

    async def on_start(self):
        behaviour = self.agent.behaviours[0]
        # self.__commander = behaviour.commander

    async def run(self):
        print(f"{self.agent.name}: state {STATE_COGNITION}.")
        await self.__shell.cognition(self.agent)
        self.set_next_state(STATE_ACTION)

class StateAction(State):
    def __init__(self, shell):
        super().__init__()
        self.__shell = shell

    async def on_start(self):
        behaviour = self.agent.behaviours[0]
        # self.__commander = behaviour.commander

    async def run(self):
        print(f"{self.agent.name}: state {STATE_ACTION}.")
        await self.__shell.action(self.agent)
        self.set_next_state(STATE_PERCEPTION)
