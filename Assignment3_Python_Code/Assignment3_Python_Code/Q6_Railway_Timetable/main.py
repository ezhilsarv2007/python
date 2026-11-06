import time

# Each train has a name, station tuples and a set of running days.
timetable = {
    "12601": {
        "name": "Chennai Express",
        "stops": [("Chennai", "06:00", "06:10"), ("Katpadi", "08:00", "08:05"), ("Bengaluru", "11:00", "11:10")],
        "days": {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
    },
    "12602": {
        "name": "Coastal Express",
        "stops": [("Chennai", "07:00", "07:10"), ("Tambaram", "07:30", "07:32"), ("Villupuram", "09:00", "09:05")],
        "days": {"Mon", "Wed", "Fri"}
    },
    "12603": {
        "name": "Hill Express",
        "stops": [("Bengaluru", "06:30", "06:40"), ("Katpadi", "09:30", "09:35"), ("Chennai", "12:00", "12:10")],
        "days": {"Tue", "Thu", "Sat"}
    },
    "12604": {
        "name": "City Link",
        "stops": [("Chennai", "08:00", "08:05"), ("Arakkonam", "09:00", "09:03"), ("Katpadi", "10:00", "10:05")],
        "days": {"Mon", "Tue", "Wed", "Thu", "Fri"}
    },
    "12605": {
        "name": "Morning Passenger",
        "stops": [("Tambaram", "05:30", "05:32"), ("Chennai", "06:15", "06:20"), ("Villupuram", "08:30", "08:35")],
        "days": {"Sun"}
    }
}

# Build a station index once, instead of checking every train for each query.
station_index = {}
for train_no, details in timetable.items():
    for station, arrival, departure in details["stops"]:
        station_index.setdefault(station, []).append((train_no, arrival, departure))

def find_trains(station, day):
    matches = []
    for train_no, details in timetable.items():
        if day not in details["days"]:
            continue
        for stop, arrival, departure in details["stops"]:
            if stop == station:
                matches.append((train_no, details["name"], arrival, departure))
    return sorted(matches, key=lambda item: item[3])

def find_trains_with_index(station, day):
    matches = []
    for train_no, arrival, departure in station_index.get(station, []):
        if day in timetable[train_no]["days"]:
            matches.append((train_no, timetable[train_no]["name"], arrival, departure))
    return sorted(matches, key=lambda item: item[3])

station = "Chennai"
day = "Mon"
print(f"Trains at {station} on {day}:")
for train in find_trains_with_index(station, day):
    print(train)

print("Unknown station:", find_trains_with_index("Unknown", "Mon"))
print("Not running that day:", find_trains_with_index("Chennai", "Sun"))

# Third station departure time of train 12601.
print("Third stop departure:", timetable["12601"]["stops"][2][2])

# Display the full timetable.
for train_no, details in timetable.items():
    print("\\n", train_no, "-", details["name"], "| Days:", sorted(details["days"]))
    for station_name, arrival, departure in details["stops"]:
        print(f"  {station_name:12} Arrival {arrival} Departure {departure}")

# Compare query approaches on the sample timetable.
start = time.perf_counter()
for _ in range(1000):
    find_trains(station, day)
scan_time = time.perf_counter() - start
start = time.perf_counter()
for _ in range(1000):
    find_trains_with_index(station, day)
index_time = time.perf_counter() - start
print(f"1000 queries: full scan={scan_time:.6f}s, indexed={index_time:.6f}s")
