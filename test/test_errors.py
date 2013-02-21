
import httplib2
import wsgi_intercept
import shutil
import os
import sys
import urllib

from tiddlywebplugins.imaker import spawn
import tiddlywebplugins.prettyerror.instance as instance_module
from tiddlywebplugins.prettyerror.config import config as init_config

from tiddlywebplugins.prettyerror import init


from wsgi_intercept import httplib2_intercept

from tiddlyweb.store import Store
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler

def make_test_env():
    try:
        shutil.rmtree('test_instance')
    except OSError:
        pass
    spawn('test_instance', init_config, instance_module)
    os.chdir('test_instance')


def setup_module(module):
    make_test_env()
    from tiddlyweb.web import serve
    from tiddlyweb.config import config
    init(config)
    def app_fn():
        return serve.load_app()
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('0.0.0.0', 8080, app_fn)
    module.store = Store(config['server_store'][0],
            config['server_store'][1], {'tiddlyweb.config': config})
    module.http = httplib2.Http()


def test_selector_404():
    response, content = http.request('http://0.0.0.0:8080/fake',
            method='GET')
    assert response['status'] == '404'
    assert response['content-type'] == 'text/html; charset=UTF-8'
    assert 'Path not found for "/fake"' in content


def test_tiddlyweb_404():
    response, content = http.request('http://0.0.0.0:8080/bags/fake',
            method='GET')
    assert response['status'] == '404'
    assert response['content-type'] == 'text/html; charset=UTF-8'
    assert 'Path not found for "/bags/fake"' in content

def test_plain_output():
    response, content = http.request('http://0.0.0.0:8080/bags/fake',
            method='GET', headers={'Accept': 'application/json'})
    assert response['status'] == '404'
    assert response['content-type'] == 'text/plain; charset=UTF-8'
    assert '404 Not Found: fake not found' in content

def test_404_with_unicode():
    """
    Apparently this bug is only tickled under some wsgi hosts, notably
    apache with mod_wsgi.

    So I thought, to test this some silliness would be require (below)
    but that doesn't tickle the bug either.
    """
    title = urllib.unquote('test%C2%B7test').decode('utf-8')
    store.put(Bag('test'))
    store.put(Tiddler(title, 'test'))
    response, content = http.request('http://0.0.0.0:8080/bags/test/tiddlers/test%C2%B7test')
    assert response['status'] == '200'
    response, content = http.request('http://0.0.0.0:8080/bags/test/tiddlers/test%C2%B7test/revisions/24')
    assert response['status'] == '404', content

    # here's the silly part
    store.environ['silly.code'] = title
    response, content = http.request('http://0.0.0.0:8080/bags/test/tiddlers/test%C2%B7test/revisions/24')
    assert response['status'] == '404', content

def test_explict_accept():
    response, content = http.request('http://0.0.0.0:8080/bags/test/test.js',
            headers={'Accept': 'text/javascript'})
    assert response['status'] == '404', content
    assert 'text/plain' in response['content-type']
