import argparse
import os
import plexapi.audio
import plexapi.exceptions
import urllib.parse

from lxml import etree
from plexapi.server import PlexServer
from read_config import read_config, str2bool

parser = argparse.ArgumentParser(description="Imports your iTunes track ratings into your Plex server.")
parser.add_argument("config", help="The YAML configuration file containing user-specific parameters.")
args = parser.parse_args()
CONFIG = read_config(args.config)

log_file = 'last_run.log'
plex_ip = CONFIG['plex']['ip']
plex_token = CONFIG['plex']['token']
lib_name = CONFIG['plex']['library']
itunes_xml_file = CONFIG['itunes']['itunes_xml_file']
log_tracks_with_zero_matches = str2bool( CONFIG['log']['log_tracks_with_zero_matches'] )
log_skipped_tracks = str2bool( CONFIG['log']['log_skipped_tracks'] )

plex_server = PlexServer(plex_ip, plex_token)

plex_lib = plex_server.library.section(lib_name)


class object_with_tracks:
    tracks: dict[str,plexapi.audio.Track] = dict() 


tracks_dict: dict[str,object_with_tracks] = dict()


def hash_all_tracks():

    all_tracks: list[plexapi.audio.Track] = plex_lib.all( libtype = 'track' )

    total_track_count = len( all_tracks )
    track_count = 0

    for track in all_tracks:

        track_count = track_count + 1

        if( track_count % 1000 == 0 ):
            print( f"Processed {track_count/total_track_count:.0%} of tracks..." )

        for track_location in track.locations: 

            track_filename = os.path.basename( track_location )

            if track_filename in tracks_dict:
                tracks_dict[track_filename].tracks[track.key] = track
            else:
                tracks: dict[str,plexapi.audio.Track] = dict()
                tracks[track.key] = track
                
                tracks_dict[track_filename] = object_with_tracks()
                tracks_dict[track_filename].tracks = tracks


track: plexapi.audio.Track
def rate(track):

    # "Track ID", "Rating", "Name", "Artist", "Composer", "Album", "Location"

    track_stats = dict()

    track_stats['successfully_rated'] = 0
    track_stats['skipped_unchanged_rating'] = 0
    track_stats['exception_bad_request'] = 0
    track_stats['exception_not_found'] = 0
    track_stats['exception_undefined'] = 0
    track_stats['no_matches'] = 0
    track_stats['multiple_matches'] = 0

    if 'Location' in track:    

        track_location = track['Location']
        track_filename_url_encoded = os.path.basename( track_location )
        track_filename = urllib.parse.unquote( track_filename_url_encoded )

        if track_filename in tracks_dict:

            track_object: object_with_tracks = tracks_dict[track_filename]
            tracks: dict[str,plexapi.audio.Track] = track_object.tracks

            if( len( tracks ) == 0 ):

                print( f"0 matches for {track_filename}" )
                track_stats['no_matches'] = 1
                return track_stats

            elif( len( tracks ) > 1 ):

                print( f"{len(tracks)} matches for {track_filename}" )
                track_stats['multiple_matches'] = 1
                return track_stats

            else:

                found_track: plexapi.audio.Track = next( iter( tracks.values() ) ) 

                if found_track.userRating == float( track["Rating"] ) / 10.0:

                    if log_skipped_tracks == True:

                        print( f"1 match for {track_location} {found_track}" )
                        print( f"  Skipped rating because the rating has not changed.")
                        
                    track_stats['skipped_unchanged_rating'] = 1
                    return track_stats
                
                else:

                    try:

                        found_track.rate( float( track["Rating"] ) / 10.0 )
                        print( f"1 match for {track_filename} {found_track}" )
                        print( f"  Rated successfully.")
                        track_stats['successfully_rated'] = 1
                        return track_stats
                    
                    except plexapi.exceptions.PlexApiException as e:

                        print( f"1 match for {track_filename} {found_track}" )
                        print( f"  Exception while rating: {e.__cause__}" ) 
                        track_stats['exception_undefined'] = 1
                        return track_stats

        else:
            print( f"0 matches for {track_filename}" )
            track_stats['no_matches'] = 1
            return track_stats
        
    else:
            print( f"0 matches for {track_filename}" )
            track_stats['no_matches'] = 1
            return track_stats
    
    return track_stats
        

def import_ratings():

    tree = etree.parse(itunes_xml_file) 
    root = tree.getroot()

    tracks_key = root.find( ".//key/[.='Tracks']" )
    tracks_dict = tracks_key.getnext()

    tracks = dict()

    for track_dict in tracks_dict.findall('dict'):
        
        track_keys = track_dict.findall('key')

        track = dict()

        track_id = None
        track_rating = None

        for track_info in track_keys:

            if track_info.text in ( "Track ID", "Rating", "Name", "Artist", "Composer", "Album", "Location" ):

                next_text = track_info.getnext().text

                track[track_info.text] = next_text

                if track_info.text == "Track ID":
                    track_id = next_text

                if track_info.text == "Rating":
                    track_rating = next_text

        if track_id != None and track_rating != None:
            tracks[track_id] = track

    tracks_stats = dict()

    tracks_stats['successfully_rated'] = 0
    tracks_stats['skipped_unchanged_rating'] = 0
    tracks_stats['exception_bad_request'] = 0
    tracks_stats['exception_not_found'] = 0
    tracks_stats['exception_undefined'] = 0
    tracks_stats['no_matches'] = 0
    tracks_stats['multiple_matches'] = 0

    attempted_to_rate_tracks_count = 0

    for track in tracks.values():

        attempted_to_rate_tracks_count = attempted_to_rate_tracks_count + 1

        track_stats = rate( track )
        
        tracks_stats['successfully_rated'] += track_stats['successfully_rated']
        tracks_stats['skipped_unchanged_rating'] += track_stats['skipped_unchanged_rating']
        tracks_stats['exception_bad_request'] += track_stats['exception_bad_request']
        tracks_stats['exception_not_found'] += track_stats['exception_not_found']
        tracks_stats['exception_undefined'] += track_stats['exception_undefined']
        tracks_stats['no_matches'] += track_stats['no_matches']
        tracks_stats['multiple_matches'] += track_stats['multiple_matches']

    print()
    print( f"Attempted to rate {attempted_to_rate_tracks_count} track(s)." )
    print( f"Successfully rated {tracks_stats['successfully_rated']} track(s)." )
    print( f"Skipped (Unchanged Rating) {tracks_stats['skipped_unchanged_rating']} track(s)." )
    print( f"Exception (Bad Request) for {tracks_stats['exception_bad_request']} track(s)." )
    print( f"Exception (Not Found) for {tracks_stats['exception_not_found']} track(s)." )
    print( f"Exception (Undefined) for {tracks_stats['exception_undefined']} track(s)." )
    print( f"No matches for {tracks_stats['no_matches']} track(s)." )
    print( f"Multiple matches for {tracks_stats['multiple_matches']} track(s)." )
    print()

if __name__ == '__main__':
    print()
    hash_all_tracks()
    import_ratings()
    print()
