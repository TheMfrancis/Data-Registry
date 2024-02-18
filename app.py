from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)



# Define the path for the main data directory
data_dir = "PDC"

# Create directory if it doesn't exist
os.makedirs(data_dir, exist_ok=True)

def load_data_from_directories():
    data = {}
    for dataset in os.listdir(data_dir):
        dataset_path = os.path.join(data_dir, dataset)
        if os.path.isdir(dataset_path):
            data[dataset] = {"raw_data_path": "", "processed_data_path": "", "summarized_data_link": ""}
            summary_link_path = os.path.join(dataset_path, "summary_data_link.txt")
            if os.path.isfile(summary_link_path):
                with open(summary_link_path) as f:
                    data[dataset]["summarized_data_link"] = f.read().strip()
            for subdir in os.listdir(dataset_path):
                subdir_path = os.path.join(dataset_path, subdir)
                if os.path.isdir(subdir_path):
                    if subdir == "raw_data":
                        data[dataset]["raw_data_path"] = subdir_path
                    elif subdir == "processed_data":
                        data[dataset]["processed_data_path"] = subdir_path
    return data





# Load data initially
data = load_data_from_directories()

@app.route("/")
def index():
    # Get list of dataset folders
    datasets = os.listdir(data_dir)
    # Create dictionary to store dataset information
    data = {}
    # Iterate through dataset folders
    for dataset in datasets:
        dataset_path = os.path.join(data_dir, dataset)
        # Check if it's a directory
        if os.path.isdir(dataset_path):
            # Get paths for raw data, processed data, and summarized data link
            raw_data_path = os.path.join(dataset_path, "raw_data")
            processed_data_path = os.path.join(dataset_path, "processed_data")
            summarized_data_path = os.path.join(dataset_path, "summary_data_link.txt")
            # Check if raw data and processed data directories exist
            if os.path.exists(raw_data_path) and os.path.exists(processed_data_path):
                # Read summarized data link from file
                with open(summarized_data_path, "r") as file:
                    summarized_data_link = file.read().strip()
                # Add dataset information to dictionary
                data[dataset] = {"raw_data_path": raw_data_path, "processed_data_path": processed_data_path, "summarized_data_link": summarized_data_link}
    return render_template("index.html", data=data)


@app.route("/add_data", methods=["POST"])
def add_data():
    # Get data from the form
    raw_data_folder = request.files.getlist("raw_data_folder")
    processed_data_folder = request.files.getlist("processed_data_folder")
    summary_data_link = request.form.get("summary_data_link")

    # Generate dataset name dynamically
    dataset_name = generate_dataset_name()

    # Create directory for the dataset
    dataset_path = os.path.join(data_dir, dataset_name)
    os.makedirs(dataset_path, exist_ok=True)

    # Create directories for raw data, processed data, and save summarized data link
    raw_data_path = os.path.join(dataset_path, "raw_data")
    processed_data_path = os.path.join(dataset_path, "processed_data")
    summary_data_path = os.path.join(dataset_path, "summary_data_link.txt")
    os.makedirs(raw_data_path, exist_ok=True)
    os.makedirs(processed_data_path, exist_ok=True)
    with open(summary_data_path, "w") as file:
        file.write(summary_data_link)

    # Save uploaded raw data files
    for uploaded_file in raw_data_folder:
        filename = os.path.basename(uploaded_file.filename)  # Extract filename
        uploaded_file.save(os.path.join(raw_data_path, filename))

    # Save uploaded processed data files
    for uploaded_file in processed_data_folder:
        filename = os.path.basename(uploaded_file.filename)  # Extract filename
        uploaded_file.save(os.path.join(processed_data_path, filename))

    # Create README file with data registry link
    readme_content = f"This dataset is part of the data registry. For more information, visit: {url_for('search_data', search_query=dataset_name, _external=True)}"
    with open(os.path.join(dataset_path, "README.txt"), "w") as readme_file:
        readme_file.write(readme_content)

    return redirect(url_for("index"))

@app.route("/search", methods=["GET"])
def search_data():
    search_query = request.args.get("search_query", "").lower()
    filtered_data = {}
    for dataset, info in load_data_from_directories().items():
        if search_query in dataset.lower():
            filtered_data[dataset] = info

    # Debug print to check the filtered data
    # print(filtered_data)

    return render_template("index.html", data=filtered_data)

@app.route("/view_dataset/<dataset_name>")
def view_dataset(dataset_name):
    data = load_data_from_directories()
    dataset_info = data.get(dataset_name)
    if dataset_info:
        return render_template("view_dataset.html", dataset_name=dataset_name, dataset_info=dataset_info)
    else:
        return "Dataset not found", 404

def generate_dataset_name():
    # Get the number of existing datasets
    num_datasets = len([name for name in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, name))])
    return f"PDC{num_datasets + 1:04d}"

if __name__ == "__main__":
    app.run(debug=True)
