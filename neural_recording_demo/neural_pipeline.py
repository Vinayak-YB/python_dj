import datajoint as dj
import numpy as np
from datetime import date, timedelta, time


# Configure connection
dj.config['database.host'] = 'localhost'
dj.config['database.user'] = 'root'
dj.config['database.password'] = 'myroot'

# Create schema
schema = dj.schema('neural_recording_lab')

@schema
class Subject(dj.Manual):
    definition = """
    subject_id : int           # unique subject identifier
    ---
    subject_name : varchar(50) # name/code of subject
    species : varchar(20)      # mouse or rat
    sex : enum('M', 'F')       # biological sex
    date_of_birth : date       # birth date
    """

# YOUR TASK: Add these 3 tables yourself based on what you learned

# 1. Session table
#    - Should reference Subject (use ->)
#    - Fields: session_id (int), session_date, experimenter (varchar), brain_region (varchar)
@schema
class Session(dj.Manual):
    definition = """
    -> Subject
    session_id : int
    ---
    session_date : date
    experimenter : varchar(100)
    brain_region : varchar(100)
    """

# 2. Recording table  
#    - Should reference Session
#    - Fields: recording_id (int), recording_time, num_channels (int), sampling_rate (float)
@schema
class Recording(dj.Manual):
    definition = """
    -> Session
    recording_id : int
    ---
    recording_time : time
    num_channels : int
    sampling_rate : float
    """
# 3. RecordingStats table (dj.Computed - we'll implement make() tomorrow)
#    - Should reference Recording
#    - Fields: mean_amplitude (float), peak_amplitude (float), noise_level (float)
@schema
class RecordingStats(dj.Computed):
    definition = """
    -> Recording
    ---
    mean_amplitude : float
    peak_amplitude : float
    noise_level : float
    """
    
    def make(self, key):
        """
        Compute statistics for a single recording.
        This method is called automatically by populate() for each Recording.
        """
        # Fetch the recording info
        recording_info = (Recording & key).fetch1()
        
        print(f"Computing stats for Recording: Subject {key['subject_id']}, "
              f"Session {key['session_id']}, Recording {key['recording_id']}")
        
        # Simulate neural signal data
        # In real life, you'd load actual recorded data from files
        # Here we generate synthetic neural signals
        num_channels = recording_info['num_channels']
        sampling_rate = recording_info['sampling_rate']
        duration_seconds = 10  # 10 seconds of recording
        
        # Generate synthetic neural data (random signals that look realistic)
        num_samples = int(duration_seconds * sampling_rate)
        
        # Simulate multi-channel neural recording
        # Each channel has baseline activity + some spikes
        signal = np.random.randn(num_channels, num_samples) * 10  # Background noise
        
        # Add some "spike" activity (simulating neuron firing)
        num_spikes = np.random.randint(50, 200)
        for _ in range(num_spikes):
            channel = np.random.randint(0, num_channels)
            spike_time = np.random.randint(0, num_samples - 100)
            spike_amplitude = np.random.uniform(50, 150)
            # Add spike waveform
            signal[channel, spike_time:spike_time+100] += spike_amplitude * np.exp(-np.linspace(0, 5, 100))
        
        # Compute statistics across all channels
        mean_amplitude = float(np.mean(np.abs(signal)))
        peak_amplitude = float(np.max(np.abs(signal)))
        noise_level = float(np.std(signal[signal < 20]))  # Std of low-amplitude signal
        
        # Insert the computed statistics into RecordingStats table
        self.insert1({
            **key,  # Include all primary keys (subject_id, session_id, recording_id)
            'mean_amplitude': mean_amplitude,
            'peak_amplitude': peak_amplitude,
            'noise_level': noise_level
        })
        
        print(f"  → Mean: {mean_amplitude:.2f} μV, Peak: {peak_amplitude:.2f} μV, "
              f"Noise: {noise_level:.2f} μV")

        pass



