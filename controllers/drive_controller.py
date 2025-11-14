import pandas as pd
from io import BytesIO
from flask import send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask import Blueprint, redirect, url_for, session, request, render_template
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from services.drive_service import list_files, download_file_content
from services.summarize_service import summarize_text
from constant.constant import ProjectConstant

import base64, json,os
# from dotenv import load_dotenv
# load_dotenv()

# credentials_b64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")
credentials_b64 = ProjectConstant.GOOGLE_CREDENTIALS_BASE64
credentials_dict = json.loads(base64.b64decode(credentials_b64).decode())


drive_bp = Blueprint('drive', __name__)

@drive_bp.route('/connect')
def connect():
    flow = Flow.from_client_config(
        credentials_dict,
        scopes=ProjectConstant.SCOPES,
        redirect_uri=url_for('drive.oauth2callback', _external=True)
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)


@drive_bp.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_config(
        credentials_dict,
        scopes=ProjectConstant.SCOPES,
        redirect_uri=url_for('drive.oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    session['creds'] = creds_to_dict(creds)
    return redirect(url_for('drive.list_drive_files'))


@drive_bp.route('/list-files')
def list_drive_files():
    creds = Credentials(**session['creds'])
    files = list_files(creds)
    flag=True
    return render_template('summarize.html', files=files,flag=flag)

@drive_bp.route('/summarize', methods=['POST'])
def summarize():
    # file_ids = request.form.getlist('file_ids')
    file_ids = request.form.get('file_ids', '').split(',')

    creds = Credentials(**session['creds'])
    summaries = []

    for file_id in file_ids:
        name, content = download_file_content(creds, file_id)
        summary = summarize_text(content)
        summaries.append({'name': name, 'summary': summary})

    session['summaries'] = summaries
    flag=True
    return render_template('summarize.html', summaries=summaries,flag=flag)

@drive_bp.route('/summaries')
def show_summaries():
    summaries = session.get('summaries')
    flag = True
    if not summaries:
        return "No summaries available.", 400
    return render_template('summaries.html', summaries=summaries)


def creds_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }


@drive_bp.route('/download/<format>')
def download_summary(format):
    summaries = session.get('summaries')
    if not summaries:
        return "No summaries available.", 400

    if format == 'csv':
        output = BytesIO()
        df = pd.DataFrame(summaries)


        df.columns = ['filename', 'summary']


        df.to_csv(output, index=False, sep='|')
        output.seek(0)

        return send_file(output, mimetype='text/csv', as_attachment=True, download_name='summaries.csv')

    elif format == 'pdf':
        output = BytesIO()
        c = canvas.Canvas(output, pagesize=A4)
        width, height = A4
        y = height - 50
        for item in summaries:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, f"Filename: {item['name']}")
            y -= 20
            c.setFont("Helvetica", 10)
            for line in item['summary'].split('\n'):
                for subline in [line[i:i + 100] for i in range(0, len(line), 100)]:
                    c.drawString(50, y, subline)
                    y -= 15
                    if y < 50:
                        c.showPage()
                        y = height - 50
            y -= 30
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()
        output.seek(0)
        return send_file(output, mimetype='application/pdf', as_attachment=True, download_name='summaries.pdf')

    else:
        return "Invalid format", 400


