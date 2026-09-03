import customtkinter as ctk
import tkinter as tk
from edit1 import RouterConfigurator as file1
import project as file2
from PIL import Image, ImageTk  # Import Pillow for image handling

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def call_file1_main():
    new_window = ctk.CTkToplevel()
    new_window.title("Router Configurator")
    new_window.geometry("1000x800")
    # new_window.resizable(False, False)
    new_window.attributes('-topmost', True)
    new_window.focus_force()
    # new_window.grab_set()
    configurator = file1(new_window)

def call_file2_main():
    file2.main()

# Create the main window
root = ctk.CTk()
root.title("Netmiko ConfigPro")
root.geometry("600x400")
root.resizable(False, False)

# Load and set background image for the main window
image = Image.open("Desktop\p5.jpg")  # Replace with your image path
image = image.resize((600, 400), Image.LANCZOS)  # Resize to match window size
background_image = ImageTk.PhotoImage(image)

# Create a Label to hold the background image
background_label = tk.Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Cover the entire window
background_label.image = background_image  # Keep a reference to prevent garbage collection

# Place buttons above the background
btn1 = ctk.CTkButton(root, text="Router Configurator", command=call_file1_main)
btn1.pack(pady=10)

btn2 = ctk.CTkButton(root, text="Switch Configurator", command=call_file2_main)
btn2.pack(pady=10)

btn_exit = ctk.CTkButton(root, text="Exit", command=root.destroy)
btn_exit.pack(pady=10)

root.mainloop()




# import customtkinter as ctk
# import tkinter as tk
# from edit1 import RouterConfigurator as file1
# import project as file2

# ctk.set_appearance_mode("dark")
# ctk.set_default_color_theme("blue")

# def call_file1_main():
#     new_window = ctk.CTkToplevel()  # Use CTkToplevel instead of tk.Toplevel
#     configurator = file1(new_window)

# def call_file2_main():
#     file2.main()

# root = ctk.CTk()
# root.title("Netmiko ConfigPro")  # Updated title based on prior recommendation
# root.geometry("600x400")
# root.resizable(False, False)

# btn1 = ctk.CTkButton(root, text="Router Configurator", command=call_file1_main)
# btn1.pack(pady=10)

# btn2 = ctk.CTkButton(root, text="Switch Configurator", command=call_file2_main)
# btn2.pack(pady=10)

# btn_exit = ctk.CTkButton(root, text="Exit", command=root.destroy)
# btn_exit.pack(pady=10)

# root.mainloop()



# import customtkinter as ctk
# import tkinter as tk
# from edit1 import RouterConfigurator as file1
# import project as file2

# ctk.set_appearance_mode("dark")
# ctk.set_default_color_theme("blue")

# def call_file1_main():
#     new_window = ctk.CTkToplevel()  # Create a new CTkToplevel window
#     new_window.title("Router Configurator")  # Set a title for clarity
#     new_window.geometry("900x600")  # Match the size from edit1.py
#     new_window.resizable(False, False)  # Optional: Prevent resizing

#     # Ensure the child window stays on top
#     new_window.attributes('-topmost', True)
    
#     # Force focus on the child window
#     new_window.focus_force()
    
#     # Make the child window modal (disables interaction with parent until closed)
#     new_window.grab_set()
    
#     # Create an instance of RouterConfigurator with the new window
#     configurator = file1(new_window)

# def call_file2_main():
#     file2.main()

# root = ctk.CTk()
# root.title("Netmiko ConfigPro")
# root.geometry("600x400")
# root.resizable(False, False)

# btn1 = ctk.CTkButton(root, text="Router Configurator", command=call_file1_main)
# btn1.pack(pady=10)

# btn2 = ctk.CTkButton(root, text="Switch Configurator", command=call_file2_main)
# btn2.pack(pady=10)

# btn_exit = ctk.CTkButton(root, text="Exit", command=root.destroy)
# btn_exit.pack(pady=10)

# root.mainloop()