import datajoint as dj
import numpy as np
from datetime import date, timedelta, time
import matplotlib.pyplot as plt

# Connection
dj.config['database.host'] = 'localhost'
dj.config['database.user'] = 'root'
dj.config['database.password'] = 'myroot'

# Schema
schema = dj.schema('neural_recording_lab')

@schema
class Subject(dj.Manual):
    definition = """
    subject_id : int          
    ---
    subject_name : varchar(50) 
    species : varchar(20)      
    sex : enum('M', 'F')       
    date_of_birth : date       
    """

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
        """
        # Fetch recording info
        recording_info = (Recording & key).fetch1()
        
        # Simulate neural signal data - tril dummy values
        num_channels = recording_info['num_channels']
        sampling_rate = recording_info['sampling_rate']
        duration_seconds = 10  
        
        # Generate synthetic neural data (random signals that look realistic)
        num_samples = int(duration_seconds * sampling_rate)
        
        # Each channel has baseline activity + some spikes
        signal = np.random.randn(num_channels, num_samples) * 10  # Noise
        
        num_spikes = np.random.randint(50, 200)
        for _ in range(num_spikes):
            channel = np.random.randint(0, num_channels)
            spike_time = np.random.randint(0, num_samples - 100)
            spike_amplitude = np.random.uniform(50, 150)
            signal[channel, spike_time:spike_time+100] += spike_amplitude * np.exp(-np.linspace(0, 5, 100))
        
        # Compute statistics across all channels
        mean_amplitude = float(np.mean(np.abs(signal)))
        peak_amplitude = float(np.max(np.abs(signal)))
        noise_level = float(np.std(signal[signal < 20]))  
        
        # Insert the stats data into RecordingStats table
        self.insert1({
            **key,  
            'mean_amplitude': mean_amplitude,
            'peak_amplitude': peak_amplitude,
            'noise_level': noise_level
        })
        
        print(f"  → Mean: {mean_amplitude:.2f} μV, Peak: {peak_amplitude:.2f} μV, "
              f"Noise: {noise_level:.2f} μV")

        pass



def populate_sample_data():
    
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
    print("\n=== Computing Recording Statistics ===")
    print(f"Recordings without stats: {len(Recording() - RecordingStats())}")
    
    RecordingStats.populate(display_progress=True) 
    
    print(f"\nTotal statistics computed: {len(RecordingStats())}")
    print("\n--- Sample Statistics ---")
    print(RecordingStats())


#Visualization PARTS

def visualize_recording_signal(subject_id, session_id, recording_id):
    # Fetch recording info and stats
    key = {'subject_id': subject_id, 'session_id': session_id, 'recording_id': recording_id}
    recording_info = (Recording & key).fetch1()
    stats = (RecordingStats & key).fetch1()
    
    num_channels = recording_info['num_channels']
    sampling_rate = recording_info['sampling_rate']
    duration_seconds = 1 
    
    num_samples = int(duration_seconds * sampling_rate)
    time_axis = np.linspace(0, duration_seconds, num_samples)
    
    # Plotting 4 channels
    channels_to_plot = min(4, num_channels)
    
    fig, axes = plt.subplots(channels_to_plot, 1, figsize=(12, 8))
    fig.suptitle(f'Neural Recording: Subject {subject_id}, Session {session_id}, Recording {recording_id}\n'
                 f'Mean: {stats["mean_amplitude"]:.2f} μV | Peak: {stats["peak_amplitude"]:.2f} μV | '
                 f'Noise: {stats["noise_level"]:.2f} μV', fontsize=12, fontweight='bold')
    
    for ch in range(channels_to_plot):
        # Generate synthetic signal for this channel
        signal = np.random.randn(num_samples) * 10  
        
        # Adding Spikes
        num_spikes = np.random.randint(3, 8)
        for _ in range(num_spikes):
            spike_time = np.random.randint(0, num_samples - 100)
            spike_amplitude = np.random.uniform(50, 150)
            signal[spike_time:spike_time+100] += spike_amplitude * np.exp(-np.linspace(0, 5, 100))
        
        if channels_to_plot == 1:
            ax = axes
        else:
            ax = axes[ch]
        
        # Plot the signal
        ax.plot(time_axis, signal, linewidth=0.5, color='black')
        ax.set_ylabel(f'Channel {ch+1} (μV)', fontsize=10)
        ax.set_xlim([0, duration_seconds])
        ax.grid(True, alpha=0.3)
        
        # Only add x-label to bottom plot
        if ch == channels_to_plot - 1:
            ax.set_xlabel('Time (seconds)', fontsize=10)
    
    plt.tight_layout()
    
    filename = f'recording_S{subject_id}_Sess{session_id}_Rec{recording_id}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f" Saved plot: {filename}")
    plt.show()


def visualize_statistics_summary():
    # Fetch all statistics
    stats_data = RecordingStats.fetch(as_dict=True)
    
    mean_amps = [s['mean_amplitude'] for s in stats_data]
    peak_amps = [s['peak_amplitude'] for s in stats_data]
    noise_levels = [s['noise_level'] for s in stats_data]
    
    # Create figure with 4 subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Recording Statistics Summary - All 20 Recordings', 
                 fontsize=16, fontweight='bold')
    
    # Plot 1: Mean Amplitude Distribution
    axes[0, 0].hist(mean_amps, bins=15, color='skyblue', edgecolor='black', alpha=0.7)
    axes[0, 0].set_xlabel('Mean Amplitude (μV)', fontsize=11)
    axes[0, 0].set_ylabel('Frequency', fontsize=11)
    axes[0, 0].set_title('Distribution of Mean Amplitudes', fontsize=12, fontweight='bold')
    axes[0, 0].axvline(np.mean(mean_amps), color='red', linestyle='--', linewidth=2,
                       label=f'Average: {np.mean(mean_amps):.2f} μV')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Peak Amplitude Distribution
    axes[0, 1].hist(peak_amps, bins=15, color='coral', edgecolor='black', alpha=0.7)
    axes[0, 1].set_xlabel('Peak Amplitude (μV)', fontsize=11)
    axes[0, 1].set_ylabel('Frequency', fontsize=11)
    axes[0, 1].set_title('Distribution of Peak Amplitudes', fontsize=12, fontweight='bold')
    axes[0, 1].axvline(np.mean(peak_amps), color='red', linestyle='--', linewidth=2,
                       label=f'Average: {np.mean(peak_amps):.2f} μV')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Noise Level Distribution
    axes[1, 0].hist(noise_levels, bins=15, color='lightgreen', edgecolor='black', alpha=0.7)
    axes[1, 0].set_xlabel('Noise Level (μV)', fontsize=11)
    axes[1, 0].set_ylabel('Frequency', fontsize=11)
    axes[1, 0].set_title('Distribution of Noise Levels', fontsize=12, fontweight='bold')
    axes[1, 0].axvline(np.mean(noise_levels), color='red', linestyle='--', linewidth=2,
                       label=f'Average: {np.mean(noise_levels):.2f} μV')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Scatter - Peak vs Mean (colored by noise)
    scatter = axes[1, 1].scatter(mean_amps, peak_amps, s=100, alpha=0.6,
                                c=noise_levels, cmap='viridis', edgecolor='black', linewidth=1.5)
    axes[1, 1].set_xlabel('Mean Amplitude (μV)', fontsize=11)
    axes[1, 1].set_ylabel('Peak Amplitude (μV)', fontsize=11)
    axes[1, 1].set_title('Peak vs Mean Amplitude', fontsize=12, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=axes[1, 1])
    cbar.set_label('Noise Level (μV)', fontsize=10)
    
    plt.tight_layout()
    
    plt.savefig('statistics_summary.png', dpi=150, bbox_inches='tight')
    print(" Saved plot: statistics_summary.png")
    plt.show()


if __name__ == '__main__':
    # populate_sample_data()
    # display_summary()
    compute_all_statistics()

    print("\n=== Creating Visualizations ===\n")
    visualize_recording_signal(subject_id=1, session_id=1, recording_id=1)
    visualize_statistics_summary()
    
    print("\n All visualizations complete!")