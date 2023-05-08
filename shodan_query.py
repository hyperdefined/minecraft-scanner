import shodan
import pandas as pd
import os
import subprocess
import time
from dotenv import load_dotenv

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
minecraft_server_data = pd.DataFrame(columns=['IP','Port','Protocol','Software','MOTD'])
if data_exists:
    print('Loading current database...')
    minecraft_server_data = pd.read_csv("database.csv")

try:
    results = api.search("\"Minecraft Server:\" ")
    for result in results["matches"]:
        ip_address = result['ip_str']
        port = result['port']

        # only continue if it's a minecraft server
        if 'minecraft' not in result:
            continue

        minecraft_info = result['minecraft']
        description = minecraft_info['description']
        protocol, server_software = minecraft_info['version']['protocol'], minecraft_info['version']['name']

        # check to see if we have it saved already
        ip_query = minecraft_server_data[minecraft_server_data['IP'] == ip_address]
        # update the data
        if len(ip_query) > 0:
            print('Updating data for IP ' + ip_address)
            for index, row in ip_query.iterrows():
                minecraft_server_data.at[index, 'Port'] = port
                minecraft_server_data.at[index, 'Protocol'] = protocol
                minecraft_server_data.at[index, 'Software'] = server_software
                minecraft_server_data.at[index, 'MOTD'] = description
            continue    

        print('Adding ' + ip_address)
        new_server_data = {'IP':ip_address, 'Port':port, 'Protocol':protocol, 'Software':server_software, 'MOTD': motd_to_string(description)}
        new_row_df = pd.DataFrame([new_server_data])
        minecraft_server_data = pd.concat([minecraft_server_data, new_row_df], ignore_index=True)
except shodan.APIError as e:
    print("Error: %s" % e)

minecraft_server_data.to_csv("database.csv", index=False)
mc_versions = [47, 107, 108, 109, 110, 210, 315, 316, 335, 338, 340, 393, 401, 404, 477, 480, 485, 490, 498, 573, 575, 578, 735, 736, 751, 753, 754, 755, 756, 757, 758, 759]
servers = minecraft_server_data[minecraft_server_data['Protocol'].isin(mc_versions)]
servers = servers.sample(frac=1, random_state=42)
for index, row in servers.iterrows():
    ip_address = row['IP']
    port = row['Port']
    version = row['Protocol']
    print('Trying ' + str(ip_address) + ':' + str(port) + ' with version ' + str(version))
    cmd = ['node', 'join_server.js', str(ip_address), str(port)]
    result = subprocess.Popen(cmd)
    result.wait()
    time.sleep(60)