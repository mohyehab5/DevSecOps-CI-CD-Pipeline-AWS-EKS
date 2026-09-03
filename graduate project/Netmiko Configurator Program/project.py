from builtins import Exception, NameError, ValueError, int, isinstance, len, map, print, range, set, str, zip
from multiprocessing import connection
import subprocess
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import ttk
from netmiko import ConnectHandler
import customtkinter as ctk
import logging
import threading
import subprocess
import time
import socket
import ipaddress
import tkinter as tk
from tkinter import scrolledtext
import customtkinter as ctk
from netmiko import ConnectHandler

switches1 = [  
        
        #swiitches connection 
        {'device_type': 'cisco_ios','host': '192.168.111.6' ,'username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.7' ,'username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.8' ,'username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.9' ,'username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.10','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.11','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.12','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.13','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.112.6' ,'username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.112.7' ,'username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.112.8' ,'username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.112.9' ,'username': 'project','password': 'pro123',},
        # Add more switches as needed
    ]
routers =[
       #  Routers connections

            # {
            #         'device_type': 'cisco_ios',  # Change as needed for your devices
            #         'host': '192.168.111.5',  # IP of the switch
            #         'username': 'project',
            #         'password': 'pro123',
            #     },{
            #         'device_type': 'cisco_ios',  # Change as needed for your devices
            #         'host': '192.168.112.5',  # IP of the switch
            #         'username': 'project',
            #         'password': 'pro123',
            #     },{
            #         'device_type': 'cisco_ios',  # Change as needed for your devices
            #         'host': '192.168.',  # IP of the switch
            #         'username': 'project',
            #         'password': 'pro123',
            #     },

    ]

sw_111= [
     
          #swiitches connection 
        {'device_type': 'cisco_ios','host': '192.168.111.6','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.7','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.8','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.9','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.10','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.11','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.12','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.13','username': 'project','password': 'pro123',},
    ] 
switchescore = [
        {'device_type': 'cisco_ios','host': '192.168.111.6', 'username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.112.6','username': 'project','password': 'pro123',},
        
        # Add more switches as needed
    ]

# Define the device details
switchesdistr = [
    {'device_type': 'cisco_ios','host': '192.168.111.7','username': 'project','password': 'pro123','global_delay_factor': 5, 'timeout': 100 },
    {'device_type': 'cisco_ios','host': '192.168.111.8','username': 'project','password': 'pro123','global_delay_factor': 5, 'timeout': 100 },
     # Add more switches as needed
    ] 
switchesacsess = [
       
          #swiitches connection 
        {'device_type': 'cisco_ios','host': '192.168.111.9','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.10','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.11','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.12','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.13','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.112.7','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.112.8','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.112.9','username': 'project','password': 'pro123',},
    ]
swacsess111 = [
              #swiitches connection 
        {'device_type': 'cisco_ios','host': '192.168.111.9','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.10','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.11','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.12','username': 'project','password': 'pro123',},
        {'device_type': 'cisco_ios','host': '192.168.111.13','username': 'project','password': 'pro123',},
    ]

global vlan_id
global vlan_name
vlan_id=[]
vlan_name=[]
global windowflage
windowflage =0
global stpflag
stpflag = 0
global pingflag
pingflag = 0
global dhcp_update
dhcp_update=0
global chochoice
chochoice=[]
global dhcp_vlan
dhcp_vlan =[]
global dhcp_interfaces
dhcp_interfaces =[]
global dhcp_interfaces_thrut
dhcp_interface_thrut =[]
global dhcp_switches
dhcp_switches =[]
deletedint=[]
deletedint={

}
entry_widget1_list = []
entry_widget2_list = []
switch = ["sw1","sw2","sw3","sw4","sw5","sw6","sw7","sw8"]
switch_dhcp = ["sw1","sw2","sw3","sw4","sw5","sw6","sw7","sw8"]
sw_ch = ""
switch1 = ["coer1","coer2","sw_a","sw_b","sw1","sw2","sw3","sw4","sw5","sw6","sw7","sw8"]
global vtpflag
vtpflag = 0
#choices

choices_sw = ["sw1", "sw2", "sw3", "sw4", "sw5", "sw6", "sw7", "sw8"]
choices_sw_dhcp = ["sw1", "sw2", "sw3", "sw4", "sw5", "sw6", "sw7", "sw8"]

choices_int_add = {
    "sw1": ["e0/2","e0/3", "e1/0"],
    "sw2": ["e0/2","e0/3", "e1/0", "e1/1"], 
    "sw3": ["e0/2","e0/3", "e1/0"], 
    "sw4": ["e0/2","e0/3", "e1/0", "e1/1", "e1/2"],   
    "sw5": ["e0/2","e0/3", "e1/0", "e1/1", "e1/2"], 
    "sw6": ["e0/1", "e0/2", "e0/3"], 
    "sw7": ["e0/1", "e0/2", "e0/3"], 
    "sw8": ["e0/1", "e0/2", "e0/3", "e1/0"]
}
choices_int_dhcplink={}
choices_int_dhcp1 = {
    "sw1": ["e0/2","e0/3", "e0/1"],
    "sw2": ["e0/2","e0/3", "e1/0", "e1/1"], 
    "sw3": ["e0/2","e0/3", "e1/0"], 
    "sw4": ["e0/2","e0/3", "e1/0", "e1/1", "e1/2"],   
    "sw5": ["e0/2","e0/3", "e1/0", "e1/1", "e1/2"], 
    "sw6": ["e0/1", "e0/2", "e0/3"], 
    "sw7": ["e0/1", "e0/2", "e0/3"], 
    "sw8": ["e0/1", "e0/2", "e0/3", "e1/0"]
}
choices_int_thrust = {
    "sw1": ["e0/2","e0/3", "e0/1"],
    "sw2": ["e0/2","e0/3", "e1/0", "e1/1"], 
    "sw3": ["e0/2","e0/3", "e1/0"], 
    "sw4": ["e0/2","e0/3", "e1/0", "e1/1", "e1/2"],   
    "sw5": ["e0/2","e0/3", "e1/0", "e1/1", "e1/2"], 
    "sw6": ["e0/1", "e0/2", "e0/3"], 
    "sw7": ["e0/1", "e0/2", "e0/3"], 
    "sw8": ["e0/1", "e0/2", "e0/3", "e1/0"]
}
choices_int_dhcp2 = {   
}

def ping_switches():
    global pingflag
    global windowflage
    global stpflag
    pingflag=0
    if vtpflag == 0 and windowflage == 0:
       open_new_window1()
       windowflage +=1
       
    for switch in switches1:
        response=1
        pingflag+=1
        ip = switch['host']
        output.insert(tk.END,f"Pinging {ip}...\n")
        
        # Running the ping command (works on both Windows and Unix-like systems)
        try:
            # Adjust command for Windows vs. Linux
            command = ["ping", "-c", "3", ip] if subprocess.os.name != 'nt' else ["ping", "-n", "3", ip]
            
            # Run the ping command
            response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            
            # Check if the ping was successful
            if response.returncode == 0:
                 output.insert(tk.END,f"Success: {ip} is reachable.\n")
            else:
                 output.insert(tk.END,f"Error: {ip} is not reachable.\n")
        except Exception as e:
            output.insert(tk.END,f"Error pinging {ip}: {e} \n")

def all_vlan():
    global entry
    global drop_frame
    global drop_frame1
    global label_frame
    global error_label
    global error_labe4
    global error_labe2
    global error_labe6
    global error_labe_dhcp
    global combo1
    global combo4
    global combo2
    global combo3
    new_window = ctk.CTkToplevel(root)
    new_window.title("Window Command")
    new_window.geometry("640x900")
    

    frame = ctk.CTkFrame(new_window)
    frame.pack(pady=20, padx=60, fill="both", expand=True)
    start_frame = ctk.CTkFrame(frame)
    start_frame.grid(row=0, column=1, columnspan=3, pady=20, padx=20)
    entry_label = ctk.CTkLabel(master=start_frame, text="Enter number of VLANs:")
    entry_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

# Entry to input number of VLANs
    entry = ctk.CTkEntry(master=start_frame)
    entry.grid(row=0, column=1, padx=10, pady=5)

# Button to create VLAN labels and entries
    create_button = ctk.CTkButton(master=start_frame, text="Create VLANs", command=create_labels_and_entries)
    create_button.grid(row=0, column=2, padx=10, pady=5)

# entry_label = ctk.CTkLabel(master=frame, text="Enter number of VLANs:")
# entry_label.grid(row=1,column=1,padx=10,pady=5,sticky="w")


