import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QTabWidget, QMessageBox, QStatusBar)
                             
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import datajoint as dj

# Import your DataJoint schema
from neural_pipeline import Subject, Session, Recording, RecordingStats, schema

class NeuralDataManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        # Window settings
        self.setWindowTitle('Neural Recording Data Manager')
        self.setGeometry(100, 100, 1200, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel('Neural Recording Data Manager')
        title_font = QFont('Arial', 16, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel('DataJoint-based Neuroscience Data Pipeline')
        subtitle_font = QFont('Arial', 10)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: gray;")
        main_layout.addWidget(subtitle)
        
        # Tab widget for different tables
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs for each table
        self.subject_tab = self.create_table_tab("Subjects")
        self.session_tab = self.create_table_tab("Sessions")
        self.recording_tab = self.create_table_tab("Recordings")
        self.stats_tab = self.create_table_tab("Recording Stats")
        
        self.tabs.addTab(self.subject_tab, "Subjects")
        self.tabs.addTab(self.session_tab, "Sessions")
        self.tabs.addTab(self.recording_tab, "Recordings")
        self.tabs.addTab(self.stats_tab, "Statistics")
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton('Refresh Data')
        self.refresh_btn.clicked.connect(self.refresh_all_tables)
        button_layout.addWidget(self.refresh_btn)
        
        self.compute_btn = QPushButton('Compute Statistics')
        self.compute_btn.clicked.connect(self.compute_statistics)
        button_layout.addWidget(self.compute_btn)
        
        self.visualize_btn = QPushButton('Show Visualizations')
        self.visualize_btn.clicked.connect(self.show_visualizations)
        button_layout.addWidget(self.visualize_btn)
        
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()
        
        # Load initial data
        self.refresh_all_tables()
        
    def create_table_tab(self, name):
        """Create a tab with a table widget"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        table = QTableWidget()
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #4a90e2;
                color: white;
                padding: 5px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(table)
        
        # Store reference to table
        if name == "Subjects":
            self.subject_table = table
        elif name == "Sessions":
            self.session_table = table
        elif name == "Recordings":
            self.recording_table = table
        elif name == "Recording Stats":
            self.stats_table = table
            
        return tab
    
    def populate_table(self, table_widget, dj_table, columns):
        """Populate a QTableWidget with data from a DataJoint table"""
        # Fetch data
        data = dj_table.fetch(as_dict=True)
        
        # Set table dimensions
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(columns))
        table_widget.setHorizontalHeaderLabels(columns)
        
        # Populate data
        for row_idx, record in enumerate(data):
            for col_idx, column in enumerate(columns):
                value = str(record.get(column, ''))
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                table_widget.setItem(row_idx, col_idx, item)
        
        # Resize columns to content
        table_widget.resizeColumnsToContents()
    
    def refresh_all_tables(self):
        """Refresh all table views with latest data"""
        try:
            # Subject table
            self.populate_table(
                self.subject_table, 
                Subject(), 
                ['subject_id', 'subject_name', 'species', 'sex', 'date_of_birth']
            )
            
            # Session table
            self.populate_table(
                self.session_table,
                Session(),
                ['subject_id', 'session_id', 'session_date', 'experimenter', 'brain_region']
            )
            
            # Recording table
            self.populate_table(
                self.recording_table,
                Recording(),
                ['subject_id', 'session_id', 'recording_id', 'recording_time', 
                 'num_channels', 'sampling_rate']
            )
            
            # RecordingStats table
            self.populate_table(
                self.stats_table,
                RecordingStats(),
                ['subject_id', 'session_id', 'recording_id', 
                 'mean_amplitude', 'peak_amplitude', 'noise_level']
            )
            
            self.update_status()
            self.status_bar.showMessage('✓ Data refreshed successfully', 3000)
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to refresh data: {str(e)}')
    
    def compute_statistics(self):
        """Trigger computation of recording statistics"""
        try:
            # Check how many recordings need stats
            recordings_without_stats = len(Recording() - RecordingStats())
            
            if recordings_without_stats == 0:
                QMessageBox.information(
                    self, 
                    'Already Computed', 
                    'All recordings already have computed statistics!'
                )
                return
            
            # Confirm computation
            reply = QMessageBox.question(
                self,
                'Compute Statistics',
                f'Compute statistics for {recordings_without_stats} recordings?',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.status_bar.showMessage('Computing statistics...')
                QApplication.processEvents()  # Update UI
                
                # Run computation
                RecordingStats.populate(display_progress=False)
                
                # Refresh tables
                self.refresh_all_tables()
                
                QMessageBox.information(
                    self,
                    'Success',
                    f'✓ Computed statistics for {recordings_without_stats} recordings!'
                )
                
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to compute statistics: {str(e)}')
    
    def show_visualizations(self):
        """Show visualization plots"""
        try:
            from neural_pipeline import visualize_statistics_summary
            self.status_bar.showMessage('Generating visualizations...')
            QApplication.processEvents()
            
            visualize_statistics_summary()
            
            self.status_bar.showMessage('✓ Visualizations displayed', 3000)
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to create visualizations: {str(e)}')
    
    def update_status(self):
        """Update status bar with database stats"""
        try:
            num_subjects = len(Subject())
            num_sessions = len(Session())
            num_recordings = len(Recording())
            num_stats = len(RecordingStats())
            
            status_text = (f'Database: {num_subjects} Subjects | {num_sessions} Sessions | '
                          f'{num_recordings} Recordings | {num_stats} Computed Stats')
            self.status_bar.showMessage(status_text)
            
        except Exception as e:
            self.status_bar.showMessage(f'Error: {str(e)}')


def main():
    """Main function to run the application"""
    # Configure DataJoint connection
    dj.config['database.host'] = 'localhost'
    dj.config['database.user'] = 'root'
    dj.config['database.password'] = 'myroot'
    
    # Create application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = NeuralDataManager()
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()