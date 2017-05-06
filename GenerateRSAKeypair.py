from urllib import request, parse
from urllib.error import HTTPError, URLError
from socket import timeout
from math import gcd
import sympy
import random

# HTTP request timeout, in seconds.
TIMEOUT = 300

# Can request a maximum of 10,000 numbers at a time via the API, so loop and split the request until we have enough
MAX_NUMBERS_IN_REQUEST = 10000

# Thanks to https://stackoverflow.com/questions/13427890/how-can-i-find-all-prime-numbers-in-a-given-range
MIN_PRIME = 5
MAX_PRIME = 25
PRIMES = list(sympy.sieve.primerange(MIN_PRIME, MAX_PRIME))


class APIRequest:
    def __init__(self, base_url, params):
        self.base_url = base_url
        self.params = params

    def get_url(self):
        return self.base_url + '?' + parse.urlencode(self.params)


def main():
    # Random.org's API has a quota of how much data you're allowed to use. If exceeded, all requests will return 503
    #if check_quota():
    #    print('Quota is fine, proceeding with RSA Keypair generation')
    keypair = generate_rsa()
    print(keypair)
    #else:
    #    print('Quota exceeded, not sending a request')


# Thanks to https://simple.wikipedia.org/wiki/RSA_(algorithm)
# And https://asecuritysite.com/Encryption/rsa
def generate_rsa():
    p = generate_p()
    print('p is ' + str(p))

    q = generate_q()
    print('q is ' + str(q))

    n = p * q
    print('n is ' + str(n))

    totient = (p - 1) * (q - 1)
    print('Totient is ' + str(totient))

    e = generate_e(totient)
    print('e is ' + str(e))

    d = generate_d(totient, e)

    return [{'Public', (n, e)}, {'Private', (n, d)}]


# Unfortunately, I exceeded my random.org API request quota while testing the image generation
# But I'll try to get it working using the built-in Python random package
def generate_p():
    return random.choice(PRIMES)


def generate_q():
    return random.choice(PRIMES)


def generate_e(totient):
    e = 2

    while gcd(e, totient) > 1:
        if e == totient:
            raise Exception('Could not generate e! Generated values for p and q were poor. Please run this tool again.')
        e += 1

    return e


def generate_d(totient, e):
    d = 0.5
    k = 1

    while not d.is_integer():
        #print('d not integer (' + str(d) + ')')
        k += 1
        d = ((k * totient) + 1) / e
        #print('calculating new d (' + str(k) + ' * ' + str(totient) + ' / ' + str(e) + ') = ' + str(d))

    print('Found d: ' + str(d) + '(k was ' + str(k) + ')')
    return d


def generate_int_values(rand_min, rand_max, num_to_generate):
    output = ''

    while num_to_generate != 0:
        num_to_request = num_to_generate if num_to_generate < MAX_NUMBERS_IN_REQUEST else MAX_NUMBERS_IN_REQUEST

        print('Requesting ' + str(num_to_request) + ' random integers')

        response = send_request(APIRequest('https://www.random.org/integers/',
                                           {'min': str(rand_min),
                                            'max': str(rand_max),
                                            'num': str(num_to_request),
                                            'col': '1',
                                            'format': 'plain',
                                            'base': '10',
                                            'rnd': 'new'}))

        output = output + ' ' + response

        num_to_generate -= num_to_request

    return list(map(int, output.split()))


# Returns the count of how many bits I'm still allowed to request today
def check_quota():
    response = send_request(APIRequest('https://www.random.org/quota/', {'format': 'plain'}))
    decoded = int(response)
    return decoded > 0


# Considered doing this asynchronously, but there's no point at the moment
# since the tool can't do anything until it hears back anyway
def send_request(req):
    try:
        return request.urlopen(req.get_url(), timeout=TIMEOUT).read().decode('utf-8')
    except (HTTPError, URLError) as error:
        print('Request for ' + req.get_url() + ' caused an error!\n' + str(error))
    except timeout:
        print('Request for ' + req.get_url() + ' timed out!')


if __name__ == '__main__':
    main()
