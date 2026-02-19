"""
Analytics Module - CSV and PDF Export
Generates reports and exports detection data
"""

import csv
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

class Analytics:
    def __init__(self, database):
        """
        Initialize analytics module
        
        Args:
            database: DetectionDatabase instance
        """
        self.db = database
        
    def export_to_csv(self, filepath='data/detections_export.csv', period='all'):
        """
        Export detections to CSV file
        
        Args:
            filepath (str): Output file path
            period (str): Time period ('today', 'week', 'month', 'all')
            
        Returns:
            str: Path to created file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Get detections based on period
        if period == 'all':
            detections = self.db.get_all_detections()
        else:
            hours_map = {'today': 24, 'week': 168, 'month': 720}
            detections = self.db.get_detections_last_hours(hours_map.get(period, 24))
        
        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'ID', 'Timestamp', 'Latitude', 'Longitude', 'Confidence', 
                'Message', 'Drone ID', 'Alert Level', 'Duration (s)', 
                'In Safe Zone', 'Created At'
            ])
            
            # Data rows
            for d in detections:
                writer.writerow([
                    d['id'],
                    d['timestamp'],
                    f"{d['latitude']:.6f}",
                    f"{d['longitude']:.6f}",
                    f"{d['confidence']:.4f}",
                    d['message'],
                    d['drone_id'],
                    d['alert_level'],
                    f"{d['duration']:.2f}",
                    'Yes' if d['in_safe_zone'] else 'No',
                    d['created_at']
                ])
        
        print(f"✅ CSV exported: {filepath} ({len(detections)} records)")
        return filepath
        
    def export_to_pdf(self, filepath='data/detection_report.pdf', period='all'):
        """
        Generate PDF report with statistics and detection table
        
        Args:
            filepath (str): Output file path
            period (str): Time period ('today', 'week', 'month', 'all')
            
        Returns:
            str: Path to created file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12
        )
        
        # Title
        title = Paragraph("AFK-Ultron Detection Report", title_style)
        story.append(title)
        
        # Report metadata
        report_info = Paragraph(
            f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
            f"<b>Period:</b> {period.capitalize()}<br/>"
            f"<b>Drone ID:</b> ULTRON-01",
            styles['Normal']
        )
        story.append(report_info)
        story.append(Spacer(1, 0.3*inch))
        
        # Get statistics
        stats = self.db.get_statistics(period)
        
        # Statistics section
        stats_heading = Paragraph("📊 Detection Statistics", heading_style)
        story.append(stats_heading)
        
        # Statistics table
        stats_data = [
            ['Metric', 'Value'],
            ['Total Detections', str(stats['total_detections'])],
            ['High Alert Detections', str(stats['high_alerts'])],
            ['Average Confidence', f"{stats['average_confidence']:.2%}"],
            ['Peak Hour', f"{stats['peak_hour']} ({stats['peak_hour_count']} detections)"],
        ]
        
        # Add alert breakdown
        for alert_level, count in stats['alert_breakdown'].items():
            stats_data.append([f'{alert_level} Alerts', str(count)])
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Recent detections section
        detections_heading = Paragraph("🚨 Recent Detections", heading_style)
        story.append(detections_heading)
        
        # Get recent detections
        if period == 'all':
            detections = self.db.get_all_detections()[:20]  # Limit to 20 for PDF
        else:
            hours_map = {'today': 24, 'week': 168, 'month': 720}
            detections = self.db.get_detections_last_hours(hours_map.get(period, 24))[:20]
        
        # Detections table
        det_data = [['Time', 'GPS', 'Confidence', 'Alert', 'Duration']]
        
        for d in detections:
            det_data.append([
                d['timestamp'].split()[1] if ' ' in d['timestamp'] else d['timestamp'],
                f"{d['latitude']:.4f}, {d['longitude']:.4f}",
                f"{d['confidence']:.2%}",
                d['alert_level'],
                f"{d['duration']:.1f}s"
            ])
        
        det_table = Table(det_data, colWidths=[1.2*inch, 2*inch, 1*inch, 0.8*inch, 0.8*inch])
        det_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(det_table)
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer = Paragraph(
            "<i>This report was automatically generated by the AFK-Ultron Command Panel</i>",
            styles['Normal']
        )
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ PDF report generated: {filepath}")
        return filepath
        
    def generate_heatmap_data(self, period='all'):
        """
        Generate heatmap data for visualization
        
        Args:
            period (str): Time period
            
        Returns:
            list: List of [lat, lon, intensity] for heatmap
        """
        if period == 'all':
            detections = self.db.get_all_detections()
        else:
            hours_map = {'today': 24, 'week': 168, 'month': 720}
            detections = self.db.get_detections_last_hours(hours_map.get(period, 24))
        
        # Group by location and count
        location_counts = {}
        for d in detections:
            key = f"{d['latitude']:.4f}_{d['longitude']:.4f}"
            if key not in location_counts:
                location_counts[key] = {
                    'lat': d['latitude'],
                    'lon': d['longitude'],
                    'count': 0
                }
            location_counts[key]['count'] += 1
        
        # Convert to heatmap format
        heatmap_data = [
            [loc['lat'], loc['lon'], loc['count']]
            for loc in location_counts.values()
        ]
        
        return heatmap_data
        
    def get_hourly_distribution(self, period='all'):
        """
        Get detection distribution by hour of day
        
        Args:
            period (str): Time period
            
        Returns:
            dict: Hour -> count mapping
        """
        if period == 'all':
            detections = self.db.get_all_detections()
        else:
            hours_map = {'today': 24, 'week': 168, 'month': 720}
            detections = self.db.get_detections_last_hours(hours_map.get(period, 24))
        
        hourly_counts = {str(h).zfill(2): 0 for h in range(24)}
        
        for d in detections:
            timestamp = d['timestamp']
            if ' ' in timestamp:
                hour = timestamp.split()[1].split(':')[0]
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        return hourly_counts


