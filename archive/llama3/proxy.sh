#!/bin/bash

proxy --port 17700 \
    --plugins proxy.plugin.ProxyPoolPlugin \
    --proxy-pool 127.0.0.1:17701 \
    --proxy-pool 127.0.0.1:17702