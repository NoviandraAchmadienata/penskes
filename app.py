from flask import Flask, render_template, request, jsonify
import joblib
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Load ML models and preprocessors
try:
    preprocessor = joblib.load('preprocessor_x.joblib')
    model = joblib.load('model_svm_rs.joblib')
    label_encoder = joblib.load('label_encoder.joblib')
    ML_MODELS_LOADED = True
except Exception as e:
    print(f"Error loading ML models: {e}")
    ML_MODELS_LOADED = False

# Poli grouping mapping for fallback classification
POLI_MAPPING = {
    'Penyakit Dalam': 'Poli Umum',
    'Paru & Pernapasan': 'Poli Umum',
    'Kulit & Kelamin': 'Poli Umum',
    'Mata': 'Poli Umum',
    'THT': 'Poli Umum',
    'Saraf': 'Poli Umum',
    'Kebidanan & Kandungan': 'Poli Umum',
    'Psikolog': 'Poli Umum',
    'Bedah': 'Poli Bedah',
    'Kedokteran Fisik & Rehabilitasi': 'Poli Bedah',
    'Jantung & Pembuluh Darah': 'Poli Bedah',
    'Anak': 'Poli Anak',
    'Gigi': 'Poli Gigi'
}

COMPLAINT_KEYWORDS = {
    'Poli Anak': ['anak', 'balita', 'bayi', 'kejang', 'susah makan'],
    'Poli Gigi': ['gigi', 'mulut', 'geraham', 'gusi', 'kawat gigi'],
    'Poli Bedah': ['bedah', 'operasi', 'luka', 'trauma', 'tumor', 'kanker', 'cedera', 'hernia', 'jantung', 'pembuluh'],
    'Poli Umum': []  # default
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/janji-temu')
def janji_temu():
    return render_template('janji-temu.html')

@app.route('/spesialisasi')
def spesialisasi():
    return render_template('spesialisasi.html')

@app.route('/layanan-unggulan')
def layanan_unggulan():
    return render_template('layanan-unggulan.html')

@app.route('/promo')
def promo():
    return render_template('promo.html')

@app.route('/artikel')
def artikel():
    return render_template('artikel.html')

@app.route('/tentang-kami')
def tentang_kami():
    return render_template('tentang-kami.html')

@app.route('/api/recommend-poli', methods=['POST'])
def recommend_poli():
    """
    Recommends a poli based on chief complaint, age, and complaint duration.
    Input JSON: {
        "complaint": "demam tinggi",
        "age": 25,
        "duration": 3
    }
    Output JSON: {
        "recommended_poli": "Poli Umum",
        "confidence": "high"
    }
    """
    try:
        data = request.get_json()
        complaint = str(data.get('complaint', '')).lower().strip()
        age = int(data.get('age', 0))
        duration = int(data.get('duration', 0))
        
        poli = 'Poli Umum'  # default
        confidence = 'low'
        
        # Try ML model first if available
        if ML_MODELS_LOADED and complaint:
            try:
                X = [[complaint, age, duration]]
                Xt = preprocessor.transform(X)
                pred = model.predict(Xt)
                poli = label_encoder.inverse_transform(pred)[0]
                confidence = 'high'
            except Exception as e:
                print(f"ML model error, using fallback: {e}")
                # Fall back to keyword-based classification
                poli = classify_by_keywords(complaint, age)
                confidence = 'medium'
        else:
            # Fallback: keyword-based classification
            poli = classify_by_keywords(complaint, age)
            confidence = 'medium' if complaint else 'low'
        
        return jsonify({
            'recommended_poli': poli,
            'confidence': confidence
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def classify_by_keywords(complaint, age):
    """Classify poli based on keywords in complaint and age."""
    if not complaint:
        return 'Poli Umum'  # default
    
    complaint_lower = complaint.lower()
    
    # Check keywords
    for poli, keywords in COMPLAINT_KEYWORDS.items():
        if keywords and any(kw in complaint_lower for kw in keywords):
            return poli
    
    # Age-based fallback
    if age < 16:
        return 'Poli Anak'
    
    return 'Poli Umum'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
