import os
import sys
import json
import locale
import wx
import wx.adv

SETTINGS_FILE = "settings.json"

# --- STANDARD EINSTELLUNGEN ---
DEFAULT_SETTINGS = {
	"language": "auto",
	"high_contrast": False,
	"large_font": False,
	"verbose_sr": False
}

SETTINGS = DEFAULT_SETTINGS.copy()

def load_settings():
	global SETTINGS
	if os.path.exists(SETTINGS_FILE):
		try:
			with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
				loaded = json.load(f)
				SETTINGS.update(loaded)
		except Exception:
			pass

def save_settings():
	try:
		with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
			json.dump(SETTINGS, f, indent=4)
	except Exception:
		pass

def get_active_language():
	if SETTINGS["language"] == "auto":
		try:
			loc = locale.getdefaultlocale()[0]
			if loc and loc.lower().startswith("de"):
				return "de"
		except Exception:
			pass
		return "en"
	return SETTINGS["language"]

# --- ÜBERSETZUNGEN ---
TRANSLATIONS = {
	"de": {
		"title": "Periodensystem",
		"calc_title": "Molmassen-Rechner",
		"settings_title": "Einstellungen",
		"file": "&Datei",
		"exit": "Beenden",
		"view": "&Ansicht",
		"list_view": "Listenansicht",
		"grid_view": "Übersichtsmodus",
		"tools": "&Werkzeuge",
		"search": "&Suchen\tCtrl+F",
		"calc": "&Molrechner\tCtrl+M",
		"settings": "E&instellungen\tCtrl+E",
		"filter_active": "Filter aktivieren",
		"main_groups": "Hauptgruppen",
		"sub_groups": "Nebengruppen",
		"close": "Schließen",
		"calc_info": "Formel eingeben (z.B. Ca(NO3)2 oder NaCl):",
		"calc_btn": "Berechnen",
		"calc_total": "Gesamt:",
		"calc_error": "Fehler in der Formel",
		"calc_unknown": "Unbekanntes Element",
		"details_title": "Details zu",
		"wiki_link": "Wikipedia-Artikel zu {} öffnen",
		"pos": "Position",
		"period": "Periode",
		"group": "Gruppe",
		"no_element": "Kein Element",
		"nav_help": "Navigation:\n↓ Periode (Runter) | → Gruppe (Rechts)\nENTER für Details",
		"not_found": "Nichts gefunden.",
		"search_prompt": "Suche nach Element, Symbol oder Ordnungszahl:",
		"lang_auto": "Automatisch (Systemsprache)",
		"lang_de": "Deutsch",
		"lang_en": "Englisch",
		"settings_a11y": "Bedienungshilfen (Blinde / Sehbehinderte)",
		"high_contrast": "Hoher Kontrast (Schwarz / Gelb)",
		"large_font": "Größere Schrift",
		"verbose_sr": "Ausführliche Screenreader-Ansagen",
		"save": "Speichern",
		"atomic_number": "Ordnungszahl",
		"mass": "Atommasse",
		"electronegativity": "Elektronegativität",
		"state": "Zustand",
		"category": "Serie",
		"config": "Elektronenkonfiguration",
		"symbol": "Symbol",
		"name": "Name",
		"restart_req": "Bitte starte das Programm neu, damit die neue Sprache vollständig übernommen wird."
	},
	"en": {
		"title": "Periodic Table",
		"calc_title": "Molar Mass Calculator",
		"settings_title": "Settings",
		"file": "&File",
		"exit": "Exit",
		"view": "&View",
		"list_view": "List View",
		"grid_view": "Grid View",
		"tools": "&Tools",
		"search": "&Search\tCtrl+F",
		"calc": "&Calculator\tCtrl+M",
		"settings": "&Settings\tCtrl+E",
		"filter_active": "Enable Filter",
		"main_groups": "Main Groups",
		"sub_groups": "Transition Metals",
		"close": "Close",
		"calc_info": "Enter formula (e.g., Ca(NO3)2 or NaCl):",
		"calc_btn": "Calculate",
		"calc_total": "Total:",
		"calc_error": "Formula error",
		"calc_unknown": "Unknown element",
		"details_title": "Details for",
		"wiki_link": "Open Wikipedia article for {}",
		"pos": "Position",
		"period": "Period",
		"group": "Group",
		"no_element": "No Element",
		"nav_help": "Navigation:\n↓ Period (Down) | → Group (Right)\nENTER for Details",
		"not_found": "Nothing found.",
		"search_prompt": "Search for element, symbol or atomic number:",
		"lang_auto": "Automatic (System Language)",
		"lang_de": "German",
		"lang_en": "English",
		"settings_a11y": "Accessibility (Blind / Visually Impaired)",
		"high_contrast": "High Contrast (Black / Yellow)",
		"large_font": "Large Font",
		"verbose_sr": "Verbose Screen Reader Announcements",
		"save": "Save",
		"atomic_number": "Atomic Number",
		"mass": "Atomic Mass",
		"electronegativity": "Electronegativity",
		"state": "State",
		"category": "Category",
		"config": "Electron Configuration",
		"symbol": "Symbol",
		"name": "Name",
		"restart_req": "Please restart the application to fully apply the new language."
	}
}

def t(key):
	lang = get_active_language()
	if lang not in TRANSLATIONS: lang = "en"
	return TRANSLATIONS[lang].get(key, key)

def apply_accessibility(win):
	is_hc = SETTINGS.get("high_contrast", False)
	is_large = SETTINGS.get("large_font", False)
	
	font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
	if is_large:
		font.SetPointSize(font.GetPointSize() + 4)
	win.SetFont(font)
	
	if is_hc:
		win.SetBackgroundColour(wx.Colour(0, 0, 0))
		if isinstance(win, wx.adv.HyperlinkCtrl):
			win.SetNormalColour(wx.Colour(255, 255, 0))
			win.SetHoverColour(wx.Colour(255, 200, 0))
			win.SetVisitedColour(wx.Colour(255, 255, 0))
		win.SetForegroundColour(wx.Colour(255, 255, 0))
	else:
		win.SetBackgroundColour(wx.NullColour)
		if isinstance(win, wx.adv.HyperlinkCtrl):
			win.SetNormalColour(wx.Colour(0, 0, 255))
			win.SetHoverColour(wx.Colour(0, 0, 255))
			win.SetVisitedColour(wx.Colour(0, 0, 255))
		win.SetForegroundColour(wx.NullColour)
		
	for child in win.GetChildren():
		apply_accessibility(child)

def get_resource_path(relative_path):
	try:
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)