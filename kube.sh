#!/bin/bash
set -euf -o pipefail

VERSION=$(date +%Y%m%d%H%M%S)

rm -rf code_to_deploy
rsync -r --exclude=__pycache__ --exclude=data db.sqlite3 generate manage.py omorfi sanaporakone verbs code_to_deploy
mkdir code_to_deploy/generate/data
rsync generate/data/omorfi.generate.hfst code_to_deploy/generate/data/omorfi.generate.hfst

# create a docker image and import it to local registry
sudo docker build -t spk:"$VERSION" . && sudo docker save spk:"$VERSION" | microk8s ctr image import -

template=`cat deployment.yaml.template | sed "s/{{VERSION}}/$VERSION/g"`

# redeploy
echo "$template" | microk8s kubectl apply -f -

# re-expost
microk8s kubectl apply -f service.yaml
