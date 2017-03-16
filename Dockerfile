FROM superphy/backend:working

COPY ./app /app

COPY /app/supervisord-rq.conf /etc/supervisor/conf.d/supervisord.conf

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh

ENV PATH /opt/conda/bin:$PATH

ENV PATH /opt/conda/envs/backend/bin:$PATH

RUN cat /etc/supervisor/conf.d/supervisord.conf
RUN which python
RUN which conda
RUN which uwsgi
RUN which rq

CMD ["/usr/bin/supervisord"]
