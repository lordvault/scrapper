FROM ubuntu:latest
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    pipx 
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
ENV CHROME_PATH=/usr/bin/google-chrome-stable
RUN ls /usr/lib/python3
#RUN mv /usr/lib/python3.13/EXTERNALLY-MANAGED /usr/lib/python3.13/EXTERNALLY-MANAGED.old
#RUN pip3 install opencv-python pytesseract
RUN pip3 install imagehash google-genai pydoll-python flask --break-system-packages
RUN mkdir scrapperpy
RUN mkdir scrapperpy/results
RUN cd scrapperpy
WORKDIR /scrapperpy
COPY *.py .
ENTRYPOINT [ "python3", "/scrapperpy/hello_world.py" ]