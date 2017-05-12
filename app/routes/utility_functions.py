import os
import tarfile
import zipfile
import json
import logging
from modules.loggingFunctions import initialize_logging
from flask import current_app
from werkzeug.utils import secure_filename
from rdflib import URIRef

# logging
log_file = initialize_logging()
log = logging.getLogger(__name__)

def handle_tar(filename, now):
    if tarfile.is_tarfile(filename):
        tar = tarfile.open(filename)
        extracted_dir = os.path.join(
            current_app.config['DATASTORE'] + '/' + now)
        os.mkdir(extracted_dir)
        for member in tar.getmembers():
            if not secure_filename(member.name):
                return 'invalid upload', 500
                # TODO: wipe temp data
        tar.extractall(path=extracted_dir)
        for fn in os.listdir(extracted_dir):
            os.rename(extracted_dir +'/' + fn, extracted_dir +'/'+ now + '-' + fn)
        tar.close()

        # set filename to dir for spfy call
        return extracted_dir

def handle_zip(filename,now):
    z = zipfile.ZipFile(filename,'r')
    extracted_dir = os.path.join(
        current_app.config['DATASTORE'] + '/' + now)
    os.mkdir(extracted_dir)
    for info in z.infolist():
        if not secure_filename(info.filename):
            return 'invalid upload', 500
    z.extractall(path=extracted_dir)
    for fn in os.listdir(extracted_dir):
        os.rename(extracted_dir +'/' + fn, extracted_dir +'/'+ now + '-' + fn)
    z.close()

    # set filename to dir for spfy call
    return extracted_dir

def fix_uri(s):
    '''
    Workaround: Flask's path converter allows slashes, but only a SINGLE slash.
    This adds the second slash.
    Also converts to rdflib.URIRef
    '''
    if 'http:/' in s:
        s = s.replace('http:/', 'http://')
    elif 'https:/' in s:
        s = s.replace('https:/', 'https://')
    uri = URIRef(s)
    return uri

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except:
    return False
  return True

def to_readable(values,readable):
    '''
    Converts URI to human readable form.
    If you want the inverse, call this function with readable.inv
    '''
    st = set()
    if type(values) in (list, set):
        for value in values:
            try:
                st.add(readable[value])
            except:
                log.error('to_readable(): No readable form found for ' + value)
                st.add(value)
        if type(uris) is set:
            return st
        else:
            return list(st)
    else:
        # sent me a single item
        try:
            return readable[values]
        except:
            log.error('to_readable(): No readable form found for ' + values)
            return values
