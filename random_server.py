import pandas as pd
import random
import pyperclip

minecraft_server_data = pd.read_csv("database.csv")

# this contains all MC versions from 1.8 to 1.19.4
# edit this to filter out different ones
#mc_versions = [47, 107, 108, 109, 110, 210, 315, 316, 335, 338, 340, 393, 401, 404, 477, 480, 485, 490, 498, 573, 575, 578, 735, 736, 751, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762]

# 1.19 to 1.19.4
mc_versions = [759, 760, 761, 762]

filtered_rows = []
for _, row in minecraft_server_data.iterrows():
    protocol = row['Protocol']
    if protocol == 'UNKNOWN':
        continue
    protocol = int(protocol)
    if protocol in mc_versions and row['Forge'] == 0 and row['Joins'] == 0 and row['Fails'] == 0:
        filtered_rows.append(row)
random.shuffle(filtered_rows)
filtered_data = pd.DataFrame(filtered_rows, columns=minecraft_server_data.columns)

for index, row in filtered_data.iterrows():
    ip = str(row['IP']) + ':' + str(row['Port'])
    print(ip)
    pyperclip.copy(ip)
    can_join_input = input("Can you join?\n")
    if can_join_input.lower() == 'y':
        can_join = True
    elif can_join_input.lower() == 'n':
        can_join = False
    else:
        print("Invalid input. Assuming 'n' (no).")
    can_join = False

    if can_join:
        current_joins = row['Joins']
        minecraft_server_data.loc[index, 'Joins'] = current_joins + 1
    else:
        current_fails = row['Fails']
        minecraft_server_data.loc[index, 'Fails'] = current_fails + 1
    minecraft_server_data.to_csv("database.csv", index=False)