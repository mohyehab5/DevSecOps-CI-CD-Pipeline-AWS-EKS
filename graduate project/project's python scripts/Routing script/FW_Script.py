import paramiko

def change_firewall_hostname(ip, username, password, new_hostname):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        
        # Automatically add the firewall's SSH key
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the firewall
        ssh.connect(ip, username=username, password=password)

        # Create a command to change the hostname
        command = f'config system global\nset hostname {new_hostname}\nend\n'

        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(command)

        # Read output and errors
        output = stdout.read().decode()
        errors = stderr.read().decode()

        if errors:
            print("Error:", errors)
        else:
            print("Output:", output)
            print(f"Hostname changed to {new_hostname} successfully.")

    except Exception as e:
        print("An error occurred:", str(e))
    finally:
        # Close the SSH connection
        ssh.close()

# Example usage
firewall_ip = '192.168.1.12'         # Replace with your firewall's IP address
username = 'admin'                   # Replace with your username
password = 'mhmd'           # Replace with your password
new_hostname = 'Mansour'         # Replace with the desired hostname

change_firewall_hostname(firewall_ip, username, password, new_hostname)