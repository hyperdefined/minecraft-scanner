import shodan
import pandas as pd
import os
from dotenv import load_dotenv

def update_server_info(ip_address):
    load_dotenv()
    api_key = os.getenv('SHODAN_KEY')
    api = shodan.Shodan(api_key)

    data_exists = os.path.exists("database.csv")
    minecraft_server_data = pd.DataFrame(columns=['IP','Port','Protocol','Software','MOTD', 'Forge', 'Icon', 'Joins', 'Fails'])
    if data_exists:
        minecraft_server_data = pd.read_csv("database.csv")
    else:
        print('Unable to load database!')
        return

    try:
        results = api.host(ip_address)
        minecraft_data = None
        port = None
        # go through the data shodan has
        # check for Minecraft data
        for data in results['data']:
            if 'minecraft' not in data:
                continue
            minecraft_data = data['minecraft']
            port = data['port']

        # if there is no Minecraft data, exit
        if minecraft_data == None:
            print('IP address has no Minecraft data attached.')
            return

        description = "none"
        if 'description' in minecraft_data:
            description = minecraft_data['description']

        protocol = "UNKNOWN"
        server_software = "UNKNOWN"
        if 'version' in minecraft_data:
            if 'protocol' in minecraft_data['version']:
                protocol = minecraft_data['version']['protocol']
            if 'name' in minecraft_data['version']:
                server_software = minecraft_data['version']['name']

        # track if the server is using forge
        is_forge = 0
        if 'forgeData' in minecraft_data:
            is_forge = 1

        # see if the server has an icon set
        icon = "none"
        if 'favicon' in minecraft_data:
            icon = minecraft_data['favicon']

        ip_query = minecraft_server_data[minecraft_server_data['IP'] == ip_address]
        print('Updating data for IP ' + ip_address)
        for index, row in ip_query.iterrows():
            if protocol == "UNKNOWN":
                minecraft_server_data.loc[index, 'Protocol'] = str(protocol)
            else:
                minecraft_server_data.loc[index, 'Port'] = int(port)    
            minecraft_server_data.loc[index, 'Software'] = str(server_software)
            minecraft_server_data.loc[index, 'MOTD'] = str(description)
            minecraft_server_data.loc[index, 'Forge'] = int(is_forge)
            minecraft_server_data.loc[index, 'Icon'] = str(icon)
    except shodan.APIError as e:
        print("Error: %s" % e)

    minecraft_server_data.to_csv("database.csv", index=False)