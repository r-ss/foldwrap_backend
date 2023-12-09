import pytest
from pathlib import Path
from config import config

# from tests.testutils import get

from models.export import BannerExportBM
from services.foldwrap_banner import FoldWrapBanner

pre_css = """
.ress_ban {position: absolute; overflow: hidden; border: 1px solid #666666; box-sizing: border-box;}
.frame, .wrap {left: 0px; right: 0px; position: absolute; overflow: hidden; border: none;}
.ress_ban, .ress_ban .frame, .ress_ban .wrap {width: 300px; height: 500px;}

.fw-0afy {position: absolute; top: -42.00px; left: -208.00px; width: 576.00px; height: 542.00px; color: none; background: url(/figma/EgePe5Ftkvz9lgjsx211ko/images/1_10.png); background-repeat: no-repeat; background-size: 100% 100%}
.fw-mphq {position: absolute; top: 447.00px; left: 188.00px; width: 100.00px; height: 40.00px; color: rgba(0,88,163,1); background: url(/figma/EgePe5Ftkvz9lgjsx211ko/images/2_2.svg); background-repeat: no-repeat; background-size: 100% 100%}
.fw-7rbn {position: absolute; top: 25.00px; left: 18.00px; width: 277.00px; height: 133.00px; color: rgba(16,16,16,1); font-family: Noto IKEA Latin; font-size: 28px; font-weight: 700; text-align: left; line-height: 38.14px; letter-spacing: 0.00px}
.fw-vtl5 {position: absolute; top: 170.00px; left: 18.00px; width: 106.00px; height: 33.00px; color: rgba(26,26,26,1); font-family: Noto IKEA Latin; font-size: 24px; font-weight: 700; text-align: left; line-height: 32.69px; letter-spacing: 0.00px}
.fw-5b3h {position: absolute; top: 204.00px; left: 18.00px; width: 118.00px; height: 19.00px; color: rgba(26,26,26,1); font-family: Noto IKEA Latin; font-size: 14px; font-weight: 400; text-align: left; line-height: 19.07px; letter-spacing: 0.00px}
.fw-mkzb {position: absolute; top: 236.00px; left: 21.00px; width: 83.00px; height: 52.00px; color: rgba(122,97,97,1); background: rgba(122,97,97,1); border-radius: 4px}
.fw-61s6 {position: absolute; top: 233.00px; left: 18.00px; width: 83.00px; height: 52.00px; color: rgba(255,234,46,1); background: rgba(255,234,46,1); border-radius: 4px}
.fw-u3rw {position: absolute; top: 231.00px; left: 27.00px; width: 25.00px; height: 57.00px; color: rgba(0,0,0,1); font-family: Noto IKEA Latin; font-size: 42px; font-weight: 700; text-align: left; line-height: 57.20px; letter-spacing: 0.00px}
.fw-r81o {position: absolute; top: 236.00px; left: 50.00px; width: 46.00px; height: 30.00px; color: rgba(0,0,0,1); font-family: Noto IKEA Latin; font-size: 22px; font-weight: 400; text-align: left; line-height: 29.96px; letter-spacing: 0.00px}


.fw-ysxf {position: absolute; top: 478.00px; left: 15.00px; width: 129.00px; height: 12.00px; color: rgba(255,255,255,0.6000000238418579); font-family: Noto IKEA Latin; font-size: 9px; font-weight: 400; text-align: left; line-height: 12.26px; letter-spacing: 0.00px}
.fw-t9y8 {background-color: rgba(197,179,160,1)}
.fw-cr3y {position: absolute; top: -72.00px; left: -254.00px; width: 634.00px; height: 596.00px; color: none; background: url(/figma/EgePe5Ftkvz9lgjsx211ko/images/1_9.png); background-repeat: no-repeat; background-size: 100% 100%}
.fw-snl5 {position: absolute; top: 447.00px; left: 188.00px; width: 100.00px; height: 40.00px; color: rgba(0,88,163,1); background: url(/figma/EgePe5Ftkvz9lgjsx211ko/images/2_2.svg); background-repeat: no-repeat; background-size: 100% 100%}
.fw-0nz6 {position: absolute; top: 25.00px; left: 18.00px; width: 277.00px; height: 133.00px; color: rgba(16,16,16,1); font-family: Noto IKEA Latin; font-size: 28px; font-weight: 700; text-align: left; line-height: 38.14px; letter-spacing: 0.00px}
.fw-3n5m {position: absolute; top: 92.00px; left: 109.00px; width: 73.00px; height: 33.00px; color: rgba(26,26,26,1); font-family: Noto IKEA Latin; font-size: 24px; font-weight: 700; text-align: left; line-height: 32.69px; letter-spacing: 0.00px}
.fw-rw6p {position: absolute; top: 126.00px; left: 109.00px; width: 96.00px; height: 19.00px; color: rgba(26,26,26,1); font-family: Noto IKEA Latin; font-size: 14px; font-weight: 400; text-align: left; line-height: 19.07px; letter-spacing: 0.00px}
.fw-8vyt {position: absolute; top: 158.00px; left: 112.00px; width: 83.00px; height: 52.00px; color: rgba(122,97,97,1); background: rgba(122,97,97,1); border-radius: 4px}
.fw-klx3 {position: absolute; top: 155.00px; left: 109.00px; width: 83.00px; height: 52.00px; color: rgba(255,234,46,1); background: rgba(255,234,46,1); border-radius: 4px}
.fw-im6q {position: absolute; top: 153.00px; left: 118.00px; width: 25.00px; height: 57.00px; color: rgba(0,0,0,1); font-family: Noto IKEA Latin; font-size: 42px; font-weight: 700; text-align: left; line-height: 57.20px; letter-spacing: 0.00px}
.fw-r964 {position: absolute; top: 158.00px; left: 141.00px; width: 46.00px; height: 30.00px; color: rgba(0,0,0,1); font-family: Noto IKEA Latin; font-size: 22px; font-weight: 400; text-align: left; line-height: 29.96px; letter-spacing: 0.00px}


.fw-rh7p {position: absolute; top: 478.00px; left: 15.00px; width: 129.00px; height: 12.00px; color: rgba(0,0,0,0.75); font-family: Noto IKEA Latin; font-size: 9px; font-weight: 400; text-align: left; line-height: 12.26px; letter-spacing: 0.00px}
.fw-drra {background-color: rgba(197,179,160,1)}
.fw-ddso {position: absolute; top: 447.00px; left: 188.00px; width: 100.00px; height: 40.00px; color: rgba(0,88,163,1); background: url(/figma/EgePe5Ftkvz9lgjsx211ko/images/2_2.svg); background-repeat: no-repeat; background-size: 100% 100%}
.fw-9ffb {position: absolute; top: 25.00px; left: 18.00px; width: 277.00px; height: 133.00px; color: rgba(16,16,16,1); font-family: Noto IKEA Latin; font-size: 28px; font-weight: 700; text-align: left; line-height: 38.14px; letter-spacing: 0.00px}
.fw-a8h7 {position: absolute; top: 136.00px; left: 18.00px; width: 277.00px; height: 133.00px; color: rgba(16,16,16,1); font-family: Noto IKEA Latin; font-size: 28px; font-weight: 400; text-align: left; line-height: 38.14px; letter-spacing: 0.00px}
.fw-us3i {position: absolute; top: 478.00px; left: 15.00px; width: 129.00px; height: 12.00px; color: rgba(0,0,0,0.75); font-family: Noto IKEA Latin; font-size: 9px; font-weight: 400; text-align: left; line-height: 12.26px; letter-spacing: 0.00px}
.fw-kps8 {position: absolute; top: 264.14px; left: 18.00px; width: 90.00px; height: 89.86px; color: rgba(0,0,0,1); background: url(/figma/EgePe5Ftkvz9lgjsx211ko/images/2_5.svg); background-repeat: no-repeat; background-size: 100% 100%}
.fw-yinn {background-color: rgba(197,179,160,1)}
"""