# Label to show error messages
    error_label = tk.Label(start_frame, text="",bg="#212121",fg="#f5df33")
    error_label.grid(row=1, column=1, padx=10, pady=5)

# Set a default valu

#creation frame 
    label_frame = ctk.CTkFrame(start_frame,width=0, height=0)
    label_frame.grid(row=2, column=0, columnspan=3, pady=10)
# Label to show error messages
    error_labe4 = tk.Label(start_frame, text="",bg="#212121",fg="#f5df33")
    error_labe4.grid(row=3, column=0, columnspan=3, pady=20)

    drop_frame = ctk.CTkFrame(frame)
    drop_frame.grid(row=4, column=1, columnspan=3, pady=20)

    label1 = ctk.CTkLabel(master=drop_frame, text="VLANs id:")
    label1.grid(row=0, column=0,pady=5)

    combo1 = ctk.CTkOptionMenu(drop_frame, values= vlan_name)
    combo1.grid(row=0, column=1, padx=5,pady=5)
    combo1.set("no vlans")

    label2 = ctk.CTkLabel(master=drop_frame, text="Switch:")
    label2.grid(row=0, column=2,pady=5)

# Create a Combobox for Switch selection
    combo2 = ctk.CTkOptionMenu(drop_frame, values=choices_sw,command=update_choices)
    combo2.grid(row=0, column=3, padx=5,pady=5)

    label3 = ctk.CTkLabel(master=drop_frame, text="Interface:")
    label3.grid(row=1, column=0,pady=5)
# Create a Combobox for Interface selection (populated dynamically based on combo2)
    combo3 = ctk.CTkOptionMenu(drop_frame)
    combo3.grid(row=1, column=1, padx=10)

    x=0
    if x==0:
     combo3.configure(values=choices_int_add["sw1"]) 
     combo3.set(choices_int_add["sw1"][0])
    x+=1 

# Create a button to trigger the function
    label4 = ctk.CTkLabel(master=drop_frame, text="      ")
    label4.grid(row=1, column=2)

    button = ctk.CTkButton(drop_frame, text="Save", command=add_vlanport)
    button.grid(row=1, column=3, padx=10)
# delete vlan
    drop_frame1 = ctk.CTkFrame(frame)
    drop_frame1.grid(row=5, column=1, columnspan=3, pady=20)

    label5 = ctk.CTkLabel(master=drop_frame1, text="vlan: ")
    label5.grid(row=0, column=0,pady=5)

    combo4 = ctk.CTkOptionMenu(drop_frame1, values= vlan_id)
    combo4.grid(row=0, column=1, padx=5)
    combo4.set("no vlans")

    label6 = ctk.CTkLabel(master=drop_frame1, text="         ")
    label6.grid(row=0, column=2,pady=5)

    button5 = ctk.CTkButton(drop_frame1, text="remove", command=remove_vlan)
    button5.grid(row=0, column=3, padx=10)

def protocol ():
    global chicce_entry
    global error_labe2
    new_window = ctk.CTkToplevel(root)
    new_window.title("Window Command")
    new_window.geometry("500x300")
    

    frame = ctk.CTkFrame(new_window)
    frame.pack(pady=20, padx=60, fill="both", expand=True)
    # Set a default value
    entry_label2 = ctk.CTkLabel(
         master=frame, 
         text="Choices  \n1. VTP  \n2. STP (PVST+)    \n3. Ethernet Channel   \n4. STP and Ethernet Channel"
        )
    entry_label2.grid(row=2, column=1, padx=10, pady=10, sticky="w")

# Add the choice entry or a similar widget on the right side
    chicce_entry = ctk.CTkEntry(
         master=frame, 
         placeholder_text="Enter your choice"
        )
    chicce_entry.grid(row=2, column=2, padx=10, pady=10, sticky="w")



# Button to start configuration
    configure_button = ctk.CTkButton(frame, text="Configure Switches",font=('Helvetica', 14), command=configure_switches)
    configure_button.grid(row=3, column=1, columnspan=3, padx=10)

    #error 2
    error_labe2 = tk.Label(frame, text="",bg="#212121",fg="#f5df33")
    error_labe2.grid(row=6, column=2, columnspan=3, pady=10)


def create_labels_and_entries():
    global entry_widget1_list, entry_widget2_list
    global button2
    global button1
    h=0
    # Clear previous widgets and reset arrays
    entry_widget1_list.clear()
    entry_widget2_list.clear()
    try:
      button2.destroy()
    except NameError:
      pass  # button2 does not exist, nothing to do

    try:
     button1.destroy()
    except NameError:
      pass  # button1 does not exist, nothing to do
    label_frame.configure(width=10, height=0)  

    for widget in label_frame.winfo_children():
        widget.destroy()

    
    try:
          
        # if error_label:
        #    error_label.destroy()
        num = int(entry.get()) 
        
        try:
           if error_label:
            # error_label.destroy()
            error_label.config(text="")
        except NameError:
        # error_label hasn't been created yet, so no action needed
           pass

         # Get the number from the entry widget
        for i in range(num):
            h=i
            # Create a label for each VLAN
            label = ctk.CTkLabel(label_frame, text=f" Vlan {i+1}")
            label.grid(row=i, column=0, padx=5, pady=5)

            # Create a corresponding entry for VLAN ID and add to the list
            entry_widget1 = ctk.CTkEntry(label_frame, placeholder_text="Enter VLAN ID")
            entry_widget1.grid(row=i, column=1, padx=5, pady=5)
            entry_widget1_list.append(entry_widget1)  # Store in the list

            # Create a corresponding entry for VLAN Name and add to the list
            entry_widget2 = ctk.CTkEntry(label_frame, placeholder_text="Enter VLAN Name")
            entry_widget2.grid(row=i, column=2, padx=5, pady=5)
            entry_widget2_list.append(entry_widget2)  # Store in the list
            
        if num >0:    
            if vtpflag==0:
                
                button2 = ctk.CTkButton(label_frame, text="Submit", command=create_vlans1)
                button2.grid(pady=5,row=h+1 ,column=1)
            else:
                button1 = ctk.CTkButton(label_frame, text="Submit", command=create_vlans2)
                button1.grid(pady=5,row=h+1, column=2)

        
        
    except ValueError:
        error_label.config(text="Please enter a valid number")
        label_frame.configure(width=10, height=0)  


    #######################################################################4

def create_vlans1():
    
    global windowflage
    if windowflage ==0:  
      open_new_window1()
      windowflage+=1
    # Loop through the lists to get each VLAN ID and VLAN Name
    global vtpflag
    vtpflag += 1

    global vlan_id
    global vlan_name

    vlan_name=[]    
    vlan_id=[]
    
    if  entry_widget2_list[0].get()!='':    
        for i in range(len(entry_widget1_list)):
            vlan_id.append(entry_widget1_list[i].get())  # Store VLAN ID
            vlan_name.append(entry_widget2_list[i].get()) # Get VLAN Name
    

    
   
    duplicate_id = find_duplicates(vlan_id)  
    duplicate_name = find_duplicates(vlan_name)
    
    try:
           if error_labe4:
            # error_label.destroy()
            error_labe4.config(text="")
    except NameError:
        # error_label hasn't been created yet, so no action needed
           pass
    global result2
    result2 = []
    global pingflag
    
    if not duplicate_id and not duplicate_name and not check_integers(vlan_name) and not (check_integers(vlan_name) or not check_integers(vlan_id)) :          

    # Loop to configure each interface as trunk

        try:
            for switch in switchescore:
                net_connect = ConnectHandler(**switch)
                net_connect.enable()
                # Loop through the lists to get each VLAN ID and VLAN Name
                
                for i in range(len(entry_widget1_list)):
                   
                    vlans_commands = [
                        f'vlan {vlan_id[i]}',
                        f'name {vlan_name[i]}'
                        
                    ]
                    result1 = net_connect.send_config_set(vlans_commands)
                    output.insert(tk.END, f'Configured {switch["host"]}:\n{result1}\n')
                net_connect.disconnect()
            
           
        except Exception as e:
             output.insert(tk.END, f'Failed to connect to switches: {e}\n') 
        
        combo1.configure(values=vlan_id)
        combo1.set(vlan_id[0]) 
        word1 ='vlan id:'
        word2 ='vlan name :'
        
        
        result2 = [f"{word1}{a} {word2}{b}" for a, b in zip(vlan_id, vlan_name)]
    
        combo4.configure(values=result2)
        if stpflag != 0:
          primary_split()    

        button2.destroy()
        button3 = ctk.CTkButton(label_frame, text="Submit", command=create_vlans2)
        button3.grid(pady=5, column=2)    

       
    if duplicate_id:
        error_labe4.config(text=f"there are dupplicated vlan{duplicate_id} please enter again")
        vlan_id=[]
        vlan_name=[]

    if duplicate_name:
        error_labe4.config(text=f"there are dupplicated vlan name{duplicate_name} please enter again")
        vlan_id=[]
        vlan_name=[]
    # Loop to configure each interface as trunk
   
    if pingflag != 12 and pingflag != 0 :
          error_labe4.config(text=f" plese check reachability of topology ")
    if result2:
      combo4.set(result2[0])
   
    if ( check_integers(vlan_name) or not vlan_name ) and not check_integers(vlan_id) :
        error_labe4.config(text=f"vlan name should be string and id should be integer")
        vlan_id=[]
        vlan_name=[]
    elif check_integers(vlan_name) or not vlan_name:
        error_labe4.config(text=f"vlan name should be string")
        vlan_id=[]
        vlan_name=[]

    elif not check_integers(vlan_id):
        error_labe4.config(text=f"vlan id should be integer")
        vlan_id=[]
        vlan_name=[]
    
