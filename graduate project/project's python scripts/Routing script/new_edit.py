import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, Toplevel
import re
import logging
from netmiko import ConnectHandler

# Configure logging
logging.basicConfig(filename='netmiko.log', level=logging.DEBUG)
logging.getLogger("netmiko").setLevel(logging.DEBUG)

class RouterConfigurator:
    def __init__(self, root):
        self.root = root
        self.root.title("Router Configuration")
        self.root.geometry("900x600")
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
        protocol_combobox = ctk.CTkOptionMenu(tab, variable=protocol_var, values=["EIGRP", "OSPF", "Default Static Routing"])
        protocol_combobox.pack(pady=5)
        self.router_inputs[router_id]['protocol'] = protocol_combobox  # Store the ComboBox
        output_text = scrolledtext.ScrolledText(tab, width=100, height=10,bg="black", fg="white")
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

            if protocol not in ["ospf", "eigrp", "default static routing"]:
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
                # Display success message in the textbox
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
        """Validates an IPv4 address."""
        pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        return bool(pattern.match(ip))

    def is_valid_interface(self, interface):
        """Validates interface format (e.g., g0/0, s1/1, loopback0)."""
        pattern = r'^(f|g|s|e)\d+/\d+$|^loopback\d+$'
        return bool(re.match(pattern, interface))
    
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
                elif not self.validate_ip(wildcard_mask_var):
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
                    # self.log_output(f"Sending command:{ospf_command}")
                    self.log_output(f"Sending command:{BW_command}",output_text)
                    self.log_output(f"Alert : Pleast ensure that reference B.W must be consistent across all routers",output_text) 
                    ssh.send_config_set([ospf_command,BW_command], exit_config_mode=False) 
                 # Handle passive interface
            
            if All_Int_passive_var.get() == 'yes':
                    All_Int_passive_var_command = f'passive-interface default'
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
                elif not self.validate_ip(wildcard_mask,0) :
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
                #hello_var != "default"
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

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # or "light"
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = RouterConfigurator(root)
    root.mainloop()