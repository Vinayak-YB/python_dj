import datajoint as dj

# Configure connection
dj.config['database.host'] = 'localhost'
dj.config['database.user'] = 'root'
dj.config['database.password'] = 'myroot'  # Replace with your actual password

# Test connection
dj.conn()
print("✓ Connected to database successfully!")