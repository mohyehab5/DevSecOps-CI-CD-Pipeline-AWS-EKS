import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, Toplevel
import re
import logging
from netmiko import ConnectHandler
# import uuid

from netmiko.ssh_auth import SSHClient

# Configure logging
logging.basicConfig(filename='netmiko.log', level=logging.DEBUG)
logging.getLogger("netmiko").setLevel(logging.DEBUG)

class RouterConfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("Router Configuration")
        self.root.geometry("1100x600")
        self.router_num = 0
        self.router_inputs = {}
        self.tabs = {}  # Store references to tabs per router
        # GUI Elements
        
        self.frame = ctk.CTkScrollableFrame(master=root)
        self.frame.pack(pady=20, padx=60, fill="both", expand=True)
        

        self.entry_label = ctk.CTkLabel(master=self.frame, text="Enter number of Routers:")
        self.entry_label.pack(pady=5)
        self.router_num_entry = ctk.CTkEntry(master=self.frame)
        self.router_num_entry.pack(pady=5)

        self.start_button = ctk.CTkButton(master=self.frame, text="Start Configuration", command=self.show_router_inputs)
        self.start_button.pack(pady=10)

        self.error_label = tk.Label(self.frame, text="", bg="#212121", fg="red")
        self.error_label.pack()

            
    def clear_textbox(self, output_text):
       output_text.delete("1.0", tk.END)
    
    def log_output(self, message, output_text):
        """Logs and displays messages in a text box."""
        output_text.insert(ctk.END, message + "\n")
        output_text.see(ctk.END)

    def show_router_inputs(self):
        """Reads the number of routers and opens a new window with a tab for each router."""
        try:
            self.router_num = int(self.router_num_entry.get())
            if self.router_num <= 0:
                self.error_label.config(text="Input Error: Please enter a valid number of routers!")
                return
            self.router_inputs = {i: {} for i in range(1, self.router_num + 1)}
            self.error_label.config(text="")
            self.open_router_window()
        except ValueError:
            self.error_label.config(text="Input Error: Please enter a valid number.")

    def open_router_window(self):
        """Clears the current window and creates tabs for each router."""
        for widget in self.frame.winfo_children():
            widget.destroy()

        notebook = ctk.CTkTabview(self.frame)
        notebook.pack(expand=True, fill="both")

        for i in range(1, self.router_num + 1):
            tab_name = f"Router {i}"
            notebook.add(tab_name)  # Create a new tab
            # Get the tab frame and add custom widgets
            tab = notebook.tab(tab_name)
            self.create_router_tab(tab, i)

    def create_router_tab(self, tab, router_id):
        """Creates UI for configuring each router."""
        ctk.CTkLabel(tab, text=f"Router {router_id} IP:").pack(pady=5)
        ip_entry = ctk.CTkEntry(tab)
        ip_entry.pack(pady=5)

        ctk.CTkLabel(tab, text="SSH Username:").pack(pady=5)
        user_entry = ctk.CTkEntry(tab)
        user_entry.pack(pady=5)

        ctk.CTkLabel(tab, text="SSH Password:").pack(pady=5)
        pass_entry = ctk.CTkEntry(tab, show="*")
        pass_entry.pack(pady=5)

        ctk.CTkLabel(tab, text="Routing Protocol:").pack(pady=5)
        protocol_var = ctk.StringVar(value="Select Protocol")
        protocol_combobox = ctk.CTkOptionMenu(tab, variable=protocol_var, values=["EIGRP", "OSPF", "Default Static Routing", "Basic Router Config","Router_on_a_stick","configure_dhcp_services","configure_nat_services"])
        protocol_combobox.pack(pady=5)
        self.router_inputs[router_id]['protocol'] = protocol_combobox  # Store the ComboBox
        output_text = scrolledtext.ScrolledText(tab, width=100, height=10, bg="black", fg="white")
        output_text.pack(pady=10)

        error_label = tk.Label(tab, text="", bg="#212121", fg="red")
        error_label.pack()

        def save_router():
            ip = ip_entry.get().strip()
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            protocol = protocol_var.get().strip().lower()

            if not ip or not username or not password or protocol == "select protocol":
                error_label.configure(text="Input Error: Please fill in all fields.")
                return

            if not username.isalpha():
                error_label.configure(text="Input Error: SSH Username must contain only letters.")
                return

            if not self.validate_ip(ip):
                error_label.configure(text="Input Error: Invalid IP address format!")
                return

            if protocol not in ["ospf", "eigrp", "default static routing", "basic router config","router_on_a_stick","configure_dhcp_services","configure_nat_services"]:
                error_label.configure(text="Input Error: Invalid routing protocol!")
                return

            self.router_inputs[router_id] = {
                "ip": ip,
                "username": username,
                "password": password,
                "protocol": protocol
            }

            try:
                self.log_output(f"Connecting to {ip}...", output_text)
                output_text.insert(tk.END, f"Trying to connect to router {ip}...\n")
                output_text.see(tk.END)  # Auto-scroll to the latest message
                output_text.update()     # Force UI to update immediately

                router_conn = {
                    'device_type': 'cisco_ios',
                    'ip': ip,
                    'username': username,
                    'password': password
                }
                self.log_output(f"Trying to connect to router {ip}...", output_text)
                ssh = ConnectHandler(**router_conn)
                self.log_output(f"Connected to {ip}. Configuring {protocol.upper()}...", output_text)
                # Insert the success message into the output_text
                output_text.insert(tk.END, f"Successfully connected to router {ip}.\n")
                output_text.see(tk.END)  # Auto-scroll to the latest message
                output_text.update()     # Force UI to update immediately

                self.log_output(f"success connect to router ip: {ip}. Proceeding to configuration...", output_text)
                if protocol == "eigrp":
                    self.configure_eigrp(ssh, ip, output_text, tab)
                elif protocol == "ospf":
                    self.configure_ospf(ssh, ip, output_text, tab)
                elif protocol == "default static routing":
                    self.configure_DSR(ssh, ip, output_text, tab)
                elif protocol == "basic router config":
                    self.configure_basic_router(ssh, ip, output_text, tab)
                elif protocol == "router_on_a_stick":
                    self.configure_router_on_a_stick(ssh, ip, output_text, tab)
                elif protocol == "configure_dhcp_services":
                    self.configure_dhcp_services(ssh, ip, output_text, tab)   
                elif protocol == "configure_nat_services":
                    self.configure_nat_services(ssh, ip, output_text, tab)


            except Exception as e:
                self.log_output(f"Connection Error: {str(e)}", output_text)
                logging.error(f"Connection failed for router {router_id}: {str(e)}")

        save_button = ctk.CTkButton(tab, text="Save & Configure", command=save_router)
        save_button.pack(pady=5)

        back_button = ctk.CTkButton(tab, text="Back to Main", command=self.back_to_main)
        back_button.pack(pady=5)

    def back_to_main(self):
        """Clears content and reinitializes the main window."""
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.update_idletasks()
        self.setup_main_window()
          # Update size dynamically    

    def setup_main_window(self):
        """Rebuilds the main window without reinitializing the entire class."""
        self.router_num = 0
        self.router_inputs = {}

        self.entry_label = ctk.CTkLabel(master=self.frame, text="Enter number of Routers:")
        self.entry_label.pack(pady=5)

        self.router_num_entry = ctk.CTkEntry(master=self.frame)
        self.router_num_entry.pack(pady=5)

        self.start_button = ctk.CTkButton(master=self.frame, text="Start Configuration", command=self.show_router_inputs)
        self.start_button.pack(pady=10)

        self.error_label = tk.Label(self.frame, text="", bg="#212121", fg="red")
        self.error_label.pack()
         # Update size dynamically
        self.frame.update_idletasks()  # Process widget layout updates
        
    def validate_ip(self, ip):
        """Validates an IPv4 address, ensuring each octet is between 0 and 255."""
        # Check format with regex
        pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        if not pattern.match(ip):
            return False
        
        # Split IP into octets and validate range
        octets = ip.split('.')
        for octet in octets:
            try:
                value = int(octet)
                if value < 0 or value > 255:
                    return False
            except ValueError:
                return False
        
        return True

    def validate_subnet_mask(self, mask):
        """Validates a subnet mask, ensuring it follows the contiguous 1s pattern."""
        # First, check if it's a valid IPv4 format
        if not self.validate_ip(mask):
            return False
        
        # Valid subnet mask octet values in descending order
        valid_octets = [255, 254, 252, 248, 240, 224, 192, 128, 0]
        
        # Split mask into octets
        octets = [int(octet) for octet in mask.split('.')]
        
        # Check if each octet is a valid subnet mask value
        for octet in octets:
            if octet not in valid_octets:
                return False
        
        # Ensure octets are in non-increasing order (e.g., 255.255.0.0 is valid, 255.0.255.0 is not)
        seen_zero = False
        for octet in octets:
            if octet == 0:
                seen_zero = True
            elif seen_zero and octet != 0:
                return False
        
        return True

    def is_valid_interface(self, interface):
        """Validates interface format (e.g., g0/0, s1/1, loopback0)."""
        pattern = r'^(f|g|s|e)\d+/\d+$|^loopback\d+$'
        return bool(re.match(pattern, interface))
    
    def validate_hostname(self, hostname):
        """Validates hostname format (alphanumeric, hyphens, max 63 characters)."""
        pattern = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$")
        return bool(pattern.match(hostname) and len(hostname) <= 63)
    
    def validate_wildcard(self, wildcard):
        """Validates a wildcard mask, ensuring it follows the correct format and logic."""
        try:
            # Check if it's a valid IPv4 format
            if not re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", wildcard):
                return False
            
            # Split wildcard into octets
            octets = [int(octet) for octet in wildcard.split('.')]
            
            # Validate each octet (0-255)
            for octet in octets:
                if octet < 0 or octet > 255:
                    return False
            
            # Ensure wildcard represents a valid subnet (complement of subnet mask)
            # Convert wildcard to binary and check for contiguous 0s (complement should have contiguous 1s)
            binary = ''.join(format(octet, '08b') for octet in octets)
            ones_count = 0
            zeros_count = 0
            for bit in binary:
                if bit == '1':
                    ones_count += 1
                    zeros_count = 0
                elif bit == '0':
                    zeros_count += 1
                    if zeros_count > 0 and ones_count > 0 and bit == '0':
                        return False  # Non-contiguous 0s indicate invalid wildcard
                if ones_count + zeros_count == 32:
                    break
            
            return True
        except ValueError:
            return False

    # def create_show_commands_section(self, config_frame, device, output_text, show_commands, row):
    #     show_frame = ctk.CTkFrame(config_frame)
    #     show_frame.grid(row=row, column=0, columnspan=12, pady=10, sticky="ew")
    #     command_var = ctk.StringVar(value="")
    #     command_label = ctk.CTkLabel(show_frame, text="Select Show Command:")
    #     command_label.grid(row=0, column=0, padx=5)
    #     command_menu = ctk.CTkOptionMenu(show_frame, variable=command_var, values=show_commands)
    #     command_menu.grid(row=0, column=1, padx=5)
        
    #     def send_command():
    #         selected_command = command_var.get()
    #         if selected_command:
    #             output = ssh.send_config_set(['do ' + selected_command], exit_config_mode=False)
    #             self.log_output(f"Output for show command on {device}:\n{output}", output_text)
        
    #     send_command_button = ctk.CTkButton(show_frame, text="Send Command", command=send_command)
    #     send_command_button.grid(row=0, column=2, padx=5, pady=10)
    #     separator = ctk.CTkFrame(show_frame, height=2)
    #     separator.grid(row=1, column=0, columnspan=10, sticky="ew", pady=5)    
    
    def configure_eigrp(self, ssh, device, output_text, tab):
        """Continues configuration in the same tab by clearing previous content."""

        # Clear the existing tab's contents
        for widget in tab.winfo_children():
            widget.destroy()

        config_frame = ctk.CTkFrame(tab)
        config_frame.pack(pady=10, fill="both", expand=True)
        # Output text box
        output_text = scrolledtext.ScrolledText(config_frame, width=100, height=15, bg="black", fg="white")
        output_text.grid(row=10, columnspan=5, pady=10 ,padx=10)

        clear_button = ctk.CTkButton(config_frame, text="Clear", command=lambda: self.clear_textbox(output_text))
        clear_button.grid(row=11, column=1, padx=10)

        back_button = ctk.CTkButton(config_frame, text="Back to Main", command=self.back_to_main)
        back_button.grid(row=12, column=1, pady=5)
        # Prompt for EIGRP AS Number
        ctk.CTkLabel(config_frame, text="EIGRP AS Number:").grid(row=0, column=0)
        AS_entry = ctk.CTkEntry(config_frame)
        AS_entry.grid(row=0, column=1)

        Auto_sum_var = ctk.StringVar(value="no")
        ctk.CTkLabel(config_frame, text="Enable Auto-summarization ?:").grid(row=1, column=0)
        ctk.CTkOptionMenu(config_frame, variable=Auto_sum_var, values=["yes", "no"]).grid(row=1, column=1)

        ctk.CTkLabel(config_frame, text="Variance:").grid(row=2, column=0)
        variance_var = ctk.StringVar(value="default")
        variance_menu = ctk.CTkComboBox(config_frame, variable=variance_var, values=["default"])
        variance_menu.grid(row=2, column=1)

        # Frame for other entries
        network_frame = ctk.CTkFrame(config_frame)
        network_frame.grid(row=4, columnspan=5, pady=10, sticky="ew")
        network_frame.grid_remove()  # Initially hide the frame

        # Initialize list to hold network configurations
        network_entries = []

        # Function to add network entries
        def add_network_entry():
            network_frame.grid()  # Show the frame when adding an entry
            row = len(network_entries) * 5  # Current row index for new entry, ensuring proper spacing

            # Network entry
            ctk.CTkLabel(network_frame, text=f"Network {row // 5 + 1}:").grid(row=row, column=0)
            network_entry = ctk.CTkEntry(network_frame)
            network_entry.grid(row=row, column=1)

            # Wildcard mask entry
            ctk.CTkLabel(network_frame, text="Wildcard Mask:").grid(row=row, column=2)
            wildcard_entry = ctk.CTkEntry(network_frame)
            wildcard_entry.grid(row=row, column=3)

            # Interface entry
            ctk.CTkLabel(network_frame, text="Interface:").grid(row=row, column=4)
            interface_entry = ctk.CTkEntry(network_frame)
            interface_entry.grid(row=row, column=5)

            # Authentication
            ctk.CTkLabel(network_frame, text="Authentication(By MD5) ?:").grid(row=row + 1, column=0)
            auth_var = ctk.StringVar(value="no")
            auth_var_menu = ctk.CTkOptionMenu(network_frame, variable=auth_var, values=["no", "yes"], command=lambda _: update_auth_entry(row))
            auth_var_menu.grid(row=row + 1, column=1)

            # chain name entry
            chain_name_label = ctk.CTkLabel(network_frame, text="Chain Name :")
            chain_name_entry = ctk.CTkEntry(network_frame)

            # key number entry
            key_no_label = ctk.CTkLabel(network_frame, text="Key Number:")
            key_no_entry = ctk.CTkEntry(network_frame)

            # Authentication key entry and label (initially hidden)
            auth_key_label = ctk.CTkLabel(network_frame, text="Authentication Key:")
            auth_key_entry = ctk.CTkEntry(network_frame, show='*')

            chain_name_label.grid(row=row + 1, column=2)
            chain_name_entry.grid(row=row + 1, column=3)
            chain_name_label.grid_remove()  # Hide the label initially
            chain_name_entry.grid_remove()  # Hide the entry initially

            key_no_label.grid(row=row + 1, column=4)
            key_no_entry.grid(row=row + 1, column=5)
            key_no_label.grid_remove()  # Hide the label initially
            key_no_entry.grid_remove()  # Hide the entry initially

            # Initially hide the label and entry
            auth_key_label.grid(row=row + 1, column=6)
            auth_key_entry.grid(row=row + 1, column=7)
            auth_key_label.grid_remove()  # Hide the label initially
            auth_key_entry.grid_remove()  # Hide the entry initially

            # Function to update the visibility of the authentication key entry and label
            def update_auth_entry(row):
                if auth_var.get() == "yes":
                    chain_name_label.grid(row=row + 1, column=2)  # Show the label
                    chain_name_entry.grid(row=row + 1, column=3)  # Show the entry

                    key_no_label.grid(row=row + 1, column=4)
                    key_no_entry.grid(row=row + 1, column=5)

                    auth_key_label.grid(row=row + 1, column=6)
                    auth_key_entry.grid(row=row + 1, column=7)
                else:
                    chain_name_label.grid_remove()
                    chain_name_entry.grid_remove()

                    key_no_label.grid_remove()
                    key_no_entry.grid_remove()

                    auth_key_label.grid_remove()
                    auth_key_entry.grid_remove()

            # interface B.W
            ctk.CTkLabel(network_frame, text="Interface B.W (%):").grid(row=row + 2, column=0)
            e_BW_var = ctk.StringVar(value="default")
            e_BW_menu = ctk.CTkOptionMenu(network_frame, variable=e_BW_var, values=["default", "10", "20", "100", "200"])
            e_BW_menu.grid(row=row + 2, column=1)

            # Hello Interval entry
            ctk.CTkLabel(network_frame, text="Hello Interval (Seconds):").grid(row=row + 3, column=0)
            hello_var = ctk.StringVar(value="default")
            hello_interval_menu = ctk.CTkOptionMenu(network_frame, variable=hello_var, values=["default", "1", "5", "10", "15", "20", "25"])
            hello_interval_menu.grid(row=row + 3, column=1)

            # Hold Time entry
            ctk.CTkLabel(network_frame, text="Hold Time (Seconds):").grid(row=row + 3, column=2)
            hold_var = ctk.StringVar(value="default")
            hold_time_menu = ctk.CTkOptionMenu(network_frame, variable=hold_var, values=["default", "4", "8", "12", "16", "20", "40"])
            hold_time_menu.grid(row=row + 3, column=3)

            # Add a horizontal line (separator)
            separator = ctk.CTkFrame(network_frame, height=2)
            separator.grid(row=row + 4, columnspan=10, sticky="ew", pady=5)

            # Store entries in the list
            network_entries.append((network_entry, wildcard_entry, auth_var, chain_name_entry, key_no_entry, auth_key_entry, interface_entry, hello_var, hold_var, e_BW_var))

        # Button to add new network entry row
        add_network_entry_btn = ctk.CTkButton(config_frame, text="Add Network Entry", command=add_network_entry)
        add_network_entry_btn.grid(row=5, columnspan=5, pady=10)

        def submit_configuration():
            # AS
            eigrp_AS = AS_entry.get()
            eigrp_command = f'router eigrp {eigrp_AS}'
            if not eigrp_AS:
                error_label.configure(text="Input Error: Please fill in the EIGRP Asynchronous System Number field.")
                return
            if not eigrp_AS.isdigit() or int(eigrp_AS) <= 0 or int(eigrp_AS) >= 65536:
                error_label.configure(text="Input Error: EIGRP Asynchronous System Number must be a number between ( 1 and 65535 ).")
                return
            self.log_output(f"Sending command: {eigrp_command}", output_text)
            # auto-summarization
            if Auto_sum_var.get() == 'yes':
                Auto_sum_command = f'auto-summary'
                self.log_output(f"Sending command: {Auto_sum_command}", output_text)
                ssh.send_config_set([eigrp_command, Auto_sum_command], exit_config_mode=False)
            else:
                Auto_sum_command = f'no auto-summary'
                self.log_output(f"Sending command: {Auto_sum_command}", output_text)
                ssh.send_config_set([eigrp_command, Auto_sum_command], exit_config_mode=False)
            # Variance
            variance_var = variance_menu.get()
            if variance_var != "default":
                if not variance_var.isdigit() or int(variance_var) <= 0:
                    error_label.configure(text="Input Error,Variance Number must be a positive integer or 'default'.")
                    return
            if variance_var == "default":
                variance_command = f'variance 1'
                ssh.send_config_set([eigrp_command, variance_command], exit_config_mode=False)
                self.log_output(f"returning for the default value of the variance that is 1", output_text)
            else:
                variance_command = f'variance {variance_var}'
                self.log_output(f"Sending command:{variance_command}", output_text)
                ssh.send_config_set([eigrp_command, variance_command], exit_config_mode=False)

            # if don't click on the 'add network' button
            if not add_network_entry_btn:
                return
            # Process each network entry
            for entry in network_entries:
                network_var = entry[0].get()
                wildcard_mask_var = entry[1].get()
                auth_var = entry[2].get()
                chain_name_var = entry[3].get()
                key_no_var = entry[4].get()
                auth_key_var = entry[5].get()
                interface_var = entry[6].get()
                hello_var = entry[7].get()
                hold_var = entry[8].get()
                Int_BW_var = entry[9].get()

                if not self.validate_ip(network_var):  # Check if the IP is valid
                    error_label.configure(text="Input Error: Please enter a valid network address.")  # Log an error if invalid
                    return  # Exit the method if there is an error
                elif not self.validate_wildcard(wildcard_mask_var):
                    error_label.configure(text="Input Error: Please enter a valid WildCard address.")  # Log an error if invalid
                    return

                if not self.is_valid_interface(interface_var):
                    error_label.configure(text="Input Error: interface must be like f0/0 , g0/1 , s1/1 or loopback0.")
                    return
                if auth_var == 'yes' and not (chain_name_var or key_no_var or auth_key_var):
                    error_label.configure(text="Input Error: please fill out all the Authentication Entries.")
                    return
                if auth_var == 'yes' and (not key_no_var.isdigit() or int(key_no_var) <= 0):
                    error_label.configure(text="Input Error: Key Number must be a positive integer.")
                    return

                if Int_BW_var != "default":
                    if not Int_BW_var.isdigit() or int(Int_BW_var) <= 0 or int(Int_BW_var) > 999999:
                        error_label.configure(text="Input Error,The interface BandWidth must be a positive integer <1-999999> or 'default'.")
                        return

                if hello_var != "default":
                    if not hello_var.isdigit() or int(hello_var) <= 0 or int(hello_var) > 65535:
                        error_label.configure(text="Input Error,Hello Interval must be a positive integer <1-65535> or 'default'.")
                        return
                if hold_var != "default":
                    if not hold_var.isdigit() or int(hold_var) <= 0 or int(hold_var) > 65535:
                        error_label.configure(text="Input Error,Hold Time must be a positive integer or 'default'.")
                        return

                # EIGRP network command
                network_command = f'network {network_var} {wildcard_mask_var}'
                self.log_output(f"Sending command: {network_command}", output_text)
                ssh.send_config_set([eigrp_command, network_command], exit_config_mode=False)
                interface_command = f'interface {interface_var}'
                if auth_var == 'yes':
                    # key chain preparing
                    k1_command = f'key chain {chain_name_var}'
                    k2_command = f'key {key_no_var}'
                    k3_command = f'key-string {auth_key_var}'
                    self.log_output(f"Sending command: {k1_command}", output_text)
                    self.log_output(f"Sending command: {k2_command}", output_text)
                    self.log_output(f"Sending command: {k3_command}", output_text)
                    ssh.send_config_set([k1_command, k2_command, k3_command], exit_config_mode=False)

                    # interface authentication
                    self.log_output(f"Sending command: {interface_command}", output_text)
                    ssh.send_config_set([interface_command], exit_config_mode=False)

                    interface_auth1_command = f'ip authentication key-chain eigrp {eigrp_AS} {chain_name_var}'
                    interface_auth2_command = f'ip authentication mode eigrp {eigrp_AS} md5'

                    self.log_output(f"Sending command: {interface_auth1_command}", output_text)
                    self.log_output(f"Sending command: {interface_auth2_command}", output_text)
                    ssh.send_config_set([interface_auth1_command, interface_auth2_command], exit_config_mode=False)

                if hello_var == "default":
                    e_hello_default_command = f'ip hello-interval eigrp {eigrp_AS} 5'
                    ssh.send_config_set([interface_command, e_hello_default_command], exit_config_mode=False)
                    self.log_output(f"returning for the default value of the hello interval that is 5 seconds", output_text)
                else:
                    # Handle Hello Interval
                    e_hello_command = f'ip hello-interval eigrp {eigrp_AS} {hello_var}'
                    self.log_output(f"Sending command:{interface_command}", output_text)
                    self.log_output(f"Sending command:{e_hello_command}", output_text)
                    ssh.send_config_set([interface_command, e_hello_command], exit_config_mode=False)

                if hold_var == "default":
                    hold_default_command = f'ip hold-time eigrp {eigrp_AS} 15'
                    ssh.send_config_set([interface_command, hold_default_command], exit_config_mode=False)
                    self.log_output(f"returning for the default value of the hold time that is 15 seconds", output_text)
                else:
                    # Handle Hold Time
                    hold_command = f'ip hold-time eigrp {eigrp_AS} {hold_var}'
                    self.log_output(f"Sending command:{interface_command}", output_text)
                    self.log_output(f"Sending command:{hold_command}", output_text)
                    ssh.send_config_set([interface_command, hold_command], exit_config_mode=False)
                # Handle interface BandWidth for the percent of the control plane with respect to the default BW of the interface
                if Int_BW_var == 'default':
                    self.log_output(f"returning for the default value of the Interface BandWidth that is 50%", output_text)
                    e_BW_default_command = f'ip bandwidth-percent eigrp {eigrp_AS} 50'
                    ssh.send_config_set([interface_command, e_BW_default_command], exit_config_mode=False)
                else:
                    e_BW_command = f'ip bandwidth-percent eigrp {eigrp_AS} {Int_BW_var}'
                    self.log_output(f"Sending command:{interface_command}", output_text)
                    self.log_output(f"Sending command:{e_BW_command}", output_text)
                    ssh.send_config_set([interface_command, e_BW_command], exit_config_mode=False)

            self.log_output(f'Success: Router "{device}" configured with EIGRP successfully.', output_text)

        # Submit button
        submit_button = ctk.CTkButton(config_frame, text="Submit Configuration", command=submit_configuration)
        submit_button.grid(row=6, columnspan=5, pady=10)
        error_label = tk.Label(config_frame, text="", bg="#212121", fg="red")
        error_label.grid(row=7, columnspan=5, pady=10)

        show_frame = ctk.CTkFrame(config_frame)
        show_frame.grid(row=8, columnspan=5, pady=10, sticky="ew")
        # Example EIGRP show commands
        eigrp_commands = [
            "show ip eigrp neighbor",
            "show ip eigrp topology",
            "show ip eigrp topology all-links",
            "show ip route",
            "show ip route eigrp",
            "show ip protocols",
            "show ip eigrp interfaces detail",
            "show key chain"
        ]

        # Combobox for selecting a command
        e_command_var = ctk.StringVar(value="")
        e_command_label = ctk.CTkLabel(show_frame, text="Select an EIGRP Show Command:")
        e_command_label.grid(row=0, column=0)
        e_command_menu = ctk.CTkOptionMenu(show_frame, variable=e_command_var, values=eigrp_commands)
        e_command_menu.grid(row=0, column=1)

        # Button to send the selected command and display output
        def e_send_command():
            e_selected_command = e_command_var.get()
            if e_selected_command:
                # Send the command to the router
                output = ssh.send_config_set(['do ' + e_selected_command], exit_config_mode=False)
                self.log_output(f"output for the show command of {device} :\n{output}", output_text)

        send_command_button = ctk.CTkButton(show_frame, text="Send Command", command=e_send_command)
        send_command_button.grid(row=0, column=2, pady=10)
        # Add a horizontal line (separator)
        separator = ctk.CTkFrame(show_frame, height=2)
        separator.grid(row=1, columnspan=10, sticky="ew", pady=5)
       
    def configure_ospf(self, ssh, device, output_text, tab):
        """Continues configuration in the same tab by clearing previous content."""
        # Clear the existing tab's contents
        for widget in tab.winfo_children():
            widget.destroy()

        config_frame = ctk.CTkFrame(tab)
        config_frame.pack(pady=10, fill="both", expand=True)
        # Output text box
        output_text = scrolledtext.ScrolledText(config_frame, width=100, height=15, bg="black", fg="white")
        output_text.grid(row=10, columnspan=5, pady=10)

        clear_button = ctk.CTkButton(config_frame, text="Clear", command=lambda: self.clear_textbox(output_text))
        clear_button.grid(row=11, column=1, pady=10)

        back_button = ctk.CTkButton(config_frame, text="Back to Main", command=self.back_to_main)
        back_button.grid(row=12, column=1, pady=5)
        # Prompt for OSPF Process ID
        ctk.CTkLabel(config_frame, text="OSPF Process ID:").grid(row=0, column=0)
        ospf_pid_entry = ctk.CTkEntry(config_frame)
        ospf_pid_entry.grid(row=0, column=1)

        All_Int_passive_var = ctk.StringVar(value="no")
        ctk.CTkLabel(config_frame, text="Making all ints passive ?:").grid(row=1, column=0)
        ctk.CTkOptionMenu(config_frame, variable=All_Int_passive_var, values=["yes", "no"]).grid(row=1, column=1)

        ctk.CTkLabel(config_frame, text="Cost BandWidth(In Mega):").grid(row=2, column=0)
        BW_var = ctk.StringVar(value="default")
        BW_menu = ctk.CTkComboBox(config_frame, variable=BW_var, values=["default"])
        BW_menu.grid(row=2, column=1)
            
        default_ospf_var = ctk.StringVar(value="no")
        ctk.CTkLabel(config_frame, text=f"Making router {device} as a default ospf route ?:").grid(row=3, column=0)
        ctk.CTkOptionMenu(config_frame, variable=default_ospf_var, values=["yes", "no"]).grid(row=3, column=1)

        # Frame for other entries
        network_frame = ctk.CTkFrame(config_frame)
        network_frame.grid(row=4, columnspan=5, pady=10, sticky="ew")
        network_frame.grid_remove()  # Initially hide the frame
        # Initialize list to hold network configurations
        network_entries = []

        # Function to add network entries
        def add_network_entry():
            network_frame.grid()  # Show the frame when adding an entry
            row = len(network_entries) * 5  # Current row index for new entry, ensuring proper spacing
            # Network entry
            ctk.CTkLabel(network_frame, text=f"Network {row // 5 + 1}:").grid(row=row, column=0)
            network_entry = ctk.CTkEntry(network_frame)
            network_entry.grid(row=row, column=1)

            # Wildcard mask entry
            ctk.CTkLabel(network_frame, text="Wildcard Mask:").grid(row=row, column=2)
            wildcard_entry = ctk.CTkEntry(network_frame)
            wildcard_entry.grid(row=row, column=3)

            # OSPF Area entry
            ctk.CTkLabel(network_frame, text="OSPF Area:").grid(row=row, column=4)
            ospf_area_entry = ctk.CTkEntry(network_frame)
            ospf_area_entry.grid(row=row, column=5)

            # Interface entry
            ctk.CTkLabel(network_frame, text="Interface:").grid(row=row, column=6)
            interface_entry = ctk.CTkEntry(network_frame)
            interface_entry.grid(row=row, column=7)

            # Passive interface entry
            passive_var = ctk.StringVar(value="no")
            ctk.CTkLabel(network_frame, text="Passive?").grid(row=row + 1, column=0)
            ctk.CTkOptionMenu(network_frame, variable=passive_var, values=["yes", "no"]).grid(row=row + 1, column=1)

            # Authentication Type
            ctk.CTkLabel(network_frame, text="Authentication Type:").grid(row=row + 1, column=2)
            auth_type_var = ctk.StringVar(value="none")
            auth_type_menu = ctk.CTkOptionMenu(network_frame, variable=auth_type_var, values=["none", "simple", "md5"], command=lambda _: update_auth_key_entry(row))
            auth_type_menu.grid(row=row + 1, column=3)

            # Authentication key entry and label (initially hidden)
            auth_key_label = ctk.CTkLabel(network_frame, text="Authentication Key:")
            auth_key_entry = ctk.CTkEntry(network_frame, show='*')

            # Initially hide the label and entry
            auth_key_label.grid(row=row + 1, column=4)
            auth_key_entry.grid(row=row + 1, column=5)
            auth_key_label.grid_remove()  # Hide the label initially
            auth_key_entry.grid_remove()  # Hide the entry initially

            # Function to update the visibility of the authentication key entry and label
            def update_auth_key_entry(row):
                if auth_type_var.get() in ["simple", "md5"]:
                    auth_key_label.grid(row=row+1, column=4)  # Show the label
                    auth_key_entry.grid(row=row+1, column=5)   # Show the entry
                else:
                    auth_key_label.grid_remove()  # Hide the label
                    auth_key_entry.grid_remove()   # Hide the entry

            # Hello Interval entry
            ctk.CTkLabel(network_frame, text="Hello Interval:").grid(row=row + 2, column=0)
            hello_var = ctk.StringVar(value="default")
            hello_interval_menu = ctk.CTkOptionMenu(network_frame, variable=hello_var, values=["default", "1", "2", "3", "4", "5", "10"])
            hello_interval_menu.grid(row=row + 2, column=1)

            # Dead Interval entry
            ctk.CTkLabel(network_frame, text="Dead Interval:").grid(row=row + 2, column=2)
            dead_var = ctk.StringVar(value="default")
            dead_interval_menu = ctk.CTkOptionMenu(network_frame, variable=dead_var, values=["default", "4", "8", "12", "16", "20", "40"])
            dead_interval_menu.grid(row=row + 2, column=3)

            ctk.CTkLabel(network_frame, text="Interface Cost:").grid(row=row + 3, column=0)
            Int_Cost_var = ctk.StringVar(value="default")
            Int_Cost_menu = ctk.CTkOptionMenu(network_frame, variable=Int_Cost_var, values=["default"])
            Int_Cost_menu.grid(row=row + 3, column=1)

            # Add a horizontal line (separator)
            separator = ctk.CTkFrame(network_frame, height=2)
            separator.grid(row=row + 4, columnspan=10, sticky="ew", pady=5)

            # Store entries in the list
            network_entries.append((network_entry, wildcard_entry, ospf_area_entry, auth_key_entry, auth_type_var, interface_entry, passive_var, hello_var, dead_var, Int_Cost_var))

        # Button to add new network entry row
        add_network_entry_btn = ctk.CTkButton(config_frame, text="Add Network Entry", command=add_network_entry)
        add_network_entry_btn.grid(row=5, columnspan=5, pady=10)
        
        def submit_configuration():
            ospf_pid = ospf_pid_entry.get()
            ospf_command = f'router ospf {ospf_pid}'
            if not ospf_pid :
                error_label.configure(text="Input Error: Please fill in the process id field.")
                return
            if not ospf_pid.isdigit() or int(ospf_pid) <= 0 or int(ospf_pid) >= 65536 :
                error_label.configure(text="Input Error: OSPF Process ID must be a number between ( 1 and 65535 ).")
                return
            
            BW_var=BW_menu.get()
            if BW_var != "default":
                if not BW_var.isdigit() or int(BW_var) <= 0:
                    error_label.configure(text="Input Error,B.W Cost must be a positive integer or 'default'.")
                    return
            self.log_output(f"Sending command: {ospf_command}",output_text)
            if BW_var == "default":
                BW_command=f'auto-cost reference-bandwidth 100'
                ssh.send_config_set([ospf_command,BW_command], exit_config_mode=False)
                self.log_output(f"returning for the default value of the Cost BandWidth",output_text)
                self.log_output(f"Alert : Pleast ensure that reference B.W must be consistent across all routers",output_text) 
            else:    
                # Handle cost B.W
                BW_command=f'auto-cost reference-bandwidth {BW_var}'
                self.log_output(f"Sending command:{BW_command}",output_text)
                self.log_output(f"Alert : Pleast ensure that reference B.W must be consistent across all routers",output_text) 
                ssh.send_config_set([ospf_command,BW_command], exit_config_mode=False) 
                 # Handle passive interface
            
            if All_Int_passive_var.get() == 'yes':
                All_Int_passive_var_command = f'passive-interface default'
            else :
                All_Int_passive_var_command = f'no passive-interface default'
            self.log_output(f"Sending command: {All_Int_passive_var_command}",output_text)
            ssh.send_config_set([ospf_command,All_Int_passive_var_command], exit_config_mode=False)    
                
            
            if default_ospf_var.get() == 'yes':
                default_ospf_var_command = f'default-information originate always'
                self.log_output(f"Sending command: {default_ospf_var_command}",output_text)
                self.log_output(f"Alert : you shuld make a default static routing or BGP to this router (router {device})  ",output_text)
                ssh.send_config_set([ospf_command,default_ospf_var_command], exit_config_mode=False)    

            # if don't click on the 'add network' button 
            if not add_network_entry_btn:
                return
            # Process each network entry
            for entry in network_entries:
                network = entry[0].get()
                wildcard_mask = entry[1].get()
                ospf_area = entry[2].get()
                auth_key = entry[3].get()
                auth_type = entry[4].get()
                interface = entry[5].get()
                passive = entry[6].get()
                hello_var = entry[7].get()
                dead_var = entry[8].get()
                Int_Cost_var=entry[9].get()
    
                if not self.validate_ip(network):  # Check if the IP is valid
                    error_label.configure(text="Input Error: Please enter a valid network address.")  # Log an error if invalid
                    return  # Exit the method if there is an error
                elif not self.validate_wildcard(wildcard_mask) :
                    error_label.configure(text="Input Error: Please enter a valid WildCard address.")  # Log an error if invalid
                    return
                elif not ospf_area.isdigit() or int(ospf_area) < 0:
                    error_label.configure(text="Input Error: area number must be a positive integer")
                    return  # Log an error if invalid
                if not self.is_valid_interface(interface):
                    error_label.configure(text="Input Error: interface must be like f0/0 , g0/1 s1/1 or loopback0.")
                    return
                if auth_type == 'md5' and not auth_key or auth_type=='simple' and not auth_key:
                    error_label.configure(text="Input Error: Authentication key cannot be empty for MD5 or simple.")
                    return
                if hello_var != "default":
                    if not hello_var.isdigit() or int(hello_var) <= 0:
                        error_label.configure(text="Input Error,Hello Interval must be a positive integer or 'default'.")
                        return
                if dead_var !="default" :        
                    if not dead_var.isdigit() or int(dead_var) <= 0:
                        error_label.configure(text="Input Error,Dead Interval must be a positive integer or 'default'.")
                        return
                if hello_var != "default" and dead_var!="default" and int(dead_var) <= int(hello_var):
                        error_label.configure(text="Input Error,Dead Interval must be greater than Hello Interval.")
                        return
                if Int_Cost_var != "default":
                    if not Int_Cost_var.isdigit() or int(Int_Cost_var) <= 0:
                        error_label.configure(text="Input Error,The interface Cost must be a positive integer or 'default'.")
                        return
                    # Validate the network address
                    
                    # OSPF network command
                network_command = f'network {network} {wildcard_mask} area {ospf_area}'
                self.log_output(f"Sending command: {network_command}",output_text)
                ssh.send_config_set([ospf_command,network_command], exit_config_mode=False)
                            
                if passive == 'yes':
                    passive_command = f'passive-interface {interface}'
                else :
                    passive_command = f'no passive-interface {interface}'
                self.log_output(f"Sending command: {passive_command}",output_text)
                ssh.send_config_set([ospf_area,passive_command], exit_config_mode=False)
                    # Handle interface-specific authentication
                interface_command = f'interface {interface}'
                if auth_type != 'none':
                    self.log_output(f"Sending command: {interface_command}", output_text)
                    ssh.send_config_set([interface_command], exit_config_mode=False)

                        # Log and send the authentication command for the interface
                if auth_type == 'md5':
                    interface_auth_command = f'ip ospf authentication message-digest'
                    self.log_output(f"Sending command: {interface_auth_command}",output_text)
                    ssh.send_config_set([interface_auth_command], exit_config_mode=False)
                    interface_auth_key_command = f'ip ospf message-digest-key 1 md5 {auth_key}'
                    self.log_output(f"Sending command: {interface_auth_key_command}",output_text)
                    ssh.send_config_set([interface_auth_key_command], exit_config_mode=False)
                elif auth_type == 'simple':
                    interface_auth_command_1 = f'ip ospf authentication'
                    self.log_output(f"Sending command: {interface_auth_command_1}",output_text)
                    ssh.send_config_set([interface_auth_command_1], exit_config_mode=False)
                    interface_auth_command_2 = f'ip ospf authentication-key {auth_key}'
                    self.log_output(f"Sending command: {interface_auth_command_2}",output_text)
                    ssh.send_config_set([interface_auth_command_2], exit_config_mode=False)

                if hello_var == "default":
                    hello_default_command=f'ip ospf hello-interval 10'
                    ssh.send_config_set([interface_command,hello_default_command], exit_config_mode=False)
                    self.log_output(f"returning for the default value of the hello interval",output_text) 
                else:    
                        # Handle Hello Interval
                    hello_command=f'ip ospf hello-interval {hello_var}'
                    self.log_output(f"Sending command:{interface_command}",output_text)
                    self.log_output(f"Sending command:{hello_command}",output_text)
                    ssh.send_config_set([interface_command,hello_command], exit_config_mode=False)    

                if dead_var == "default":
                    dead_default_command=f'ip ospf dead-interval 40'
                    ssh.send_config_set([interface_command,dead_default_command], exit_config_mode=False) 
                    self.log_output(f"returning for the default value of the dead interval",output_text)
                else :
                        # Handle Dead Interval
                    dead_command=f'ip ospf dead-interval {dead_var}'
                    self.log_output(f"Sending command:{interface_command}",output_text)
                    self.log_output(f"Sending command:{dead_command}",output_text)
                    ssh.send_config_set([interface_command,dead_command], exit_config_mode=False)

                if Int_Cost_var == "default":
                        # check if the int is fasst or giga or serial first
                        # 10 if ethernet , 1 if giga or fast ethernet , 64 if serial
                    if interface[0].lower()=='e':
                        int_cost_default_value=10
                    elif interface[0].lower()=='f'or interface[0].lower()=='g':
                        int_cost_default_value=1
                    else :
                        int_cost_default_value=64        
                        Int_Cost_command=f'ip ospf cost {int_cost_default_value}'
                        ssh.send_config_set([interface_command,Int_Cost_command], exit_config_mode=False) 
                        self.log_output(f"returning for the default value of the interface {interface} cost that is {int_cost_default_value}",output_text)
                else :
                    Int_Cost_command=f'ip ospf cost {Int_Cost_var}'
                    self.log_output(f"Sending command:{Int_Cost_command}",output_text)
                    ssh.send_config_set([interface_command,Int_Cost_var], exit_config_mode=False)
           
            self.log_output(f'Success: Router "{device}" configured with OSPF successfully.',output_text)

        # Submit button
        submit_button = ctk.CTkButton(config_frame, text="Submit Configuration", command=submit_configuration)
        submit_button.grid(row=6, columnspan=5, pady=10)
        error_label = tk.Label(config_frame, text="", bg="#212121", fg="red")
        error_label.grid(row=7, columnspan=5, pady=10)
        show_frame = ctk.CTkFrame(config_frame)
        show_frame.grid(row=8, columnspan=5, pady=10, sticky="ew")
        # Example OSPF show commands
        ospf_commands = [
            "show ip ospf",
            "show ip ospf neighbor",
            "show ip ospf database",
            "show ip ospf interface",
            "show ip route",
            "show ip route ospf",
            "show ip protocols"
        ]

        # Combobox for selecting a command
        command_var = ctk.StringVar(value="")
        command_label = ctk.CTkLabel(show_frame, text="Select OSPF Show Command:")
        command_label.grid(row=0, column=0)
        command_menu = ctk.CTkOptionMenu(show_frame, variable=command_var, values=ospf_commands)
        command_menu.grid(row=0, column=1)

        # Button to send the selected command and display output
        def send_command():
            selected_command = command_var.get()
            if selected_command:
                # Send the command to the router
                output = ssh.send_config_set(['do ' + selected_command], exit_config_mode=False)
                self.log_output(f"output for the show command of {device} :\n{output}", output_text)

        send_command_button = ctk.CTkButton(show_frame, text="Send Command", command=send_command)
        send_command_button.grid(row=0, column=2, pady=10)
        # Add a horizontal line (separator)
        separator = ctk.CTkFrame(show_frame, height=2)
        separator.grid(row=1, columnspan=10, sticky="ew", pady=5)

    
    def configure_DSR(self, ssh, device, output_text, tab):
            """Continues configuration in the same tab by clearing previous content."""
            # Clear the existing tab's contents
            for widget in tab.winfo_children():
             widget.destroy()

            config_frame = ctk.CTkFrame(tab)
            config_frame.pack(pady=10, fill="both", expand=True)
            
            ctk.CTkLabel(config_frame, text="Exit Interface:").grid(row=0, column=0)
            interface_entry = ctk.CTkEntry(config_frame)
            interface_entry.grid(row=0, column=1)
        
            def D_submit_configuration():
                exit_int = interface_entry.get()
                if not self.is_valid_interface(exit_int):
                    error_label.configure(text="Input Error: interface must be like f0/0 , g0/1 or s1/1 , loopback0.")
                    return
                # Handle Hello Interval
                default_routing_command=f'ip route 0.0.0.0 0.0.0.0 {exit_int}'
                self.log_output(f"Sending command:{default_routing_command}",output_text)
                ssh.send_config_set([default_routing_command], exit_config_mode=False)  
            
                self.log_output(f'Success: Router "{device}" configured with Default Static Routing successfully.',output_text)
                
            # Submit button
            submit_button =ctk.CTkButton(config_frame, text="Submit Configuration", command=D_submit_configuration)
            submit_button.grid(row=1, columnspan=2, pady=10)
            error_label = tk.Label(config_frame, text="", bg="#212121", fg="red")
            error_label.grid(row=2, columnspan=2, pady=10)
            # Add a horizontal line (separator)
            separator = ctk.CTkFrame(config_frame, height=2)
            separator.grid(row=3, columnspan=10, sticky="ew", pady=5)

             # Output text box
            output_text = scrolledtext.ScrolledText(config_frame, width=100, height=15, bg="black", fg="white")
            output_text.grid(row=10, columnspan=5, pady=10)

            clear_button = ctk.CTkButton(config_frame, text="Clear", command=lambda: self.clear_textbox(output_text))
            clear_button.grid(row=11, column=1, pady=10)
            back_button = ctk.CTkButton(config_frame, text="Back to Main", command=self.back_to_main)
            back_button.grid(row=12, column=1, pady=5)
            # Interface entry

    def configure_basic_router(self, ssh, device, output_text, tab):
        """Configures basic router settings with each method in a separate line, configurable independently."""
        # Clear the existing tab's contents
        for widget in tab.winfo_children():
            widget.destroy()

        config_frame = ctk.CTkFrame(tab)
        config_frame.pack(pady=10, fill="both", expand=True)
        
        # Output text box
        output_text = scrolledtext.ScrolledText(config_frame, width=100, height=15, bg="black", fg="white")
        output_text.grid(row=20, columnspan=10, pady=10)

        # Error label for feedback
        error_label = tk.Label(config_frame, text="", bg="#212121", fg="red")
        error_label.grid(row=13, columnspan=10, pady=10)

        clear_button = ctk.CTkButton(config_frame, text="Clear", command=lambda: self.clear_textbox(output_text))
        clear_button.grid(row=21, column=1, pady=10)

        back_button = ctk.CTkButton(config_frame, text="Back to Main", command=self.back_to_main)
        back_button.grid(row=22, column=1, pady=5)

        # Hostname
        ctk.CTkLabel(config_frame, text="Hostname:").grid(row=0, column=0, padx=5, pady=5)
        hostname_entry = ctk.CTkEntry(config_frame)
        hostname_entry.grid(row=0, column=1, padx=5, pady=5)
        hostname_button = ctk.CTkButton(config_frame, text="Apply Hostname", command=lambda: apply_hostname())
        hostname_button.grid(row=0, column=2, padx=5, pady=5)

        def apply_hostname():
            hostname = hostname_entry.get().strip()
            if hostname and not self.validate_hostname(hostname):
                error_label.configure(text="Input Error: Hostname must be alphanumeric, hyphens allowed, max 63 chars.")
                return
            if hostname:
                self.log_output(f"Sending command: hostname {hostname}", output_text)
                output = ssh.send_config_set([f"hostname {hostname}"], exit_config_mode=False)
                self.log_output(f"Router output:\n{output}", output_text)
                if any(line.strip().startswith('%') for line in output.splitlines()):
                    error_label.configure(text="Configuration Error: Check output for details.")
                    self.log_output(f"Error: Failed to set hostname {hostname} on {device}.", output_text)
                else:
                    error_label.configure(text="")
                    self.log_output(f"Success: Hostname set to {hostname} on {device}.", output_text)
            else:
                self.log_output("Hostname not provided, skipping.", output_text)

        # Interface configuration
        ctk.CTkLabel(config_frame, text="Interface (e.g., g0/0):").grid(row=1, column=0, padx=5, pady=5)
        interface_entry = ctk.CTkEntry(config_frame)
        interface_entry.grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkLabel(config_frame, text="IP Address:").grid(row=1, column=2, padx=5, pady=5)
        ip_entry = ctk.CTkEntry(config_frame)
        ip_entry.grid(row=1, column=3, padx=5, pady=5)
        ctk.CTkLabel(config_frame, text="Subnet Mask:").grid(row=1, column=4, padx=5, pady=5)
        subnet_entry = ctk.CTkEntry(config_frame)
        subnet_entry.grid(row=1, column=5, padx=5, pady=5)
        clock_rate_var = ctk.StringVar(value="no change")
        clock_rate_menu = ctk.CTkOptionMenu(config_frame, variable=clock_rate_var, values=["no change", "default", "custom"])
        clock_rate_menu.grid(row=1, column=6, padx=5, pady=5)
        clock_rate_menu.grid_remove()
        dce_alert_label = ctk.CTkLabel(config_frame, text="Clock rate applies to serial interfaces on the DCE (ISP) side only.", text_color="orange")
        dce_alert_label.grid(row=2, column=0, columnspan=8, padx=5, pady=2, sticky="w")
        dce_alert_label.grid_remove()
        ctk.CTkLabel(config_frame, text="Clock Rate:").grid(row=3, column=0, padx=5, pady=5)
        clock_rate_entry = ctk.CTkEntry(config_frame)
        clock_rate_entry.grid(row=3, column=1, padx=5, pady=5)
        clock_rate_entry.grid_remove()
        interface_button = ctk.CTkButton(config_frame, text="Apply Interface", command=lambda: apply_interface())
        interface_button.grid(row=3, column=2, padx=5, pady=5)

        def update_interface_fields(*args):
            interface = interface_entry.get().strip().lower()
            is_serial = interface.startswith('s') and self.is_valid_interface(interface)
            if is_serial:
                clock_rate_menu.grid(row=1, column=6)
                dce_alert_label.grid(row=2, column=0, columnspan=8)
                if clock_rate_var.get() == "custom":
                    clock_rate_entry.grid(row=3, column=1)
                else:
                    clock_rate_entry.grid_remove()
            else:
                clock_rate_menu.grid_remove()
                clock_rate_entry.grid_remove()
                dce_alert_label.grid_remove()

        interface_entry.bind("<KeyRelease>", lambda event: update_interface_fields())
        clock_rate_var.trace("w", update_interface_fields)

        def apply_interface():
            interface = interface_entry.get().strip()
            ip_address = ip_entry.get().strip()
            subnet_mask = subnet_entry.get().strip()
            clock_rate_mode = clock_rate_var.get()
            clock_rate = clock_rate_entry.get().strip() if clock_rate_mode == "custom" else ""

            if interface or ip_address or subnet_mask or clock_rate_mode != "no change":
                if not interface or not ip_address or not subnet_mask:
                    error_label.configure(text="Input Error: Interface, IP address, and subnet mask must all be provided.")
                    return
                if not self.is_valid_interface(interface):
                    error_label.configure(text="Input Error: Interface must be like f0/0, g0/1, s1/1, or loopback0.")
                    return
                if not self.validate_ip(ip_address):
                    error_label.configure(text="Input Error: Invalid IP address format.")
                    return
                if not self.validate_subnet_mask(subnet_mask):
                    error_label.configure(text="Input Error: Invalid subnet mask format.")
                    return

                commands = [f"interface {interface}", f"ip address {ip_address} {subnet_mask}", "no shutdown"]

                if clock_rate_mode != "no change":
                    if not interface.lower().startswith('s'):
                        error_label.configure(text="Input Error: Clock rate is only applicable to serial interfaces (e.g., s1/0).")
                        return
                    if clock_rate_mode == "custom":
                        if not clock_rate.isdigit() or int(clock_rate) < 1200 or int(clock_rate) > 2000000:
                            error_label.configure(text="Input Error: Clock rate must be a number between 1200 and 2000000.")
                            return
                        commands.append(f"clock rate {clock_rate}")
                    elif clock_rate_mode == "default":
                        commands.append("clock rate 2000000")

                for cmd in commands:
                    self.log_output(f"Sending command: {cmd}", output_text)
                output = ssh.send_config_set(commands, exit_config_mode=False)
                self.log_output(f"Router output:\n{output}", output_text)
                if any(line.strip().startswith('%') for line in output.splitlines()):
                    error_label.configure(text="Configuration Error: Check output for details.")
                    self.log_output(f"Error: Failed to configure interface {interface} on {device}.", output_text)
                else:
                    error_label.configure(text="")
                    self.log_output(f"Success: Interface {interface} configured with IP {ip_address} on {device}.", output_text)
            else:
                self.log_output("Interface configuration not provided, skipping.", output_text)

        # Enable Password
        ctk.CTkLabel(config_frame, text="Enable Password Type:").grid(row=4, column=0, padx=5, pady=5)
        enable_pass_type = ctk.StringVar(value="clear")
        ctk.CTkOptionMenu(config_frame, variable=enable_pass_type, values=["clear", "md5"]).grid(row=4, column=1, padx=5, pady=5)
        ctk.CTkLabel(config_frame, text="Enable Password:").grid(row=4, column=2, padx=5, pady=5)
        enable_pass_entry = ctk.CTkEntry(config_frame, show="*")
        enable_pass_entry.grid(row=4, column=3, padx=5, pady=5)
        enable_pass_button = ctk.CTkButton(config_frame, text="Apply Enable Password", command=lambda: apply_enable_password())
        enable_pass_button.grid(row=4, column=4, padx=5, pady=5)

        def apply_enable_password():
            enable_pass = enable_pass_entry.get().strip()
            enable_type = enable_pass_type.get()
            if enable_pass:
                cmd = f"enable password {enable_pass}" if enable_type == "clear" else f"enable secret {enable_pass}"
                self.log_output(f"Sending command: {cmd}", output_text)
                output = ssh.send_config_set([cmd], exit_config_mode=False)
                self.log_output(f"Router output:\n{output}", output_text)
                if any(line.strip().startswith('%') for line in output.splitlines()):
                    error_label.configure(text="Configuration Error: Check output for details.")
                    self.log_output(f"Error: Failed to set enable password ({enable_type}) on {device}.", output_text)
                else:
                    error_label.configure(text="")
                    self.log_output(f"Success: Enable password ({enable_type}) set on {device}.", output_text)
            else:
                self.log_output("Enable password not provided, skipping.", output_text)

        # Service Password Encryption
        ctk.CTkLabel(config_frame, text="Service Password Encryption:").grid(row=5, column=0, padx=5, pady=5)
        encrypt_pass_var = ctk.StringVar(value="no")
        ctk.CTkOptionMenu(config_frame, variable=encrypt_pass_var, values=["yes", "no"]).grid(row=5, column=1, padx=5, pady=5)
        encrypt_pass_button = ctk.CTkButton(config_frame, text="Apply Encryption", command=lambda: apply_encrypt_password())
        encrypt_pass_button.grid(row=5, column=2, padx=5, pady=5)

        def apply_encrypt_password():
            cmd = "service password-encryption" if encrypt_pass_var.get() == "yes" else "no service password-encryption"
            self.log_output(f"Sending command: {cmd}", output_text)
            output = ssh.send_config_set([cmd], exit_config_mode=False)
            self.log_output(f"Router output:\n{output}", output_text)
            if any(line.strip().startswith('%') for line in output.splitlines()):
                error_label.configure(text="Configuration Error: Check output for details.")
                self.log_output(f"Error: Failed to configure service password encryption on {device}.", output_text)
            else:
                error_label.configure(text="")
                self.log_output(f"Success: Service password encryption {'enabled' if encrypt_pass_var.get() == 'yes' else 'disabled'} on {device}.", output_text)

        # Banner
        ctk.CTkLabel(config_frame, text="Banner Message (MOTD):").grid(row=6, column=0, padx=5, pady=5)
        banner_entry = ctk.CTkEntry(config_frame)
        banner_entry.grid(row=6, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        banner_button = ctk.CTkButton(config_frame, text="Apply Banner", command=lambda: apply_banner())
        banner_button.grid(row=6, column=4, padx=5, pady=5)

        def apply_banner():
            banner = banner_entry.get().strip()
            if banner:
                cmd = f"banner motd # {banner} #"
                self.log_output(f"Sending command: {cmd}", output_text)
                output = ssh.send_config_set([cmd], exit_config_mode=False)
                self.log_output(f"Router output:\n{output}", output_text)
                if any(line.strip().startswith('%') for line in output.splitlines()):
                    error_label.configure(text="Configuration Error: Check output for details.")
                    self.log_output(f"Error: Failed to set banner on {device}.", output_text)
                else:
                    error_label.configure(text="")
                    self.log_output(f"Success: Banner set on {device}.", output_text)
            else:
                self.log_output("Banner message not provided, skipping.", output_text)

        # Telnet
        ctk.CTkLabel(config_frame, text="Enable Telnet:").grid(row=7, column=0, padx=5, pady=5)
        telnet_var = ctk.StringVar(value="no")
        ctk.CTkOptionMenu(config_frame, variable=telnet_var, values=["yes", "no"]).grid(row=7, column=1, padx=5, pady=5)
        ctk.CTkLabel(config_frame, text="Telnet Password:").grid(row=7, column=2, padx=5, pady=5)
        telnet_pass_entry = ctk.CTkEntry(config_frame, show="*")
        telnet_pass_entry.grid(row=7, column=3, padx=5, pady=5)
        telnet_pass_entry.grid_remove()
        telnet_button = ctk.CTkButton(config_frame, text="Apply Telnet", command=lambda: apply_telnet())
        telnet_button.grid(row=7, column=4, padx=5, pady=5)

        def update_telnet_fields(*args):
            if telnet_var.get() == "yes":
                telnet_pass_entry.grid(row=7, column=3)
            else:
                telnet_pass_entry.grid_remove()

        telnet_var.trace("w", update_telnet_fields)

        def apply_telnet():
            telnet_enabled = telnet_var.get()
            telnet_pass = telnet_pass_entry.get().strip()
            if telnet_enabled == "yes":
                if not telnet_pass:
                    error_label.configure(text="Input Error: Telnet password cannot be empty when Telnet is enabled.")
                    return
                commands = ["line vty 0 4", f"password {telnet_pass}", "login", "transport input telnet"]
                for cmd in commands:
                    self.log_output(f"Sending command: {cmd}", output_text)
                output = ssh.send_config_set(commands, exit_config_mode=False)
                self.log_output(f"Router output:\n{output}", output_text)
                if any(line.strip().startswith('%') for line in output.splitlines()):
                    error_label.configure(text="Configuration Error: Check output for details.")
                    self.log_output(f"Error: Failed to enable Telnet on {device}.", output_text)
                else:
                    error_label.configure(text="")
                    self.log_output(f"Success: Telnet enabled on {device}.", output_text)
            else:
                self.log_output("Telnet not enabled, skipping.", output_text)

        # SSH
        ctk.CTkLabel(config_frame, text="Enable SSH:").grid(row=8, column=0, padx=5, pady=5)
        ssh_var = ctk.StringVar(value="no")
        ctk.CTkOptionMenu(config_frame, variable=ssh_var, values=["yes", "no", "default"]).grid(row=8, column=1, padx=5, pady=5)
        ctk.CTkLabel(config_frame, text="Domain Name:").grid(row=8, column=2, padx=5, pady=5)
        domain_entry = ctk.CTkEntry(config_frame)
        domain_entry.grid(row=8, column=3, padx=5, pady=5)
        domain_entry.grid_remove()
        ctk.CTkLabel(config_frame, text="SSH Username:").grid(row=8, column=4, padx=5, pady=5)
        ssh_user_entry = ctk.CTkEntry(config_frame)
        ssh_user_entry.grid(row=8, column=5, padx=5, pady=5)
        ssh_user_entry.grid_remove()
        ctk.CTkLabel(config_frame, text="SSH Password:").grid(row=9, column=0, padx=5, pady=5)
        ssh_pass_entry = ctk.CTkEntry(config_frame, show="*")
        ssh_pass_entry.grid(row=9, column=1, padx=5, pady=5)
        ssh_pass_entry.grid_remove()
        ctk.CTkLabel(config_frame, text="SSH Version:").grid(row=9, column=2, padx=5, pady=5)
        ssh_version_var = ctk.StringVar(value="2")
        ssh_version_menu = ctk.CTkOptionMenu(config_frame, variable=ssh_version_var, values=["1", "2"])
        ssh_version_menu.grid(row=9, column=3, padx=5, pady=5)
        ssh_version_menu.grid_remove()
        ctk.CTkLabel(config_frame, text="Privilege Level:").grid(row=9, column=4, padx=5, pady=5)
        privilege_var = ctk.StringVar(value="default")
        privilege_menu = ctk.CTkOptionMenu(config_frame, variable=privilege_var, values=["default", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"])
        privilege_menu.grid(row=9, column=5, padx=5, pady=5)
        privilege_menu.grid_remove()
        ctk.CTkLabel(config_frame, text="VTY Logins:").grid(row=10, column=0, padx=5, pady=5)
        vty_logins_var = ctk.StringVar(value="default")
        vty_logins_menu = ctk.CTkOptionMenu(config_frame, variable=vty_logins_var, values=["default", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"])
        vty_logins_menu.grid(row=10, column=1, padx=5, pady=5)
        vty_logins_menu.grid_remove()
        ctk.CTkLabel(config_frame, text="RSA Key Length:").grid(row=10, column=2, padx=5, pady=5)
        key_length_var = ctk.StringVar(value="default")
        key_length_menu = ctk.CTkOptionMenu(config_frame, variable=key_length_var, values=["default", "1024", "2048"])
        key_length_menu.grid(row=10, column=3, padx=5, pady=5)
        key_length_menu.grid_remove()
        ssh_button = ctk.CTkButton(config_frame, text="Apply SSH", command=lambda: apply_ssh())
        ssh_button.grid(row=8, column=6, padx=5, pady=5)

        def update_ssh_fields(*args):
            ssh_mode = ssh_var.get()
            if ssh_mode == "yes":
                domain_entry.grid(row=8, column=3)
                ssh_user_entry.grid(row=8, column=5)
                ssh_pass_entry.grid(row=9, column=1)
                ssh_version_menu.grid(row=9, column=3)
                privilege_menu.grid(row=9, column=5)
                vty_logins_menu.grid(row=10, column=1)
                key_length_menu.grid(row=10, column=3)
            else:
                domain_entry.grid_remove()
                ssh_user_entry.grid_remove()
                ssh_pass_entry.grid_remove()
                ssh_version_menu.grid_remove()
                privilege_menu.grid_remove()
                vty_logins_menu.grid_remove()
                key_length_menu.grid_remove()

        ssh_var.trace("w", update_ssh_fields)

        def apply_ssh():
            ssh_mode = ssh_var.get()
            if ssh_mode in ["yes", "default"]:
                domain_name = domain_entry.get().strip() if ssh_mode == "yes" else "example.com"
                ssh_username = ssh_user_entry.get().strip() if ssh_mode == "yes" else "admin"
                ssh_password = ssh_pass_entry.get().strip() if ssh_mode == "yes" else "cisco"
                ssh_version = ssh_version_var.get() if ssh_mode == "yes" else "2"
                privilege = privilege_var.get() if ssh_mode == "yes" else "15"
                vty_logins = vty_logins_var.get() if ssh_mode == "yes" else "5"
                key_length = key_length_var.get() if ssh_mode == "yes" else "1024"

                if ssh_mode == "yes":
                    if not domain_name :
                        error_label.configure(text="Input Error: Domain name must be alphanumeric, hyphens allowed.")
                        return
                    if not ssh_username or not ssh_username.isalnum():
                        error_label.configure(text="Input Error: SSH username must be alphanumeric.")
                        return
                    if not ssh_password:
                        error_label.configure(text="Input Error: SSH password cannot be empty.")
                        return
                    if ssh_version not in ["1", "2"]:
                        error_label.configure(text="Input Error: SSH version must be 1 or 2.")
                        return
                    if privilege != "default" and (not privilege.isdigit() or not 1 <= int(privilege) <= 15):
                        error_label.configure(text="Input Error: Privilege level must be 1-15 or default.")
                        return
                    if vty_logins != "default" and (not vty_logins.isdigit() or not 1 <= int(vty_logins) <= 16):
                        error_label.configure(text="Input Error: VTY logins must be 1-16 or default.")
                        return
                    if key_length != "default" and key_length not in ["1024", "2048"]:
                        error_label.configure(text="Input Error: Key length must be 1024, 2048, or default.")
                        return

                privilege = "15" if privilege == "default" else privilege
                vty_logins = "5" if vty_logins == "default" else vty_logins
                key_length = "1024" if key_length == "default" else key_length
                vty_range = f"0 {int(vty_logins) - 1}" if int(vty_logins) > 0 else "0"
                commands = [
                    f"ip domain-name {domain_name}",
                    f"ip ssh version {ssh_version}",
                    f"crypto key generate rsa general-keys modulus {key_length}",
                    f"username {ssh_username} privilege {privilege} secret {ssh_password}",
                    f"line vty {vty_range}",
                    "transport input ssh",
                    "login local"
                ]
                for cmd in commands:
                    self.log_output(f"Sending command: {cmd}", output_text)
                output = ssh.send_config_set(commands, exit_config_mode=False)
                self.log_output(f"Router output:\n{output}", output_text)
    
                error_label.configure(text="")
                self.log_output(f"Success: SSH (version {ssh_version}) enabled on {device} with {vty_logins} VTY logins.", output_text)
            else:
                self.log_output("SSH not enabled, skipping.", output_text)

        # IP Domain Lookup
        ctk.CTkLabel(config_frame, text="IP Domain Lookup:").grid(row=11, column=0, padx=5, pady=5)
        domain_lookup_var = ctk.StringVar(value="no")
        ctk.CTkOptionMenu(config_frame, variable=domain_lookup_var, values=["yes", "no"]).grid(row=11, column=1, padx=5, pady=5)
        domain_lookup_button = ctk.CTkButton(config_frame, text="Apply Domain Lookup", command=lambda: apply_domain_lookup())
        domain_lookup_button.grid(row=11, column=2, padx=5, pady=5)

        def apply_domain_lookup():
            cmd = "ip domain-lookup" if domain_lookup_var.get() == "yes" else "no ip domain-lookup"
            self.log_output(f"Sending command: {cmd}", output_text)
            output = ssh.send_config_set([cmd], exit_config_mode=False)
            self.log_output(f"Router output:\n{output}", output_text)
            if any(line.strip().startswith('%') for line in output.splitlines()):
                error_label.configure(text="Configuration Error: Check output for details.")
                self.log_output(f"Error: Failed to configure IP domain lookup on {device}.", output_text)
            else:
                error_label.configure(text="")
                self.log_output(f"Success: IP domain lookup {'enabled' if domain_lookup_var.get() == 'yes' else 'disabled'} on {device}.", output_text)

        # Console Port Security
        ctk.CTkLabel(config_frame, text="Console Password:").grid(row=12, column=0, padx=5, pady=5)
        console_pass_entry = ctk.CTkEntry(config_frame, show="*")
        console_pass_entry.grid(row=12, column=1, padx=5, pady=5)
        ctk.CTkLabel(config_frame, text="Logging Synchronous:").grid(row=12, column=2, padx=5, pady=5)
        logging_sync_var = ctk.StringVar(value="no")
        ctk.CTkOptionMenu(config_frame, variable=logging_sync_var, values=["yes", "no"]).grid(row=12, column=3, padx=5, pady=5)
        ctk.CTkLabel(config_frame, text="Exec Timeout:").grid(row=12, column=4, padx=5, pady=5)
        exec_timeout_var = ctk.StringVar(value="no change")
        exec_timeout_menu = ctk.CTkOptionMenu(config_frame, variable=exec_timeout_var, values=["no change", "default", "custom"])
        exec_timeout_menu.grid(row=12, column=5, padx=5, pady=5)
        exec_timeout_entry = ctk.CTkEntry(config_frame)
        exec_timeout_entry.grid(row=12, column=6, padx=5, pady=5)
        exec_timeout_entry.grid_remove()
        console_button = ctk.CTkButton(config_frame, text="Apply Console Security", command=lambda: apply_console())
        console_button.grid(row=12, column=7, padx=5, pady=5)

        def update_exec_timeout_fields(*args):
            if exec_timeout_var.get() == "custom":
                exec_timeout_entry.grid(row=12, column=6)
            else:
                exec_timeout_entry.grid_remove()

        exec_timeout_var.trace("w", update_exec_timeout_fields)

        def apply_console():
            console_pass = console_pass_entry.get().strip()
            logging_sync = logging_sync_var.get()
            exec_timeout_mode = exec_timeout_var.get()
            exec_timeout = exec_timeout_entry.get().strip() if exec_timeout_mode == "custom" else ""

            commands = ["line console 0"]
            if console_pass:
                commands.extend([f"password {console_pass}", "login"])
            if logging_sync == "yes":
                commands.append("logging synchronous")
            elif logging_sync == "no":
                commands.append("no logging synchronous")
            if exec_timeout_mode == "custom":
                if not exec_timeout.isdigit() or int(exec_timeout) < 0 or int(exec_timeout) > 35791:
                    error_label.configure(text="Input Error: Exec timeout must be a number between 0 and 35791 minutes.")
                    return
                commands.append(f"exec-timeout {exec_timeout} 0")
            elif exec_timeout_mode == "default":
                commands.append("exec-timeout 10 0")

            if len(commands) > 1:  # Only send if there's more than just "line console 0"
                for cmd in commands:
                    self.log_output(f"Sending command: {cmd}", output_text)
                output = ssh.send_config_set(commands, exit_config_mode=False)
                self.log_output(f"Router output:\n{output}", output_text)
                if any(line.strip().startswith('%') for line in output.splitlines()):
                    error_label.configure(text="Configuration Error: Check output for details.")
                    self.log_output(f"Error: Failed to configure console security on {device}.", output_text)
                else:
                    error_label.configure(text="")
                    self.log_output(f"Success: Console security configured on {device}.", output_text)
            else:
                self.log_output("Console configuration not provided, skipping.", output_text)

        # Save Configuration
        ctk.CTkLabel(config_frame, text="Save Configuration:").grid(row=14, column=0, padx=5, pady=5)
        save_config_var = ctk.StringVar(value="yes")
        ctk.CTkOptionMenu(config_frame, variable=save_config_var, values=["yes", "no"]).grid(row=14, column=1, padx=5, pady=5)
        save_button = ctk.CTkButton(config_frame, text="Apply Save", command=lambda: apply_save_config())
        save_button.grid(row=14, column=2, padx=5, pady=5)

        def apply_save_config():
            if save_config_var.get() == "yes":
                cmd = "do write memory"
                self.log_output(f"Sending command: {cmd}", output_text)
                output = ssh.send_config_set([cmd], exit_config_mode=False)
                self.log_output(f"Router output:\n{output}", output_text)
                if any(line.strip().startswith('%') for line in output.splitlines()):
                    error_label.configure(text="Configuration Error: Check output for details.")
                    self.log_output(f"Error: Failed to save configuration on {device}.", output_text)
                else:
                    error_label.configure(text="")
                    self.log_output(f"Success: Configuration saved on {device}.", output_text)
            else:
                self.log_output("Configuration save skipped.", output_text)

        # Show commands
        show_frame = ctk.CTkFrame(config_frame)
        show_frame.grid(row=15, columnspan=10, pady=10, sticky="ew")
        show_commands = [
            "show running-config",
            "show ip interface brief",
            "show crypto key mypubkey rsa",
            "show users",
            "show version"
        ]

        command_var = ctk.StringVar(value="")
        command_label = ctk.CTkLabel(show_frame, text="Select Show Command:")
        command_label.grid(row=0, column=0, padx=5)
        command_menu = ctk.CTkOptionMenu(show_frame, variable=command_var, values=show_commands)
        command_menu.grid(row=0, column=1, padx=5)

        def send_command():
            selected_command = command_var.get()
            if selected_command:
                cmd = f"do {selected_command}"
                self.log_output(f"Sending command: {cmd}", output_text)
                output = ssh.send_config_set([cmd], exit_config_mode=False)
                self.log_output(f"Output for show command on {device}:\n{output}", output_text)

        send_command_button = ctk.CTkButton(show_frame, text="Send Command", command=send_command)
        send_command_button.grid(row=0, column=2, padx=5, pady=10)

    def configure_router_on_a_stick(self, ssh, device, output_text, tab):
        """Configures Router on a Stick for inter-VLAN routing with dynamic subinterfaces."""
        # Clear the existing tab's contents
        for widget in tab.winfo_children():
            widget.destroy()

        config_frame = ctk.CTkFrame(tab)
        config_frame.pack(pady=10, fill="both", expand=True)

        # Output text box
        output_text = scrolledtext.ScrolledText(config_frame, width=100, height=15, bg="black", fg="white")
        output_text.grid(row=10, column=0, columnspan=6, pady=10)

        # Physical Interface
        ctk.CTkLabel(config_frame, text="Physical Interface (e.g., g0/0):").grid(row=0, column=0, padx=5, pady=5)
        interface_entry = ctk.CTkEntry(config_frame)
        interface_entry.grid(row=0, column=1, padx=5, pady=5)
        interface_alert_label = ctk.CTkLabel(config_frame, text="The physical interface will be enabled before configuring subinterfaces.", text_color="orange")
        interface_alert_label.grid(row=1, column=0, columnspan=6, padx=5, pady=2, sticky="w")
        interface_alert_label.grid_remove()

        def update_interface_alert(*args):
            interface = interface_entry.get().strip()
            if interface and self.is_valid_interface(interface):
                interface_alert_label.grid(row=1, column=0, columnspan=6)
            else:
                interface_alert_label.grid_remove()

        interface_entry.bind("<KeyRelease>", update_interface_alert)

        # Subinterface configuration headers
        header_frame = ctk.CTkFrame(config_frame)
        header_frame.grid(row=2, column=0, columnspan=6, pady=5, sticky="ew")
        ctk.CTkLabel(header_frame, text="VLAN ID").grid(row=0, column=0, padx=25, pady=2)
        ctk.CTkLabel(header_frame, text="IP Address").grid(row=0, column=1, padx=50, pady=2)
        ctk.CTkLabel(header_frame, text="Subnet Mask").grid(row=0, column=2, padx=50, pady=2)

        # Subinterface configuration
        subinterface_frame = ctk.CTkScrollableFrame(config_frame, height=100)
        subinterface_frame.grid(row=3, column=0, columnspan=6, pady=5, sticky="ew")
        subinterface_entries = []

        def add_subinterface():
            row = len(subinterface_entries)
            vlan_entry = ctk.CTkEntry(subinterface_frame, width=100)
            vlan_entry.grid(row=row, column=0, padx=5, pady=2)
            ip_entry = ctk.CTkEntry(subinterface_frame, width=150)
            ip_entry.grid(row=row, column=1, padx=5, pady=2)
            subnet_entry = ctk.CTkEntry(subinterface_frame, width=150)
            subnet_entry.grid(row=row, column=2, padx=5, pady=2)
            remove_button = ctk.CTkButton(subinterface_frame, text="Remove", command=lambda: remove_subinterface(row))
            remove_button.grid(row=row, column=3, padx=5, pady=2)
            subinterface_entries.append((vlan_entry, ip_entry, subnet_entry, remove_button))

        def remove_subinterface(row):
            if subinterface_entries:
                entry = subinterface_entries.pop(row)
                for widget in entry:
                    widget.destroy()
                # Re-grid remaining entries to fill gaps
                for i, (vlan, ip, subnet, btn) in enumerate(subinterface_entries):
                    vlan.grid(row=i, column=0)
                    ip.grid(row=i, column=1)
                    subnet.grid(row=i, column=2)
                    btn.grid(row=i, column=3)

        # Add initial subinterface
        add_subinterface()

        # Add subinterface button
        add_subinterface_button = ctk.CTkButton(config_frame, text="Add Subinterface", command=add_subinterface)
        add_subinterface_button.grid(row=4, column=0, padx=5, pady=5)

        # Apply ROAS configuration
        def apply_roas():
            interface = interface_entry.get().strip()
            if not interface:
                error_label.configure(text="Input Error: Physical interface must be provided.")
                return
            if not self.is_valid_interface(interface):
                error_label.configure(text="Input Error: Interface must be like g0/0, g0/1, s1/1.")
                return

            # Get existing interface subnets
            try:
                output = ssh.send_config_set(['do show running-config | include interface|ip address'], exit_config_mode=False)
                existing_subnets = []
                current_interface = None
                for line in output.splitlines():
                    line = line.strip()
                    if line.startswith('interface'):
                        current_interface = line.split()[1]
                    elif line.startswith('ip address') and current_interface:
                        parts = line.split()
                        if len(parts) >= 4:
                            ip = parts[2]
                            mask = parts[3]
                            if self.validate_ip(ip) and self.validate_subnet_mask(mask):
                                network = self.calculate_network(ip, mask)
                                existing_subnets.append((current_interface, network))
            except Exception as e:
                error_label.configure(text=f"Error: Failed to retrieve interface configurations: {str(e)}")
                return

            # Validate subinterface inputs and check for subnet overlaps
            subinterface_configs = []
            for vlan_entry, ip_entry, subnet_entry, _ in subinterface_entries:
                vlan = vlan_entry.get().strip()
                ip = ip_entry.get().strip()
                subnet = subnet_entry.get().strip()

                if not (vlan or ip or subnet):
                    continue  # Skip empty subinterfaces
                if not (vlan and ip and subnet):
                    error_label.configure(text="Input Error: VLAN ID, IP address, and subnet mask must all be provided for each subinterface.")
                    return
                if not vlan.isdigit() or not 1 <= int(vlan) <= 4094:
                    error_label.configure(text="Input Error: VLAN ID must be a number between 1 and 4094.")
                    return
                if not self.validate_ip(ip):
                    error_label.configure(text="Input Error: Invalid IP address format.")
                    return
                if not self.validate_subnet_mask(subnet):
                    error_label.configure(text="Input Error: Invalid subnet mask format.")
                    return

                network = self.calculate_network(ip, subnet)
                subinterface = f"{interface}.{vlan}"  # Define subinterface here
                # Check against existing interfaces
                for intf, existing_net in existing_subnets:
                    if network == existing_net:
                        error_label.configure(text=f"Input Error: Subnet {network} overlaps with interface {intf}.")
                        return
                # Check against other subinterfaces in the form
                for other_vlan, other_subint, other_ip, other_subnet, other_network in subinterface_configs:
                    if vlan != other_vlan:  # Skip self-comparison
                        if network == other_network:
                            error_label.configure(text=f"Input Error: Subnet {network} overlaps with VLAN {other_vlan} subinterface.")
                            return
                subinterface_configs.append((vlan, subinterface, ip, subnet, network))

            if not subinterface_configs:
                error_label.configure(text="Input Error: At least one subinterface must be configured.")
                return

            # Build commands
            commands = [
                f"interface {interface}",
                "no shutdown"
            ]
            for vlan, subinterface, ip, subnet, _ in subinterface_configs:
                commands.extend([
                    f"interface {subinterface}",
                    f"encapsulation dot1Q {vlan}",
                    f"ip address {ip} {subnet}",
                    "no shutdown"
                ])

            for cmd in commands:
                self.log_output(f"Sending command: {cmd}", output_text)
                ssh.send_config_set([cmd], exit_config_mode=False)
            self.log_output(f"Success: Router on a Stick configured on {device} for interface {interface}.", output_text)

        apply_button = ctk.CTkButton(config_frame, text="Apply ROAS", command=apply_roas)
        apply_button.grid(row=5, column=0, padx=5, pady=5)

        clear_button = ctk.CTkButton(config_frame, text="Clear", command=lambda: self.clear_textbox(output_text))
        clear_button.grid(row=5, column=1, padx=5, pady=5)

        back_button = ctk.CTkButton(config_frame, text="Back to Main", command=self.back_to_main)
        back_button.grid(row=5, column=2, padx=5, pady=5)

        error_label = tk.Label(config_frame, text="", bg="#212121", fg="red")
        error_label.grid(row=6, column=0, columnspan=6, pady=5)

        # Show commands
        show_frame = ctk.CTkFrame(config_frame)
        show_frame.grid(row=7, column=0, columnspan=6, pady=10, sticky="ew")
        show_commands = [
            "show running-config",
            "show ip interface brief",
            "show ip route",
            "show interfaces"
        ]

        command_var = ctk.StringVar(value="")
        command_label = ctk.CTkLabel(show_frame, text="Select Show Command:")
        command_label.grid(row=0, column=0, padx=5)
        command_menu = ctk.CTkOptionMenu(show_frame, variable=command_var, values=show_commands)
        command_menu.grid(row=0, column=1, padx=5)

        def send_command():
            selected_command = command_var.get()
            if selected_command:
                output = ssh.send_config_set(['do ' + selected_command], exit_config_mode=False)
                self.log_output(f"Output for show command on {device}:\n{output}", output_text)

        send_command_button = ctk.CTkButton(show_frame, text="Send Command", command=send_command)
        send_command_button.grid(row=0, column=2, padx=5, pady=10)


        separator = ctk.CTkFrame(show_frame, height=2)
        separator.grid(row=1, columnspan=10, sticky="ew", pady=5)

    def calculate_network(self, ip, mask):
        """Calculates the network address from an IP and subnet mask."""
        try:
            ip_parts = list(map(int, ip.split('.')))
            mask_parts = list(map(int, mask.split('.')))
            network = [ip_parts[i] & mask_parts[i] for i in range(4)]
            return '.'.join(map(str, network)) + '/24'  # Assuming /24 for simplicity; adjust if needed
        except Exception:
            return None
        
    def configure_dhcp_services(self, ssh, device, output_text, tab):
        """Configures DHCP server, relay agent, and snooping on a router or Layer 3 switch."""
        # Clear the existing tab's contents
        for widget in tab.winfo_children():
            widget.destroy()

        config_frame = ctk.CTkFrame(tab)
        config_frame.pack(pady=10, fill="both", expand=True)

        # DHCP Server Pools Section
        ctk.CTkLabel(config_frame, text="DHCP Server Pools", font=("Arial", 14, "bold")).grid(row=1, column=0, columnspan=12, padx=5, pady=5, sticky="w")
        server_error_label = tk.Label(config_frame, text="", bg="#212121", fg="red")
        server_error_label.grid(row=2, column=0, columnspan=12, pady=5)
        pool_frame = ctk.CTkScrollableFrame(config_frame, height=200)
        pool_frame.grid(row=3, column=0, columnspan=12, pady=5, sticky="ew")
        pool_entries = []

        # Column labels for DHCP Server Pools (first row)
        ctk.CTkLabel(pool_frame, text="Pool Name").grid(row=0, column=0, padx=10, pady=2)
        ctk.CTkLabel(pool_frame, text="Network IP").grid(row=0, column=1, padx=10, pady=2)
        ctk.CTkLabel(pool_frame, text="Subnet Mask").grid(row=0, column=2, padx=10, pady=2)
        ctk.CTkLabel(pool_frame, text="Default Gateway").grid(row=0, column=3, padx=10, pady=2)
        # Column labels for DNS and Lease (second row, spanning fewer columns)
        ctk.CTkLabel(pool_frame, text="DNS Servers").grid(row=1, column=0, columnspan=2, padx=10, pady=2)
        ctk.CTkLabel(pool_frame, text="Lease (D H M)").grid(row=1, column=2, columnspan=2, padx=10, pady=2)

        def add_pool():
            row = len(pool_entries) * 3 + 2
            name_entry = ctk.CTkEntry(pool_frame, width=180, placeholder_text="e.g., POOL1")
            name_entry.grid(row=row, column=0, padx=10, pady=2)
            network_entry = ctk.CTkEntry(pool_frame, width=180, placeholder_text="e.g., 192.168.1.0")
            network_entry.grid(row=row, column=1, padx=10, pady=2)
            mask_entry = ctk.CTkEntry(pool_frame, width=180, placeholder_text="e.g., 255.255.255.0")
            mask_entry.grid(row=row, column=2, padx=10, pady=2)
            gateway_entry = ctk.CTkEntry(pool_frame, width=180, placeholder_text="e.g., 192.168.1.1")
            gateway_entry.grid(row=row, column=3, padx=10, pady=2)
            dns_entry = ctk.CTkEntry(pool_frame, width=360, placeholder_text="e.g., 8.8.8.8 8.8.4.4")
            dns_entry.grid(row=row + 1, column=0, columnspan=2, padx=10, pady=2)
            lease_entry = ctk.CTkEntry(pool_frame, width=360, placeholder_text="e.g., 1 0 0")
            lease_entry.grid(row=row + 1, column=2, columnspan=2, padx=10, pady=2)
            remove_button = ctk.CTkButton(pool_frame, text="Remove", command=lambda r=row: remove_pool(r))
            remove_button.grid(row=row, column=4, padx=10, pady=2)
            separator = ctk.CTkFrame(pool_frame, height=2, fg_color="gray")
            separator.grid(row=row + 2, column=0, columnspan=5, sticky="ew", pady=5)
            pool_entries.append((name_entry, network_entry, mask_entry, gateway_entry, dns_entry, lease_entry, remove_button, separator))
            if len(pool_entries) > 2:
                pool_frame.configure(height=200 + (len(pool_entries) - 2) * 60)

        def remove_pool(row):
            if pool_entries:
                for entry in pool_entries:
                    if entry[0].grid_info()['row'] == row:
                        for widget in entry:
                            widget.destroy()
                        pool_entries.remove(entry)
                        break
                for i, entry in enumerate(pool_entries):
                    new_row = i * 3 + 2
                    name_entry, network_entry, mask_entry, gateway_entry, dns_entry, lease_entry, remove_button, separator = entry
                    name_entry.grid(row=new_row, column=0, padx=10, pady=2)
                    network_entry.grid(row=new_row, column=1, padx=10, pady=2)
                    mask_entry.grid(row=new_row, column=2, padx=10, pady=2)
                    gateway_entry.grid(row=new_row, column=3, padx=10, pady=2)
                    dns_entry.grid(row=new_row + 1, column=0, columnspan=2, padx=10, pady=2)
                    lease_entry.grid(row=new_row + 1, column=2, columnspan=2, padx=10, pady=2)
                    remove_button.grid(row=new_row, column=4, padx=10, pady=2)
                    separator.grid(row=new_row + 2, column=0, columnspan=5, sticky="ew", pady=5)
                if len(pool_entries) <= 2:
                    pool_frame.configure(height=200)
                else:
                    pool_frame.configure(height=200 + (len(pool_entries) - 2) * 60)

        add_pool()
        add_pool_button = ctk.CTkButton(config_frame, text="Add Pool", command=add_pool)
        add_pool_button.grid(row=4, column=0, padx=5, pady=5)

        def apply_dhcp_server():
            server_error_label.configure(text="")
            commands = []
            pool_configs = []
            
            for name_entry, network_entry, mask_entry, gateway_entry, dns_entry, lease_entry, _, _ in pool_entries:
                name = name_entry.get().strip()
                network = network_entry.get().strip()
                mask = mask_entry.get().strip()
                gateway = gateway_entry.get().strip()
                dns = dns_entry.get().strip()
                lease = lease_entry.get().strip()

                if not (name or network or mask or gateway or dns or lease):
                    continue
                if not all([name, network, mask, gateway, dns, lease]):
                    server_error_label.configure(text="Input Error: All pool fields required if any provided.")
                    return
                if not name.replace("_", "").isalnum():
                    server_error_label.configure(text="Input Error: Pool name must be alphanumeric.")
                    return
                if not self.validate_ip(network):
                    server_error_label.configure(text="Input Error: Invalid network address.")
                    return
                if not self.validate_subnet_mask(mask):
                    server_error_label.configure(text="Input Error: Invalid subnet mask.")
                    return
                if not self.validate_ip(gateway):
                    server_error_label.configure(text="Input Error: Invalid gateway IP.")
                    return
                dns_ips = dns.split()
                if not all(self.validate_ip(d) for d in dns_ips) or len(dns_ips) > 2:
                    server_error_label.configure(text="Input Error: DNS servers must be 1–2 valid IPs.")
                    return
                lease_parts = lease.split()
                if not (1 <= len(lease_parts) <= 3 and all(p.isdigit() and 0 <= int(p) <= 255 for p in lease_parts)):
                    server_error_label.configure(text="Input Error: Lease must be 1–3 numbers (0–255).")
                    return

                pool_configs.append({
                    "name": name,
                    "network": network,
                    "mask": mask,
                    "gateway": gateway,
                    "dns": dns,
                    "lease": lease
                })

            if not pool_configs:
                server_error_label.configure(text="Input Error: At least one valid pool required.")
                return

            for pool in pool_configs:
                commands.extend([
                    "ip dhcp enable",
                    f"ip dhcp pool {pool['name']}",
                    f"network {pool['network']} {pool['mask']}",
                    f"default-router {pool['gateway']}",
                    f"dns-server {pool['dns']}",
                    f"lease {pool['lease']}"
                ])

            for cmd in commands:
                self.log_output(f"Sending command: {cmd}", output_text)
                ssh.send_config_set([cmd], exit_config_mode=False)
            self.log_output(f"Success: DHCP Server configured on {device}.", output_text)
            server_error_label.configure(text="")

        apply_dhcp_button = ctk.CTkButton(config_frame, text="Apply DHCP Server", command=apply_dhcp_server)
        apply_dhcp_button.grid(row=5, column=0, padx=5, pady=5)

        # Excluded IPs Section
        ctk.CTkLabel(config_frame, text="Excluded IPs", font=("Arial", 14, "bold")).grid(row=6, column=0, columnspan=12, padx=5, pady=5, sticky="w")
        exclude_error_label = tk.Label(config_frame, text="", bg="#212121", fg="red")
        exclude_error_label.grid(row=7, column=0, columnspan=12, pady=5)
        exclude_frame = ctk.CTkScrollableFrame(config_frame, height=80)
        exclude_frame.grid(row=8, column=0, columnspan=12, pady=5, sticky="ew")
        exclude_entries = []

        ctk.CTkLabel(exclude_frame, text="Excluded IP Range").grid(row=0, column=0, padx=10, pady=2)

        def add_exclude():
            row = len(exclude_entries) + 1
            exclude_entry = ctk.CTkEntry(exclude_frame, width=360, placeholder_text="e.g., 192.168.1.100 192.168.1.150")
            exclude_entry.grid(row=row, column=0, padx=10, pady=2)
            remove_button = ctk.CTkButton(exclude_frame, text="Remove", command=lambda: remove_exclude(row))
            remove_button.grid(row=row, column=1, padx=10, pady=2)
            exclude_entries.append((exclude_entry, remove_button))

        def remove_exclude(row):
            if exclude_entries:
                for entry in exclude_entries:
                    if entry[0].grid_info()['row'] == row:
                        for widget in entry:
                            widget.destroy()
                        exclude_entries.remove(entry)
                        break
                for i, widgets in enumerate(exclude_entries, 1):
                    for j, widget in enumerate(widgets):
                        widget.grid(row=i, column=j)

        add_exclude()
        add_exclude_button = ctk.CTkButton(config_frame, text="Add Excluded IP", command=add_exclude)
        add_exclude_button.grid(row=9, column=0, padx=5, pady=5)

        def apply_excluded_ips():
            exclude_error_label.configure(text="")
            commands = []
            exclude_configs = []

            for exclude_entry, _ in exclude_entries:
                exclude = exclude_entry.get().strip()
                if not exclude:
                    continue
                exclude_ips = exclude.split()
                if len(exclude_ips) != 2 or not all(self.validate_ip(e) for e in exclude_ips):
                    exclude_error_label.configure(text="Input Error: Excluded IPs must be two valid IPs.")
                    return
                start_ip, end_ip = exclude_ips
                start_int = sum(int(o) << (24 - 8 * i) for i, o in enumerate(start_ip.split('.')))
                end_int = sum(int(o) << (24 - 8 * i) for i, o in enumerate(end_ip.split('.')))
                if start_int > end_int:
                    exclude_error_label.configure(text="Input Error: Excluded start IP must be less than end IP.")
                    return

                exclude_configs.append(exclude)

            if not exclude_configs:
                exclude_error_label.configure(text="Input Error: At least one valid excluded IP range required.")
                return

            for exclude in exclude_configs:
                commands.append(f"ip dhcp excluded-address {exclude}")

            for cmd in commands:
                self.log_output(f"Sending command: {cmd}", output_text)
                ssh.send_config_set([cmd], exit_config_mode=False)
            self.log_output(f"Success: Excluded IPs configured on {device}.", output_text)
            exclude_error_label.configure(text="")

        apply_exclude_button = ctk.CTkButton(config_frame, text="Apply Excluded IPs", command=apply_excluded_ips)
        apply_exclude_button.grid(row=10, column=0, padx=5, pady=5)

        # DHCP Relay Agent Section
        ctk.CTkLabel(config_frame, text="DHCP Relay Interfaces", font=("Arial", 14, "bold")).grid(row=11, column=0, columnspan=12, padx=5, pady=5, sticky="w")
        relay_error_label = tk.Label(config_frame, text="", bg="#212121", fg="red")
        relay_error_label.grid(row=12, column=0, columnspan=12, pady=5)
        relay_frame = ctk.CTkScrollableFrame(config_frame, height=80)
        relay_frame.grid(row=13, column=0, columnspan=12, pady=5, sticky="ew")
        relay_entries = []

        ctk.CTkLabel(relay_frame, text="Interface").grid(row=0, column=0, padx=10, pady=2)
        ctk.CTkLabel(relay_frame, text="DHCP Server IP").grid(row=0, column=1, padx=10, pady=2)

        def add_relay():
            row = len(relay_entries) + 1
            interface_entry = ctk.CTkEntry(relay_frame, width=180, placeholder_text="e.g., f0/0 or f0/0.10")
            interface_entry.grid(row=row, column=0, padx=10, pady=2)
            server_ip_entry = ctk.CTkEntry(relay_frame, width=180, placeholder_text="e.g., 192.168.1.100")
            server_ip_entry.grid(row=row, column=1, padx=10, pady=2)
            remove_button = ctk.CTkButton(relay_frame, text="Remove", command=lambda: remove_relay(row))
            remove_button.grid(row=row, column=2, padx=10, pady=2)
            relay_entries.append((interface_entry, server_ip_entry, remove_button))

        def remove_relay(row):
            if relay_entries:
                for entry in relay_entries:
                    if entry[0].grid_info()['row'] == row:
                        for widget in entry:
                            widget.destroy()
                        relay_entries.remove(entry)
                        break
                for i, widgets in enumerate(relay_entries, 1):
                    for j, widget in enumerate(widgets):
                        widget.grid(row=i, column=j)

        add_relay()
        add_relay_button = ctk.CTkButton(config_frame, text="Add Relay", command=add_relay)
        add_relay_button.grid(row=14, column=0, padx=5, pady=5)

        def apply_dhcp_relay():
            relay_error_label.configure(text="")
            commands = []
            relay_configs = []

            for interface_entry, server_ip_entry, _ in relay_entries:
                interface = interface_entry.get().strip()
                server_ip = server_ip_entry.get().strip()

                if not (interface or server_ip):
                    continue
                if not all([interface, server_ip]):
                    relay_error_label.configure(text="Input Error: Both relay interface and server IP required.")
                    return
                # Validate interface (including sub-interfaces like f0/0.10)
                if not re.match(r'^[a-zA-Z0-9]+(/[0-9]+){1,2}(\.[0-9]+)?$', interface):
                    relay_error_label.configure(text="Input Error: Invalid interface format (e.g., f0/0 or f0/0.10).")
                    return
                if not self.validate_ip(server_ip):
                    relay_error_label.configure(text="Input Error: Invalid DHCP server IP.")
                    return

                relay_configs.append({
                    "interface": interface,
                    "server_ip": server_ip
                })

            if not relay_configs:
                relay_error_label.configure(text="Input Error: At least one valid relay configuration required.")
                return

            for relay in relay_configs:
                commands.extend([
                    f"interface {relay['interface']}",
                    f"ip helper-address {relay['server_ip']}"
                ])

            for cmd in commands:
                self.log_output(f"Sending command: {cmd}", output_text)
                ssh.send_config_set([cmd], exit_config_mode=False)
            self.log_output(f"Success: DHCP Relay configured on {device}.", output_text)
            relay_error_label.configure(text="")

        apply_relay_button = ctk.CTkButton(config_frame, text="Apply DHCP Relay", command=apply_dhcp_relay)
        apply_relay_button.grid(row=15, column=0, padx=5, pady=5)

        # Clear and Back Buttons
        clear_button = ctk.CTkButton(config_frame, text="Clear", command=lambda: self.clear_textbox(output_text))
        clear_button.grid(row=23, column=0, padx=5, pady=5)
        back_button = ctk.CTkButton(config_frame, text="Back to Main", command=self.back_to_main)
        back_button.grid(row=23, column=1, padx=5, pady=5)

        # Show Commands Section
        show_frame = ctk.CTkFrame(config_frame)
        show_frame.grid(row=24, column=0, columnspan=12, pady=10, sticky="ew")
        show_commands = [
            "show running-config",
            "show ip interface brief",
            "show ip dhcp binding",
            "show ip dhcp pool",
            "show ip interface",
            "show running-config | include ip dhcp excluded-address",
            "show running-config | include ip helper-address",
            "show ip dhcp conflict"
        ]
        command_var = ctk.StringVar(value="")
        command_label = ctk.CTkLabel(show_frame, text="Select Show Command:")
        command_label.grid(row=0, column=0, padx=5)
        command_menu = ctk.CTkOptionMenu(show_frame, variable=command_var, values=show_commands)
        command_menu.grid(row=0, column=1, padx=5)
        def send_command():
            selected_command = command_var.get()
            if selected_command:
                output = ssh.send_config_set(['do ' + selected_command], exit_config_mode=False)
                self.log_output(f"Output for show command on {device}:\n{output}", output_text)
        send_command_button = ctk.CTkButton(show_frame, text="Send Command", command=send_command)
        send_command_button.grid(row=0, column=2, padx=5, pady=10)

        # Output Textbox
        output_text = scrolledtext.ScrolledText(config_frame, width=100, height=15, bg="black", fg="white")
        output_text.grid(row=25, column=0, columnspan=12, pady=10)

    def configure_nat_services(self, ssh, device, output_text, tab):
        """Configures Network Address Translation (NAT) on a router."""
        # Clear the existing tab's contents
        for widget in tab.winfo_children():
            widget.destroy()

        config_frame = ctk.CTkFrame(tab)
        config_frame.pack(pady=10, fill="both", expand=True)

        # Access List Section (for IPs allowed to be translated)
        ctk.CTkLabel(config_frame, text="Access List for NAT Translation", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=12, padx=5, pady=5, sticky="w")
        acl_error_label = tk.Label(config_frame, text="", bg="#212121", fg="red")
        acl_error_label.grid(row=1, column=0, columnspan=12, pady=5)
        acl_frame = ctk.CTkScrollableFrame(config_frame, height=80)
        acl_frame.grid(row=2, column=0, columnspan=12, pady=5, sticky="ew")
        acl_entries = []

        # Column labels for Access List (simplified for NAT)
        ctk.CTkLabel(acl_frame, text="ACL Number").grid(row=0, column=0, padx=10, pady=2)
        ctk.CTkLabel(acl_frame, text="Action").grid(row=0, column=1, padx=10, pady=2)
        ctk.CTkLabel(acl_frame, text="Source IP").grid(row=0, column=2, padx=10, pady=2)
        ctk.CTkLabel(acl_frame, text="Src Wildcard").grid(row=0, column=3, padx=10, pady=2)

        def create_access_list():
            row = len(acl_entries) + 1
            acl_num_entry = ctk.CTkEntry(acl_frame, width=100, placeholder_text="e.g., 1")
            acl_num_entry.grid(row=row, column=0, padx=10, pady=2)
            action_var = ctk.StringVar(value="permit")
            action_menu = ctk.CTkOptionMenu(acl_frame, variable=action_var, values=["permit", "deny"])
            action_menu.grid(row=row, column=1, padx=10, pady=2)
            src_ip_entry = ctk.CTkEntry(acl_frame, width=180, placeholder_text="e.g., 192.168.1.0")
            src_ip_entry.grid(row=row, column=2, padx=10, pady=2)
            src_wildcard_entry = ctk.CTkEntry(acl_frame, width=180, placeholder_text="e.g., 0.0.0.255")
            src_wildcard_entry.grid(row=row, column=3, padx=10, pady=2)
            acl_entries.append((acl_num_entry, action_var, src_ip_entry, src_wildcard_entry))

        create_access_list()
        add_acl_button = ctk.CTkButton(config_frame, text="Add Access List Rule", command=create_access_list)
        add_acl_button.grid(row=3, column=0, padx=5, pady=5)

        def apply_access_list():
            acl_error_label.configure(text="")
            commands = []
            acl_configs = []

            for acl_num_entry, action_var, src_ip_entry, src_wildcard_entry in acl_entries:
                acl_num = acl_num_entry.get().strip()
                action = action_var.get()
                src_ip = src_ip_entry.get().strip()
                src_wildcard = src_wildcard_entry.get().strip()

                if not acl_num or not action or not src_ip or not src_wildcard:
                    acl_error_label.configure(text="Input Error: All fields are required.")
                    return
                if not acl_num.isdigit() or (int(acl_num) < 1 or int(acl_num) > 199):
                    acl_error_label.configure(text="Input Error: ACL number must be 1-199.")
                    return
                if not self.validate_ip(src_ip) or not self.validate_wildcard(src_wildcard):
                    acl_error_label.configure(text="Input Error: Invalid source IP or wildcard.")
                    return

                cmd = f"access-list {acl_num} {action} {src_ip} {src_wildcard}"
                acl_configs.append(cmd)

            if not acl_configs:
                acl_error_label.configure(text="Input Error: At least one valid ACL rule required.")
                return

            for cmd in acl_configs:
                commands.append(cmd)

            for cmd in commands:
                self.log_output(f"Sending command: {cmd}", output_text_widget)
                ssh.send_config_set([cmd], exit_config_mode=False)
            self.log_output(f"Success: Access List for NAT configured on {device}.", output_text_widget)
            acl_error_label.configure(text="")

        apply_acl_button = ctk.CTkButton(config_frame, text="Apply Access List", command=apply_access_list)
        apply_acl_button.grid(row=4, column=0, padx=5, pady=5)

        # Public IP Pool Section
        ctk.CTkLabel(config_frame, text="Public IP Pool Configuration", font=("Arial", 14, "bold")).grid(row=5, column=0, columnspan=12, padx=5, pady=5, sticky="w")
        pool_error_label = tk.Label(config_frame, text="", bg="#212121", fg="red")
        pool_error_label.grid(row=6, column=0, columnspan=12, pady=5)
        pool_frame = ctk.CTkScrollableFrame(config_frame, height=80)
        pool_frame.grid(row=7, column=0, columnspan=12, pady=5, sticky="ew")
        pool_entries = []

        # Column labels for Public IP Pool
        ctk.CTkLabel(pool_frame, text="Pool Name").grid(row=0, column=0, padx=10, pady=2)
        ctk.CTkLabel(pool_frame, text="Start IP").grid(row=0, column=1, padx=10, pady=2)
        ctk.CTkLabel(pool_frame, text="End IP").grid(row=0, column=2, padx=10, pady=2)
        ctk.CTkLabel(pool_frame, text="Netmask").grid(row=0, column=3, padx=10, pady=2)

        def create_pool():
            row = len(pool_entries) + 1
            pool_name_entry = ctk.CTkEntry(pool_frame, width=180, placeholder_text="e.g., NAT_POOL")
            pool_name_entry.grid(row=row, column=0, padx=10, pady=2)
            start_ip_entry = ctk.CTkEntry(pool_frame, width=180, placeholder_text="e.g., 200.1.1.1")
            start_ip_entry.grid(row=row, column=1, padx=10, pady=2)
            end_ip_entry = ctk.CTkEntry(pool_frame, width=180, placeholder_text="e.g., 200.1.1.6")
            end_ip_entry.grid(row=row, column=2, padx=10, pady=2)
            netmask_entry = ctk.CTkEntry(pool_frame, width=180, placeholder_text="e.g., 255.255.255.248")
            netmask_entry.grid(row=row, column=3, padx=10, pady=2)
            pool_entries.append((pool_name_entry, start_ip_entry, end_ip_entry, netmask_entry))

        create_pool()
        add_pool_button = ctk.CTkButton(config_frame, text="Add Public IP Pool", command=create_pool)
        add_pool_button.grid(row=8, column=0, padx=5, pady=5)

        def apply_pool():
            pool_error_label.configure(text="")
            commands = []
            pool_configs = []

            for pool_name_entry, start_ip_entry, end_ip_entry, netmask_entry in pool_entries:
                pool_name = pool_name_entry.get().strip()
                start_ip = start_ip_entry.get().strip()
                end_ip = end_ip_entry.get().strip()
                netmask = netmask_entry.get().strip()

                if not pool_name or not start_ip or not end_ip or not netmask:
                    pool_error_label.configure(text="Input Error: All fields are required.")
                    return
                if not pool_name.isalnum():
                    pool_error_label.configure(text="Input Error: Pool name must be alphanumeric.")
                    return
                if not self.validate_ip(start_ip) or not self.validate_ip(end_ip):
                    pool_error_label.configure(text="Input Error: Invalid pool IP addresses.")
                    return
                if not self.validate_subnet_mask(netmask):
                    pool_error_label.configure(text="Input Error: Invalid netmask.")
                    return

                cmd = f"ip nat pool {pool_name} {start_ip} {end_ip} netmask {netmask}"
                pool_configs.append(cmd)

            if not pool_configs:
                pool_error_label.configure(text="Input Error: At least one valid pool required.")
                return

            for cmd in pool_configs:
                commands.append(cmd)

            for cmd in commands:
                self.log_output(f"Sending command: {cmd}", output_text_widget)
                ssh.send_config_set([cmd], exit_config_mode=False)
            self.log_output(f"Success: Public IP Pool configured on {device}.", output_text_widget)
            pool_error_label.configure(text="")

        apply_pool_button = ctk.CTkButton(config_frame, text="Apply Public IP Pool", command=apply_pool)
        apply_pool_button.grid(row=9, column=0, padx=5, pady=5)

        # NAT Configuration Section
        ctk.CTkLabel(config_frame, text="NAT Configuration", font=("Arial", 14, "bold")).grid(row=10, column=0, columnspan=12, padx=5, pady=5, sticky="w")
        nat_error_label = tk.Label(config_frame, text="", bg="#212121", fg="red")
        nat_error_label.grid(row=11, column=0, columnspan=12, pady=5)
        nat_frame = ctk.CTkScrollableFrame(config_frame, height=120)
        nat_frame.grid(row=12, column=0, columnspan=12, pady=5, sticky="ew")

        # NAT Interface Selection (always visible)
        ctk.CTkLabel(nat_frame, text="Inside Interface").grid(row=0, column=0, padx=10, pady=2)
        inside_intf_entry = ctk.CTkEntry(nat_frame, width=180, placeholder_text="e.g., f0/0")
        inside_intf_entry.grid(row=0, column=1, padx=10, pady=2)
        ctk.CTkLabel(nat_frame, text="Outside Interface").grid(row=0, column=2, padx=10, pady=2)
        outside_intf_entry = ctk.CTkEntry(nat_frame, width=180, placeholder_text="e.g., s0/0")
        outside_intf_entry.grid(row=0, column=3, padx=10, pady=2)

        # NAT Type Selection
        nat_type_var = ctk.StringVar(value="Static")
        ctk.CTkLabel(nat_frame, text="NAT Type").grid(row=1, column=0, padx=10, pady=2)
        nat_type_menu = ctk.CTkOptionMenu(nat_frame, variable=nat_type_var, values=["Static", "Dynamic", "PAT"])
        nat_type_menu.grid(row=1, column=1, columnspan=2, padx=10, pady=2)

        # Static NAT Mapping
        static_inside_label = ctk.CTkLabel(nat_frame, text="Inside Local IP")
        static_inside_label.grid(row=2, column=0, padx=10, pady=2)
        static_inside_ip_entry = ctk.CTkEntry(nat_frame, width=180, placeholder_text="e.g., 192.168.1.10")
        static_inside_ip_entry.grid(row=2, column=1, padx=10, pady=2)
        static_global_label = ctk.CTkLabel(nat_frame, text="Inside Global IP")
        static_global_label.grid(row=2, column=2, padx=10, pady=2)
        static_global_ip_entry = ctk.CTkEntry(nat_frame, width=180, placeholder_text="e.g., 200.1.1.10")
        static_global_ip_entry.grid(row=2, column=3, padx=10, pady=2)

        # Dynamic NAT Pool Selection
        dynamic_pool_label = ctk.CTkLabel(nat_frame, text="Pool Name")
        dynamic_pool_label.grid(row=3, column=0, padx=10, pady=2)
        dynamic_pool_entry = ctk.CTkEntry(nat_frame, width=180, placeholder_text="e.g., NAT_POOL")
        dynamic_pool_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=2)
        dynamic_acl_label = ctk.CTkLabel(nat_frame, text="ACL Number for Dynamic NAT")
        dynamic_acl_label.grid(row=4, column=0, padx=10, pady=2)
        dynamic_acl_entry = ctk.CTkEntry(nat_frame, width=180, placeholder_text="e.g., 1 (must match ACL)")
        dynamic_acl_entry.grid(row=4, column=1, columnspan=2, padx=10, pady=2)

        # PAT Configuration
        pat_mode_var = ctk.StringVar(value="Interface")
        ctk.CTkLabel(nat_frame, text="PAT Mode").grid(row=3, column=0, padx=10, pady=2)
        pat_mode_menu = ctk.CTkOptionMenu(nat_frame, variable=pat_mode_var, values=["Interface", "Pool"])
        pat_mode_menu.grid(row=3, column=1, padx=10, pady=2)
        pat_acl_label = ctk.CTkLabel(nat_frame, text="ACL Number for PAT")
        pat_acl_label.grid(row=4, column=0, padx=10, pady=2)
        pat_acl_entry = ctk.CTkEntry(nat_frame, width=180, placeholder_text="e.g., 1 (must match ACL)")
        pat_acl_entry.grid(row=4, column=1, padx=10, pady=2)
        pat_interface_label = ctk.CTkLabel(nat_frame, text="Outside Interface")
        pat_interface_label.grid(row=4, column=2, padx=10, pady=2)
        pat_interface_entry = ctk.CTkEntry(nat_frame, width=180, placeholder_text="e.g., s0/0")
        pat_interface_entry.grid(row=4, column=3, padx=10, pady=2)
        pat_pool_label = ctk.CTkLabel(nat_frame, text="Pool Name")
        pat_pool_label.grid(row=5, column=0, padx=10, pady=2)
        pat_pool_entry = ctk.CTkEntry(nat_frame, width=180, placeholder_text="e.g., NAT_POOL")
        pat_pool_entry.grid(row=5, column=1, columnspan=2, padx=10, pady=2)

        # Output Textbox (created within the function to ensure it persists)
        output_text_widget = scrolledtext.ScrolledText(config_frame, width=100, height=15, bg="black", fg="white")
        output_text_widget.grid(row=16, column=0, columnspan=12, pady=10)

        # Initially hide all NAT type-specific fields
        def update_nat_fields(*args):
            # Hide all fields
            static_inside_label.grid_remove()
            static_inside_ip_entry.grid_remove()
            static_global_label.grid_remove()
            static_global_ip_entry.grid_remove()
            dynamic_pool_label.grid_remove()
            dynamic_pool_entry.grid_remove()
            dynamic_acl_label.grid_remove()
            dynamic_acl_entry.grid_remove()
            pat_mode_menu.grid_remove()
            pat_acl_label.grid_remove()
            pat_acl_entry.grid_remove()
            pat_interface_label.grid_remove()
            pat_interface_entry.grid_remove()
            pat_pool_label.grid_remove()
            pat_pool_entry.grid_remove()

            # Show fields based on NAT type
            nat_type = nat_type_var.get()
            if nat_type == "Static":
                static_inside_label.grid()
                static_inside_ip_entry.grid()
                static_global_label.grid()
                static_global_ip_entry.grid()
            elif nat_type == "Dynamic":
                dynamic_pool_label.grid()
                dynamic_pool_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=2)
                dynamic_acl_label.grid()
                dynamic_acl_entry.grid(row=4, column=1, columnspan=2, padx=10, pady=2)
            elif nat_type == "PAT":
                pat_mode_menu.grid()
                pat_acl_label.grid()
                pat_acl_entry.grid()
                if pat_mode_var.get() == "Interface":
                    pat_interface_label.grid()
                    pat_interface_entry.grid()
                else:  # Pool
                    pat_pool_label.grid()
                    pat_pool_entry.grid(row=5, column=1, columnspan=2, padx=10, pady=2)

        # Bind the update function to NAT type and PAT mode changes
        nat_type_var.trace("w", update_nat_fields)
        pat_mode_var.trace("w", update_nat_fields)
        update_nat_fields()  # Initial call to set visibility

        def apply_nat():
            nat_error_label.configure(text="")
            commands = []
            nat_type = nat_type_var.get()
            inside_intf = inside_intf_entry.get().strip()
            outside_intf = outside_intf_entry.get().strip()

            # Interface validation
            if not inside_intf or not outside_intf:
                nat_error_label.configure(text="Input Error: Both inside and outside interfaces required.")
                return
            if not re.match(r'^[a-zA-Z0-9]+(/[0-9]+){1,2}(\.[0-9]+)?$', inside_intf) or \
            not re.match(r'^[a-zA-Z0-9]+(/[0-9]+){1,2}(\.[0-9]+)?$', outside_intf):
                nat_error_label.configure(text="Input Error: Invalid interface format (e.g., f0/0 or f0/0.10).")
                return

            # Interface configuration
            commands.extend([
                f"interface {inside_intf}",
                "ip nat inside",
                f"interface {outside_intf}",
                "ip nat outside"
            ])

            if nat_type == "Static":
                inside_ip = static_inside_ip_entry.get().strip()
                global_ip = static_global_ip_entry.get().strip()
                if not inside_ip or not global_ip:
                    nat_error_label.configure(text="Input Error: Inside and global IPs required for Static NAT.")
                    return
                if not self.validate_ip(inside_ip) or not self.validate_ip(global_ip):
                    nat_error_label.configure(text="Input Error: Invalid IP addresses for Static NAT.")
                    return
                commands.append(f"ip nat inside source static {inside_ip} {global_ip}")

            elif nat_type == "Dynamic":
                pool_name = dynamic_pool_entry.get().strip()
                acl_num = dynamic_acl_entry.get().strip()

                if not pool_name or not acl_num:
                    nat_error_label.configure(text="Input Error: Pool name and ACL number required for Dynamic NAT.")
                    return
                if not acl_num.isdigit() or (int(acl_num) < 1 or int(acl_num) > 199):
                    nat_error_label.configure(text="Input Error: ACL number must be 1-199.")
                    return

                commands.append(f"ip nat inside source list {acl_num} pool {pool_name}")

            elif nat_type == "PAT":
                acl_num = pat_acl_entry.get().strip()
                if not acl_num:
                    nat_error_label.configure(text="Input Error: ACL number required for PAT.")
                    return
                if not acl_num.isdigit() or (int(acl_num) < 1 or int(acl_num) > 199):
                    nat_error_label.configure(text="Input Error: ACL number must be 1-199.")
                    return
                if pat_mode_var.get() == "Interface":
                    pat_intf = pat_interface_entry.get().strip()
                    if not pat_intf:
                        nat_error_label.configure(text="Input Error: Interface required for PAT.")
                        return
                    if not re.match(r'^[a-zA-Z0-9]+(/[0-9]+){1,2}(\.[0-9]+)?$', pat_intf):
                        nat_error_label.configure(text="Input Error: Invalid interface format for PAT.")
                        return
                    if pat_intf != outside_intf:
                        nat_error_label.configure(text="Input Error: PAT interface must match outside interface.")
                        return
                    commands.append(f"ip nat inside source list {acl_num} interface {pat_intf} overload")
                else:  # Pool
                    pool_name = pat_pool_entry.get().strip()
                    if not pool_name:
                        nat_error_label.configure(text="Input Error: Pool name required for PAT.")
                        return
                    commands.append(f"ip nat inside source list {acl_num} pool {pool_name} overload")

            for cmd in commands:
                self.log_output(f"Sending command: {cmd}", output_text_widget)
                ssh.send_config_set([cmd], exit_config_mode=False)
            self.log_output(f"Success: NAT configured on {device}.", output_text_widget)
            nat_error_label.configure(text="")

        apply_nat_button = ctk.CTkButton(config_frame, text="Apply NAT", command=apply_nat)
        apply_nat_button.grid(row=13, column=0, padx=5, pady=5)

        # Clear and Back Buttons
        clear_button = ctk.CTkButton(config_frame, text="Clear", command=lambda: self.clear_textbox(output_text_widget))
        clear_button.grid(row=14, column=0, padx=5, pady=5)
        back_button = ctk.CTkButton(config_frame, text="Back to Main", command=self.back_to_main)
        back_button.grid(row=14, column=1, padx=5, pady=5)

        # Show Commands Section
        show_frame = ctk.CTkFrame(config_frame)
        show_frame.grid(row=15, column=0, columnspan=12, pady=10, sticky="ew")
        show_commands = [
            "show running-config | include ip nat",
            "show ip nat translations",
            "show ip nat statistics",
            "show access-lists"
        ]
        command_var = ctk.StringVar(value="")
        command_label = ctk.CTkLabel(show_frame, text="Select Show Command:")
        command_label.grid(row=0, column=0, padx=5)
        command_menu = ctk.CTkOptionMenu(show_frame, variable=command_var, values=show_commands)
        command_menu.grid(row=0, column=1, padx=5)
        def send_command():
            selected_command = command_var.get()
            if selected_command:
                output = ssh.send_config_set(['do ' + selected_command], exit_config_mode=False)
                self.log_output(f"Output for show command on {device}:\n{output}", output_text_widget)
        send_command_button = ctk.CTkButton(show_frame, text="Send Command", command=send_command)
        send_command_button.grid(row=0, column=2, padx=5, pady=10)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # or "light"
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = RouterConfigurator(root)
    root.mainloop()
