from urllib import request, parse
from urllib.error import HTTPError, URLError
from socket import timeout

from PIL import Image


# HTTP request timeout, in seconds.
TIMEOUT = 300
# Can request a maximum of 10,000 numbers at a time via the API, so loop and split the request until we have enough
MAX_NUMBERS_IN_REQUEST = 10000
WIDTH = 128
HEIGHT = 128


class APIRequest:
    def __init__(self, base_url, params):
        self.base_url = base_url
        self.params = params

    def get_url(self):
        return self.base_url + '?' + parse.urlencode(self.params)


def main():
    # Random.org's API has a quota of how much data you're allowed to use. If exceeded, all requests will return 503
    if check_quota():
        print('Quota is fine, proceeding with image generation')
        generate_random_image(WIDTH, HEIGHT)
    else:
        print('Quota exceeded, not sending a request')


def generate_random_image(width, height):
    print('Generating a random image of size ' + str(width) + 'x' + str(height))
    num_pixels = width * height

    # Generate three random values per pixel in the image
    raw_values = generate_int_values(0, 255, num_pixels * 3)

    # Split the response array into three equal sets
    r_values = raw_values[:num_pixels]
    g_values = raw_values[num_pixels:num_pixels * 2]
    b_values = raw_values[num_pixels * 2:]

    image = Image.new('RGB', (width, height))
    raw_pixels = image.load()
    n = 0

    # Iterate over all pixels in the image, setting their RGB values
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            raw_pixels[i, j] = (r_values[n], g_values[n], b_values[n]) #TODO: Add alpha channel?
            n += 1

    # Display the generated image and write it to a file on disk
    image.show()
    image.save('Output.bmp', 'bmp')


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
