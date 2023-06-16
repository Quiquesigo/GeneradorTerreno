import json
import time
import os

from entity import EntityAgent
from queue import Queue
from threading import Thread

from custom_typings import Config


def create_default_config_file(filename: str) -> dict[Config]:
    json_string = """
    {
        "fiveserver": {
            "name": "fiveserver",
            "at": "localhost"
        },
        "agents": [
            {
                "name": "agente1",
                "at": "localhost",
                "password": "xmppserver",
                "folderCapacitySize": 3,
                "imageFolderName": "captures",
                "enableAgentCollision": true,
                "prefabName": "Tractor",
                "position": {
                    "x": -2.6,
                    "y": 0.0,
                    "z": 0.0
                }
            },
            {
                "name": "agente2",
                "at": "localhost",
                "password": "xmppserver",
                "folderCapacitySize": 3,
                "imageFolderName": "captures",
                "enableAgentCollision": true,
                "prefabName": "Tractor",
                "position": "Spawner 1"
            }
        ]
    }
    """
    json_object = json.loads(json_string)
    write_json_file(filename, json_object)
    return json_object

def read_json_file(filename:str) -> dict:
    with open(filename, "r") as config_file:
        return json.load(config_file)

def write_json_file(filename:str, json_object:dict):
    with open(filename, "w") as config_file:
        json.dump(json_object, config_file, indent=4)

def setup_thread_agents(agents:list, simulator:dict, threads:list):
    entities = Queue() 
    for agent in agents:
        t = Thread(target=launch_agent, args=(agent, simulator, entities,))
        t.daemon = True
        t.name = agent['name']
        threads.append(t)
        t.start()
    return list(entities.queue)

def launch_agent(agent_data:dict, fiveserver:dict, entities:Queue):
    agent = EntityAgent(
        agent_jid = f"{agent_data['name']}@{agent_data['at']}", 
        password = agent_data['password'],
        folder_capacity_size = agent_data['folderCapacitySize'],
        image_folder_name = agent_data['imageFolderName'],
        enable_agent_collision = agent_data['enableAgentCollision'],
        prefab_name = agent_data['prefabName'],
        starter_position = agent_data['position'],
        fiveserver_jid = f"{fiveserver['name']}@{fiveserver['at']}",
        behaviour_path= agent_data['behaviour']
    )
    future = agent.start(auto_register = True)
    future.result()
    entities.put(agent)

def wait_for_agents(entities:list):
    alive = True
    while alive:
        for entity in entities:
            if entity.is_alive():
                alive = True
                break
            alive = False
        time.sleep(1)

def main():
    configuration_filename = "configuration.json"
    if os.path.isfile(configuration_filename):
        configuration = read_json_file(configuration_filename)
        fiveserver_config = configuration["fiveserver"]
        agents_config = configuration["agents"]
        threads = []
        entities = setup_thread_agents(agents_config, fiveserver_config, threads)
        try:
            wait_for_agents(entities)
        except KeyboardInterrupt:
            for entity in entities:
                entity.stop()
        for thread in threads:
            thread.join()
    else:
        default_config = create_default_config_file(filename)
        if (default_config):
            print(f"{configuration_filename} was not present and it is now created with a default configuration.")

if __name__ == "__main__":
    main()
