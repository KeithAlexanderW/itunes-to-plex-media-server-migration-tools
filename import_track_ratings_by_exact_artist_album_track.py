import argparse
import plexapi.exceptions

from lxml import etree
from plexapi.server import PlexServer
from read_config import read_config, str2bool

parser = argparse.ArgumentParser(description="Imports your iTunes track ratings into your Plex Media Server.")
parser.add_argument("config", help="The YAML configuration file containing user-specific parameters.")
args = parser.parse_args()
CONFIG = read_config(args.config)

plex_ip = CONFIG['plex']['ip']
plex_token = CONFIG['plex']['token']
lib_name = CONFIG['plex']['library']
itunes_xml_file = CONFIG['itunes']['itunes_xml_file']
log_tracks_with_zero_matches = str2bool( CONFIG['log']['log_tracks_with_zero_matches'] )
log_skipped_tracks = str2bool( CONFIG['log']['log_skipped_tracks'] )

plex_server = PlexServer(plex_ip, plex_token)

plex_lib = plex_server.library.section(lib_name)

def rate(track):

    # "Track ID", "Rating", "Name", "Artist", "Composer", "Album"

    track_stats = dict()

    track_stats['successfully_rated'] = 0
    track_stats['skipped_unchanged_rating'] = 0
    track_stats['exception_bad_request'] = 0
    track_stats['exception_not_found'] = 0
    track_stats['exception_undefined'] = 0
    track_stats['no_matches'] = 0
    track_stats['multiple_matches'] = 0

    search_filters = dict()
    search_filters['and'] = list()

    if 'Name' in track:
        name_filters = dict()
        name_filters['or'] = list()

        name_unicode_01 = track['Name']
        name_unicode_02 = name_unicode_01.replace( u"\u2019", u"\u0027" ) # right single quote to apostrophe
        name_unicode_03 = name_unicode_01.replace( u"\u0027", u"\u2019" ) # apostrophe to right single quote

        name_filters['or'].append( dict( [ ('track.title=', name_unicode_01 ) ] ) )
        if name_unicode_02 != name_unicode_01:
            name_filters['or'].append( dict( [ ('track.title=', name_unicode_02 ) ] ) )
        if name_unicode_03 != name_unicode_01:
            name_filters['or'].append( dict( [ ('track.title=', name_unicode_03 ) ] ) )

        search_filters['and'].append( name_filters )

    if 'Artist' in track or 'Composer' in track:

        artist_filters = dict()
        artist_filters['or'] = list()

        artist_unicode_01 = track['Artist']
        artist_unicode_02 = artist_unicode_01.replace( u"\u2019", u"\u0027" ) # right single quote to apostrophe
        artist_unicode_03 = artist_unicode_01.replace( u"\u0027", u"\u2019" ) # apostrophe to right single quote
        artist_unicode_04 = artist_unicode_01.replace( u"\u2019", "" ) # right single quote to nothing
        artist_unicode_05 = artist_unicode_01.replace( u"\u0027", "" ) # apostrophe to nothing
        artist_unicode_06 = artist_unicode_01.replace( u"\u2010", "-" ) # hyphen to ASCII dash
        artist_unicode_07 = artist_unicode_01.replace( "-", u"\u2010" ) # ASCII dash to hyphen

        artist_filters['or'].append( dict( [ ('artist.title=', artist_unicode_01 ) ] ) )
        if artist_unicode_02 != artist_unicode_01:
            artist_filters['or'].append( dict( [ ('artist.title=', artist_unicode_02 ) ] ) )
        if artist_unicode_03 != artist_unicode_01:
            artist_filters['or'].append( dict( [ ('artist.title=', artist_unicode_03 ) ] ) )
        if artist_unicode_04 != artist_unicode_01:
            artist_filters['or'].append( dict( [ ('artist.title=', artist_unicode_04 ) ] ) )
        if artist_unicode_05 != artist_unicode_01:
            artist_filters['or'].append( dict( [ ('artist.title=', artist_unicode_05 ) ] ) )
        if artist_unicode_06 != artist_unicode_01:
            artist_filters['or'].append( dict( [ ('artist.title=', artist_unicode_06 ) ] ) )
        if artist_unicode_07 != artist_unicode_01:
            artist_filters['or'].append( dict( [ ('artist.title=', artist_unicode_07 ) ] ) )

        # if 'Artist' in track:
        #     artist_or_composer_filters['or'].append( dict( [ ('artist.title=', track['Artist'] ) ] ) )

        # if "Composer" in track:
        #      artist_or_composer_filters['or'].append( dict( [ ('artist.title=', track['Composer'] ) ] ) )

        search_filters['and'].append( artist_filters )

    if 'Album' in track:
        album_filters = dict()
        album_filters['or'] = list()

        album_unicode_01 = track['Album']
        album_unicode_02 = album_unicode_01.replace( u"\u2019", u"\u0027" ) # right single quote to apostrophe
        album_unicode_03 = album_unicode_01.replace( u"\u0027", u"\u2019" ) # apostrophe to right single quote

        album_filters['or'].append( dict( [ ('album.title=', album_unicode_01 ) ] ) )
        if album_unicode_02 != album_unicode_01:
            album_filters['or'].append( dict( [ ('album.title=', album_unicode_02 ) ] ) )
        if album_unicode_03 != album_unicode_01:
            album_filters['or'].append( dict( [ ('album.title=', album_unicode_03 ) ] ) )

        search_filters['and'].append( album_filters )

    try:
        track_search_matches = plex_lib.search( libtype = 'track', filters = search_filters )
    except plexapi.exceptions.BadRequest as e:
        # The search resulted in a bad request
        print( f"0 matches for {search_filters}" )
        print( f"  Bad Request Exception: {e.__cause__}" )
        track_stats['exception_bad_request'] = 1
        return track_stats
    except plexapi.exceptions.NotFound:
        # The track is not in the Plex library
        if log_tracks_with_zero_matches == True:
            print( f"0 matches for {search_filters}" )
            print( f"  Not Found Exception: {e.__cause__}" )
        track_stats['exception_not_found'] = 1
        return track_stats 
    
    if len( track_search_matches ) == 0:
        if log_tracks_with_zero_matches == True:
            print( f"0 matches for {search_filters}" )
        track_stats['no_matches'] = 1
        return track_stats

    elif len( track_search_matches ) == 1:
        for found_track in track_search_matches:

            

            if found_track.userRating == float( track["Rating"] ) / 10.0:
                if log_skipped_tracks == True:
                    print( f"1 match for {search_filters} {found_track}" )
                    print( f"  Skipped rating because the rating has not changed.")
                track_stats['skipped_unchanged_rating'] = 1
                return track_stats
            
            else:

                try:
                    found_track.rate( float( track["Rating"] ) / 10.0 )
                    print( f"1 match for {search_filters} {found_track}" )
                    print( f"  Rated successfully.")
                    track_stats['successfully_rated'] = 1
                    return track_stats
                except plexapi.exceptions.PlexApiException:
                    print( f"1 match for {search_filters} {found_track}" )
                    print( f"  Exception while rating: {search_filters} {found_track}" ) 
                    track_stats['exception_undefined'] = 1
                    return track_stats
            
    elif len( track_search_matches ) > 1: 
        print( f"{len( track_search_matches )} matches for {search_filters}" )
        track_stats['multiple_matches'] = 1
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

            if track_info.text in ( "Track ID", "Rating", "Name", "Artist", "Composer", "Album" ):

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
    import_ratings()
