from fontTools.ttLib import TTFont

# from fontTools.ttLib.woff import WOFFFont


class FontTool:
    def convert_to_woff(otf_path, woff_path):
        # Load the OTF font
        font = TTFont(otf_path)

        # Save the font as WOFF
        font.save(woff_path, "woff")


"""
    Subset


    https://stackoverflow.com/questions/55009981/how-to-use-pyftsubset-of-fonttools-inside-of-the-python-environment-not-from-th

    https://fonttools.readthedocs.io/en/latest/subset/


"""
