# coding: utf-8
import base64
from io import BytesIO
import numpy
import random

from PIL import Image, ImageFont, ImageDraw, ImageFilter


__all__ = ['Validation']


class Validation(object):

    @classmethod
    def new_validation_code(cls):
        # source: http://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/00140767171357714f87a053a824ffd811d98a83b58ec13000
        # source: http://stackoverflow.com/questions/31826335/how-to-convert-pil-image-image-object-to-base64-string
        # source: https://github.com/lvziwen/generate-identify-code/blob/master/generate_identify_code.py

        # 随机字母:
        def rndChar():
            return chr(random.randint(65, 90))

        # 随机颜色1:
        def rndColor():
            return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

        # 随机颜色2:
        def rndColor2():
            return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

        # 240 x 60:
        width = 100 * 2
        height = 32 * 2
        image = Image.new('RGB', (width, height), (255, 255, 255))

        # 创建Font对象:
        font = ImageFont.truetype('./fonts/LiberationSerif-Bold.ttf', 55)

        # 创建Draw对象:
        draw = ImageDraw.Draw(image)

        # 填充每个像素:
        for x in range(width):
            for y in range(height):
                draw.point((x, y), fill=rndColor())

        # 输出文字:
        char_list = [rndChar() for _ in range(4)]

        for t in range(4):
            draw.text((50 * t, 6), char_list[t], font=font, fill=rndColor2())

        # 模糊:
        image = image.filter(ImageFilter.BLUR)

        # img_str = base64.b64encode(buffer.getvalue())

        # validation_code_id = "".join([str(random.randint(1, 9)) for _ in range(10)])
        # # 设置验证码过期时间60s
        # redis = get_redis_connection()
        # redis.setex(validation_code_id, "".join(char_list).upper(), 600)

        # return validation_code_id, char_list, img_str.decode()
        return numpy.array(image.convert('RGB')), ''.join(char_list)


if __name__ == '__main__':

    for i in range(1000):
        Validation.new_validation_code('data2')
