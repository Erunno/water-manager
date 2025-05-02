from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import csv
import os
import datetime
import sys
from threading import Thread

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Determine CSV file path from command line argument or environment variable
if len(sys.argv) > 1:
    CSV_FILE = sys.argv[1]
elif os.environ.get('CSV_FILE'):
    CSV_FILE = os.environ.get('CSV_FILE')
else:
    CSV_FILE = 'data.csv'  # Default fallback

print(f"Using database file: {CSV_FILE}")

# Initialize the CSV file if it doesn't exist
if not os.path.exists(CSV_FILE):
    os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
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

# API route to get raw CSV data
@app.route('/api/data-csv', methods=['GET'])
def get_csv_data():
    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8-sig') as file:
            csv_content = file.read()
        
        response = app.response_class(
            response=csv_content,
            status=200,
            mimetype='text/csv'
        )
        response.headers["Content-Disposition"] = "attachment; filename=water-jugs.csv"
        return response
    except Exception as e:
        return jsonify({'error': f'Error reading CSV file: {str(e)}'}), 500

# Serve frontend files
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def serve_frontend(path):
    return send_from_directory(app.static_folder, path)

# Add a basic health check endpoint that doesn't require HTTPS
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

# In the "__main__" block:
if __name__ == '__main__':
    # Function to run the HTTP server
    def run_http_server():
        http_app = Flask(__name__, static_folder='../frontend', static_url_path='')
        CORS(http_app)
        
        # Define the same routes for the HTTP app
        @http_app.route('/api/jugs', methods=['GET'])
        def http_get_jugs():
            return get_jugs()
        
        @http_app.route('/api/jugs/fill', methods=['POST'])
        def http_fill_jugs():
            return fill_jugs()
        
        @http_app.route('/api/jugs/empty', methods=['POST'])
        def http_empty_jug():
            return empty_jug()
            
        @http_app.route('/api/data-csv', methods=['GET'])
        def http_get_csv_data():
            return get_csv_data()
            
        @http_app.route('/health', methods=['GET'])
        def http_health_check():
            return health_check()
        
        # Serve frontend files
        @http_app.route('/', defaults={'path': 'index.html'})
        @http_app.route('/<path:path>')
        def http_serve_frontend(path):
            return send_from_directory(http_app.static_folder, path)
            
        print("Starting server with HTTP on http://0.0.0.0:80")
        http_app.run(host='0.0.0.0', port=80, debug=False)
    
    # Check if certificates exist for HTTPS
    cert_path = os.path.join(os.getcwd(), 'server.cert')
    key_path = os.path.join(os.getcwd(), 'server.key')
    
    # Start HTTP server in a separate thread
    http_thread = Thread(target=run_http_server)
    http_thread.daemon = True
    http_thread.start()
    
    # Start the HTTPS server in the main thread
    if os.path.exists(cert_path) and os.path.exists(key_path):
        context = (cert_path, key_path)
        print("Starting server with HTTPS on https://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, ssl_context=context, debug=True, use_reloader=False)
    else:
        print("HTTPS certificates not found. Only HTTP server is available.")
        # Keep the main thread alive
        import time
        while True:
            time.sleep(1)