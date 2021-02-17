Via Test Harness
================

A small app for creating signed URLs to view various Via projects with.

## Getting started

 * Add the relevant environment secrets to `conf/secrets.json`
 * Run: `make dev`
 * Visit: https://0.0.0.0:9101/
 * This service runs on SSL with a self signed certificate, so you will need
  to allow it in Chrome
 * You can disable this with `conf/config.json: ssl` option