# Test the analytics module
if __name__ == "__main__":
    print("=" * 70)
    print("📊 ANALYTICS MODULE TEST")
    print("=" * 70)
    
    from database import DetectionDatabase
    
    # Initialize database
    db = DetectionDatabase()
    
    # Add some test detections
    test_detections = [
        {
            'timestamp': '2026-01-29 14:30:00',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'confidence': 0.87,
            'message': 'HUMAN DETECTED',
            'drone_id': 'ULTRON-01'
        },
        {
            'timestamp': '2026-01-29 14:31:15',
            'latitude': 28.6140,
            'longitude': 77.2091,
            'confidence': 0.92,
            'message': 'HUMAN DETECTED',
            'drone_id': 'ULTRON-01'
        },
        {
            'timestamp': '2026-01-29 15:00:00',
            'latitude': 28.6141,
            'longitude': 77.2092,
            'confidence': 0.78,
            'message': 'HUMAN DETECTED',
            'drone_id': 'ULTRON-01'
        }
    ]
    
    for det in test_detections:
        db.add_detection(det, duration=5.0)
    
    # Initialize analytics
    analytics = Analytics(db)
    
    # Export to CSV
    csv_path = analytics.export_to_csv()
    
    # Export to PDF
    pdf_path = analytics.export_to_pdf()
    
    # Generate heatmap data
    heatmap = analytics.generate_heatmap_data()
    print(f"\n🗺️  Heatmap data points: {len(heatmap)}")
    
    # Get hourly distribution
    hourly = analytics.get_hourly_distribution()
    print(f"\n⏰ Hourly distribution: {sum(hourly.values())} total detections")
    
    print("\n" + "=" * 70)
    print("✅ Analytics test complete!")
    print(f"   CSV: {csv_path}")
    print(f"   PDF: {pdf_path}")