def create_vlans2():
    vlan_id1=[]
    vlan_name1=[]
    global vlan_name
    global vlan_id
    try:
           if error_labe4:
            # error_label.destroy()
            error_labe4.config(text="")
    except NameError:
        # error_label hasn't been created yet, so no action needed
           pass
    for i in range(len(entry_widget1_list)):
          vlan_id.append(entry_widget1_list[i].get())  # Store VLAN ID
          vlan_name.append(entry_widget2_list[i].get()) # Get VLAN Name  # Get VLAN Name if    
    duplicate_idint = find_duplicates(vlan_id)
    duplicate_nameint = find_duplicates(vlan_name)
    
    # if not duplicate_id and not duplicate_name and not check_integers(vlan_name) and not (check_integers(vlan_name) or not check_integers(vlan_id)) :
    if not duplicate_nameint and not duplicate_idint and not (check_integers(vlan_name) or not check_integers(vlan_id)):
        if vlan_id:
           if isinstance(vlan_id, str):
                vlan_id = [vlan_id]  # Convert the string into a list
                
        if vlan_name:
          if isinstance(vlan_name, str):
                vlan_name = [vlan_name]  # Convert the string into a list
            # Append the additional data (array) to vlan_id 
          

        duplicate_id = find_duplicates(vlan_id)  
        duplicate_name = find_duplicates(vlan_name)  
        
    

        if not duplicate_id and not duplicate_name:
            
            combo1.configure(values=vlan_id)
            combo1.set(vlan_id[0])
            
            try:
                global output
                for switch in switchescore:
                  net_connect = ConnectHandler(**switch)
                  net_connect.enable()
                # Loop through the lists to get each VLAN ID and VLAN Name
                
                  for i in range(len(entry_widget1_list)):
                      vlans_commands = [
                        f'vlan {vlan_id[-i-1]}',
                        f'name {vlan_name[-i-1]}'
                        
                    ]
                      result1 = net_connect.send_config_set(vlans_commands)
                      output.insert(tk.END, f'Configured {switch["host"]}:\n{result1}\n')
                  net_connect.disconnect()
                
                global result2
                word1 ='vlan id:'
                word2 ='vlan name :'
                result2 = []
                result2 = [f"{word1}{a} {word2}{b}" for a, b in zip(vlan_id, vlan_name)]
                
                combo4.configure(values=result2)
                combo4.set(result2[0])        
            except Exception as e:
                output.insert(tk.END, 'Failed to connect to switches: {e}\n')     
                return        
            if stpflag != 0:
              primary_split()       
        if duplicate_id:
            # seen = set()
            # vlan_id_without=[]
            # for item in vlan_id:
            #    if item not in seen:
            #         seen.add(item)
            #         vlan_id_without.append(item)
            # vlan_id=vlan_id_without
            print(vlan_id)

        if duplicate_name:
            # print(1)
            # seen = set()
            # vlan_name_without=[]
            # for item in vlan_name:
            #   if item not in seen:
            #         seen.add(item)
            #         vlan_name_without.append(item)
            
            # vlan_name=vlan_name_without
            print(vlan_name)

    print(vlan_name)
    print(vlan_id)        
    if check_integers(vlan_name) or not vlan_name:
        error_labe4.config(text=f"vlan name should be string")
          
    if not check_integers(vlan_id) or duplicate_idint or duplicate_nameint or(check_integers(vlan_name) or not vlan_name):
       vlan_id.pop()
       vlan_name.pop()  
    if not check_integers(vlan_id):
        error_labe4.config(text=f"vlan id should be integer")
         
    if duplicate_idint:
        
        error_labe4.config(text=f"there are dupplicated vlan{duplicate_idint} please enter again")
              
    if duplicate_nameint:    
        error_labe4.config(text=f"there are dupplicated vlan name{duplicate_nameint} please enter again")
        
    

     #countinuo vlan configration
    # label_frame.configure(width=10, height=0)  

#append vlans 
def check_integers(input_array):
    # Try to convert all elements to integers
    for i in range(len(input_array)):
        try:
            # Try converting each element to an integer
            int(input_array[i])
        except ValueError:
            return False  # Return False as soon as one element fails to convert
    
    return True  # If all elements converted successfully, return True

def find_duplicates(arr):
    seen = set()  # To keep track of seen values
    duplicates = []  # To store duplicates

    for item in arr:
        if item in seen:
            # Append to duplicates if not already added
            if item not in duplicates:
                duplicates.append(item)
        else:
            seen.add(item)  # Otherwise, add to seen set

    return duplicates

def update_choices(event):
    combo3.set('') # Clear current selection in combo3
    combo3.configure(values=choices_int_add[combo2.get()]) 
    combo3.set(choices_int_add[combo2.get()][0]) # Update combo3 with the corresponding values

def add_vlanport():

    global selected_vlan
    selected_vlan = combo1.get()
    selected_switch = combo2.get()
    
   
    try:
        if error_labe3:
            error_labe3.config(text="")
            # error_label.destroy()
    except NameError:
        # error_label hasn't been created yet, so no action needed
        pass

   

    if not selected_switch:
        error_labe3 = tk.Label(drop_frame, text="",bg="#212121",fg="#f5df33")
        error_labe3.grid(column=1)
        error_labe3.config(text="Please enter a valid switch")
    
    if not selected_vlan:
        error_labe3 = tk.Label(drop_frame, text="",bg="#212121",fg="#f5df33")
        error_labe3.grid(column=1)
        error_labe3.config(text="Please enter a valid vlan")

    
    if not combo3.get():
        error_labe3 = tk.Label(drop_frame, text="",bg="#212121",fg="#f5df33")
        error_labe3.grid(column=1)
        error_labe3.config(text="Please enter a valid interface")      

    x=0
    
    if selected_switch == "sw1": 
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.9',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw2":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.10',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw3":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.11',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw4":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.12',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw5":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.13',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw6":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.6',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw7":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.7',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw8":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.8',  'username': 'project','password': 'pro123',},] 
    
    else:
        error_labe3 = tk.Label(drop_frame, text="",bg="#212121",fg="#f5df33")
        error_labe3.grid(column=1)
        error_labe3.config(text="Please enter a valns at first ")
        x+=1
    
    if x==0:
        global output
        selected_interface = combo3.get() 
        for switch in chochoice:
            output.insert(tk.END, f'Connecting to {switch["host"]}...\n')
            connection = ConnectHandler(**switch)
            output.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')

            command_vlan = [
                f'int {selected_interface}',
                'switchport mode access',
                f'switchport access vlan {selected_vlan}'

                            
                            ]

            result1 = connection.send_config_set(command_vlan)
            output.insert(tk.END, f'Configured {switch["host"]}:\n{result1}\n')

            connection.disconnect()                          

        selected_option = combo3.get()  # Get the selected option
        
        x=-1
        y=-1
        h=0
        
        append_interface(f'{selected_vlan}',f'{selected_switch}',f'{selected_option}',choices_int_dhcp2)
        append_interface(f'{selected_vlan}',f'{selected_switch}',f'{selected_option}',choices_int_dhcplink)    
        append_interface(f'{selected_vlan}',dhcp_vlan)  

        for i in range(len(choices_int_add[f"{selected_switch}"])):
            
            if choices_int_add[f"{selected_switch}"][i]==selected_option:
                x=i
       
        if x != -1:

            choices_int_add[f"{selected_switch}"].remove( choices_int_add[f"{selected_switch}"][x])  # Remove the selected option from the list
            if choices_int_add[f"{selected_switch}"]:
              combo3['values'] = choices_int_add[f"{selected_switch}"]  # Update the ComboBox values
              combo3.set(choices_int_add[f"{selected_switch}"][0])  # Reset the ComboBox to be empty
              combo3.configure(values=choices_int_add[f"{selected_switch}"])             
            else:
                combo3.set("no interfaces")
                     
        if  not choices_int_add[f"{selected_switch}"]:
           for i in range(len(choices_sw)):
           
            if choices_sw[i]==selected_switch:
                y=i
               
           choices_sw.remove(choices_sw[y])
           
           combo2['values'] = choices_sw  # Update the ComboBox values
           combo2.set(choices_sw[0])  # Reset the ComboBox to be empty
           combo3.set(choices_sw[0][0])
        
        if  not choices_int_add:
             combo2.set("no switches")
             combo3.set("no Interfaces")  
        
        global result2
        word1 ='vlan id:'
        word2 ='vlan name :'
        result2 = []
        result2 = [f"{word1}{a} {word2}{b}" for a, b in zip(vlan_id, vlan_name)]
    
        combo4.configure(values=result2)
        combo4.set(result2[0])    

