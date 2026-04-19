import wx
import config
import model
from dialogs import SettingsDialog, CalculatorDialog, DetailDialog

class MainFrame(wx.Frame):
	def __init__(self):
		super().__init__(None, title=config.t("title"), size=(650, 750))
		
		self.panel = wx.Panel(self, style=wx.WANTS_CHARS)
		
		# --- Screenreader Proxy ---
		self.sr_proxy = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.WANTS_CHARS, pos=(-20000, -20000))
		self.sr_proxy.Bind(wx.EVT_KEY_DOWN, self.on_proxy_key)
		self.sr_proxy.Hide() 

		self.all_elements = model.load_elements(model.DATA_FILE)
		self.displayed_elements = list(self.all_elements)
		
		self.grid_map = {}
		for e in self.all_elements:
			try:
				p = int(e.period); g = int(e.group)
				self.grid_map[(p, g)] = e
			except: pass
		
		self.cur_period = 1
		self.cur_group = 1
		self.overview_active = False

		# Menü
		menubar = wx.MenuBar()
		file_menu = wx.Menu()
		item_exit = file_menu.Append(wx.ID_EXIT, config.t("exit"), config.t("exit"))
		menubar.Append(file_menu, config.t("file"))
		
		view_menu = wx.Menu()
		self.item_view_list = view_menu.AppendRadioItem(wx.ID_ANY, config.t("list_view"))
		self.item_view_grid = view_menu.AppendRadioItem(wx.ID_ANY, config.t("grid_view"))
		menubar.Append(view_menu, config.t("view"))

		tools_menu = wx.Menu()
		item_search = tools_menu.Append(wx.ID_ANY, config.t("search"), config.t("search"))
		item_calc = tools_menu.Append(wx.ID_ANY, config.t("calc"), config.t("calc"))
		item_settings = tools_menu.Append(wx.ID_ANY, config.t("settings"), config.t("settings"))
		menubar.Append(tools_menu, config.t("tools"))
		self.SetMenuBar(menubar)
		
		# Layout
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(self.main_sizer)

		# --- Listen-Ansicht UI ---
		self.sizer_list_view = wx.BoxSizer(wx.VERTICAL)
		
		hbox_filter = wx.BoxSizer(wx.HORIZONTAL)
		self.chk_filter = wx.CheckBox(self.panel, label=config.t("filter_active"))
		hbox_filter.Add(self.chk_filter, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=10)
		
		categories = sorted(list(set(e.category for e in self.all_elements)))
		filter_choices = [config.t("main_groups"), config.t("sub_groups")] + categories
		self.choice_filter = wx.Choice(self.panel, choices=filter_choices)
		hbox_filter.Add(self.choice_filter, proportion=1, flag=wx.ALIGN_CENTER_VERTICAL)
		
		self.choice_filter.Hide() 
		
		self.sizer_list_view.Add(hbox_filter, flag=wx.EXPAND | wx.ALL, border=10)
		
		self.list_box = wx.ListBox(self.panel, style=wx.LB_SINGLE)
		self.sizer_list_view.Add(self.list_box, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

		# --- Übersichts-Ansicht UI ---
		self.sizer_grid_view = wx.BoxSizer(wx.VERTICAL)
		self.init_overview_ui()

		self.main_sizer.Add(self.sizer_list_view, 1, wx.EXPAND)
		self.main_sizer.Add(self.sizer_grid_view, 1, wx.EXPAND)
		self.main_sizer.Hide(self.sizer_grid_view)
		
		self.refresh_list()

		# Bindings
		self.Bind(wx.EVT_CHECKBOX, self.on_toggle_filter, self.chk_filter)
		self.Bind(wx.EVT_CHOICE, self.on_filter_change, self.choice_filter)
		self.Bind(wx.EVT_LISTBOX_DCLICK, self.on_open_details_list, self.list_box)
		
		self.Bind(wx.EVT_MENU, self.on_exit, item_exit)
		self.Bind(wx.EVT_MENU, self.on_open_calculator, item_calc)
		self.Bind(wx.EVT_MENU, self.on_open_settings, item_settings)
		self.Bind(wx.EVT_MENU, self.on_search, item_search)
		self.Bind(wx.EVT_MENU, self.on_view_change, self.item_view_list)
		self.Bind(wx.EVT_MENU, self.on_view_change, self.item_view_grid)
		
		self.panel.Bind(wx.EVT_CHAR_HOOK, self.on_key_hook)
		
		ID_DETAILS = wx.NewIdRef()
		self.Bind(wx.EVT_MENU, self.on_details_shortcut, id=ID_DETAILS)
		
		self.SetAcceleratorTable(wx.AcceleratorTable([
			(wx.ACCEL_CTRL, ord('F'), item_search.GetId()),
			(wx.ACCEL_NORMAL, wx.WXK_RETURN, ID_DETAILS),
			(wx.ACCEL_NORMAL, wx.WXK_NUMPAD_ENTER, ID_DETAILS),
			(wx.ACCEL_CTRL, ord('M'), item_calc.GetId()),
			(wx.ACCEL_CTRL, ord('E'), item_settings.GetId())
		]))
		
		config.apply_accessibility(self)
		self.list_box.SetFocus()
		self.panel.Layout()
		self.Show()

	def init_overview_ui(self):
		info_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.lbl_nav_pos = wx.StaticText(self.panel, label=f"{config.t('pos')}: -")
		self.lbl_nav_pos.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
		info_sizer.Add(self.lbl_nav_pos, 0, wx.ALL, 10)
		self.sizer_grid_view.Add(info_sizer, 0, wx.ALIGN_CENTER)
		self.sizer_grid_view.AddSpacer(20)

		self.card_panel = wx.Panel(self.panel, style=wx.SIMPLE_BORDER)
		self.card_panel.SetBackgroundColour(wx.Colour(240, 240, 240))
		card_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.lbl_grid_oz = wx.StaticText(self.card_panel, label="1")
		card_sizer.Add(self.lbl_grid_oz, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
		self.lbl_grid_symbol = wx.StaticText(self.card_panel, label="H")
		self.lbl_grid_symbol.SetFont(wx.Font(48, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
		card_sizer.Add(self.lbl_grid_symbol, 0, wx.ALIGN_CENTER | wx.ALL, 20)
		self.lbl_grid_name = wx.StaticText(self.card_panel, label="Wasserstoff")
		self.lbl_grid_name.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		card_sizer.Add(self.lbl_grid_name, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
		self.lbl_grid_mass = wx.StaticText(self.card_panel, label="1.008 u")
		card_sizer.Add(self.lbl_grid_mass, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)
		
		self.card_panel.SetSizer(card_sizer)
		self.sizer_grid_view.Add(self.card_panel, 0, wx.ALIGN_CENTER | wx.ALL, 20)
		
		help_txt = wx.StaticText(self.panel, label=config.t("nav_help"))
		help_txt.SetForegroundColour(wx.Colour(100, 100, 100))
		self.sizer_grid_view.Add(help_txt, 0, wx.ALIGN_CENTER | wx.TOP, 20)
		self.sizer_grid_view.AddStretchSpacer()

	def on_view_change(self, event):
		if self.item_view_list.IsChecked():
			self.overview_active = False
			self.main_sizer.Hide(self.sizer_grid_view)
			self.main_sizer.Show(self.sizer_list_view)
			self.sr_proxy.Hide()
			if not self.chk_filter.GetValue():
				self.choice_filter.Hide()
			self.list_box.SetFocus()
		else:
			self.overview_active = True
			self.main_sizer.Hide(self.sizer_list_view)
			self.main_sizer.Show(self.sizer_grid_view)
			self.sr_proxy.Show()
			self.update_grid_display()
		self.panel.Layout()

	def update_grid_display(self):
		p, g = self.cur_period, self.cur_group
		self.lbl_nav_pos.SetLabel(f"{config.t('period')}: {p}  |  {config.t('group')}: {g}")
		
		elem = self.grid_map.get((p, g))
		
		is_high_contrast = config.SETTINGS.get("high_contrast", False)
		default_fg = wx.Colour(255, 255, 0) if is_high_contrast else wx.BLACK
		muted_fg = wx.Colour(200, 200, 0) if is_high_contrast else wx.Colour(200, 200, 200)
		
		if elem:
			self.lbl_grid_symbol.SetLabel(elem.symbol)
			self.lbl_grid_name.SetLabel(elem.name)
			self.lbl_grid_oz.SetLabel(str(elem.oz))
			self.lbl_grid_mass.SetLabel(f"{elem.mass} u")
			self.lbl_grid_symbol.SetForegroundColour(default_fg)
		else:
			self.lbl_grid_symbol.SetLabel("-")
			self.lbl_grid_name.SetLabel(config.t("no_element"))
			self.lbl_grid_oz.SetLabel("-")
			self.lbl_grid_mass.SetLabel("")
			self.lbl_grid_symbol.SetForegroundColour(muted_fg)

		if config.SETTINGS.get("verbose_sr", False):
			a11y_text = f"{config.t('period')} {p}, {config.t('group')} {g}. "
			if elem:
				a11y_text += f"{elem.name}, {config.t('symbol')} {elem.symbol}, {config.t('atomic_number')} {elem.oz}, {config.t('mass')} {elem.mass} Units, {config.t('category')} {elem.category}."
			else:
				a11y_text += f"{config.t('no_element')}."
		else:
			a11y_text = f"{p}, {g}. {elem.name if elem else config.t('no_element')}."
			
		self.sr_proxy.SetValue(a11y_text)
		self.sr_proxy.SetFocus()
		self.panel.Layout()

	def on_proxy_key(self, event):
		key = event.GetKeyCode()
		if key in (wx.WXK_UP, wx.WXK_DOWN, wx.WXK_LEFT, wx.WXK_RIGHT):
			changed = False
			if key == wx.WXK_RIGHT:
				if self.cur_group < 18: self.cur_group += 1; changed = True
			elif key == wx.WXK_LEFT:
				if self.cur_group > 1: self.cur_group -= 1; changed = True
			elif key == wx.WXK_DOWN:
				if self.cur_period < 7: self.cur_period += 1; changed = True
			elif key == wx.WXK_UP:
				if self.cur_period > 1: self.cur_period -= 1; changed = True
				
			if changed:
				self.update_grid_display()
		elif key == wx.WXK_RETURN or key == wx.WXK_NUMPAD_ENTER:
			self.on_details_shortcut(None)
		else:
			event.Skip()

	def on_key_hook(self, event):
		if not self.overview_active:
			event.Skip(); return
			
		self.on_proxy_key(event)

	def on_details_shortcut(self, event):
		if self.overview_active:
			elem = self.grid_map.get((self.cur_period, self.cur_group))
			if elem:
				dlg = DetailDialog(self, elem)
				dlg.ShowModal()
				dlg.Destroy()
				wx.CallAfter(self.force_sr_update)
		else:
			self.on_open_details_list(None)

	def force_sr_update(self):
		self.sr_proxy.SetFocus()

	def refresh_list(self):
		old_selection = self.list_box.GetSelection()
		self.list_box.Clear()
		for elem in self.displayed_elements: self.list_box.Append(elem.get_list_label())
		if self.displayed_elements:
			if old_selection != wx.NOT_FOUND and old_selection < self.list_box.GetCount():
				self.list_box.SetSelection(old_selection)
			else:
				self.list_box.SetSelection(0)
		else:
			self.list_box.Append(config.t("not_found"))

	def on_toggle_filter(self, event):
		if self.chk_filter.GetValue():
			self.choice_filter.Show()
			if self.choice_filter.GetCount()>0 and self.choice_filter.GetSelection()==wx.NOT_FOUND:
				self.choice_filter.SetSelection(0)
			self.apply_filter(); self.choice_filter.SetFocus()
		else:
			self.choice_filter.Hide(); self.displayed_elements = list(self.all_elements); self.refresh_list(); self.list_box.SetFocus()
		self.panel.Layout()

	def on_filter_change(self, event): self.apply_filter()
	def apply_filter(self):
		sel = self.choice_filter.GetStringSelection()
		mg = {"1","2","13","14","15","16","17","18"}; tg = {str(i) for i in range(3,13)}
		if sel == config.t("main_groups"): self.displayed_elements = [e for e in self.all_elements if e.group in mg]
		elif sel == config.t("sub_groups"): self.displayed_elements = [e for e in self.all_elements if e.group in tg]
		else: self.displayed_elements = [e for e in self.all_elements if e.category == sel]
		self.refresh_list()

	def on_open_details_list(self, event):
		s = self.list_box.GetSelection()
		if s != wx.NOT_FOUND and self.displayed_elements:
			d = DetailDialog(self, self.displayed_elements[s]); d.ShowModal(); d.Destroy(); self.list_box.SetFocus()

	def on_open_calculator(self, event):
		d = CalculatorDialog(self, self.all_elements); d.ShowModal(); d.Destroy()
		if self.overview_active: wx.CallAfter(self.force_sr_update)
		else: self.list_box.SetFocus()

	def on_open_settings(self, event):
		d = SettingsDialog(self)
		if d.ShowModal() == wx.ID_OK:
			config.apply_accessibility(self)
			self.refresh_list()
			if self.overview_active:
				self.update_grid_display()
			self.panel.Layout()
			self.Refresh()
		d.Destroy()

	def on_search(self, event):
		d = wx.TextEntryDialog(self, config.t("search_prompt"), config.t("search"))
		config.apply_accessibility(d)
		if d.ShowModal() == wx.ID_OK: self.perform_search(d.GetValue().strip().lower())
		d.Destroy()
		if self.overview_active: wx.CallAfter(self.force_sr_update)
		else: self.list_box.SetFocus()

	def perform_search(self, query):
		if not query: return
		if self.overview_active:
			t_elem = next((e for e in self.all_elements if query in (e.symbol.lower(), str(e.oz), e.name_de.lower(), e.name_en.lower())), None)
			if t_elem: 
				self.cur_period = int(t_elem.period); self.cur_group = int(t_elem.group); self.update_grid_display()
			else: wx.MessageBox(config.t("not_found"))
			return
		
		idx = -1
		for i, e in enumerate(self.displayed_elements):
			if query in (e.symbol.lower(), str(e.oz)): idx = i; break
		if idx == -1:
			for i, e in enumerate(self.displayed_elements):
				if query in e.name_de.lower() or query in e.name_en.lower(): idx = i; break
		if idx != -1: self.list_box.SetSelection(idx); self.list_box.EnsureVisible(idx); self.on_open_details_list(None)
		else: wx.MessageBox(config.t("not_found"))

	def on_exit(self, event): self.Close()

if __name__ == "__main__":
	config.load_settings()
	app = wx.App()
	frame = MainFrame()
	app.MainLoop()