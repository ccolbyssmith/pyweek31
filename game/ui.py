import pygame

from game.utils import Text, TextButton, LinedText, Button

PANEL_COLOR = (75, 75, 75)
PANEL_BORDER_COLOR = (0, 0, 0)

class TowerInfoPanel:
	def __init__(self, screen, tower, pos):
		self.screen = screen
		self.tower = tower
		self.pos = pos

		self.size = (250, 530)
		self.panel = pygame.Surface(self.size)
		self.rect = pygame.Rect(self.pos, self.size)
		self.panel.fill(PANEL_COLOR)
		
		if self.tower == None:
			return

		self.title = Text(self.tower.name, [self.pos[0] + self.size[0] / 2, self.pos[1] + 10], 36, centered=True)

		self.make_info_text()
		self.make_upgrade_button()

		self.info_image = pygame.transform.scale(self.tower.info_image, (275,275))
		self.flavor_text = LinedText(self.tower.text, (self.pos[0] + 15, self.pos[1] + 330), 30, size=14)

	# updates tower info text, needs to be called when tower is upgraded so info panel is accurate
	def make_info_text(self):
		self.lvl_text = Text("Lvl " + str(self.tower.lvl + 1), [self.pos[0] + self.size[0] / 2, self.pos[1] + 45], 18, centered=True)

		start_y = 383
		spacing = 25
		self.damage_text = Text("Damage: " + str(self.tower.damage), [self.pos[0] + 25, self.pos[1] + start_y], 22)
		self.range_text = Text("Range: " + str(self.tower.max_range), [self.pos[0] + 25, self.pos[1] + start_y + spacing], 22)
		self.speed_text = Text("Fire Speed: " + str(self.tower.fire_speed), [self.pos[0] + 25, self.pos[1] + start_y + spacing * 2], 22)

	def make_upgrade_button(self):
		if not self.tower.is_max_level():
			self.upgrade_button = TextButton("Promote", [self.pos[0] + self.size[0] / 2, self.pos[1] + 465], 38, centered=True, color=(0, 255, 0))
			self.upgrade_cost_text = Text("Costs " + str(self.tower.upgrade_cost()) + " goodwill", [self.pos[0] + self.size[0] / 2, self.pos[1] + 500], 14, centered=True)
		else:
			self.upgrade_button = Text("Max Level", [self.pos[0] + self.size[0] / 2, self.pos[1] + 465], 38, centered=True, color=(255, 204, 0))
			self.upgrade_cost_text = Text("", self.pos)

	def update(self, currency, loop):
		if self.tower == None:
			return currency

		cost = self.tower.upgrade_cost()
		if not self.tower.is_max_level() and self.upgrade_button.clicked and currency >= cost:
			self.tower.upgrade()
			self.make_info_text()
			self.make_upgrade_button()
			loop.soundManager.playBuildingSound()
			return currency - cost
		elif not self.tower.is_max_level() and self.upgrade_button.clicked:
			loop.soundManager.playFailSound()

		return currency

	def draw(self, tmap_offset):
		self.screen.blit(self.panel, self.pos)
		pygame.draw.rect(self.screen, PANEL_BORDER_COLOR, (self.pos, self.size), width=4)

		if self.tower == None:
			return

		# drawing range circle
		pygame.draw.circle(self.screen, (255,255,255), self.tower.center_pos(tmap_offset), self.tower.max_range, width=1)
		self.screen.blit(self.panel, self.pos) # has to redraw so panel is on top of range circle
		pygame.draw.rect(self.screen, PANEL_BORDER_COLOR, (self.pos, self.size), width=4)

		self.title.draw(self.screen)
		self.lvl_text.draw(self.screen)

		self.screen.blit(self.info_image, [self.pos[0] - 12, self.pos[1] + 60])
		self.flavor_text.draw(self.screen)

		self.damage_text.draw(self.screen)
		self.range_text.draw(self.screen)
		self.speed_text.draw(self.screen)

		self.upgrade_button.draw(self.screen)
		self.upgrade_cost_text.draw(self.screen)

	def get_rect(self):
		return self.rect

		
