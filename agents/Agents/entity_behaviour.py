import socket
import sys

from spade.behaviour import FSMBehaviour, CyclicBehaviour

from image_data import ImageData

class AgentBehaviour(FSMBehaviour):
    async def on_end(self):
        await self.agent.stop()

class AgentImageBehaviour(CyclicBehaviour):
    async def on_start(self):
        print(f"{self.agent.name}: init image behaviour.")

    async def on_end(self):
        print(f"{self.agent.name}: finished image behaviour.")
        await self.agent.stop()

    async def run(self):
        message = await self.receive(sys.float_info.max)
        if message:
            self.agent.image_queue.put(ImageData(message.body)) 
