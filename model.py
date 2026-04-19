import os
import config

DATA_FILE = "elements.dat"

class Element:
	def __init__(self, symbol, name_de, name_en, oz, mass, en, period, group, state_de, state_en, cat_de, cat_en, elem_config):
		self.symbol = symbol
		self.name_de = name_de
		self.name_en = name_en
		self.oz = oz
		self.mass = mass
		self.en = en
		self.period = period
		self.group = group
		self.state_de = state_de
		self.state_en = state_en
		self.cat_de = cat_de
		self.cat_en = cat_en
		self.config = elem_config

	@property
	def name(self):
		return self.name_de if config.get_active_language() == "de" else self.name_en
		
	@property
	def state(self):
		return self.state_de if config.get_active_language() == "de" else self.state_en
		
	@property
	def category(self):
		return self.cat_de if config.get_active_language() == "de" else self.cat_en

	def get_list_label(self):
		if config.SETTINGS.get("verbose_sr", False):
			return f"{config.t('atomic_number')} {self.oz}, {self.name}, {config.t('symbol')} {self.symbol}, {config.t('category')}: {self.category}"
		return f"{self.oz} {self.symbol}, {self.name}"

	def get_details_text(self):
		if config.SETTINGS.get("verbose_sr", False):
			return (f"{config.t('name')}: {self.name}\n"
					f"{config.t('symbol')}: {self.symbol}\n"
					f"{config.t('atomic_number')}: {self.oz}\n"
					f"{config.t('category')}: {self.category}\n"
					f"{config.t('state')}: {self.state}\n"
					f"{config.t('config')}: {self.config}\n"
					f"{config.t('mass')}: {self.mass} u\n"
					f"{config.t('electronegativity')}: {self.en}\n"
					f"{config.t('period')}: {self.period}\n"
					f"{config.t('group')}: {self.group}\n\n"
					f"Zusätzliche Audio-Info: Element {self.name}, "
					f"Kategorie {self.category}, Zustand {self.state}.")
		else:
			return (f"{config.t('name')}: {self.name}\n"
					f"{config.t('symbol')}: {self.symbol}\n"
					f"{config.t('atomic_number')}: {self.oz}\n"
					f"{config.t('category')}: {self.category}\n"
					f"{config.t('state')}: {self.state}\n"
					f"{config.t('config')}: {self.config}\n"
					f"{config.t('mass')}: {self.mass} u\n"
					f"{config.t('electronegativity')}: {self.en}\n"
					f"{config.t('period')}: {self.period}\n"
					f"{config.t('group')}: {self.group}")

	def get_mass_float(self):
		clean_mass = self.mass.replace("(", "").replace(")", "").strip()
		try:
			return float(clean_mass)
		except ValueError:
			return 0.0

def load_elements(filename):
	elements = []
	full_path = config.get_resource_path(filename)
	if not os.path.exists(full_path):
		return []
	
	with open(full_path, "r", encoding="utf-8") as f:
		for line in f:
			line = line.strip()
			if not line or "{" not in line: continue
			try:
				symbol, rest = line.split("{")
				rest = rest.replace("}", "")
				data = rest.split(";")
				
				elem = Element(
					symbol=symbol.strip(),
					name_de=data[0],
					name_en=data[1],
					oz=int(data[2]),
					mass=data[3],
					en=data[4],
					period=data[5],
					group=data[6],
					state_de=data[7],
					state_en=data[8],
					cat_de=data[9],
					cat_en=data[10],
					elem_config=data[11] if len(data) > 11 else ""
				)
				elements.append(elem)
			except Exception:
				continue
				
	elements.sort(key=lambda x: x.oz)
	return elements