class BuyPanel:
	def __init__(self, screen, pos, towers, is_tower_unlocked, unlock_advanced_icon, unlock_advanced_cost):
		self.screen = screen
		self.pos = pos
		self.towers = towers
		self.is_tower_unlocked = is_tower_unlocked

		self.size = (1030, 200)
		self.panel = pygame.Surface(self.size)
		self.panel.fill(PANEL_COLOR)

		self.buttons = []
		for i in range(len(self.towers)):
			b = BuyButton(self.screen, [self.pos[0] + 20 + 200 * i, self.pos[1] + 10], self.towers[i])
			self.buttons.append(b)

		self.unlock_advanced_icon = unlock_advanced_icon
		self.unlock_advanced_text1 = Text("Unlock", [self.pos[0] + 800, self.pos[1] + 109], 24)
		self.unlock_advanced_text2 = Text("Advanced Weapons", [self.pos[0] + 800, self.pos[1] + 135], 24)
		self.unlock_advanced_cost_text = self.cost_text = Text("Costs " + str(unlock_advanced_cost) + " goodwill", [self.pos[0] + 820, self.pos[1] + 165], 14)
		self.unlock_advanced_button = Button(pygame.Rect([self.pos[0] + 800, self.pos[1]], [200, 175]))

	def update(self):
		for i,b in enumerate(self.buttons):
			b.update(self.is_tower_unlocked[i])

		self.unlock_advanced_button.draw(self.screen)

	def draw(self):
		self.screen.blit(self.panel, self.pos)
		pygame.draw.rect(self.screen, PANEL_BORDER_COLOR, (self.pos, self.size), width=4)

		for i,b in enumerate(self.buttons):
			b.draw(self.is_tower_unlocked[i])

		self.screen.blit(self.unlock_advanced_icon, [self.pos[0] + 820, self.pos[1] + 30])
		self.unlock_advanced_text1.draw(self.screen)
		self.unlock_advanced_text2.draw(self.screen)
		self.unlock_advanced_cost_text.draw(self.screen)

	def unlock_advanced(self):
		self.unlock_advanced_text1.update_text("")
		self.unlock_advanced_text2.update_color((255, 204, 0))
		self.unlock_advanced_text2.update_text("       Unlocked")
		self.unlock_advanced_cost_text.update_text("")


class BuyButton:
	def __init__(self, screen, pos, tower):
		self.screen = screen
		self.pos = pos
		self.tower = tower

		self.icon = pygame.transform.scale(tower.buy_icon, (163,120))
		self.text = Text("Deploy " + tower.name, [self.pos[0], self.pos[1] + 125], 24)
		self.cost_text = Text("Costs " + str(tower.cost[0]) + " goodwill", [self.pos[0] + 10, self.pos[1] + 155], 14)

		self.locked_icon = pygame.transform.scale(tower.locked_icon, (163,120))
		self.locked_text = Text("Deploy " + ("?" * len(tower.name)), [self.pos[0], self.pos[1] + 125], 24)
		self.locked_cost_text = Text("Costs ??? goodwill", [self.pos[0] + 10, self.pos[1] + 155], 14)

		self.button = Button(pygame.Rect(self.pos, (163,175)))

	def update(self, is_unlocked):
		if is_unlocked:
			self.button.draw(self.screen)

	def draw(self, is_unlocked):
		if is_unlocked:
			self.screen.blit(self.icon, self.pos)
			self.text.draw(self.screen)
			self.cost_text.draw(self.screen)
		else:
			self.screen.blit(self.locked_icon, self.pos)
			self.locked_text.draw(self.screen)
			self.locked_cost_text.draw(self.screen)


