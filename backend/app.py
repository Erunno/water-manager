from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import csv
import os
import datetime

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for all routes

import sys

if len(sys.argv) > 1:
    CSV_FILE = sys.argv[1]
else:
    raise ValueError("Please provide the path to the CSV file as a command line argument.")

# Initialize the CSV file if it doesn't exist
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(['JugName', 'State', 'DateTime'])

def read_csv():
    data = []
    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) >= 3:  # Make sure row has enough columns
                    data.append({
                        'JugName': row[0].strip(),  # Strip any whitespace or BOM characters
                        'State': row[1],
                        'DateTime': row[2]
                    })
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return data

def write_csv(data):
    # Remove any duplicates (same jug, state and timestamp)
    unique_entries = []
    seen_entries = set()
    
    for item in data:
        entry_key = (item['JugName'].strip(), item['State'], item['DateTime'])
        if entry_key not in seen_entries:
            seen_entries.add(entry_key)
            unique_entries.append(item)
    
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['JugName', 'State', 'DateTime'])
            for item in unique_entries:
                writer.writerow([item['JugName'].strip(), item['State'], item['DateTime']])
    except Exception as e:
        print(f"Error writing CSV: {e}")

# API route to get jugs
@app.route('/api/jugs', methods=['GET'])
def get_jugs():
    data = read_csv()
    
    # Filter for filled jugs if requested
    if request.args.get('state') == 'filled':
        # Get only the most recent state for each jug
        jug_states = {}
        for entry in sorted(data, key=lambda x: x['DateTime']):
            jug_states[entry['JugName']] = entry
            
        # Filter jugs that are currently filled
        filled_jugs = [jug for jug in jug_states.values() if jug['State'] == 'Filled']
        # Sort by datetime (oldest first)
        filled_jugs.sort(key=lambda x: x['DateTime'])
        return jsonify(filled_jugs)
    
    return jsonify(data)

# API route to fill jugs
@app.route('/api/jugs/fill', methods=['POST'])
def fill_jugs():
    jugs = request.json.get('jugs', [])
    data = read_csv()
    timestamp = datetime.datetime.now().strftime('%H:%M:%S %d.%m.%Y')
    
    # Check for duplicates in the same transaction
    added_jugs = set()
    for jug in jugs:
        jug_name = jug.strip()  # Remove any leading/trailing whitespace
        if jug_name not in added_jugs:
            data.append({
                'JugName': jug_name,
                'State': 'Filled',
                'DateTime': timestamp
            })
            added_jugs.add(jug_name)
    
    write_csv(data)
    return jsonify({'message': f'Naplněno {len(added_jugs)} kanystrů', 'status': 'success'})

# API route to empty jug
@app.route('/api/jugs/empty', methods=['POST'])
def empty_jug():
    jug_name = request.json.get('jugName')
    data = read_csv()
    timestamp = datetime.datetime.now().strftime('%H:%M:%S %d.%m.%Y')
    
    data.append({
        'JugName': jug_name,
        'State': 'Emptied',
        'DateTime': timestamp
    })
    
    write_csv(data)
    return jsonify({'message': f'Emptied jug {jug_name}', 'status': 'success'})

# Serve frontend files
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_frontend(path):
    return send_from_directory(app.static_folder, path)

# In the "__main__" block:
if __name__ == '__main__':
    # Create SSL context using existing certificate files
    context = (
        os.path.join(os.getcwd(), 'server.cert'),
        os.path.join(os.getcwd(), 'server.key')
    )
    
    print("Starting server on https://0.0.0.0:5000")
    print("Access from your phone using https://YOUR_PHONE_IP:5000")
    
    # Run with SSL context
    app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=True)