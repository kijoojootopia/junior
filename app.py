import os
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv

# .env 환경변수 로드
load_dotenv()

from services.screening_engine import screen_ingredients
from services.exchange_api import get_current_exchange_rates
from services.export_routes import export_bp

app = Flask(__name__)
app.register_blueprint(export_bp)
app.config['UPLOAD_FOLDER'] = 'uploads'

# 첫 접속은 수출 권역 지도로 이동
@app.route('/')
def home():
    return redirect(url_for('export.dashboard'))


# 진단 대시보드 라우터
@app.route('/dashboard')
def index():
    rates = get_current_exchange_rates()
    pipeline_data = {}
    for region in ('us', 'eu', 'eac', 'uae'):
        file_path = os.path.join(app.root_path, 'data', region, 'pipeline_checklist.json')
        try:
            with open(file_path, encoding='utf-8') as source:
                data = json.load(source)
            # 미국은 GENERAL/OTC로 나뉘고, 다른 권역은 단일 목록입니다.
            if isinstance(data, list):
                data = {'GENERAL': data}
            if not isinstance(data, dict) or not all(isinstance(items, list) for items in data.values()):
                raise ValueError('파이프라인 항목은 목록이어야 합니다.')
            pipeline_data[region] = data
        except (OSError, ValueError):
            app.logger.exception('%s 파이프라인 자료를 읽지 못했습니다.', region)
            pipeline_data[region] = {'GENERAL': []}

    return render_template(
        'index.html', rates=rates, pipeline_data=pipeline_data,
        pipeline_items=pipeline_data['us'].get('GENERAL', []),
        pipeline_label='미국 · 일반 화장품',
    )

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
