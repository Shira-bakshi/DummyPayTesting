"""Build a standalone presentation report from a self-contained pytest-html report."""

import argparse
import json
import re
from html import escape, unescape
from pathlib import Path


SCENARIOS = {
    "test_changeButtonRequiresDifferentCurrency": (
        "כפתור שינוי מטבע",
        "הכפתור זמין לאחר בחירת מטבע אחר ומושבת כשחוזרים למטבע המקורי.",
    ),
    "test_saveButtonRequiresDifferentDisplayName": (
        "כפתור שמירת שם",
        "נבדקת לחיצות הכפתור אחרי עריכה וביטול השינוי באמצעות החזרת השם המקורי.",
    ),
    "test_displayNamePersistsAfterReload": (
        "שמירת שם ושחזור",
        "השם החדש מופיע אחרי רענון. בדיקה נוספת מאמתת שהשם המקורי שוחזר.",
    ),
    "empty": ("שם ריק", "מופיעה שגיאת אורך, ואחרי רענון מוצג השם המקורי."),
    "one-character-after-trimming": (
        "תו יחיד אחרי הסרת רווחים", "מופיעה שגיאה על אורך מינימלי של שני תווים.",
    ),
    "above-maximum": ("שם באורך 51 תווים", "מופיעה שגיאה על חריגה מ־50 תווים."),
    "digits": ("שם שמכיל ספרות בלבד", "הדפדפן יוזם בקשת שמירה, והטסט חוסם אותה."),
    "symbols": ("שם שמכיל סימנים בלבד", "הדפדפן יוזם בקשת שמירה, והטסט חוסם אותה."),
    "maximum": ("שם באורך 50 תווים", "הדפדפן יוזם בקשת שמירה בגבול העליון, והטסט חוסם אותה."),
}

STEPS = {
    "original-display-name": "השם המקורי בפתיחת הדף",
    "original-name-after-reload": "השם המקורי אחרי רענון",
    "new-name-before-save": "השם החדש לפני שמירה",
    "new-name-after-save": "השם החדש מוצג בפרופיל",
    "new-name-after-reload": "השם החדש מופיע גם אחרי רענון",
    "original-name-restored-after-reload": "השם המקורי שוחזר ואומת אחרי רענון",
    "invalid-name-before-save": "ערך לא תקין לפני שמירה",
    "validation-error-after-save": "הודעת הוולידציה אחרי לחיצה",
    "valid-name-before-save": "הערך שנבדק לפני שמירה",
    "after-save-request-blocked": "המסך אחרי חסימת בקשת השמירה",
    "original-name-after-reopening": "השם המקורי אחרי פתיחה מחדש",
    "original-name-save-disabled": "שם מקורי וכפתור שמירה מושבת",
    "different-name-save-enabled": "שם אחר וכפתור שמירה זמין",
    "original-name-restored": "חזרה לשם המקורי בשדה העריכה",
    "original-currency-change-disabled": "מטבע מקורי וכפתור שינוי מושבת",
    "different-currency-change-enabled": "מטבע אחר וכפתור שינוי זמין",
    "original-currency-restored": "חזרה למטבע המקורי בתפריט",
}


LEGACY_TEST_NAMES = {
    "test_change_button_requires_different_currency": "test_changeButtonRequiresDifferentCurrency",
    "test_save_button_requires_different_display_name": "test_saveButtonRequiresDifferentDisplayName",
    "test_display_name_persists_after_reload": "test_displayNamePersistsAfterReload",
}


def getScenarioName(testId):
    function = testId.split("::")[-1].split("[")[0]
    return LEGACY_TEST_NAMES.get(function, function)


def renderCase(test):
    name = test["testId"].split("::")[-1]
    function = getScenarioName(test["testId"])
    variant = name.partition("[")[2].rstrip("]").partition("-")[2]
    title, description = SCENARIOS.get(variant or function, (name, ""))
    images = []
    for extra in test["extras"]:
        source = extra["content"]
        if not source.startswith("data:image/png;base64,"):
            continue
        step, _, key = extra["name"].partition("-")
        caption = escape(STEPS.get(key, key.replace("-", " ")))
        images.append(
            f'<button type="button" class="shot"><img loading="lazy" src="{escape(source)}" '
            f'alt="{caption}"><span><b>{escape(step)}</b> {caption}</span></button>'
        )
    passed = test["result"] == "Passed"
    status = "עבר" if passed else escape(test["result"])
    state = "pass" if passed else "other"
    log = ""
    if not passed:
        log = f'<pre dir="ltr">{escape(test.get("log", ""))}</pre>'
    return f"""
<details class="case" {'open' if function == 'test_displayNamePersistsAfterReload' else ''}>
  <summary><span class="case-title">{escape(title)}</span>
    <span class="badge {state}">{status}</span><time dir="ltr">{escape(test['duration'])}</time></summary>
  <div class="case-body"><p>{escape(description)}</p><code dir="ltr">{escape(name)}</code>
    {log}<div class="shots" aria-label="צילומי מסך לפי שלב">{''.join(images)}</div>
  </div>
</details>""", len(images)


def buildReport(source, destination):
    markup = source.read_text(encoding="utf-8")
    match = re.search(r'data-jsonblob="([^"]*)"', markup)
    if not match:
        raise ValueError("The input does not contain pytest-html results.")
    data = json.loads(unescape(match.group(1)))
    tests = [test for attempts in data["tests"].values() for test in attempts]
    if not tests:
        raise ValueError("The input report contains no tests.")
    tests.sort(key=lambda test: getScenarioName(test["testId"]) != "test_displayNamePersistsAfterReload")
    cases = [renderCase(test) for test in tests]
    passed = sum(test["result"] == "Passed" for test in tests)
    screenshots = sum(count for _, count in cases)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        PAGE.replace("{{TOTAL}}", str(len(tests)))
        .replace("{{PASSED}}", str(passed))
        .replace("{{IMAGES}}", str(screenshots))
        .replace("{{CASES}}", "".join(card for card, _ in cases)),
        encoding="utf-8",
    )


