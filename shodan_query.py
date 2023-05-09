import shodan
import pandas as pd
import os
import subprocess
import time
from dotenv import load_dotenv
import single_query
import sys
import random

def motd_to_string(motd):
    # If the dictionary only has a 'text' key, return its value
    if 'text' in motd and 'extra' not in motd:
        return motd['text']
    
    # If the dictionary doesn't have an 'extra' key or the 'extra' list is empty, return "A Minecraft server"
    if 'extra' not in motd or not motd['extra']:
        return "A Minecraft server"
    
    # Initialize an empty string to hold the result
    result = ''
    
    # Iterate over each element in the 'extra' list
    for element in motd['extra']:
        # If the element has a 'text' key, append its value to the result string
        if 'text' in element:
            result += element['text']
    
    # Return the result string
    return result

load_dotenv()

api_key = os.getenv('SHODAN_KEY')
api = shodan.Shodan(api_key)

data_exists = os.path.exists("database.csv")
minecraft_server_data = pd.DataFrame(columns=['IP','Port','Protocol','Software','MOTD', 'Forge', 'Icon'])
if data_exists:
    print('Loading current database...')
    minecraft_server_data = pd.read_csv("database.csv")
    print('Loaded ' + str(len(minecraft_server_data.index)) + " servers.")

counter = 0

if len(sys.argv) == 2:
    if sys.argv[1] == 'update':
        saved_ips = minecraft_server_data['IP']
        for ip in saved_ips:
            single_query.update_server_info(ip_address=ip)
            time.sleep(5)

try:
    results = api.search("\"Minecraft Server:\"")
    for result in results["matches"]:
        ip_address = result['ip_str']
        port = result['port']

        # if we have the IP saved, ignore it and continue
        already_saved = (minecraft_server_data['IP'] == ip_address).any()
        if already_saved:
            continue

        # only continue if it's a minecraft server
        if 'minecraft' not in result:
            continue

        minecraft_info = result['minecraft']
        description = minecraft_info['description']
        protocol, server_software = minecraft_info['version']['protocol'], minecraft_info['version']['name']

        # track if the server is using forge
        is_forge = 0
        if 'forgeData' in minecraft_info:
            is_forge = 1

        # see if the server has an icon set
        icon = "none"
        if 'favicon' in minecraft_info:
            icon = minecraft_info['favicon']

        print('Adding ' + ip_address)
        counter = counter + 1

        # build the data to add
        new_server_data = {'IP':ip_address, 'Port':port, 'Protocol':protocol, 'Software':server_software, 'MOTD': motd_to_string(description), 'Forge': is_forge, 'Icon': icon}
        
        # add the new data
        new_row_df = pd.DataFrame([new_server_data])
        minecraft_server_data = pd.concat([minecraft_server_data, new_row_df], ignore_index=True)
except shodan.APIError as e:
    print("Error: %s" % e)

minecraft_server_data.to_csv("database.csv", index=False)

if counter > 0:
    print('Added ' + str(counter) + ' new servers.')
    print('New total: ' + str(len(minecraft_server_data.index)) + ' servers.')

# only join servers from 1.8 to 1.19 since that's what Mineflayer supports
# filter out forge servers since we can't join them
mc_versions = [47, 107, 108, 109, 110, 210, 315, 316, 335, 338, 340, 393, 401, 404, 477, 480, 485, 490, 498, 573, 575, 578, 735, 736, 751, 753, 754, 755, 756, 757, 758, 759]
servers = minecraft_server_data[(minecraft_server_data['Protocol'].isin(mc_versions)) & (minecraft_server_data['Forge'] == 0)]
# randomize the rows for fun
servers = servers.sample(frac=1, random_state=random.randint(1,500))
for index, row in servers.iterrows():
    ip_address = row['IP']
    port = row['Port']
    version = row['Protocol']
    # build the command to run the node script to join
    print('Trying ' + str(ip_address) + ':' + str(port) + ' with version ' + str(version))
    cmd = ['node', 'join_server.js', str(ip_address), str(port)]
    result = subprocess.Popen(cmd)
    result.wait()
    # sleep for 20 seconds so we don't ratelimit ourself
    time.sleep(20)