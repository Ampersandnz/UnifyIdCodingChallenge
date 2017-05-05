import urllib.request
from socket import timeout
from urllib.error import HTTPError, URLError

from PIL import Image
# TODO: Send HTTP requests asynchronously


class APIRequest:
    def __init__(self, url):
        self.url = url
        # TODO: Add customisable param tuples instead of hardcoding into url using urllib.urlencode
        return


def main():
    if check_quota():
        print('Quota is fine')
        generate_random_image(128, 128)
    else:
        print('Quota exceeded, not sending a request')


def generate_random_image(width, height):
    num_pixels = width * height
    raw_values = generate_multiple_int(0, 255, num_pixels * 3)

    r_values = raw_values[:num_pixels]
    g_values = raw_values[num_pixels:num_pixels * 2]
    b_values = raw_values[num_pixels * 2:]

    image = Image.new('RGB', (width, height), 'green')
    raw_pixels = image.load()
    n = 0

    # Iterate over all pixels in the image, setting their RGB values
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            raw_pixels[i, j] = (r_values[n], g_values[n], b_values[n]) #TODO: Add alpha channel?
            n += 1

    image.show()
    image.save('Output.bmp', 'bmp')


def generate_single_int(rand_min, rand_max):
    response = send_request(APIRequest('https://www.random.org/integers/?min=' + str(rand_min) + '&max=' + str(rand_max)
                                       + '&num=1&col=1&format=plain&base=10&rnd=new'))

    return int(response)


def generate_multiple_int(rand_min, rand_max, num_generated):
    output = ''

    while num_generated != 0:
        if num_generated < 10000:
            num_to_request = num_generated
        else:
            num_to_request = 10000

        response = send_request(APIRequest('https://www.random.org/integers/?min=' + str(rand_min) + '&max='
                                           + str(rand_max) + '&num=' + str(num_to_request)
                                           + '&col=1&format=plain&base=10&rnd=new'))

        output = output + ' ' + response

        num_generated -= num_to_request

    return list(map(int, output.split()))


def check_quota():
    response = send_request(APIRequest('https://www.random.org/quota/?format=plain'))
    decoded = int(response)
    return decoded > 0


def send_request(request):
    try:
        return urllib.request.urlopen(request.url, timeout=300).read().decode('utf-8')
    except (HTTPError, URLError) as error:
        print('Request for ' + request.url + ' caused an error!\n' + error)
    except timeout:
        print('Request for ' + request.url + ' timed out!')


if __name__ == '__main__':
    main()