def append_interface(vlan, switch, new_interface,choices_int):
    """
    Append a new interface to the given switch under the specified VLAN.
    """
    # Check if the VLAN exists
    if vlan in choices_int:
        # Check if the switch exists within the VLAN
        if switch in choices_int[vlan]:
            # Append the new interface to the list of interfaces for the given switch
            choices_int[vlan][switch].append([new_interface])  # Append as a new list inside the 3D structure
            
        else:
            choices_int[vlan][switch] = [[new_interface]]
          
    else:
        choices_int[vlan] = {switch: [[new_interface]]}
        for switch1 in switch_dhcp:
        
            if switch1 != switch: 
                choices_int_dhcp2[vlan] = {switch1: [[]]}
           

def primary_split():
    global switch1_vlans
    global switch2_vlans
    global vtpflag
    global windowflage
    global stpflag
    x=1
    if vtpflag == 0 and windowflage == 0:
       open_new_window1()
       windowflage +=1
                                                                                     
    switch1_vlans, switch2_vlans = split_vlans(vlan_id)
    if  vlan_id :
           
            commands=[]
            for root_primary in switchesdistr:
                
                if x==1:
                #   commands = [f'spanning-tree vlan {" , ".join(map(str, switch1_vlans))} root primary']
                   for i in range(len(switch1_vlans)):
                     commands.append(f'spanning-tree vlan {switch1_vlans[i]} root primary')
                   x+=1
                else:
                    commands=[]
                    for i in range(len(switch2_vlans)):
                     commands.append(f'spanning-tree vlan {switch2_vlans[i]} root primary')

                try:
                   global output
                   connection = ConnectHandler(**root_primary)
                   resu = connection.send_config_set(commands)
                   output.insert(tk.END,f"Output for {root_primary['host']}:\n{resu}\n")
                except Exception as e:
                    output.insert(tk.END,f"Failed to connect to {root_primary['host']}: {e}")
                finally:
                  connection.disconnect() 

def split_vlans(vlans):
    mid = len(vlans) // 2
    if len(vlans) % 2 == 0:
        return vlans[:mid], vlans[mid:]  # Even: split evenly
    else:
        return vlans[:mid], vlans[mid:]   # Odd: first switch gets the smaller half

def remove_vlan():
    global vlan_id
    global vlan_name
    global result2
    remelement = combo4.get()
    if vlan_id:
        
        for i in range(len(vlan_id)):
                if result2[i]==remelement:
                    x=i
       
                   
        remove_vlanel=int(vlan_id[x])
        for switch in switch_dhcp :

          if remove_vlanel in choices_int_dhcp2:
        # Check if the switch exists within the specified VLAN
            if switch in choices_int_dhcp2[remove_vlanel]:
            # If the switch exists, remove the interfaces (if needed)
              if choices_int_dhcp2[remove_vlanel][switch]:
                    choices_int_add[f'{switch}'].append(choices_int_dhcp2 [f'{remove_vlanel}'][f'{switch}'])
                    combo3['values'] = choices_int_add[f"{switch}"]  # Update the ComboBox values
                    combo3.configure(values=choices_int_add[f"{switch}"])  
                    if combo2.get ==switch :
                        combo3.set(choices_int_add[f"{switch}"][0])  # Reset the ComboBox to be empty
            else:
                    choices_sw.append(switch)
                    choices_int_add[f'{switch}'].append(choices_int_dhcp2 [f'{remove_vlanel}'][f'{switch}'])
                    combo3['values'] = choices_int_add[f"{switch}"]  # Update the ComboBox values
                    if combo2.get ==switch :
                        combo3.set(choices_int_add[f"{switch}"][0])  # Reset the ComboBox to be empty
        
        del choices_int_dhcp2[f'{remove_vlanel}']
        vlan_name.remove(vlan_name[x])  
        vlan_id.remove(vlan_id[x])
        result2.remove(result2[x])
        global stpflag
        if stpflag != 0:
          primary_split()


        # result2 = [f"{word1}{a} {word2}{b}" for a, b in zip(vlan_id, vlan_name)]
        if result2:
           combo4.configure(values=result2)
           combo1.configure(values=vlan_id)
           combo4.set(result2[0])
           combo1.set(vlan_id[0])
        else: 
           novvalns=["no vlans"] 
           combo4.configure(values=novvalns)
           combo1.configure(values=novvalns)
        
           combo4.set(novvalns[0])
           combo1.set(novvalns[0])
        
        
        try:
                global output
                for switch in switchescore:
                  net_connect = ConnectHandler(**switch)
                  net_connect.enable()
                # Loop through the lists to get each VLAN ID and VLAN Name
                
                  for i in range(len(entry_widget1_list)):
                    vlans_commands = [
                        f'no vlan {remove_vlanel}'
                        
                    ]
                    result1 = net_connect.send_config_set(vlans_commands)
                    output.insert(tk.END, f'Configured {switch["host"]}:\n{result1}\n')
                  net_connect.disconnect()   
                
        except Exception as e:
             output.insert(tk.END, 'Failed to connect to switches: {e}\n')
             return 

def generate_switch_config(choices_sw, choices_int):
    configs = []
    for switch in choices_sw:
        global output
        configs.append(f"Configure {switch}:")
        for interface in choices_int[switch]:
            configs.append(f"  interface {interface}")
            configs.append("    switchport mode access")
        configs.append("")  # Add a blank line for readability
    return "\n".join(configs)

def configure_switches():
    global vtpflag
    global windowflage
    global stpflag
    if vtpflag == 0 and windowflage == 0:
       open_new_window1()
       windowflage +=1
        # Now you can send commands to the switches using this data
    try:
           global output
           if error_labe2:
              error_labe2.config(text="")
            #  error_labe2.destroy()
    except NameError:
        # error_label hasn't been created yet, so no action needed
           pass
    
    choice = chicce_entry.get()

    if choice == "1":
        for switch in switches1:
        
            try:
                
                if switch in switchescore:
                    net_connect = ConnectHandler(**switch)
                    net_connect.enable()
                # VTP Configuration commands
                    vtp_commands = [
                'vtp domain BestTeam',  # Replace with your VTP domain
                'vtp mode server',              # Or 'client' if you're configuring a VTP client
            # 'vtp password YOUR_VTP_PASSWORD'  # Replace with your VTP password
            ]
            # Send VTP commands to the switch
                    result = net_connect.send_config_set(vtp_commands)
                    output.insert(tk.END, f'Configured {result}\n')
             
                    net_connect.disconnect()
                else:
                    net_connect = ConnectHandler(**switch)
                    net_connect.enable()
                # VTP Configuration commands
                    vtp_commands = [
                'vtp domain BestTeam',  # Replace with your VTP domain
                'vtp mode client',              # Or 'client' if you're configuring a VTP client
            # 'vtp password YOUR_VTP_PASSWORD'  # Replace with your VTP password
            ]
            # Send VTP commands to the switch
                    resu = net_connect.send_config_set(vtp_commands)
                    output.insert(tk.END, f'Configured {resu}\n')
                    # print(output
            # Disconnect SSH session
                    net_connect.disconnect()
            except Exception as e:
                    output.insert(tk.END, f'Failed to connect to {switch["host"]}: {e}\n')
                    return

        
    if choice == "2":
           # switch1_vlans, switch2_vlans = split_vlans(vlan_id)
        stpflag +=1
       
        if  vlan_id :
            
            primary_split()
            for mode_pvst in sw_111:
               commands = ['spanning-tree mode pvst']
           
               try:
                  connection = ConnectHandler(**mode_pvst)
                  res = connection.send_config_set(commands)
                  output.insert(tk.END,f"Output for {mode_pvst['host']}:\n{res}\n")
               except Exception as e:
                  output.insert(tk.END, f"Failed to connect to {mode_pvst['host']}: {e}\n")
                  return               
               finally:
                 connection.disconnect()   
