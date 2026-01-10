import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QTabWidget, QMessageBox, QStatusBar, QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit, 
                             QDialogButtonBox, QFileDialog, QGroupBox)
                             
from PyQt5.QtCore import Qt, QDate
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
        
        self.add_subject_btn = QPushButton(' Add Subject')
        self.add_subject_btn.clicked.connect(self.add_subject)
        button_layout.addWidget(self.add_subject_btn)

        #Export 
        self.export_btn = QPushButton(' Export to CSV')
        self.export_btn.clicked.connect(self.export_data)
        button_layout.addWidget(self.export_btn)

        main_layout.addLayout(button_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status()
        
        # Load initial data
        self.refresh_all_tables()
        
    def create_table_tab(self, name):
        """Create a tab with a table widget and search functionality"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel('Search:')
        search_input = QLineEdit()
        search_input.setPlaceholderText('Type to filter...')
        search_input.textChanged.connect(lambda text: self.filter_table(table, text))
        search_layout.addWidget(search_label)
        search_layout.addWidget(search_input)
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Table widget
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
        
        # Count label
        count_label = QLabel()
        count_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(count_label)
        
        # Store references
        if name == "Subjects":
            self.subject_table = table
            self.subject_count_label = count_label
        elif name == "Sessions":
            self.session_table = table
            self.session_count_label = count_label
        elif name == "Recordings":
            self.recording_table = table
            self.recording_count_label = count_label
        elif name == "Recording Stats":
            self.stats_table = table
            self.stats_count_label = count_label
            
        return tab
    
    def filter_table(self, table, search_text):
        """Filter table rows based on search text"""
        for row in range(table.rowCount()):
            match = False
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item and search_text.lower() in item.text().lower():
                    match = True
                    break
            table.setRowHidden(row, not match)

    def populate_table(self, table_widget, dj_table, columns, count_label=None):
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

        # Update count label
        if count_label:
            count_label.setText(f'Total entries: {len(data)}')
    
    def refresh_all_tables(self):
        """Refresh all table views with latest data"""
        try:
            # Subject table
            self.populate_table(
                self.subject_table, 
                Subject(), 
                ['subject_id', 'subject_name', 'species', 'sex', 'date_of_birth'],
                self.subject_count_label
            )
            
            # Session table
            self.populate_table(
                self.session_table,
                Session(),
                ['subject_id', 'session_id', 'session_date', 'experimenter', 'brain_region'],
                self.session_count_label
            )
            
            # Recording table
            self.populate_table(
                self.recording_table,
                Recording(),
                ['subject_id', 'session_id', 'recording_id', 'recording_time', 
                 'num_channels', 'sampling_rate'],
                 self.recording_count_label
            )
            
            # RecordingStats table
            self.populate_table(
                self.stats_table,
                RecordingStats(),
                ['subject_id', 'session_id', 'recording_id', 
                 'mean_amplitude', 'peak_amplitude', 'noise_level'],
                 self.stats_count_label
            )
            
            self.update_status()
            self.status_bar.showMessage('Data refreshed successfully', 3000)
            
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
                    f' Computed statistics for {recordings_without_stats} recordings!'
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
    
    def add_subject(self):
        """Open dialog to add a new subject"""
        dialog = AddSubjectDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_data()
                Subject.insert1(data)
                
                self.refresh_all_tables()
                
                QMessageBox.information(
                    self,
                    'Success',
                    f'✓ Added subject: {data["subject_name"]}'
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    'Error',
                    f'Failed to add subject: {str(e)}'
                )

    def export_data(self):
        """Export current tab's data to CSV"""
        try:
            import pandas as pd
            
            # Get current tab
            current_tab_index = self.tabs.currentIndex()
            tab_names = ['Subjects', 'Sessions', 'Recordings', 'Statistics']
            current_tab_name = tab_names[current_tab_index]
            
            # Get corresponding DataJoint table
            if current_tab_index == 0:
                data = Subject.fetch(as_dict=True)
            elif current_tab_index == 1:
                data = Session.fetch(as_dict=True)
            elif current_tab_index == 2:
                data = Recording.fetch(as_dict=True)
            else:
                data = RecordingStats.fetch(as_dict=True)
            
            if not data:
                QMessageBox.warning(self, 'No Data', 'No data to export!')
                return
            
            # Ask for save location
            filename, _ = QFileDialog.getSaveFileName(
                self,
                f'Export {current_tab_name}',
                f'{current_tab_name.lower()}_export.csv',
                'CSV Files (*.csv)'
            )
            
            if filename:
                # Convert to DataFrame and save
                df = pd.DataFrame(data)
                df.to_csv(filename, index=False)
                
                QMessageBox.information(
                    self,
                    'Success',
                    f'✓ Exported {len(data)} rows to:\n{filename}'
                )
                
        except ImportError:
            QMessageBox.warning(
                self,
                'Missing Dependency',
                'Please install pandas: pip install pandas'
            )
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to export: {str(e)}')

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

class AddSubjectDialog(QDialog):
    """Dialog for adding a new subject"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add New Subject')
        self.setModal(True)
        self.initUI()
        
    def initUI(self):
        layout = QFormLayout(self)
        
        # Subject ID
        self.subject_id_input = QLineEdit()
        layout.addRow('Subject ID:', self.subject_id_input)
        
        # Subject Name
        self.subject_name_input = QLineEdit()
        layout.addRow('Subject Name:', self.subject_name_input)
        
        # Species
        self.species_combo = QComboBox()
        self.species_combo.addItems(['mouse', 'rat'])
        layout.addRow('Species:', self.species_combo)
        
        # Sex
        self.sex_combo = QComboBox()
        self.sex_combo.addItems(['M', 'F'])
        layout.addRow('Sex:', self.sex_combo)
        
        # Date of Birth
        self.dob_input = QDateEdit()
        self.dob_input.setDate(QDate.currentDate())
        self.dob_input.setCalendarPopup(True)
        layout.addRow('Date of Birth:', self.dob_input)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def get_data(self):
        """Return the entered data as a dictionary"""
        return {
            'subject_id': int(self.subject_id_input.text()),
            'subject_name': self.subject_name_input.text(),
            'species': self.species_combo.currentText(),
            'sex': self.sex_combo.currentText(),
            'date_of_birth': self.dob_input.date().toPyDate()
        }

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