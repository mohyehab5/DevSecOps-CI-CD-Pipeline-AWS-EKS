from random import random
import random
import re
import tkinter as tk
from turtle import bgcolor  # Importing the tkinter library for GUI
from netmiko import ConnectHandler  # Importing ConnectHandler from netmiko for SSH connections
import logging  # Import logging for detailed output
from tkinter import simpledialog, ttk, Toplevel  # Importing specific dialogs and ComboBox from tkinter

# Configure logging
logging.basicConfig(filename='netmiko.log', level=logging.DEBUG)
logging.getLogger("netmiko").setLevel(logging.DEBUG)

# colors_List=["#00FFFF", "#32CD32", "#FF6347", "#FFD700", "#FF00FF"]
# colors_list = [
#     "#FFFFFF",  # White - High contrast
#     "#F0F0F0",  # Light Gray - Subtle contrast
#     "#FFD700",  # Gold - Warm accent
#     "#00FF00",  # Bright Green - Vibrant contrast
#     "#1E90FF",  # Dodger Blue - Cool accent
#     "#FF4500",  # Orange Red - Bold contrast
#     "#FF69B4",  # Hot Pink - Playful contrast
#     "#7FFF00",  # Chartreuse - Bright and lively
#     "#8A2BE2",  # Blue Violet - Rich and deep
#     "#FFA500",  # Orange - Warm and vibrant
# ]
# colors_list = [
#     "#1C1C1C",  # Very Dark Gray - Slightly lighter than the background
#     "#444444",  # Dark Gray - Subtle contrast
#     "#8B0000",  # Dark Red - Rich and deep
#     "#006400",  # Dark Green - Muted and natural
#     "#00008B",  # Dark Blue - Deep and calming
#     "#4B0082",  # Indigo - Dark and sophisticated
#     "#800080",  # Purple - Rich and elegant
#     "#8B4513",  # Saddle Brown - Earthy and warm
#     "#2F4F4F",  # Dark Slate Gray - Cool and muted
#     "#556B2F",  # Dark Olive Green - Natural and subdued
# ]
    
