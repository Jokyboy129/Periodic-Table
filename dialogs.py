import wx
import wx.adv
import re
import config

class SettingsDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title=config.t("settings_title"), size=(400, 400))
		
		panel = wx.Panel(self)
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		lbl_lang = wx.StaticText(panel, label="Sprache / Language:")
		vbox.Add(lbl_lang, flag=wx.LEFT | wx.TOP, border=10)
		
		self.choice_lang = wx.Choice(panel, choices=[config.t("lang_auto"), config.t("lang_de"), config.t("lang_en")])
		if config.SETTINGS["language"] == "de": self.choice_lang.SetSelection(1)
		elif config.SETTINGS["language"] == "en": self.choice_lang.SetSelection(2)
		else: self.choice_lang.SetSelection(0)
		vbox.Add(self.choice_lang, flag=wx.EXPAND | wx.ALL, border=10)
		
		sb = wx.StaticBox(panel, label=config.t("settings_a11y"))
		sbs = wx.StaticBoxSizer(sb, wx.VERTICAL)
		
		self.chk_contrast = wx.CheckBox(panel, label=config.t("high_contrast"))
		self.chk_contrast.SetValue(config.SETTINGS["high_contrast"])
		sbs.Add(self.chk_contrast, flag=wx.ALL, border=5)
		
		self.chk_font = wx.CheckBox(panel, label=config.t("large_font"))
		self.chk_font.SetValue(config.SETTINGS["large_font"])
		sbs.Add(self.chk_font, flag=wx.ALL, border=5)
		
		self.chk_sr = wx.CheckBox(panel, label=config.t("verbose_sr"))
		self.chk_sr.SetValue(config.SETTINGS["verbose_sr"])
		sbs.Add(self.chk_sr, flag=wx.ALL, border=5)
		
		vbox.Add(sbs, flag=wx.EXPAND | wx.ALL, border=10)
		
		btn_save = wx.Button(panel, label=config.t("save"))
		btn_save.Bind(wx.EVT_BUTTON, self.on_save)
		vbox.Add(btn_save, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
		
		panel.SetSizer(vbox)
		config.apply_accessibility(self)
		
	def on_save(self, event):
		old_lang = config.SETTINGS["language"]
		
		sel = self.choice_lang.GetSelection()
		if sel == 1: config.SETTINGS["language"] = "de"
		elif sel == 2: config.SETTINGS["language"] = "en"
		else: config.SETTINGS["language"] = "auto"
		
		config.SETTINGS["high_contrast"] = self.chk_contrast.GetValue()
		config.SETTINGS["large_font"] = self.chk_font.GetValue()
		config.SETTINGS["verbose_sr"] = self.chk_sr.GetValue()
		
		config.save_settings()
		
		if old_lang != config.SETTINGS["language"]:
			wx.MessageBox(config.t("restart_req"), config.t("settings_title"), wx.OK | wx.ICON_INFORMATION)
			
		self.EndModal(wx.ID_OK)

class CalculatorDialog(wx.Dialog):
	def __init__(self, parent, elements):
		super().__init__(parent, title=config.t("calc_title"), size=(450, 450))
		self.elements = elements
		self.mass_dict = {e.symbol: e.get_mass_float() for e in elements}
		self.name_dict = {e.symbol: e.name for e in elements}

		panel = wx.Panel(self)
		vbox = wx.BoxSizer(wx.VERTICAL)

		lbl_info = wx.TextCtrl(panel, value=config.t("calc_info"), 
							   style=wx.TE_READONLY | wx.TE_MULTILINE | wx.BORDER_NONE)
		lbl_info.SetMinSize((-1, 40)) 
		vbox.Add(lbl_info, flag=wx.ALL | wx.EXPAND, border=10)

		self.txt_formula = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
		vbox.Add(self.txt_formula, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

		btn_calc = wx.Button(panel, label=config.t("calc_btn"))
		vbox.Add(btn_calc, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=15)

		self.txt_result = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
		vbox.Add(self.txt_result, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

		btn_close = wx.Button(panel, wx.ID_CANCEL, config.t("close"))
		vbox.Add(btn_close, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)

		panel.SetSizer(vbox)

		btn_calc.Bind(wx.EVT_BUTTON, self.on_calculate)
		self.txt_formula.Bind(wx.EVT_TEXT_ENTER, self.on_calculate)
		
		config.apply_accessibility(self)
		
		if not config.SETTINGS.get("high_contrast", False):
			lbl_info.SetBackgroundColour(panel.GetBackgroundColour())
			
		self.txt_formula.SetFocus()

	def on_calculate(self, event):
		formula = self.txt_formula.GetValue().strip()
		if not formula: return
		try:
			raw_tokens = re.findall(r'([A-Z][a-z]?)|(\d+)|(\()|(\))', formula)
			tokens = [item for t in raw_tokens for item in t if item]
			
			stack = [{}] 
			i = 0
			error_msg = ""
			while i < len(tokens):
				token = tokens[i]
				if token == '(':
					stack.append({}); i += 1
				elif token == ')':
					if len(stack) < 2: error_msg = config.t("calc_error"); break
					multiplier = 1
					if i + 1 < len(tokens) and tokens[i+1].isdigit():
						multiplier = int(tokens[i+1]); i += 1 
					current = stack.pop(); parent = stack[-1]
					for a, c in current.items(): parent[a] = parent.get(a, 0) + c * multiplier
					i += 1
				elif token.isdigit(): i += 1
				else:
					if token not in self.mass_dict: error_msg = config.t("calc_unknown"); break
					c = 1
					if i + 1 < len(tokens) and tokens[i+1].isdigit():
						c = int(tokens[i+1]); i += 1
					stack[-1][token] = stack[-1].get(token, 0) + c
					i += 1
			
			if error_msg: self.txt_result.SetValue(error_msg); return
			
			final = stack[0]
			total = sum(self.mass_dict[a] * c for a, c in final.items())
			details = [f"{a}: {c} x {self.mass_dict[a]} = {c*self.mass_dict[a]:.3f}" for a, c in final.items()]
			self.txt_result.SetValue(f"{config.t('calc_total')} {total:.4f} u\n" + "\n".join(details))
			self.txt_result.SetFocus()
		except Exception as e:
			self.txt_result.SetValue(str(e))

class DetailDialog(wx.Dialog):
	def __init__(self, parent, element):
		super().__init__(parent, title=f"{config.t('details_title')} {element.name}", size=(450, 500))
		panel = wx.Panel(self)
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		info_text = wx.TextCtrl(panel, value=element.get_details_text(), 
								style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_NO_VSCROLL)
		vbox.Add(info_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
		
		lang_prefix = "de" if config.get_active_language() == "de" else "en"
		wiki_url = f"https://{lang_prefix}.wikipedia.org/wiki/{element.name}"
		link_label = config.t("wiki_link").format(element.name)
		link = wx.adv.HyperlinkCtrl(panel, label=link_label, url=wiki_url)
		vbox.Add(link, flag=wx.ALL | wx.ALIGN_LEFT, border=10)
		
		btn_close = wx.Button(panel, wx.ID_CANCEL, config.t("close"))
		vbox.Add(btn_close, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)
		
		panel.SetSizer(vbox)
		config.apply_accessibility(self)
		info_text.SetFocus()