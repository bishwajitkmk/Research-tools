import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

cleaned_df = None
filtered_df = None
file_path = None
data_type = None  # This one tracks whether the data is of Type 1 or 2

# Observational Parameters
important_features_type1 = [
    "obs_collection", "instrument_name", "filters", "wavelength_region", 
    "target_name", "target_classification", "s_ra", "s_dec", "calib_level", 
    "t_min", "t_exptime", "distance"
]

# Astrometric Parameter
important_features_type2 = [
    "source_id", "ra", "dec", "l", "b", "parallax", "parallax_over_error",
    "pmra", "pmdec", "radial_velocity", "phot_g_mean_mag", "phot_bp_mean_mag",
    "phot_rp_mean_mag", "bp_rp", "teff_val", "radius_val", "lum_val"
]

def upload_file():
    global file_path, data_type
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    
    if file_path:
        messagebox.showinfo("Success", "File uploaded successfully! Now click 'Clear CSV'.")
        detect_data_type()  # Detect the data type automatically
    else:
        messagebox.showerror("Error", "No file selected!")

def detect_data_type():
    global file_path, data_type
    try:
        df = pd.read_csv(file_path, comment="#")
        columns = set(df.columns)

        # Check which type of data this is
        type1_match = any(col in columns for col in important_features_type1)
        type2_match = any(col in columns for col in important_features_type2)

        if type1_match and not type2_match:
            data_type = "Type 1"
        elif type2_match and not type1_match:
            data_type = "Type 2"
        elif type1_match and type2_match:
            data_type = "Both"
        else:
            data_type = None

        if data_type == "Both":
            messagebox.showinfo("Multiple Matches", "Both data types detected. Please select the correct filter!")
        elif data_type:
            messagebox.showinfo("Data Type Detected", f"Detected {data_type} dataset.")
        else:
            messagebox.showwarning("Unknown Format", "This CSV does not match known data types.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to detect data type:\n{e}")

def clear_csv():
    global cleaned_df, file_path
    if not file_path:
        messagebox.showerror("Error", "Please upload a CSV file first!")
        return
    
    try:
        # Load CSV and remove comments
        cleaned_df = pd.read_csv(file_path, comment="#")
        messagebox.showinfo("Success", "Comments removed! Click 'Filter CSV' to process data.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process file:\n{e}")

def filter_csv():
    global cleaned_df, filtered_df, data_type
    if cleaned_df is None:
        messagebox.showerror("Error", "No cleaned data available! Click 'Clear CSV' first.")
        return

    # If both types were detected, ask the user to choose
    if data_type == "Both":
        user_choice = messagebox.askquestion("Choose Filter", "Both data types detected. Do you want to apply Type 1 filter?\n(Select 'No' for Type 2)")
        if user_choice == "yes":
            data_type = "Type 1"
        else:
            data_type = "Type 2"

    # Select filter based on detected type
    if data_type == "Type 1":
        selected_features = important_features_type1
    elif data_type == "Type 2":
        selected_features = important_features_type2
    else:
        messagebox.showerror("Error", "Unknown data type! Cannot filter.")
        return

    try:
        # Keep only important features (if they exist in the dataset)
        filtered_df = cleaned_df[[col for col in selected_features if col in cleaned_df.columns]]
        
        # Remove columns where all values are NaN
        filtered_df = filtered_df.dropna(axis=1, how="all")

        messagebox.showinfo("Success", f"Data filtered using {data_type} filter! Click 'Save CSV' to download.")
    except Exception as e:
        messagebox.showerror("Error", f"Filtering failed:\n{e}")

def save_file():
    global filtered_df
    if filtered_df is None:
        messagebox.showerror("Error", "No filtered data available! Click 'Filter CSV' first.")
        return
    
    save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if save_path:
        filtered_df.to_csv(save_path, index=False)
        messagebox.showinfo("Success", f"File saved successfully to:\n{save_path}")
    else:
        messagebox.showerror("Error", "No file name specified!")

# Tkinter GUI Setup
root = tk.Tk()
root.title("CSV Cleaner & Auto-Filter")
root.geometry("500x420")
root.config(bg="#2C3E50") 

# Basic styling
button_style = {
    "font": ("Arial", 12, "bold"),
    "bg": "#3498DB", 
    "fg": "white",
    "activebackground": "#2980B9",
    "activeforeground": "white",
    "relief": "raised",
    "width": 18,
    "height": 2
}

# Title Label
title_label = tk.Label(root, text="CSV Cleaner & Auto-Filter", font=("Arial", 18, "bold"), fg="white", bg="#2C3E50")
title_label.pack(pady=15)

# Button Frame
frame = tk.Frame(root, bg="#2C3E50")
frame.pack(pady=10)

# Upload Button
btn_upload = tk.Button(frame, text="📂 Upload CSV", command=upload_file, **button_style)
btn_upload.grid(row=0, column=0, pady=5)

# Clear CSV Button
btn_clear = tk.Button(frame, text="🗑️ Clear CSV", command=clear_csv, **button_style)
btn_clear.grid(row=1, column=0, pady=5)

# Filter CSV Button
btn_filter = tk.Button(frame, text="🔍 Filter CSV", command=filter_csv, **button_style)
btn_filter.grid(row=2, column=0, pady=5)

# Save CSV Button
btn_save = tk.Button(frame, text="💾 Save CSV", command=save_file, **button_style)
btn_save.grid(row=3, column=0, pady=5)

root.mainloop()
