from flask import Flask, render_template, request, redirect, url_for
from flask import send_from_directory
from flask import request, render_template
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Define the paths for raw and summarized data directories
raw_data_dir = "raw_data"
summarized_data_dir = "summarized_data"

# Create directories if they don't exist
os.makedirs(raw_data_dir, exist_ok=True)
os.makedirs(summarized_data_dir, exist_ok=True)

@app.route("/")
def index():
    # Load raw and summarized data from files in the directories
    data = load_data_from_directories(raw_data_dir, summarized_data_dir)
    
    return render_template("index.html", data=data)

@app.route("/search", methods=["GET"])
def search():
    search_query = request.args.get("search_query", "").lower()

    # Assuming your raw data folders are stored in a 'raw_data' directory
    raw_data_dir = "raw_data"

    # Get all folder names in the 'raw_data' directory
    all_datasets = [folder_name for folder_name in os.listdir(raw_data_dir) if os.path.isdir(os.path.join(raw_data_dir, folder_name))]

    # Filter datasets based on the search query
    filtered_datasets = [dataset for dataset in all_datasets if search_query in dataset.lower()]

    # Create a dictionary with dataset names as keys and their paths and summary data links as values
    filtered_data = {}
    for dataset in filtered_datasets:
        raw_data_path = os.path.join(raw_data_dir, dataset)
        summary_data_link_path = os.path.join("summarized_data", dataset, "summary_data_link.txt")  # Assuming summary data link is stored in a 'summary_data_link.txt' file

        # Check if the paths exist before adding to the dictionary
        if os.path.exists(raw_data_path) and os.path.exists(summary_data_link_path):
            with open(summary_data_link_path, "r") as summary_link_file:
                summary_data_link = summary_link_file.read().strip()

            filtered_data[dataset] = {'raw_data_path': raw_data_path, 'summary_data_link': summary_data_link}

    return render_template("index.html", data=filtered_data)

def create_readme(dataset_name, readme_filepath):
    with open(readme_filepath, "w") as readme_file:
        readme_file.write(f"Dataset: {dataset_name}\n\n")
        readme_file.write("This folder contains raw data for the dataset.\n")
        readme_file.write("For more information, please visit the Data Registry Web App:\n")
        readme_file.write("https://your-data-registry-app-url.com\n")

@app.route("/add_data", methods=["POST"])
def add_data():
    # Get data from the form
    dataset_name = request.form.get("dataset_name")
    raw_data_folder = request.files.getlist("raw_data_folder")
    summary_data_link = request.form.get("summary_data_link")

    # Create directories for raw and summarized data using the dataset name
    entry_raw_data_dir = os.path.join(raw_data_dir, secure_filename(dataset_name))
    entry_summarized_data_dir = os.path.join(summarized_data_dir, secure_filename(dataset_name))

    os.makedirs(entry_raw_data_dir, exist_ok=True)
    os.makedirs(entry_summarized_data_dir, exist_ok=True)

    # Save uploaded raw data files
    for uploaded_file in raw_data_folder:
        # Ensure a safe filename using secure_filename
        filename = secure_filename(uploaded_file.filename)
        uploaded_file.save(os.path.join(entry_raw_data_dir, filename))

    # Save summary data link
    summary_link_filepath = os.path.join(entry_summarized_data_dir, "summary_data_link.txt")
    write_data_to_file(summary_data_link, summary_link_filepath)

    # Create README file
    readme_filepath = os.path.join(entry_raw_data_dir, "README.txt")
    create_readme(dataset_name, readme_filepath)

    return redirect(url_for("index"))

@app.route("/download_raw_data/<dataset_name>")
def download_raw_data(dataset_name):
    # Path to the raw data directory
    raw_data_dir = os.path.join("raw_data", secure_filename(dataset_name))

    # Zip the raw data directory
    zip_filename = f"{dataset_name}_raw_data.zip"
    zip_filepath = os.path.join("downloads", zip_filename)
    shutil.make_archive(zip_filepath[:-4], "zip", raw_data_dir)

    return send_from_directory("downloads", zip_filename, as_attachment=True)

def load_data_from_directories(raw_data_directory, summarized_data_directory):
    data = {}
    for entry_name in os.listdir(raw_data_directory):
        entry_raw_data_dir = os.path.join(raw_data_directory, entry_name)
        entry_summarized_data_dir = os.path.join(summarized_data_directory, entry_name)

        if os.path.isdir(entry_raw_data_dir) and os.path.exists(os.path.join(entry_summarized_data_dir, "summary_data_link.txt")):
            entry_data = {}
            entry_data["raw_data_path"] = entry_raw_data_dir
            with open(os.path.join(entry_summarized_data_dir, "summary_data_link.txt"), "r") as link_file:
                entry_data["summary_data_link"] = link_file.read().strip()

            data[entry_name] = entry_data

    return data

def write_data_to_file(data, filepath):
    with open(filepath, "w") as file:
        file.write(data)

if __name__ == "__main__":
    app.run(debug=True)