pre_html = """
<div class="ress_ban ressban_layout drag-list" id="ress_ban"><div class="frame drag-item" id="frame1" draggable="true">
<div class="wrap fw-t9y8" style="">
      <div class="rev fw-0afy" style=""></div><div class="rev fw-mphq" style=""></div><div class="txt fw-7rbn" style="">Dale un cambio<br>a tu vida nocturna</div><div class="group fw-k25z" style=""><div class="txt fw-vtl5" style="">BARLAST</div><div class="txt fw-5b3h" style="">Lámpara de mesa</div><div class="group fw-u787" style=""><div class="rev fw-mkzb" style=""></div><div class="rev fw-61s6" style=""></div><div class="txt fw-u3rw" style="">4</div><div class="txt fw-r81o" style="">,99€</div></div></div><div class="txt fw-ysxf" style="">© Inter IKEA Systems B.V. 2023</div>
</div>
</div><div class="frame drag-item" id="frame2" draggable="true">
<div class="wrap fw-drra" style="">
      <div class="rev fw-cr3y" style=""></div><div class="rev fw-snl5" style=""></div><div class="txt fw-0nz6" style="">Alegra tu salón</div><div class="group fw-q83f" style=""><div class="txt fw-3n5m" style="">GURLI</div><div class="txt fw-rw6p" style="">Funda de cojín</div><div class="group fw-oqfw" style=""><div class="rev fw-8vyt" style=""></div><div class="rev fw-klx3" style=""></div><div class="txt fw-im6q" style="">3</div><div class="txt fw-r964" style="">,99€</div></div></div><div class="txt fw-rh7p" style="">© Inter IKEA Systems B.V. 2023</div>
</div>
</div><div class="frame drag-item" id="frame3" draggable="true">
<div class="wrap fw-yinn" style="">
      <div class="rev fw-ddso" style=""></div><div class="txt fw-9ffb" style="">#homepositive</div><div class="txt fw-a8h7" style="">Ver más<br>en el sitio web<br>de IKEA</div><div class="txt fw-us3i" style="">© Inter IKEA Systems B.V. 2023</div><div class="rev fw-kps8" style=""></div>
</div>
</div></div>
"""

