# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Executes a build process for a format.
"""
import os
from lib.adcase import helper as f
# pylint: disable=line-too-long


def build(req):
  """Builder for this format.

  Args:
    req: flask request

  Returns:
    Json containing the creative data
  """

  errors = []
  v = {}
  data = {"collapsed": {}, "expanded": {}}
  tdir = "/tmp/" + f.get_tmp_file_name()

  index = get_html()

  if "collapsed_zip" not in req.files:
    return {"errors": ["No collapsed file"]}
  if "expanded_zip" not in req.files:
    return {"errors": ["No expanded file"]}

  ## collapsed
  data["collapsed"]["ext"] = f.get_ext(req.files["collapsed_zip"].filename)
  if data["collapsed"]["ext"] == "zip":
    os.mkdir(tdir)
    if not f.extract_zip(req.files["collapsed_zip"], tdir + "/collapsed"):
      return {"errors": ["Wrong collapsed zip file"]}

    file_name = "index2.html"
    try:
      os.rename(tdir + "/collapsed/index.html", tdir+ "/collapsed/" + file_name)
    except os.FileNotFoundError:
      return {"errors": ["No index.html in collapsed zip"]}
  elif not data["collapsed"]["ext"]:
    return {"errors": ["No collapsed file"]}
  else:
    f.save_file(req.files["collapsed_zip"], tdir + "/collapsed."
                + data["collapsed"]["ext"])

  ## expanded
  data["expanded"]["ext"] = f.get_ext(req.files["expanded_zip"].filename)
  if data["expanded"]["ext"] == "zip":
    if not f.extract_zip(req.files["expanded_zip"], tdir + "/expanded"):
      return {"errors": ["Wrong expanded zip file"]}

    file_name = "index2.html"
    try:
      os.rename(tdir + "/expanded/index.html", tdir+ "/expanded/" + file_name)
    except os.FileNotFoundError:
      return {"errors": ["No index.html in expanded zip"]}
  elif not data["expanded"]["ext"]:
    return {"errors": ["No expanded file"]}
  else:
    f.save_file(req.files["expanded_zip"], tdir + "/expanded." + data["expanded"]["ext"])

  v["width"] = f.strtoken(f.get_param("collapsed_size"), 1, "x")
  v["expandedHeight"] = f.strtoken(f.get_param("expanded_size"), 2, "x")
  v["height"] = v["expandedHeight"]
  v["collapsedHeight"] = f.strtoken(f.get_param("collapsed_size"), 2, "x")
  v["animatedTransition"] = str(f.get_int_param("animatedTransition") * 250)

  if data["collapsed"]["ext"] == "zip":
    v["collapsedContent"] = "<iframe src='collapsed/index2.html' frameborder=0 style='width:"+v["width"]+"px;height:+"+v["collapsedHeight"]+"px' scrolling='no'></iframe>"
  else:
    v["collapsedContent"] = "<img src='collapsed."+data["collapsed"]["ext"]+"' style='border:0;width:"+v["width"]+"px;height:"+v["collapsedHeight"]+"px' />"

  if data["expanded"]["ext"] == "zip":
    v["expandedContent"] = "<iframe src='expanded/index2.html' frameborder=0 style='width:"+v["width"]+"px;height:"+v["expandedHeight"]+"px' scrolling='no'></iframe>"
  else:
    v["expandedContent"] = "<img src='expanded."+data["expanded"]["ext"]+"' style='border:0;width:"+v["width"]+"px;height:"+v["expandedHeight"]+"px' />"

  return {"errors": errors, "dir": tdir, "index": index, "vars": v}


def get_html():
  """Gets html.

  Returns:
    index.html content
  """

  return """<!DOCTYPE HTML><html lang="en-us">
<head>
    <meta name="ad.size" content="width=[[width]],height=[[expandedHeight]]">
<script>

var clickTag = "[[clicktag_url]]";
var tpl = {};

tpl.receiveMessage = function(e) {

}

window.addEventListener ? window.addEventListener("message", tpl.receiveMessage, !1)
    : (window.attachEvent && window.attachEvent("message", tpl.receiveMessage));


tpl.expand = function() {
  window.top.postMessage({ msg: "adcase", format:"default",
    params: { action: "pushonclick", expand:true } } , "*");
  document.getElementById("expandLayer").style.display="none";
  document.getElementById("ad_collapsed") && (document.getElementById("ad_collapsed").style.display = "none");
  document.getElementById("ad_expanded") && (document.getElementById("ad_expanded").style.display = "block");

}

</script>
</head>
<body style='margin:0;cursor:pointer'>
<div id='expandLayer' style='z-index:99;width:100%;height:100%;position:fixed;top:0;left:0' onclick='tpl.expand()'></div>
[[clicktag_layer]]
    <div id='ad_collapsed' style=';width:[[width]]px;height:[[collapsedHeight]]px;overflow:hidden;'>
        [[collapsedContent]]
    </div>
    <div id='ad_expanded' style='display:none;width:[[width]]px;height:[[expandedHeight]]px;overflow:hidden;'>
        [[expandedContent]]
    </div>
<script>
window.top.postMessage({ msg: "adcase", format:"default",
    params: { action: "pushonclick", animatedTransition:[[animatedTransition]], expandedHeight: [[expandedHeight]], collapsedHeight: [[collapsedHeight]] } } , "*");

</script>
</body></html>"""
