# begin Dockerfile
# If you need Python 3 and the GitHub CLI, then use:
FROM cicirello/pyaction:4

# If all you need is Python 3, use:
# FROM cicirello/pyaction-lite:3

# If Python 3 + git is sufficient, then use:
# FROM cicirello/pyaction:3

# To pull from the GitHub Container Registry instead, use one of these:
# FROM ghcr.io/cicirello/pyaction-lite:3
# FROM ghcr.io/cicirello/pyaction:4
# FROM ghcr.io/cicirello/pyaction:3

COPY entrypoint.py /entrypoint.py
COPY requirements.txt /requirements.txt
COPY prompt.py /prompt.py
COPY locale/ /locale/

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir --requirement /requirements.txt

ENTRYPOINT ["/entrypoint.py"]
# end Dockerfile