PAGE = """<!doctype html>
<html lang="he" dir="rtl">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DummyPay | דוח בדיקות הגדרות</title>
<style>
:root{font-family:"Segoe UI",Arial,sans-serif;color:#172339;background:#eef2f8;line-height:1.55}
*{box-sizing:border-box}body{margin:0}button,a,summary{touch-action:manipulation}
.wrap{width:min(1120px,calc(100% - 32px));margin:auto}
header{background:linear-gradient(120deg,#111d37,#1c3857 68%,#15565b);color:white;padding:36px 0 68px}
nav{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.brand{font-size:20px;letter-spacing:.04em;font-weight:750}
nav a{color:white;margin-inline-start:16px;text-underline-offset:5px}
h1{font-size:clamp(32px,6vw,58px);line-height:1.12;margin:38px 0 12px}
header p{color:#dce8f4;margin:0}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:-35px}
.metric,.case{border:1px solid #d8e2ee;background:white;border-radius:16px;box-shadow:0 8px 24px #162c4510}
.metric{padding:16px 20px}.metric strong{display:block;font-size:34px;line-height:1.2}.metric span{color:#42546a}
section{margin:34px 0}.section-head{display:flex;gap:12px;justify-content:space-between;align-items:center;flex-wrap:wrap}
.section-head h2{margin:0}.section-head button,dialog button{border:1px solid #bccbdd;background:#fff;border-radius:8px;padding:8px 14px;color:#172339;cursor:pointer;font:inherit}
.case{margin:12px 0;overflow:hidden}.case[open] summary{border-bottom:1px solid #e6edf4}
summary{display:grid;grid-template-columns:minmax(0,1fr) auto auto;align-items:center;gap:12px;cursor:pointer;padding:16px}
summary::-webkit-details-marker{display:none}.case-title{font-weight:700}.case-title::before{content:"+";display:inline-block;width:24px;color:#27556a}.case[open] .case-title::before{content:"−"}
.badge{border-radius:20px;padding:3px 12px;font-weight:700}.pass{background:#dcf6eb;color:#07593d}.other{background:#fde5e4;color:#8c2732}
time,code{color:#475a72}code{display:block;overflow-wrap:anywhere;text-align:left;font-size:12px}
.case-body{padding:16px}.case-body p{margin:0 0 10px}.shots{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:12px;margin-top:18px}
.shot{background:#f5f8fc;border:1px solid #d6e2ef;border-radius:10px;overflow:hidden;cursor:zoom-in;padding:0;text-align:right;color:inherit;font:inherit}
.shot:hover,.shot:focus-visible{outline:2px solid #16766d;outline-offset:2px}.shot img{width:100%;height:132px;object-fit:contain;background:#e4edf7;display:block}
.shot span{display:block;padding:8px 10px}.shot b{color:#12645e;margin-inline-end:5px}
dialog{border:0;border-radius:14px;padding:16px;max-width:min(96vw,1450px);max-height:94vh;color:#172339}
dialog::backdrop{background:#081426d9}dialog img{display:block;max-width:100%;max-height:73vh;object-fit:contain;margin:auto}dialog p{margin:10px 0}pre{white-space:pre-wrap}
footer{padding:0 0 32px;color:#475a72}
@media(max-width:520px){.metric{padding:12px}.metric strong{font-size:27px}summary{gap:7px;padding:12px}time{font-size:12px}}
</style></head>
<body><header><div class="wrap">
<nav aria-label="ניווט בדוח"><b class="brand" dir="ltr">DummyPay · QA</b><div><a href="#summary">סיכום</a><a href="#scenarios">תרחישים וצילומים</a></div></nav>
<h1>פרופיל והגדרות</h1><p>דוח אוטומציה · Playwright / pytest · <bdi>Chromium</bdi></p>
</div></header><main class="wrap">
<div class="metrics" id="summary">
<div class="metric"><strong>{{TOTAL}}</strong><span>תרחישים</span></div>
<div class="metric"><strong>{{PASSED}}</strong><span>עברו בהצלחה</span></div>
<div class="metric"><strong>{{IMAGES}}</strong><span>צילומי מסך</span></div>
</div>
<section id="scenarios"><div class="section-head"><h2>תרחישי הבדיקה</h2><button type="button" id="toggle">פתיחת כל התרחישים</button></div>
{{CASES}}</section>
<footer>צילומי מסך מלאים לפי סדר הביצוע. לחיצה על תמונה פותחת אותה בהגדלה.</footer>
</main>
<dialog aria-labelledby="caption"><form method="dialog"><button>סגירה</button></form><p id="caption"></p><img alt=""></dialog>
<script>
const dialog = document.querySelector("dialog");
document.querySelectorAll(".shot").forEach(button => button.addEventListener("click", () => {
  const image = button.querySelector("img");
  dialog.querySelector("img").src = image.src;
  dialog.querySelector("img").alt = image.alt;
  document.querySelector("#caption").textContent = image.alt;
  dialog.showModal();
}));
const cards = [...document.querySelectorAll(".case")];
const toggle = document.querySelector("#toggle");
const update = () => {
  toggle.textContent = cards.every(card => card.open) ? "סגירת כל התרחישים" : "פתיחת כל התרחישים";
};
toggle.addEventListener("click", () => {
  const open = !cards.every(card => card.open);
  cards.forEach(card => { card.open = open; });
  update();
});
cards.forEach(card => card.addEventListener("toggle", update));
</script></body></html>"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    buildReport(args.source, args.destination)
