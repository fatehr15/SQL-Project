# Configuring Local PostgreSQL Database Connection

## Current Connection Settings

The application is configured to connect to:
- **Host**: `localhost` (127.0.0.1)
- **Port**: `5432` (default PostgreSQL port)
- **Database**: `university_db`
- **Username**: `postgres`
- **Password**: Currently set to empty string

## Option 1: Set Password in db_connection.py (Recommended)

If your PostgreSQL has a password, update `db_connection.py` line 141:

```python
password=os.getenv('DB_PASSWORD', 'your_actual_password')
```

## Option 2: Configure PostgreSQL for Trust Authentication (Local Only)

If you want to allow local connections without a password:

1. Find PostgreSQL configuration file `pg_hba.conf`:
   - Usually at: `C:\Program Files\PostgreSQL\18\data\pg_hba.conf`
   - Or check pgAdmin: Right-click server → Properties → "hba_file" path

2. Edit `pg_hba.conf` and change this line:
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            scram-sha-256
   ```
   To:
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            trust
   ```

3. Restart PostgreSQL service:
   - Open Services (Windows key → "services")
   - Find "postgresql-x64-18" (or your version)
   - Right-click → Restart

**Warning**: This disables password authentication for local connections. Only use on secure local machines.

## Option 3: Use Environment Variable

Set password before running:
```powershell
$env:DB_PASSWORD = "your_password"
python "Part2\Python App\App.py"
```

## Option 4: Create .pgpass File (Windows)

Create a file at: `C:\Users\ram com\AppData\Roaming\postgresql\pgpass.conf`

Format:
```
localhost:5432:university_db:postgres:your_password
```

Set file permissions (readable only by you).

## Verify Connection

Test the connection:
```powershell
python "Part2\Python App\test_connection.py"
```

Or use pgAdmin to verify you can connect with your credentials.

