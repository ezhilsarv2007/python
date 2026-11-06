import sqlite3

readings = [("Adyar", "2026-10-01", 48.0), ("Guindy", "2026-10-01", 95.0),
            ("Guindy", "2026-10-03", 121.0), ("Adyar", "2026-10-04", 60.0)]

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE aq (station TEXT, day TEXT, pm25 REAL)")
# TODO 1: Insert all readings with ONE executemany call using ? placeholders, then
#   commit
con.executemany("INSERT INTO aq (station, day, pm25) VALUES (?, ?, ?)", readings)
con.commit()


def station_average(name):
    # TODO 2: Return the average pm25 of the given station using a parameterised SELECT
    #   ... WHERE station = ?
    row = con.execute("SELECT AVG(pm25) FROM aq WHERE station = ?", (name,)).fetchone()
    return row[0]          # AVG of zero rows is NULL, which Python shows as None


print(station_average("Adyar"), station_average("Guindy"))
print(station_average("Adyar' OR '1'='1"))      # an injection attempt finds nothing
con.close()
