import tkinter as tk  # Importing the tkinter library for GUI
from netmiko import ConnectHandler  # Importing ConnectHandler from netmiko for SSH connections
import logging  # Import logging for detailed output
from tkinter import simpledialog, ttk, Toplevel  # Importing specific dialogs and ComboBox from tkinter

# Configure logging
logging.basicConfig(filename='netmiko.log', level=logging.DEBUG)
logging.getLogger("netmiko").setLevel(logging.DEBUG)

class CustomDialog(Toplevel):
    def __init__(self, parent, title, prompt):
        super().__init__(parent)
        self.title(title)

        # Set dialog size
        self.geometry("600x250")
        self.parent = parent
        self.result = None
        
        # Center the dialog on the screen
        self.update_idletasks()  # Update "requested size" from geometry manager
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.parent.winfo_screenwidth() // 2) - (width // 2)
        y = (self.parent.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        label = tk.Label(self, text=prompt)
        label.pack(pady=10)

        self.entry = tk.Entry(self)
        self.entry.pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        ok_button = tk.Button(button_frame, text="OK", command=self.ok)
        ok_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancel", command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5)

        self.transient(parent)  # Keep dialog above parent
        self.grab_set()  # Make dialog modal
        self.parent.wait_window(self)  # Wait for dialog to close

    def ok(self):
        self.result = self.entry.get()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

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
        self.next_button = tk.Button(self.scrollable_frame, text="Next", command=self.show_router_inputs, bg="#4E4E4E", fg="white")
        self.next_button.pack(pady=10)

        # Create a frame for router inputs
        self.router_frame = tk.Frame(self.scrollable_frame, bg="#2E2E2E")
        self.router_frame.pack(pady=10)

        # Create a text box for output display
        self.output_text = tk.Text(self.scrollable_frame, height=15, bg="#1E1E1E", fg="white", font=("Arial", 12))
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
            self.router_inputs = {i: {} for i in range(1, self.router_num + 1)}  # Initialize input storage
            self.current_router = 1  # Reset current router index
            self.prompt_router_info()
        except ValueError:
            self.log_output("Input Error: Please enter a valid number.")

    def prompt_router_info(self):
        if self.current_router > self.router_num:
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

        tk.Label(self.router_frame, text="Routing Protocol:", bg="#2E2E2E", fg="white").pack()
        self.protocol_var = tk.StringVar()
        protocol_combobox = ttk.Combobox(self.router_frame, textvariable=self.protocol_var, values=["EIGRP", "OSPF"])
        protocol_combobox.pack()
        self.router_inputs[self.current_router]['protocol'] = protocol_combobox  # Store the ComboBox

        # Proceed button for the current router
        proceed_button = tk.Button(self.router_frame, text="Next Router", command=self.next_router, bg="#4E4E4E", fg="white")
        proceed_button.pack(pady=10)

    def next_router(self):
        # Collect the inputs for the current router
        ip = self.router_inputs[self.current_router]['ip'].get()
        username = self.router_inputs[self.current_router]['username'].get()
        password = self.router_inputs[self.current_router]['password'].get()
        protocol = self.router_inputs[self.current_router]['protocol'].get().strip().lower()

        if not ip or not username or not password or not protocol:
            self.log_output("Input Error: Please fill in all fields.")
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
                else:
                    self.log_output(f"Input Error: Invalid routing protocol for router {router_num}.")
            except Exception as e:
                self.log_output(f"Connection Error for router {router_num}: {str(e)}")
                logging.exception(f"Connection failed for router {router_num}")

    def configure_eigrp(self, ssh, device):
        # Create a frame for EIGRP configuration inputs
        config_frame = tk.Frame(self.master, bg="#2E2E2E")
        config_frame.pack(pady=10, fill='both', expand=True)

        # Prompt for EIGRP Autonomous System number
        tk.Label(config_frame, text="EIGRP AS #:", bg="#2E2E2E", fg="white").grid(row=0, column=0)
        eigrpas_entry = tk.Entry(config_frame)
        eigrpas_entry.grid(row=0, column=1)

        # Prompt for the MD5 authentication key
        tk.Label(config_frame, text="MD5 Authentication Key:", bg="#2E2E2E", fg="white").grid(row=1, column=0)
        auth_key_entry = tk.Entry(config_frame, show='*')
        auth_key_entry.grid(row=1, column=1)

        # Prompt for the key chain name
        tk.Label(config_frame, text="Key Chain Name:", bg="#2E2E2E", fg="white").grid(row=2, column=0)
        key_chain_name_entry = tk.Entry(config_frame)
        key_chain_name_entry.grid(row=2, column=1)

        # Prompt to disable automatic summarization
        tk.Label(config_frame, text="Enable Auto-Summary?", bg="#2E2E2E", fg="white").grid(row=3, column=0)
        disable_autosum_var = tk.StringVar(value="no")
        tk.OptionMenu(config_frame, disable_autosum_var, "yes", "no").grid(row=3, column=1)

        # Frame for network/interface entries
        network_frame = tk.Frame(config_frame, bg="#2E2E2E")
        network_frame.grid(row=4, columnspan=2, pady=10, sticky="ew")

        # Initialize list to hold network configurations
        network_entries = []

        # Function to add network entries
        def add_network_entry():
            row = len(network_entries)

            # Network entry
            tk.Label(network_frame, text=f"Network {row + 1}:", bg="#2E2E2E", fg="white").grid(row=row, column=0)
            network_entry = tk.Entry(network_frame)
            network_entry.grid(row=row, column=1)

            # Interface entry
            tk.Label(network_frame, text="Interface:", bg="#2E2E2E", fg="white").grid(row=row, column=2)
            interface_entry = tk.Entry(network_frame)
            interface_entry.grid(row=row, column=3)

            # Enable authentication entry
            enable_auth_var = tk.StringVar(value="no")
            tk.Label(network_frame, text="Enable Auth?", bg="#2E2E2E", fg="white").grid(row=row, column=4)
            tk.OptionMenu(network_frame, enable_auth_var, "yes", "no").grid(row=row, column=5)

            # Passive interface entry
            passive_var = tk.StringVar(value="no")
            tk.Label(network_frame, text="Passive?", bg="#2E2E2E", fg="white").grid(row=row, column=6)
            tk.OptionMenu(network_frame, passive_var, "yes", "no").grid(row=row, column=7)

            # Store entries in the list
            network_entries.append((network_entry, interface_entry, enable_auth_var, passive_var))

        # Button to add new network entry row
        tk.Button(config_frame, text="Add Network Entry", command=add_network_entry).grid(row=5, columnspan=2, pady=10)

        # Button to submit the configuration
        def submit_configuration():
            eigrpas = eigrpas_entry.get()
            if not eigrpas.isdigit() or int(eigrpas) <= 0:
                self.log_output("Input Error: EIGRP AS number must be a positive integer.")
                return

            routereigrp = f'router eigrp {eigrpas}'
            auth_key = auth_key_entry.get()
            if not auth_key:
                self.log_output("Input Error: Authentication key cannot be empty.")
                return

            key_chain_name = key_chain_name_entry.get()
            if not key_chain_name:
                self.log_output("Input Error: Key chain name cannot be empty.")
                return

            auto_summary_command = 'auto-summary' if disable_autosum_var.get().strip().lower() == 'yes' else 'no auto-summary'

            interface_auth_commands = []

            # Process each network entry
            for entry in network_entries:
                network_i = entry[0].get()
                interface = entry[1].get()
                enable_auth = entry[2].get().strip().lower()
                passive = entry[3].get().strip().lower()

                if not network_i:
                    self.log_output("Input Error: Network cannot be empty.")
                    continue

                if not interface:
                    self.log_output("Input Error: Interface cannot be empty.")
                    continue

                if 'loopback' in interface.lower():
                    self.log_output(f'Info: Skipping authentication for loopback interface {interface}')
                    continue

                # Prepare configuration commands for the network
                config_commands = [routereigrp, f'network {network_i}', auto_summary_command]
                self.log_output("Sending command: " + ', '.join(config_commands))
                output = ssh.send_config_set(config_commands, exit_config_mode=False)

                # Handle interface authentication commands
                if enable_auth == 'yes':
                    interface_auth_commands.extend([
                        f'interface {interface}',
                        f'ip authentication mode eigrp {eigrpas} md5',
                        f'ip authentication key-chain eigrp {eigrpas} {key_chain_name}'
                    ])

                if passive == 'yes':
                    interface_auth_commands.append(f'passive-interface {interface}')

            # If there are any interface authentication commands, send them
            if interface_auth_commands:
                self.log_output("Sending command: " + ', '.join(interface_auth_commands))
                output = ssh.send_config_set(interface_auth_commands, exit_config_mode=False)

            # Prepare the key chain configuration commands
            key_chain_config = [f'key chain {key_chain_name}', 'key 1', f'key-string {auth_key}']
            self.log_output("Sending command: " + ', '.join(key_chain_config))
            output = ssh.send_config_set(key_chain_config)

            self.log_output(f'Success: Router "{device}" configured with EIGRP successfully.')

        # Submit button
        submit_button = tk.Button(config_frame, text="Submit Configuration", command=submit_configuration)
        submit_button.grid(row=6, columnspan=2, pady=10)
   
    def configure_ospf(self, ssh, device):
        # Prompt for the OSPF Process ID
        ospf_process_id_dialog = CustomDialog(self.master, "OSPF Configuration - " + device, "OSPF Process ID:")
        ospf_process_id = ospf_process_id_dialog.result
        if not ospf_process_id:
            self.log_output("Input Error: OSPF Process ID cannot be empty.")
            return

        routerospf = f'router ospf {ospf_process_id}'

        # Prompt for OSPF Authentication Type
        auth_type_dialog = CustomDialog(self.master, "OSPF Authentication - " + device, "Enter OSPF Authentication Type (none/simple/md5):")
        auth_type = auth_type_dialog.result
        if auth_type not in ['none', 'simple', 'md5']:
            self.log_output("Input Error: Invalid authentication type.")
            return

        auth_key = None
        key_chain_name = None

        # If MD5 authentication is used, prompt for the key and key-chain name
        if auth_type == 'md5':
            auth_key_dialog = CustomDialog(self.master, "OSPF Configuration - " + device, "Enter MD5 Authentication Key:")
            auth_key = auth_key_dialog.result
            if not auth_key:
                self.log_output("Input Error: Authentication key cannot be empty.")
                return
                
            # Prompt for the key-chain name
            key_chain_name_dialog = CustomDialog(self.master, "OSPF Configuration - " + device, "Enter Key Chain Name:")
            key_chain_name = key_chain_name_dialog.result
            if not key_chain_name:
                self.log_output("Input Error: Key chain name cannot be empty.")
                return

        # Continue prompting for networks
        network_num_dialog = CustomDialog(self.master, "OSPF Configuration - " + device, "How many networks would you like to enable in OSPF:")
        network_num = network_num_dialog.result
        if not network_num.isdigit() or int(network_num) <= 0:
            self.log_output("Input Error: Invalid number of networks.")
            return

        network_num = int(network_num)
        for _ in range(network_num):
            network_i_dialog = CustomDialog(self.master, "OSPF Configuration - " + device, "Please specify the network and wildcard (separated by a space) to enable:")
            network_i = network_i_dialog.result
            if not network_i:
                self.log_output("Input Error: Network cannot be empty.")
                continue

            area_dialog = CustomDialog(self.master, "OSPF Configuration - " + device, "Please specify the OSPF area:")
            area = area_dialog.result
            if not area:
                self.log_output("Input Error: OSPF area cannot be empty.")
                continue

            # Prepare OSPF configuration commands
            config_commands = [routerospf, f'network {network_i} area {area}']

            # Add authentication command if applicable
            if auth_type == 'simple':
                simple_key_dialog = CustomDialog(self.master, "OSPF Configuration - " + device, "Enter Simple Password:")
                simple_key = simple_key_dialog.result
                if not simple_key:
                    self.log_output("Input Error: Password cannot be empty.")
                    continue
                config_commands.append(f'area {area} authentication simple {simple_key}')
            elif auth_type == 'md5':
                config_commands.append(f'area {area} authentication message-digest')
                config_commands.append(f'key chain {key_chain_name}')
                config_commands.append(f'key 1')
                config_commands.append(f'key-string {auth_key}')

            # Ask if the user wants to enable authentication on interfaces
            enable_auth_dialog = CustomDialog(self.master, "Interface Authentication - " + device, f'Enable authentication on interface for network {network_i}? (yes/no):')
            if enable_auth_dialog.result.lower() == 'yes':
                interface_dialog = CustomDialog(self.master, "Interface Authentication - " + device, "Please specify the interface (e.g., GigabitEthernet0/0):")
                interface = interface_dialog.result
                if interface:
                    config_commands.append(f'interface {interface}')
                    if auth_type == 'md5':
                        config_commands.append(f'ip ospf authentication message-digest')
                        config_commands.append(f'ip ospf message-digest-key 1 md5 {auth_key}')
                    elif auth_type == 'simple':
                        config_commands.append(f'ip ospf authentication simple {simple_key}')

                    # Ask if the user wants to configure the interface as passive
                    passive_dialog = CustomDialog(self.master, "Passive Interface - " + device, f'Configure {interface} as passive interface? (yes/no):')
                    if passive_dialog.result.lower() == 'yes':
                        config_commands.append(f'passive-interface {interface}')

            # Send configuration commands to the device
            output = ssh.send_config_set(config_commands, exit_config_mode=False)
            ssh.exit_config_mode()

        self.log_output(f'Success: Router "{device}" configured with OSPF successfully')
if __name__ == "__main__":
    root = tk.Tk()  # Create the main application window
    app = RouterConfigurator(root)  # Instantiate the RouterConfigurator class
    root.mainloop()  # Start the Tkinter event loop