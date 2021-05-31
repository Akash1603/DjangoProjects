from oauthlib import common


def random_token_generator(length=255):
    # token in access model had max_length of 255
    return common.generate_token(length=255)