# sw1-sw5 >>
            global_commands = [
                    'errdisable recovery interval 30',
                    'errdisable recovery cause bpduguard'
                ]



# Loop through each device to configure
            for device in swacsess111:
                i=0
                interface_commands = []
                interface_range =choices_int_add[choices_sw[i]]
                i+=1
                if i==4:
                    break
                try:
                   connection = ConnectHandler(**device)
        
            # Send global commands
                   resu = connection.send_config_set(global_commands)
                   output.insert(tk.END,f"Global Configuration Output for {device['host']}:\n{resu}")

                   interface_commands = []
                   for interface in interface_range:
                                # interfacecommand=[
                                #     f'interface {interface}',
                                #     'spanning-tree portfast'
                                #     'spanning-tree bpduguard enable'
                                # ]

                                interface_commands.append(f'interface {interface}')
                                interface_commands.append('spanning-tree portfast')
                                interface_commands.append('spanning-tree bpduguard enable')
                        # Send interface commands
                   res = connection.send_config_set(interface_commands)
                   output.insert(tk.END,f"Interface Configuration Output for {device['host']}:\n{res}")

                   

                except Exception as e:
                     output.insert(tk.END,f"Failed to connect to {device['host']}: {e}")
                     return
                finally:
                     connection.disconnect()  

        else :
          error_labe2.config(text="there is no vlans")   

            
    if choice == "3":
        n = 1
        try:
               for switch in switchesdistr:
                 output.insert(tk.END, f'Connecting to {switch["host"]}...\n')
                 connection = ConnectHandler(**switch)
                 output.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')
              
                 commands1 = [
                   'int range e1/1-3',
                    'channel-group 1 mode desir',
                    'exit',
                    f'int port {n}',
                    'shutd',
                    'exit',
                   
                ]
                 n+=1
                 if n==3:
                   n=0

                 result2 = connection.send_config_set(commands1)
                 output.insert(tk.END, f'Configured {switch["host"]}:\n{result2}\n')
                 connection.disconnect()
        except Exception as e:                  
                output.insert(tk.END, f'Failed to connect to {switch["host"]}: {e}\n')   
                return        
        
        n = 1
        try:
            for switch in switchesdistr:
            
               output.insert(tk.END, f'Connecting to {switch["host"]}...\n')
               connection = ConnectHandler(**switch)
               output.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')
               comands2= [
                   f'int port {n}',
                    'no shutd',
                   
               ]
               n+=1
               if n==3:
                   n=0

               result2 = connection.send_config_set(comands2)
               output.insert(tk.END, f'Configured {switch["host"]}:\n{result2}\n')
                    
               connection.disconnect()
        except Exception as e:
                output.insert(tk.END, f'Failed to connect to {switch["host"]}: {e}\n')    
                return 
        n=1
        if vlan_id:
            try:  
                 for switch in switchesdistr:
                   for i in len(vlan_id):
                    output.insert(tk.END, f'Connecting to {switch["host"]}...\n')
                    connection = ConnectHandler(**switch)
                    output.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')
                    commands1 = [
                              
                             f'int port {n}',                    
                             'switchport trunk encapsulation dot1q',
                              f'switchport trunk allowed vlan {vlan_id[i]}',
                              'exit',
                   
                           ]
                    n+=1
                    if n==3:
                      n=0

                    result2 = connection.send_config_set(commands1)
                    output.insert(tk.END, f'Configured {switch["host"]}:\n{result2}\n')
                    connection.disconnect()
            except Exception as e:                  
                          output.insert(tk.END, f'Failed to connect to {switch["host"]}: {e}\n') 
                          return 
    if choice == "4":
        stpflag +=1
       
        if  vlan_id :
            
            primary_split()
            for mode_pvst in sw_111:
               commands = ['spanning-tree mode pvst']
           
               try:
                  connection = ConnectHandler(**mode_pvst)
                  res = connection.send_config_set(commands)
                  output.insert(tk.END,f"Output for {mode_pvst['host']}:\n{res}\n")
               except Exception as e:
                  output.insert(tk.END, f"Failed to connect to {mode_pvst['host']}: {e}\n")
                  return               
               finally:
                 connection.disconnect()   
# sw1-sw5 >>
            global_commands = [
                    'errdisable recovery interval 30',
                    'errdisable recovery cause bpduguard'
                ]



# Loop through each device to configure
            for device in swacsess111:
                i=0
                interface_commands = []
                interface_range =choices_int_add[choices_sw[i]]
                i+=1
                if i==4:
                    break
                try:
                   connection = ConnectHandler(**device)
        
            # Send global commands
                   resu = connection.send_config_set(global_commands)
                   output.insert(tk.END,f"Global Configuration Output for {device['host']}:\n{resu}")

                   interface_commands = []
                   for interface in interface_range:
                                # interfacecommand=[
                                #     f'interface {interface}',
                                #     'spanning-tree portfast'
                                #     'spanning-tree bpduguard enable'
                                # ]

                                interface_commands.append(f'interface {interface}')
                                interface_commands.append('spanning-tree portfast')
                                interface_commands.append('spanning-tree bpduguard enable')
                        # Send interface commands
                   res = connection.send_config_set(interface_commands)
                   output.insert(tk.END,f"Interface Configuration Output for {device['host']}:\n{res}")

                   

                except Exception as e:
                     output.insert(tk.END,f"Failed to connect to {device['host']}: {e}")
                     return
                finally:
                     connection.disconnect()  

        else :
          error_labe2.config(text="there is no vlans")   

        n = 1
        try:
               for switch in switchesdistr:
                 output.insert(tk.END, f'Connecting to {switch["host"]}...\n')
                 connection = ConnectHandler(**switch)
                 output.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')
              
                 commands1 = [
                   'int range e1/1-3',
                    'channel-group 1 mode desir',
                    'exit',
                    f'int port {n}',
                    'shutd',
                    'exit',
                   
                ]
                 n+=1
                 if n==3:
                   n=0

                 result2 = connection.send_config_set(commands1)
                 output.insert(tk.END, f'Configured {switch["host"]}:\n{result2}\n')
                 connection.disconnect()
        except Exception as e:                  
                output.insert(tk.END, f'Failed to connect to {switch["host"]}: {e}\n')   
                return        
        
        n = 1
        try:
            for switch in switchesdistr:
            
               output.insert(tk.END, f'Connecting to {switch["host"]}...\n')
               connection = ConnectHandler(**switch)
               output.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')
               comands2= [
                   f'int port {n}',
                    'no shutd',
                   
               ]
               n+=1
               if n==3:
                   n=0

               result2 = connection.send_config_set(comands2)
               output.insert(tk.END, f'Configured {switch["host"]}:\n{result2}\n')
                    
               connection.disconnect()
        except Exception as e:
                output.insert(tk.END, f'Failed to connect to {switch["host"]}: {e}\n')    
                return 
        n=1
        if vlan_id:
            try:  
                 for switch in switchesdistr:
                   for i in len(vlan_id):
                    output.insert(tk.END, f'Connecting to {switch["host"]}...\n')
                    connection = ConnectHandler(**switch)
                    output.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')
                    commands1 = [
                              
                             f'int port {n}',                    
                             'switchport trunk encapsulation dot1q',
                              f'switchport trunk allowed vlan {vlan_id[i]}',
                              'exit',
                   
                           ]
                    n+=1
                    if n==3:
                      n=0

                    result2 = connection.send_config_set(commands1)
                    output.insert(tk.END, f'Configured {switch["host"]}:\n{result2}\n')
                    connection.disconnect()
            except Exception as e:                  
                          output.insert(tk.END, f'Failed to connect to {switch["host"]}: {e}\n') 
                          return         

    if choice not in ['1', '2', '3', '4']: 
        error_labe2.config(text=" not available ( please choose from the choices 1 2 3 4 ) ") 


# Function to update combo3 choices based on combo2 selection
#Function to check dublication 


def on_select(event):
    selected_value = combo1.get()

