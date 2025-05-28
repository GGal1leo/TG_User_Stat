#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from database import IOCDatabase
from datetime import datetime, timedelta
import os
import tempfile
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production

# Initialize database
db = IOCDatabase()

@app.route('/')
def dashboard():
    """Main dashboard with statistics and recent IOCs."""
    stats = db.get_stats()
    recent_iocs = db.get_iocs(limit=10)
    
    # Process recent IOCs for display
    for ioc in recent_iocs:
        try:
            ioc['detected_at'] = datetime.fromisoformat(ioc['detected_at']).strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
        # Truncate long message content
        if ioc['message_content'] and len(ioc['message_content']) > 100:
            ioc['message_content'] = ioc['message_content'][:100] + '...'
    
    return render_template('dashboard.html', stats=stats, recent_iocs=recent_iocs)

@app.route('/iocs')
def list_iocs():
    """List IOCs with filtering and pagination."""
    page = request.args.get('page', 1, type=int)
    ioc_type = request.args.get('type', '')
    search_term = request.args.get('search', '')
    limit = request.args.get('limit', 50, type=int)
    
    if search_term:
        iocs = db.search_ioc(search_term)
    else:
        iocs = db.get_iocs(ioc_type=ioc_type if ioc_type else None, limit=limit)
    
    # Process IOCs for display
    for ioc in iocs:
        try:
            ioc['detected_at'] = datetime.fromisoformat(ioc['detected_at']).strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    
    return render_template('iocs.html', iocs=iocs, current_type=ioc_type, 
                         current_search=search_term, current_limit=limit)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics."""
    return jsonify(db.get_stats())

@app.route('/api/iocs')
def api_iocs():
    """API endpoint for IOCs."""
    ioc_type = request.args.get('type')
    limit = request.args.get('limit', 100, type=int)
    search_term = request.args.get('search')
    
    if search_term:
        iocs = db.search_ioc(search_term)
    else:
        iocs = db.get_iocs(ioc_type=ioc_type, limit=limit)
    
    return jsonify(iocs)

@app.route('/api/unique_iocs')
def api_unique_iocs():
    """API endpoint for unique IOCs."""
    ioc_type = request.args.get('type')
    unique_iocs = db.get_unique_iocs(ioc_type=ioc_type)
    return jsonify(unique_iocs)

@app.route('/export')
def export_csv():
    """Export IOCs to CSV."""
    try:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        temp_file.close()
        
        # Export to temp file
        success = db.export_to_csv(temp_file.name)
        
        if success:
            return send_file(temp_file.name, as_attachment=True, 
                           download_name=f'iocs_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                           mimetype='text/csv')
        else:
            flash('Export failed', 'error')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Export error: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/search')
def search():
    """Search page."""
    return render_template('search.html')

@app.route('/analytics')
def analytics():
    """Analytics page with charts and insights."""
    stats = db.get_stats()
    
    # Get IOCs by type for chart
    ioc_types = {}
    for key, value in stats.items():
        if key.endswith('_count'):
            ioc_type = key.replace('_count', '')
            ioc_types[ioc_type] = value
    
    # Get recent activity (last 7 days)
    recent_iocs = db.get_iocs(limit=1000)  # Get more for analysis
    
    # Process for daily activity chart
    daily_activity = {}
    for ioc in recent_iocs:
        try:
            date = datetime.fromisoformat(ioc['detected_at']).date()
            daily_activity[str(date)] = daily_activity.get(str(date), 0) + 1
        except:
            pass
    
    # Sort by date and get last 7 days
    sorted_dates = sorted(daily_activity.keys())[-7:]
    daily_data = {date: daily_activity.get(date, 0) for date in sorted_dates}
    
    return render_template('analytics.html', stats=stats, ioc_types=ioc_types, 
                         daily_activity=daily_data)

@app.template_filter('datetime')
def datetime_filter(timestamp):
    """Template filter to format datetime."""
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp)
        else:
            dt = timestamp
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp

@app.template_filter('truncate_text')
def truncate_text_filter(text, length=50):
    """Template filter to truncate text."""
    if not text:
        return ''
    if len(text) <= length:
        return text
    return text[:length] + '...'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