pre_data = """
{"options":{"size":"300x500","frame_delay":2.5,"animationStyle":"light","loopsCount":0},"templateAnimations":[{"name":"fade","rules":[{"selector":".wrap","properties":{"opacity":[0,1]},"duration":1,"delay":0,"easing":"easeOutSine"},{"selector":".rev, .txt, .group","properties":{"opacity":[0,1]},"duration":1,"delay":0.3,"easing":"easeInOutSine"}]},{"name":"light","rules":[{"selector":".wrap","properties":{"opacity":[0,1]},"duration":0.5,"delay":0,"easing":"easeOutSine"},{"selector":".txt","properties":{"translateY":[25,0],"opacity":[0,1]},"duration":0.5,"delay":0.1,"easing":"easeOutQuad"},{"selector":".rev","properties":{"translateY":[35,0],"opacity":[0,1]},"duration":0.7,"delay":0.1,"easing":"easeOutBack"},{"selector":".group","properties":{"translateY":[35,1],"opacity":[0,1]},"duration":1,"delay":0.35,"easing":"easeOutQuad"}]},{"name":"dynamic","rules":[{"selector":".wrap","properties":{"opacity":[0,1]},"duration":0.5,"delay":0,"easing":"easeOutSine"},{"selector":".txt","properties":{"translateY":[25,0],"opacity":[0,1]},"duration":0.6,"delay":0.1,"easing":"easeOutQuad"},{"selector":".rev","properties":{"translateY":[35,0],"opacity":[0,1]},"duration":0.7,"delay":0.1,"easing":"easeOutBack"},{"selector":".group","properties":{"scale":[0.7,1],"opacity":[0,1]},"duration":1.5,"delay":0,"easing":"easeOutElastic"}]}],"templateNodes":[{"name":"text","tag":"div","tag_classlist":["txt"],"tag_default_innerHTML":"<div>Текст</div>","toggle_name":"text","greedy_for":"disclaimer","movable":true},{"name":"pic","tag":"div","tag_classlist":["image"],"tag_default_innerHTML":"<img src=\"host/gfx/noimage.png\">","toggle_name":"pic","greedy_for":"disclaimer","movable":true}]}
"""


@pytest.mark.anyio
async def test_foldwrap_banner_a():
    data = {
        "title": "epic",
        "size": "300x500",
        "css": pre_css,
        "html": pre_html,
        "data": pre_data,
    }

    banner = BannerExportBM.parse_obj(data)

    assert type(banner) == BannerExportBM

    fwb = FoldWrapBanner(banner)

    print("======= GFX:")
    for item in fwb.gfx:
        print(item)
    print("============")

    assert type(fwb) == FoldWrapBanner
    assert fwb.width == 300
    assert fwb.height == 500
    assert fwb.size == "300x500"

    export_path = Path(config.DATA_DIR_TEMP).joinpath("export_test")
    # with open(engine_path, 'r') as engine_file:

    result = fwb.exportAsHTML(export_path)

    assert result["success"] is True
    # assert result["total_weight"] == "29KB"
    # assert result["zipped_weight"] == "10KB"

    print(result)
