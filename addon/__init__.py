"""Hover Glossary: plain-English pop-up definitions for medical terms on any card.

Terms are marked in the reviewer webview by web/glossary.js after the card is
drawn, so note fields are never changed (safe with AnkiHub/AnKing updates,
AnkiCollab, and Onigiri's edit-in-reviewer, which the script steps out of).

Data: web/glossary_data.js (built by tools/build_data.py) plus the user's own
edits in user_files/overrides.json, which survive add-on updates.
"""

import json
import os

from aqt import gui_hooks, mw
from aqt.qt import QAction, QDialog, QDialogButtonBox, QLabel, QPlainTextEdit, QVBoxLayout

ADDON_DIR = os.path.dirname(__file__)
ADDON_PKG = mw.addonManager.addonFromModule(__name__)
OVERRIDES = os.path.join(ADDON_DIR, "user_files", "overrides.json")

mw.addonManager.setWebExports(__name__, r"web/.*\.(js|css)")


def _config():
    return mw.addonManager.getConfig(__name__) or {}


def _load_overrides():
    try:
        with open(OVERRIDES, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _save_overrides(data):
    os.makedirs(os.path.dirname(OVERRIDES), exist_ok=True)
    with open(OVERRIDES, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def _is_review_surface(context):
    from aqt.reviewer import Reviewer

    if isinstance(context, Reviewer):
        return True
    try:
        from aqt.browser.previewer import Previewer

        return isinstance(context, Previewer)
    except ImportError:
        return False


def on_webview_will_set_content(web_content, context):
    if not _is_review_surface(context):
        return
    cfg = _config()
    base = f"/_addons/{ADDON_PKG}/web"
    opts = {
        "enabled": cfg.get("enabled", True),
        "question": cfg.get("showOnQuestion", True),
        "everyOccurrence": cfg.get("markEveryOccurrence", False),
        "hoverDelayMs": cfg.get("hoverDelayMs", 120),
        "overrides": _load_overrides(),
    }
    web_content.css.append(f"{base}/glossary.css")
    web_content.head += f"<script>window.HG_OPTS = {json.dumps(opts)};</script>"
    web_content.js.append(f"{base}/glossary_data.js")
    web_content.js.append(f"{base}/glossary.js")


def _edit_definition(web, key, title, current):
    dlg = QDialog(mw)
    dlg.setWindowTitle(f"Edit definition: {title}")
    lay = QVBoxLayout(dlg)
    lay.addWidget(QLabel("Plain-English definition (leave empty to restore the default):"))
    box = QPlainTextEdit(current)
    box.setMinimumSize(460, 140)
    lay.addWidget(box)
    btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
    btns.accepted.connect(dlg.accept)
    btns.rejected.connect(dlg.reject)
    lay.addWidget(btns)
    if not dlg.exec():
        return
    text = box.toPlainText().strip()
    data = _load_overrides()
    if text:
        data[key] = text
    else:
        data.pop(key, None)
    _save_overrides(data)
    web.eval(f"window.HG && HG.setOverride({json.dumps(key)}, {json.dumps(text or None)});")


def on_js_message(handled, message, context):
    if not isinstance(message, str) or not message.startswith("hg:edit:"):
        return handled
    payload = json.loads(message[len("hg:edit:"):])
    web = getattr(context, "web", None) or getattr(context, "_web", None) or mw.reviewer.web
    _edit_definition(web, payload["key"], payload["title"], payload.get("def", ""))
    return (True, None)


def _toggle(checked):
    cfg = _config()
    cfg["enabled"] = bool(checked)
    mw.addonManager.writeConfig(__name__, cfg)
    if mw.reviewer and mw.reviewer.web:
        mw.reviewer.web.eval(f"window.HG && HG.setEnabled({json.dumps(bool(checked))});")


def _add_menu():
    action = QAction("Hover Glossary definitions", mw)
    action.setCheckable(True)
    action.setChecked(_config().get("enabled", True))
    action.toggled.connect(_toggle)
    mw.form.menuTools.addAction(action)


_add_menu()
gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
gui_hooks.webview_did_receive_js_message.append(on_js_message)
