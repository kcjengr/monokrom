# Process Database

The process database stores cut parameters (pierce height, cut height, feed rate, volts,
amps, kerf) indexed by gas type, machine type, material, thickness, and consumable. It is
backed by SQLite and managed through the ProcessFilterService.

## Database Location

The database file is located in the machine configuration directory:

```
~/linuxcnc/configs/sim.monokrom/plasmac/plasma_table.db
```

## Database Schema

The plasma processes plugin creates a SQLite database with the following schema:

```sql
CREATE TABLE cuts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gas TEXT,
    machine TEXT,
    material TEXT,
    thickness REAL,
    consumable TEXT,
    pierce_height REAL,
    pierce_delay REAL,
    cut_height REAL,
    cut_feed_rate REAL,
    cut_volts REAL,
    cut_amperage REAL,
    kerf REAL,
    tool_number INTEGER
);
```

## Accessing the Database

### Via QtPyVCP Plugin

The database is accessed through the `plasmaprocesses` data plugin:

```python
# In config.yml
plasmaprocesses:
  provider: qtpyvcp.plugins.plasma_processes:PlasmaProcesses
  kwargs:
    db_type: "sqlite"
```

### Via SQLite CLI

```bash
sqlite3 plasma_table.db
```

### Common Queries

```sql
-- List all cuts
SELECT * FROM cuts;

-- Find cuts for a specific material
SELECT * FROM cuts WHERE material = 'Mild Steel';

-- Find cuts for a specific thickness
SELECT * FROM cuts WHERE thickness = 3.0;

-- Find cuts matching multiple filters
SELECT * FROM cuts WHERE gas = 'Air' AND material = 'Mild Steel' AND thickness = 6.0;

-- Count cuts per material
SELECT material, COUNT(*) FROM cuts GROUP BY material;

-- Get the highest tool number
SELECT MAX(tool_number) FROM cuts;
```

## Seeding the Database

### From CSV

A seed CSV file (`master-seed-source.csv`) is provided in the config directory. The format:

```csv
gas,machine,material,thickness,consumable,pierce_height,pierce_delay,cut_height,cut_feed_rate,cut_volts,cut_amperage,kerf,tool_number
Air,A120,Mild Steel,3,Standard,5.0,1.0,3.0,1500,28.5,120,1.2,1
Air,A120,Mild Steel,6,Standard,6.0,1.5,4.0,1000,30.0,150,1.5,2
```

To import from CSV, use the PlasmaProcesses plugin API or a custom import script:

```python
import csv
import sqlite3

conn = sqlite3.connect('plasma_table.db')
cursor = conn.cursor()

with open('master-seed-source.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute('''
            INSERT INTO cuts (gas, machine, material, thickness, consumable,
                            pierce_height, pierce_delay, cut_height, cut_feed_rate,
                            cut_volts, cut_amperage, kerf, tool_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['gas'],
            row['machine'],
            row['material'],
            float(row['thickness']),
            row['consumable'],
            float(row['pierce_height']),
            float(row['pierce_delay']),
            float(row['cut_height']),
            float(row['cut_feed_rate']),
            float(row['cut_volts']),
            float(row['cut_amperage']),
            float(row['kerf']),
            int(row['tool_number'])
        ))

conn.commit()
conn.close()
```

### Via the VCP UI

New cuts can be added directly through the VCP:

1. Go to the Parameters tab.
2. Set all filter fields (Gas, Machine, Material, Thickness, Consumable).
3. Enter cut parameters in the PARAMS fields.
4. Click **ADD NEW CUT**.

The tool number is auto-incremented.

## Multi-Field Filtering

The process database supports filtering by any combination of fields:

| Filter Field | Type | Example Values |
|-------------|------|----------------|
| Gas | Text | Air, Oxygen, Nitrogen |
| Machine | Text | A120, Hypertherm 45, Hypertherm 85 |
| Material | Text | Mild Steel, Stainless Steel, Aluminum |
| Thickness | Real (float) | 1.0, 3.0, 6.0, 10.0, 12.0 |
| Consumable | Text | Standard, Extended Life, HD |

### Filtering Logic

- Each filter field is independent.
- Selecting a value for a filter restricts results to that value.
- Unselected filters match all values.
- The SUB-LIST shows all matching cuts.
- Selecting a row from the SUB-LIST loads that cut's parameters.

### Example Filter Combinations

**All Air cuts on Mild Steel:**
- Gas = Air
- Material = Mild Steel
- Machine, Thickness, Consumable = (unselected)

**All 6mm cuts regardless of material:**
- Thickness = 6.0
- All other filters = (unselected)

**Air, A120, 3mm, Standard consumable:**
- Gas = Air
- Machine = A120
- Thickness = 3.0
- Consumable = Standard
- Material = (unselected)

## Updating Cuts

### Via VCP UI

1. Select the cut from the SUB-LIST.
2. Modify the desired parameters in the PARAMS fields.
3. Click **UPDATE CUT**.

### Via SQL

```sql
UPDATE cuts SET cut_feed_rate = 1200 WHERE id = 5;
UPDATE cuts SET pierce_height = 5.5 WHERE material = 'Mild Steel' AND thickness = 3.0;
```

## Deleting Cuts

### Via SQL

```sql
DELETE FROM cuts WHERE id = 5;
DELETE FROM cuts WHERE material = 'Old Material';
```

**Warning:** Deleting cuts via SQL bypasses the VCP's confirmation dialogs. Use with caution.

## Material Configuration File

When materials are first used, a material configuration file is generated:

```
<machine_name>_material.cfg
```

This file stores material-specific settings and is automatically created/updated by the VCP.

## Switching to MySQL

For networked installations with multiple machines, the database can be switched from SQLite
to MySQL:

### In config.yml

```yaml
plasmaprocesses:
  provider: qtpyvcp.plugins.plasma_processes:PlasmaProcesses
  kwargs:
    db_type: "mysql"
    db_host: "localhost"
    db_port: 3306
    db_name: "monokrom_plasma"
    db_user: "monokrom"
    db_password: "secret"
```

### MySQL Schema

The MySQL schema is automatically created on first connection. The table structure is
identical to the SQLite schema.

### Backup and Migration

```bash
# SQLite backup
cp plasma_table.db plasma_table.db.backup

# Export SQLite to SQL
sqlite3 plasma_table.db .dump > plasma_table.sql

# Import to MySQL
mysql -u monokrom -p monokrom_plasma < plasma_table.sql
```

## Customizing the Database

### Adding Custom Fields

To add custom fields to the cuts table:

1. Modify the database schema:
   ```sql
   ALTER TABLE cuts ADD COLUMN custom_field TEXT;
   ```

2. Update the PlasmaProcesses plugin to handle the new field (requires code modification).

3. Update the VCP UI to display/edit the new field (requires UI modification).

### Custom Database Providers

The `db_type` parameter supports:
- `sqlite` — Default, single-file database
- `mysql` — MySQL/MariaDB for networked installations
- Custom providers can be added by implementing the PlasmaProcesses interface