class RouterConfigurator:
    def __init__(self, master):

        self.master = master  # Set the master window
        master.title("Router Configuration")  # Set the title of the window
        
        # Set window to full screen
        master.attributes('-fullscreen', True)
        master.configure(bg="#2E2E2E")  # Set background color
        
        # Create a canvas for scrolling
        self.canvas = tk.Canvas(master, bg="#2E2E2E")
        self.scrollbar = tk.Scrollbar(master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#2E2E2E")

        # Configure the scrollable frame
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create UI components
        self.label = tk.Label(self.scrollable_frame, text="Router Configuration Tool", bg="#2E2E2E", fg="white", font=("Arial", 16))
        self.label.pack(pady=10)

        # Create and pack the label and entry for the number of routers
        self.router_num_label = tk.Label(self.scrollable_frame, text="Number of routers:", bg="#2E2E2E", fg="white")
        self.router_num_label.pack()
        self.router_num_entry = tk.Entry(self.scrollable_frame)  # Create an entry field for input
        self.router_num_entry.pack()

        # Create a button to proceed to the next input
        self.next_button = tk.Button(self.scrollable_frame, text="Next / Remove", command=self.show_router_inputs, bg="#4E4E4E", fg="white")
        self.next_button.pack(pady=10)

        # Create a frame for router inputs
        self.router_frame = tk.Frame(self.scrollable_frame, bg="#2E2E2E")
        self.router_frame.pack(pady=10)

        # Create a text box for output display
        self.output_text = tk.Text(self.scrollable_frame, height=30,width=150, bg="#1E1E1E", fg="white", font=("Arial", 12))
        self.output_text.pack(pady=10)

        # Initialize variables for router inputs
        self.router_inputs = {}
        self.current_router = 1

    def log_output(self, message):
        # Insert output message in the text box and auto-scroll
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

    def show_router_inputs(self):
        # Clear previous inputs
        for widget in self.router_frame.winfo_children():
            widget.destroy()
    
        # Get number of routers
        try:
            self.router_num = int(self.router_num_entry.get())
            if self.router_num <=0 :
                self.log_output("Input Error: Please enter a valid number.")
            self.router_inputs = {i: {} for i in range(1, self.router_num + 1)}  # Initialize input storage
            self.current_router = 1  # Reset current router index
            self.prompt_router_info()
        except ValueError:
            self.log_output("Input Error: Please enter a valid number.")

    def prompt_router_info(self):
        if self.current_router > self.router_num :
            # if yes (configure multiple routers at the same time ==yes) --> break and connect to  other routers.
            self.log_output("All routers configured. Proceeding to configuration...")
            self.configure_routers()
            return

       # Create input fields for the current router
        tk.Label(self.router_frame, text=f"Router {self.current_router} IP:", bg="#2E2E2E", fg="white").pack()
        ip_entry = tk.Entry(self.router_frame)
        ip_entry.pack()
        self.router_inputs[self.current_router]['ip'] = ip_entry  # Store the Entry widget

        tk.Label(self.router_frame, text="SSH Username:", bg="#2E2E2E", fg="white").pack()
        user_entry = tk.Entry(self.router_frame)
        user_entry.pack()
        self.router_inputs[self.current_router]['username'] = user_entry  # Store the Entry widget

        tk.Label(self.router_frame, text="SSH Password:", bg="#2E2E2E", fg="white").pack()
        pass_entry = tk.Entry(self.router_frame, show='*')
        pass_entry.pack()
        self.router_inputs[self.current_router]['password'] = pass_entry  # Store the Entry widget

        tk.Label(self.router_frame, text="Service:", bg="#2E2E2E", fg="white").pack()
        self.protocol_var = tk.StringVar()
        protocol_combobox = ttk.Combobox(self.router_frame, textvariable=self.protocol_var, values=["EIGRP", "OSPF","default static routing","other configurations"])
        protocol_combobox.pack()
        self.router_inputs[self.current_router]['protocol'] = protocol_combobox  # Store the ComboBox

        # Proceed button for the current router
        proceed_button = tk.Button(self.router_frame, text="Next Router", command=self.next_router, bg="#4E4E4E", fg="white")
        proceed_button.pack(pady=10)

    def validate_ip(self, ip,num):  # Function to validate IP address
        # Regular expression for validating an IPv4 address
        ip_pattern = re.compile(
            r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'  # Matches the standard IPv4 format
        )
        if ip_pattern.match(ip):  # Check if the IP matches the pattern
            # Split the IP into its components and check each octet
            octets = ip.split('.')
            for octet in octets:
                if not 0 <= int(octet) <= 255:  # Each octet must be between 0 and 255
                    return False  # Invalid if any octet is out of range
            # Additional checks for specific invalid IPs
            if num ==1 :# if it is ip or network do the check 
                if ip == "0.0.0.0" or ip == "255.255.255.255":  # Check for invalid IPs
                    return False  # Return False for these specific cases
            return True  # Valid IP address
        return False  # Invalid if the pattern does not match

    # def is_valid_wildcard(self,wildcard):
    #     """
    #     Validate the wildcard mask format.
    #     A valid wildcard mask is a string in the format of 'X.X.X.X' where X is an integer between 0 and 255,
    #     and at least one byte must be 255 or 0.
    #     """
    #     # Check if the wildcard matches the pattern of four octets
    #     pattern = r'^(255|254|252|248|240|224|192|128|0)(\.(255|254|252|248|240|224|192|128|0)){3}$'
    #     return bool(re.match(pattern, wildcard))    
        
    def is_valid_interface(self, interface):
        """
        Validate the interface format.
        A valid interface format is 'fX/Y', 'gX/Y', 'sX/Y', 'eX/Y', or 'loopbackX', where X and Y are integers.
        """
        # Pattern to match valid interfaces like f0/0, g0/0, s0/0, e0/0, or loopback0
        pattern = r'^(f|g|s|e)\d+/\d+$|^loopback\d+$'
        return bool(re.match(pattern, interface))
    # def is_valid_network_address(self,network_address):
    #     """
    #     Validate the network address format.
    #     A valid network address is a string in the format of 'X.X.X.X' where X is an integer between 0 and 255.
    #     The last octet should be 0 for a valid network address.
    #     """
    #     # Check if the network address matches the pattern of four octets
    #     pattern = r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.0$'
    #     return bool(re.match(pattern, network_address))    

    def next_router(self):
        # Collect the inputs for the current router
        ip = self.router_inputs[self.current_router]['ip'].get()
        username = self.router_inputs[self.current_router]['username'].get()
        password = self.router_inputs[self.current_router]['password'].get()
        protocol = self.router_inputs[self.current_router]['protocol'].get().strip().lower()

        if not ip or not username or not password or not protocol :
            self.log_output("Input Error: Please fill in all fields.")
            return
      
         # Validate the IP address
        if not self.validate_ip(ip,1):  # Check if the IP is valid
            self.log_output("Input Error: Please enter a valid IP address.")  # Log an error if invalid
            return  # Exit the method if there is an error    

         # Validate routing protocol
        if protocol not in ["ospf", "eigrp","default static routing","other configurations"]:
            self.log_output("Input Error: Please enter 'ospf' , 'eigrp' or 'default static routing' as the routing protocol.")
            return
        # Store inputs
        self.router_inputs[self.current_router] = {
            'ip': ip,
            'username': username,
            'password': password,
            'protocol': protocol
        }

        # Move to the next router input
        self.current_router += 1
        self.prompt_router_info()

    def configure_routers(self):
        for router_num in range(1, self.router_num + 1):
            router_info = self.router_inputs[router_num]
            Router = {
                'device_type': 'cisco_ios',
                'ip': router_info['ip'],
                'username': router_info['username'],
                'password': router_info['password']
            }

            try:
                self.log_output(f"Connecting to {router_info['ip']}...")
                myssh = ConnectHandler(**Router)
                hostname = myssh.send_command('show run | i host')
                device = hostname.split()[1]
                routing_protocol = router_info['protocol']

                if routing_protocol == 'eigrp':
                    self.configure_eigrp(myssh, device)
                elif routing_protocol == 'ospf':
                    self.configure_ospf(myssh, device)
                elif routing_protocol == 'default static routing':
                    self.configure_DSR(myssh, device)
                elif routing_protocol == 'other configurations':
                    self.configure_other(myssh, device)    
                else:
                    self.log_output(f"Input Error: Invalid service for router {router_num}.")
            except Exception as e:
                self.log_output(f"Connection Error for router {router_num}: {str(e)}")
                logging.exception(f"Connection failed for router {router_num}")
                #............................................................................................................
    def configure_DSR(self, ssh, device):

            # config_frame = tk.Frame(self.scrollable_frame, bg= colors_list[random.randint(0, 4)])
            config_frame = tk.Frame(self.scrollable_frame, bg="#2E2E2E")
            config_frame.pack(pady=10, fill='both', expand=True)

            # Interface entry
            tk.Label(config_frame, text="Exit Interface:", bg="#2E2E2E", fg="white").grid(row=0, column=0)
            interface_entry = tk.Entry(config_frame)
            interface_entry.grid(row=0, column=1)
            
            def D_submit_configuration():
                exit_int = interface_entry.get()
                if not self.is_valid_interface(exit_int):
                    self.log_output("Input Error: interface must be like f0/0 , g0/1 or s1/1 , loopback0.")
                    return
                # Handle Hello Interval
                default_routing_command=f'ip route 0.0.0.0 0.0.0.0 {exit_int}'
                self.log_output(f"Sending command:{default_routing_command}")
                ssh.send_config_set([default_routing_command], exit_config_mode=False)  
            
                self.log_output(f'Success: Router "{device}" configured with Default Static Routing successfully.')
                
            # Submit button
            submit_button = tk.Button(config_frame, text="Submit Configuration", command=D_submit_configuration)
            submit_button.grid(row=1, columnspan=2, pady=10)
            # Add a horizontal line (separator)
            separator = tk.Frame(config_frame, height=2, bg="gray")
            separator.grid(row=2, columnspan=10, sticky="ew", pady=5)
                        
#...................................................................................................................
    def configure_other(self, ssh, device):

        # Reusable function to create OptionMenu, labels, and entries
        def create_option_menu( frame, label_text, hidden_label_texts, options, row, pw ,checkbox_at_indexes):
            var = tk.StringVar(value="no")
            label = tk.Label(frame, text=label_text, bg="#2E2E2E", fg="white")
            label.grid(row=row, column=0) #always appearing

            # Create a list to store the entry labels
            hidden_labels = [] 
            hidden_entries = []
            # Function to update visibility of labels and entries
            def update_visibility(*_):
                if var.get() == "yes":
                    for i in range (0,1+len(hidden_label_texts)): 
                        label = tk.Label(frame, text=f"{hidden_label_texts[i]}:", bg="#2E2E2E", fg= "white")  
                        label.grid(row=row, column=2*i+2)
                        hidden_labels.append(label)
                        #if entry is a checkbox 
                        if i in checkbox_at_indexes:
                            entry_var = tk.StringVar(value="no")
                            entry = tk.OptionMenu(frame, entry_var, "yes", "no")
                            entry.grid(row=row, column=2*i+3)
                            hidden_entries.append(entry)
                            continue
                        #if entry is a text entry
                        elif pw==0 :
                            entry = tk.Entry(frame)
                            entry.grid(row=row, column=2*i+3)
                            hidden_entries.append(entry)
                        
                         #if entry is a password entry
                        else:
                            entry = tk.Entry(frame, show='*')
                            entry.grid(row=row, column=2*i+3)
                            hidden_entries.append(entry)
                else:
                    for label in hidden_labels:
                        label.grid_remove()
                    for entry in hidden_entries:
                        entry.grid_remove()
                                    
            # Create OptionMenu
            option_menu = tk.OptionMenu(frame, var, *options, command=update_visibility)
            option_menu.grid(row=row, column=1)
            
            # Initially hide the entry and its label
            for label in hidden_labels:
                label.grid_remove()
            for entry in hidden_entries:  
                entry.grid_remove()
            
            return var, hidden_entries
#.................................................
        # Main code
        # config_frame = tk.Frame(self.scrollable_frame, bg=colors_list[random.randint(0, 4)])
        config_frame = tk.Frame(self.scrollable_frame, bg="#2E2E2E")
        config_frame.pack(pady=10, fill='both', expand=True)

        # Create hostname section
        HN_var, HN_entry = create_option_menu(config_frame, "Change hostname ?:",["New HostName"] ,["no", "yes"], row=0,pw=0,checkbox_at_indexes=[])
        #var is no or yes but entry is the new hostname that will be entered by the user
        # Create enable password section
        EP_var, EP_entry = create_option_menu(config_frame, "Enable password ?:",["New Enable Password"] ,["no", "yes"], row=1,pw=1,checkbox_at_indexes=[])
        
        # Create username section
        UN_var, UN_entry = create_option_menu(config_frame, "Create username ?:",["Username","Password","privilege"] ,["no", "yes"], row=2,pw=1,checkbox_at_indexes=[])

        banner_var, banner_entry = create_option_menu(config_frame, "Create banner ?:",["Banner Message"] ,["no", "yes"], row=3,pw=0,checkbox_at_indexes=[])
        IP_var, IP_entry = create_option_menu(config_frame, "Change IP Address ?:",["interface or loopback:","New IP Address","Subnet Mask","shutdown the interface?"] ,["no", "yes"], row=4,pw=0,checkbox_at_indexes=[3])
        # Create a function to submit the configuration
        def other_submit_configuration():
            # Handle errors
            if HN_var.get() == "yes" and not HN_entry[0].get():
                self.log_output("Input Error: Please enter a new hostname.")
                return
            if EP_var.get() == "yes" and EP_entry[0].get() == "":
                self.log_output("Input Error: Please enter a new enable password.")
                return
            if UN_var.get() == "yes" and (UN_entry[0].get() == "" or UN_entry[1].get() == "" or UN_entry[2].get() == ""):
                self.log_output("Input Error: Please enter a username and password.")
                return
            if UN_var.get() == "yes" and (not UN_entry[2].get().isdigit() or int(UN_entry[2].get()) < 0 or int(UN_entry[2].get()) > 15):
                self.log_output("Input Error: Privilege level must be a number between 0 and 15.")
                return 
            if banner_var.get() == "yes" and not banner_entry[0].get():
                self.log_output("Input Error: Please enter a banner message.")
                return
            if IP_var.get() == "yes" and not self.validate_ip(IP_entry[1].get(),0):
                self.log_output("Input Error: Please enter a valid IP address.")
                return
            if IP_var.get() == "yes" and not self.is_valid_interface(IP_entry[0].get()):
                self.log_output("Input Error: interface must be like f0/0 , g0/1 , s1/1 or loopback0.")
                return
            if IP_var.get() == "yes" and not self.validate_ip(IP_entry[2].get(),0):
                self.log_output("Input Error: Please enter a valid subnet mask.")
                return

            # Handle Hostname
            if HN_var.get() == "yes":
                new_hostname = HN_entry[0].get()
                hostname_command = f'hostname {new_hostname}'
                self.log_output(f"Sending command: {hostname_command}")
                ssh.send_config_set([hostname_command], exit_config_mode=False)
            
            # Handle Enable Password
            if EP_var.get() == "yes":
                new_enable_password = EP_entry[0].get()
                enable_password_command = f'enable secret {new_enable_password}'
                self.log_output(f"Sending command: {enable_password_command}")
                ssh.send_config_set([enable_password_command], exit_config_mode=False)
            
            # Handle Username
            if UN_var.get() == "yes":
                new_username = UN_entry[0].get()
                new_password = UN_entry[1].get()
                new_privilege = UN_entry[2].get()
                username_command = f'username {new_username} privilege {new_privilege} secret {new_password}'
                self.log_output(f"Sending command: {username_command}")
                ssh.send_config_set([username_command], exit_config_mode=False)
            
            # Handle Banner
            if banner_var.get() == "yes":
                new_banner = banner_entry[0].get()
                banner_command = f'banner motd %{new_banner}%'
                self.log_output(f"Sending command: {banner_command}")
                ssh.send_config_set([banner_command], exit_config_mode=False)

            if IP_var.get() == "yes":
                interface = IP_entry[0].get()
                new_ip = IP_entry[1].get()
                SM=IP_entry[2].get()
                open_int_var = IP_entry[3].get()
                interface_command = f'interface {interface}'
                ip_command = f'ip address {new_ip} {SM}'
                self.log_output(f"Sending command: {interface_command}")
                self.log_output(f"Sending command: {ip_command}")
                ssh.send_config_set([interface_command, ip_command], exit_config_mode=False)
                if open_int_var =="yes" :
                    open_int_command = f'no shutdown'
                    self.log_output(f"Sending command: {open_int_command}")
                    ssh.send_config_set([open_int_command], exit_config_mode=False)
                else :
                    close_int_command = f'shutdown'
                    self.log_output(f"Sending command: {close_int_command}")
                    ssh.send_config_set([close_int_command], exit_config_mode=False)

            self.log_output(f"Success: Router{device}configured with other configurations successfully.")

        # Submit button
        submit_button = tk.Button(config_frame, text="Submit Configuration", command=other_submit_configuration)
        submit_button.grid(row=9, columnspan=2, pady=10)

#...................................................        
        # def other_submit_configuration():
        #     exit_int = interface_entry.get()
        #     if not self.is_valid_interface(exit_int):
        #         self.log_output("Input Error: interface must be like f0/0 , g0/1 or s1/1.")
        #         return
        #     # Handle Hello Interval
              # default_routing_command=f'ip route 0.0.0.0 0.0.0.0 {exit_int}'
        #     self.log_output(f"Sending command:{default_routing_command}")
        #     ssh.send_config_set([default_routing_command], exit_config_mode=False)  
        
        #     self.log_output(f'Success: Router "{device}" configured with Default Static Routing successfully.')
            
        # # Submit button
        # submit_button = tk.Button(config_frame, text="Submit Configuration", command=other_submit_configuration)
        # submit_button.grid(row=9, columnspan=2, pady=10)
        # # Add a horizontal line (separator)
        # separator = tk.Frame(config_frame, height=2, bg="gray")
        # separator.grid(row=10, columnspan=10, sticky="ew", pady=5)
        
# .............................................................................................................................
    def configure_eigrp(self, ssh, device):
        # Create a frame for eigrp configuration inputs
        # config_frame = tk.Frame(self.scrollable_frame, bg=colors_list[random.randint(0, 4)])
        config_frame = tk.Frame(self.scrollable_frame, bg="#2E2E2E")
        config_frame.pack(pady=10, fill='both', expand=True)

        # Prompt for OSPF Process ID
        tk.Label(config_frame, text="EIGRP AS Number:", bg="#4E4E4E", fg="white").grid(row=0, column=0)
        AS_entry = tk.Entry(config_frame)
        AS_entry.grid(row=0, column=1)

        Auto_sum_var = tk.StringVar(value="no")
        tk.Label(config_frame, text="Enable Auto-summarization ?:", bg="#4E4E4E", fg="white").grid(row=1, column=0)
        tk.OptionMenu(config_frame, Auto_sum_var, "yes", "no").grid(row= 1, column=1)

        tk.Label(config_frame, text="Variance:", bg="#4E4E4E", fg="white").grid(row=2, column=0)
        variance_var = tk.StringVar(value="default")
        variance_menu = ttk.Combobox(config_frame, textvariable=variance_var, values=["default"])
        variance_menu.grid(row=2, column=1)
            
        # Frame for other entries
        network_frame = tk.Frame(config_frame, bg="#4E4E4E")
        network_frame.grid(row=4, columnspan=5, pady=10, sticky="ew")

        # Initialize list to hold network configurations
        network_entries = []
        # Function to add network entries
        def add_network_entry():
            row = len(network_entries) * 5  # Current row index for new entry, ensuring proper spacing

            # Network entry
            tk.Label(network_frame, text=f"Network {row // 5 + 1}:", bg="#2E2E2E", fg="white").grid(row=row, column=0)
            network_entry = tk.Entry(network_frame)
            network_entry.grid(row=row, column=1)

            # Wildcard mask entry
            tk.Label(network_frame, text="Wildcard Mask:", bg="#2E2E2E", fg="white").grid(row=row, column=2)
            wildcard_entry = tk.Entry(network_frame)
            wildcard_entry.grid(row=row, column=3)

            # Interface entry
            tk.Label(network_frame, text="Interface:", bg="#2E2E2E", fg="white").grid(row=row, column=4)
            interface_entry = tk.Entry(network_frame)
            interface_entry.grid(row=row, column=5)

            # Authentication 
            tk.Label(network_frame, text="Authentication(By MD5) ?:", bg="#2E2E2E", fg="white").grid(row=row+1, column=0)
            auth_var = tk.StringVar(value="no")
            auth_var_menu = tk.OptionMenu(network_frame, auth_var, "no", "yes", command=lambda _: update_auth_entry(row))
            auth_var_menu.grid(row=row+1, column=1)

            # chain name entry
            chain_name_label = tk.Label(network_frame, text="Chain Name :", bg="#2E2E2E", fg="white") 
            chain_name_entry = tk.Entry(network_frame)
        
            # key number entry
            key_no_label = tk.Label(network_frame, text="Key Number:", bg="#2E2E2E", fg="white")
            key_no_entry = tk.Entry(network_frame)
            
            # Authentication key entry and label (initially hidden)
            auth_key_label = tk.Label(network_frame, text="Authentication Key:", bg="#2E2E2E", fg="white")
            auth_key_entry = tk.Entry(network_frame, show='*')
            
            chain_name_label.grid(row=row+1, column=2)
            chain_name_entry.grid(row=row+1, column=3)
            chain_name_label.grid_remove()  # Hide the label initially
            chain_name_entry.grid_remove()   # Hide the entry initially

            key_no_label.grid(row=row+1, column=4)
            key_no_entry.grid(row=row+1, column=5)
            key_no_label.grid_remove()  # Hide the label initially
            key_no_entry.grid_remove()   # Hide the entry initially

            # Initially hide the label and entry
            auth_key_label.grid(row=row+1, column=6)
            auth_key_entry.grid(row=row+1, column=7)
            auth_key_label.grid_remove()  # Hide the label initially
            auth_key_entry.grid_remove()   # Hide the entry initially

            # Function to update the visibility of the authentication key entry and label
            def update_auth_entry(row):
                if auth_var.get() == "yes":
                    chain_name_label.grid(row=row+1, column=2)    # Show the label 
                    chain_name_entry.grid(row=row+1, column=3)    # Show the entry  
                    
                    key_no_label.grid(row=row+1, column=4)
                    key_no_entry.grid(row=row+1, column=5)
                    
                    auth_key_label.grid(row=row+1, column=6)
                    auth_key_entry.grid(row=row+1, column=7)   
                else:
                    chain_name_label.grid_remove()  
                    chain_name_entry.grid_remove()   
                    
                    key_no_label.grid_remove()  
                    key_no_entry.grid_remove()   

                    auth_key_label.grid_remove() 
                    auth_key_entry.grid_remove()

            #interface B.W
            tk.Label(network_frame, text="Interface B.W (%):", bg="#2E2E2E", fg="white").grid(row=row + 2, column=0)
            e_BW_var = tk.StringVar(value="default")
            e_BW_menu = ttk.Combobox(network_frame, textvariable=e_BW_var, values=["default", "10", "20", "100", "200"])
            e_BW_menu.grid(row=row + 2, column=1)

            # Hello Interval entry
            tk.Label(network_frame, text="Hello Interval (Seconds):", bg="#2E2E2E", fg="white").grid(row=row + 3, column=0)
            hello_var = tk.StringVar(value="default")
            hello_interval_menu = ttk.Combobox(network_frame, textvariable=hello_var, values=["default", "1", "5", "10", "15", "20", "25"])
            hello_interval_menu.grid(row=row + 3, column=1)

            # Hold Time entry
            tk.Label(network_frame, text="Hold Time (Seconds):", bg="#2E2E2E", fg="white").grid(row=row + 3, column=2)
            hold_var = tk.StringVar(value="default")
            hold_time_menu = ttk.Combobox(network_frame, textvariable=hold_var, values=["default", "4", "8", "12", "16", "20", "40"])
            hold_time_menu.grid(row=row + 3, column=3)

            # Add a horizontal line (separator)
            separator = tk.Frame(network_frame, height=2, bg="gray")
            separator.grid(row=row + 4, columnspan=10, sticky="ew", pady=5)

            # Store entries in the list
            network_entries.append((network_entry, wildcard_entry, auth_var, chain_name_entry, key_no_entry, auth_key_entry, interface_entry,  hello_var, hold_var, e_BW_var))

        # Button to add new network entry row
        add_network_entry_btn=tk.Button(config_frame, text="Add Network Entry", command=add_network_entry)
        add_network_entry_btn.grid(row=5, columnspan=5, pady=10)
        
        def submit_configuration():
            # AS
            eigrp_AS = AS_entry.get()
            eigrp_command = f'router eigrp {eigrp_AS}'
            if not eigrp_AS :
                 self.log_output("Input Error: Please fill in the EIGRP Asynchronous System Number field.")
                 return
            if not eigrp_AS.isdigit() or int(eigrp_AS) <= 0 or int(eigrp_AS) >= 65536 :
                self.log_output("Input Error: EIGRP Asynchronous System Number must be a number between ( 1 and 65535 ).")
                return
            self.log_output(f"Sending command: {eigrp_command}")
            # auto-summarization    
            if Auto_sum_var.get() == 'yes':
                    Auto_sum_command = f'auto-summary'
                    self.log_output(f"Sending command: {Auto_sum_command}")
                    ssh.send_config_set([eigrp_command,Auto_sum_command], exit_config_mode=False)
            else :
                    Auto_sum_command = f'no auto-summary'
                    self.log_output(f"Sending command: {Auto_sum_command}")
                    ssh.send_config_set([eigrp_command,Auto_sum_command], exit_config_mode=False)
            # Variance
            variance_var=variance_menu.get()
            if variance_var != "default":
                if not variance_var.isdigit() or int(variance_var) <= 0:
                    self.log_output("Input Error,Variance Number must be a positive integer or 'default'.")
                    return
            # self.log_output(f"Sending command: {eigrp_command}")
            if variance_var == "default":
                    variance_command=f'variance 1'
                    ssh.send_config_set([eigrp_command,variance_command], exit_config_mode=False)
                    self.log_output(f"returning for the default value of the variance that is 1")
            else:    
                    variance_command=f'variance {variance_var}'
                    self.log_output(f"Sending command:{variance_command}") 
                    ssh.send_config_set([eigrp_command,variance_command], exit_config_mode=False) 
            
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
                Int_BW_var=entry[9].get()
    
                if not self.validate_ip(network_var,0):  # Check if the IP is valid
                        self.log_output("Input Error: Please enter a valid network address.")  # Log an error if invalid
                        return  # Exit the method if there is an error
                elif not self.validate_ip(wildcard_mask_var,0) :
                        self.log_output("Input Error: Please enter a valid WildCard address.")  # Log an error if invalid
                        return
            
                if not self.is_valid_interface(interface_var):
                        self.log_output("Input Error: interface must be like f0/0 , g0/1 , s1/1 or loopback0.")
                        return
                if auth_var == 'yes' and not (chain_name_var or key_no_var or auth_key_var ):
                        self.log_output("Input Error: please fill out all the Authentication Entries.")
                        return
                if auth_var == 'yes' and (not key_no_var.isdigit() or int(key_no_var) <= 0):
                        self.log_output("Input Error: Key Number must be a positive integer.")
                        return 

                if Int_BW_var != "default":
                    if not Int_BW_var.isdigit() or int(Int_BW_var) <= 0 or int(Int_BW_var) > 999999:
                            self.log_output("Input Error,The interface BandWidth must be a positive integer <1-999999> or 'default'.")
                            return
            
                #hello_var != "default"
                if hello_var != "default":
                    if not hello_var.isdigit() or int(hello_var) <= 0 or int(hello_var) > 65535 :
                            self.log_output("Input Error,Hello Interval must be a positive integer <1-65535> or 'default'.")
                            return
                if hold_var !="default" :        
                    if not hold_var.isdigit() or int(hold_var) <= 0 or int(hold_var) > 65535 :
                            self.log_output("Input Error,Hold Time must be a positive integer or 'default'.")
                            return
                                        
                # EIGRP network command
                network_command = f'network {network_var} {wildcard_mask_var}'
                self.log_output(f"Sending command: {network_command}")
                ssh.send_config_set([eigrp_command,network_command], exit_config_mode=False)
                interface_command = f'interface {interface_var}'             
                if auth_var == 'yes':  
                    # key chain preparing           
                            k1_command = f'key chain {chain_name_var}' 
                            k2_command = f'key {key_no_var}'
                            k3_command = f'key-string {auth_key_var}'
                            self.log_output(f"Sending command: {k1_command}")
                            self.log_output(f"Sending command: {k2_command}")
                            self.log_output(f"Sending command: {k3_command}")
                            ssh.send_config_set([k1_command,k2_command,k3_command], exit_config_mode=False)
                                                
                            # interface authentication
                        
                            self.log_output(f"Sending command: {interface_command}")
                            ssh.send_config_set([interface_command], exit_config_mode=False)

                            interface_auth1_command = f'ip authentication key-chain eigrp {eigrp_AS} {chain_name_var}'
                            interface_auth2_command = f'ip authentication mode eigrp {eigrp_AS} md5'

                            self.log_output(f"Sending command: {interface_auth1_command}")
                            self.log_output(f"Sending command: {interface_auth2_command}")
                            ssh.send_config_set([interface_auth1_command,interface_auth2_command], exit_config_mode=False)

                if hello_var == "default":
                        e_hello_default_command=f'ip hello-interval eigrp {eigrp_AS} 5'
                        ssh.send_config_set([interface_command,e_hello_default_command], exit_config_mode=False)
                        self.log_output(f"returning for the default value of the hello interval that is 5 seconds") 
                else:    
                        # Handle Hello Interval
                        e_hello_command=f'ip hello-interval eigrp {eigrp_AS} {hello_var}'
                        self.log_output(f"Sending command:{interface_command}")
                        self.log_output(f"Sending command:{e_hello_command}")
                        ssh.send_config_set([interface_command,e_hello_command], exit_config_mode=False)    

                if hold_var == "default":
                        hold_default_command=f'ip hold-time eigrp {eigrp_AS} 15'
                        ssh.send_config_set([interface_command,hold_default_command], exit_config_mode=False) 
                        self.log_output(f"returning for the default value of the hold time that is 15 seconds")
                else :
                        # Handle Hold Time
                        hold_command=f'ip hold-time eigrp {eigrp_AS} {hold_var}'
                        self.log_output(f"Sending command:{interface_command}")
                        self.log_output(f"Sending command:{hold_command}")
                        ssh.send_config_set([interface_command,hold_command], exit_config_mode=False)
                # Handle interface BandWidth for the percent of the control plane with respect to the default BW of the interface
                if Int_BW_var =='default':
                        self.log_output(f"returning for the default value of the Interface BandWidth that is 50%")
                        e_BW_default_command=f'ip bandwidth-percent eigrp {eigrp_AS} 50'
                        ssh.send_config_set([interface_command,e_BW_default_command], exit_config_mode=False)
                else:
                        e_BW_command=f'ip bandwidth-percent eigrp {eigrp_AS} {Int_BW_var}'
                        self.log_output(f"Sending command:{interface_command}")
                        self.log_output(f"Sending command:{e_BW_command}")
                        ssh.send_config_set([interface_command,e_BW_command], exit_config_mode=False)

            self.log_output(f'Success: Router "{device}" configured with EIGRP successfully.')
        # Submit button
        submit_button = tk.Button(config_frame, text="Submit Configuration", command=submit_configuration)
        submit_button.grid(row=6, columnspan=5, pady=10)

        show_frame = tk.Frame(config_frame, bg="#4E4E4E")
        show_frame.grid(row=7, columnspan=5, pady=10, sticky="ew")
        # Example EIGRP show commands
        eigrp_commands = [
            "show ip eigrp neighbor",
            "show ip eigrp topology",
            "show ip eigrp topology all-links",
            "show ip route",
            "show ip route eigrp",
            "show ip protocols",
            "show  ip eigrp interfaces detail",
            "show key chain" 
        ]

        # Combobox for selecting a command
        e_command_var = tk.StringVar(value="")
        e_command_label = tk.Label(show_frame, text="Select an EIGRP Show Command:", bg="#4E4E4E", fg="gray")
        e_command_label.grid(row=0, column=0)
        e_command_menu = ttk.Combobox(show_frame, textvariable=e_command_var, values=eigrp_commands)
        e_command_menu.grid(row=0, column=1)

        # Button to send the selected command and display output
        def e_send_command():
            e_selected_command = e_command_var.get()
            if e_selected_command:
                # Send the command to the router
                output=ssh.send_config_set(['do '+e_selected_command], exit_config_mode=False)
                self.log_output(f"output for the show command of {device} :\n{output}")

        send_command_button = tk.Button(show_frame, text="Send Command", command=e_send_command)
        send_command_button.grid(row=0, column=2, pady=10)
        # Add a horizontal line (separator)
        separator = tk.Frame(show_frame, height=2, bg="gray")
        separator.grid(row=1, columnspan=10, sticky="ew", pady=5)
#................................................................................................................
    def configure_ospf(self, ssh, device):
        # Create a frame for OSPF configuration inputs
        # config_frame = tk.Frame(self.scrollable_frame, bg=colors_list[random.randint(0, 4)])
        config_frame = tk.Frame(self.scrollable_frame, bg="#2E2E2E")
        config_frame.pack(pady=10, fill='both', expand=True)

        # Prompt for OSPF Process ID
        tk.Label(config_frame, text="OSPF Process ID:", bg="#4E4E4E", fg="white").grid(row=0, column=0)
        ospf_pid_entry = tk.Entry(config_frame)
        ospf_pid_entry.grid(row=0, column=1)

        All_Int_passive_var = tk.StringVar(value="no")
        tk.Label(config_frame, text="Making all ints passive ?:", bg="#4E4E4E", fg="white").grid(row=1, column=0)
        tk.OptionMenu(config_frame, All_Int_passive_var, "yes", "no").grid(row= 1, column=1)

        tk.Label(config_frame, text="Cost BandWidth(In Mega):", bg="#4E4E4E", fg="white").grid(row=2, column=0)
        BW_var = tk.StringVar(value="default")
        BW_menu = ttk.Combobox(config_frame, textvariable=BW_var, values=["default"])
        BW_menu.grid(row=2, column=1)
            
        default_ospf_var = tk.StringVar(value="no")
        tk.Label(config_frame, text=f"Making router {device} as a default ospf route ?:", bg="#4E4E4E", fg="white").grid(row=3, column=0)
        tk.OptionMenu(config_frame, default_ospf_var, "yes", "no").grid(row= 3, column=1)

        # Frame for other entries
        network_frame = tk.Frame(config_frame, bg="#4E4E4E")
        network_frame.grid(row=4, columnspan=5, pady=10, sticky="ew")

        # Initialize list to hold network configurations
        network_entries = []

        # Function to add network entries
        def add_network_entry():
            row = len(network_entries) * 5  # Current row index for new entry, ensuring proper spacing

            # Network entry
            tk.Label(network_frame, text=f"Network {row // 5 + 1}:", bg="#2E2E2E", fg="white").grid(row=row, column=0)
            network_entry = tk.Entry(network_frame)
            network_entry.grid(row=row, column=1)

            # Wildcard mask entry
            tk.Label(network_frame, text="Wildcard Mask:", bg="#2E2E2E", fg="white").grid(row=row, column=2)
            wildcard_entry = tk.Entry(network_frame)
            wildcard_entry.grid(row=row, column=3)

            # OSPF Area entry
            tk.Label(network_frame, text="OSPF Area:", bg="#2E2E2E", fg="white").grid(row=row, column=4)
            ospf_area_entry = tk.Entry(network_frame)
            ospf_area_entry.grid(row=row, column=5)

            # Interface entry
            tk.Label(network_frame, text="Interface:", bg="#2E2E2E", fg="white").grid(row=row, column=6)
            interface_entry = tk.Entry(network_frame)
            interface_entry.grid(row=row, column=7)

            # Passive interface entry
            passive_var = tk.StringVar(value="no")
            tk.Label(network_frame, text="Passive?", bg="#2E2E2E", fg="white").grid(row=row + 1, column=0)
            tk.OptionMenu(network_frame, passive_var, "yes", "no").grid(row=row + 1, column=1)

            # Authentication Type
            tk.Label(network_frame, text="Authentication Type:", bg="#2E2E2E", fg="white").grid(row=row+1, column=2)
            auth_type_var = tk.StringVar(value="none")
            auth_type_menu = tk.OptionMenu(network_frame, auth_type_var, "none", "simple", "md5", command=lambda _: update_auth_key_entry(row))
            auth_type_menu.grid(row=row+1, column=3)

            # Authentication key entry and label (initially hidden)
            auth_key_label = tk.Label(network_frame, text="Authentication Key:", bg="#2E2E2E", fg="white")
            auth_key_entry = tk.Entry(network_frame, show='*')

            # Initially hide the label and entry
            auth_key_label.grid(row=row+1, column=4)
            auth_key_entry.grid(row=row+1, column=5)
            auth_key_label.grid_remove()  # Hide the label initially
            auth_key_entry.grid_remove()   # Hide the entry initially

            # Function to update the visibility of the authentication key entry and label
            def update_auth_key_entry(row):
                if auth_type_var.get() in ["simple", "md5"]:
                    auth_key_label.grid(row=row+1, column=4)  # Show the label
                    auth_key_entry.grid(row=row+1, column=5)   # Show the entry
                else:
                    auth_key_label.grid_remove()  # Hide the label
                    auth_key_entry.grid_remove()   # Hide the entry

            # Hello Interval entry
            tk.Label(network_frame, text="Hello Interval:", bg="#2E2E2E", fg="white").grid(row=row + 2, column=0)
            hello_var = tk.StringVar(value="default")
            hello_interval_menu = ttk.Combobox(network_frame, textvariable=hello_var, values=["default", "1", "2", "3", "4", "5", "10"])
            hello_interval_menu.grid(row=row + 2, column=1)

            # Dead Interval entry
            tk.Label(network_frame, text="Dead Interval:", bg="#2E2E2E", fg="white").grid(row=row + 2, column=2)
            dead_var = tk.StringVar(value="default")
            dead_interval_menu = ttk.Combobox(network_frame, textvariable=dead_var, values=["default", "4", "8", "12", "16", "20", "40"])
            dead_interval_menu.grid(row=row + 2, column=3)

            tk.Label(network_frame, text="Interface Cost:", bg="#2E2E2E", fg="white").grid(row=row + 3, column=0)
            Int_Cost_var = tk.StringVar(value="default")
            dead_interval_menu = ttk.Combobox(network_frame, textvariable=Int_Cost_var, values=["default"])
            dead_interval_menu.grid(row=row + 3, column=1)

            # Add a horizontal line (separator)
            separator = tk.Frame(network_frame, height=2, bg="gray")
            separator.grid(row=row + 4, columnspan=10, sticky="ew", pady=5)

            # Store entries in the list
            network_entries.append((network_entry, wildcard_entry, ospf_area_entry, auth_key_entry, auth_type_var, interface_entry, passive_var, hello_var, dead_var, Int_Cost_var))

        # Button to add new network entry row
        add_network_entry_btn=tk.Button(config_frame, text="Add Network Entry", command=add_network_entry)
        add_network_entry_btn.grid(row=5, columnspan=5, pady=10)
        
        def submit_configuration():
            ospf_pid = ospf_pid_entry.get()
            ospf_command = f'router ospf {ospf_pid}'
            if not ospf_pid :
                 self.log_output("Input Error: Please fill in the process id field.")
                 return
            if not ospf_pid.isdigit() or int(ospf_pid) <= 0 or int(ospf_pid) >= 65536 :
                self.log_output("Input Error: OSPF Process ID must be a number between ( 1 and 65535 ).")
                return
            
            BW_var=BW_menu.get()
            if BW_var != "default":
                if not BW_var.isdigit() or int(BW_var) <= 0:
                    self.log_output("Input Error,B.W Cost must be a positive integer or 'default'.")
                    return
            self.log_output(f"Sending command: {ospf_command}")
            if BW_var == "default":
                    BW_command=f'auto-cost reference-bandwidth 100'
                    ssh.send_config_set([ospf_command,BW_command], exit_config_mode=False)
                    self.log_output(f"returning for the default value of the Cost BandWidth")
                    self.log_output(f"Alert : Pleast ensure that reference B.W must be consistent across all routers") 
            else:    
                    # Handle cost B.W
                    BW_command=f'auto-cost reference-bandwidth {BW_var}'
                    # self.log_output(f"Sending command:{ospf_command}")
                    self.log_output(f"Sending command:{BW_command}")
                    self.log_output(f"Alert : Pleast ensure that reference B.W must be consistent across all routers") 
                    ssh.send_config_set([ospf_command,BW_command], exit_config_mode=False) 
                 # Handle passive interface
            
            if All_Int_passive_var.get() == 'yes':
                    All_Int_passive_var_command = f'passive-interface default'
                    self.log_output(f"Sending command: {All_Int_passive_var_command}")
                    ssh.send_config_set([ospf_command,All_Int_passive_var_command], exit_config_mode=False)

            if default_ospf_var.get() == 'yes':
                    default_ospf_var_command = f'default-information originate always'
                    self.log_output(f"Sending command: {default_ospf_var_command}")
                    self.log_output(f"Alert : you shuld make a default static routing or BGP to this router (router {device})  ")
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
    
                if not self.validate_ip(network,0):  # Check if the IP is valid
                        self.log_output("Input Error: Please enter a valid network address.")  # Log an error if invalid
                        return  # Exit the method if there is an error
                elif not self.validate_ip(wildcard_mask,0) :
                        self.log_output("Input Error: Please enter a valid WildCard address.")  # Log an error if invalid
                        return
                elif not ospf_area.isdigit() or int(ospf_area) < 0:
                        self.log_output("Input Error: area number must be a positive integer")
                        return  # Log an error if invalid
                if not self.is_valid_interface(interface):
                        self.log_output("Input Error: interface must be like f0/0 , g0/1 s1/1 or loopback0.")
                        return
                if auth_type == 'md5' and not auth_key or auth_type=='simple' and not auth_key:
                        self.log_output("Input Error: Authentication key cannot be empty for MD5 or simple.")
                        return
                #hello_var != "default"
                if hello_var != "default":
                    if not hello_var.isdigit() or int(hello_var) <= 0:
                            self.log_output("Input Error,Hello Interval must be a positive integer or 'default'.")
                            return
                if dead_var !="default" :        
                    if not dead_var.isdigit() or int(dead_var) <= 0:
                                self.log_output("Input Error,Dead Interval must be a positive integer or 'default'.")
                                return
                if hello_var != "default" and dead_var!="default" and int(dead_var) <= int(hello_var):
                        self.log_output("Input Error,Dead Interval must be greater than Hello Interval.")
                        return
                if Int_Cost_var != "default":
                    if not Int_Cost_var.isdigit() or int(Int_Cost_var) <= 0:
                            self.log_output("Input Error,The interface Cost must be a positive integer or 'default'.")
                            return
                    # Validate the network address
                    
                    # OSPF network command
                network_command = f'network {network} {wildcard_mask} area {ospf_area}'
                self.log_output(f"Sending command: {network_command}")
                ssh.send_config_set([ospf_command,network_command], exit_config_mode=False)
                            
                if passive == 'yes':
                        passive_command = f'passive-interface {interface}'
                else :
                        passive_command = f'no passive-interface {interface}'
                self.log_output(f"Sending command: {passive_command}")
                ssh.send_config_set([ospf_area,passive_command], exit_config_mode=False)
                    # Handle interface-specific authentication
                interface_command = f'interface {interface}'
                if auth_type != 'none':
                    self.log_output(f"Sending command: {interface_command}")
                    ssh.send_config_set([interface_command], exit_config_mode=False)

                        # Log and send the authentication command for the interface
                if auth_type == 'md5':
                            interface_auth_command = f'ip ospf authentication message-digest'
                            self.log_output(f"Sending command: {interface_auth_command}")
                            ssh.send_config_set([interface_auth_command], exit_config_mode=False)
                            interface_auth_key_command = f'ip ospf message-digest-key 1 md5 {auth_key}'
                            self.log_output(f"Sending command: {interface_auth_key_command}")
                            ssh.send_config_set([interface_auth_key_command], exit_config_mode=False)
                elif auth_type == 'simple':
                            interface_auth_command_1 = f'ip ospf authentication'
                            self.log_output(f"Sending command: {interface_auth_command_1}")
                            ssh.send_config_set([interface_auth_command_1], exit_config_mode=False)

                            interface_auth_command_2 = f'ip ospf authentication-key {auth_key}'
                            self.log_output(f"Sending command: {interface_auth_command_2}")
                            ssh.send_config_set([interface_auth_command_2], exit_config_mode=False)

                if hello_var == "default":
                        hello_default_command=f'ip ospf hello-interval 10'
                        ssh.send_config_set([interface_command,hello_default_command], exit_config_mode=False)
                        self.log_output(f"returning for the default value of the hello interval") 
                else:    
                        # Handle Hello Interval
                        hello_command=f'ip ospf hello-interval {hello_var}'
                        self.log_output(f"Sending command:{interface_command}")
                        self.log_output(f"Sending command:{hello_command}")
                        ssh.send_config_set([interface_command,hello_command], exit_config_mode=False)    

                if dead_var == "default":
                        dead_default_command=f'ip ospf dead-interval 40'
                        ssh.send_config_set([interface_command,dead_default_command], exit_config_mode=False) 
                        self.log_output(f"returning for the default value of the dead interval")
                else :
                        # Handle Dead Interval
                        dead_command=f'ip ospf dead-interval {dead_var}'
                        self.log_output(f"Sending command:{interface_command}")
                        self.log_output(f"Sending command:{dead_command}")
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
                        self.log_output(f"returning for the default value of the interface {interface} cost that is {int_cost_default_value}")
                else :
                        Int_Cost_command=f'ip ospf cost {Int_Cost_var}'
                        self.log_output(f"Sending command:{Int_Cost_command}")
                        ssh.send_config_set([interface_command,Int_Cost_var], exit_config_mode=False)
           
            self.log_output(f'Success: Router "{device}" configured with OSPF successfully.')

        # Submit button
        submit_button = tk.Button(config_frame, text="Submit Configuration", command=submit_configuration)
        submit_button.grid(row=6, columnspan=5, pady=10)

        show_frame = tk.Frame(config_frame, bg="#4E4E4E")
        show_frame.grid(row=7, columnspan=5, pady=10, sticky="ew")
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
        command_var = tk.StringVar(value="")
        command_label = tk.Label(show_frame, text="Select OSPF Show Command:", bg="#4E4E4E", fg="gray")
        command_label.grid(row=0, column=0)
        command_menu = ttk.Combobox(show_frame, textvariable=command_var, values=ospf_commands)
        command_menu.grid(row=0, column=1)

        # Button to send the selected command and display output
        def send_command():
            selected_command = command_var.get()
            if selected_command:
                # Send the command to the router
                output=ssh.send_config_set(['do '+selected_command], exit_config_mode=False)
                self.log_output(f"output for the show command of {device} :\n{output}")

        send_command_button = tk.Button(show_frame, text="Send Command", command=send_command)
        send_command_button.grid(row=0, column=2, pady=10)
        # Add a horizontal line (separator)
        separator = tk.Frame(show_frame, height=2, bg="gray")
        separator.grid(row=1, columnspan=10, sticky="ew", pady=5)
#..........................................................................................................................
# Main loop
if __name__ == "__main__":
    root = tk.Tk()
    app = RouterConfigurator(root)
    root.mainloop()