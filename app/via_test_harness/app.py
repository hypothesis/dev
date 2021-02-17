import json
from flask import Flask, render_template, request
from h_vialib import ViaClient


def _get_config():
    """Load config from the conf directory."""

    with open('conf/config.json') as handle:
        config = json.load(handle)

    with open('conf/secrets.json') as handle:
        config['secrets'] = json.load(handle)

    return config


def _get_url(app_config, secrets, urls):
    """Get a list of signed URLs."""

    if not urls:
        return None

    secret = secrets[app_config['env']]

    if not secret:
        return None

    app_type = app_config['type']
    host_url = None

    if app_type == "viahtml":
        client = ViaClient(
            secret=secret,
            host_url=host_url,
            service_url=None,
            html_service_url=app_config['prefix']
        )

        return [
            client.url_for(url, content_type="html")
            for url in urls
        ]

    elif app_type == "via3":
        client = ViaClient(
            secret=secret,
            host_url=host_url,
            service_url=app_config['prefix'],
            html_service_url=None
        )

        return [client.url_for(url) for url in urls]

    raise ValueError("Unknown app type")


config = _get_config()
app = Flask(__name__)


@app.route('/')
def root():
    app = request.args.get('app')
    raw_urls = request.args.get('urls', '').strip()

    if app and raw_urls:
        urls = [url.strip() for url in raw_urls.split('\n')]
        urls = [url for url in urls if url]

        via_urls = _get_url(config['apps'][app], config['secrets'], urls)
    else:
        via_urls = None

    return render_template(
        "ui.html.jinja2",
        config=config, app=app, urls=raw_urls, via_urls=via_urls
    )


if __name__ == '__main__':
    app.run(
        '0.0.0.0', port='9101', debug=True,
        # Run a self signed certificate
        ssl_context="adhoc" if config['ssl'] else None
    )