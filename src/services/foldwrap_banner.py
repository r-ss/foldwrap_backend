# -*- coding: utf-8 -*-
#! /usr/bin/env python
import re
from PIL import Image
from log import log

from pathlib import Path
from config import config

from models.export import BannerExportBM

from services.misc.filesystem import FileSystemUtils as fs


from services.misc.png_optimizer import PNGOptimizer


def convert_png_to_jpg(image, src, dst, html):
    def convert(src, dst):
        image = Image.open(src)
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(dst, "JPEG")

    def optimize_png(src, dst):
        try:
            optimizer = PNGOptimizer()
            optimizer.optimize_PNG(src, dst)
        except Exception as e:
            print(f"Error: {e}")

    def calculate_transparency_percentage(image_path):
        try:
            with Image.open(image_path) as img:
                # Convert the image to RGBA mode (if not already)
                img = img.convert("RGBA")

                # Get pixel data
                pixels = img.getdata()

                # Count transparent pixels
                transparent_pixel_count = sum(1 for pixel in pixels if pixel[3] == 0)

                # Calculate percentage
                total_pixels = len(pixels)
                transparency_percentage = transparent_pixel_count / total_pixels

                return transparency_percentage
        except Exception as e:
            print(f"Error: {e}")
            return None

    if str(src).endswith(".png"):
        filename_without_extension = src.stem
        replace_from = f"{filename_without_extension}.png"
        replace_to = f"{filename_without_extension}.jpg"

        transparency_percentage = calculate_transparency_percentage(src)

        if transparency_percentage < 0.1:
            print(f"Transparency Percentage: {transparency_percentage*100:.1f}%, Converting {src.name} to jpeg.")
            convert(src, str(dst).replace(replace_from, replace_to))
            return html.replace(replace_from, replace_to)
        else:
            print(f"Transparency Percentage: {transparency_percentage*100:.1f}%, Keeping PNG format")
            # fs.copy(src, dst)
            optimize_png(src, dst)
            # optimize_png_tinify(src, dst)
            return html

    else:
        raise ValueError("Not a png file")


