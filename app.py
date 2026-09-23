import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# .env 환경변수 로드
load_dotenv()

from services.screening_engine import screen_ingredients
from services.exchange_api import get_current_exchange_rates
from services.export_routes import export_bp

app = Flask(__name__)
app.register_blueprint(export_bp)
app.config['UPLOAD_FOLDER'] = 'uploads'

# 메인 페이지 라우터
@app.route('/')
def index():
    rates = get_current_exchange_rates()
    return render_template('index.html', rates=rates)

# CSV 업로드 및 성분 판정 API 라우터
@app.route('/api/screen', methods=['POST'])
def run_screening():
    if 'file' not in request.files:
        return jsonify({'error': '파일이 없습니다.'}), 400
        
    file = request.files['file']
    target_region = request.form.get('region', 'us')
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    result = screen_ingredients(file_path, target_region)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
