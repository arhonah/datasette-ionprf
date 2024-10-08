from datasette import hookimpl
from datasette.utils.asgi import Response
from jinja2 import Template
from jinja2 import Environment
from jinja2 import FileSystemLoader
import datetime
import math
from ionodata import get_f2m


signal_colors = {"1": "#ff004b96",
                 "0": "#ff004b96",
                 "2": "#ff0000ff",
                 "3": "#ff00a5ff",
                 "4": "#ff00ffff",
                 "5": "#ff00ff00",
                 "6": "#ffff0000",
                 "7": "#ff82004b",
                 "8": "#ffff007f",
                 "9": "#ffffffff",
                 }

def db_to_s(db):
    test_db = int(db)
    if(test_db > 32):
        return "9"
    if(test_db > 27):
        return "8"
    if(test_db > 21):
        return "7"
    if(test_db > 15):
        return "6"
    if(test_db > 8):
        return "5"
    if(test_db > 2):
        return "4"
    if(test_db >= 1):
        return "3"
    return "0"

def load_colors():
    global signal_colors
    signal_colors["1"] = "[" + str(int("96", 16)) + "," + str(int("4b", 16)) + "," +str(int("00", 16)) + "," +str(int("ff", 16)) + "]"
    signal_colors["0"] = "[" + str(int("96", 16)) + "," + str(int("4b", 16)) + "," +str(int("00", 16)) + "," +str(int("ff", 16)) + "]"
    signal_colors["2"] = "[" + str(int("ff", 16)) + "," + str(int("00", 16)) + "," +str(int("00", 16)) + "," +str(int("ff", 16)) + "]"
    signal_colors["3"] = "[" + str(int("ff", 16)) + "," + str(int("a5", 16)) + "," +str(int("00", 16)) + "," +str(int("ff", 16)) + "]"
    signal_colors["4"] = "[" + str(int("ff", 16)) + "," + str(int("ff", 16)) + "," +str(int("00", 16)) + "," +str(int("ff", 16)) + "]"
    signal_colors["5"] = "[" + str(int("00", 16)) + "," + str(int("ff", 16)) + "," +str(int("00", 16)) + "," +str(int("ff", 16)) + "]"
    signal_colors["6"] = "[" + str(int("00", 16)) + "," + str(int("00", 16)) + "," +str(int("ff", 16)) + "," +str(int("ff", 16)) + "]"
    signal_colors["7"] = "[" + str(int("4b", 16)) + "," + str(int("00", 16)) + "," +str(int("82", 16)) + "," +str(int("ff", 16)) + "]"
    signal_colors["8"] = "[" + str(int("7f", 16)) + "," + str(int("00", 16)) + "," +str(int("ff", 16)) + "," +str(int("ff", 16)) + "]"
    signal_colors["9"] = "[" + str(int("ff", 16)) + "," + str(int("ff", 16)) + "," +str(int("ff", 16)) + "," +str(int("ff", 16)) + "]"
    


REQUIRED_COLUMNS = {"tx_lat", "tx_lng", "rx_lat", "rx_lng", "Spotter", "dB"}


@hookimpl
def prepare_connection(conn):
    conn.create_function(
        "hello_world", 0, lambda: "Hello world!"
    )

@hookimpl
def register_output_renderer():
    print("made it into the plugin")
    load_colors()
    return {"extension": "czml", "render": render_czml, "can_render": can_render_atom}

def render_czml(
    datasette, request, sql, columns, rows, database, table, query_name, view_name, 
    data):
    from datasette.views.base import DatasetteError
    #print(datasette.plugin_config)
    if not REQUIRED_COLUMNS.issubset(columns):
        raise DatasetteError(
            "SQL query must return columns {}".format(", ".join(REQUIRED_COLUMNS)),
            status=400,
        )
    return Response(
            get_czml(rows),
            content_type="application/vnd.google-earth.kml+xml; charset=utf-8",
            status=200,
        )


def can_render_atom(columns):
    return True
    print(str(REQUIRED_COLUMNS))
    print(str(columns))
    print(str(REQUIRED_COLUMNS.issubset(columns)))
    return REQUIRED_COLUMNS.issubset(columns)

def line_color(rst):
    if(len(str(rst)) == 3):
        return signal_colors[str(rst)[1]] 
    else:
        return signal_colors[db_to_s(rst)]

def is_qso(rst):
    if(len(str(rst)) == 3):
        return True
    else:
        return False
    