def dhcp_spoofing():
    
    
    primary_split()
    try:
        if error_labe_dhcp:
            error_labe_dhcp.config(text="")
            # error_label.destroy()
    except NameError:
        # error_label hasn't been created yet, so no action needed
        pass

    global output

    for vlan in switch2_vlans:  
        i = 0
        for switch in switchesacsess:
       
            if i == 8:
                break
            
            interface_commands = []
            interface_range =choices_int_add[choices_sw[i]]
            i += 1
            output.insert(tk.END, f'Connecting to {switch["host"]}...\n')
            connection = ConnectHandler(**switch)
            output.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')
            
            command_vlan = [
                
                'ip dhcp snooping',
                f'ip dhcp snooping vlan {vlan}' ,
                'no ip dhcp snooping information option ',
                'int e0/1',
                'ip dhcp snooping trust',

                                       ]
            for interface in interface_range:
                                # interfacecommand=[
                                #     f'interface {interface}',
                                #     'spanning-tree portfast'
                                #     'spanning-tree bpduguard enable'
                                # ]

                                interface_commands.append(f'interface {interface}')
                                interface_commands.append('ip dhcp snooping limit rate 3')
                                interface_commands.append('exit')
                        # Send interface commands
            
            result1 = connection.send_config_set(command_vlan)
            res = connection.send_config_set(interface_commands)
            output.insert(tk.END, f'Configured {switch["host"]}:\n{result1}\n')
            output.insert(tk.END, f'Configured {switch["host"]}:\n{res}\n')

            connection.disconnect()                          
        for vlan in switch1_vlans:  
         
         i = 0
         for switch in switchesacsess:
        
            if i == 9:
                break

            interface_commands = []
            interface_range =choices_int_add[choices_sw[i]]
            i += 1
            output.insert(tk.END, f'Connecting to {switch["host"]}...\n')
            connection = ConnectHandler(**switch)
            output.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')
            
            command_vlan = [
                
                'ip dhcp snooping',
                f'ip dhcp snooping vlan {vlan}' ,
                'no ip dhcp snooping information optaion ',
                'int e0/0',
                'ip dhcp snooping trust',

                                       ]
            for interface in interface_range:
                                # interfacecommand=[
                                #     f'interface {interface}',
                                #     'spanning-tree portfast'
                                #     'spanning-tree bpduguard enable'
                                # ]

                                interface_commands.append(f'interface {interface}')
                                interface_commands.append('ip dhcp snooping limit rate 3')
                                interface_commands.append('exit')
                        # Send interface commands
            
            result1 = connection.send_config_set(command_vlan)
            res = connection.send_config_set(interface_commands)
            output.insert(tk.END, f'Configured {switch["host"]}:\n{result1}\n')
            output.insert(tk.END, f'Configured {switch["host"]}:\n{res}\n')

            connection.disconnect()                          

def seim_solution():
    selected_switch= combo4_dhcp.get()

    if selected_switch == "sw1": 
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.9',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw2":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.10',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw3":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.11',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw4":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.12',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw5":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.13',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw6":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.6',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw7":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.7',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw8":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.8',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "coer1":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.6',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "coer2":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.6',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw_a":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.7',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw_b":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.8',  'username': 'project','password': 'pro123',},]    
    global output
    for switch in chochoice:
            output.insert(tk.END, f'Connecting to {switch["host"]}...\n')
            connection = ConnectHandler(**switch)
            output.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')

            command_vlan = [
                'logging host 192.168.111.128',
                'logging on',

                            ]

            result1 = connection.send_config_set(command_vlan)
            output.insert(tk.END, f'Configured {switch["host"]}:\n{result1}\n')

            connection.disconnect()                          

def port_security():
    global windowflage
    if windowflage ==0:  
      open_new_window1()
      windowflage+=1
    interfaces = ['Ethernet0/0','Ethernet0/1', 'Ethernet0/2', 'Ethernet0/3','Ethernet1/0','Ethernet1/1', 'Ethernet1/2', 'Ethernet1/3','Ethernet2/0']

    global output   
    for switch in switchesdistr:    
        try:
            output.insert(tk.END, f'Connecting to {switch["host"]}...\n')
            connection = ConnectHandler(**switch)
            output.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')

            # Enter enable mode (if required)
            connection.enable()
            for interface in interfaces:
               commands = [
                    f'interface {interface}',     # Enter interface configuration mode
                    'switchport mode trunk',      # Set the interface to trunk mode
                    'switchport trunk allowed vlan all'  # Allow all VLANs on the trunk
                ]
                
                # Send configuration commands to the switch
               res = connection.send_config_set(commands)
               output.insert(tk.END, f'Configured {res}\n')

               connection.disconnect()
        except Exception as e:
                output.insert(tk.END, f'Failed to connect to {switch["host"]}: {e}\n')

    # Loop to configure each interface as trunk

    ##############trunk for core2
        try:
           core2interfaces=['Ethernet0/1', 'Ethernet0/2', 'Ethernet0/3']
           connection = ConnectHandler(**switchescore[1])
    # Enter enable mode (if required)
           connection.enable()
           for interfacee in core2interfaces:
               commands = [
                 f'interface {interfacee}', # Enter interface configuration mode
                 'switchport trunk encapsulation dot1q',    # Set trunk encapsulation to dot1q
                 'switchport mode trunk',      # Set the interface to trunk mode
                 'switchport trunk allowed vlan all'  # Allow all VLANs on the trunk
                ]
        
        # Send configuration commands to the switch
               result = connection.send_config_set(commands)
               output.insert(tk.END, f'Configured {result}\n')
        # Print output to verify the commands were applied


    # Disconnect the SSH session
           connection.disconnect()

        except Exception as e:
                output.insert(tk.END, f'Failed to connect to {switch["host"]}: {e}\n')


        for switch in switchesacsess:
          try:
            connection = ConnectHandler(**switch)

            # Enter enable mode (if required)
            connection.enable()
            i=0
            for interface in choices_int_add[choices_sw[i]]:
                i+=1
                commands = [
                f'interface {interface}', # Enter interface configuration mode
                 ' switchport mode access',  # Allow all VLANs on the trunk
                 'switchport port-security',
                 'switchport port-security maximum 2',
                 'switchport port-security violation shutdown',

            ]
                

            # Send configuration commands to the switch
                result1 = connection.send_config_set(commands)
                output.insert(tk.END, f'Configured {result1}\n')
          except Exception as e:
                output.insert(tk.END, f'Failed to connect to {switch["host"]}: {e}\n')      


          try:        
            switch_config = generate_switch_config(switchesacsess, choices_int_add)
            output.insert(tk.END, f'Configured {switch_config}\n')
          except Exception as e:
                output.insert(tk.END, 'Failed to connect to switches: {e}\n')   
        # Save the configuration changes
           
def window_security():
    # Declare all global variables at the top of the function
    global dhcp_window, combo1_dhcp, error_labe_dhcp, combo4_dhcp

    # Create the DHCP window
    dhcp_window = ctk.CTkToplevel(root)
    dhcp_window.title("security")
    dhcp_window.geometry("800x700")

    frame_dhcp_window = ctk.CTkFrame(dhcp_window)
    frame_dhcp_window.pack(pady=20, padx=60, fill="both", expand=True)

    drop_frame_dhcp = ctk.CTkFrame(frame_dhcp_window)
    drop_frame_dhcp.pack(pady=20)
    
    # Create VLAN combo box based on dhcp_vlan variable
    
        
    combo1_dhcp = ctk.CTkOptionMenu(drop_frame_dhcp, values=vlan_id)
    dhcp_label1 = ctk.CTkLabel(master=drop_frame_dhcp, text="Dhcp security:")
    dhcp_label1.grid(row=0, column=0, padx=10, pady=5)
    button_dhcp = ctk.CTkButton(drop_frame_dhcp, text="save", command=dhcp_spoofing)
    button_dhcp.grid(row=0, column=2, padx=10)
        
    
      

    # Label for errors
    error_labe_dhcp = tk.Label(frame_dhcp_window, text="", bg="#212121", fg="#f5df33")
    error_labe_dhcp.pack()

    drop_frame1_dhcp = ctk.CTkFrame(frame_dhcp_window)
    drop_frame1_dhcp.pack(pady=20)

    combo4_dhcp = ctk.CTkOptionMenu(drop_frame1_dhcp, values=switch1)
    combo4_dhcp.grid(row=0, column=0, padx=10)
    combo4_dhcp.set(switch1[0])
    button5_dhcp = ctk.CTkButton(drop_frame1_dhcp, text="Debugigng", command=seim_solution)
    button5_dhcp.grid(row=0, column=1, padx=10)

    button6_dhcp = ctk.CTkButton(frame_dhcp_window, text="port security", command=port_security)
    button6_dhcp.pack(padx=10)
    
    button7_dhcp = ctk.CTkButton(frame_dhcp_window, text="ARP Protection Tool", command=create_main_window)
    button7_dhcp.pack( pady=10,padx=20)

