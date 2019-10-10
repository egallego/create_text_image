from abc import ABCMeta, abstractmethod
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from os.path import join


class ImageCreator(object):
    __metaclass__ = ABCMeta

    def __init__(self, font, name=None, color='black', size=(600, 600),
                 font_size=60, xmin=60, max_length=12, x_signature=320, scale_name=0.7):

        self.name = name

        if color == 'black':
            background_color = (0, 0, 0)
            text_color = (255, 255, 255)
        else:
            background_color = (255, 255, 255)
            text_color = (0, 0, 0)

        # Image parameters
        self.background_color = background_color
        self.text_color = text_color
        self.size = size
        self.xmin = xmin
        self.max_length = max_length

        # font parameters
        self.font_size = font_size
        self.x_signature = x_signature
        self.font = ImageFont.truetype(join('./fonts', font), self.font_size)
        self.font_author = ImageFont.truetype(join('./fonts', font), int(self.font_size * 0.7))
        self.font_signature = ImageFont.truetype(join('./fonts', font), int(self.font_size * scale_name))
        self.created_image = None
        self.base_image = None
        self.txt_base_image = None

    @property
    def image(self):
        return self.created_image

    def create_image(self, text, author=None):
        """
        Put text on image

        Parameters
        ----------
        text: str
        author: str

        Returns
        -------

        """

        # call the method to create the base images
        self.create_base_images()

        # define lines in which the text is split
        formated_text = self.format_input_text(text)
        lines_print = self.define_text_format(formated_text)

        # Add author if we have it
        if author:
            lines_print.append(author)

        # define y axis position
        y_positions = self.define_y_position(lines_print)

        # insert text into image
        self.insert_text_image(lines_print, y_positions)

        self.created_image = Image.alpha_composite(self.base_image, self.txt_base_image)

    def create_base_images(self):
        """
        Creates base image

        """

        # create the base image
        base_image = Image.new('RGBA', self.size, self.background_color)

        # make a blank image for the text
        txt_base_image = Image.new('RGBA', self.size, self.background_color)

        # stores into the object
        self.base_image = base_image
        self.txt_base_image = txt_base_image

    def define_text_format(self, text):
        """
        Split text in different sentences

        Parameters
        ----------
        text: str

        Returns
        -------
        total_lines: list of string
            [str, str, ... ]
        """

        words_sentence = text.split()

        line = []
        total_lines = []

        for ind, word in enumerate(words_sentence):
            if len(' '.join(line)) < self.max_length:
                line += [word]
            else:
                total_lines.append(' '.join(line))
                line = [word]

        total_lines.append(' '.join(line))

        return total_lines

    @staticmethod
    def format_input_text(text):
        """
        Format text if need

        Parameters
        ----------
        text: str

        Returns
        -------
        formated text: str
        """

        if not text.endswith('.'):
            text += '.'
            pass
        return text

    def define_y_position(self, lines):
        """
        Define y position for each line in the image
        Itinial position is defined based on number of lines. Then iteatre over the
        lines and define position for upper and lower lines.

        Parameters
        ----------
        lines: list of string
            [str, str, ... ]

        Returns
        -------
        ypos: list of int
            y position where to print each line
            [int, int, ... ]
        """

        # Define initial positions depending if we have add lines or not
        if len(lines) % 2 == 1:
            y_pos = [self.size[1] / 2 - self.font_size / 2]
            y_offsets = (y_pos[0] - 1 * self.font_size,
                         y_pos[0] + 1 * self.font_size)
        else:
            y_pos = []
            y_offsets = (self.size[1] / 2 - 0.5 * self.font_size - self.font_size / 2,
                         self.size[1] / 2 + 0.5 * self.font_size - self.font_size / 2)

        # define as may positions as lines we have
        for i in range(len(lines) / 2):
            y_pos.extend(y_offsets)
            y_offsets = (y_offsets[0] - self.font_size,
                         y_offsets[1] + self.font_size)
        return sorted(y_pos)

    def insert_text_image(self, lines_print, y_positions):
        """
        Insert text in image

        Parameters
        ----------
        lines_print: list of string
            [str, str, ... ]
        y_positions: list of int
            [int, int, ... ]

        """

        # get a drawing context
        d = ImageDraw.Draw(self.txt_base_image)

        # draw text
        for ind, line in enumerate(lines_print):
            d.text((self.xmin, y_positions[ind]), line, font=self.font, fill=self.text_color)

        # draw name of page
        if self.name is not None:
            d.text((self.x_signature, y_positions[-1] + 20 + self.font_size), self.name,
                   font=self.font_signature, fill=self.text_color)

    def save_image(self, path_results):
        """
        save image into a jpg file

        Parameters
        ----------
        path_results: str
            String where to store the file

        """
        # convert image to rgb
        image = self.created_image.convert("RGB")

        # save image
        image.save(path_results)
