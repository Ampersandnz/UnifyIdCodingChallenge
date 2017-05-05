from urllib import request, parse
from urllib.error import HTTPError, URLError
from socket import timeout

from PIL import Image
# TODO: Send HTTP requests asynchronously?


class APIRequest:
    def __init__(self, base_url, params):
        self.base_url = base_url
        self.params = params

    def get_url(self):
        return self.base_url + '?' + parse.urlencode(self.params)


def main():
    # Random.org's API has a quota of how much data you're allowed to use. If exceeded, all requests will return 503
    if check_quota():
        print('Quota is fine')
        generate_random_image(128, 128)
    else:
        print('Quota exceeded, not sending a request')


def generate_random_image(width, height):
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


def generate_int_values(rand_min, rand_max, num_generated):
    output = ''

    # Can request a maximum of 10,000 numbers at a time via the API, so loop and split the request until we have enough
    while num_generated != 0:
        if num_generated < 10000:
            num_to_request = num_generated
        else:
            num_to_request = 10000

        response = send_request(APIRequest('https://www.random.org/integers/',
                                           {'min': str(rand_min),
                                            'max': str(rand_max),
                                            'num': str(num_to_request),
                                            'col': '1',
                                            'format':'plain',
                                            'base':'10',
                                            'rnd':'new'}))

        output = output + ' ' + response

        num_generated -= num_to_request

    return list(map(int, output.split()))


# Returns the count of how many bits I'm still allowed to request today
def check_quota():
    response = send_request(APIRequest('https://www.random.org/quota/', {'format': 'plain'}))
    decoded = int(response)
    return decoded > 0


def send_request(req):
    try:
        return request.urlopen(req.get_url(), timeout=300).read().decode('utf-8')
    except (HTTPError, URLError) as error:
        print('Request for ' + req.get_url() + ' caused an error!\n' + str(error))
    except timeout:
        print('Request for ' + req.get_url() + ' timed out!')


if __name__ == '__main__':
    main()
