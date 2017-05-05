import urllib.request


class APIRequest:
    def __init__(self, url):
        self.url = url
        return

    # TODO


def main():
    if (check_quota()):
        print('Quota is fine')
    else:
        print('Quota exceeded, not sending a request')
    return


def check_quota():
    response = send_request(APIRequest('https://www.random.org/quota/?format=plain'))
    converted = response_to_int(response)
    return converted > 0


def send_request(request):
    return urllib.request.urlopen(request.url).read()


def response_to_int(response):
    return int(response.decode("utf-8"))

if __name__ == '__main__':
    main()
