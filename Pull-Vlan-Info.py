import csv
import pandas as pd
from netmiko import ConnectHandler
from getpass import getpass

# Function to SSH and execute the command on the switch
def get_vlan_info(hostname, username, password):
    try:
        # Define the device information
        device = {
            'device_type': 'cisco_ios',  # Assuming the device is Cisco IOS
            'host': hostname,
            'username': username,
            'password': password,
        }

        # Establish an SSH connection using Netmiko
        connection = ConnectHandler(**device)
        
        # Send the command to the switch
        output = connection.send_command('show vlan brief')
        
        # Close the connection
        connection.disconnect()
        
        return output

    except Exception as e:
        print(f"Failed to connect to {hostname}: {e}")
        return None

# Function to filter and parse VLAN information from the output
def filter_vlan_info(vlan_output):
    vlan_lines = vlan_output.splitlines()

    vlan_data = []
    for line in vlan_lines:
        if "default" not in line:  # Ignore lines with 'default'
            columns = line.split()
            if len(columns) > 1:  # Check if the line contains VLAN data
                vlan_id = columns[0]
                vlan_full_name = columns[1]
                
                # Split VLAN name and subnet by the last occurrence of either '-' or '_'
                if '-' in vlan_full_name:
                    vlan_name = vlan_full_name.rsplit('-', 1)[0]  # Name before the last dash
                    subnet = vlan_full_name.rsplit('-', 1)[1]     # Subnet after the last dash
                elif '_' in vlan_full_name:
                    vlan_name = vlan_full_name.rsplit('_', 1)[0]  # Name before the last underscore
                    subnet = vlan_full_name.rsplit('_', 1)[1]     # Subnet after the last underscore
                else:
                    vlan_name = vlan_full_name
                    subnet = ""  # No subnet info found
                
                vlan_data.append((vlan_id, vlan_name, subnet))
    
    return vlan_data

# Main function
def main():
    # Prompt user for SSH credentials
    username = input("Enter your SSH username: ")
    password = getpass("Enter your SSH password: ")
    
    # Read hostnames from input.csv
    hostnames = pd.read_csv('input.csv')['hostname'].tolist()
    
    # Create an empty DataFrame to store results
    vlan_results = pd.DataFrame(columns=['Hostname', 'Vlan ID', 'Name', 'Subnet'])
    
    # Loop over each hostname and gather VLAN information
    for hostname in hostnames:
        print(f"\nConnecting to {hostname}...")
        
        # Get VLAN information from the switch
        vlan_output = get_vlan_info(hostname, username, password)
        
        if vlan_output:
            # Filter the VLAN information
            vlan_info = filter_vlan_info(vlan_output)
            
            # Append the filtered VLAN data to the DataFrame
            for vlan_id, vlan_name, subnet in vlan_info:
                vlan_results = vlan_results.append({
                    'Hostname': hostname,
                    'Vlan ID': vlan_id,
                    'Name': vlan_name,
                    'Subnet': subnet
                }, ignore_index=True)
        else:
            print(f"Failed to retrieve VLAN information from {hostname}.")
    
    # Write the DataFrame to an Excel file
    output_file = 'vlan_info.xlsx'
    vlan_results.to_excel(output_file, index=False)
    print(f"\nVLAN information has been saved to {output_file}.")

if __name__ == "__main__":
    main()