def create_main_window():
    root2 = ctk.CTkToplevel(root)
    root2.title("ARP Protection Tool")
    root2.geometry("700x600")

    frame = ctk.CTkFrame(root2)
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    output_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=10)
    output_text.pack(pady=10, padx=20, fill='both', expand=True)

    def log_output(message):
        output_text.insert(tk.END, message + "\n")
        output_text.see(tk.END)

    def detect_arp_flooding():
        def flooding_thread():
            try:
                log_output("Detecting ARP Flooding...")
                arp_request_count = {}
                
                while True:
                    try:
                        arp_table = get_arp_table()
                        lines = arp_table.split('\n')
                        
                        for line in lines:
                            parts = line.split()
                            if len(parts) > 1:
                                ip = parts[0]
                                
                                arp_request_count[ip] = arp_request_count.get(ip, 0) + 1
                                
                                if arp_request_count[ip] > 100:
                                    log_output(f"ARP Flooding detected from {ip}")
                                    mitigate_arp_flooding(ip)
                        
                        if len(arp_request_count) > 1000:
                            arp_request_count.clear()
                        
                        time.sleep(30)
                    
                    except Exception as e:
                        log_output(f"Error detecting ARP Flooding: {e}")
            
            except Exception as e:
                log_output(f"General error: {e}")

        threading.Thread(target=flooding_thread, daemon=True).start()

    def detect_arp_cache_poisoning():
        def poisoning_thread():
            try:
                log_output("Detecting ARP Cache Poisoning...")
                arp_cache = {}
                
                while True:
                    try:
                        arp_table = get_arp_table()
                        lines = arp_table.split('\n')
                        
                        for line in lines:
                            parts = line.split()
                            if len(parts) > 2:
                                ip = parts[0]
                                mac = parts[2]
                                
                                if ip in arp_cache and arp_cache[ip] != mac:
                                    log_output(f"ARP Cache Poisoning detected on {ip}")
                                    log_output(f"Old MAC: {arp_cache[ip]}, New MAC: {mac}")
                                    mitigate_arp_cache_poisoning(ip)
                                
                                arp_cache[ip] = mac
                        
                        time.sleep(30)
                    
                    except Exception as e:
                        log_output(f"Error detecting ARP Cache Poisoning: {e}")
            
            except Exception as e:
                log_output(f"General error: {e}")

        threading.Thread(target=poisoning_thread, daemon=True).start()

    def detect_arp_replay_attack():
        def replay_thread():
            try:
                log_output("Detecting ARP Replay Attack...")
                seen_packets = set()
                
                while True:
                    try:
                        arp_table = get_arp_table()
                        
                        packet_signature = hash(arp_table)
                        
                        if packet_signature in seen_packets:
                            log_output("Potential ARP Replay Attack detected")
                            mitigate_arp_replay_attack()
                        
                        seen_packets.add(packet_signature)
                        
                        if len(seen_packets) > 1000:
                            seen_packets.clear()
                        
                        time.sleep(30)
                    
                    except Exception as e:
                        log_output(f"Error detecting ARP Replay Attack: {e}")
            
            except Exception as e:
                log_output(f"General error: {e}")

        threading.Thread(target=replay_thread, daemon=True).start()

    def mitigate_arp_flooding(ip):
        try:
            log_output(f"Mitigating ARP Flooding from {ip}")
            if subprocess.os.name == 'nt':
                subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule', 
                                f'name=BlockFlooding{ip}', 'dir=in', 'action=block', f'remoteip={ip}'])
            else:
                subprocess.run(['iptables', '-A', 'INPUT', '-p', 'arp', '-s', ip, '-j', 'DROP'])
        except Exception as e:
            log_output(f"Error mitigating ARP Flooding: {e}")

    def mitigate_arp_cache_poisoning(ip):
        try:
            log_output(f"Mitigating ARP Cache Poisoning from {ip}")
            if subprocess.os.name == 'nt':
                subprocess.run(['netsh', 'advfirewall', 'firewall', 'add', 'rule', 
                                f'name=BlockPoisoning{ip}', 'dir=in', 'action=block', f'remoteip={ip}'])
            else:
                subprocess.run(['iptables', '-A', 'INPUT', '-p', 'arp', '-s', ip, '-j', 'DROP'])
        except Exception as e:
            log_output(f"Error mitigating ARP Cache Poisoning: {e}")

    def mitigate_arp_replay_attack():
        try:
            log_output("Mitigating ARP Replay Attack")
            if subprocess.os.name == 'nt':
                subprocess.run(['netsh', 'interface', 'ip', 'reset'])
            else:
                subprocess.run(['systemctl', 'restart', 'networking'])
        except Exception as e:
            log_output(f"Error mitigating ARP Replay Attack: {e}")

    def get_arp_table():
        try:
            result = subprocess.run(
                ['arp', '-a'] if subprocess.os.name == 'nt' else ['arp', '-n'], 
                capture_output=True, 
                text=True
            )
            return result.stdout
        except Exception as e:
            log_output(f"Error retrieving ARP table: {e}")
            return ""

    def configure_switches0():
        def config_thread():
            try:
                log_output("Configuring switches...")
                for switch in switches1:
                    try:
                        log_output(f"Connecting to switch: {switch['host']}")
                        net_connect = ConnectHandler(**switch)
                        net_connect.enable()

                        config_commands = [
                            'ip arp inspection vlan 1-200',
                            'ip arp inspection validate ip',
                            'ip arp inspection limit rate 15'
                        ]

                        result = net_connect.send_config_set(config_commands)
                        log_output(f"Configuration result:\n{result}")

                        net_connect.save_config()
                        log_output("Configuration saved successfully")

                        net_connect.disconnect()
                    except Exception as switch_error:
                        log_output(f"Error configuring switch {switch['host']}: {switch_error}")
            except Exception as e:
                log_output(f"General error: {e}")

        threading.Thread(target=config_thread, daemon=True).start()

    flooding_button = ctk.CTkButton(
        frame, 
        text="Detect ARP Flooding", 
        command=detect_arp_flooding
    )
    flooding_button.pack(pady=5, padx=20, fill='x')

    cache_poisoning_button = ctk.CTkButton(
        frame, 
        text="Detect ARP Cache Poisoning", 
        command=detect_arp_cache_poisoning
    )
    cache_poisoning_button.pack(pady=5, padx=20, fill='x')

    replay_button = ctk.CTkButton(
        frame, 
        text="Detect ARP Replay Attack", 
        command=detect_arp_replay_attack
    )
    replay_button.pack(pady=5, padx=20, fill='x')

    switch_config_button = ctk.CTkButton(
        frame, 
        text="Configure Switches", 
        command=configure_switches
    )
    switch_config_button.pack(pady=5, padx=20, fill='x')

def open_new_window1():
    new_window1 = ctk.CTkToplevel(root)
    new_window1.title("New Window")
    new_window1.geometry("600x500")
    
    label = ctk.CTkLabel(new_window1, text="This is a result window")
    label.pack(pady=20)
    global output
    output = scrolledtext.ScrolledText(master=new_window1, width=60, height=20,bg='black', fg='white', font=('Helvetica', 14))
    output.pack(pady=10)

def open_new_window2():
    new_window2 = ctk.CTkToplevel(root)
    new_window2.title("New Window")
    new_window2.geometry("600x500")
    
    label = ctk.CTkLabel(new_window2, text="This is a check result window")
    label.pack(pady=20)

    label = ctk.CTkLabel(new_window2, text="choocs \n 1-show vlans  \n 2- show vtp \n 3-show stp \n 4-show Ethernet channal ")
    label.pack(pady=20)
         
    drop_frame2 = ctk.CTkFrame(new_window2)
    drop_frame2.pack(pady=20)
    
    global combo5
    combo5 = ctk.CTkOptionMenu(drop_frame2, values= switch1) 
    combo5.grid(row=0, column=0, padx=10)
     
    #choiccs select
    global choice_entry1
    choice_entry1 = ctk.CTkEntry(new_window2, placeholder_text="enter your choice")  
    choice_entry1.pack(pady=10)
     
    global error_labe6
    error_labe6 = tk.Label(new_window2, text="",bg="#212121",fg="#f5df33")
    error_labe6.pack()

    button5 = ctk.CTkButton(new_window2, text="show", command= check_result)
    button5.pack(pady=10 )
    global output1
    output1 = scrolledtext.ScrolledText(master=new_window2, width=60, height=20,bg='black', fg='white', font=('Helvetica', 14))
    output1.pack(pady=10)
                                                
