import os
import tarfile
import zipfile
import redis
from datetime import datetime
# flask/external lib
from flask import Blueprint, render_template, request, jsonify, current_app, g, url_for, redirect
from rq import Queue
from werkzeug.utils import secure_filename
from flask_recaptcha import ReCaptcha
# spfy code
from modules.spfy import spfy
from routes.utility_functions import handle_tar, handle_zip, fix_uri
from modules.groupComparisons.sparql_queries import get_all_attribute_types, get_attribute_values
bp = Blueprint('main', __name__)

@bp.route('/api/v0/get_attribute_values/type/<path:attributetype>')
def call_get_attribute_values(attributetype):
    '''
    Front-End API:
    Get all attribute values for a given attribute type.
    '''
    # workaround: Flask's path converter allows slashes, but only a SINGLE slash
    # this adds the second slash
    # also convert to a rdflib.URIRef object
    uri = fix_uri(attributetype)
    return jsonify(get_attribute_values(attributeTypeUri=uri))

@bp.route('/api/v0/get_all_attribute_types')
def call_get_all_atribute_types():
    '''
    Front-End API:
    Get all possible attribute types.
    '''
    return jsonify(get_all_attribute_types())

def fetch_job(job_id):
    '''
    Iterates through all queues looking for the job.
    '''
    redis_url = current_app.config['REDIS_URL']
    redis_connection = redis.from_url(redis_url)
    queues = current_app.config['QUEUES_SPFY']
    for queue in queues:
        q = Queue(queue, connection=redis_connection)
        job = q.fetch_job(job_id)
        if job is not None:
            return job
    return "fudge muffins!", 500

@bp.route('/results/<job_id>')
def job_status(job_id):
    job = fetch_job(job_id)
    if job.is_finished:
        return jsonify(job.result)
    elif job.is_failed:
        return job.exc_info, 415
    else:
        return "Still pending", 202

@bp.route('/upload', methods=['POST'])
def upload():
    recaptcha = ReCaptcha(app=current_app)
    if request.method == 'POST':
        if recaptcha.verify():
            form = request.form
            options = {}
            #defaults
            options['amr']=True
            options['vf']=True
            options['serotype']=True
            options['pi']=90

            # processing form data
            for key, value in form.items():
                #we need to convert lower-case true/false in js to upper case in python
                    #remember, we also have numbers
                if not value.isdigit():
                    if value.lower() == 'false':
                        value = False
                    else:
                        value = True
                    if key == 'options.amr':
                        options['amr']=value
                    if key == 'options.vf':
                        options['vf']=value
                    if key == 'options.serotype':
                        options['serotype']=value
                else:
                    if key =='options.pi':
                        options['pi']=int(value)

            # get a list of files submitted
            uploaded_files = request.files.getlist("file")
            print uploaded_files

            #set up constants for identifying this sessions
            now = datetime.now()
            now = now.strftime("%Y-%m-%d-%H-%M-%S-%f")
            jobs_dict = {}

            for file in uploaded_files:
                if file:
                    # for saving file
                    filename = os.path.join(current_app.config[
                                            'DATASTORE'], now + '-' + secure_filename(file.filename))
                    file.save(filename)
                    print 'IVE SAVED YO FILE AT', str(filename)

                    if tarfile.is_tarfile(filename):
                        # set filename to dir for spfy call
                        filename = handle_tar(filename, now)
                    else if zipfile.is_zipfile(filename):
                        filename = handle_zip(filename, now)

                    # for enqueing task
                    jobs_enqueued = spfy(
                        {'i': filename, 'disable_serotype': False, 'disable_amr': False, 'disable_vf': False, 'pi':options['pi'], 'options':options})
                    jobs_dict.update(jobs_enqueued)

                    d = dict(jobs_dict)
                    #strip jobs that the user doesn't want to see
                    # we run them anyways cause we want the data analyzed on our end
                    for job_id, descrip_dict in jobs_dict.items():
                        if (not options['serotype']) and (not options['vf']):
                            if descrip_dict['analysis'] == 'Virulence Factors and Serotype':
                                del d[job_id]
                        if (not options['amr']):
                            if descrip_dict['analysis'] == 'Antimicrobial Resistance':
                                del d[job_id]
                    jobs_dict = d

            return jsonify(jobs_dict)
    return "boo", 500

@bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")