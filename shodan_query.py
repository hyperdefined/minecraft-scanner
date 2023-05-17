import shodan
import pandas as pd
import os
import subprocess
import time
from dotenv import load_dotenv
import single_query
import sys
import random

def filter_servers(server_data):
    # only join servers from 1.8 to 1.19 since that's what Mineflayer supports
    # filter out forge servers since we can't join them
    mc_versions = [47, 107, 108, 109, 110, 210, 315, 316, 335, 338, 340, 393, 401, 404, 477, 480, 485, 490, 498, 573, 575, 578, 735, 736, 751, 753, 754, 755, 756, 757, 758, 759]
    filtered_rows = []
    for _, row in server_data.iterrows():
        protocol = row['Protocol']
        if protocol == 'UNKNOWN':
            continue
        protocol = int(protocol)
        if protocol in mc_versions and row['Forge'] == 0 and row['Joins'] < 5:
            filtered_rows.append(row)
    random.shuffle(filtered_rows)
    filtered_data = pd.DataFrame(filtered_rows, columns=server_data.columns)
    
    return filtered_data

def join_server(host, port, version):
    # build the command to run the node script to join
    print('Trying ' + str(host) + ':' + str(port) + ' with version ' + str(version))
    cmd = ['node', 'join_server.js', str(host), str(port)]
    result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = result.communicate()

    # Decode the output from bytes to string
    output = stdout.decode('utf-8')
    error = stderr.decode('utf-8')

    ip_query = minecraft_server_data[minecraft_server_data['IP'] == host]

    # Print or return the output
    if output:
        # kicked from server
        # logged into server
        if 'Kicked from' in output:
            current_fails = ip_query['Fails'].iloc[0]
            new_fails = current_fails + 1
            minecraft_server_data.loc[ip_query.index, 'Fails'] = int(new_fails)
            minecraft_server_data.to_csv('database.csv', index=False)
        if 'Logged into server' in output:
            # Action to perform when 'Logged into server' is present in the output
            current_joins = ip_query['Joins'].iloc[0]
            new_joins = current_joins + 1
            minecraft_server_data.loc[ip_query.index, 'Joins'] = int(new_joins)
            minecraft_server_data.to_csv('database.csv', index=False)
        print(output)
    if error:
        # error connecting
        print('Error:', error)
        current_fails = ip_query['Fails'].iloc[0]
        new_fails = current_fails + 1
        minecraft_server_data.loc[ip_query.index, 'Fails'] = int(new_fails)
        minecraft_server_data.to_csv('database.csv', index=False)

load_dotenv()

api_key = os.getenv('SHODAN_KEY')
api = shodan.Shodan(api_key)

data_exists = os.path.exists("database.csv")
minecraft_server_data = pd.DataFrame(columns=['IP','Port','Protocol','Software','MOTD', 'Forge', 'Icon', 'Joins', 'Fails'])
if data_exists:
    print('Loading current database...')
    minecraft_server_data = pd.read_csv("database.csv")
    print('Loaded ' + str(len(minecraft_server_data.index)) + " servers.")

counter = 0

if len(sys.argv) == 2:
    if sys.argv[1] == 'update':
        minecraft_server_data = minecraft_server_data[::-1].reset_index(drop=True)
        filtered_servers = filter_servers(minecraft_server_data)
        for index, row in filtered_servers.iterrows():
            ip = row['IP']
            port = row['Port']
            version = row['Protocol']
            single_query.update_server_info(ip_address=str(ip))
            time.sleep(5)
            join_server(host=ip, port=port, version=version)

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

        description = "none"
        if 'description' in minecraft_info:
            description = minecraft_info['description']

        protocol = "UNKNOWN"
        server_software = "UNKNOWN"
        if 'version' in minecraft_info:
            if 'protocol' in minecraft_info['version']:
                protocol = minecraft_info['version']['protocol']
            if 'name' in minecraft_info['version']:
                server_software = minecraft_info['version']['name']

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

        # make sure protocol saves correctly
        try:
            protocol = int(protocol)
        except ValueError:
            protocol = str(protocol)

        # build the data to add
        new_server_data = {'IP':str(ip_address), 'Port':int(port), 'Protocol':protocol, 'Software':str(server_software), 'MOTD': str(description), 'Forge': int(is_forge), 'Icon': str(icon)}
        
        # add the new data
        new_row_df = pd.DataFrame([new_server_data])
        minecraft_server_data = pd.concat([minecraft_server_data, new_row_df], ignore_index=True)
except shodan.APIError as e:
    print("Error: %s" % e)

minecraft_server_data.to_csv("database.csv", index=False)

if counter > 0:
    print('Added ' + str(counter) + ' new servers.')
    print('New total: ' + str(len(minecraft_server_data.index)) + ' servers.')

filtered_servers = filter_servers(minecraft_server_data)
for index, row in filtered_servers.iterrows():
    join_server(host=row['IP'], port=row['Port'], version=row['Protocol'])
    # sleep for 20 seconds so we don't ratelimit ourself
    time.sleep(20)