class FoldWrapBanner:
    # Represents a FoldWrap HTML banner
    html_filename = "index.html"

    # Initializer / Instance Attributes
    def __init__(self, banner: BannerExportBM):
        self.figma_key = None
        if banner.figma_key:
            self.figma_key = banner.figma_key

        self.headinjection = None
        if banner.headinjection:
            self.headinjection = banner.headinjection

        self.type = "foldwrap_banner"
        self.title = "untitled"
        self.gfx = []
        # self.website = None
        # self.ttx = None
        self.skeleton = ""
        self.engine = ""
        self.html = banner.html
        # self.data = banner.data
        self.nodes_data = banner.nodes_data
        self.css = banner.css
        self.width = None
        self.height = None
        # self.additionalFiles = [] # add here files for proper work on some platforms. createJS for mail.ru for example

        print(banner.nodes_data)

        self.total_weight = None
        self.zipped_weight = None
        self.zippath = None  # for export function in creative editor

        # Filling size
        # size_arr = re.findall('(\d+)x(\d+)', banner.size)[0]
        size_arr = re.findall(r"(\d+)x(\d+)", banner.size)[0]
        self.width = int(size_arr[0])
        self.height = int(size_arr[1])

        log(f"Size is {self.width} x {self.height}")

        # Filling HTML and JavaScript

        skeleton_path = Path(Path(__file__).resolve().parent).joinpath("misc/banner_export_assets/export_skeleton.html")
        with open(skeleton_path, "r") as skeleton_file:
            # Read the entire content of the file into a string
            self.skeleton = skeleton_file.read()

        engine_path = Path(Path(__file__).resolve().parent).joinpath("misc/banner_export_assets/export_engine_gsap.js")
        with open(engine_path, "r") as engine_file:
            # Read the entire content of the file into a string
            self.engine = engine_file.read()

        # foldwrapban_js = open('%sfoldwrapban.js' % Config.STORAGE['MEDIA'], 'r').read()

        # fixing one stupid \n symbol in JS
        # foldwrapban_js = re.sub(r'\\n', ' ', foldwrapban_js)

        # self.js = 'const creativeDataJSON = %s\n\n\n\n%s' % (json.dumps(jsoncreativedata), foldwrapban_js)
        # self.html = creative.get_dom

        self.searchAndFillGFX()

    def searchAndFillGFX(self):
        regexp = r"\/figma\/([a-zA-Z0-9]{22})\/images\/([a-zA-Z0-9-_]{1,20}.[a-zA-Z]{1,4})"
        gfx_items = re.findall(regexp, self.css)
        for match in gfx_items:
            if match[1] not in self.gfx:
                item = {
                    "filename": match[1],
                    "figma_file_key": match[0],
                }
                self.gfx.append(item)

        self.css = re.sub(r"\/figma\/([a-zA-Z0-9]{22})\/images\/", "", self.css)

    @property
    def size(self):
        return "{}x{}".format(self.width, self.height)

    def __repr__(self):
        return "Banner {} {}x{}".format(self.type, self.width, self.height)

    def buildHTML(self):
        # optionsscript = '<script type="text/javascript">var production = true;\nvar options_JSON = \'%s\';</script>' % json.dumps(self.creative.get_options)

        html = re.sub(r"<!-- STYLE -->", "<!-- STYLE -->\n<style>\n%s\n</style>" % self.css, self.skeleton, 1)  # 1 on end means to replace only first occurrence
        # html = re.sub(r'<!-- SCRIPT -->', '<!-- SCRIPT -->\n<script type="text/javascript">\n%s\n</script>' % self.js, html, 1) # 1 on end means to replace only first occurrence
        html = html.replace("<!-- SCRIPT -->", '<!-- SCRIPT -->\n<script type="text/javascript">\n%s\n</script>' % self.engine, 1)

        html = html.replace("<!-- SCRIPT -->", '<!-- SCRIPT -->\n<script type="text/javascript">\nconst nodes_data = %s\n</script>' % self.nodes_data, 1)

        if self.headinjection:
            html = html.replace("<!-- OPTIONS -->", "<!-- OPTIONS -->\n%s" % self.headinjection)

        # adding display: none for eliminate possible blibking on banner loading
        # domWithStyle = re.sub(r'id="foldwrap_ban"', 'id="foldwrap_ban" style="display: none;"', self.html, 1)  # 1 on end means to replace only first occurrence

        html = re.sub(r"<!-- DOM -->", '<!-- DOM -->\n<div class="foldwrap-container" id="foldwrap_container">%s\n</div>' % self.html, html, 1)  # 1 on end means to replace only first occurrence
        return html

    def exportAsHTML(self, dst_path, andZIP=True):
        dst_path = Path(dst_path).joinpath("content")

        fs.remove_directory(dst_path)

        html = self.buildHTML()

        fs.check_dir(dst_path)
        fs.check_dir(config.DATA_DIR_TEMP)

        html = self.collectGFX(html, dst_path)

        """ clean-up and stupid fix html """
        html = html.replace(" ressban_layout", "")
        # html = html.replace('draggable="true"', '')
        # html = html.replace(' drag-item', '')
        html = html.replace(' style=""', "")

        html_temp_path = f"{config.DATA_DIR_TEMP}/{self.title}.html"

        f = open(html_temp_path, "w", encoding="utf8")
        f.write(html)
        f.close()

        fs.move_file(html_temp_path, "%s/%s" % (dst_path, self.html_filename))

        """ Now, when 'banner', animated view fully ready on the filesystem, we also make a layout, static version of it 
        dst_layout_path = Path(dst_path).parent.joinpath('layout')
        fs.remove_directory(dst_layout_path)
        fs.copy(dst_path, dst_layout_path)

        layout_html_path = Path(dst_layout_path).joinpath("index.html")
        with open(layout_html_path, "r+") as lay_html_file:
            # Read the entire content of the file into a string
            lhtml = lay_html_file.read()

            # Replace the target string
            lhtml = lhtml.replace("<!-- OPTIONS -->", "<!-- OPTIONS -->\n<script type=\"text/javascript\">\nconst layoutView = true\n</script>")


            # Write the file out again
            lay_html_file.seek(0)
            lay_html_file.write(lhtml)
            lay_html_file.truncate()
        """

        self.total_weight = fs.getHumanReadableFilesize(fs.get_dir_size(dst_path), 0)

        print("total_weight", self.total_weight)

        if andZIP:
            ziptemp = "%s%s_%s.zip" % (config.DATA_DIR_TEMP, self.title, self.size)
            fs.make_zip(dst_path, ziptemp)
            self.zipped_weight = fs.getHumanReadableFilesize(fs.get_filesize(ziptemp, kb=False), 0)

            #  removing last path component to step one level up in directories tree
            head = Path(dst_path).parent
            zippath = "%s/%s_%s.zip" % (head, self.title, self.size)
            fs.move_file(ziptemp, zippath)
            self.zippath = zippath

            # fs.remove_directory(dst_path)

            return {
                "success": True,
                "figma_key": self.figma_key,
                "zip_path": zippath,
                "preview_url_content": f"/temp/export/{self.figma_key}/content",
                "download_url": f"/temp/export/{self.figma_key}/{self.title}_{self.size}.zip",
                "total_weight": self.total_weight,
                "zipped_weight": self.zipped_weight,
            }

        return {"success": True, "zipped": "No"}

    def collectGFX(self, html, to_directory):
        for image in self.gfx:
            src = Path(config.DATA_DIR_FIGMA_FILES).joinpath(image["figma_file_key"]).joinpath("images").joinpath(image["filename"])
            dst = Path(to_directory).joinpath(image["filename"])
            # print(src, dst)
            if str(src).endswith(".png"):
                html = convert_png_to_jpg(image, src, dst, html)
            else:
                fs.copy(src, dst)

        return html
