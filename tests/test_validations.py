import os
import pytest
from app.validations import is_valid_url

def test_is_valid_url(monkeypatch):
    monkeypatch.setenv('ALLOWED_DOMAINS', 'example.com,trusted.com')
    monkeypatch.setattr('app.config.Config.ALLOWED_IPS', {
        'MAKE_US1': [
            'us1.make.com',
            '54.209.79.175',
            '54.80.47.193',
            '54.161.178.114'
        ],
        'MAKE_EU2': [
            'eu2.make.com',
            '34.254.1.9',
            '52.31.156.93',
            '52.50.32.186'
        ],
        'MAKE_EU1': [
            'eu1.make.com',
            '54.75.157.176',
            '54.78.149.203',
            '52.18.144.195'
        ]
    })

    # Valid URLs
    assert is_valid_url('http://example.com') == True
    assert is_valid_url('https://trusted.com') == True
    assert is_valid_url('http://us1.make.com') == True
    assert is_valid_url('http://54.209.79.175') == True

    # Invalid URLs
    assert is_valid_url('http://invalid.com') == False
    assert is_valid_url('https://10.0.0.1') == False
    assert is_valid_url('ftp://example.com') == False
