import json
import os
import pytest
import requests

from urllib.parse import urlencode
from unittest import mock


class MathjsClient:

    @classmethod
    def from_request(cls, request):
        if 'MATHJS_BASE_URL' in os.environ:
            base_url = os.getenv('MATHJS_BASE_URL')
        elif hasattr(request.instance, 'mathjs_base_url'):
            base_url = getattr(request.instance, 'mathjs_base_url')
        elif hasattr(request.cls, 'mathjs_base_url'):
            base_url = getattr(request.cls, 'mathjs_base_url')
        elif hasattr(request.module, 'mathjs_base_url'):
            base_url = getattr(request.module, 'mathjs_base_url')
        else:
            base_url = 'http://api.mathjs.org/v4/'
        return MathjsClient(base_url)

    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, expr, precision=None):
        params = {'expr': expr}
        if precision is not None:
            params['precision'] = precision
        return self.get_raw(urlencode(params))

    def get_raw(self, params):
        response = requests.get(f'{self.base_url}?{params}')
        response.raise_for_status()
        return response.text

    def post(self, *exprs, precision=None):
        content = {'expr': list(exprs)}
        if precision is not None:
            content['precision'] = precision
        response = requests.post(self.base_url, json=content)
        response.raise_for_status()
        return json.loads(response.text)['result']

    def post_raw(self, text, headers):
        response = requests.post(self.base_url, data=text, headers=headers)
        response.raise_for_status()
        return response.text


@pytest.fixture
def mathjs(request):
    return MathjsClient.from_request(request)


class TestExpr:

    def test_string(self, mathjs):
        with pytest.raises(requests.exceptions.HTTPError):
            mathjs.get('a-string')

    def test_missing_expr(self, mathjs):
        with pytest.raises(requests.exceptions.HTTPError):
            mathjs.get_raw('')

    def test_no_value(self, mathjs):
        assert mathjs.get('') == 'undefined'


class TestExtraParams:

    def test_extra_param_ignored(self, mathjs):
        assert mathjs.get_raw('expr=2-1&param1=1') == '1'


class TestGetEncoding:

    def test_encoded_url(self, mathjs):
        assert mathjs.get('1+2') == '3'

    def test_non_encoded_url(self, mathjs):
        with pytest.raises(requests.exceptions.HTTPError):
            mathjs.get_raw('expr=1+2')


class TestPrecision:

    def test_default_precision(self, mathjs):
        assert mathjs.get('1/3') == '0.3333333333333333'

    def test_0_value(self, mathjs):
        assert mathjs.get('1/3', precision=0) == '0.3333333333333333'

    def test_precision_with_value(self, mathjs):
        assert mathjs.get('1/3', precision=3) == '0.333'

    def test_max_value(self, mathjs):
        assert mathjs.get('1/3', precision=17) == '0.3333333333333333'

    def test_negative_value(self, mathjs):
        """ Not sure if this is a valid value but I assume it is """
        assert mathjs.get('1/3', precision=-1) == '00'


class InvalidOperations:

    def test_div_0(self, mathjs):
        """ I assume this value as correct although it should return NaN [
        https://en.wikipedia.org/wiki/Division_by_zero] """
        assert mathjs.get('1/0') == 'Infinity'


class TestConfigurableUrl:
    """ This is not testing the calculator functionality but the framework. Usually I don't test code used in tests
        unless it is package that can be used in different projects or there is a specific reason to do so.
    """

    @pytest.fixture
    def m_request(self):
        request = mock.Mock()
        del request.instance.mathjs_base_url
        del request.cls.mathjs_base_url
        del request.module.mathjs_base_url
        return request

    def test_base_url_from_env_var(self, m_request, monkeypatch):
        monkeypatch.setenv('MATHJS_BASE_URL', 'http://my-url')
        client = MathjsClient.from_request(m_request)
        assert client.base_url == 'http://my-url'

    def test_base_url_from_module(self, m_request):
        m_request.module.mathjs_base_url = 'http://module-url/'
        client = MathjsClient.from_request(m_request)
        assert client.base_url == 'http://module-url/'

    def test_base_url_from_cls(self, m_request):
        m_request.cls.mathjs_base_url = 'http://cls-url/'
        client = MathjsClient.from_request(m_request)
        assert client.base_url == 'http://cls-url/'

    def test_base_url_from_instance(self, m_request):
        m_request.instance.mathjs_base_url = 'http://instance-url/'
        client = MathjsClient.from_request(m_request)
        assert client.base_url == 'http://instance-url/'


class TestPost:

    def test_post(self, mathjs):
        result = mathjs.post('a = 1.2 * (2 + 4.5)', "a / 2")
        assert result[0] == '7.8'
        assert result[1] == '3.9'

    def test_no_content(self, mathjs):
        with pytest.raises(requests.HTTPError):
            mathjs.post_raw('', {'Content-Type': 'application/json'})

    def test_no_json_header(self, mathjs):
        response = mathjs.post_raw('{"expr":["1+1"]}', headers={})
        assert response == '{"result":["2"],"error":null}'

    def test_empty_json(self, mathjs):
        with pytest.raises(requests.HTTPError):
            mathjs.post_raw('{}', {'Content-Type': 'application/json'})

    def test_json_with_extra_values(self, mathjs):
        with pytest.raises(requests.HTTPError):
            mathjs.post_raw('{"expr":["1+1"], a: 1}', {'Content-Type': 'application/json'})


class TestPostPrecision:

    def test_precision(self, mathjs):
        result = mathjs.post('1/3', '2/3', precision=1)
        assert result[0] == '0.3'
        assert result[1] == '0.7'

    def test_max_value(self, mathjs):
        result = mathjs.post('1/3', '2/3', precision=0)
        assert result[0] == '0.3333333333333333'
        assert result[1] == '0.6666666666666666'

    def test_value_0(self, mathjs):
        result = mathjs.post('1/3', '2/3', precision=17)
        assert result[0] == '0.3333333333333333'
        assert result[1] == '0.6666666666666666'

    def test_negative_value(self, mathjs):
        result = mathjs.post('1/3', '2/3', precision=-2)
        assert result[0] == '000'
        assert result[1] == '000'

    def test_empty_string_value(self, mathjs):
        mathjs.post('1/3', '2/3', precision='')


class TestOperationErrors:

    def test_divide_by_0(self, mathjs):
        result = mathjs.post('1+1', '2/0')
        assert result[0] == '2'
        assert result[1] == 'Infinity'
