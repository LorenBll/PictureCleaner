import customtkinter as ctk
import sys
import threading
import time
import os
from PIL import Image, ImageTk
import send2trash


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("PictureCleaner")
        self.geometry("920x595")
        
        # Set minimum window size to accommodate the 800x500 green section
        # 800 (green) + 50 (left sidebar) + 50 (right sidebar) + 20 (padding) = 920px width
        # 500 (green) + 75 (bottom section) + 20 (padding) = 595px height
        self.minsize(920, 595)
        
        # Set maximum window width to 1200 pixels
        self.maxsize(1200, 10000)  # 10000 for height allows unlimited vertical expansion
        
        # Set theme and color
        ctk.set_appearance_mode("system")  # Default system theme
        ctk.set_default_color_theme("blue")  # Blue color theme
        
        # Configure window close behavior
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind ESC key to cancel focus
        self.bind("<Escape>", self.cancel_focus)
        
        # Bind keyboard shortcuts for navigation and deletion
        self.bind("<Key-d>", self.on_key_right_arrow)
        self.bind("<Key-D>", self.on_key_right_arrow)
        self.bind("<Right>", self.on_key_right_arrow)
        
        self.bind("<Key-a>", self.on_key_left_arrow)
        self.bind("<Key-A>", self.on_key_left_arrow)
        self.bind("<Left>", self.on_key_left_arrow)
        
        self.bind("<Key-s>", self.on_key_delete)
        self.bind("<Key-S>", self.on_key_delete)
        self.bind("<Down>", self.on_key_delete)
        
        self.bind("<Key-r>", self.on_key_rotate)
        self.bind("<Key-R>", self.on_key_rotate)
        
        # Make sure the window can receive focus for key events
        self.focus_set()
        
        # Configure grid layout (optional, for future use)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create display layers
        self.create_layers()
        
        # Initialize current image index
        self.current_image_index = 0
        
        # Show the initial layer
        self.show_layer1()
    
    def create_layers(self):
        """
        Create the two display layers as frames
        """
        # Layer 1: Initial layer with input box and button
        self.layer1 = ctk.CTkFrame(self)
        self.layer1.grid(row=0, column=0, sticky="nsew")
        self.layer1.grid_columnconfigure(0, weight=1)
        self.layer1.grid_rowconfigure(0, weight=1)
        self.layer1.grid_rowconfigure(1, weight=0)
        self.layer1.grid_rowconfigure(2, weight=0)
        self.layer1.grid_rowconfigure(3, weight=0)
        self.layer1.grid_rowconfigure(4, weight=0)
        self.layer1.grid_rowconfigure(5, weight=1)
        
        # Input box in the middle
        self.input_box = ctk.CTkEntry(
            self.layer1,
            placeholder_text="Enter text here...",
            width=300,
            height=40
        )
        self.input_box.grid(row=1, column=0, pady=(10, 10), sticky="")
        
        # Checkbox and label frame
        self.checkbox_frame = ctk.CTkFrame(self.layer1, fg_color="transparent")
        self.checkbox_frame.grid(row=2, column=0, pady=(10, 10), sticky="")
        self.checkbox_frame.configure(width=300)
        
        # Recursive checkbox
        self.recursive_checkbox = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="Operate Recursively",
            width=200,
            height=20
        )
        self.recursive_checkbox.pack(anchor="center")
        
        # Error message label below the checkbox
        self.error_label = ctk.CTkLabel(
            self.layer1,
            text="",
            text_color="red",
            width=300,
            height=20
        )
        self.error_label.grid(row=3, column=0, pady=(10, 10), sticky="")
        
        # Button below the error label
        self.main_button = self.create_button(
            self.layer1,
            text="Submit",
            command=self.handle_submit,
            width=300,
            height=40
        )
        self.main_button.grid(row=4, column=0, pady=(10, 10), sticky="")
        
        # Layer 2: Second layer with 4 sections
        self.layer2 = ctk.CTkFrame(self)
        self.layer2.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid layout for 3 columns and 2 rows
        self.layer2.grid_columnconfigure(0, weight=0, minsize=50)  # Left sidebar - fixed 50px
        self.layer2.grid_columnconfigure(1, weight=1)              # Middle section (expandable)
        self.layer2.grid_columnconfigure(2, weight=0, minsize=50)  # Right sidebar - fixed 50px
        self.layer2.grid_rowconfigure(0, weight=1)                 # Top row (expandable)
        self.layer2.grid_rowconfigure(1, weight=0, minsize=75)     # Bottom row - fixed 75px
        
        # Left sidebar (spans both rows) - fixed 50px width
        self.left_sidebar = ctk.CTkFrame(self.layer2, width=50)
        self.left_sidebar.grid(row=0, column=0, rowspan=2, sticky="ns", padx=5, pady=5)
        self.left_sidebar.grid_propagate(False)  # Prevent resizing
        
        # Configure left sidebar grid for centering
        self.left_sidebar.grid_columnconfigure(0, weight=1)
        self.left_sidebar.grid_rowconfigure(0, weight=1)
        
        # Load left arrow icon
        try:
            left_arrow_icon = ctk.CTkImage(
                light_image=Image.open("resources/images/arrow-92-64.ico"),
                dark_image=Image.open("resources/images/arrow-92-64.ico"),
                size=(24, 24)
            )
        except Exception as e:
            left_arrow_icon = None
        
        # Left sidebar button (centered)
        self.left_button = self.create_button(
            self.left_sidebar,
            text="◀" if left_arrow_icon is None else "",
            image=left_arrow_icon,
            command=self.on_left_arrow_click,
            width=40,
            height=40
        )
        self.left_button.grid(row=0, column=0, sticky="")
        
        # Right sidebar (spans both rows) - fixed 50px width
        self.right_sidebar = ctk.CTkFrame(self.layer2, width=50)
        self.right_sidebar.grid(row=0, column=2, rowspan=2, sticky="ns", padx=5, pady=5)
        self.right_sidebar.grid_propagate(False)  # Prevent resizing
        
        # Configure right sidebar grid for centering
        self.right_sidebar.grid_columnconfigure(0, weight=1)
        self.right_sidebar.grid_rowconfigure(0, weight=1)
        
        # Load right arrow icon
        try:
            right_arrow_icon = ctk.CTkImage(
                light_image=Image.open("resources/images/arrow-28-64.ico"),
                dark_image=Image.open("resources/images/arrow-28-64.ico"),
                size=(24, 24)
            )
        except Exception as e:
            right_arrow_icon = None
        
        # Right sidebar button (centered)
        self.right_button = self.create_button(
            self.right_sidebar,
            text="▶" if right_arrow_icon is None else "",
            image=right_arrow_icon,
            command=self.on_right_arrow_click,
            width=40,
            height=40
        )
        self.right_button.grid(row=0, column=0, sticky="")
        
        # Top middle section - green display area with minimum size
        self.green_section = ctk.CTkFrame(self.layer2, width=800, height=500)
        self.green_section.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.green_section.grid_propagate(False)  # Prevent resizing
        
        # Configure green section grid for centering image and labels
        self.green_section.grid_columnconfigure(0, weight=1)
        self.green_section.grid_rowconfigure(0, weight=1)  # Image display area
        self.green_section.grid_rowconfigure(1, weight=0)  # Image name label area
        
        # Add image display label in the green section
        self.image_label = ctk.CTkLabel(
            self.green_section,
            text="No image selected",
            font=("Arial", 16),
            text_color="white"
        )
        self.image_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        
        # Add image name label below the image (without extension)
        self.image_name_label = ctk.CTkLabel(
            self.green_section,
            text="",
            font=("Arial", 14, "bold"),
            text_color="white"
        )
        self.image_name_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        # Bottom middle section - fixed 75px height
        self.bottom_middle = ctk.CTkFrame(self.layer2, height=75)
        self.bottom_middle.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.bottom_middle.grid_propagate(False)  # Prevent resizing
        
        # Configure bottom middle grid for centering 2 buttons horizontally
        self.bottom_middle.grid_columnconfigure(0, weight=1)
        self.bottom_middle.grid_columnconfigure(1, weight=0)
        self.bottom_middle.grid_columnconfigure(2, weight=0)
        self.bottom_middle.grid_columnconfigure(3, weight=1)
        self.bottom_middle.grid_rowconfigure(0, weight=1)
        
        # Add delete button centered in the bottom section
        # Load icon images
        try:
            trash_icon = ctk.CTkImage(
                light_image=Image.open("resources/images/trash-10-64.ico"),
                dark_image=Image.open("resources/images/trash-10-64.ico"),
                size=(20, 20)
            )
        except Exception as e:
            # Fallback to text if images can't be loaded
            trash_icon = None
        
        # Try to load rotate icon (you can add rotate-64.ico as a rotate icon)
        try:
            rotate_icon = ctk.CTkImage(
                light_image=Image.open("resources/images/rotate-64.ico"),
                dark_image=Image.open("resources/images/rotate-64.ico"),
                size=(20, 20)
            )
        except Exception as e:
            # Fallback to text if images can't be loaded
            rotate_icon = None
        
        self.bottom_button1 = self.create_button(
            self.bottom_middle,
            text="🗑️" if trash_icon is None else "",
            image=trash_icon,
            command=self.on_delete_click,
            fg_color="red",
            hover_color="darkred",
            width=80,
            height=30
        )
        self.bottom_button1.grid(row=0, column=1, padx=5, sticky="")
        
        # Add rotate button
        self.bottom_button2 = self.create_button(
            self.bottom_middle,
            text="🔄" if rotate_icon is None else "",
            image=rotate_icon,
            command=self.on_rotate_click,
            width=80,
            height=30
        )
        self.bottom_button2.grid(row=0, column=2, padx=5, sticky="")
        
        # Hide layer 2 initially
        self.layer2.grid_remove()
    
    def show_layer1(self):
        """
        Show layer 1 and hide layer 2
        """
        self.layer2.grid_remove()
        self.layer1.grid(row=0, column=0, sticky="nsew")
    
    def show_layer2(self):
        """
        Show layer 2 and hide layer 1
        """
        self.layer1.grid_remove()
        self.layer2.grid(row=0, column=0, sticky="nsew")
    
    def create_button(self, parent, text, command=None, **kwargs):
        """
        Method for creating buttons with consistent styling
        
        Args:
            parent: Parent widget to place the button in
            text (str): Button text
            command (callable): Function to call when button is clicked
            **kwargs: Additional keyword arguments for button customization
            
        Returns:
            ctk.CTkButton: Created button instance
        """
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            **kwargs
        )
        return button
    
    def cancel_focus(self, event=None):
        """
        Cancel focus on any focused widget when ESC is pressed
        
        Args:
            event: The key event (ESC key press)
        """
        # Remove focus from the currently focused widget
        self.focus_set()
    
    def on_key_right_arrow(self, event=None):
        """
        Handle D key, right arrow key presses - navigate to next image
        Only active when layer 2 is shown
        
        Args:
            event: The key event
        """
        # Only process if layer 2 is active (image viewing mode)
        if hasattr(self, 'layer2') and self.layer2.winfo_viewable():
            self.on_right_arrow_click()
    
    def on_key_left_arrow(self, event=None):
        """
        Handle A key, left arrow key presses - navigate to previous image
        Only active when layer 2 is shown
        
        Args:
            event: The key event
        """
        # Only process if layer 2 is active (image viewing mode)
        if hasattr(self, 'layer2') and self.layer2.winfo_viewable():
            self.on_left_arrow_click()
    
    def on_key_delete(self, event=None):
        """
        Handle S key press - delete current image
        Only active when layer 2 is shown
        
        Args:
            event: The key event
        """
        # Only process if layer 2 is active (image viewing mode)
        if hasattr(self, 'layer2') and self.layer2.winfo_viewable():
            self.on_delete_click()
    
    def on_key_rotate(self, event=None):
        """
        Handle R key press - rotate current image 90° clockwise
        Only active when layer 2 is shown
        
        Args:
            event: The key event
        """
        # Only process if layer 2 is active (image viewing mode)
        if hasattr(self, 'layer2') and self.layer2.winfo_viewable():
            self.on_rotate_click()
    
    def display_error(self, label, message, duration=3):
        """
        Display an error message in the specified label for a given duration
        
        Args:
            label (ctk.CTkLabel): The label widget to display the error in
            message (str): The error message to display
            duration (int): Time in seconds to display the error (default: 3)
        """
        def clear_error():
            time.sleep(duration)
            label.configure(text="")
        
        # Display the error message immediately
        label.configure(text=message)
        
        # Start a thread to clear the error after the specified duration
        threading.Thread(target=clear_error, daemon=True).start()
    
    def update_navigation_buttons(self, current_item_path):
        """
        Update the state of navigation buttons based on current item position
        
        Args:
            current_item_path (str): Path to the currently displayed item
        """
        if not hasattr(self, 'directory_images') or not self.directory_images:
            # No images available, gray out both buttons
            self.left_button.configure(fg_color="gray", hover_color="gray")
            self.right_button.configure(fg_color="gray", hover_color="gray")
            return
        
        try:
            # Find the current item's index in the list
            current_index = self.directory_images.index(current_item_path)
            self.current_image_index = current_index
            
            # Check if there's a previous item
            if current_index <= 0:
                # No previous item, gray out left button
                self.left_button.configure(fg_color="gray", hover_color="gray")
            else:
                # There is a previous item, enable left button with normal colors
                self.left_button.configure(fg_color=("#3B8ED0", "#1F6AA5"), hover_color=("#36719F", "#144870"))
            
            # Check if there's a next item
            if current_index >= len(self.directory_images) - 1:
                # No next item, gray out right button
                self.right_button.configure(fg_color="gray", hover_color="gray")
            else:
                # There is a next item, enable right button with normal colors
                self.right_button.configure(fg_color=("#3B8ED0", "#1F6AA5"), hover_color=("#36719F", "#144870"))
                
        except ValueError:
            # Current item not found in list, gray out both buttons
            self.left_button.configure(fg_color="gray", hover_color="gray")
            self.right_button.configure(fg_color="gray", hover_color="gray")
    
    def pre_button_execution(self, current_item_path):
        """
        Function to run before executing any button action
        Updates navigation button states based on current item position
        
        Args:
            current_item_path (str): Path to the currently displayed item
        """
        self.update_navigation_buttons(current_item_path)

    def list_images(self, directory_path, recursive=False):
        """
        List viewable image files in the specified directory
        
        Args:
            directory_path (str): Path to the directory to list files from
            recursive (bool): Whether to list files recursively in subdirectories
            
        Returns:
            list: List of viewable image file paths (absolute paths)
        """
        try:
            # Get all items in the directory
            all_items = os.listdir(directory_path)
            
            # Separate files and folders with absolute paths
            files = []
            folders = []
            
            for item in all_items:
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    # Skip files that contain "desktop.ini" in their name
                    if "desktop.ini" not in item.lower():
                        files.append(item_path)  # Add absolute path
                elif os.path.isdir(item_path):
                    folders.append(item_path)  # Add absolute path
            
            if not recursive:
                # If not recursive, filter to only viewable images
                images = [f for f in files if self.is_image_or_video(f)]
                return images
            else:
                # If recursive, process folders and add their contents
                for folder in folders:
                    # Recursively get files from each folder
                    folder_files = self.list_images(folder, recursive=True)
                    # Add all files from the folder to the original list
                    files.extend(folder_files)
                
                # Filter to only viewable images
                images = [f for f in files if self.is_image_or_video(f)]
                return images
                
        except PermissionError:
            raise PermissionError("Permission denied accessing directory")
        except Exception as e:
            raise Exception(f"Error accessing directory: {str(e)}")
    
    def handle_submit(self):
        """
        Handle the submit button click - validate directory and switch layers
        """
        # Run pre-execution function if there's a current image
        if hasattr(self, 'current_image_path') and self.current_image_path:
            self.pre_button_execution(self.current_image_path)
        
        # Get the directory path from the input box
        directory_path = self.input_box.get().strip()
        
        # Check if input is empty
        if not directory_path:
            self.display_error(self.error_label, "Please enter a directory path")
            return
        
        # Check if directory exists
        if not os.path.exists(directory_path):
            self.display_error(self.error_label, "Directory does not exist")
            return
        
        # Check if path is actually a directory
        if not os.path.isdir(directory_path):
            self.display_error(self.error_label, "Path is not a directory")
            return
        
        # Check read, write, and execute permissions
        if not os.access(directory_path, os.R_OK):
            self.display_error(self.error_label, "Cannot read from directory")
            return
        
        if not os.access(directory_path, os.W_OK):
            self.display_error(self.error_label, "Cannot write to directory")
            return
        
        if not os.access(directory_path, os.X_OK):
            self.display_error(self.error_label, "Cannot execute in directory")
            return
        
        # Try to list files in the directory
        try:
            # Check if recursive operation is enabled
            is_recursive = self.recursive_checkbox.get()
            
            # Get files using the dedicated function
            images = self.list_images(directory_path, is_recursive)
            
            # Check if the files list is empty
            if not images:
                self.display_error(self.error_label, "The directory has no images. Activate the Recursive Option if the images are in sub-directories")
                return
            
            self.directory_images = images
            self.current_directory = directory_path
            self.current_image_index = 0
            self.current_image_path = images[0] if images else None
            
            # If all checks pass, switch to second layer
            self.show_layer2()
            
            # Load and display the first media file
            self.load_first_media_file()
            
        except PermissionError:
            self.display_error(self.error_label, "Permission denied accessing directory")
        except Exception as e:
            self.display_error(self.error_label, f"Error accessing directory: {str(e)}")
    
    def on_left_arrow_click(self):
        """
        Handle left arrow button click - navigate to previous image
        """
        if hasattr(self, 'directory_images') and self.directory_images and hasattr(self, 'current_image_path'):
            # Run pre-execution function
            self.pre_button_execution(self.current_image_path)
            
            # Navigate to previous image
            if self.current_image_index > 0:
                self.current_image_index -= 1
                previous_image_path = self.directory_images[self.current_image_index]
                self.display_file_info(previous_image_path)
        else:
            pass  # No images available for navigation
    
    def on_right_arrow_click(self):
        """
        Handle right arrow button click - navigate to next image
        """
        if hasattr(self, 'directory_images') and self.directory_images and hasattr(self, 'current_image_path'):
            # Run pre-execution function
            self.pre_button_execution(self.current_image_path)
            
            # Navigate to next image
            if self.current_image_index < len(self.directory_images) - 1:
                self.current_image_index += 1
                next_image_path = self.directory_images[self.current_image_index]
                self.display_file_info(next_image_path)
        else:
            pass  # No images available for navigation
    
    def on_delete_click(self):
        """
        Handle delete button click - move current image to trash and navigate to next
        """
        if hasattr(self, 'directory_images') and self.directory_images and hasattr(self, 'current_image_path'):
            # Run pre-execution function
            self.pre_button_execution(self.current_image_path)
            
            try:
                # Move current image to trash
                send2trash.send2trash(self.current_image_path)
                
                # Remove the image from the list
                self.directory_images.remove(self.current_image_path)
                
                # Check if there are any images left
                if not self.directory_images:
                    # No images left, return to first layer
                    self.input_box.delete(0, 'end')  # Clear input box
                    self.display_error(self.error_label, "All images and videos were cleared")
                    self.show_layer1()
                    return
                
                # Adjust current index if it's beyond the new list size
                if self.current_image_index >= len(self.directory_images):
                    self.current_image_index = len(self.directory_images) - 1
                
                # Display the next image (or the last one if we were at the end)
                next_image_path = self.directory_images[self.current_image_index]
                self.display_file_info(next_image_path)
                
            except Exception as e:
                # You could add error handling here if needed
                pass
                
        else:
            pass  # No images available for deletion
    
    def on_rotate_click(self):
        """
        Handle rotate button click - rotate current image 90° clockwise
        """
        if hasattr(self, 'directory_images') and self.directory_images and hasattr(self, 'current_image_path'):
            # Run pre-execution function
            self.pre_button_execution(self.current_image_path)
            
            try:
                # Check if the file is an image (not a video)
                if not self.is_image_file(self.current_image_path):
                    return  # Skip rotation for non-image files
                
                # Open the image
                image = Image.open(self.current_image_path)
                
                # Rotate the image 90 degrees clockwise
                rotated_image = image.rotate(-90, expand=True)
                
                # Save the rotated image, overwriting the original
                rotated_image.save(self.current_image_path)
                
                # Refresh the display to show the rotated image
                self.display_file_info(self.current_image_path)
                
            except Exception as e:
                # Handle any errors during rotation
                pass
                
        else:
            pass  # No images available for rotation
    
    def on_closing(self):
        """
        Handle window close event - shuts down the entire application
        """
        self.quit()
        self.destroy()
        sys.exit()
    
    def display_image_or_video(self, image_path):
        """Display an image in the green section, resized to fit."""
        try:
            # Open and resize the image to fit the green section
            image = Image.open(image_path)
            
            # Calculate the maximum size that fits in the green section
            max_width = 780  # 800 - 20 for padding
            max_height = 480  # 500 - 20 for padding
            
            # Calculate the aspect ratio
            aspect_ratio = image.width / image.height
            
            # Determine the new size while maintaining aspect ratio
            if aspect_ratio > max_width / max_height:
                # Image is wider, fit to width
                new_width = max_width
                new_height = int(max_width / aspect_ratio)
            else:
                # Image is taller, fit to height
                new_height = max_height
                new_width = int(max_height * aspect_ratio)
            
            # Resize the image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update the label
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Keep a reference to prevent garbage collection
            
        except Exception as e:
            self.image_label.configure(image=None, text=f"Error loading image: {str(e)}")
            self.image_label.image = None
    
    def clear_image(self):
        """Clear the image display."""
        self.image_label.configure(image=None, text="No image selected")
        self.image_label.image = None
    
    def is_image_or_video(self, file_path):
        """
        Check if a file is an image or video based on its extension
        
        Args:
            file_path (str): Path to the file to check
            
        Returns:
            bool: True if the file is an image or video, False otherwise
        """
        # Common image and video extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
        
        # Get file extension and convert to lowercase
        _, ext = os.path.splitext(file_path.lower())
        
        return ext in image_extensions or ext in video_extensions
    
    def is_image_file(self, file_path):
        """
        Check if a file is an image (not video) based on its extension
        
        Args:
            file_path (str): Path to the file to check
            
        Returns:
            bool: True if the file is an image, False otherwise
        """
        # Common image extensions
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}
        
        # Get file extension and convert to lowercase
        _, ext = os.path.splitext(file_path.lower())
        
        return ext in image_extensions
    
    def display_file_info(self, file_path):
        """
        Display file information including image name (without extension)
        
        Args:
            file_path (str): Path to the file to display
        """
        if file_path:
            # Update current image path
            self.current_image_path = file_path
            
            # Extract filename from path
            filename = os.path.basename(file_path)
            
            # Extract image name without extension
            image_name = os.path.splitext(filename)[0]
            
            # Update labels - only show image name without extension
            self.image_name_label.configure(text=image_name)
            
            # Try to display the image
            self.display_image_or_video(file_path)
            
            # Update navigation buttons based on current file
            self.update_navigation_buttons(file_path)
        else:
            # Clear all labels and image if no file
            self.clear_image()
            self.image_name_label.configure(text="")
            self.current_image_path = None
            
            # Disable navigation buttons when no file is selected
            if hasattr(self, 'left_button') and hasattr(self, 'right_button'):
                self.left_button.configure(fg_color="gray", hover_color="gray")
                self.right_button.configure(fg_color="gray", hover_color="gray")
    
    def load_first_media_file(self):
        """
        Load and display the first viewable image file from the files list
        """
        if hasattr(self, 'directory_images') and self.directory_images:
            # Get the first image from the list (it's already filtered to only contain images)
            first_viewable_image = self.directory_images[0]
            self.current_image_index = 0
            self.display_file_info(first_viewable_image)
        else:
            self.display_file_info(None)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()