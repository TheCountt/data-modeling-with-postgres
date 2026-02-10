import os
import glob
import pandas as pd
import sqlite3  # Changed from psycopg2 to sqlite3
from sql_queries import *



def process_song_file(cur, filepath):
    """
    Process songs files and insert records into the SQLite database.
    :param cur: cursor reference (your database assistant)
    :param filepath: complete file path for the file to load
    """
    # open song file
    df = pd.DataFrame([pd.read_json(filepath, typ='series', convert_dates=False)])
    # Creates: [ [song_data1], [song_data2], ... ]
    
    for value in df.values:
        # Extract song information (like unpacking a music album)
        num_songs, artist_id, artist_latitude, artist_longitude, \
        artist_location, artist_name, song_id, title, duration, year = value

        # insert artist record (add artist to our library). Build artist tuple and insert
        artist_data = (artist_id, artist_name, artist_location,
                       artist_latitude, artist_longitude)
        cur.execute(artist_table_insert, artist_data) # SQL: INSERT INTO artists

        # insert song record (add song to our library). Build song tuple and insert  
        song_data = (song_id, title, artist_id, year, duration)
        cur.execute(song_table_insert, song_data) # SQL: INSERT INTO songs
    
    print(f"Records inserted for file {filepath}")


def process_log_file(cur, filepath):
    """
    Process Event log files and insert records into the sqlite database.
    :param cur: cursor reference
    :param filepath: complete file path for the file to load
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df['page'] == "NextSong"].astype({'ts': 'datetime64[ms]'})

    # convert timestamp column to datetime
    t = pd.Series(df['ts'], index=df.index)
    
    # insert time data records
    column_labels = ["timestamp", "hour", "day", "weekofyear", "month", "year", "day_name"]
    time_data = []
    for data in t:
        time_data.append([data.strftime('%Y-%m-%d %H:%M:%S') ,data.hour, data.day, data.weekofyear, data.month, data.year, data.day_name()])

    time_df = pd.DataFrame.from_records(data = time_data, columns = column_labels)

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[['userId','firstName','lastName','gender','level']]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, list(row))

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = ( row.ts.strftime('%Y-%m-%d %H:%M:%S'), row.userId, row.level, songid, artistid, row.sessionId, row.location, row.userAgent)
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """
    Driver function to load data from songs and event log files into SQLite(Postgres) database.
    :param cur: a database cursor reference
    :param conn: database connection reference
    :param filepath: parent directory where the files exists
    :param func: function to call
    """
    # get all files matching extension from directory. List to store all found file paths
    all_files = []

    # os.walk traverses all subdirectories
    for root, dirs, files in os.walk(filepath):
         # Find all .json files in current directory
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            # Get absolute path and add to list
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    # print('{} files found in {}'.format(num_files, filepath))
    print(f'{num_files} files found in {filepath}')

    # iterate over files. Process each file
    for i, datafile in enumerate(all_files, 1): # Start counting at 1
         # Call the processing function (process_song_file or process_log_file)
        func(cur, datafile)

        # Commit after each file (save progress)
        conn.commit()

        # Progress tracking
        print('{}/{} files processed.'.format(i, num_files))
        # print(f'{i}/{num_files} files processed.')


def main():
    """
    Driver function for loading songs and log data into SQLite database
    """
    # Connect to SQLite database (single file instead of server)
    conn = sqlite3.connect('sparkifydb.sqlite')  # Changed to SQLite
    cur = conn.cursor()

    # Process song data (music library)
    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    
    # Process log data (user activity)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()  # Close the database when done


if __name__ == "__main__":
    main()
    print("\n\nFinished processing!!!\n\n")