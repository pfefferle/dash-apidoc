#!/bin/sh

httrack http://apidocjs.com/ \
  -O apiDoc.docset/Contents/Resources/Documents,cache -I0 \
  --display=2 --timeout=60 --retries=99 --sockets=7 \
  --connection-per-second=5 --max-rate=250000 \
  --keep-alive --depth=5 --mirror --clean --robots=0 \
  --user-agent '$(httrack --version); dash-apidoc ()' \
  "-*" "+apidocjs.com/*"