class InfoDisplay:
	def __init__(self, screen, pos):
		self.screen = screen
		self.pos = pos

		self.size = (250, 70)
		self.panel = pygame.Surface(self.size)
		self.panel.fill(PANEL_COLOR)

		self.lives_text = Text("", [self.pos[0] + 10, self.pos[1] + 5], size=32)
		self.currency_text = Text("", [self.pos[0] + 10, self.pos[1] + 35], size=32)

	def update(self, lives, currency):
		self.lives_text.update_text("Lives: " + str(lives))
		self.currency_text.update_text("Goodwill: " + str(currency))

	def draw(self):
		self.screen.blit(self.panel, self.pos)
		pygame.draw.rect(self.screen, PANEL_BORDER_COLOR, (self.pos, self.size), width=4)

		self.lives_text.draw(self.screen)
		self.currency_text.draw(self.screen)


class WavesDisplay:
	def __init__(self, screen, pos):
		self.screen = screen
		self.pos = pos

		self.size = (250, 120)
		self.panel = pygame.Surface(self.size)
		self.panel.fill(PANEL_COLOR)

		self.waves_text = Text("", [self.pos[0] + 125, self.pos[1] + 20], size=32, centered=True)
		self.next_wave = TextButton("[Play]",  [self.pos[0] + 125, self.pos[1] + 70], size=32, centered=True)

	def update(self, waves):
		wl, wp = waves.get_progress()
		self.waves_text.update_text(f"Wave {wl}/{wp}")

		if wl > 0 and self.next_wave.settings[0] == 32:
			self.next_wave = TextButton("[Call Next]",  [self.pos[0] + 125, self.pos[1] + 70], size=24, centered=True)

	def draw(self):
		self.screen.blit(self.panel, self.pos)
		pygame.draw.rect(self.screen, PANEL_BORDER_COLOR, (self.pos, self.size), width=4)

		self.waves_text.draw(self.screen)
		self.next_wave.draw(self.screen)


class LevelSelectButton:
	def __init__(self, screen, level, rect, label_text):
		self.screen = screen
		self.level = level
		self.rect = rect
		self.label_text = label_text

		self.completed = False
		self.unlocked = False

		self.locked_color = (255, 0, 0)
		self.unlocked_color = (255, 242, 0)
		self.completed_color = (30, 255, 0)

		self.current_color = self.locked_color

		self.b = Button(self.rect)
		self.surf = pygame.Surface(self.rect.size)
		self.surf.set_alpha(160)

		self.desc = Description(self.screen,self.label_text, self.level.description, (366, 384))

	def update(self, loop):
		if not self.unlocked:
			self.current_color = self.locked_color
		elif not self.completed:
			self.current_color = self.unlocked_color
			self.b.draw(self.screen)
			if self.b.hovered and self.desc.text.text != "":
				self.desc.draw(self.completed)
		else:
			self.current_color = self.completed_color
			self.b.change_cursor = False
			self.b.draw(self.screen)
			if self.b.hovered and self.desc.text.text != "":
				self.desc.draw(self.completed)
			

		if self.surf.get_at((0,0)) != self.current_color:
			self.surf.fill(self.current_color)
			self.label = Text(self.label_text, (self.rect.center[0], self.rect.center[1] - 10), 30, color=(0,0,0), centered=True)	
		

	def draw(self):
		self.screen.blit(self.surf, (self.rect.x, self.rect.y))
		pygame.draw.rect(self.screen, self.current_color, self.rect, width=2)

		self.label.draw(self.screen)
		

class Description:
	def __init__(self, screen, title, description, pos):
		self.screen = screen
		self.description = description
		self.title = title
		self.pos = pos

		self.size = (664, 270)
		self.panel = pygame.Surface(self.size)
		self.panel.fill(PANEL_COLOR)

		self.title = Text(self.title, (self.pos[0] + self.size[0]/2, self.pos[1] + 20), 40, centered=True)
		self.completed_text = Text("(Completed!)", (self.pos[0] + 410, self.pos[1] + 26), 28, color=(0,255,0))
		self.text = LinedText(self.description, [self.pos[0] + 50, self.pos[1] + 70], 54, size=22)

	def draw(self, completed):
		self.screen.blit(self.panel, self.pos)
		pygame.draw.rect(self.screen, PANEL_BORDER_COLOR, (self.pos, self.size), width=2)

		self.title.draw(self.screen)
		self.text.draw(self.screen)

		if completed:
			self.completed_text.draw(self.screen)
