#!/bin/bash
supervisord -c /etc/supervisor/supervisord.conf
tail -f /app_pipeline/run_pipeline.sh