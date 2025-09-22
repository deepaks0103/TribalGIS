import os
from flask import Flask, request, jsonify, render_template_string
from PIL import Image
import pytesseract
import spacy
from geopy.geocoders import Nominatim

# --------- Setup -------------
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load NER model
nlp = spacy.blank("en")
ruler = nlp.add_pipe("entity_ruler")
ruler.add_patterns([
    {"label": "PLACE", "pattern": "Salem"},
    {"label": "PLACE", "pattern": "Chennai"},
    {"label": "PLACE", "pattern": "Delhi"},
    {"label": "PLACE", "pattern": "Mumbai"},
    {"label": "NAME", "pattern": "Ramesh"}
])

geolocator = Nominatim(user_agent="fra_demo")

# --------- HTML Frontend ----------
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>FRA OCR + NER + WebGIS Trace</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
  <style>
    body { font-family: Arial, sans-serif; margin:20px; background:#f5f5f5; }
    #map { height:500px; margin-top:20px; border-radius:8px; overflow:hidden; }
    .card { background:white; padding:20px; border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.1); max-width:700px; margin:auto; }
    button { background:#1a535c; color:#fff; border:none; padding:10px 15px; border-radius:5px; cursor:pointer; margin-top:10px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>Upload Claim Form</h2>
    <input type="file" id="fileInput">
    <button onclick="uploadFile()">Upload & Extract</button>

    <div id="results"></div>
    <div id="map"></div>
  </div>

  <script>
    const map = L.map('map').setView([20.5937, 78.9629], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19
    }).addTo(map);

    let routeLine;

    async function uploadFile() {
      const file = document.getElementById('fileInput').files[0];
      if (!file) return alert("Please select an image");

      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch('/extract', { method: 'POST', body: formData });
      const data = await res.json();
      console.log(data);

      document.getElementById('results').innerHTML = 
        "<h3>Extracted Text:</h3><pre>"+data.text+"</pre>";

      const coords = [];
      data.entities.forEach(e => {
        if (e.label === 'PLACE' && e.coordinates) {
          const lat = e.coordinates.lat;
          const lon = e.coordinates.lon;
          coords.push([lat, lon]);
          L.marker([lat, lon]).addTo(map).bindPopup(`${e.text}`);
        }
      });

      if (routeLine) {
        map.removeLayer(routeLine);
      }

      if (coords.length > 1) {
        routeLine = L.polyline(coords, {color:'red', weight:3}).addTo(map);
        map.fitBounds(routeLine.getBounds());
      } else if (coords.length === 1) {
        map.setView(coords[0], 8);
      }
    }
  </script>
</body>
</html>
'''

# --------- Routes ----------
@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/extract", methods=["POST"])
def extract():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    img = Image.open(file.stream)
    text = pytesseract.image_to_string(img)

    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        ent_data = {"label": ent.label_, "text": ent.text}
        if ent.label_ == "PLACE":
            loc = geolocator.geocode(ent.text)
            if loc:
                ent_data["coordinates"] = {"lat": loc.latitude, "lon": loc.longitude}
        entities.append(ent_data)

    return jsonify({"text": text, "entities": entities})

# --------- Main ----------
if __name__ == "__main__":
    # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    app.run(host="0.0.0.0", port=5000, debug=True)