def minimum_time(rows):
    min_time = datetime.datetime.strptime('2124-02-02 00:00:00', "%Y-%m-%d %H:%M:%S")
    for row in rows:
        new_time = datetime.datetime.strptime(row['timestamp'].replace('T',' '), "%Y-%m-%d %H:%M:%S")
        if new_time < min_time:
            min_time = new_time
    print('found min_time = ' + str(min_time))
    return min_time
    

def maximum_time(rows):
    max_time = datetime.datetime.strptime('1968-02-02 00:00:00', "%Y-%m-%d %H:%M:%S")
    for row in rows:
        new_time = datetime.datetime.strptime(row['timestamp'].replace('T',' '), "%Y-%m-%d %H:%M:%S")
        if new_time > max_time:
            max_time = new_time
    return max_time    

#Returns the total number of minutes before the first and last QSOs + 5
def time_span(rows):
    #find the largest time
    max_time = datetime.datetime.strptime('1968-02-02 00:00:00', "%Y-%m-%d %H:%M:%S")
    for row in rows:
        new_time = datetime.datetime.strptime(row['timestamp'].replace('T',' '), "%Y-%m-%d %H:%M:%S")
        if new_time > max_time:
            max_time = new_time
    print("max time is " + str(max_time))
    
    min_time = minimum_time(rows)
    print("min time is " + str(min_time))
    span = max_time - min_time
    print(str(span.seconds))
    mins = int(math.ceil(span.seconds/(60)))
    print('minutes ' + str(mins))
    return mins

def get_czml(rows):
    from jinja2 import Template
    map_minutes = []
    qso_ends = []
    f2_start = []
    f2_end = []
    f2_height = []
    f2_lat = []
    f2_lng = []
    #not used yet; eventually pass into get_f2m
    f2_station = "EA653"
    mins = time_span(rows)
    print("mins " + str(mins))
    #get the array of minutes ready to go
    map_time = minimum_time(rows)
    for minute in range(mins):
      map_time_str = str(map_time + datetime.timedelta(0,60))
      map_time_str = map_time_str.replace(' ', 'T')
      map_minutes.append(map_time_str)
      map_time = map_time + datetime.timedelta(0,60)
    #Add an end time for each QSO of one minute later (for now)
    f2delta = datetime.timedelta(minutes=5)
    delta = datetime.timedelta(minutes=1)
    for row in rows:
        print(row['timestamp'])
        start_time = datetime.datetime.strptime(row['timestamp'].replace('T',' '), "%Y-%m-%d %H:%M:%S")
        end_time = start_time + delta
        qso_ends.append(datetime.datetime.strftime(end_time, '%Y-%m-%d %H:%M:%S').replace(' ','T'))
        #F2 window
        f2s = datetime.datetime.strptime(row['timestamp'].replace('T',' '), "%Y-%m-%d %H:%M:%S") - f2delta
        f2_start.append(f2s)
        f2e = f2s + f2delta + f2delta
        f2_end.append(f2e)
        #f2h = get_f2m(f2s, f2e, row['ionosonde'])
        #print(row['Spotter'] + " f2 height = " + str(f2h) + "km")
        #f2_height.append(f2h*1000)

        
        
            

    with open('./plugins/templates/qso_map_header.czml') as f:
        #tmpl = Template(f.read())
        tmpl = Environment(loader=FileSystemLoader("./plugins/templates")).from_string(f.read())
        tmpl.globals['line_color'] = line_color
        tmpl.globals['is_qso'] = is_qso
        mit = minimum_time(rows) - delta
        mat = maximum_time(rows) + delta
        mintime = str(mit).replace(' ', 'T')
        #display all the QSOs for a few seconds at the beginning of the maps
        delta = datetime.timedelta(minutes=0.3)
        tmb = mit - delta
        tme = mit + delta
        totmapend=str(tme).replace(' ', 'T')
        totmapbegin=str(tmb).replace(' ', 'T')
        maxtime=str(mat).replace(' ', 'T')
    return(tmpl.render(
        kml_name = 'my first map',
        Rows = rows,
        Map_minutes = map_minutes,
        QSO_ends = qso_ends,
        MinTime = mintime,
        MaxTime = maxtime,
        TotMapEnd = totmapend,
        TotMapBegin = totmapbegin,
        F2Height = f2_height,
        F2Lat = f2_lat,
        F2Lng = f2_lng,
    ))
