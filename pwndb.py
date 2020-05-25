import re
import requests
import argparse

description = 'Tool to find row on http://pwndb2am4tzkvold.onion\nAuthor: sunny.capt@tuta.io\nVersion: 1.0\n'


pwndb_to_string = lambda data: '\n'.join(' | '.join(f'[{k}] => {v}' for k, v in l.items()) for l in data)


def parse_rows(html: str) -> dict:
    data = re.findall(
        '(Array \(.*\) )', 
        html.replace('\n', ' ').replace('\t', ' ')
    )[0].split('Array')
    data = [l.replace('     ', ' ').strip(' 0123456789').rstrip(') ').lstrip('( ') for l in data]
    return [
        {kv.split('=>')[0].strip('[] '): kv.split('=>')[1].strip() for kv in l.split(' [') if '=>' in kv} 
        for l in data
    ]


def pwndb(email=None, password=None, username_mode=0, hostname_mode=1) -> requests.Response:
    """
    Find row on http://pwndb2am4tzkvold.onion

    :param: email - email to find
    :param: password - password to find
    :param: username_mode - 0 -> equels, 1 -> look like
    :param: hostname_mode - 0 -> equels, 1 -> look like
    """

    assert email is not None or password is not None, 'Set email or password'
    assert (email is not None) ^ (password is not None), 'Set only email or only password'

    if email is not None:
        assert '@' in email, 'Wrong email format'
        data = {
            'luser': email.split('@')[0],
            'domain': email.split('@')[1],
            'luseropr': username_mode,
            'domainopr': hostname_mode,
            'submitform': 'em'
        }
    else:
        data = {
            'password': password,
            'submitform': 'pw'
        }
    response = requests.post(
            'http://pwndb2am4tzkvold.onion/', 
            data=data, 
            proxies={'http': 'socks5h://127.0.0.1:9050'}
    )

    if not response.ok:
        raise Exception(f'HTTP error {response}: {response.text}')

    return parse_rows(response.text)


def cli():
    print(description)
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--email', type=str, default=None, help='Email to find')
    parser.add_argument('-unm', '--username_mode', type=str, default=0, help='0 -> equels (default), 1 -> look like')
    parser.add_argument('-hnm', '--hostname_mode', type=str, default=1, help='0 -> equels, 1 -> look like (default)')
    parser.add_argument('-p', '--password', type=str, default=None, help='Password to find')
    args = parser.parse_args()
    
    try:
        data = pwndb(**args.__dict__)
    except Exception as e:
        print(f'[ERROR]: {e}')
        exit(-1)

    print(pwndb_to_string(data))


if __name__ == '__main__':
    cli()