def populate_sample_data():
    """Populate database with sample neuroscience data"""
    
    # Insert 5 subjects
    subjects = [
        {'subject_id': 1, 'subject_name': 'M001', 'species': 'mouse', 'sex': 'M', 'date_of_birth': date(2024, 1, 15)},
        {'subject_id': 2, 'subject_name': 'M002', 'species': 'mouse', 'sex': 'F', 'date_of_birth': date(2024, 2, 10)},
        {'subject_id': 3, 'subject_name': 'R001', 'species': 'rat', 'sex': 'M', 'date_of_birth': date(2024, 3, 5)},
        {'subject_id': 4, 'subject_name': 'M003', 'species': 'mouse', 'sex': 'F', 'date_of_birth': date(2024, 1, 20)},
        {'subject_id': 5, 'subject_name': 'R002', 'species': 'rat', 'sex': 'M', 'date_of_birth': date(2024, 4, 12)},
    ]
    Subject.insert(subjects, skip_duplicates=True)
    print(f" Inserted {len(subjects)} subjects")
    
    # Insert 10 sessions
    sessions = [
        {'subject_id': 1, 'session_id': 1, 'session_date': date(2024, 6, 1), 'experimenter': 'Alice', 'brain_region': 'V1'},
        {'subject_id': 1, 'session_id': 2, 'session_date': date(2024, 6, 5), 'experimenter': 'Alice', 'brain_region': 'V1'},
        {'subject_id': 2, 'session_id': 1, 'session_date': date(2024, 6, 2), 'experimenter': 'Bob', 'brain_region': 'M1'},
        {'subject_id': 2, 'session_id': 2, 'session_date': date(2024, 6, 8), 'experimenter': 'Bob', 'brain_region': 'M1'},
        {'subject_id': 3, 'session_id': 1, 'session_date': date(2024, 6, 3), 'experimenter': 'Charlie', 'brain_region': 'Hippocampus'},
        {'subject_id': 3, 'session_id': 2, 'session_date': date(2024, 6, 10), 'experimenter': 'Alice', 'brain_region': 'Hippocampus'},
        {'subject_id': 4, 'session_id': 1, 'session_date': date(2024, 6, 4), 'experimenter': 'Bob', 'brain_region': 'PFC'},
        {'subject_id': 4, 'session_id': 2, 'session_date': date(2024, 6, 12), 'experimenter': 'Charlie', 'brain_region': 'PFC'},
        {'subject_id': 5, 'session_id': 1, 'session_date': date(2024, 6, 6), 'experimenter': 'Alice', 'brain_region': 'Striatum'},
        {'subject_id': 5, 'session_id': 2, 'session_date': date(2024, 6, 15), 'experimenter': 'Bob', 'brain_region': 'Striatum'},
    ]
    Session.insert(sessions, skip_duplicates=True)
    print(f" Inserted {len(sessions)} sessions")
    
    # Insert 20 recordings
    recordings = [
        # Subject 1, Session 1
        {'subject_id': 1, 'session_id': 1, 'recording_id': 1, 'recording_time': time(9, 30), 'num_channels': 32, 'sampling_rate': 30000.0},
        {'subject_id': 1, 'session_id': 1, 'recording_id': 2, 'recording_time': time(10, 15), 'num_channels': 32, 'sampling_rate': 30000.0},
        # Subject 1, Session 2
        {'subject_id': 1, 'session_id': 2, 'recording_id': 1, 'recording_time': time(9, 45), 'num_channels': 32, 'sampling_rate': 30000.0},
        {'subject_id': 1, 'session_id': 2, 'recording_id': 2, 'recording_time': time(11, 0), 'num_channels': 32, 'sampling_rate': 30000.0},
        # Subject 2, Session 1
        {'subject_id': 2, 'session_id': 1, 'recording_id': 1, 'recording_time': time(10, 0), 'num_channels': 64, 'sampling_rate': 25000.0},
        {'subject_id': 2, 'session_id': 1, 'recording_id': 2, 'recording_time': time(11, 30), 'num_channels': 64, 'sampling_rate': 25000.0},
        # Subject 2, Session 2
        {'subject_id': 2, 'session_id': 2, 'recording_id': 1, 'recording_time': time(9, 15), 'num_channels': 64, 'sampling_rate': 25000.0},
        {'subject_id': 2, 'session_id': 2, 'recording_id': 2, 'recording_time': time(10, 45), 'num_channels': 64, 'sampling_rate': 25000.0},
        # Subject 3, Session 1
        {'subject_id': 3, 'session_id': 1, 'recording_id': 1, 'recording_time': time(8, 30), 'num_channels': 128, 'sampling_rate': 20000.0},
        {'subject_id': 3, 'session_id': 1, 'recording_id': 2, 'recording_time': time(9, 45), 'num_channels': 128, 'sampling_rate': 20000.0},
        # Subject 3, Session 2
        {'subject_id': 3, 'session_id': 2, 'recording_id': 1, 'recording_time': time(10, 30), 'num_channels': 128, 'sampling_rate': 20000.0},
        {'subject_id': 3, 'session_id': 2, 'recording_id': 2, 'recording_time': time(11, 15), 'num_channels': 128, 'sampling_rate': 20000.0},
        # Subject 4, Session 1
        {'subject_id': 4, 'session_id': 1, 'recording_id': 1, 'recording_time': time(9, 0), 'num_channels': 32, 'sampling_rate': 30000.0},
        {'subject_id': 4, 'session_id': 1, 'recording_id': 2, 'recording_time': time(10, 30), 'num_channels': 32, 'sampling_rate': 30000.0},
        # Subject 4, Session 2
        {'subject_id': 4, 'session_id': 2, 'recording_id': 1, 'recording_time': time(8, 45), 'num_channels': 32, 'sampling_rate': 30000.0},
        {'subject_id': 4, 'session_id': 2, 'recording_id': 2, 'recording_time': time(10, 0), 'num_channels': 32, 'sampling_rate': 30000.0},
        # Subject 5, Session 1
        {'subject_id': 5, 'session_id': 1, 'recording_id': 1, 'recording_time': time(9, 30), 'num_channels': 64, 'sampling_rate': 25000.0},
        {'subject_id': 5, 'session_id': 1, 'recording_id': 2, 'recording_time': time(11, 0), 'num_channels': 64, 'sampling_rate': 25000.0},
        # Subject 5, Session 2
        {'subject_id': 5, 'session_id': 2, 'recording_id': 1, 'recording_time': time(10, 15), 'num_channels': 64, 'sampling_rate': 25000.0},
        {'subject_id': 5, 'session_id': 2, 'recording_id': 2, 'recording_time': time(11, 45), 'num_channels': 64, 'sampling_rate': 25000.0},
    ]
    Recording.insert(recordings, skip_duplicates=True)
    print(f" Inserted {len(recordings)} recordings")
    
    print("\n=== Data Population Complete ===")

def display_summary():
    """Display summary of database contents"""
    print("\n=== Database Summary ===")
    print(f"Total Subjects: {len(Subject())}")
    print(f"Total Sessions: {len(Session())}")
    print(f"Total Recordings: {len(Recording())}")
    
    print("\n--- Sample Subjects ---")
    print(Subject())
    
    print("\n--- Sample Sessions ---")
    print(Session())

def compute_all_statistics():
    """
    Compute statistics for all recordings that don't have stats yet.
    This is the magic of Computed tables!
    """
    print("\n=== Computing Recording Statistics ===")
    print(f"Recordings without stats: {len(Recording() - RecordingStats())}")
    
    # This ONE line computes stats for ALL recordings automatically!
    RecordingStats.populate(display_progress=True)
    
    print(f"\nTotal statistics computed: {len(RecordingStats())}")
    print("\n--- Sample Statistics ---")
    print(RecordingStats())



if __name__ == '__main__':
    # populate_sample_data()
    # display_summary()
    compute_all_statistics()