def check_result():

    selected_switch = combo5.get()
    
    if selected_switch == "sw1": 
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.9',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw2":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.10',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw3":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.11',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw4":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.12',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw5":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.13',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw6":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.6',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw7":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.7',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw8":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.8',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "coer1":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.6',  'username': 'project','password': 'pro123',},]
    elif selected_switch == "coer2":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.6',  'username': 'project','password': 'pro123',},]
    elif selected_switch == "sw_a":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.7',  'username': 'project','password': 'pro123',},]
    elif selected_switch == "sw_b":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.8',  'username': 'project','password': 'pro123',},] 
    else:
        error_labe3 = tk.Label(drop_frame, text="",bg="#212121",fg="#f5df33")
        error_labe3.grid(column=1)
        error_labe3.config(text="Please enter a valns at first ")
    choice = choice_entry1.get()

    if choice == "1":
     try:   
        for switch in chochoice:
            output1.insert(tk.END, f'Connecting to {switch["host"]}...\n')
            connection = ConnectHandler(**switch)
            output1.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')
            command_vlan = [
                    'do show vlan',

                                                                ]

            result1 = connection.send_config_set(command_vlan)
            output1.insert(tk.END, f'Configured {switch["host"]}:\n{result1}\n')

            connection.disconnect()  
     except Exception as e:
             output1.insert(tk.END, f'Failed to connect to switches: {e}\n')                          
    elif choice == "2":
     try:   
        for switch in chochoice:
            output1.insert(tk.END, f'Connecting to {switch["host"]}...\n')
            connection = ConnectHandler(**switch)
            output1.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')

            command_vlan = [
                    'do show vtp status',
                    # 'do show vtp vlan',                                   ]
            ]
            result1 = connection.send_config_set(command_vlan)
            output1.insert(tk.END, f'Configured {switch["host"]}:\n{result1}\n')

            connection.disconnect()  
     except Exception as e:
             output1.insert(tk.END, 'Failed to connect to switches: {e}\n')  
    elif choice == "3":
     try:   
        for switch in chochoice:
            output1.insert(tk.END, f'Connecting to {switch["host"]}...\n')
            connection = ConnectHandler(**switch)
            output1.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')

            command_vlan = [
                    'do show running-config | include spanning-tree',
                    'do show spanning-tree'

                                
                                ]

            result1 = connection.send_config_set(command_vlan)
            output1.insert(tk.END, f'Configured {switch["host"]}:\n{result1}\n')

            connection.disconnect()  
     except Exception as e:
             output1.insert(tk.END, f'Failed to connect to switches: {e}\n')                            
    elif choice == "4":
     try:   
        for switch in chochoice:
            output1.insert(tk.END, f'Connecting to {switch["host"]}...\n')
            connection = ConnectHandler(**switch)
            output1.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')

            command_vlan = [
                    'do show etherchannel 1 detail',
                    'do show etherchannel protocol',

                                
                                ]

            result1 = connection.send_config_set(command_vlan)
            output1.insert(tk.END, f'Configured {switch["host"]}:\n{result1}\n')

            connection.disconnect()  
     except Exception as e:
             output1.insert(tk.END, f'Failed to connect to switches: {e}\n')                            
    else:
         error_labe6.config(text="Please enter a valid number")
   
        # Label to show error messag

def window_command():
    global combo6
    global mode_combo
    global entry
    mode_options = ["EXEC Mode", "Configuration Mode"]
    # Create a new window
    new_window = ctk.CTkToplevel(root)
    new_window.title("Window Command")
    new_window.geometry("600x600")
    
    # Create a frame in the new window
    frame = ctk.CTkFrame(new_window)
    frame.pack(padx=10, pady=10, fill="both", expand=True)

    # Create two drop-down menus (OptionMenu)

    combo6= ctk.CTkOptionMenu(frame, values=switch1)
    combo6.grid(row=0, column=1, padx=10)
    combo6.set(switch1[0])

    mode_combo = ctk.CTkOptionMenu(frame, values=mode_options)
    mode_combo.grid(row=0, column=2, padx=10)
    mode_combo.set(mode_options[0])  # Default to User EXEC Mode


    # Create an entry field
    entry= ctk.CTkEntry(frame , width=450)
    entry.grid(row=1, column=1, columnspan=2, padx=50, pady=10)

    # Create a button below the entry field
    button_in_new_window = ctk.CTkButton(frame, text="Submit", command=command_button)
    button_in_new_window.grid(row=2, column=1, columnspan=2, pady=5)

    global output2
    output2 = scrolledtext.ScrolledText(master=new_window, width=60, height=40,bg='black', fg='white', font=('Helvetica', 14))
    output2.pack(pady=10)
      

def command_button():
    global combo6
    global mode_combo
    global windowflage
    global entry
    global entry_command
    global output2
    entry_command = entry.get()

    global selected_switch
    selected_switch = combo6.get()

    if selected_switch == "sw1": 
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.9',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw2":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.10',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw3":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.11',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw4":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.12',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw5":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.13',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw6":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.6',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw7":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.7',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw8":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.8',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "coer1":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.6',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "coer2":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.112.6',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw_a":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.7',  'username': 'project','password': 'pro123',},] 
    elif selected_switch == "sw_b":   
        chochoice=[ {'device_type': 'cisco_ios','host': '192.168.111.8',  'username': 'project','password': 'pro123',},]    
  
    global mode_selected
    mode_selected= mode_combo.get()
    if mode_selected== "EXEC Mode":
            
        try:
            for switch in chochoice:
              output2.insert(tk.END, f'Connecting to {switch["host"]}...\n')
              connection = ConnectHandler(**switch)
              output2.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')

              # The command to be run in EXEC Mode (no 'do' prefix needed)
              command= entry_command

              # Send the command and get the result
              result1 = connection.send_command(command)  # Send the command in EXEC Mode

              output2.insert(tk.END, f'Executed command on {switch["host"]}:\n{result1}\n')

              connection.disconnect()
        except Exception as e:
             output2.insert(tk.END, f'Failed to connect to switches: {e}\n')

     
    if mode_selected == "Configuration Mode":
        try:   
          for switch in chochoice:
            output2.insert(tk.END, f'Connecting to {switch["host"]}...\n')
            connection = ConnectHandler(**switch)
            output2.insert(tk.END, f'Successfully connected to {switch["host"]}.\n')

            command = entry_command

            result1 = connection.send_config_set(command)
            output2.insert(tk.END, f'Configured {switch["host"]}:\n{result1}\n')

            connection.disconnect()  
        except Exception as e:
             output2.insert(tk.END, 'Failed to connect to switches: {e}\n')  


# Create the main window
def main():
    global root 
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()

    root.title("switching  Configurator")
    root.geometry("500x600")

    frame = ctk.CTkFrame(master=root)
    frame.pack(pady=20, padx=60, fill="both", expand=True)

    # --- Top Widgets (Label, Entry, Button) arranged horizontally ---
    # Label for VLAN input

    pingtest_button = ctk.CTkButton(master=frame, text="test connection", command=ping_switches)
    pingtest_button.grid(row=0, column=1, columnspan=3, pady=10)

    button_vlan = ctk.CTkButton(frame, text="vlans", command=all_vlan)
    button_vlan.grid(row=1, column=1, columnspan=3, pady=10)
    button_protocol = ctk.CTkButton(frame, text="protocols", command=protocol)
    button_protocol.grid(row=2, column=1, columnspan=3, pady=10)

    # show outbut scrollebare 
    button7 = ctk.CTkButton(frame, text="output window", command=open_new_window1)
    button7.grid(row=3, column=1, columnspan=3, pady=10)

    #open test configration
    open_window_button2 = ctk.CTkButton(frame, text="test topologey", command=open_new_window2)
    open_window_button2.grid(row=4, column=1, columnspan=3, pady=10)

    #security 
    button6 = ctk.CTkButton(frame, text="security", command=window_security)
    button6.grid(row=5, column=1, columnspan=3, pady=10)


    button7 = ctk.CTkButton(frame, text="commands", command=window_command)
    button7.grid(row=6, column=1, columnspan=3, pady=10 , padx=110)
    # Run the application
    root.mainloop()