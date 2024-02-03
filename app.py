from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Define the paths for raw, processed, and summarized data directories
data_dir = "data"

# Create directories if they don't exist
os.makedirs(data_dir, exist_ok=True)

@app.route("/")
def index():
    # Load data from directories
    data = load_data_from_directory(data_dir)
    
    return render_template("index.html", data=data)

def load_data_from_directory(directory):
    data = {}
    for entry_name in os.listdir(directory):
        entry_path = os.path.join(directory, entry_name)

        if os.path.isdir(entry_path):
            data[entry_name] = {'raw_data_path': os.path.join(entry_path, "raw"),
                                'processed_data_path': os.path.join(entry_path, "processed"),
                                'summary_data_link': get_summary_data_link(entry_path)}  # Assuming function to get summary data link

    return data

@app.route("/search", methods=["GET"])
def search():
    search_query = request.args.get("search_query", "").lower()

    # Get all folder names in the data directory
    all_datasets = [folder_name for folder_name in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, folder_name))]

    # Filter datasets based on the search query
    filtered_datasets = [dataset for dataset in all_datasets if search_query in dataset.lower()]

    # Create a dictionary with dataset names as keys and their paths and summary data links as values
    filtered_data = {}
    for dataset in filtered_datasets:
        dataset_path = os.path.join(data_dir, dataset)
        summary_data_link = get_summary_data_link(dataset_path)  # Assuming function to get summary data link

        # Check if the summary data link exists before adding to the dictionary
        if summary_data_link:
            filtered_data[dataset] = {'raw_data_path': os.path.join(dataset_path, "raw"),
                                      'processed_data_path': os.path.join(dataset_path, "processed"),
                                      'summary_data_link': summary_data_link}

    return render_template("index.html", data=filtered_data)

def get_summary_data_link(dataset_path):
    summary_data_link_path = os.path.join(dataset_path, "summary_data_link.txt")
    if os.path.exists(summary_data_link_path):
        with open(summary_data_link_path, "r") as f:
            return f.read().strip()
    else:
        return None

@app.route("/add_data", methods=["POST"])
def add_data():
    # Get data from the form
    dataset_name = request.form.get("dataset_name")
    raw_data_folder = request.files.getlist("raw_data_folder")
    processed_data_folder = request.files.getlist("processed_data_folder")
    summary_data_link = request.form.get("summary_data_link")

    # Create directory for the dataset if it doesn't exist
    dataset_dir = os.path.join("data", secure_filename(dataset_name))
    os.makedirs(dataset_dir, exist_ok=True)

    # Create directory for raw data if it doesn't exist
    raw_data_dir = os.path.join(dataset_dir, "raw")
    os.makedirs(raw_data_dir, exist_ok=True)

    # Create directory for processed data if it doesn't exist
    processed_data_dir = os.path.join(dataset_dir, "processed")
    os.makedirs(processed_data_dir, exist_ok=True)

    # Save uploaded raw data files
    for uploaded_file in raw_data_folder:
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(raw_data_dir, filename))

    # Save uploaded processed data files
    for uploaded_file in processed_data_folder:
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(processed_data_dir, filename))

    # Save summary data link
    summary_link_filepath = os.path.join(dataset_dir, "summary_data_link.txt")
    write_data_to_file(summary_data_link, summary_link_filepath)

    # Redirect to the index page
    return redirect(url_for("index"))




# def load_data_from_directories(raw_data_directory, summarized_data_directory):
#     data = {}
#     for entry_name in os.listdir(raw_data_directory):
#         entry_raw_data_dir = os.path.join(raw_data_directory, entry_name)
#         entry_summarized_data_dir = os.path.join(summarized_data_directory, entry_name)

#         if os.path.isdir(entry_raw_data_dir) and os.path.exists(os.path.join(entry_summarized_data_dir, "summary_data_link.txt")):
#             entry_data = {}
#             entry_data["raw_data_path"] = entry_raw_data_dir
#             with open(os.path.join(entry_summarized_data_dir, "summary_data_link.txt"), "r") as link_file:
#                 entry_data["summary_data_link"] = link_file.read().strip()

#             data[entry_name] = entry_data

#     return data

def create_readme(dataset_name, readme_filepath):
    with open(readme_filepath, "w") as readme_file:
        readme_file.write(f"Dataset: {dataset_name}\n\n")
        readme_file.write("This folder contains raw data for the dataset.\n")
        readme_file.write("For more information, please visit the Data Registry Web App:\n")
        readme_file.write("https://your-data-registry-app-url.com\n")

def write_data_to_file(data, filepath):
    with open(filepath, "w") as file:
        file.write(data)

if __name__ == "__main__":
    app.run(debug=True)
